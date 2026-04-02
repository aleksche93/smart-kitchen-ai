# ARCHITECTURE PROPOSAL

## Goal Description
Upgrading the `smart-kitchen-ai` ecosystem by migrating the legacy Stateful Chef logic (FSM & Persona) into the modern `asyncio`/FastAPI architecture. The system will persist state via SQLite, maintain a stateless API layer, support future IoT integrations via structured JSON tool calling, and follow strict i18n and English base-language conventions while preserving all original Ukrainian code comments.

## User Review Required
> [!IMPORTANT]
> Please review this architecture plan carefully. Proceeding to Phase 2 (Database & State Implementation) requires your explicit approval.
> - **Database Choice:** Are you fine with using SQLAlchemy with async support (`SQLAlchemy[asyncio]` + `aiosqlite`)? This is the industry standard for FastAPI.
> - **Schema Layout:** The plan proposes a hybrid schema where core state is strictly relational but traits, preferences, and long-term memory metrics use flexible JSON columns. Do you authorize this hybrid design?

## Proposed Changes

### 1. Merging FSM and Persona into Current Endpoints

**Stateful Logic in a Stateless FastAPI Environment:**
FastAPI handles requests concurrently and statelessly. To bring the FSM to the API:
1. **Dependency Injection**: Every relevant endpoint will use a FastAPI `Depends` method to inject the database session and load the `ChefFSM` / `ChefPersona` context for the current user.
2. **Action to Trigger Mapping**: User inputs (e.g. asking a recipe, scanning receipt) will be mapped to `ChefTrigger` events (e.g., `COMPLEX_TASK`).
3. **Execution**: The endpoint will execute `chef_fsm.trigger(event)` and `chef_persona.react_to_...` to compute the emotional shift and state transition in-memory.
4. **Dynamic Prompt Injection**: The computed state (e.g., `OFFLINE`, `SERIOUS`, `ANNOYED`), character traits, and preferences will be stringified and embedded directly into the system prompt for Gemini `gemini-2.5-flash`.
5. **Database Commit**: Before resolving the API response, the system will save the updated `ChefState` and `EmotionBuffer` back into SQLite, ensuring persistence across server and Docker restarts.

**Impact on Endpoints:**
- `/api/v1/chef/advice`: This endpoint will be completely overhauled to: load state -> process trigger -> generate structured prompt -> extract Gemini's response -> save state -> respond. 

### 2. Database Schema (SQLite via `aiosqlite`)

The database will live in a mounted Docker Volume (e.g., `/app/data/kitchen.db`) so it survives container restarts.

```sql
-- Core User/Session Tracking
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR,
    preferred_language VARCHAR DEFAULT 'uk'
);

-- Chef FSM State & Emotion Buffer
CREATE TABLE chef_state (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    current_state VARCHAR NOT NULL, -- e.g. "IDLE", "PLAYFUL"
    emotion_value FLOAT NOT NULL,
    personality_profile VARCHAR DEFAULT 'neutral'
);

-- Long-Term Memory, Sins & Traits
CREATE TABLE chef_memory (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    preferences JSON, -- { "likes_spicy": true, "likes_chicken": false }
    traits JSON,      -- { "chaotic": 2, "seafood_lover": 1 }
    cooking_sins JSON,-- { "tuna_welldone": true, "protein_chaos": false }
    long_term_counters JSON -- respect_count, toxicity_count, etc.
);

-- Short-Term Context
CREATE TABLE chef_session (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    recent_triggers JSON,
    ui_events JSON
);
```
*(By heavily grouping dynamic metrics into `JSON` columns, we keep our schema simple while still utilizing SQLite's excellent JSON querying capabilities)*.

### 3. Future IoT Preparation (Tool Calling Stubs)

We will switch Gemini generation to strictly use `response_schema`. Instead of returning raw markdown text, the AI will return a structured JSON interface, making it safe to parse and forward commands.

```python
class ActionStub(BaseModel):
    action: str  -- e.g., "activate_stove", "set_timer"
    params: dict -- e.g., {"minutes": 15, "temperature": 180}

class ChefResponse(BaseModel):
    advice_text: str
    recipe: Optional[str] = None
    emotion_displayed: str       -- e.g., "smiling", "eye_roll" (for UI sync)
    tool_commands: List[ActionStub] = Field(default_factory=list)
```
Initially, `tool_commands` will remain empty or hold dummy stubs, which the UI can simply ignore until actual smart home integrations are implemented.

### 4. Language & i18n Policy

- **Code Comments**: All existing Ukrainian code comments will be rigidly preserved for learning context.
- **Base Logic**: All variables, function names, metrics (like FSM state names), DB fields, HTTP responses, logs, and prints will be cleanly translated to standard **English**.
- **Localization (i18n)**: All hardcoded Ukrainian strings found in `chef_persona.py` (e.g., `"Морепродукти так довго не живуть.", "Це вже не креветки..."`) will be mapped to keys and stored in a localization file `locales/uk.json`. In Python, the code will dynamically load: `i18n.get("response.overcooked_seafood.0")`.

## Verification Plan

### Automated Tests
- Validate Pydantic schema generation with stubs.
- Boot up API and ensure SQLite Database connection functions correctly inside stateless requests.

### Manual Verification
- Deploy to local Docker instance, trigger `/api/v1/chef/advice`, and verify that `chef_state` updates correctly.
- Restart Docker and ensure memory remains intact.
- Verify Ukrainian responses still properly display on client via the `locales` mapper without hardcoding them in the logic.
