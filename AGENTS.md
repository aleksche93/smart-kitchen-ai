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