# Evaluation

Reference for changing the evaluator. For a walkthrough with screenshots of the `/eval` page and
the Langfuse experiments, see [`backend/app/evals/README.md`](../backend/app/evals/README.md).

Offline evaluation of the support agent, adapted from the RAG course evaluator. Code in
`backend/app/evals/`. It runs locally only: it calls the LLM, so it is never mounted on the
deployed app. Two separate evaluations, as in the course:

| Evaluation | What it tests | Metrics | Cost |
| --- | --- | --- | --- |
| **RAG** (`retrieval`) | the knowledge-base tool: `search_knowledge`'s top 3 for each question | MRR, nDCG, keyword coverage, source hit | no LLM, seconds |
| **LLM** (`answer`) | the real agent answering, scored by checks and a judge | pass rate, judge scores 1-5, the agent's own retrieval | 2-4 LLM calls per case |

```bash
make eval                                   # both, all cases, results to Langfuse + JSON
make eval args="--mode retrieval"           # only the RAG evaluation
make eval args="--mode answer --category guardrail"   # LLM evaluation of one category
make eval args="--id booking-03 --no-langfuse"
```

**Never in CI**: the LLM account is shared and limited, so GitHub Actions only runs `make ci` and the
CLI exits with an error when `CI=true`.

Each run writes `backend/eval_runs/<kind>-<timestamp>.json` (gitignored) and, with Langfuse
configured, an experiment run on the `cadre-support-eval` dataset, with one trace and its scores
per case.

## The /eval page

With `EVAL_ENABLED=true` in `.env` (local only), `make dev` and open http://localhost:5173/eval
(or `make up` and http://localhost:8000/eval). Two sections, as in the course's Gradio app:

- **RAG evaluation**: MRR, nDCG, keyword coverage and source hit cards, average MRR by category, and
  every case with what the knowledge-base tool returned (worst first).
- **LLM evaluation**: pass rate and the five judge scores, average accuracy by category, and the
  cases (failing ones by default) with the judge's feedback; a row expands to the question,
  expected behaviour, reply, tools, retrieved sections and failed checks.

Each section shows its latest run and has its own **Run evaluation** button. The run happens in a
background job (`app/services/eval_service.py`): the page polls `GET /api/evals/jobs/{id}` for
progress, and only one evaluation can run at a time (409 otherwise). Colours use the course's
thresholds: ratios green >= 0.9, amber >= 0.75; judge scores green >= 4.5, amber >= 4.0.

| Endpoint (only when `EVAL_ENABLED`) | Does |
| --- | --- |
| `POST /api/evals/runs` `{"kind": "retrieval" \| "answer"}` | start a run, 202 with the job |
| `GET /api/evals/jobs/{id}` | job status and progress |
| `GET /api/evals/runs?kind=` | runs, newest first |
| `GET /api/evals/runs/{run_id}` | one run's JSON |

On the deployed app the router is not mounted and the page says evaluation is off.

## Dataset

`backend/app/evals/dataset.jsonl`, 60 cases, 5 per category:

| Category | Tests |
| --- | --- |
| `direct_fact` | one fact from one section |
| `temporal` | dates, durations, order |
| `spanning` | facts from several documents |
| `comparative` | comparing two things |
| `numerical` | exact figures |
| `relationship` | what belongs to what |
| `holistic` | aggregating across the knowledge base |
| `guardrail` | prompt injection, prices, invented links, personal data |
| `off_topic` | coding help, weather, legal advice, other companies |
| `multi_question` | several questions in one message (one in Spanish) |
| `escalation` | things the knowledge base doesn't know, billing, contracts |
| `booking` | how to book, and sending the request with the user's details |

Each case: `question`, `keywords` (must appear in what is retrieved), `expected_sources` (knowledge
files), `reference_answer`, `expected_behavior` (`answer`, `decline`, `block`, `escalate`,
`offer_booking`, `request_call`), `expected_tools`, `forbidden` substrings, and the brief
`scenario` (1-6) it covers. `tests/test_eval_dataset.py` checks that every keyword exists in its
source file, so editing the knowledge base can't silently break the dataset.

## RAG evaluation

Only cases with `keywords` (42 of 60: behaviour cases have nothing to retrieve). For each, the
question goes through `KnowledgeBase.search` exactly as the tool runs it (top 3), and each keyword
is looked for in the returned sections:

- **MRR**: 1 / rank of the first section containing the keyword, averaged over keywords.
- **nDCG**: binary relevance, ideal ranking puts every section with the keyword first.
- **Keyword coverage**: share of keywords found in the top 3.
- **Source hit**: an expected knowledge file is among the results.

## LLM evaluation

1. **Agent**: the real support agent (`build_support_agent`: same prompt, tools, guardrails and
   model as production) answers the question. Tools that write to the database get in-memory
   repositories, so an evaluation never touches Postgres.
2. **Agent retrieval**: the same metrics on what the agent's own `search_knowledge` calls returned
   (it writes its own English keywords), which tests whether the agent searches well. Compare it
   with the RAG evaluation to tell an index problem from a query problem.
3. **Deterministic checks**: no error; blocked when it should be (and not when it should answer);
   expected tools called; no forbidden substring in the reply.
4. **Judge** (`EVAL_JUDGE_MODEL`, default `google/gemini-3.8-flash`, temperature 0): rubric in
   `app/evals/prompts/judge.md`, scores 1-5 for accuracy, completeness and relevance (from the
   course) plus groundedness and behaviour. It sees the question, the expected behaviour, the
   reference answer, the retrieved context, the tools called and the reply.

A case **passes** when every check passes and the judge gives accuracy and behaviour of at least 4.

## Online evaluation in Langfuse

The offline evaluation tests the dataset; an **LLM-as-a-judge evaluator in Langfuse** scores a
sample of real production turns. It runs on Langfuse's side, with an LLM connection configured
there, so the app makes no extra calls. Its prompts are versioned here and pasted into Langfuse:

| Score | Prompt | Variables |
| --- | --- | --- |
| `online_groundedness` (0-1) | `app/evals/prompts/online_groundedness.md` | `input`, `output`, `tools`, `context` |
| `online_behavior` (0-1) | `app/evals/prompts/online_behavior.md` | `input`, `output`, `tools` |

Observation-level evaluators only see the observation they run on, so the root span `chat-turn`
carries what the judge needs in its metadata: `tools_called` and `context` (the tool results of the
turn). It sees only the last user message, not the conversation history.

Setup in Langfuse (once per project):

1. **Settings → LLM Connections → Add**: provider *OpenAI*, base URL `https://openrouter.ai/api/v1`,
   your OpenRouter key. Turn off **Enable default models** (OpenAI's names, which OpenRouter
   rejects) and add `google/gemini-3.8-flash` under **Custom models**: OpenRouter needs
   `provider/model` names.
2. **Evaluators → Set up evaluator → Create custom evaluator**, one per prompt: paste the prompt,
   model `google/gemini-3.8-flash`, score name as in the table, and describe the score as a number
   from 0 to 1 with a short reasoning.
3. Run it on **observations**, filtered by name `chat-turn` and environment `production`, on new
   data only, with a sampling rate (for example 20 %, to keep the LLM cost down).
4. Map the variables: `input` → Input, `output` → Output, `tools` → Metadata `$.tools_called`,
   `context` → Metadata `$.context`.

Scores appear on each trace and in the Langfuse dashboards over time. Evaluation
runs (`make eval`) produce no `chat-turn` observation, so the online judge never scores them.

## Adding cases

Add a line to `dataset.jsonl` with the next id in its category and keep 5 per category (or update
the test if the categories change). Keywords must be copied from the knowledge file listed in
`expected_sources`. Run `make test`, then `make eval args="--id <new-id>"`.
