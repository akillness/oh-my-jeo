# Prepared guidance: instinct-ledger

Family: `atomic-instincts`  
Category: `optimization`  
Phase: `instinct-ledger`  
Role: `tracker`

## Contract
[omh] Recurring lessons worth promoting: turn repeated project or cross-project lessons into atomic, confidence-scored instinct candidates with scoped promotion and export boundaries. Use when the user says: instinct-ledger, instinct ledger, project instincts, project-scoped instincts, project scoped instincts, global instincts, instinct review, instinct candidate.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- instinct-ledger
- instinct ledger
- project instincts
- project-scoped instincts
- project scoped instincts
- global instincts
- instinct review
- instinct candidate

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- instinct_ledger_plan/v1
- instinct_candidate/v1
- project_instinct_scope_map/v1
- instinct_promotion_review/v1
- instinct_export_review/v1 when requested

## Artifact expectations
- instinct_candidate/v1 with trigger, action, confidence, domain, scope, source evidence, non-goals, and review state
- project_instinct_scope_map/v1 separating project, global, imported, and promotion-candidate instincts
- instinct_promotion_review/v1 with repeated evidence, confidence threshold, conflicts, and approval state
- instinct_export_review/v1 with redaction, destination, import/export trust gaps, and raw-observation exclusion when requested

## Acceptance criteria
- Each instinct is atomic: one trigger, one action, one scope, confidence, evidence refs, and review state.
- Project-specific conventions, global practices, project/global promotion candidates, imports, and exports are separated.
- No hooks, memory writes, skill edits, global promotion, import/export, or behavior-change claims are made without observed approval and implementation evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Route only on the source-defined description and triggers; do not treat nearest local contracts workflow-learning as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-instinct-ledger/SKILL.md`
- SHA256: `dfa7798ccd95bd2a92ffc5c0a0451f90675af65411cc1f8e74472ac1805b1a4b`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member instinct-ledger is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
