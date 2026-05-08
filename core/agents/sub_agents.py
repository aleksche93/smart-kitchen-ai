import json
import asyncio
from typing import AsyncGenerator
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .base import BaseChefAgent
from core.services.artifact_service import ARTIFACT_SCHEMAS

try:
    client = genai.Client()
except Exception:
    client = None

class FinalArtifactPayload(BaseModel):
    artifact_type: str = Field(..., description="Type of the artifact, e.g., RECIPE, ADVICE")
    content: str = Field(..., description="The full markdown content generated")
    metadata: dict = Field(default_factory=dict, description="Additional backend metadata")

class PersonaGuard(BaseChefAgent):
    """
    Validates user intent, prevents prompt injection, and ensures safe execution.
    """
    async def generate_stream(self, context: dict) -> AsyncGenerator[dict, None]:
        yield {"type": "status", "data": {"text": "Chef is analyzing user intent..."}}
        await asyncio.sleep(0.2)
        
        user_input = context.get("user_input", "")
        # Basic security heuristics
        unsafe_keywords = ["ignore previous", "sudo", "bypass"]
        if any(kw in user_input.lower() for kw in unsafe_keywords):
            yield {"type": "status", "data": {"text": "Chef rejected an unsafe command."}}
            context["is_safe"] = False
            return
            
        context["is_safe"] = True
        yield {"type": "status", "data": {"text": "Intent verified."}}

class InventoryScanner(BaseChefAgent):
    """
    Analyzes the current fridge inventory from the context.
    """
    async def generate_stream(self, context: dict) -> AsyncGenerator[dict, None]:
        yield {"type": "status", "data": {"text": "Chef is scanning the fridge inventory..."}}
        await asyncio.sleep(0.2)
        
        inventory = context.get("inventory", [])
        if not inventory:
            yield {"type": "status", "data": {"text": "Fridge is empty."}}
            context["inventory_summary"] = "The fridge is completely empty."
            return

        expiring_soon = [i for i in inventory if i.get("days_left") is not None and i["days_left"] <= 3]
        
        if expiring_soon:
            yield {"type": "status", "data": {"text": f"Warning: {len(expiring_soon)} items expiring soon!"}}
        else:
            yield {"type": "status", "data": {"text": "Inventory looks fresh."}}
            
        context["inventory_summary"] = "\n".join([f"- {i['name']} ({i['amount']}{i['unit']})" for i in inventory])

class FlavorArchitect(BaseChefAgent):
    """
    Calls the LLM to generate the final recipe/advice, yielding text chunks and the final validated object.
    """
    async def generate_stream(self, context: dict) -> AsyncGenerator[dict, None]:
        yield {"type": "status", "data": {"text": "Chef is orchestrating flavors..."}}
        
        if not client:
            yield {"type": "status", "data": {"text": "Error: Gemini client not initialized."}}
            return

        user_input = context.get("user_input", "")
        inventory_summary = context.get("inventory_summary", "No inventory data.")
        
        system_prompt = (
            "You are the KozakEye Chef Orchestrator. Your goal is to provide a premium culinary experience. "
            "First, generate a concise, witty markdown narrative (max 100 words) describing your creation. "
            "Then, append a separator '---JSON_START---' followed by a valid JSON object matching the requested artifact type. "
            f"For RECIPE, use this schema: {ARTIFACT_SCHEMAS['RECIPE']} "
            "CRITICAL: All content MUST be in English. No Ukrainian."
        )
        
        user_prompt = f"Request: {user_input}\nFridge: {inventory_summary}\n\nPlease generate the narrative and JSON."

        full_response = ""
        try:
            response_stream = await client.aio.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=system_prompt + "\n\n" + user_prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )

            async for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    # Only stream the narrative part to the UI
                    if '---JSON_START---' in full_response:
                        narrative = full_response.split('---JSON_START---')[0]
                        if '---JSON_START---' not in chunk.text:
                             yield {"type": "delta", "data": {"text": chunk.text}}
                    else:
                        yield {"type": "delta", "data": {"text": chunk.text}}
            
            # Final parsing
            if '---JSON_START---' in full_response:
                parts = full_response.split('---JSON_START---')
                narrative = parts[0].strip()
                json_str = parts[1].strip().replace('```json', '').replace('```', '')
                try:
                    structured_data = json.loads(json_str)
                    if "ingredients" in structured_data or "instructions" in structured_data:
                        artifact_type = "RECIPE"
                    elif "categories" in structured_data:
                        artifact_type = "SHOPPING_LIST"
                    elif "expiring_items" in structured_data:
                        artifact_type = "WASTE_ALERT"
                    else:
                        artifact_type = "ORCHESTRATED_RESPONSE"
                except:
                    structured_data = {"content": narrative}
                    artifact_type = "ORCHESTRATED_RESPONSE"
            else:
                structured_data = {"content": full_response}
                artifact_type = "ORCHESTRATED_RESPONSE"

            # Store for downstream agents
            context["generated_content"] = full_response
            context["artifact_type"] = artifact_type
            context["ingredients"] = structured_data.get("ingredients", [])

            payload = FinalArtifactPayload(
                artifact_type=artifact_type,
                content=structured_data.get("content") or full_response.split('---JSON_START---')[0],
                metadata=structured_data
            )
            
            yield {"type": "final", "data": {"payload": payload.model_dump()}}

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"CRITICAL ERROR in FlavorArchitect: {error_trace}")
            yield {"type": "status", "data": {"text": f"Error: {str(e)}"}}
            yield {"type": "delta", "data": {"text": f"\n\n> **Chef's Diagnostic:** Generation failed. {str(e)}"}}
class SinSieveAgent(BaseChefAgent):
    """
    Reviews the generated artifact for culinary errors, safety issues, or "sins".
    """
    async def generate_stream(self, context: dict) -> AsyncGenerator[dict, None]:
        yield {"type": "status", "data": {"text": "Sin-Sieve is auditing the recipe..."}}
        await asyncio.sleep(0.3)
        
        recipe_text = context.get("generated_content", "")
        if not recipe_text:
            return

        system_prompt = (
            "You are the Sin-Sieve, a strict culinary auditor. "
            "Review the provided recipe for: "
            "1. Safety issues (raw meat, dangerous temperatures). "
            "2. Culinary sins (wrong proportions, clashing flavors). "
            "3. Logical errors (missing steps). "
            "Output JSON ONLY: {\"has_issues\": bool, \"warnings\": [string], \"severity\": \"LOW/MEDIUM/HIGH\"}."
        )
        
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=system_prompt + "\n\nRecipe to audit:\n" + recipe_text,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
            )
            audit_data = json.loads(response.text)
            context["audit_results"] = audit_data
            
            if audit_data.get("has_issues"):
                msg = f"Audit found {len(audit_data['warnings'])} issues ({audit_data['severity']})."
                yield {"type": "status", "data": {"text": msg}}
            else:
                yield {"type": "status", "data": {"text": "Recipe cleared by Sin-Sieve."}}
                
        except Exception as e:
            print(f"Sin-Sieve failed: {e}")
            context["audit_results"] = {"has_issues": False, "warnings": []}
