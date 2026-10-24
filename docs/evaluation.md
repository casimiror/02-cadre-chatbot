# Evaluation

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

Each run writes `backend/eval_runs/<kind>-<timestamp>.json` (gitignored) and, with Langfuse
configured, an experiment run on the `cadre-support-eval` dataset, with one trace and its scores
per case.

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

## Adding cases

Add a line to `dataset.jsonl` with the next id in its category and keep 5 per category (or update
the test if the categories change). Keywords must be copied from the knowledge file listed in
`expected_sources`. Run `make test`, then `make eval args="--id <new-id>"`.
