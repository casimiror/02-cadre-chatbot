# Cadre AI Support Chatbot — CLAUDE.md

Customer support chatbot for Cadre AI (take-home). One deployable unit: FastAPI serves the API
**and** the built React app. Read `plan.md` for phases, scope and what is explicitly out of scope.

## Stack (do not swap without updating plan.md)

- **Backend**: Python 3.12, FastAPI (>=0.141, uses `app.frontend()`), LangGraph, LangChain v1 chat models.
- **Package manager**: `uv` only. Never `pip install`. Add deps with `uv add <pkg>` inside `backend/`.
- **Frontend**: React + Vite + TypeScript in `frontend/`. Build output `frontend/dist` is served by FastAPI.
- **DB**: Supabase used as plain Postgres via SQLAlchemy 2 + psycopg 3 (`DATABASE_URL`). Schema = ORM models in `app/db/models.py`; migrations with **Alembic** in `backend/alembic/`. The browser never talks to the DB.
- **Observability**: Langfuse via `langfuse.langchain.CallbackHandler`, one trace per chat turn, `session_id = conversation_id`.
- **Runtime**: Docker (multi-stage: node builds the UI, python runs it). `docker compose up` is the local prod-like run.

## Commands

```bash
# backend (from backend/)
uv sync                                   # install
uv run fastapi dev                        # dev server on :8000 (entrypoint in pyproject)
uv run pytest                             # tests
uv run ruff check . && uv run ruff format .
uv run alembic revision --autogenerate -m "add x"   # after changing app/db/models.py; READ the generated file
uv run alembic upgrade head               # apply to DATABASE_URL
uv run alembic upgrade head --sql         # print SQL without a DB (review)

# frontend (from frontend/)
npm install && npm run dev                # :5173, proxies /api -> :8000
npm run build                             # -> frontend/dist (served by FastAPI)

# everything, prod-like
docker compose up --build                 # :8000
```

## Backend architecture — the layering is the rule

```
api/routes  ->  services  ->  repositories  ->  db/daos  ->  Postgres (Supabase)
                   |
                   +-> agents (LangGraph graph built by AgentBuilder)
                          +-> tools (built by ToolBuilder; may use repositories)
                          +-> guardrails (input/output nodes in the graph)
```

- **routes** (`app/api/routes/`): HTTP only. Validate with `app/schemas`, apply rate limit, call a service. No business logic, no DB.
- **services** (`app/services/`): orchestrate one use case (`ChatService.handle_turn`). Load history, invoke the graph, persist.
- **repositories** (`app/repositories/`): domain-level persistence API, returns `app/domain` models. Combines DAOs.
- **daos** (`app/db/daos/`): one file/class per table, subclass `BaseDAO[Row]`, each call is its own short transaction, returns ORM rows. Nothing outside `app/db/` imports SQLAlchemy sessions.
- **tools** (`app/tools/<area>/`): one file per tool, each exposes `build_<name>_tool(deps) -> BaseTool` made with `ToolBuilder`. Register it in `app/tools/registry.py`.
- **agents** (`app/agents/`): `AgentBuilder` composes LLM + system prompt + tools + guardrails into a compiled `StateGraph`. Prompts are Markdown in `app/agents/prompts/`, never inline strings.
- **guardrails** (`app/guardrails/`): pure functions/classes, no LLM calls unless stated. Must be unit-tested.
- Dependency wiring lives only in `app/api/deps.py`.

## Rules

- Conversation history source of truth is the `messages` table, not a LangGraph checkpointer.
- Schema changes only through `app/db/models.py` + an Alembic revision. Never edit an applied revision; add a new one. Every new public table gets `enable row level security` in its migration (Supabase exposes `public` over REST).
- The bot answers **only** from `app/knowledge/` (via the `search_knowledge` tool) or tool results. No invented prices, URLs, clients or case studies. Unknown -> escalate.
- Every external URL the bot can say (booking link, portal) comes from `Settings`, never from the model.
- Secrets only via env (`.env`, see `.env.example`). The LLM API key is shared and rate-limited: keep `/api/chat` behind the limiter and the input length guardrail.
- New tool: `/new-tool`. New agent: `/new-agent`. Before committing: `/check`.
- Small commits, imperative messages, one concern per commit (the git history is reviewed).

## Gotchas

- `app.frontend()` must be registered **after** all API routers. `check_dir="auto"` only skips the dist check when `FASTAPI_ENV=development` (set by `fastapi dev`); in tests/scripts set it yourself or build the UI first.
- Run the CLI without a path (`fastapi dev` / `fastapi run`): the entrypoint is `[tool.fastapi]` in pyproject. `fastapi run app/main.py` fails with `No module named 'app'`.
- Supabase: use the direct or session-pooler URL (port 5432). The transaction pooler (6543) breaks psycopg prepared statements.
- langchain-core 1.x: `message.text` is a property, not a method.
- slowapi needs `request: Request` in the endpoint signature or the limiter silently does nothing.
- Langfuse reads keys from the `Langfuse(...)` client created in `core/observability.py`; `CallbackHandler()` reuses it.
- Output guardrail runs after generation, so responses are returned whole (no token streaming) in v1. See plan.md.
