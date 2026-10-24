# Cadre AI — how Cadre designs AI agents
<!-- Source: the three agent levels, "digital employees", SOPs and human oversight are from
cadre.ai (agents, strategy). The design method, patterns and human-in-the-loop detail are
synthetic: written for this take-home from general agentic AI practice. -->

## When to use an agent, a workflow or a prompt
Cadre picks the simplest thing that solves the problem:
- Prompt or assistant: one person, one task, a human reviews every output (drafting, summarizing).
- Workflow automation: the steps are known and repeatable; AI handles the fuzzy parts such as
  classifying an email or extracting fields from a document.
- AI agent: the path changes case by case, the work spans several tools, and the agent has to plan
  and decide the next step itself.
Many projects start as a workflow with AI steps and become an agent only when the variety of cases
requires it. Deterministic logic stays in code; the model is used where judgment is needed.

## Agent readiness: what an agent needs before it is built
Cadre treats AI agents like digital employees. Before building one, the client needs:
- A documented SOP for the process, including exceptions and who handles them today.
- Access to the systems involved through APIs, with credentials for the agent itself.
- Company templates and examples of good output.
- A business owner who reviews the agent's work and a definition of success (time saved, error rate,
  volume handled).
Like people, agents improve with monitoring, feedback and training, and are much better six months
in than on day one.

## Anatomy of a Cadre agent
Every agent Cadre builds is defined by:
- Role and goal: one clear job for one team, written as the agent's instructions.
- Model: chosen per task by Cadre's model selection policy (fast models for routing and
  extraction, stronger models for complex reasoning).
- Tools: the specific actions it may take (search knowledge, read the CRM, create a ticket, draft
  an email), each with a narrow permission.
- Memory: short-term conversation context, plus long-term knowledge retrieved from approved
  sources instead of stuffed into the prompt.
- Guardrails: input and output checks, topic limits and approval steps for risky actions.
- Evaluation and observability: a test set before launch and tracing of every run after.

## Single agent or multi-agent
Cadre starts with a single agent with a few well-described tools, because it is easier to test and
explain. It moves to several specialized agents only when one agent's instructions get too broad or
tasks benefit from specialists. Patterns Cadre uses:
- Graph: predefined steps and conditional branches, ideal for customer support and escalation
  flows (this support assistant is built that way).
- Workflow pipeline: a fixed sequence such as extract, validate, enrich, report.
- Supervisor with specialists: a coordinating agent routes subtasks to a research, a drafting or a
  validation agent.
Every handoff between agents is logged so the whole run can be traced.

## Human in the loop
Cadre designs the level of autonomy per action, not per agent:
- Human in the loop: the agent prepares, a person approves before anything is sent or changed
  (payments, contracts, customer-facing messages in regulated contexts).
- Human on the loop: the agent acts on its own and people review samples and exceptions.
- Machine in the loop: a person does the work and AI assists with suggestions and checks.
Agents escalate to a person when confidence is low, data is missing, the case is outside policy or
the user asks for a human, and the person's decision is recorded as feedback to improve the agent.

## Designing agent tools
Tools are the agent's hands, so Cadre designs them carefully:
- One clear purpose per tool, with a description that says when to use it.
- Typed, validated inputs; the agent never builds raw queries or URLs.
- Least privilege: read-only unless the workflow needs to write, scoped to the records it needs.
- Safe failures: short error messages the agent can act on (retry, ask the user, escalate).
- Limits: timeouts, rate limits and confirmation steps for irreversible actions.
- Standard connectors such as the Model Context Protocol (MCP) when the client's tools support it.

## From pilot to production agent
1. Map the process and define success metrics with the business owner.
2. Build a pilot on real but limited data and test it against a set of real cases.
3. Run it alongside the current process (shadow mode) and compare results.
4. Launch to a small group with human review, then widen autonomy as quality is proven.
5. Monitor usage, quality and cost, and run a 30/60/90-day validation before calling it done.
