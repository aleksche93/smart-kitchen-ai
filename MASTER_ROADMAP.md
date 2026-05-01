# 🗺️ MASTER ROADMAP: Smart Kitchen AI OS (2026)

## 🏁 STAGE I: STABLE FOUNDATION (PHASES 1–10.3.1) — `[100% COMPLETED]`
*This block is a closed technological asset. The entire infrastructure is deployed and operational.*

- [x] **Backend Core:** FastAPI, asynchronous architecture (SQLAlchemy 2.0, aiosqlite).
- [x] **Lifecycle Management:** Implementation of `lifespan` for safe connection/disconnection of resources and DB.
- [x] **Vision Ingestion:** Gemini Vision API for receipt scanning with SHA-256 deduplication.
- [x] **Security (Jules Protocol):** Full input sanitization, SQL bound parameters, injection protection.
- [x] **UI Framework:** Vue 3 (Dark Mode), Draggable UI Matrix, Pinia for state management.
- [x] **DevOps:** Docker containerization, GitHub Sync, `.env` isolation.

<details>
<summary><b>View Detailed History (Phases 1 - 10.3.1)</b></summary>

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

### Phase 10.3.1: Application Lifecycle Refactoring [100% COMPLETED] ✅
- **Lifespan Migration**: Replaced deprecated `@app.on_event("startup")` events in `app.py` with SQLAlchemy 2.0+ compliant `lifespan` contextual managers, guaranteeing clean database connectivity startup and graceful teardown (`engine.dispose()`).
- **Resource Insulation**: Abstracted dynamic routing and persistent volume paths safely outside the immediate logic boundary of Starlette to prevent API boot deadlocks.
- **Static Analysis Compliance**: Standardized variable sequence in `app.py`, ensuring all global constants (`DEFAULT_USER_ID`) and resource managers (`lifespan`) are defined before their respective references, resolving 30+ linter warnings.
- **Robust Documentation**: Integrated updated documentation tracking modern API boot processes.

</details>

---

## 🚀 STAGE II: INTERACTION & ORCHESTRATION (PHASES 10.4–11) — `[PRIORITY №1]`
*Transition to "Chef as Orchestrator" architecture. Separation of communication logic and task execution.*

### Phase 10.4: Interaction Decoupling & Persona Sandbox `[100% COMPLETED]`
- [x] **"Jules" Security & Observability (Batch 1):** Implemented FSM validation tests, Native XSS Shield in `AdviceDisplay.vue`, and added explicit `lifespan` initialization logging.
- [x] **"Jules" Performance & Robustness (Batch 2):** Eradicated N+1 query bottlenecks via bulk SQLAlchemy deletion (`delete_receipt_and_sync_inventory`) and secured locales JSON parsing.
- [x] **"AI Brigade" UX Sync & Strategic RAG Update (Batch 3):** Established FSM-Pinia reactivity, enforced strict i18n for scanning feedback, and added 5MB client-side constraints.
- [x] **"Sarcastic Reactivity & Ghost State" (Batch 3.1):** Created a Pinia Sarcastic Idle Engine, fixed global dimensional layout scrolling (CSS h-auto overrides), and developed frontend memory maps ("Ghost Metadata") for orphaned bulk-deleted receipts.
- [x] **Layout Architecture & Logic Decoupling (Batch 4):** Refactored AI JSON payloads to separate `chat_message` from `technical_data`. Implemented Fullscreen Responsive Grid (`w-full`, `grid-cols-2`/`grid-cols-3`) and extracted Receipt Parsed Data to a floating Teleport overlay.
- [x] **The "Living OS" Polish (Batch 5):** Added Kinetic Typography (`useTypewriter`) with randomized typos, integrated `@container` queries for dynamic density in `FridgeList.vue`, and implemented Intent Triage (Magic Trigger ✨) for heavy recipe queries.
- [x] **Density & Chat Logic Fixes (Batch 5.1):** Separated `/api/v1/chef/chat` for plain lightweight conversation from heavy RAG recipe generation. Stabilized adaptive grids with pixel-perfect `@container` thresholds in both Fridge and Advice widgets.


### Phase 11.1: Memory Infra & API Optimization [100% COMPLETED] ✅
- [x] **Infrastructure Alignment:** Integrate ChromaDB (8001:8000) and `sentence-transformers` for local embeddings.
- [x] **Persistence & Models:** Add spatial metadata (`z_index`, `rotation_angle`) to `UILayoutModel` and refactor `ChefSessionModel` (`id`, `user_id`, `topic`, `summary`, `created_at`, `recent_triggers`, `ui_events`).
- [x] **API Modularization:** Migrate `get_chef_advice` into a dedicated `api/smart_fridge.py` router.
- [x] **N+1 Optimization:** Implement `generate_batch_recipe` using a single Gemini 3.1 Flash LLM call to process all expiring items simultaneously.

### Phase 11: Cognitive Brain & Agentic Orchestrator
- [x] **Local Inference Architecture:** Successfully deployed local inference pipeline for Flavor Bible parsing using Gemma 4 via Ollama.
- [x] **Autonomous Knowledge Extraction:** Implemented specialized Python ETL scripts optimized by Gemini Code Assist for automated JSON knowledge extraction.
- [ ] **Chef as Orchestrator:** Transform the Chef into a controlling model that asynchronously calls agents (Scanner, Generator, Inventory Analyst).
- [ ] **Vector DB & Flavor Bible:** Creation of a vector knowledge base (e.g., Qdrant/Chroma) for dynamic flavor pairing search.
- [ ] **Flavor Harmony Score:** Algorithm for evaluating ingredient compatibility (Weighting 1.0 - 4.0) based on RAG.
- [ ] **Persona RAG & Hardening:** Connecting the knowledge base to the Chef's Brains to prevent hallucinations. Setting up sarcastic redirects for off-topic requests.
- [ ] **The "Sin-Sieve" Agent:** Autonomous agent for detecting errors in recipes (e.g., `protein_chaos`).
- [ ] **Smart Receipt 2.0:** Transition to proactive financial analytics (Unit price tracking, categorical normalization).
- [ ] **Agentic Skill Interface:** Standardization of the interaction protocol between the Chef and his "Workers".

---

## 🎮 STAGE III: LIVE HUD & JUICY UX (PHASE 12)
*Visualization of the AI's "thought process" and enhancement of emotional response.*

- [ ] **Instant Avatar Transitions:** Transition to instantaneous changes in the avatar's emotional states upon trigger (no delays).
	- [ ] **Kinetic Identity v2:** Deepened avatar animation (branding, shadow pulsation, emotion dependency).
- [ ] **Persistent Persona State:** Saving the Chef's emotional state and context between page reloads (Redis/LocalStorage).
- [ ] **Live Thought Ticker 2.0:**
	- [ ] Relocation of the ticker to the upper zone (closer to the avatar, but without rigid attachment to the header).
    - [ ] Visualization of asynchronous agent work (status-stream: "Chef is thinking...", "Scanner Agent is working...", "Generator is forming a response...").
    - [ ] Global "thoughts" terminal widget for the Chef (FSM state log + Zen Mode).
- [ ] **Visual Polish:** Strengthening color indication of states and updating animations (preparation for 3D-Kozak implementation).
- [ ] **Processing Feedback:** Contextual animations (🔪 for slicing, 🥘 for cooking) instead of standard spinners.

---

## 🏗️ STAGE IV: ECOSYSTEM & SKILLS (PHASES 13–14)
*Expanding capabilities through specialized modules.*

### Phase 13: Capability Expansion
- [ ] **Skill: Recipe Generator:** Transforming the generator into an autonomous asynchronous tool with its own instructions.
- [ ] **Skill: Bag Management:** Module for tracking consumable materials ("bag of bags").
	- [ ] **Bag Skill (Skill-Based Architecture):** Separate skill for the "bag of bags" (`FunModuleBagModel` DB, visual widget).
- [ ] **Search Trigger:** Function to invoke external search (Google Search/Gemini) through the Chef for complex queries.
- [ ] **Financial Analyst Agent:** Proactive analytics of supermarket prices and offers.
- [ ] **Loyalty-Tracker:** Agent that aggregates supermarket bonuses (_Silpo_, _ATB_) from OCR data.
- [ ] **Chrono-Mise-en-place:** Visual timeline planner for parallel cooking processes.

### Phase 14: Hands-Free and IoT Integration
- [ ] **Voice Interaction:** Web Speech API (STT/TTS) — voice control of recipe steps.
- [ ] **IoT Controller Stubs:** Creation of API endpoints for future integration with Home Assistant (ovens, refrigerators).
- [ ] **Persistent Web-Push:** Notifications about product expiration dates directly to desktop/mobile.

---

## 🌌 STAGE V: NEXT-GEN AI & VISUALIZATION (PHASE 15+)
*Future of the project: 3D, Edge Computing, total privacy, full autonomy, and immersion*

- [ ] **Digital Twin (3D Kitchen):** Kitchen visualization via Three.js/Rive. Animated 3D-Chef moves between modules depending on system state.
- [ ] **Edge Computing (Local AI):** Migration of analytics to **Gemma 4** (via WebGPU/AI Edge) to ensure 100% data privacy (Local Privacy First).
- [ ] **Vision Mentor:** Video stream analysis of cooking (Computer Vision) for real-time user training in slicing techniques.
- [ ] **Imagen 3 Integration:** Generation of photorealistic food images based on recipes created by the Chef.

---

## 📉 DIFF ANALYSIS (What changed?)

| **Category** | **What was removed / changed** | **Reason** |
|---|---|---|
| **Completed** | "Migration to FastAPI", "SQL Hardening", "Lifespan managers" | These items were moved from "Future" to "Completed" (Phase 10.3.1 successfully closed). |
| **Merged** | "Flavor Bible" + "Flavor Harmony Score" | This is a single entity. Harmony Score is a metric derived from RAG database integration. |
| **Refined** | "Bag Skill" | In Phase 9.5, this was an idea; here it is highlighted as a separate module in Stage III (skills architecture). |
| **Deleted** | "Firebase/Firestore Migration" | Decided to leave this as an option, but focus shifted to **Local AI (Gemma 4)** and **Edge Computing** for privacy. |
| **Clarified** | "Thought Ticker" | Merged the idea of "Chat-first" and "Console UI" into a single Global Thought Ticker. |
