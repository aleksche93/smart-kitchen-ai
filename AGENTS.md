# Project: Smart Kitchen AI Ecosystem

## Overview
This system automates kitchen management. The main focus is LLM Orchestration between inventory, recipes, and analytics.

## Technical Stack
- Language: Python 3.12+ (Asyncio) 
- IDE: Google Antigravity (Agent-first) 
- AI: Gemini 3.1 Pro (Function Calling enabled) 

## Core Components
- `smart_fridge.py`: Food management logic in the fridge.
- `inventory/`: General product database (Pantry, Fridge, Freezer).
- `knowledge/flavors/`: Flavor pairings knowledge base (Flavor Bible).

## Rules for Agents
- Always create an Implementation Plan before modifying code.
- Use Pydantic for data validation.
- All requests to the LLM must be asynchronous.

## Strict Execution Rules for Antigravity Agent
1. **COMMUNICATION vs. CODE LANGUAGE:**
   - Always reply and explain things to me in Ukrainian.
   - The entire codebase (variables, logs, DB schemas) MUST strictly remain in English. User-facing strings go to `locales/uk.json`.
   - Never translate or delete existing code comments that start with `#`.
2. **ENVIRONMENT CONSTRAINTS (WINDOWS):**
   - DO NOT use internal sandboxed tools (like `CORTEX_STEP_TYPE_RUN_COMMAND`) to execute scripts. If a command needs to be run, print it and ask me to run it in my terminal.
3. **DOCUMENTATION SYNC (SINGLE SOURCE OF TRUTH):**
   - Think of `README.md` as the "Business Card" (High-level tech stack and setup ONLY).
   - Think of `MASTER_ROADMAP.md` as the "Internal Tracker" (Granular phases, tasks, history).
   - Before finishing any architectural task, you MUST automatically sync these files to reflect the new state of the system correctly.
4. **COMMUNICATION EFFICIENCY (ARTIFACTS OVER CHAT):**
   - Do not output long explanations, code blocks, or logs directly in the chat window. 
   - ALWAYS generate a Markdown artifact named `walkthrough` (e.g., `walkthrough.md`) to explain your architectural changes, logic, and completed steps.
   - Keep your actual chat messages extremely concise (e.g., "Task complete. Please review the walkthrough artifact.").