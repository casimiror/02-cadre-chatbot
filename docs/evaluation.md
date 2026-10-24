# Evaluation

Offline evaluation of the support agent, adapted from the RAG course evaluator (retrieval MRR /
nDCG / keyword coverage plus an LLM judge). Code in `backend/app/evals/`. It runs locally only:
every case calls the LLM, so it is never mounted on the deployed app.

```bash
make eval                                   # all 60 cases, results to Langfuse + JSON
make eval args="--category guardrail"       # one category (repeatable)
make eval args="--id booking-03 --no-langfuse"
```

Each run writes `backend/eval_runs/<run-id>.json` (gitignored) and, with Langfuse configured, an
experiment run on the `cadre-support-eval` dataset, with one trace and its scores per case.

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

## How a case is scored

1. **Agent**: the real support agent (`build_support_agent`: same prompt, tools, guardrails and
   model as production) answers the question. Tools that write to the database get in-memory
   repositories, so an evaluation never touches Postgres.
2. **Retrieval**, measured twice:
   - *index*: `KnowledgeBase.search(question)`, which tests the BM25 index and the content;
   - *agent*: the sections its own `search_knowledge` calls returned, which tests whether the agent
     searches well.

   Metrics: MRR, nDCG, keyword coverage, and whether an expected source was retrieved.
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
