import json
import re
import asyncio
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from datetime import datetime
import aiofiles

from db.database import get_db, async_session
from db.models import InventoryItemModel, ChefStateModel, ChefMemoryModel, ChefSessionModel
from core.fsm import ChefFSM, ChefTrigger
from core.persona import ChefPersona
from core.services.artifact_service import ARTIFACT_SCHEMAS
from core.agents.orchestrator import ChefOrchestrator

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

# ---------------------------------------------------------------------------
# Analytics Schemas — MUST be defined BEFORE orchestrator wiring
# Used for ANALYTICS intent inventory reports (avoids 500 on event: final)
# ---------------------------------------------------------------------------

class AnalyticsItemReport(BaseModel):
    """A single fridge item in the analytics report."""
    name: str
    days_left: Optional[int] = None
    amount: float = 0.0
    unit: str = ""
    priority: str = "FRESH"  # "CRITICAL" | "WARNING" | "FRESH"

class AnalyticsReportSchema(BaseModel):
    """Structured inventory analytics report for ANALYTICS artifacts."""
    summary: str = ""
    critical_items: List[AnalyticsItemReport] = []   # days_left <= 2
    warning_items: List[AnalyticsItemReport] = []    # days_left 3-5
    fresh_items: List[AnalyticsItemReport] = []      # days_left > 5 or None
    total_items: int = 0
    waste_risk_count: int = 0

class ProcessRequest(BaseModel):
    """Unified request model for all Orchestrator interactions (chat + recipe)."""
    title: str = "Chef's Artifact"
    artifact_type: str = "RECIPE"
    context_parameters: Optional[str] = ""
    # Last 10 messages for conversational memory: [{role: "user"|"assistant", content: "..."}]
    chat_history: Optional[List[Dict[str, Any]]] = []
    # Force a specific intent, bypassing the LLM classifier (used by executeMagic)
    force_intent: Optional[str] = None


@router.post("/v1/chef/process")
async def process_orchestrator(request: ProcessRequest):
    """
    Single Orchestrator endpoint for ALL interactions (chat and artifact generation).
    Implements 3-Tier SSE Protocol: status → delta (with intent field) → final.
    The frontend routes delta chunks based on delta.data.intent: CHAT or RECIPE.
    Persists user + assistant messages to SQLite for session history restoration.
    """
    from db.models import ChefSessionModel, ChatMessageModel
    from sqlalchemy import select as sa_select
    import logging

    async def event_generator():
        full_assistant_reply = ""
        user_input_text = (request.context_parameters or request.title or "").strip()
        try:
            async with async_session() as session:
                fridge_query = await session.execute(
                    select(InventoryItemModel)
                    .where(InventoryItemModel.storage_location == 'Fridge')
                    .where(InventoryItemModel.quantity > 0.001)
                )
                all_items = fridge_query.scalars().all()
                inventory_data = [
                    {
                        "name": i.name,
                        "amount": i.quantity,
                        "unit": i.unit,
                        "days_left": (
                            (datetime.fromisoformat(i.expiry_date) - datetime.now()).days
                            if i.expiry_date else None
                        )
                    }
                    for i in all_items
                ]

                # Sanitize and limit chat_history to last 10 messages
                raw_history = request.chat_history or []
                safe_history = [
                    {"role": str(m.get("role", "user")), "content": str(m.get("content", ""))}
                    for m in raw_history
                    if m.get("content", "").strip()
                ][-10:]

                context = {
                    "user_input": user_input_text,
                    "artifact_type": (
                        request.artifact_type.value
                        if hasattr(request.artifact_type, "value")
                        else request.artifact_type
                    ),
                    "title": request.title,
                    "inventory": inventory_data,
                    "chat_history": safe_history,
                    "force_intent": request.force_intent,
                }

                orchestrator = ChefOrchestrator()
                async for chunk in orchestrator.process(context):
                    # Intercept delta chunks to accumulate CHAT reply for DB persistence
                    try:
                        event_obj = json.loads(chunk.replace("data: ", "").strip())
                        if event_obj.get("type") == "delta" and event_obj["data"].get("intent") == "CHAT":
                            full_assistant_reply += event_obj["data"].get("text", "")
                    except Exception:
                        pass
                    yield chunk

                # --- DB Persistence: save user + assistant messages to SQLite ---
                if user_input_text and not request.force_intent:
                    try:
                        sess_q = await session.execute(
                            sa_select(ChefSessionModel)
                            .where(ChefSessionModel.user_id == DEFAULT_USER_ID)
                            .order_by(ChefSessionModel.created_at.desc())
                        )
                        active_session = sess_q.scalars().first()
                        if active_session:
                            clean_reply = (
                                full_assistant_reply
                                .replace("[ACTION: MAGIC_TRIGGER]", "")
                                .replace("[ACTION: AUDIT_WARNING]", "")
                                .strip()
                            )
                            session.add(ChatMessageModel(
                                session_id=active_session.id,
                                role="user",
                                content=user_input_text
                            ))
                            if clean_reply:
                                session.add(ChatMessageModel(
                                    session_id=active_session.id,
                                    role="assistant",
                                    content=clean_reply
                                ))
                            await session.commit()
                    except Exception as db_err:
                        logging.warning(f"[/process] DB persist failed (non-fatal): {db_err}")

        except asyncio.CancelledError:
            logging.info("[/process] SSE stream disconnected by client.")
            raise
        except Exception as e:
            logging.error(f"[/process] Unhandled error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'status', 'data': {'text': 'Fatal error occurred.'}})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

class WasteAlertSchema(BaseModel):
    severity: str
    expiring_items: list
    total_value_at_risk: str
    recommended_action: str

class RecipeSchema(BaseModel):
    name: str
    time: str
    difficulty: str
    ingredients: list
    instructions: list
    notes: Optional[str] = None

class CookRequest(BaseModel):
    ingredients: List[str]  # e.g. ["2 eggs", "100g butter", "1 cup flour"]

class InventoryItem(BaseModel):
    name: str
    amount: float
    unit: str
    days_left: Optional[int] = None
    category: Optional[str] = "General"
    unit_price: Optional[float] = 0.0

@router.post("/fridge/receipt")
async def scan_receipt(file: UploadFile = File(...)):
    """
    Smart Receipt 2.0: Proactive extraction of items, categories, and pricing.
    """
    contents = await file.read()
    
    prompt = """
    Extract items from this receipt. Return ONLY a valid JSON list of objects:
    [{"name": "...", "amount": float, "unit": "...", "days_left": int/null, "category": "...", "unit_price": float}].
    If the receipt has a store name, add a field "store_name": "..." to each object if possible.
    Categories should be: Produce, Dairy, Meat, Pantry, Frozen, Drinks.
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, types.Part.from_bytes(data=contents, mime_type=file.content_type)],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        items_data = json.loads(response.text)
        
        # Save to DB logic here (skipped for conciseness as per existing pattern)
        return {"status": "success", "items": items_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/v1/fridge/item/{item_id_or_name}")
async def remove_fridge_item(item_id_or_name: str, session: AsyncSession = Depends(get_db)):
    """
    Phase 13.5: Hardened manual delete supporting both UUID and direct name lookup.
    Ensures absolute persistence with explicit commit.
    """
    try:
        # 1. Try UUID lookup first
        item = None
        if len(item_id_or_name) == 36:
            item = await session.get(InventoryItemModel, item_id_or_name)
        
        # 2. Fallback to Name lookup (case-insensitive) if ID fails
        if not item:
            q = await session.execute(
                select(InventoryItemModel).where(InventoryItemModel.name.ilike(item_id_or_name))
            )
            item = q.scalars().first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item_name = item.name
        await session.delete(item)
        await session.commit()
        return {"status": "success", "message": f"Successfully removed {item_name}"}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
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

    items_q = await session.execute(select(InventoryItemModel).where(InventoryItemModel.quantity > 0))
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
        # Phase 13.5: Handle float quantities correctly to prevent ghost items
        new_quantity = matched.quantity - 1
        if new_quantity <= 0.001:
            items_to_delete.append(matched.id)
            deducted.append(f"{matched.name} (removed)")
        else:
            items_to_update.append({"id": matched.id, "quantity": new_quantity})
            deducted.append(f"{matched.name} ({new_quantity} left)")

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
