# Prepared guidance: rules-distill

Family: `rule-candidates`  
Category: `knowledge`  
Phase: `rules-distillation`  
Role: `memory-keeper`

## Contract
[omh] Turn repeated lessons into written rules: extract repeated principles from skills, prompts, traces, reviews, and failures into reviewed rule candidates without auto-mutating guidance. Use when the user says: rules-distill, rules distill, distill rules, rule distillation, principle distill, skill principles, extract agent rules, turn traces into rules.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- rules-distill
- rules distill
- distill rules
- rule distillation
- principle distill
- skill principles
- extract agent rules
- turn traces into rules

## Required inputs
- source corpus: skills, prompts, traces, reviews, failures, or docs
- destination boundary: AGENTS, skill catalog, prompt, docs, memory, or no-write review
- rule granularity and acceptance criteria
- reviewer or approval requirement

## Expected outputs
- rules_distillation_plan/v1
- principle_candidate_set/v1
- duplication_conflict_report/v1
- review_queue/v1
- approved_patch_handoff/v1 when approved
- not-evidence boundary

## Artifact expectations
- principle_candidate_set/v1 with source references, repeated pattern, candidate wording, scope, non-goals, and risk
- duplication_conflict_report/v1 with already-covered rules, conflicts, and stale guidance
- review_queue/v1 separating proposed, approved, rejected, deferred, and needs-evidence candidates

## Acceptance criteria
- The durable fact, source evidence, retrieval hint, and staleness risk are recorded.
- Uncertain or conflicting knowledge is marked as review-needed rather than permanent truth.
- Separate coding or docs tasks are extracted instead of buried in notes.

## Handoff policy
Keep principle extraction and candidate review in Hermes. Editing AGENTS.md, catalog data, prompts, skills, or docs requires explicit approved implementation work and verification.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The user wants a single workflow route regression; use `workflow-learning`.
- Source routing exclusion: The user wants durable factual project memory; use `wiki` or memory curation.
- Source routing exclusion: The user already approved a concrete code/doc change; use the implementation workflow.
- Source routing exclusion: The ask is writing or keeping current the file an agent reads at startup -- AGENTS.md, CLAUDE.md, a Cursor rule; use `agent-instructions`, which updates only its marked region.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-rules-distill/SKILL.md`
- SHA256: `71e259d34ecffd67e10898e07e65921e4ef8caec8ca1983463dcdbdd54db37d8`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member rules-distill is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
