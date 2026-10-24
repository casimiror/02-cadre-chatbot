# Cadre AI — LLM selection, data security and guardrails
<!-- Source: "LLM selection & data security" bullets (strategy, ai-engineering) and the data
security answer (data-and-dashboards) are from cadre.ai. The guardrail and AI security method is
synthetic: written for this take-home from general AI security practice. -->

## LLM selection and data security approach
Cadre helps each client:
- Select the right LLM for each use case.
- Black-box company data so it is never used to train other models.
- Stop employees from sharing company secrets on personal LLM accounts.
- Get the whole team on secure, compliant AI tools.
Cadre is model-agnostic: it is an official partner of both Anthropic and OpenAI and works with
Microsoft Copilot and other platforms, so the recommendation follows the client's tech stack, data
and use cases rather than a single vendor.

## How client data is protected
In Cadre's data builds, each customer gets an isolated instance on a SOC 2 Type II platform. There
is zero AI data retention under signed agreements with the AI providers, client data never trains a
model, and row-level security controls who sees what at query time. Cadre favors business and
enterprise AI plans whose terms exclude training on customer data, with single sign-on and admin
controls. Data is encrypted in transit and at rest, and secrets are stored in a secrets manager.

## Guardrails in Cadre's AI systems
Guardrails are checks that run before and after the model:
- Input guardrails: length limits, detection of prompt injection and jailbreak attempts, blocking
  sensitive data (for example card numbers or credentials) before it reaches the model.
- Topic restrictions: the assistant stays within its job and declines regulated advice it is not
  authorized to give (legal, medical, financial) or information about other companies.
- Output guardrails: block unsupported claims, prices or links that did not come from an approved
  source, personal data that should not be shown, and off-brand or harmful content.
- Action guardrails: risky tool calls need confirmation or human approval.
When a guardrail triggers, the user gets a safe, helpful fallback (for example an offer to talk to
a person) and the event is logged.

## Prompt injection and adversarial inputs
Prompt injection is an attempt to override the AI's instructions, either typed by a user ("ignore
your rules") or hidden in a document or web page the AI reads. Cadre's defenses:
- Keep trusted instructions separate from untrusted content, and treat retrieved text as data.
- Never let the model reveal its instructions, secrets or other users' data.
- Validate permissions in the tool, not in the prompt, so a manipulated model still cannot act
  beyond its access.
- Test every assistant with injection and adversarial cases before launch and after changes.

## Personal data (PII) handling
Cadre minimizes the personal data AI systems see: only the fields the workflow needs, masked or
redacted where possible, and never used for training. Conversation logs that contain personal data
follow the client's retention policy, and assistants that collect contact details (like this one)
ask for them explicitly and use them only to follow up on the request.

## Monitoring and tuning guardrails
Guardrails are measured like any other part of the system: how often they block, false positives
(legitimate requests blocked) and false negatives (bad outputs that got through). Cadre reviews
blocked conversations regularly and adjusts the rules without breaking legitimate use.

## Cost and usage controls
Cadre protects clients from runaway AI spend with rate limits per user, input size limits, spend
alerts and budgets per workflow, and a model selection policy that keeps expensive models for the
tasks that need them.
