import json
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from datetime import datetime
import aiofiles

from db.database import get_db
from db.models import InventoryItemModel, ChefStateModel, ChefMemoryModel, ChefSessionModel
from core.fsm import ChefFSM, ChefTrigger
from core.persona import ChefPersona
from core.services.artifact_service import ARTIFACT_SCHEMAS

from google import genai
from google.genai import types

try:
    client = genai.Client()
except Exception as e:
    client = None

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

router = APIRouter()

class RecipeRequest(BaseModel):
    ingredient: str

from enum import Enum
from typing import List, Dict, Any

class ArtifactType(str, Enum):
    RECIPE = "RECIPE"
    SHOPPING_LIST = "SHOPPING_LIST"
    PREP_SCHEDULE = "PREP_SCHEDULE"
    TASK_LIST = "TASK_LIST"
    WASTE_ALERT = "WASTE_ALERT"

class ArtifactSummary(BaseModel):
    title: str
    short_desc: str
    match_score: int
    artifact_type: ArtifactType

class TechnicalData(BaseModel):
    artifact_summaries: List[ArtifactSummary]
    tool_commands: List[str]

class ChefResponse(BaseModel):
    chat_message: str
    technical_data: TechnicalData
    emotion_displayed: str

class ArtifactRequest(BaseModel):
    title: str
    artifact_type: ArtifactType
    context_parameters: str = ""

class CookRequest(BaseModel):
    ingredients: List[str]  # e.g. ["2 eggs", "100g butter", "1 cup flour"]

@router.post("/v1/chef/advice")
async def generate_batch_recipe(request: RecipeRequest, session: AsyncSession = Depends(get_db)):
    """
    Generates ONE cohesive recipe from the Chef for a batch of expiring ingredients,
    eliminating N+1 LLM calls.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is missing. Check your API Key.")

    user_query = request.ingredient.strip() if request.ingredient else ""
    
    # 1. Aggregate expiring items from DB
    fridge_query = await session.execute(select(InventoryItemModel).where(InventoryItemModel.storage_location == 'Fridge'))
    all_items = fridge_query.scalars().all()
    
    current_date = datetime.now()
    expiring_batch_data = {}
    
    for item in all_items:
        if item.expiry_date:
            try:
                days_left = (datetime.fromisoformat(item.expiry_date) - current_date).days
                if days_left <= 7:  # Expiring soon batching
                    expiring_batch_data[item.name] = {
                        "days_left": days_left,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "category": item.category
                    }
            except ValueError:
                pass
                
    if not expiring_batch_data:
        expiring_summary = "No items are expiring soon. Fridge is stable."
    else:
        expiring_summary = ", ".join([
            f"{k} ({v['quantity']}{v['unit']}, expires in {v['days_left']} days)" 
            for k, v in expiring_batch_data.items()
        ])

    # 2. Load DB State
    state_db = await session.get(ChefStateModel, DEFAULT_USER_ID)
    memory_db = await session.get(ChefMemoryModel, DEFAULT_USER_ID)
    session_db_q = await session.execute(
        select(ChefSessionModel)
        .where(ChefSessionModel.user_id == DEFAULT_USER_ID)
        .order_by(ChefSessionModel.created_at.desc())
    )
    session_db = session_db_q.scalars().first()
    
    if not state_db or not memory_db or not session_db:
        raise HTTPException(status_code=500, detail="State not found for default user.")

    # 3. FSM
    chef_fsm = ChefFSM(state_db=state_db, memory_db=memory_db, session_db=session_db)
    chef_persona = ChefPersona(fsm=chef_fsm)
    chef_fsm.trigger(ChefTrigger.COMPLEX_TASK)
    chef_persona.update_preferences(user_query)

    # 4. Passive RAG
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
        pass 

    system_prompt = chef_persona.generate_system_prompt()
    flavor_string = ", ".join(best_pairs) if best_pairs else "None"
    
    # 5. EXACTLY ONE Call Context
    user_prompt = f"""
    You are the KozakEye Chef FSM System.
    Context:
    - User Request: {user_query}
    - Expiring Ingredients Batch: {expiring_summary}
    - Found Classic Flavor Pairings: {flavor_string}

    Instructions:
    1. Propose EXACTLY 3 helpful artifacts for the user to prevent waste. These can be recipes (RECIPE), shopping lists (SHOPPING_LIST), prep schedules (PREP_SCHEDULE), task lists (TASK_LIST), or waste alerts (WASTE_ALERT).
    2. Acknowledge the user's request conversationally in `chat_message`. DO NOT put full artifact details in `chat_message`.
    3. Place the 3 proposals in `technical_data.artifact_summaries`.
    4. Emotion should be one of: IDLE, FOCUSED, PLAYFUL, ANGRY, PANICKED, CHAOTIC, FURIOUS, CREATIVE.
    5. You MUST output valid JSON conforming exactly to the defined schema.
    """
    
    try:
        # Gemini 2.5 Flash — balanced performance for batch recipe generation
        # Note: If the SDK is an older version, we pass it via raw config or just temperature.
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ChefResponse,
                temperature=0.7
            )
        )
        
        if getattr(response, "parsed", None):
            chef_response_data = response.parsed.model_dump()
        else:
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            try:
                chef_response_data = json.loads(raw_text)
            except json.JSONDecodeError as e:
                chef_response_data = {
                    "chat_message": f"System Error: Parse fail. {e}",
                    "technical_data": {
                        "artifact_summaries": [],
                        "tool_commands": []
                    },
                    "emotion_displayed": "ANGRY"
                }
                
        if "artifact_summaries" not in chef_response_data.get("technical_data", {}):
            chef_response_data["technical_data"]["artifact_summaries"] = []
            
        await session.commit()

        return {
            "status": "success",
            "ingredient_to_save": user_query,
            "chef_response": chef_response_data
        }
    except Exception as e:
        import logging
        logging.error("Batch recipe generation error", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/v1/chef/generate-artifact")
async def generate_artifact(request: ArtifactRequest, session: AsyncSession = Depends(get_db)):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini Client is missing. Check your API Key.")

    fridge_query = await session.execute(select(InventoryItemModel).where(InventoryItemModel.storage_location == 'Fridge'))
    all_items = fridge_query.scalars().all()
    fridge_summary = ", ".join([f"{i.name} ({i.quantity}{i.unit})" for i in all_items])

    artifact_type_key = request.artifact_type.value
    schema_instruction = ARTIFACT_SCHEMAS.get(artifact_type_key, ARTIFACT_SCHEMAS["RECIPE"])

    user_prompt = f"""
    Generate the full detailed JSON payload for the requested artifact.
    Artifact Title: {request.title}
    Artifact Type: {artifact_type_key}
    User Context/Parameters: {request.context_parameters}
    Current Fridge Inventory: {fridge_summary}
    """

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=schema_instruction,
                response_mime_type="application/json",
                temperature=0.65
            )
        )

        raw_text = response.text.replace("```json", "").replace("```", "").strip() if response.text else "{}"
        try:
            artifact_data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            artifact_data = {"error": f"Parse fail: {e}", "raw": raw_text[:500]}

        return {
            "status": "success",
            "artifact_type": artifact_type_key,
            "artifact": artifact_data
        }

    except Exception as e:
        import logging
        logging.error("Artifact generation error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/v1/fridge/item/{name}")
async def remove_fridge_item(name: str, session: AsyncSession = Depends(get_db)):
    """
    Phase 12.1-B: Legacy fridge logic ported from Fridge.remove_product().
    """
    items_q = await session.execute(select(InventoryItemModel).where(InventoryItemModel.name == name))
    item = items_q.scalars().first()
    
    if item:
        await session.delete(item)
        await session.commit()
        return {"status": "success", "message": f"Removed: {name}"}
    
    raise HTTPException(status_code=404, detail=f"Product {name} is not in the fridge, can't take it out.")

@router.post("/v1/fridge/cook")
async def deduct_cooked_ingredients(request: CookRequest, session: AsyncSession = Depends(get_db)):
    """
    Phase 12.1-B: Legacy fridge logic ported from Fridge.use_product().
    Strict validation: if ANY non-ignored ingredient is missing, the operation aborts.
    """
    deducted: List[str] = []
    not_found: List[str] = []
    matched_items = []

    IGNORED_SPICES = {"salt", "black pepper", "pepper", "water", "сіль", "перець", "вода", "цукор", "sugar"}

    items_q = await session.execute(select(InventoryItemModel))
    all_inv = items_q.scalars().all()

    inv_name_map = {item.name.lower(): item for item in all_inv}

    for ingredient_str in request.ingredients:
        clean = re.sub(r'^[\d.,/½¼¾]+\s*(?:g|kg|ml|l|oz|lb|cups?|tbsp|tsp|pcs|cloves?|slices?|large|medium|small)?\s*', '', ingredient_str, flags=re.IGNORECASE).strip()
        keyword = clean.lower() if clean else ingredient_str.lower()
        
        if keyword in IGNORED_SPICES:
            continue

        matched = inv_name_map.get(keyword)
        if not matched:
            matched = next(
                (item for name_lower, item in inv_name_map.items()
                 if keyword in name_lower or name_lower in keyword),
                None
            )

        if matched:
            matched_items.append((matched, ingredient_str))
        else:
            not_found.append(ingredient_str)

    if not_found:
        # Strict validation failed: abort cook
        return {
            "status": "error",
            "missing": not_found,
            "deducted": [],
            "not_found": not_found
        }

    # All required items present, proceed with deduction
    items_to_delete = []
    items_to_update = []
    for matched, ingredient_str in matched_items:
        if matched.quantity <= 1:
            items_to_delete.append(matched.id)
            deducted.append(f"{matched.name} (removed — last unit used)")
        else:
            items_to_update.append({"id": matched.id, "quantity": matched.quantity - 1})
            deducted.append(f"{matched.name} ({matched.quantity - 1} left)")

    if items_to_delete:
        await session.execute(delete(InventoryItemModel).where(InventoryItemModel.id.in_(items_to_delete)))
    
    if items_to_update:
        from sqlalchemy import bindparam
        stmt = update(InventoryItemModel).where(InventoryItemModel.id == bindparam("id")).values(quantity=bindparam("quantity"))
        await session.execute(stmt, items_to_update)

    await session.commit()

    return {
        "status": "success",
        "deducted": deducted,
        "not_found": []
    }
