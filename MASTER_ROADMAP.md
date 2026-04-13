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
- **Final Visual Polish**: Implemented "melting" animations for AI status tickers, dynamic `z-index` layering during Drag & Drop, and strict Action Button state machines for the core UX.

---

## Current Phase: Phase 10.2 (Advanced Dashboard & IoT Base)

### Objective
Expand the dynamic OS-like workspace, refine the existing modules (including the Bag Skill Fun Module), and prepare the frontend infrastructure for scaling to non-perishable categories.

### Implementation Checklist
- [ ] TBD: Awaiting context or new directives for Phase 10.2.

---

## Future Roadmap
- **Phase 11**: IoT Controller integration stubs, household inventory zone, and persistent web-push notifications.
