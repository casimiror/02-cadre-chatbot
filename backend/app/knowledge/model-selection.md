# Cadre AI — AI model selection policy
<!-- Source: cadre.ai/articles/ai-model-selection (May 2026), scraped 2026-10-24. -->

## Why model selection matters
Most teams have no model selection strategy: every task runs on the most capable and most
expensive model, whether it needs it or not. Costs compound quickly, slower responses hurt adoption,
and workflows built on the wrong tier are expensive to rearchitect later. Cadre addresses model
selection policy as one of the first structural elements of the AI Transformation Intensive, before
any workflow is built. In Cadre's words, model selection is not a technical decision, it is a
strategy decision.

## Model tiers and what each is for
Using Anthropic's Claude family as the example:
- Fast, low-cost tier (Claude Haiku): document classification and routing, extracting structured
  data from forms, templated answers to common questions, short summaries, simple validation.
- Balanced tier (Claude Sonnet): writing and editing, multi-step research and synthesis, drafting
  policies, customer service that needs judgment and tone, most analytical work. This is the
  practical default for most business workflows.
- Highest-capability tier (Claude Opus): complex due diligence where errors are costly, synthesizing
  conflicting long documents, high-stakes communications, work whose reasoning must be auditable.
In Cadre's experience, roughly 60 to 70 percent of business workflows belong in the fast or
balanced tiers. On high-volume classification, the fast tier can cut per-task cost by 90 percent or
more with equivalent accuracy. The same logic applies to other providers' model families.

## What a model selection policy includes
A policy answers four questions:
1. Which task types belong in each tier: a one-page guide mapping 10 to 15 common workflows to a
   default model.
2. Who decides exceptions: the balanced tier is the default; the top tier requires a deliberate
   choice with a stated reason.
3. How usage is monitored: token spend logged by model and workflow, so it is clear where cost is
   concentrated and where the policy is not followed.
4. When it is reviewed: quarterly, because model capabilities change.
Auditing current workflows and assigning each a default tier is about a one-day exercise; the
policy does not need to be perfect, it needs to exist.

## Choosing between AI platforms
Beyond the model tier, Cadre compares platforms (for example ChatGPT, Claude, Microsoft Copilot) on
how they fit the client's tech stack and documents, data terms and security, admin controls, cost
at the expected volume, and the features the team needs, such as file handling or integrations.
Cadre evaluates candidates on the client's own tasks before recommending one.
