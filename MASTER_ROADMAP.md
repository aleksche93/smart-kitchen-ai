# Smart Kitchen AI - Master Roadmap

## Introduction
This document serves as the Single Source of Truth for the Smart Kitchen AI Ecosystem development, mapping the transition from a CLI-based Stateful Agent to a B2C Vue 3 SPA architecture utilizing native structured outputs.

## Completed Phases

### Phase 1: Microservice Migration ✅
- CLI to FastAPI REST API migration.
- Containerization via Docker & Docker Compose (`docker-compose.yml`, `Dockerfile`).

### Phase 2: State Persistence ✅
- SQLite and `aiosqlite` integration with async SQLAlchemy sessions.
- Stateful Chef memory (tracking FSM states and "cooking sins") using JSON columns.


### Phase 3: Hardware Ingestion ✅
- OCR receipt scanning via Gemini Vision (`scanner.py`, `POST /api/v1/scan-receipt`).
- Direct integration mapping physical scanned goods to the database (`my_fridge._Fridge__items`).

### Phase 4 & 5: Modern Vue 3 SPA (B2C Pivot) ✅
- Implemented "Neo-Ukrainian Warmth" B2C dark palette (Slate, `neoTerracotta`, `neoWheat`).
- Replaced legacy HTML templates with Vue 3 Teleport Modals and 3-Panel dynamic architecture (`AdviceDisplay.vue`, `FridgeList.vue`, `InteractionZone.vue`).

### Phase 5.1 & 6: Cognitive Persona Refinement & Safety ✅
- Built the "Flavor Bible" heuristics weighting.
- Dual-Mode API abstraction: decoupled target item validation to allow free-flow contextual chatting.
- Strict Pydantic sub-schemas enforced inside Gemini's Native Generator parsing.
- Universal Language Detection equipped with a rigid Anti-Russian Safety constraint.

### Phase 7: Interactive Multi-Recipe B2C Experience ✅
- Backend Schema Upgrade: Refactored `ChefResponse` to support multi-option `recipe_options: list[RecipeOption]`.
- Frontend Integration: Updated `AdviceDisplay.vue` to map the array structure using `v-for`.
- UI/UX Pattern: Implemented Selectable Recipe Cards and an Accordion-style layout for technical cooking instructions.

### Phase 8: Smart Kitchen Pipeline Synchronization ✅
- Established structured receipt parsing pipeline mapping LLM output directly to SQLite schema.
- Synchronized frontend UI to consume parsed receipt items directly, enforcing Single Source of Truth for the main inventory.

### Phase 9: System Integration & User Experience [100% COMPLETE] ✅
- Phase 9.1: Receipt Archive Infrastructure (Physical storage, Hash Duplication logic).
- Phase 9.2: Recovery & UI Expansion (SQLite wipe, UUID Schema, Gallery Frontend).
- Phase 9.3: UX & Native Rules Migration (Traceability Bridge, Pill Navigation, Agentic Native Architecture).
- Phase 9.4: Stability & Terminal UI (Data Reactivity, Ghosting Fix, Global ThoughtTicker).
- Phase 9.5: Vision Optimization & Enterprise Polish (High-Density Financials, Hybrid Cropper, Animated Split-View, AI Sanitization, Bag Skill).

### Phase 10.1: Workspace Mobility & Persistent Layouts [100% COMPLETED] ✅
- **Draggable UI Matrix**: Discarded rigid grid for a fluid `vuedraggable` layout, allowing end-user customization of component positioning and collapsed states.
- **State Persistence**: Wired `layoutStore.js` to SQL DB `ui_layout` table via `/api/v1/ui/layout` ensuring cross-session persistence of the customized dashboard.
- **Phase 10.1.5 Final Visual Polish**: Fixed UI "Drowning" with strict Widget max-heights (`500px`/`300px`), deployed precise `z-index` DND physics exclusively bound to drag activity, isolated `ThoughtTicker` as a distinct layout widget with 3s Slow Melt animation and auto-collapse DB syncing, and enforced codebase hygiene.
- **Phase 10.1.6 The Surgeon's Cut**: Refactored component hierarchy by anchoring `ThoughtTicker` directly inside `InteractionZone` (Command Hub) with a reactive `isConsoleOpen` toggle. Enforced high-density UI hygiene by swapping `WidgetWrapper` to `h-auto` and violently compressing `FridgeList` paddings. Wired live asynchronous Health Ping (`GET /api/v1/health`) to dynamic real-time textual UI indicator.
- **Phase 10.1.7 Grid Stabilization**: Executed backend SQLite orphan wipe (eradicating ghost IDs), anchored dimensional boundaries with strict `min-h-[450px]` bounds for primary modules, overhauled the ping network sequence to a recurring loop with `animate-pulse` error states, and finalized nomenclature to `[Chef’s Cognition HUD]`.

---

## Phase 10.2: Global Shell Migration & Telemetry Refactor [100% COMPLETED] ✅

### Objective
Relocate primary identity logic to a Global Header, evolve the Command Hub into a chat-first interface with integrated HUD telemetry, and optimize backend recipe mapping.

### Implementation Checklist
- ✅ Data & State Hygiene: Execute Pinia `WIDGET_REGISTRY` mapping to eradicate UI anomalies natively.
- ✅ Global Shell Refactor: Move `ChefAvatar` out of Grid into `App.vue` Top Header with embedded sub-options.
- ✅ Command Hub Pivot: Transform `InteractionZone` to pure Chat-first context with inline camera embedding. Drop unused legacy interface modals.
- ✅ Geometry Fixes: Limit cursor physics and adapt `AdviceDisplay` height to 100%. 
- ✅ Backend Telemetry: Upgrade Pydantic Models for structured logic variables `estimated_duration` and `recipe_complexity`.


### Phase 10.2.1: UI Stabilization & Logic Restoration [100% COMPLETED] ✅
- **Ghost Eradication**: Patched `app.py` startup routine to wipe any widget NOT strictly bounded by the `WIDGET_REGISTRY`. Checked and purged `App.vue` of legacy disconnected component tags.
- **Cognition Glassmorphism**: Repositioned `ThoughtTicker` inside the command hub with a `backdrop-blur` UI, open by default for OS transparency.
- **Fuzzy Inventory Diffing**: Connected `AdviceDisplay` to `useKitchenAPI()` directly to fuzzily cross-reference generated recipes against live Fridge inventory, injecting intuitive Green (✓) and Amber (+) UI signals.
- **Pill Architecture**: Hardcoded structural boundaries to the Interaction send button, solving animation jitter, and converted input to an organic `rounded-full` layout.

### Phase 10.2.3: Identity & Logic Finalization [100% COMPLETED] ✅
- **Kinetic Identity**: Refactored `ChefAvatar.vue` exclusively for the Global Header. Bound an infinite `@keyframes breathing` pulse logic directly to the SVG wrapper.
- **Emotive Header**: Linked the Dropdown `ChefAvatar` to an exhaustive `mood` prop, passing live `chefState.emotionDisplay` straight from the core engine.
- **Telemetry Precision**: Corrected `RecipeOption.estimated_duration` strict validation (String -> Integer). Mapped Vue HUD extraction (`{{ recipe.estimated_duration }} min`).
- **Pruning**: Validated zero-debt architecture in `FridgeList.vue` confirming legacy Ask-Chef hooks have been permanently severed.

### Phase 10.2.4: UI Density & Backend Integrity [100% COMPLETED] ✅
- **Avatar Glow**: Scaled keyframes to 1.08 max and injected a subtle `drop-shadow` mimicking physiological vitality. Locked the interactive identity header to strictly `onClick` events.
- **Mini-Chat Evolution**: Re-engineered `InteractionZone` into a Flex Column storing interactive arrays mapping previous queries and `chefState.adviceText`, condensing the footprint of the ThoughtTicker to gracefully absorb empty space.
- **Micro-Data Grids**: Scaled output recipes into grid architectures mapping `Quantity + Unit` explicitly while injecting mapped logical emojis contextually. Dynamic `emerald` rendering isolates pre-existing items visually.
- **The Jules Fix**: Overhauled FSM stub `delete_receipt_and_sync_inventory`. Generated native SQLAlchemy async operations implementing cascading purges to Inventory structures protecting DB integrity.

### Phase 10.2.5: The Sticky Soul & Layout Physics [100% COMPLETED] ✅
- **Chat-Centric UX:** Refactored `InteractionZone.vue` into a pure vertical "Messenger" structure pinning the Chat Input strictly to the bottom space with an isolated static top area for Action triggers.
- **Backend Triage Persona:** Re-tuned `persona.py` strictly forbidding redundant output of recipes directly into standard chat, enforcing a 2-3 sentence strict response limit.
- **Rendering Precision:** Eradicated the array-string breakdown bug (`1-letter bug`) by generating `normalizedIngredients` arrays. Embedded bold Emoji blocks for high readability data-density in `AdviceDisplay.vue`.
- **Intensified Kinetic Force:** Enhanced avatar pulsing `drop-shadow(0 0 10px)` mapped vividly over 1.08 max-scale `transform`.

### Phase 10.3: "Jules" Security & Performance Integration [100% COMPLETED] ✅
- **ORM Decoupling**: Refactored `models.py` by dissolving `cascade="all, delete-orphan"` from Receipt History relationships, securely utilizing `ondelete="SET NULL"` to preserve item persistence during historical receipt clearing.
- **SQL Hardening**: Sanitized system endpoints (like UI state manipulation) via strict SQLAlchemy bound-parameter `text()` executions, definitively closing injection vulnerability vectors.
- **Micro-Optimizations**: Streamlined dataloader bottlenecks within `get_fridge_inventory` by substituting CPU-expensive `try/except` iteration blocks with fast length-check string validations.
- **Zero-Build Testing**: Sculpted an external native Node.js test infrastructure mapping FSM state transitions locally without NPM or Vite dependencies, alongside deep Python backend behavioral validations utilizing `pytest`.
---

## Future Roadmap
- **Phase 11**: IoT Controller integration stubs, household inventory zone, and persistent web-push notifications.
