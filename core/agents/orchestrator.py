import asyncio
import json
from typing import AsyncGenerator

from .sub_agents import PersonaGuard, InventoryScanner, FlavorArchitect

class ChefOrchestrator:
    """
    Main Orchestrator that coordinates PersonaGuard, InventoryScanner, and FlavorArchitect.
    Yields standard Server-Sent Events (SSE) format strings conforming to the 3-Tier Event System:
    - status
    - delta
    - final
    """
    def __init__(self):
        self.guard = PersonaGuard()
        self.scanner = InventoryScanner()
        self.architect = FlavorArchitect()

    async def process(self, context: dict) -> AsyncGenerator[str, None]:
        try:
            # 1. Persona Guard
            async for event in self.guard.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"
            
            if not context.get("is_safe", True):
                yield f"data: {json.dumps({'type': 'status', 'data': {'text': 'Process aborted due to safety policies.'}})}\n\n"
                return

            # 2. Inventory Scanner
            async for event in self.scanner.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"

            # 3. Flavor Architect (LLM Generation)
            async for event in self.architect.generate_stream(context):
                yield f"data: {json.dumps(event)}\n\n"

        except asyncio.CancelledError:
            # Re-raise to ensure proper cleanup upstream (e.g., session rollback in FastAPI)
            # The client disconnected mid-stream.
            raise
        except Exception as e:
            error_payload = {"type": "status", "data": {"text": f"Orchestrator error: {str(e)}"}}
            yield f"data: {json.dumps(error_payload)}\n\n"
