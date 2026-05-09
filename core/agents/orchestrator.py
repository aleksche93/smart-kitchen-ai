import asyncio
import json
from typing import AsyncGenerator

from .sub_agents import PersonaGuard, InventoryScanner, FlavorArchitect, SinSieveAgent
from core.services.flavor_service import get_harmony_score, get_pairing_tips

class ChefOrchestrator:
    """
    Main Orchestrator that coordinates PersonaGuard, InventoryScanner, 
    FlavorArchitect, and SinSieveAgent.
    """
    def __init__(self):
        self.guard = PersonaGuard()
        self.scanner = InventoryScanner()
        self.architect = FlavorArchitect()
        self.sieve = SinSieveAgent()

    async def process(self, context: dict) -> AsyncGenerator[str, None]:
        try:
            # 1. Persona Guard
            async for event in self.guard.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"
            
            if not context.get("is_safe", True):
                return

            # 2. Sin-Sieve (Input Audit - Aggressive Firewall)
            async for event in self.sieve.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"
            
            if not context.get("is_safe", True):
                return

            # 3. Inventory Scanner
            async for event in self.scanner.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"

            # 4. Flavor Architect (Narrative & Delta)
            final_artifact_event = None
            async for event in self.architect.generate_stream(context):
                if event['type'] == 'final':
                    final_artifact_event = event
                else:
                    yield f"data: {json.dumps(event)}\n\n"

            # 5. Sin-Sieve (Output Audit - Content Polish)
            async for event in self.sieve.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"

            # 5. Enrichment (Harmony Score)
            if final_artifact_event and context.get("ingredients"):
                harmony = get_harmony_score(context["ingredients"])
                tips = get_pairing_tips(context["ingredients"])
                
                # Enrich metadata
                final_artifact_event['data']['payload']['metadata']['harmony_score'] = harmony
                final_artifact_event['data']['payload']['metadata']['pairing_tips'] = tips
                final_artifact_event['data']['payload']['metadata']['audit'] = context.get("audit_results")

            # 6. Final Yield
            if final_artifact_event:
                yield f"data: {json.dumps(final_artifact_event)}\n\n"

        except asyncio.CancelledError:
            raise
        except Exception as e:
            error_payload = {"type": "status", "data": {"text": f"Orchestrator error: {str(e)}"}}
            yield f"data: {json.dumps(error_payload)}\n\n"
