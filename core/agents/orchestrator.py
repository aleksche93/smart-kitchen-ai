import asyncio
import json
from typing import AsyncGenerator

from .sub_agents import (
    PersonaGuard,
    InventoryScanner,
    FlavorArchitect,
    SinSieveAgent,
    IntentClassifierAgent,
    ConversationalAgent,
    AnalyticsAgent,
)
from core.services.flavor_service import get_harmony_score, get_pairing_tips

# Status messages that are UI-visible (content-aware thoughts for Thought Trace).
# Technical routing messages are filtered out — not listed here.
_UI_THOUGHT_PREFIXES = (
    "Chef is",
    "Scanning",
    "Analyzing",
    "Categorizing",
    "Checking",
    "Warning:",
    "Fridge is empty",
    "Inventory looks",
    "Chef rejected",
    "Blocked:",
)

# Explicit blocklist — these must NEVER reach the UI thought trace.
# They are internal technical logs, not chef narrative.
_UI_THOUGHT_BLOCKLIST = (
    "Intent:",
    "Classifying",
    "Sin-Sieve is auditing",
    "Intent verified",
)


def _sse(event: dict) -> str:
    """Serialize a dict to a valid SSE data line with proper \\n\\n delimiter."""
    return f"data: {json.dumps(event)}\n\n"


class ChefOrchestrator:
    """
    Single Source of Truth for all AI processing.
    Coordinates the full agent pipeline: Guard → Sieve → Classify → Route → Generate → Audit.

    Stream protocol (SSE event types):
      - status: {"type": "status", "data": {"text": "...", "intent"?: "CHAT"|"RECIPE"|"ANALYTICS", "ui_thought"?: true}}
      - delta:  {"type": "delta",  "data": {"text": "...", "intent": "CHAT"|"RECIPE"|"ANALYTICS"}}
      - final:  {"type": "final",  "data": {"payload": {...}}}

    The frontend routes delta chunks based on the 'intent' field:
      CHAT      → append to last assistant chat bubble (InteractionZone), typing effect
      RECIPE    → render in AdviceDisplay streaming view
      ANALYTICS → render in AdviceDisplay, emit as ANALYTICS artifact on final
    """

    def __init__(self):
        self.guard = PersonaGuard()
        self.scanner = InventoryScanner()
        self.classifier = IntentClassifierAgent()
        self.chat_agent = ConversationalAgent()
        self.architect = FlavorArchitect()
        self.analytics = AnalyticsAgent()
        self.sieve = SinSieveAgent()

    def _tag_thought(self, event: dict) -> dict:
        """
        Tags a status event as ui_thought=True if its text is a content-aware
        narrative thought (visible in the Thought Trace bubble).

        Blocklist takes priority — technical routing logs are never shown to users.
        """
        if event.get("type") != "status":
            return event
        text = event.get("data", {}).get("text", "")
        # Blocklist check first — explicit deny
        if any(text.startswith(b) for b in _UI_THOUGHT_BLOCKLIST):
            return event  # NOT a ui_thought
        # Prefix allowlist check
        is_ui_thought = any(text.startswith(p) for p in _UI_THOUGHT_PREFIXES)
        if is_ui_thought:
            return {**event, "data": {**event["data"], "ui_thought": True}}
        return event

    async def process(self, context: dict) -> AsyncGenerator[str, None]:
        try:
            # ── 1. Persona Guard (basic heuristic shield) ────────────────────
            async for event in self.guard.generate_stream(context):
                yield _sse(self._tag_thought(event))

            if not context.get("is_safe", True):
                return

            # ── 2. Sin-Sieve — Input Audit (Fail-Fast firewall) ──────────────
            async for event in self.sieve.generate_stream(context):
                yield _sse(self._tag_thought(event))

            if not context.get("is_safe", True):
                return

            # ── 3. Intent Classification ─────────────────────────────────────
            yield _sse({"type": "status", "data": {"text": "Classifying intent..."}})
            intent = await self.classifier.classify(context)

            # Broadcast intent so frontend configures routing — NOT a ui_thought (technical)
            yield _sse({"type": "status", "data": {"text": f"Intent: {intent}", "intent": intent}})

            # ── 4. Inventory Scanner (all paths need fridge context) ──────────
            async for event in self.scanner.generate_stream(context):
                yield _sse(self._tag_thought(event))

            # ── 5a. ANALYTICS path ───────────────────────────────────────────
            if intent == "ANALYTICS":
                async for event in self.analytics.generate_stream(context):
                    yield _sse(self._tag_thought(event))
                return  # EXIT — no recipe generation needed

            # ── 5b. CHAT path ────────────────────────────────────────────────
            if intent == "CHAT":
                async for event in self.chat_agent.generate_stream(context):
                    yield _sse(self._tag_thought(event))
                return  # EXIT — no artifact generation needed

            # ── 5c. RECIPE path — Flavor Architect ───────────────────────────
            final_artifact_event = None
            async for event in self.architect.generate_stream(context):
                if event["type"] == "final":
                    final_artifact_event = event
                else:
                    yield _sse(self._tag_thought(event))

            # ── 6. Sin-Sieve — Output Audit (RECIPE only) ────────────────────
            async for event in self.sieve.generate_stream(context):
                yield _sse(self._tag_thought(event))

            # ── 7. Enrichment — Harmony Score & Pairing Tips ─────────────────
            if final_artifact_event and context.get("ingredients"):
                harmony = get_harmony_score(context["ingredients"])
                tips = get_pairing_tips(context["ingredients"])

                payload = final_artifact_event["data"]["payload"]
                payload.setdefault("metadata", {})
                payload["metadata"]["harmony_score"] = harmony
                payload["metadata"]["pairing_tips"] = tips
                payload["metadata"]["audit"] = context.get("audit_results")

            # ── 8. Final yield ────────────────────────────────────────────────
            if final_artifact_event:
                yield _sse(final_artifact_event)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            import traceback
            print(f"[ChefOrchestrator] Unhandled error:\n{traceback.format_exc()}")
            yield _sse({"type": "status", "data": {"text": f"Orchestrator error: {str(e)}"}})
