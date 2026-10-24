# Cadre AI — retrieval and grounding AI in company knowledge
<!-- Source: "data first", the semantic layer and the separate document build are from
cadre.ai/data-and-dashboards. The RAG method (preparation, chunking, search, citations) is
synthetic: written for this take-home from general retrieval practice. -->

## Why AI needs grounding in company data
A general model does not know a company's business: which field marks one type of deal from
another, what the team means by its terms, or last year's monthly totals. Pointed at raw data it
guesses and answers with confidence. Cadre grounds AI in two kinds of company knowledge: structured
data (records, amounts, dates) through connected and modeled data, and documents (policies, SOPs,
contracts, manuals) through retrieval-augmented generation, also called RAG. In both cases the AI
answers only from the company's sources and says so when it does not have the information.

## Structured data first
For questions about numbers, Cadre connects the systems into one data warehouse, normalizes the
data and writes agreed definitions into a semantic layer before any AI is built (the 60-day data
build). The AI then queries modeled data with agreed definitions instead of guessing from raw
tables, so "gross margin" means the same thing in every report and every AI answer, and the AI
refuses questions about data it cannot access.

## How Cadre builds document retrieval (RAG)
Document retrieval is scoped and built separately from the structured data build:
1. Inventory sources and owners: which documents are authoritative and who keeps them current.
2. Prepare documents: remove duplicates and outdated versions, extract text and tables, normalize
   terms.
3. Add metadata to every document: source, owner, date, version, department and access level.
4. Split documents into chunks that follow their structure (section, procedure, table), keeping the
   heading as context, so each chunk holds one complete idea.
5. Index for search and test retrieval with a set of real questions before connecting the model.
6. Generate answers only from the retrieved passages, with citations.

## Keyword, semantic and hybrid search
- Keyword search matches exact words: precise for product names, codes and policy numbers, and easy
  to debug.
- Semantic (vector) search matches meaning, so "time off" finds "vacation policy", using embeddings.
- Hybrid search combines both and is Cadre's default for larger document sets, often followed by a
  re-ranking step that puts the most relevant passages first.
For a small, curated knowledge base, keyword search is often enough and cheaper to run; Cadre adds
semantic search when the content or the vocabulary of users grows.

## Citations and refusing without evidence
Cadre's retrieval systems show where each answer comes from (document and section) so users can
verify it. If retrieval finds nothing relevant, the assistant says it does not know and offers a
next step, such as escalating to a person, instead of filling the gap with general model knowledge.
This is the main defense against hallucinations in company-facing assistants.

## Permissions in retrieval
Retrieval respects the same access rules as the source systems: a user only gets answers built
from documents and rows they are allowed to see, enforced at query time with metadata filters or
row-level security. Confidential sources can be excluded from an assistant entirely.

## Keeping knowledge current
Each source has an owner and a refresh schedule; structured data refreshes nightly by default.
Documents are versioned so an answer can be traced to the version it used, outdated versions are
removed from the index, and unanswered questions are reviewed regularly to find gaps in the
knowledge base.

## Measuring retrieval quality
Cadre evaluates retrieval separately from the final answer, with a set of real questions and their
expected sources:
- Did the right passage come back in the top results (recall)?
- How much of what came back was relevant (precision)?
- Is the answer faithful to the passages, with no unsupported claims (groundedness)?
- Does the answer actually address the question (relevance)?
