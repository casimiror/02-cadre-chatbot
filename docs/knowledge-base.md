# Knowledge base

What the bot is allowed to know. Markdown files in `backend/app/knowledge/`, searched by the
`search_knowledge` tool.

## Sources

Each file's header comment (before the first `##`, not indexed) says where its content comes from:

- **From cadre.ai** (scraped 2026-10-24): `company`, `services`, `industries-and-departments`,
  `case-studies`, `faq`, `model-selection`.
- **Synthetic**, written for this exercise as Cadre's methodology from general practice:
  `ai-governance`, `agent-design`, `retrieval-and-knowledge`, `security-and-guardrails`,
  `evaluation-and-production`, `compliance`, and the maturity levels in `ai-maturity-index`.

Never present synthetic content as published by Cadre outside the bot, and never add
certifications, clients, prices or URLs that aren't in a source.

## Writing sections

- Split by `## ` headings; each section is one retrievable chunk, so make it self-contained and
  about 100-250 words.
- Put the words people search with in the heading (titles weigh 3x in ranking).
- No raw URLs and no `$` amounts: the output guardrails would replace the whole reply. Write
  amounts as `420,000 USD`; links come from `Settings` through tools.
- English only (the tool asks the model for English keywords).

## Retrieval

`backend/app/tools/knowledge/kb.py`: BM25 over all sections, title words weighted 3x, plurals
folded, small stopword list, top 3 returned with their `[file › heading]` source. Keyword search
is intentional: small KB, easy to debug. Revisit (hybrid or pgvector) if the KB grows past ~50
documents or users phrase things very differently from the headings.

## Tests

`backend/tests/test_knowledge.py` checks that scenario queries hit the expected file and that no
section would trip the output guardrails. Add a query there when you add a topic.
