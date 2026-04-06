# Smart Kitchen AI - Master Roadmap

## Introduction
This document serves as the Single Source of Truth for the Smart Kitchen AI Ecosystem development, mapping the transition from a CLI-based Stateful Agent to a B2C Vue 3 SPA architecture utilizing native structured outputs.

## Completed Phases (1-6)

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

---

## Current Phase: Phase 7 (Interactive Multi-Recipe B2C Experience)

### Objective
Transition the Chef's response from a single forced monolithic recipe into an interactive, multi-option structure that presents 3 distinct culinary variations for the user to choose from.

### Implementation Checklist
- [ ] **Backend Schema Upgrade:** Refactor `ChefResponse.recipe` into `recipe_options: list[RecipeOption]`.
- [ ] **Frontend Prop Drilling:** Update `AdviceDisplay.vue` to map the new array structure using `v-for`.
- [ ] **UI/UX Pattern:** Implement Selectable Recipe Cards and an Accordion-style layout for technical cooking instructions.

---

## Future Roadmap
- **Phase 8:** Pantry and Freezer routing (non-perishables orchestration).
- **Phase 9:** IoT Controller integration with the `ActionStub` pipeline.
