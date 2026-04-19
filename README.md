# 🍳 Smart Kitchen AI Ecosystem (Stateful Autonomous Agent)

An asynchronous, multimodal AI agent built to optimize kitchen inventory, reduce food waste, and provide real-time culinary orchestration using **Google Gemini Pro API**, **Agentic RAG**, and **FastAPI**.

Unlike typical stateless AI wrappers, this ecosystem features a **Stateful Artificial Persona**. The AI "Chef" possesses memory, emotional states (managed via a Finite State Machine), and tracks user preferences across sessions.

## 🧠 Core Architecture & Features

1. **Stateful AI Memory (SQLite + SQLAlchemy):** User habits, "cooking sins", and the Chef's emotional state (FSM) are persisted locally via async database sessions, mapped against safe backend cascade purges (The "Jules" Architecture).
2. **Structured Tool Calling:** Forces the LLM to return strictly typed JSON responses (`ChefResponse`), including actionable stubs (`tool_commands`) designed for future IoT Smart Home integration.
3. **Neo-Ukrainian Premium SPA:** A Vue 3 B2C Frontend utilizing Tailwind CSS and `<Teleport>` modals. It embraces a "Neo-Ukrainian Warmth" dark palette (Slate, Terracotta, Wheat) to provide an immersive 3-panel user interface.
4. **Dual-Mode Chat & Teleportation:** Interaction logic is cleanly divided. General chat runs via the main hub, while targeted ingredient recipes are triggered cleanly via isolated Item Modals utilizing Vue's Teleport feature.
5. **Modular UI Architecture & Workspace Mobility:** Fully decouple widgets using a Stateful Draggable Grid powered by Pinia and SQLite. Users can drag and reorder their dashboard, with complete persistence saved between sessions.
6. **Agentic RAG:** Asynchronously fetches "classic flavor pairings" from a local knowledge base (The Flavor Bible) to rescue expiring ingredients.

## 👁️ Advanced Vision Pipeline & Security (Phase 9 Integration)
The ecosystem features a robust, enterprise-grade ingestion engine for digitizing physical grocery receipts:
- **Hybrid Vision Processing:** A powerful combination of the native HTML5 Canvas API for user-guided interactive cropping (grayscale pixel manipulation, contrast enhancement) and **Gemini 2.5 Flash** for high-accuracy OCR structural extraction.
- **Security (Agent Trap Mitigation):** Implementation of a zero-trust AI sanitization layer. Text extracted from physical media is treated strictly as raw data, completely neutralizing malicious prompt injection attempts (e.g., "Ignore previous instructions").
- **Semantic Grounding (UAH Anchor):** Context-aware heuristic logic that identifies Native Store Profiles (e.g., *Сільпо*, *АТБ*) directly from the image, preserving original Cyrillic scripts and automatically forcing the `UAH` currency standard to ensure financial precision.
- **UX Mastery:** A seamless **Animated Split-View Modal** connects physical artifacts to digital inventory. A **Global Thought Ticker** simulates a live terminal, providing real-time AI transparency during ingestion, complemented by playful contextual animations (e.g., "Chopping veg 🔪") and interactive skill triggers like the *Bag Detection Module*.

## 🏗 Architectural Governance
Please see `.agents/rules/` for the strict architectural standards on databases, PKs, and UI rendering. All external subagents must respect these constraints.

## 🛠 Tech Stack
- **Backend:** Python 3.12+, FastAPI (Lifespan Context Architecture), Uvicorn, Asyncio
- **Database:** SQLite, `aiosqlite`, SQLAlchemy (Async)
- **Frontend:** Vue 3 (Composition API), Vite, Tailwind CSS (Typography Plugin), HTML5 Canvas (Vision Preprocessing)
- **AI/LLM:** Google Gemini SDK (Function Calling, Structured Outputs, Multimodal Vision)
- **DevOps:** Docker, Docker Compose, Volume Persistence

## 🎮 Usage: Draggable OS Workspace & Chat-First Hub
In Phase 10, we introduced a fully dynamic workspace (Layout Engine) and transitioned to a Global Shell structure:
- **Global Identity Shell**: The Chef's persistent avatar now lives in the unified Top Header, serving as an omnipresent navigation anchor equipped with session control. The Avatar uses a kinetic `@keyframes breathing` pulse to represent system vitality and dynamically shifts colors (Red/Yellow/Blue) acting as an Emotive FSM State tracker. 
- **Chat-First Command Hub**: The central Interaction Zone has shed heavy UI buttons entirely, pivoting to a clean **Messenger Pattern** architecture pinning the input field to the bottom while your query history streams vertically above. Hardware vision triggers (like Receipt Scanning via Camera) are seamlessly isolated to a static top action bar.
- **Cognitive Glassmorphism**: A floating `ThoughtTicker` HUD natively integrates with the background, actively broadcasting the core backend processes and flexing dynamically into empty chat spaces.
- **Micro-Data Grids & Fuzzy Diffing**: The Culinary Advice interface directly cross-references generated LLM recipes with the live Fridge database, visually parsing ingredients into rich `Grid Format` data-blocs and rendering missing (+) vs available (✓) UI states.
- **Drag & Drop**: Grab the `⠿` marker on any widget (e.g., Inventory or Culinary Advice) to reposition it. The state is instantly saved to the database.
- **Data Integrity & Security**: All UI manipulation endpoints are fortified against SQL injection using boundary parametrization. Receipt parsing features an ORM-decoupled engine (The Jules Fix), allowing item persistence when scan history is cleared.
- **Zero-Build Sandbox**: A native ES6 Node test suite is integrated allowing instant validation of component states (`node tests/run.js`) without compiling Webpack/Vite bundles.
- **Lifespan Architecture**: Safe API backend initialization and teardown controlled by modern `@asynccontextmanager`, isolating database logic from UI routing processes.
- **Collapse Panel**: Click the arrow in the top right corner of a widget to collapse it, freeing up screen real estate.
- Upon page refresh, all your custom layout preferences are restored automatically!

## 🐳 Deployment (Dockerized)

The entire ecosystem is containerized. The AI's memory is safely persisted via Docker Volumes.

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/smart-kitchen-ai.git](https://github.com/your-username/smart-kitchen-ai.git)

# 2. Set your API Key (Required)
export GEMINI_API_KEY="your_api_key_here" (or $env:GEMINI_API_KEY="your_api_key_here" on Windows)

# 3. Build and run in detached mode
docker-compose up --build -d
The API will be available at http://localhost:8000. Interactive documentation (Swagger UI) is available at http://localhost:8000/docs.
```

(Note: The system automatically provisions a ./data directory on your host machine to persist kitchen.db across container restarts).

---

## 🗺️ Roadmap & Tasks
Please check `MASTER_ROADMAP.md` for historical phases, current task tracking, and future iterations.
