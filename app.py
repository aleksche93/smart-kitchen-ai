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
from datetime import datetime, timedelta
from sqlalchemy import select
from db.models import InventoryItemModel, ReceiptHistoryModel
import hashlib

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

@app.on_event("startup")
async def startup_event():
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

class ParsedReceiptItem(BaseModel):
    name: str = Field(..., description="Normalized clean name of the product")
    category: str = Field(..., description="Semantic grouping: Dairy, Meat, Produce, etc.")
    storage_location: str = Field(..., description="MUST BE one of: Fridge, Freezer, Pantry, Bathroom, Other")
    estimated_days_left: Optional[int] = Field(None, description="Estimated shelf life in days. Return null for non-perishables.")
    quantity: float = Field(default=1.0, description="Number of items or amount")
    unit: str = Field(default="pcs", description="Unit of measurement, e.g., pcs, kg, L")
    price: Optional[float] = Field(None, description="Total price for the item, if detected")

class ParsedReceiptResponse(BaseModel):
    store_name: str = Field(..., description="Store name extracted from receipt")
    store_address: Optional[str] = Field(None, description="Store address if found")
    receipt_date: Optional[str] = Field(None, description="ISO format date if found on the receipt")
    items: List[ParsedReceiptItem]

@app.post("/api/v1/fridge/receipt")
async def parse_receipt_vision(file: UploadFile = File(...), session: AsyncSession = Depends(get_db)):
    """
    Intelligently parses receipt images using Gemini Vision into SQLite Inventory records with deduplication.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is missing. Check your API Key.")
        
    allowed_mimes = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, or WEBP allowed.")
        
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 5MB limit.")
        
    image_hash = hashlib.sha256(content).hexdigest()
    
    # Check deduplication layer
    exists = await session.execute(select(ReceiptHistoryModel).where(ReceiptHistoryModel.image_hash == image_hash))
    if exists.scalars().first():
        raise HTTPException(status_code=409, detail={"is_duplicate": True, "message": "Receipt already scanned."})
        
    receipt_sys_prompt = """
    You are a Smart Kitchen Data Architect. Analyze the provided grocery receipt image.
    1. Normalization: Clean up messy abbreviations (e.g., convert 'MLK 2.5% VOL' to 'Milk 2.5%').
    2. Storage Routing: Accurately classify where the item belongs. `storage_location` MUST BE one of: "Fridge", "Freezer", "Pantry", "Bathroom", "Other".
    3. Shelf-life Estimation: Provide a realistic `estimated_days_left` for perishable foods. IMPORTANT: Return null for non-perishables. Do NOT use 0 for non-perishables.
    4. STRICT PRIVACY PROTOCOL: Completely ignore and scrub any Personally Identifiable Information (PII) like credit card digits, personal names, and phone numbers. You may extract the store name and address.
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                receipt_sys_prompt,
                types.Part.from_bytes(data=content, mime_type=file.content_type)
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ParsedReceiptResponse,
                temperature=0.2
            )
        )
        
        if getattr(response, "parsed", None):
            receipt_data = response.parsed.model_dump()
        else:
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            receipt_data = json.loads(raw_text)
            
        added_items = []
        current_date = datetime.now()
        
        for item_data in receipt_data.get("items", []):
            expiry = None
            if item_data.get("estimated_days_left") is not None:
                expiry = (current_date + timedelta(days=item_data["estimated_days_left"])).isoformat()
                
            new_item = InventoryItemModel(
                user_id=DEFAULT_USER_ID,
                name=item_data["name"],
                category=item_data["category"],
                storage_location=item_data["storage_location"],
                quantity=item_data.get("quantity", 1.0),
                unit=item_data.get("unit", "pcs"),
                price=item_data.get("price", None),
                added_date=current_date.isoformat(),
                expiry_date=expiry
            )
            session.add(new_item)
            added_items.append(item_data["name"])
            
        # Add to history to prevent duplicates
        new_receipt = ReceiptHistoryModel(image_hash=image_hash)
        session.add(new_receipt)
            
        await session.commit()
        
        return {
            "status": "success",
            "store_name": receipt_data.get("store_name", "Unknown Store"),
            "total_recognized": len(added_items),
            "items_added": added_items
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/fridge")
async def get_fridge_inventory(session: AsyncSession = Depends(get_db)):
    """Returns current fridge inventory directly from SQLite."""
    query = await session.execute(select(InventoryItemModel).where(InventoryItemModel.storage_location == 'Fridge'))
    all_items = query.scalars().all()
    
    items_data = []
    current_date = datetime.now()
    
    for item in all_items:
        days_left = 999
        if item.expiry_date:
            try:
                days_left = (datetime.fromisoformat(item.expiry_date) - current_date).days
            except:
                pass
        
        if days_left > 0:
            items_data.append({
                "id": str(item.id),
                "name": item.name,
                "category": item.category,
                "amount": item.quantity,
                "unit": item.unit,
                "days_left": days_left if item.expiry_date else None
            })
            
    return {"status": "success", "total_fresh": len(items_data), "inventory": items_data}

class RecipeRequest(BaseModel):
    ingredient: str

class RecipeOption(BaseModel):
    name: str
    ingredients: List[str]
    instructions: List[str]
    time: str
    difficulty: str

class ChefResponse(BaseModel):
    advice_text: str
    recipe_options: List[RecipeOption]
    emotion_displayed: str
    tool_commands: List[str]

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
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is missing. Check your API Key.")

    user_query = request.ingredient.strip() if request.ingredient else ""
    
    # 1. Passive Context Generation from DB
    fridge_query = await session.execute(select(InventoryItemModel).where(InventoryItemModel.storage_location == 'Fridge'))
    all_items = fridge_query.scalars().all()
    
    fridge_summary_list = []
    current_date = datetime.now()
    
    for item in all_items:
        if item.expiry_date:
            try:
                days_left = (datetime.fromisoformat(item.expiry_date) - current_date).days
                if days_left > 0:
                    fridge_summary_list.append(f"{item.name} ({days_left}d left)")
            except:
                pass
        else:
            fridge_summary_list.append(f"{item.name}")
            
    fridge_summary = ", ".join(fridge_summary_list)
    if not fridge_summary:
        fridge_summary = "The fridge is completely empty."

    # 1.1 Load Database state for default user
    state_db = await session.get(ChefStateModel, DEFAULT_USER_ID)
    memory_db = await session.get(ChefMemoryModel, DEFAULT_USER_ID)
    session_db = await session.get(ChefSessionModel, DEFAULT_USER_ID)
    
    if not state_db or not memory_db or not session_db:
        raise HTTPException(status_code=500, detail="State not found for default user.")

    # 2. Initialize Core Wrappers
    chef_fsm = ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)
    chef_persona = ChefPersona(fsm=chef_fsm)

    # 3. Trigger the FSM
    chef_fsm.trigger(ChefTrigger.COMPLEX_TASK)
    chef_persona.update_preferences(user_query)

    # Passive Flavor Bible Lookup (Only append if we find a direct hit for the query)
    best_pairs = []
    try:
        async with aiofiles.open("knowledge/flavors.json", "r", encoding="utf-8") as f:
            knowledge_data = json.loads(await f.read())
            flavor_map = {item["ingredient"].lower(): item["pairings"] for item in knowledge_data}
            if user_query.lower() in flavor_map:
                best_pairs = [
                    p["paired_with"] for p in flavor_map[user_query.lower()]
                    if p.get("affinity") in ["classic", "highly recommended"]
                ]
    except Exception:
        pass # Gracefully ignore KB missing in dual-mode

    # 4. Generate Dynamic Prompt for Gemini & Structured Outputs
    system_prompt = chef_persona.generate_system_prompt()
    
    pairings_context = f"Relevant Flavor Pairs: {best_pairs}.\n" if best_pairs else ""
    user_prompt = (
        f"Available Fridge Items as context: {fridge_summary}\n"
        f"User Input/Query: \"{user_query}\"\n"
        f"{pairings_context}"
        f"Provide compelling advice based on your persona, a structured recipe object if requested, and any tool_commands."
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
            try:
                chef_response_data = json.loads(raw_text)
            except json.JSONDecodeError as e:
                chef_response_data = {
                    "advice_text": f"System Error: Chef is too chaotic. {e}",
                    "recipe_options": [{
                        "name": "Chef's Surprise",
                        "ingredients": [],
                        "instructions": ["Improvise!"],
                        "time": "15 min",
                        "difficulty": "Easy"
                    }],
                    "emotion_displayed": "ANGRY",
                    "tool_commands": []
                }
            
        # Pydantic Fallback handling: enforce strict sub-schema format
        if "recipe_options" not in chef_response_data or not chef_response_data.get("recipe_options"):
            chef_response_data["recipe_options"] = [{
                "name": "Chef's Surprise",
                "ingredients": [],
                "instructions": ["Improvise!"],
                "time": "15 min",
                "difficulty": "Easy"
            }]
        
        # 5. Save the updated emotional state
        await session.commit()

        # In Dual-Mode, ingredient parameter is just arbitrary user query
        return {
            "status": "success",
            "ingredient_to_save": user_query,
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
