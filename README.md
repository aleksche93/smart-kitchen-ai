# 🍳 Smart Kitchen AI Ecosystem (Stateful Autonomous Agent)

An asynchronous, multimodal AI agent built to optimize kitchen inventory, reduce food waste, and provide real-time culinary orchestration using **Google Gemini Pro API**, **Agentic RAG**, and **FastAPI**.

Unlike typical stateless AI wrappers, this ecosystem features a **Stateful Artificial Persona**. The AI "Chef" possesses memory, emotional states (managed via a Finite State Machine), and tracks user preferences across sessions.

## 🧠 Core Architecture & Features

1. **Stateful AI Memory (SQLite + SQLAlchemy):** User habits, "cooking sins", and the Chef's emotional state (FSM) are persisted locally via async database sessions, allowing the LLM to remember past interactions.
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
- **Backend:** Python 3.12+, FastAPI, Uvicorn, Asyncio
- **Database:** SQLite, `aiosqlite`, SQLAlchemy (Async)
- **Frontend:** Vue 3 (Composition API), Vite, Tailwind CSS (Typography Plugin), HTML5 Canvas (Vision Preprocessing)
- **AI/LLM:** Google Gemini SDK (Function Calling, Structured Outputs, Multimodal Vision)
- **DevOps:** Docker, Docker Compose, Volume Persistence

## 🎮 Usage: Draggable OS Workspace
In Phase 10, is introduced a fully dynamic workspace (Layout Engine):
- **Drag & Drop**: Grab the `⠿` marker on any widget (e.g., Inventory or Chef Log) to reposition it. The state is instantly saved to the database.
- **Collapse Panel**: Click the arrow in the top right corner of a widget to collapse it, freeing up screen real estate.
- **Z-Index Focus**: The widget you are dragging or clicking automatically elevates to the top layer.
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
Please see `MASTER_ROADMAP.md` for historical phases, current task tracking, and future iterations.
