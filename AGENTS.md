# 🤖 Smart Kitchen AI: Project Governance

## 1. Project Structure & Environment
- **Root Directory:** Contains `app.py` (Backend), `docker-compose.yml`, `AGENTS.md`.
- **Database:** `vs/data/kitchen.db`.
- **Frontend Directory:** `/frontend` (Vue 3 + Tailwind project).
- **Docker:** Use `docker-compose.yml` for orchestration (Backend + Frontend).

## 2. Operational Protocols (Mandatory)
1. **Context Recovery:** At the start of a session, read `AGENTS.md` and `MASTER_ROADMAP.md`.
2. **Artifact Ownership:** The Agent MUST update `walkthrough.md` and implementation plans.
3. **Spec-Driven:** Every UI change requires a Plan before coding.
4. **Code Integrity:** Never remove existing Ukrainian comments (#).

## 3. Communication Strategy
- **Internal Specs:** English.
- **Reports & User Chat:** Ukrainian.