# Cadre AI — AI governance framework
<!-- Synthetic: written for this take-home as Cadre's methodology, based on general AI governance
practice (prompt management, access control, audit, risk management). Not published by Cadre. -->

## What AI governance means at Cadre
For Cadre, AI governance is the set of owners, policies and controls that let a company use AI
quickly without losing control of its data, costs or quality. Governance is not a brake added at
the end: it is set up during the AI Transformation Intensive, before workflows are built, so every
new use case follows the same rules. It covers who owns AI decisions, which tools and models are
approved, how prompts and agents change, how usage is logged and audited, and how risks are
tracked.

## Roles and ownership
Cadre helps each client name an accountable AI leader who reports to the CEO, and a small AI
council with business, IT/security, legal/compliance and finance representatives. Each AI workflow
or agent has a business owner (accountable for results), a technical owner (accountable for how it
runs) and a reviewer who is not on the build team. Internal AI champions in each department collect
feedback and new use case ideas.

## AI acceptable use policy
Every client gets a written AI policy that employees can understand in a few minutes:
- Which AI platforms are approved, and that company data never goes into personal AI accounts.
- What data may and may not be shared with AI tools (for example customer PII, credentials,
  unreleased financials).
- When a human must review AI output before it is sent or acted on.
- How to request a new AI tool or use case.
- Who to contact about mistakes or incidents.

## Approved tools and the AI command center
Cadre recommends choosing one company-wide AI command center (such as ChatGPT for Business, Microsoft
Copilot or Claude) with business-grade data terms, single sign-on and admin controls, instead of a
patchwork of individual subscriptions. New tools go through a short review: business case, data
handled, vendor data terms, security and integration fit.

## Prompt and agent change management
Prompts, agent instructions and tool configurations are treated like code: stored in version
control, reviewed before release, tested against an evaluation set, and released with a change log
so any answer can be traced back to the version that produced it. Changes that affect regulated or
customer-facing workflows need sign-off from the business owner. Development, testing and
production environments are kept separate, and every release has a rollback plan.

## Access control and least privilege
AI systems get only the access they need. Agents and tools use their own service identities, not a
person's account, with read-only access by default and write access only where the workflow needs
it. Users only see answers built from data they are allowed to see (for example row-level security
at query time). Secrets live in a secrets manager, never in prompts or code.

## Logging, audit and monitoring
Every AI interaction in a production workflow is logged with who asked, which model and prompt
version answered, which tools were called and what the result was. Logs feed dashboards for usage,
quality, cost and policy violations, and are retained according to the client's data retention
policy. Audits review samples of conversations, blocked requests and escalations on a fixed
cadence.

## AI risk management
Cadre keeps a risk register per client that covers three levels:
- Technical risk: service outages, scaling limits, integration breaks. Controls: timeouts, retries,
  fallbacks, load tests, rollback plans.
- Operational risk: runaway costs, security incidents, data leaks. Controls: spend limits and
  alerts, model selection policy, guardrails, incident runbooks.
- Business risk: low adoption, unclear ROI, change fatigue. Controls: baseline KPIs before the
  pilot, training, validation phase after launch.
Each risk has an owner, likelihood, impact, controls and the signals that are monitored. The
register is reviewed whenever a model, data source or workflow changes.

## Governance review cadence
- Weekly during a rollout: usage, incidents, user feedback.
- Monthly: cost per workflow, quality metrics, blocked requests, open risks.
- Quarterly: model selection policy, approved tools, AI policy updates and the roadmap.
- Every 6 to 12 months: re-run the AI Maturity Index.
