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

from db.database import get_db, async_session
from db.models import InventoryItemModel, ChefMemoryModel, ChefSessionModel
from core.fsm import ChefFSM
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

from core.agents.sub_agents import AnalyticsReportSchema

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
                # ---------------------------------------------------------------------------
                # Phase 14: Session Termination Ritual (/kinec)
                # ---------------------------------------------------------------------------
                if user_input_text.lower().startswith("/kinec"):
                    from core.agents.sub_agents import extract_user_traits
                    from sqlalchemy import delete
                    
                    yield f"data: {json.dumps({'type': 'status', 'data': {'text': 'Chef is packing up... analyzing your session...', 'intent': 'CHAT'}})}\n\n"
                    
                    # 1. Fetch current chat history for analysis
                    sess_q = await session.execute(
                        sa_select(ChefSessionModel)
                        .where(ChefSessionModel.user_id == DEFAULT_USER_ID)
                        .order_by(ChefSessionModel.created_at.desc())
                    )
                    active_session = sess_q.scalars().first()
                    
                    if active_session:
                        msg_q = await session.execute(
                            sa_select(ChatMessageModel)
                            .where(ChatMessageModel.session_id == active_session.id)
                            .order_by(ChatMessageModel.id.asc())
                        )
                        db_msgs = msg_q.scalars().all()
                        chat_history_for_extraction = [{"role": m.role, "content": m.content} for m in db_msgs]
                        
                        # 2. Extract traits
                        traits = await extract_user_traits(chat_history_for_extraction)
                        
                        # 3. Update ChefMemoryModel
                        try:
                            mem_q = await session.execute(
                                sa_select(ChefMemoryModel)
                                .where(ChefMemoryModel.user_id == DEFAULT_USER_ID)
                            )
                            memory_obj = mem_q.scalars().first()
                            if memory_obj:
                                existing_traits = memory_obj.traits or {}
                                traits = traits or {}
                                # Merge traits safely
                                if traits.get('preferences'):
                                    prefs = traits['preferences'] if isinstance(traits['preferences'], list) else [traits['preferences']]
                                    exist_prefs = existing_traits.get('preferences', [])
                                    exist_prefs = exist_prefs if isinstance(exist_prefs, list) else []
                                    existing_traits['preferences'] = list(set(exist_prefs + prefs))
                                    
                                if traits.get('personality'):
                                    pers = traits['personality'] if isinstance(traits['personality'], list) else [traits['personality']]
                                    exist_pers = existing_traits.get('personality', [])
                                    exist_pers = exist_pers if isinstance(exist_pers, list) else []
                                    existing_traits['personality'] = list(set(exist_pers + pers))
                                    
                                if traits.get('skill_level'):
                                    existing_traits['skill_level'] = traits['skill_level']
                                    
                                memory_obj.traits = existing_traits
                                await session.commit()
                        except Exception as e:
                            logging.error(f"Failed to merge traits: {e}")
                        
                        # 4. Generate user-facing summary in their language
                        summary_text = "Session ended. Memory updated."
                        if client and chat_history_for_extraction:
                            # Detect language from last user message or default to Ukrainian
                            last_user_msg = next((m["content"] for m in reversed(chat_history_for_extraction) if m["role"] == "user"), "")
                            prompt = (
                                f"You are the Chef. Summarize the following extracted traits into a short, witty farewell message (max 2 sentences). "
                                f"IMPORTANT: Respond in the exact same language as the user's last message: '{last_user_msg}'. "
                                f"If unsure, use Ukrainian. Traits: {json.dumps(traits)}"
                            )
                            try:
                                sum_resp = await client.aio.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=prompt,
                                    config=types.GenerateContentConfig(temperature=0.7)
                                )
                                if sum_resp.text:
                                    summary_text = sum_resp.text.strip()
                            except Exception as e:
                                logging.warning(f"Failed to generate localized summary: {e}")
                        
                        yield f"data: {json.dumps({'type': 'status', 'data': {'text': 'Memory updated. Closing kitchen...', 'intent': 'CHAT'}})}\n\n"
                        
                        # Send summary via delta word by word so UI renders it properly
                        words = summary_text.split()
                        for i, word in enumerate(words):
                            space = " " if i > 0 else ""
                            yield f"data: {json.dumps({'type': 'delta', 'data': {'text': space + word, 'intent': 'CHAT'}})}\n\n"
                        
                        # Final payload
                        final_payload = {
                            "artifact_type": "CHAT",
                            "text": summary_text,
                            "metadata": {}
                        }
                        yield f"data: {json.dumps({'type': 'final', 'data': {'payload': final_payload}})}\n\n"
                        
                        # Session remains in database for future conversational history features.
                        return

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
    
    # MIME type protection: fallback to image/jpeg if unknown
    mime_type = file.content_type if file.content_type and "image" in file.content_type else "image/jpeg"

    prompt = """
    Extract items from this receipt. Return ONLY a valid JSON list of objects:
    [{"name": "...", "amount": float, "unit": "...", "days_left": int/null, "category": "...", "unit_price": float}].
    If the receipt has a store name, add a field "store_name": "..." to each object if possible.
    Categories should be: Produce, Dairy, Meat, Pantry, Frozen, Drinks.
    """
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, types.Part.from_bytes(data=contents, mime_type=mime_type)],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        items_data = json.loads(response.text)
        
        # Save to DB logic here (skipped for conciseness as per existing pattern)
        return {"status": "success", "items": items_data}
    except Exception as e:
        import logging
        logging.error(f"[ReceiptScanner] Error: {e}", exc_info=False)
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
