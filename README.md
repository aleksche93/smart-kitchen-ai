# 🍳 Smart Kitchen AI Ecosystem (Agentic Orchestrator)

An asynchronous, multimodal AI agent built to optimize kitchen inventory, reduce food waste, and provide real-time culinary orchestration using **Google Gemini API** and **Agentic RAG**.

## 🧠 Core Architecture & Features

This project demonstrates a fully functional Applied AI pipeline:
1. **Computer Vision (Data Ingestion):** Uses `gemini-2.5-flash` to scan physical grocery receipts (`scanner.py`), extracting structured JSON data via Pydantic schemas.
2. **Strict Routing (State Management):** Filters extracted items, routing perishable goods to the `Fridge` module while isolating unsupported categories (Pantry/Freezer) to maintain data integrity.
3. **Agentic RAG (Knowledge Layer):** Asynchronously fetches "classic flavor pairings" from a local JSON knowledge base (based on *The Flavor Bible*) for items close to expiration.
4. **Human-in-the-Loop LLM Orchestration:** Prompts the user to select an expiring ingredient, then dynamically injects the context into the Gemini model (`thinking_level='low'`) to generate a fast, zero-hallucination rescue recipe.

## 🛠️ Tech Stack
- **Language:** Python 3.12+ (Asyncio)
- **IDE:** Google Antigravity (Agent-first)
- **AI Models:** Google Gemini 2.5 Flash / Gemini 3.1 Pro via `google-genai` SDK
- **Data Validation:** Pydantic
- **I/O:** `aiofiles` for non-blocking local storage, `Pillow` for image processing

## 🚀 Quick Start
    ```bash
    # 1. Clone the repository
    git clone [https://github.com/your-username/smart-kitchen-ai.git](https://github.com/your-username/smart-kitchen-ai.git)
    
    # 2. Setup virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # 3. Install dependencies
    pip install -r requirements.txt

    # 4. Set your API Key
    export GEMINI_API_KEY="your_api_key_here"  # On Windows: $env:GEMINI_API_KEY="your_api_key_here"

    # 5. Run the orchestrator
    python smart_fridge.py
    ```

## 🐳 Deployment via Docker
Для швидкого розгортання екосистеми як ізольованого контейнера, використовуйте Docker & Docker Compose:

```bash
# 1. Скомпілюйте образ (build)
docker-compose build

# 2. Запустіть сервіс у фоновому режимі (up)
docker-compose up -d
```
> **Увага:** Переконайтеся, що змінна середовища `GEMINI_API_KEY` експортована перед запуском docker-compose, оскільки вона прокидається всередину контейнера.

## 🗺️ Roadmap (Next Iterations)
- [ ] Implement Pantry and Freezer modules for non-perishable routing.
- [x] Containerize the application using Docker for isolated deployments.
- [ ] Transition local JSON storage to a lightweight Vector DB for semantic RAG search.
