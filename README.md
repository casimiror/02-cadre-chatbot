# Cadre AI Support Chatbot

Support chatbot for Cadre AI: answers common inbound questions from a curated knowledge base,
explains how to book a strategy call (and can send the request itself), and escalates to the team
when it can't answer.

**Live**: _TODO deployed URL_

## Architecture

- **FastAPI** serves `POST /api/chat` and the built React UI (`app.frontend()`), one container.
- **LangGraph** agent: `input_guard -> agent <-> tools -> output_guard`, built with `AgentBuilder`.
- **Tools** (`ToolBuilder`): `search_knowledge`, `get_booking_link`, `request_strategy_call`, `escalate_to_human`.
- **Knowledge base** (`backend/app/knowledge/`): Markdown split by `##`, ranked with BM25. Company,
  services, industries, case studies and FAQ come from cadre.ai (scraped 2026-10-24). The
  methodology docs (governance, agent design, retrieval, security, evaluation, compliance, Maturity
  Index levels) are synthetic, written for this exercise; each file's header comment says which.
- **Data**: Supabase Postgres via SQLAlchemy DAOs + repositories; migrations with Alembic.
- **Guardrails**: input length + prompt-injection heuristics; output blocks invented prices/URLs.
- **Rate limiting**: slowapi per IP on `/api/chat`.
- **Observability**: Langfuse, one trace per turn; session = conversation, user = anonymous visitor id
  (a UUID the browser keeps across conversations, so the Users view groups a visitor's sessions).

Details and conventions: [CLAUDE.md](CLAUDE.md). Scope, phases and trade-offs: [plan.md](plan.md).

## Run

Everything runs in Docker (`docker compose`); the `Makefile` wraps the usual commands. Only
`uv add` / `uv lock` run on the host.

```bash
make env        # creates .env from .env.example: fill LLM_API_KEY (OpenRouter) and LANGFUSE_*
make up         # prod-like: Postgres + migrations + app on http://localhost:8000
make dev        # dev: API with reload (:8001) + Vite (http://localhost:5173), migrations on start
make down       # stop (make reset-db also wipes the local database)
```

| Command | What it does |
| --- | --- |
| `make test` | backend tests (pytest) |
| `make lint` / `make format` | ruff check / autofix + format |
| `make migrate` | `alembic upgrade head` on `DATABASE_URL` |
| `make migration m="add x"` | autogenerate a revision from `app/db/models.py` (read it before committing) |
| `make migrate-check` | fail if models changed without a migration |
| `make migrate-roundtrip` | downgrade to base and upgrade again (local DB only) |
| `make ui-build` | build the React app |
| `make psql` | SQL shell on the local Postgres |
| `make check` | lint + tests + migration check + UI build (run before committing) |
| `make lock` | re-lock uv dependencies on the host |

`make help` lists every target.

### Configuration

- **LLM**: OpenRouter, default model `google/gemini-3.5-flash-lite` (`LLM_PROVIDER`, `LLM_MODEL`).
- **Database**: `DATABASE_URL` points to the compose `db` service (Postgres 17, a local stand-in
  for Supabase). To use Supabase, set it to the session-pooler URL (port 5432) and run
  `make migrate`.
- **Links**: `BOOKING_URL` (cadre.ai/contact), `CONTACT_EMAIL`, `WEBSITE_URL`, `PORTAL_URL` are the
  only links and contact details the bot may share.
