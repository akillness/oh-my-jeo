# Prepared guidance: legal-compliance-review

Family: `legal`<br>
Category: `review`<br>
Phase: `legal-compliance-review`<br>
Role: `reviewer`

## Contract
[omh] Business contract, NDA, or policy with legal risk: surface contract and compliance risks, questions, and escalation points before a legal decision or action. Use when the user says: contract review, contract liability clause, regulatory analysis, compliance review, contract redline, redline the contract, negotiation preparation, negotiation strategy.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- legal-compliance-review
- contract review
- contract liability clause
- regulatory analysis
- compliance review
- contract redline
- redline the contract
- negotiation preparation
- negotiation strategy

## Required inputs
- jurisdiction
- document or process version
- supplied authority
- review objective

## Expected outputs
- legal_scope_authority_record/v1
- legal_issue_traceability_matrix/v1
- legal_risk_counsel_hold_register/v1
- legal_negotiation_preparation/v1 when the objective is a redline rather than an assessment
- legal_review_disposition/v1

## Artifact expectations
- prepared legal and compliance issue matrix when a wrapper captures it
- legal_negotiation_preparation/v1 with one row per contested clause: the playbook position it came from, the proposed language, the fallback, and the walk-away, plus the concession order across rows

## Acceptance criteria
- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. The result is a prepared review and escalation aid, not legal advice, counsel sign-off, compliance certification, contract execution, filing, or regulator communication.

## Catalog rules
- Source routing exclusion: The user needs a final jurisdiction-specific legal opinion, legal representation, or authoritative filing decision; prepare the issue and counsel brief instead.
- Source routing exclusion: The review is about code, secrets, permissions, prompt injection, dependencies, or unsafe tool behavior; use `security-safety-review`.
- Source routing exclusion: The request is a plain-language rewrite without a legal-risk review objective; use `content-operator`.
- Source routing exclusion: The user asks to sign, accept, submit, file, publish, or change a policy or contract in an external system; use `connector-operator` only after explicit authority.
- Route only on the source-defined description and triggers; do not treat nearest local contracts code-review as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-legal-compliance-review/SKILL.md`
- SHA256: `e2c82551a10012f0a0c753b5d474ce8be8a2dc410cc490a3ad259f3193701d22`

## Method references
- `legal-compliance-review/omh-legal-compliance-review/references/negotiation-preparation.md` (pinned `skills/omh-legal-compliance-review/references/negotiation-preparation.md`)
- `legal-compliance-review/omh-legal-compliance-review/references/procedure.md` (pinned `skills/omh-legal-compliance-review/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member legal-compliance-review is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. The result is a prepared review and escalation aid, not legal advice, counsel sign-off, compliance certification, contract execution, filing, or regulator communication. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
