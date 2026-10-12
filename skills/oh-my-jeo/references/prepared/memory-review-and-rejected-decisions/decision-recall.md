# Prepared guidance: decision-recall

Family: `memory-review-and-rejected-decisions`<br>
Category: `memory`<br>
Phase: `decision-recall`<br>
Role: `memory-keeper`

## Contract
[omh] Previously rejected options to revisit: recall scoped reviewed rejected decisions without elevating them to approved memory. Use when the user says: decision-recall, rejected decision recall, rejected decisions, why was this rejected, previously rejected alternative, 거절된 결정, 기각된 대안.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- decision-recall
- rejected decision recall
- rejected decisions
- why was this rejected
- previously rejected alternative
- 거절된 결정
- 기각된 대안

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- rejected_decision_recall/v1
- scoped rejected-decision matches
- claim boundary

## Artifact expectations
- rejected_decision_recall/v1 metadata-only recall result

## Acceptance criteria
- The query, scope, tags, stale policy, and match limit are explicit.
- Only reviewed rejected candidates are returned; expired candidates stay excluded.
- Recall output is not presented as approved memory, source freshness, or execution evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-decision-recall/SKILL.md`
- SHA256: `ddd0e6b703ab6edb1acb0f01db3a51eb1cc1f2d4a4da0f04326d7ad409eb6fbc`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member decision-recall is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
