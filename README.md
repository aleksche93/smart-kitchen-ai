Markdown
# 🍳 Smart Kitchen AI Ecosystem (Stateful Autonomous Agent)

An asynchronous, multimodal AI agent built to optimize kitchen inventory, reduce food waste, and provide real-time culinary orchestration using **Google Gemini Pro API**, **Agentic RAG**, and **FastAPI**.

Unlike typical stateless AI wrappers, this ecosystem features a **Stateful Artificial Persona**. The AI "Chef" possesses memory, emotional states (managed via a Finite State Machine), and tracks user preferences across sessions.

## 🧠 Core Architecture & Features

1. **Stateful AI Memory (SQLite + SQLAlchemy):** User habits, "cooking sins", and the Chef's emotional state (FSM) are persisted locally via async database sessions, allowing the LLM to remember past interactions.
2. **Computer Vision Ingestion:** Uses `gemini-2.5-flash` to scan physical grocery receipts, extracting structured JSON data via Pydantic schemas.
3. **Structured Tool Calling:** Forces the LLM to return strictly typed JSON responses (`ChefResponse`), including actionable stubs (`tool_commands`) designed for future IoT Smart Home integration.
4. **Neo-Ukrainian Premium SPA:** A Vue 3 B2C Frontend utilizing Tailwind CSS and `<Teleport>` modals. It embraces a "Neo-Ukrainian Warmth" dark palette (Slate, Terracotta, Wheat) to provide an immersive 3-panel user interface.
5. **Dual-Mode Chat & Teleportation:** Interaction logic is cleanly divided. General chat runs via the main hub, while targeted ingredient recipes are triggered cleanly via isolated Item Modals utilizing Vue's Teleport feature.
6. **Agentic RAG:** Asynchronously fetches "classic flavor pairings" from a local knowledge base (The Flavor Bible) to rescue expiring ingredients.

## 🛠️ Tech Stack
- **Backend:** Python 3.12+, FastAPI, Uvicorn, Asyncio
- **Database:** SQLite, `aiosqlite`, SQLAlchemy (Async)
- **Frontend:** Vue 3 (Composition API), Vite, Tailwind CSS (Typography Plugin)
- **AI/LLM:** Google Gemini SDK (Function Calling & Structured Outputs)
- **DevOps:** Docker, Docker Compose, Volume Persistence

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

## 🗺️ Roadmap (Next Iterations)
- [x] Migrate from CLI to FastAPI REST microservice.
- [x] Containerize the ecosystem using Docker & Docker Compose.
- [x] Implement persistent state (FSM memory) via SQLite and JSON columns.
- [x] **Phase 4 & 5:** Build a modern Vue 3 SPA Frontend with B2C Pivot ("Neo-Ukrainian Warmth"), Teleport modals, and dynamic 3-panel architecture.
- [x] **Phase 5.1:** B2C UI Polish (Structured JSON recipe rendering, Interactive Hover Toasts, Hiding technical IoT logs).
- [ ] Implement Pantry and Freezer modules for non-perishable routing.
- [ ] Transition local JSON knowledge base to a Vector DB for semantic RAG search.
