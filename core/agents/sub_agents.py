import json
import asyncio
from typing import AsyncGenerator
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .base import BaseChefAgent

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
            "You are the KozakEye Chef Orchestrator. "
            "You are generating a recipe, cooking instructions, or culinary advice. "
            "CRITICAL RULE: You MUST generate all content, instructions, and labels STRICTLY in English. "
            "Do NOT use Ukrainian or any other language in your output. "
            "Provide a well-structured markdown response."
        )
        
        user_prompt = f"User Request: {user_input}\nFridge Inventory:\n{inventory_summary}\n\nPlease generate the culinary response."

        full_text = ""
        try:
            response_stream = await client.aio.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=system_prompt + "\n\n" + user_prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )

            async for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text
                    yield {"type": "delta", "data": {"text": chunk.text}}
            
            # Final validation via Pydantic
            payload = FinalArtifactPayload(
                artifact_type="ORCHESTRATED_RESPONSE",
                content=full_text,
                metadata={"item_count": len(context.get("inventory", []))}
            )
            
            yield {"type": "final", "data": {"payload": payload.model_dump()}}

        except Exception as e:
            yield {"type": "status", "data": {"text": f"Error generating flavors: {str(e)}"}}
