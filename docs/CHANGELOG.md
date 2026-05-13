# Changelog KozakEye

All notable changes to the KozakEye Smart Kitchen AI project will be documented in this file.

## [Phase 14.4 Jules Audit Integration] - 2026-05-13
### Security & Architecture Fixes
- **Empty Artifact Fix:** Patched `InteractionZone.vue` (`upsertArtifact` and `executeMagic`) to strictly check `Object.keys(metadata).length > 0` before prioritizing it over the full payload.
- **CORS Hardening:** Removed wildcard `"*"` from `allow_origins` in `app.py`, restricting access strictly to trusted local development origins (`http://localhost:5173` and `http://127.0.0.1:5173`).
- **N+1 Query Performance:** Refactored `get_harmony_score` in `flavor_service.py` to batch ChromaDB queries by passing the entire `ingredients` array to `query_texts`, drastically reducing I/O overhead.
- **Traceback Exposure:** Replaced unsafe `traceback.print_exc()` with sanitized `logging.error(..., exc_info=False)` in `smart_fridge.py`, `sub_agents.py`, and `orchestrator.py` to prevent architecture leaks to logs.
- **XSS Prevention:** Removed `v-html` for user messages in the chat interface, replacing it with secure text interpolation (`{{ msg.content }}`).
- **Stream Pacing:** Removed artificial `asyncio.sleep` blocks from the backend `/kinec` generator, offloading typing animations entirely to the frontend.
- **Code Hygiene:** Removed unused `AnalyticsItemReport` import from `smart_fridge.py`.
- **Test Coverage:** Added `test_security_cors.py` and `test_flavor_service.py` to ensure long-term stability of the newly implemented constraints.

## [Phase 14.3 Final Hotfix] - 2026-05-13
### Fixed
- **Fatal Database Crash:** Resolved an `AttributeError` during `/kinec` session termination by ordering `ChatMessageModel` queries by `.id` instead of a non-existent `.created_at` column.
- **Empty /kinec Bubble:** Fixed the frontend filtering issue by ensuring the `intent: "CHAT"` property is explicitly included in both the `status` and `delta` payloads during the session termination stream.
- **Thought Trace Spam:** Suppressed repetitive `[The X-Ray Buddy]` warnings by adding an `is_first_message` check in the Orchestrator, ensuring proactive inventory scans only appear in the UI on the first message of a session.

## [Phase 14.2 Hotfix] - 2026-05-12
### Fixed
- **F5 State Hydration:** Updated `saveChatToStorage` in `InteractionZone.vue` to properly serialize the `thoughts` array and `thoughtsCollapsed` state, preventing thought trace loss on page reload.
- **Session History Deletion:** Removed the destructive `delete(ChatMessageModel)` call from `/kinec` to retain historical chat logs for future features (e.g., chat history sidebar).
- **Stream Pacing:** Improved the `/kinec` summary stream by tokenizing the string and yielding words with an explicit delay to match the frontend's natural typing simulation.

## [Phase 14.1] - 2026-05-12
- **Instant Visual Feedback:** Introduced immediate `COOKING` and `ANALYZING` avatar states triggered before backend fulfillment for Magic Button and Receipt Scanning.
- **Localized /kinec Summaries:** Session termination now dynamically generates farewell messages matching the user's input language, preserving cultural context.

### Changed
- **Intent Classifier Re-balancing:** Retuned `IntentClassifierAgent` to instantly route pure inventory queries (e.g., "What's in my fridge?") to the `ANALYTICS` artifact, bypassing the Chat Clarification loop.
- **Morphing Send Button:** Upgraded the chat input button to feature a realistic professional chef's knife SVG that intelligently morphs into a stop button exclusively on hover during stream processing.
- **Inline Button Hygiene:** The inline "Generate Recipe" button now automatically hides itself from the message history once clicked.

### Fixed
- **Empty /kinec Bubble:** Resolved the visual "black hole" during session termination by yielding the summary via `delta` events before the database is cleared.

## [Phase 14.0] - 2026-05-12
- **Session Termination Ritual:** New `/kinec` command that performs automated session end-of-life: trait extraction, memory update, and chat clearing.
- **User Trait Extraction:** Integrated `extract_user_traits` helper using `gemini-2.5-flash` to analyze psychological and culinary profiles (preferences, personality, skill level) from chat history.
- **Contextual Magic Button:** The "Generate Recipe" button is now tied to specific messages via `hasMagicAction` property, preventing UI "ghosting" and improving contextual flow.

### Changed
- **Clarification Loop UX:** Re-tuned `IntentClassifierAgent` to aggressively favor `CHAT`. The Chef now prioritizes discussion and clarification before triggering artifact generation.
- **Magic Trigger Protocol:** The `MAGIC_TRIGGER` signal now requires explicit user confirmation within the chat history to prevent premature artifact generation.
- **Backend Language Standard:** Enforced strict English-only system messages in `api/smart_fridge.py` final events.

## [Phase 13.6] - 2026-05-10
### Added
- **Thought Trace UI:** Native `<details>` element in chat bubbles to display Chef's reasoning (`ui_thought` streaming) without cluttering the chat.
- **Agent Personas:** The Orchestrator now maps sub-agents to snarky personas in the Thought Trace (e.g., `[X-Ray Buddy]`, `[The Mad Alchemist]`, `[The Fun Police]`).
- **Avatar Persistence:** Chef's state (IDLE/COOKING) is now saved in `localStorage` with a 15-minute TTL via Pinia `layoutStore`.
- **i18n Keys:** Added missing localizations for Analytics and Recipe UI.

### Changed
- **Analytics UI:** Completely redesigned `AnalyticsArtifact.vue` into a glanceable, compact grid with status chips (Critical/Warning/Fresh) instead of wide table rows.
- **Message Merging:** Artifact confirmation messages (e.g., "Recipe is ready") are now merged into the existing Thought Trace bubble instead of spawning a new empty bubble.
- **Send Button Morphing:** Replaced the chat input button with a rotating "Chef's Knife" 🔪 SVG that morphs into a "Stop" button during stream processing.
- **Recipe Artifact UX:** Missing ingredients are now displayed as elegant UI chips with a snarky Chef commentary instead of raw text.

### Fixed
- **Ghost Items (Database):** Fixed a critical bug where items with `0` quantity remained in Analytics. Added hard `await session.commit()` and filtering logic to physical SQLite deletion endpoints.
- **SSE Stream Parser:** Resolved a `SyntaxError` caused by escaped `\n\n` in Python's Orchestrator `yield` statements, ensuring robust chunk buffering in Vue.
- **Vue Scoping:** Fixed `renderContent` runtime compilation errors in `InteractionZone.vue`.
- **Receipt Scanner:** Upgraded to `gemini-2.5-flash` with robust `mime_type` handling to prevent 500 Internal Server Errors.

## [Phase 13.5] - 2026-05-05
### Added
- **Sin-Sieve Alert System:** Integrated a rich HTML alert parser for Sin-Sieve markdown blocks.
- **Avatar State Persistence:** Implemented persistent `chefStatus` with `localStorage` TTL.

### Changed
- **Database Integrity:** Hardened `DELETE` and `/cook` endpoints with explicit `session.commit()` and float-tolerance filters. Manual delete now supports Name lookup.
- **UI Hygiene:** Synchronized `en.json`/`uk.json` with missing keys and fixed `ArtifactCard.vue` overflows.

### Fixed
- **InteractionZone Restoration:** Fixed Vue scoping (`renderContent`) and initialized `layoutStore`.
- **UX Anomalies:** Resolved `setRecipe` crash, fixed AdviceDisplay overlay intent logic, and restored Magic Button ✨.

## [Phase 13.4] - 2026-04-28
### Added
- **Confirmation Messages:** `InteractionZone.vue` `onFinal` now pushes localized assistant bubbles for RECIPE/ANALYTICS.
- **Thought Trace Persistence:** Replaced `<Transition>` with native `<details>`/`<summary>`. Thoughts stay in DOM, collapse on first delta, remain expandable.

### Changed
- **Thought Trace Filter:** Added `_UI_THOUGHT_BLOCKLIST` to `orchestrator.py` `_tag_thought()`. Technical intents explicitly denied.

### Fixed
- **Vue Compiler Fix:** `AnalyticsArtifact.vue` rewritten as pure SFC to eliminate inline string templates.
- **LLM Math Fix:** Python now performs 100% of math in `AnalyticsAgent`. Gemini solely writes a witty summary sentence.

## [Phase 13.3] - 2026-04-20
### Added
- **ANALYTICS Intent:** New `AnalyticsAgent` generates structured `InventoryReportArtifact`.
- **`AnalyticsArtifact.vue`:** Modular component with stats grid and CRITICAL/WARNING/FRESH tiers.
- **Thought Trace UI:** `InteractionZone` renders ⚙️ thought trace per bubble, fades out on first delta.

### Changed
- **Pydantic Safety:** Defined `AnalyticsItemReport` + `AnalyticsReportSchema` before routing (eliminates 500 errors).
- **Morphing Send/Stop Button:** Single button (paper-plane ↔ stop-square) prevents layout shifts.

### Fixed
- **SSE Parser Fix (CRITICAL):** Fixed `\\n\\n` escaped newline in `orchestrator.py`. Rewrote `useChefStream.js` with proper accumulator buffer.

## [Phase 13.2] - 2026-04-12
### Added
- **Conversational Memory:** `chat_history` (last 10 msgs) sent in payload for multi-turn context.
- **Proactive Inventory Logic:** `InventoryScanner` tags expiring items; Magic Button generates "Chef's Special" from them.

### Changed
- **Unified Endpoint:** ALL chat + magic requests route through `/api/v1/chef/process`. Old `/chef/chat` deprecated.
- **Stream Routing:** Orchestrator broadcasts `intent` in first `status` event.

## [Phase 13.1] - 2026-04-05
### Added
- **Stop Control:** Integrated `AbortController` UI for instant stream termination.
- **Language Switcher:** Integrated EN/UA toggle into the Chef Identity menu.

### Changed
- **Localization Sync:** Multi-language HUD keys integrated via `i18n`. Cleaned locales (English as default).
- **Ticker Persistence:** Refactored `ThoughtTicker.vue` for permanent visibility.

### Fixed
- **UI Stabilization:** Eradicated render crashes in `i18n.js` by hardening the translation engine against malformed regex.

---

## [Historical Archive: STAGE II] - Orchestration & Spatial OS

### Phase 12.6: UI & Logic Stabilization
- Restored KozakEYE Branding (Iris kinetic indicator, keYellow).
- Switched Thought Ticker to classic `-` minimize button and fixed drag-and-drop.
- Added manual "Clear Artifacts" utility in Chef's dropdown.

### Phase 12.5: Audit Cleanup (Sprint A)
- Complete cleanup of CSS variables to `--ke-`.
- Embedded Thought Ticker collapse button natively and bound state to `layoutStore`.
- Fixed `useDraggable.js` scale/zoom anchor logic to prevent widget displacement.

### Phase 12.4: System Integrity & KozakEye OS
- Enforced strict 1440px workspace lockdown via `Math.clamp`.
- Implemented `localStorage` hydration for active artifacts in `layoutStore.js`.
- Re-branded to KozakEye OS, strictly enforced English artifact headers.

### Phase 12.2: Spatial OS & Troll Chef Refinement
- Removed `vuedraggable` grid layout from `App.vue`, moved to true 2.5D Spatial Desktop (`position: absolute`).
- Implemented The Dock in the Top Header for minimizing/restoring widgets.
- Enhanced Fleeing Button math in `RecipeArtifact.vue` using exact bounding constraints.

### Phase 12.1: Living Soul Evolution
- Humanized SSE + Kinetic Typing with multi-lingual auto-detection.
- Implemented Polymorphic Artifacts (Recipe, Shopping List, Waste Alert) and the "Magic Bridge" ✨ trigger.
- Dynamic Advice Panel resizing and focus overlays with backdrop blurs.

### Phase 11.1 - 11.2: Memory Infra & Spatial UI
- Integrated ChromaDB and `sentence-transformers` for local embeddings.
- Refactored `/chat` endpoint to use Server-Sent Events (SSE) with emotion metadata.
- Implemented Spatial Memory (STM & LTM) with background `extract_and_store_traits` via ChromaDB.

### Phase 10.4: Interaction Decoupling & Persona Sandbox
- FSM validation tests, Native XSS Shield in `AdviceDisplay.vue`.
- Eradicated N+1 query bottlenecks via bulk SQLAlchemy deletion.
- Created Pinia Sarcastic Idle Engine and intent triage (Magic Trigger).

---

## [Historical Archive: STAGE I] - Stable Foundation

### Phases 7 - 10.3: System Polish & The "Jules" Protocol
- **App Lifecycle:** Replaced `@app.on_event("startup")` with SQLAlchemy 2.0+ compliant `lifespan` managers.
- **Security:** SQL Hardening via strict bound-parameter `text()` executions, definitively closing injection vectors.
- **UI Evolution:** Draggable UI Matrix, Chat-Centric UX, Emotive Identity Header, and Micro-Data Grids.
- **Architecture:** Global Shell Migration, backend telemetry upgrade, and zero-debt widget architecture.

### Phases 4 - 6: Modern SPA & Cognitive Persona
- Replaced legacy HTML templates with Vue 3 Teleport Modals and 3-Panel dynamic architecture.
- Built the "Flavor Bible" heuristics weighting and dual-mode API abstraction.
- Strict Pydantic sub-schemas enforced inside Gemini's Native Generator parsing.

### Phases 1 - 3: Inception & Hardware Ingestion
- Migrated from CLI to FastAPI REST API, containerized via Docker.
- Stateful Chef memory tracking FSM states using JSON columns in SQLite.
- OCR receipt scanning via Gemini Vision with direct database integration.
