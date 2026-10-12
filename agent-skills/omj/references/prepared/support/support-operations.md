# Prepared guidance: support-operations

Family: `support`<br>
Category: `triage`<br>
Phase: `support-operations`<br>
Role: `operator`

## Contract
[omh] Support ticket your team must answer or escalate: turn a support case into a clear customer reply, severity path, and owned next step. Use when the user says: support escalation, customer support reply, ticket triage, 고객 지원 에스컬레이션, 고객 답변 초안, 지원 티켓 분류.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- support-operations
- support escalation
- customer support reply
- ticket triage
- 고객 지원 에스컬레이션
- 고객 답변 초안
- 지원 티켓 분류

## Required inputs
- support case
- known facts
- customer impact
- available ownership or escalation path

## Expected outputs
- customer-safe reply draft with stated facts, unknowns, and tone
- issue/severity/impact/escalation matrix
- internal next-step and owner handoff brief
- missing repro, account, entitlement, or approval evidence list

## Artifact expectations
- prepared support case brief when a wrapper captures it
- Artifact contracts:
- This label denotes the machine-enforcement level, not a skill quality score and not an observed evidence state.
- contract_id: `support-operations`; enforcement_level: `guidance_only`; consumer_id: `none`

## Acceptance criteria
- The source boundary, signal clusters, severity, and follow-up lane are named.
- Bug, feature, research, strategy, and coding handoff outcomes stay separate.
- The next workflow is recommended before any implementation claim.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Reply text is a draft, escalation is a recommendation, and no ticket state, message send, refund, account action, or customer outcome is claimed.

## Catalog rules
- Source routing exclusion: The request clusters a backlog of customer signals to find product patterns or roadmap candidates; use `feedback-triage`.
- Source routing exclusion: The user only needs a generic, non-support marketing or email rewrite with no case, severity, or escalation context; use `content-operator`.
- Source routing exclusion: The request asks to send a reply, change ticket priority or status, issue a refund, modify an account, or update a helpdesk; use `connector-operator` with an explicit target and observed result.
- Source routing exclusion: The request is an incident that is still open, needing severity declared, a commander assigned, and a running timeline rather than a support-case response; use `live-incident-response`.
- Source routing exclusion: The request is a closed incident's postmortem or reliability evidence rather than a support-case response; use `reliability-review`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts feedback-triage as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-support-operations/SKILL.md`
- SHA256: `66d79e8a68058f862823032d8aa599c2bb12ebba15b1f88adeb5c81b8a3a8719`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member support-operations is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Reply text is a draft, escalation is a recommendation, and no ticket state, message send, refund, account action, or customer outcome is claimed. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
