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
- **Observability**: Langfuse, one trace per turn, session = conversation.

Details and conventions: [CLAUDE.md](CLAUDE.md). Scope, phases and trade-offs: [plan.md](plan.md).

## Run

```bash
cp .env.example .env          # fill LLM_API_KEY, DATABASE_URL, LANGFUSE_*
cd backend && uv sync && uv run alembic upgrade head
docker compose up --build     # http://localhost:8000
```

Dev mode: `cd backend && uv run fastapi dev` + `cd frontend && npm install && npm run dev` (http://localhost:5173).

Tests: `cd backend && uv run pytest`.
