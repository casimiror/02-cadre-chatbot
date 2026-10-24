# Cadre AI — compliance and responsible AI
<!-- Synthetic: written for this take-home from general AI compliance practice. Cadre does not
publish certifications beyond the SOC 2 Type II platform used for data builds; do not claim any. -->

## How Cadre approaches AI compliance
Cadre designs AI implementations so clients can meet their own regulatory and contractual
obligations: it maps which rules apply to each use case, builds the controls into the workflow, and
leaves the evidence (policies, logs, approvals, evaluations) the client needs for audits. Cadre does
not give legal advice: final interpretation of regulations belongs to the client's legal and
compliance team, which Cadre involves from the start of regulated projects.

## Regulations and frameworks Cadre designs for
Depending on industry and location, Cadre aligns AI work with:
- Privacy laws such as GDPR and US state privacy laws like the CCPA/CPRA: data minimization, purpose
  limitation, deletion and access rights, vendor data processing agreements.
- Sector rules: for example financial services and lending (fair lending, record keeping, model
  risk management), healthcare data under HIPAA when it applies, and client confidentiality in
  professional services.
- Security frameworks clients already follow, such as SOC 2 and ISO/IEC 27001.
- AI-specific frameworks: the NIST AI Risk Management Framework, ISO/IEC 42001 (AI management
  systems) and, for companies operating in Europe, the EU AI Act's risk-based obligations.
Whether a specific system complies is decided per client and use case; the assistant cannot
confirm a client's compliance status.

## Compliance controls built into AI workflows
- Data classification: which data each AI system may use, and exclusion of restricted data.
- Vendor review: AI providers with business terms, no training on client data, zero or limited
  retention, and a data processing agreement.
- Human oversight for decisions that affect people (credit, hiring, pricing, eligibility), with
  the human decision recorded.
- Audit trail: inputs, outputs, model and prompt versions, approvals and tool actions are logged
  and retained per policy.
- Transparency: users are told when they are talking to AI and how to reach a person.
- Fairness checks: outputs for high-impact decisions are tested across groups and equivalent
  phrasings to detect bias.

## AI risk classification of use cases
Cadre classifies each use case by impact before building it:
- Low risk: internal productivity (drafting, summarizing, search) with a human using the output.
- Medium risk: customer-facing assistants and automations that act on company systems; needs
  guardrails, monitoring and escalation paths.
- High risk: decisions about people's credit, employment, health or legal rights; needs human
  approval, documented testing, explainability and legal review before launch.
The classification sets the controls, review depth and who must sign off.

## Responsible AI principles
Cadre's AI work follows five principles: people stay accountable for decisions AI supports; AI
answers only from approved sources and admits what it does not know; client data stays private and
never trains models; systems are tested and monitored before and after launch; and teams are
trained to use AI well, including when not to use it.

## Security questionnaires and contracts
Security questionnaires, data processing agreements, NDAs and contract terms are handled by the
Cadre team directly. For these, the assistant offers a strategy call or escalates to a person.
