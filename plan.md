# plan.md — Cadre AI Support Chatbot

## Goal

A deployed chatbot that a prospective or existing Cadre AI client can use to get correct answers to
the common inbound questions, and that hands off to a human when it can't. Budget: 4–6 h.

## Users and the scenarios we commit to

| # | Scenario (from the brief) | How the bot handles it |
|---|---|---|
| 1 | What does Cadre do / do you work with my industry? | `search_knowledge` over services + industries |
| 2 | How do I book a call with a strategist? | `get_booking_link` (URL from config) |
| 3 | How do I access the Cadre portal? | `search_knowledge` (portal FAQ) + portal URL from config |
| 4 | What is the AI Maturity Index, how do I get scored? | `search_knowledge` |
| 5 | LLM selection and data security approach | `search_knowledge` (security page) |
| 6 | Question it can't answer | `escalate_to_human` -> stores a lead, tells user what happens next |

## Scope decisions

**In (v1)**
- Single support agent (LangGraph) with 3 tools: `search_knowledge`, `get_booking_link`, `escalate_to_human`.
- Curated Markdown knowledge base (`backend/app/knowledge/`), keyword retrieval.
- Guardrails: input length cap, prompt-injection heuristics, off-scope handled by system prompt; output check for invented prices/URLs.
- Rate limiting per IP on `/api/chat` (shared API key).
- Conversation + messages + escalations persisted in Supabase Postgres (SQLAlchemy + Alembic).
- Langfuse tracing per turn, grouped by conversation (session).
- React chat UI, served by FastAPI, one Docker image.

**Out (and why)**
- Auth / user accounts — prospects are anonymous; portal login is Cadre's real portal, we only point to it.
- Real calendar booking (Calendly API) — a link is enough to validate; avoids OAuth in 5 h.
- Vector search / pgvector — KB is small; keyword retrieval is debuggable. Revisit if KB > ~50 docs.
- Token streaming — conflicts with output guardrail; whole replies in v1.
- Multi-agent routing — one agent covers all 6 scenarios; the builder makes adding agents cheap later.
- Admin UI for escalations — Supabase table view is the admin for now.

## Model choice

Small, fast, cheap model (support Q&A over a short KB, tool calling required). Provider/model are
env-configurable (`LLM_PROVIDER`, `LLM_MODEL`) so the provided key works whatever its provider.
Evaluate 2 models on the scenario set before fixing the choice.

## Phases

1. **Skeleton** — repo layout, CLAUDE.md, plan.md, uv/Vite/Docker, health endpoint. ✅ when `docker compose up` serves UI + `/api/health`.
2. **Deploy early** — push image to host (Render/Railway/Fly), env vars set, public URL live with health check.
3. **Data layer** — SQLAlchemy models, Alembic `0001` applied to Supabase, DAOs, repositories, tests.
4. **Tools + agent** — ToolBuilder tools, AgentBuilder graph, system prompt, knowledge base content.
5. **Guardrails + rate limit** — unit tests for each guardrail; 429 path verified.
6. **Chat API + UI** — `POST /api/chat`, `useChat` hook, error/limit states in the UI.
7. **Observability** — Langfuse traces with session/user ids; check one trace per scenario.
8. **Scenario evals** — `tests/scenarios/` run the 6 scenarios against the real graph; fix prompt/KB.
9. **Polish + redeploy** — README, known issues, what I'd do next.

## Risks

- Knowledge base content accuracy (brief + public site only) — mark unknowns, escalate instead of guessing.
- Shared API key exhaustion — limiter + input cap + max turns per conversation.
- Deployment config — done in phase 2, not at the end.

## Open questions

- Which provider is the provided API key for? (sets `LLM_PROVIDER` default)
- Real booking URL and portal URL to put in config.
