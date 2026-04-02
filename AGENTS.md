# Project: Smart Kitchen AI Ecosystem

## Overview
Ця система автоматизує управління кухнею. Основний фокус — LLM Orchestration між інвентарем, рецептами та аналітикою.

## Technical Stack
- Language: Python 3.12+ (Asyncio) 
- IDE: Google Antigravity (Agent-first) 
- AI: Gemini 3.1 Pro (Function Calling enabled) 

## Core Components
- `smart_fridge.py`: Логіка управління продуктами в холодильнику.
- `inventory/`: Загальна база даних продуктів (Pantry, Fridge, Freezer).
- `knowledge/flavors/`: База знань про поєднання смаків (Flavor Bible).

## Rules for Agents
- Перед зміною коду завжди створюй Implementation Plan.
- Використовуй Pydantic для валідації даних.
- Всі запити до LLM мають бути асинхронними.

## Strict Execution Rules for Antigravity Agent
1. **COMMUNICATION vs. CODE LANGUAGE:**
   - Always reply and explain things to me in Ukrainian.
   - The entire codebase (variables, logs, DB schemas) MUST strictly remain in English. User-facing strings go to `locales/uk.json`.
   - Never translate or delete existing code comments that start with `#`.
2. **ENVIRONMENT CONSTRAINTS (WINDOWS):**
   - DO NOT use internal sandboxed tools (like `CORTEX_STEP_TYPE_RUN_COMMAND`) to execute scripts. If a command needs to be run, print it and ask me to run it in my terminal.
3. **DOCUMENTATION SYNC:**
   - Before finishing any architectural task, you MUST automatically update `ARCHITECTURE_PROPOSAL.md`, `requirements.txt` and the `README.md` to reflect the new state of the system.
4. **COMMUNICATION EFFICIENCY (ARTIFACTS OVER CHAT):**
   - Do not output long explanations, code blocks, or logs directly in the chat window. 
   - ALWAYS generate a Markdown artifact named `walkthrough` (e.g., `walkthrough.md`) to explain your architectural changes, logic, and completed steps.
   - Keep your actual chat messages extremely concise (e.g., "Task complete. Please review the walkthrough artifact.").