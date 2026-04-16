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
5. **Conciseness:** Do not output full conversational fillers. Use only <thought> blocks for reasoning and <final_report> for short summaries. Max 3 sentences per response. Detailed reports should be in `Artifacts`

## 3. Communication Strategy
- **Internal Specs:** English.
- **Reports & User Chat:** Ukrainian.

## 4. SYNC
- **Project Rules:** Always check .agents\rules for actual `project rules`