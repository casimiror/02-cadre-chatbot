# Cadre AI — evaluating AI and taking it to production
<!-- Source: the production validation phase (30/60/90 days, owner outside the build team,
business metrics, 90-day retrospective) is from cadre.ai/articles/validate-ai-implementation-
production (June 2026). Evaluation method and metrics are synthetic: written for this take-home. -->

## What "done" means for an AI project
For Cadre, an AI workflow is not launched when the code is deployed. It is done when the intended
users are performing the intended workflow, producing the intended output, at a frequency that
justifies the investment. Only about a quarter of organizations report AI deployments that moved
past pilot into sustained production use (McKinsey, 2025), and the gap between "shipped" and
"adopted" is where most AI investment is lost.

## Production validation phase (30, 60, 90 days)
Every Cadre implementation includes a validation phase of 30 to 90 days after deployment:
1. Define adoption thresholds before launch: active users, run frequency, what counts as success.
2. Instrument the system: who uses it, how often, and with what result.
3. Structured user feedback sessions at 30, 60 and 90 days: what works, what is broken, what was
   never adopted.
4. Tie production results back to the business case: measured time saved, error rates before and
   after.
The validation owner is not on the build team, success is defined in business terms ("40% more
applications processed with the same headcount", not "94% accuracy"), and a 90-day retrospective
documents what was adopted, what was abandoned and why.

## How Cadre evaluates AI quality before launch
Cadre builds an evaluation set for every assistant or agent: real questions or cases with the
expected answer or behavior, including edge cases. Each version of the prompt, model or tools is
run against it before release, and results are compared with the previous version. Evaluation
mixes three methods:
- Deterministic checks: format, required fields, allowed values, no forbidden content.
- Model-graded checks: a second model scores answers against a rubric (relevance, groundedness,
  tone), calibrated against human ratings.
- Human review: domain experts review samples, especially for high-stakes outputs.

## Quality dimensions Cadre measures
- Relevance: answers the actual question.
- Factual accuracy and groundedness: every claim is backed by an approved source.
- Completeness: nothing critical is missing.
- Helpfulness: the user can complete their goal or knows the next step.
- Tone and brand: matches the role and the client's voice.
- Consistency: similar inputs get similar answers.
- Safety and compliance: no data exposure or disallowed content.
- Task success for agents: the workflow actually completed correctly, end to end.

## Edge cases and adversarial testing
Evaluation sets always include empty or very long inputs, several intents in one message, other
languages, contradictory context, missing data, unavailable tools, and prompt injection and
jailbreak attempts. Each case has an expected behavior and a safe fallback.

## Observability in production
Every production AI system Cadre ships is traced: request, model and prompt version, tool calls,
latency, cost and outcome. Dashboards and alerts track:
- Usage and adoption (active users, runs per day, abandonment).
- Quality (user feedback, unanswered questions, escalation rate, guardrail blocks).
- Reliability (errors, tool failures, latency).
- Cost per task, per user and per workflow.
Alert thresholds are agreed before launch, and traces are kept for incident review and improvement.

## From proof of concept to enterprise adoption
Cadre moves AI from pilot to scale in four phases:
1. Foundation: AI owner, policy, approved platform, connected data, first use cases prioritized.
2. Pilot in production: a few workflows with real users, human review and measured baselines.
3. Scale and optimize: expand what works to more teams, tune models and costs, automate more.
4. Enterprise adoption: AI is part of every department's plan, governed by a repeatable process
   and measured by the AI Maturity Index.
Moving between phases requires evidence: adoption, quality and ROI against the baseline.

## Measuring ROI
Cadre defines the baseline before a pilot (hours spent, volume, error rate, cycle time, revenue
impact) and measures the same numbers after launch. ROI includes the full cost: licenses, model
usage, build and the human time still needed for review and corrections.
