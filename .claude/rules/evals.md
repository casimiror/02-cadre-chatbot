---
paths:
  - "backend/app/evals/**"
---
# Evaluation

Before changing the evaluator or its dataset, read `docs/evaluation.md`. Keep 5 cases per category,
copy keywords from the files in `expected_sources`, and never let the evaluator write to a real
database (tools get in-memory repositories).
