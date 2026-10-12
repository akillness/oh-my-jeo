# Prepared guidance: people-ops

Family: `people`<br>
Category: `operations`<br>
Phase: `people-operations`<br>
Role: `operator`

## Contract
[omh] Company hiring or HR process to structure: turn hiring and people context into a fair, structured recruiting or people-operations brief. Use when the user says: recruiting plan, hiring scorecard, interview scorecard, candidate debrief, 채용 계획, 면접 평가표, 후보자 비교.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- recruiting plan
- hiring scorecard
- interview scorecard
- candidate debrief
- 채용 계획
- 면접 평가표
- 후보자 비교

## Required inputs
- role or people-process outcome
- available evidence
- decision owner
- policy constraints

## Expected outputs
- role/outcome and must-have versus trainable-criteria brief
- structured interview scorecard and evidence-based debrief template
- hiring-process, interviewer, and decision-owner plan
- inclusion, privacy, policy, and missing-evidence flags with a next route

## Artifact expectations
- prepared people-operations brief when a wrapper captures it

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes can prepare fair process guidance and interview artifacts; it cannot claim a candidate was contacted, evaluated, hired, rejected, or recorded in an HR system.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The request asks for a jurisdiction-specific employment-law conclusion, policy compliance ruling, or contract interpretation; use `legal-compliance-review`.
- Source routing exclusion: The user only needs a one-off job-ad, rejection, or interview-email rewrite; use `content-operator`.
- Source routing exclusion: The user asks to create ATS records, send invitations, book interviews, change employment status, or modify HRIS settings; use `connector-operator` with explicit authorization and observed results.
- Source routing exclusion: The prompt asks the workflow to make an unsupported candidate decision from protected characteristics or missing interview evidence; retain the process and evidence gap instead.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-people-ops/SKILL.md`
- SHA256: `d0bfa06fcf9f9c4fa9c1ecbec0b1e45f5097cbbdeefcac96cffd94dfe5184e18`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member people-ops is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
