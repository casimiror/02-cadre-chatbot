# Backend architecture

FastAPI app in `backend/app/`. One process serves the API (`/api/*`) and the built React app
(`app.frontend()`, registered last in `app/main.py`).
`app.frontend(..., check_dir="auto")` only skips the "build exists" check when
`FASTAPI_ENV=development` (set by `fastapi dev`); scripts that import `app.main` need the UI built
or that variable set.

## Layers

The layering is the rule. A layer only calls the one below it.

```
api/routes  ->  services  ->  repositories  ->  db/daos  ->  Postgres
                   |
                   +-> agents (LangGraph graph built by AgentBuilder)
                          +-> tools (built by ToolBuilder; may use repositories)
                          +-> guardrails (input/output nodes in the graph)
```

| Layer | Folder | Responsibility | Must not |
| --- | --- | --- | --- |
| Routes | `app/api/routes/` | HTTP only: validate with `app/schemas`, rate limit, call a service | contain business logic or touch the DB |
| Schemas | `app/schemas/` | Pydantic request/response models (the HTTP contract) | be used below the route layer |
| Services | `app/services/` | One use case each (`ChatService.handle_turn`): load history, invoke the graph, persist | build agents or open sessions |
| Repositories | `app/repositories/` | Domain persistence API; combine DAOs; return `app/domain` models | return ORM rows |
| DAOs | `app/db/daos/` | One class per table, subclass `BaseDAO[Row]`, each call is its own short transaction | be imported outside repositories |
| Domain | `app/domain/` | Pydantic models the app passes around | know about SQLAlchemy |
| Agents | `app/agents/` | `AgentBuilder` composes LLM + prompt + tools + guardrails into a `StateGraph` | inline prompts (they live in `app/agents/prompts/*.md`) |
| Tools | `app/tools/<area>/` | One file per tool, `build_<name>_tool(deps) -> BaseTool` via `ToolBuilder`; registered in `app/tools/registry.py` | use DAOs or sessions directly |
| Guardrails | `app/guardrails/` | Pure checks on input/output text; unit-tested | call an LLM (unless stated) |
| Core | `app/core/` | Settings, LLM factory, rate limiter, observability | depend on routes or services |

Wiring of concrete classes happens **only** in `app/api/deps.py`.

## HTTP API

| Method and path | Body | Response |
| --- | --- | --- |
| `GET /api/health` | | `{"status": "ok"}` |
| `POST /api/chat` | `message`, `conversation_id?`, `visitor_id?` | `conversation_id`, `message_id` (the stored reply), `reply` |
| `PUT /api/messages/{id}/feedback` | `{"rating": "up" \| "down"}` | 204; 404 if `id` isn't an assistant message |
| `DELETE /api/messages/{id}/feedback` | | 204 (idempotent); 404 as above |

Limits: `RATE_LIMIT_CHAT` (10/min) and `RATE_LIMIT_FEEDBACK` (30/min) per client IP.

## A chat turn

1. `POST /api/chat` (`routes/chat.py`): slowapi limits per client IP, `ChatRequest` validates
   (`message`, optional `conversation_id`, optional `visitor_id` UUID).
2. `ChatService.handle_turn` gets or creates the conversation (storing `visitor_id`), loads the last
   `MAX_HISTORY_MESSAGES` from `messages` (the source of truth, no LangGraph checkpointer).
3. `observability.trace_turn` opens one Langfuse trace: root span + `propagate_attributes`
   (`session_id = conversation_id`, `user_id = visitor_id`).
4. The graph runs: `input_guard -> agent <-> tools -> output_guard`.
   - Input guardrails: max length, prompt-injection heuristics. Blocked -> canned reply, no LLM call.
   - Agent: LLM with tools bound; loops through `ToolNode` until it answers.
   - Output guardrails: no prices, only allowed URLs. Blocked -> the reply is replaced.
5. User and assistant messages are persisted **after** the turn succeeds (no half turns); the
   assistant message's id is returned as `message_id` so the UI can attach feedback to it.
6. The route schedules `observability.flush` as a background task (serverless instances can freeze).

## Tools

| Tool | Area | What it does |
| --- | --- | --- |
| `search_knowledge` | `knowledge/` | BM25 search over `app/knowledge/*.md` sections (see `docs/knowledge-base.md`) |
| `get_booking_link` | `booking/` | Contact page + email from `Settings`; offers `request_strategy_call` |
| `request_strategy_call` | `booking/` | Stores a contact-form request in `contact_requests` |
| `escalate_to_human` | `escalation/` | Stores an unanswered question in `escalations` |

Conventions for tools (also in `/new-tool`): the description says *when* to call it; args are a
Pydantic model with a `Field(description=...)` each; per-turn context (conversation id) comes from
`config: RunnableConfig`, never from args; failures return a short string starting with an
UPPERCASE code (`NO_RESULTS:`, `BOOKING_UNAVAILABLE:`) the prompt can react to.

## Guardrails

Each guardrail has `name` and `check(text) -> GuardrailResult` (`app/guardrails/base.py`).

| Guardrail | Stage | Blocks |
| --- | --- | --- |
| `MaxLengthGuardrail` | input | messages over `MAX_INPUT_CHARS` |
| `PromptInjectionGuardrail` | input | "ignore previous instructions", "reveal your system prompt", ... |
| `NoInventedPricesGuardrail` | output | `$`, `USD`, `€` followed by a number |
| `AllowedLinksGuardrail` | output | any URL not starting with a `Settings` URL |

The output check runs after generation, so replies are returned whole (no token streaming).

## Feedback

`FeedbackService` (`app/services/feedback_service.py`) lets a visitor rate a reply: one row per
message in `message_feedback`, upserted in one statement (`MessageFeedbackDAO.upsert`), deleted when
the vote is removed. Only assistant messages are rateable (`MessageNotRateableError` -> 404). Join
`message_feedback -> messages -> conversations` to analyse a conversation with its votes.

## Configuration

`app/core/config.py` (`Settings`, pydantic-settings). Everything comes from env; `.env.example`
documents each variable. Notable aliases: `DATABASE_URL` falls back to `POSTGRES_URL` (Vercel's
Supabase integration), `LANGFUSE_BASE_URL` to `LANGFUSE_HOST`, and `VERCEL=1` sets `serverless`.

## Observability

Langfuse, one trace per turn (`app/core/observability.py`). The `Langfuse(...)` client is created
once in the lifespan; `CallbackHandler()` reuses it. The root span records the user text, the reply
and `blocked_by`. `visitor_id` is an anonymous UUID: never send emails or names to Langfuse.
