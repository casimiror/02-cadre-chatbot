# Cadre AI Support Chatbot

Support chatbot for Cadre AI: answers common inbound questions from a curated knowledge base,
explains how to book a strategy call (and can send the request itself), and escalates to the team
when it can't answer.

**Live**: _TODO deployed URL_ (Vercel + Supabase, see [Deploy](#deploy))

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
- **Database**: one variable, two targets. Locally `DATABASE_URL` points to the compose `db`
  service (Postgres 17, a stand-in for Supabase). Deployed it is Supabase (see Deploy).
  `app/db/url.py` accepts any `postgres://` / `postgresql://` URL and adapts it: psycopg driver,
  `sslmode=require` for Supabase hosts, prepared statements off on the transaction pooler (6543).
- **Links**: `BOOKING_URL` (cadre.ai/contact), `CONTACT_EMAIL`, `WEBSITE_URL`, `PORTAL_URL` are the
  only links and contact details the bot may share.

## Deploy (Vercel + Supabase)

Production runs on **Vercel** (FastAPI preset: one Python function, React build on the CDN) with
**Supabase** Postgres. Docker is only for local work.

| | Local | Vercel |
| --- | --- | --- |
| Database | compose `db` (direct, port 5432) | Supabase transaction pooler (port 6543) |
| Connection pool | SQLAlchemy pool (5) | `NullPool`: Supavisor pools (`VERCEL=1` sets `serverless`) |
| Prepared statements | on | off (transaction mode can't use them) |
| Migrations | `make migrate` | `make migrate-supabase` (session pooler, port 5432) |
| Frontend | Vite (`make dev`) or `/app/static` in the image | built by `vercel-build.sh` into `backend/static`, served from the CDN |

### 1. Supabase

1. Create a project in a region close to your Vercel functions (e.g. `us-east-1` with Vercel's
   `iad1`).
2. **Connect** button: copy the **Transaction pooler** URL (port 6543) and the **Session pooler**
   URL (port 5432), with the database password filled in.
3. Put the session pooler URL in `.env` as `SUPABASE_DB_URL` and run `make migrate-supabase`.
   Migrations go through the session pooler because the direct `db.<ref>.supabase.co` host is
   IPv6-only. Every table has RLS on with no policies, so Supabase's REST API exposes nothing; the
   backend connects as the table owner.

### 2. Vercel

1. **Add New → Project**, import this GitHub repo.
2. **Root Directory**: `backend`. Keep "Include files outside the root directory in the Build
   Step" on (default): the build compiles `../frontend`. The FastAPI preset is detected from
   `pyproject.toml` (`[tool.vercel]`); `vercel.json` sets `maxDuration` 60 s for LLM turns.
3. **Environment variables** (Production and Preview):

   | Variable | Value |
   | --- | --- |
   | `DATABASE_URL` | Supabase transaction pooler URL (6543). Or install the Supabase integration, which sets `POSTGRES_URL` (read as a fallback). |
   | `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` | `openrouter`, `google/gemini-3.5-flash-lite`, your key |
   | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` | your project's keys and region URL |
   | `PORTAL_URL` | client portal URL (optional) |

   `BOOKING_URL`, `CONTACT_EMAIL`, `WEBSITE_URL` and the limits have working defaults.
4. **Settings → Functions → Region**: the same region as Supabase.
5. Deploy, then check `https://<app>.vercel.app/api/health` and send a chat message.

### Known limits on Vercel

- **Rate limit is per function instance** (slowapi in-memory storage); the client IP comes from
  Vercel's `x-real-ip`. For a global limit, point slowapi at Redis (e.g. Upstash).
- **Langfuse** traces are flushed after every response (`BackgroundTasks`), since an instance can
  freeze between requests.
