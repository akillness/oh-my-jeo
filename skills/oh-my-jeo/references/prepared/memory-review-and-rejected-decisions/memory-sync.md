# Prepared guidance: memory-sync

Family: `memory-review-and-rejected-decisions`  
Category: `memory`  
Phase: `curation-review`  
Role: `memory-keeper`

## Contract
[omh] Outdated or wrong Hermes memory entries: English-canonical Hermes memory-review guidance: inspect USER.md and MEMORY.md claims and prepare a native write diff without invoking, applying, or observing a native write; for a new fact use memory-new, and for a past decision use decision-recall. Use when the user says: memory-sync, memory curation, memory review, memory inspect, memory check, memory update, context cleanup, curate memory.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- memory-sync
- memory curation
- memory review
- memory inspect
- memory check
- memory update
- context cleanup
- curate memory

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- memory-sync/v1 card or guidance
- next action
- prepared-vs-observed boundary

## Artifact expectations
- memory-sync/v1 metadata-only runtime or wrapper card when recorded

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

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
- Source path: `skills/omh-memory-sync/SKILL.md`
- SHA256: `22274080815463ec40d0c49f91b5c233bf94498d8d4dfc1df1c1dd6eef84cbdc`

## Method references
- `omh-memory-sync/references/source-recovery.md` (pinned `skills/omh-memory-sync/references/source-recovery.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member memory-sync is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
