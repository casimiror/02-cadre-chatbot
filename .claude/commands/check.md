---
description: Lint, test and build everything before a commit
---
Run, in order, and stop at the first failure (show the error and fix it before continuing):

1. `cd backend && uv run ruff check . && uv run ruff format --check .`
2. `cd backend && uv run pytest -q`
3. `cd backend && uv run alembic check` only if `DATABASE_URL` points to a reachable DB
   (detects models that changed without a migration); otherwise `uv run alembic upgrade head --sql > /dev/null`.
4. `cd frontend && npm run build`

Then delegate a review of the staged diff to the `verifier` subagent and report its findings.
Do not commit; summarize what passed and propose a commit message.
