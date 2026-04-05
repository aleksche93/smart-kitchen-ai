import os
import shutil
import tempfile
import asyncio
import json
import aiofiles
import uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

# New database and core imports
from db.database import get_db, init_db, async_session
from db.models import UserModel, ChefStateModel, ChefMemoryModel, ChefSessionModel
from core.fsm import ChefFSM, ChefTrigger
from core.persona import ChefPersona
from core.locales import i18n

# Gemini API setup for structured output
from google import genai
from google.genai import types

# Import existing logic
from scanner import scan_receipt
from smart_fridge import Fridge, BaseProduct

app = FastAPI(
    title="Smart Kitchen AI",
    description="Smart Kitchen ecosystem based on FastAPI",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy User Context
DEFAULT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

my_fridge = None

@app.on_event("startup")
async def startup_event():
    global my_fridge
    my_fridge = await Fridge.create()
    print("✅ Web API: Fridge initialized.")
    
    # Init DB and default user
    await init_db()
    print("✅ Web API: Database initialized.")
    
    async with async_session() as session:
        user = await session.get(UserModel, DEFAULT_USER_ID)
        if not user:
            user = UserModel(id=DEFAULT_USER_ID, name="Homeowner")
            state = ChefStateModel(user_id=DEFAULT_USER_ID)
            memory = ChefMemoryModel(user_id=DEFAULT_USER_ID)
            chef_session_db = ChefSessionModel(user_id=DEFAULT_USER_ID)
            session.add_all([user, state, memory, chef_session_db])
            await session.commit()
            print("✅ Web API: Default User Context created.")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Kitchen AI Ecosystem API!"}

@app.post("/api/v1/scan-receipt")
async def scan_receipt_api(file: UploadFile = File(...)):
    """
    Accepts a receipt image, extracts products using Gemini Vision,
    and automatically adds 'fridge' items to the database.
    """
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail=i18n.get("api.error.only_images_allowed", "Only JPG/PNG images are allowed."))
    
    # Temporary file for synchronous scanner backward compatibility
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        print(f"🔄 Web API: Scanning receipt {file.filename}...")
        # Async call to synchronous legacy code to prevent blocking event loop
        items = await asyncio.to_thread(scan_receipt, temp_file_path)
        
        if not items:
            return {"status": "success", "message": i18n.get("api.error.scan_failed", "Scanner found no products."), "added_to_fridge": 0, "recognized_items": []}

        total_items = len(items)
        added_to_fridge = 0
        added_items_details = []
        routed_items = []
        
        for item in items:
            cat = item.get("category", "other").lower()
            p_name = item.get("name", "Unknown")
            
            if cat == "fridge":
                product = BaseProduct(
                    name=p_name,
                    category=item.get("category", "fridge"),
                    amount=float(item.get("quantity", 1.0)),
                    unit=item.get("unit", "pcs"),
                    days_left=7
                )
                await my_fridge.add_product(product, silent=True)
                added_to_fridge += 1
                added_items_details.append(p_name)
            else:
                routed_items.append({"name": p_name, "zone": cat, "status": "Module in development"})
                
        return {
            "status": "success", 
            "total_recognized": total_items, 
            "added_to_fridge_count": added_to_fridge,
            "fridge_items_added": added_items_details,
            "other_routed_items": routed_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/api/v1/fridge")
async def get_fridge_inventory():
    """Returns current fridge inventory (all fresh products) in JSON format."""
    if not my_fridge:
        raise HTTPException(status_code=500, detail="Fridge not initialized")
    
    items_data = []
    # Звертаємось до поля _Fridge__items 
    for item in my_fridge._Fridge__items: 
        if item.days_left > 0:
            items_data.append(await item.to_dict())
        
    return {"status": "success", "total_fresh": len(items_data), "inventory": items_data}

class RecipeRequest(BaseModel):
    ingredient: str

class ActionStub(BaseModel):
    action: str
    params: Optional[str] = Field(None, description="Parameters in JSON string format")

class ChefResponse(BaseModel):
    advice_text: str
    recipe: Optional[str] = None
    emotion_displayed: str
    tool_commands: List[ActionStub] = Field(default_factory=list)

try:
    client = genai.Client()
except Exception as e:
    client = None

@app.post("/api/v1/chef/advice")
async def get_chef_recipe(request: RecipeRequest, session: AsyncSession = Depends(get_db)):
    """
    Generates a recipe from the Chef for a chosen critical ingredient,
    using Flavor Bible combinations and integrating the Chef FSM.
    """
    if not my_fridge:
        raise HTTPException(status_code=500, detail="Fridge not initialized")
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is missing. Check your API Key.")

    urgent_items = await my_fridge.get_urgent_list()
    target_name = request.ingredient.lower()
    
    # Check if this product is among spoiling items
    has_target = next((item for item in urgent_items if item.name.lower() == target_name), None)
    if not has_target:
        msg = i18n.get("api.error.ingredient_not_found").replace("{ingredient}", request.ingredient)
        raise HTTPException(
            status_code=400, 
            detail=msg
        )

    # 1. Load Database state for default user
    state_db = await session.get(ChefStateModel, DEFAULT_USER_ID)
    memory_db = await session.get(ChefMemoryModel, DEFAULT_USER_ID)
    session_db = await session.get(ChefSessionModel, DEFAULT_USER_ID)
    
    if not state_db or not memory_db or not session_db:
        raise HTTPException(status_code=500, detail="State not found for default user. Did startup_event run?")

    # 2. Initialize Core Wrappers
    chef_fsm = ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)
    chef_persona = ChefPersona(fsm=chef_fsm)

    # 3. Trigger the FSM
    chef_fsm.trigger(ChefTrigger.COMPLEX_TASK)
    
    # Let Persona react to ingredient
    chef_persona.update_preferences(target_name)

    # Read knowledge base
    try:
        async with aiofiles.open("knowledge/flavors.json", "r", encoding="utf-8") as f:
            knowledge_data = json.loads(await f.read())
    except Exception:
        raise HTTPException(status_code=500, detail=i18n.get("api.error.knowledge_data_missing"))
        
    flavor_map = {item["ingredient"].lower(): item["pairings"] for item in knowledge_data}
    
    if target_name not in flavor_map:
        msg = i18n.get("api.error.no_pairings_for_ingredient").replace("{ingredient}", request.ingredient)
        raise HTTPException(status_code=404, detail=msg)
        
    best_pairs = [
        p["paired_with"] for p in flavor_map[target_name]
        if p.get("affinity") in ["classic", "highly recommended"]
    ]
    
    if not best_pairs:
        msg = i18n.get("api.error.no_classic_pairings").replace("{ingredient}", request.ingredient)
        raise HTTPException(status_code=404, detail=msg)

    # 4. Generate Dynamic Prompt for Gemini & Structured Outputs
    system_prompt = chef_persona.generate_system_prompt()
    user_prompt = (
        f"I need advice on saving: {has_target.display_name.capitalize()}.\n"
        f"Ideal pairings from your knowledge base: {best_pairs}.\n"
        f"Provide compelling advice based on your current emotional state, give a recipe, and suggest any smart interactions via tool_commands."
    )

    try:
        # Structured output strictly returns valid JSON mapped to ChefResponse
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt + "\n\n" + user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChefResponse,
                temperature=0.7
            )
        )
        
        if not response.text:
            raise ValueError(f"Gemini returned empty text. Candidates: {response.candidates}")
            
        # Extract parsed object if provided natively by the SDK (google-genai)
        if getattr(response, "parsed", None):
            chef_response_data = response.parsed.model_dump()
        else:
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            chef_response_data = json.loads(raw_text)
        
        # 5. Save the updated emotional state
        await session.commit()

        return {
            "status": "success",
            "ingredient_to_save": has_target.display_name,
            "days_left": has_target.days_left,
            "chef_response": chef_response_data
        }
    except Exception as e:
        import traceback
        print(f"❌ Gemini Chef API Error: {e}")
        traceback.print_exc()
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
