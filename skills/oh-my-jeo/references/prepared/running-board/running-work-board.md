# Prepared guidance: running-work-board

Family: `running-board`  
Category: `operator`  
Phase: `observability`  
Role: `tracker`

## Contract
[omh] Live view of running coding units: showing which coding units are running right now, on which runtime and model, with observed tokens and elapsed time. Use when the user says: running-work-board, running work board, which units are running, what models are running, 지금 뭐 돌고 있어, 뭐가 돌고 있어, 어떤 모델로 돌고 있어, 실행 중인 작업 보여줘.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- running-work-board
- running work board
- which units are running
- what models are running
- 지금 뭐 돌고 있어
- 뭐가 돌고 있어
- 어떤 모델로 돌고 있어
- 실행 중인 작업 보여줘

## Required inputs
- local coding artifacts

## Expected outputs
- per-unit runtime and model
- observed tokens and elapsed
- explicit unknowns

## Artifact expectations
- metadata-only status board projection from local artifacts

## Acceptance criteria
- Runtime and model are named per unit, or explicitly reported as unknown.
- Token counts and session references are observed values or the literal unknown, never estimates.
- Elapsed time for an unfinished unit comes from its start marker, which cannot prove the unit is still alive.
- The board is labelled observed activity, not result, verification, review, CI, or merge evidence.

## Handoff policy
Read local dispatch and progress artifacts directly and render the board; never dispatch or modify a unit from this workflow.

## Catalog rules
- quality_tier: evidence-gated
- contract_source: skills/omh-running-work-board/SKILL.md:66
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-running-work-board/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-running-work-board/SKILL.md`
- SHA256: `e456cb2502f40be140fdb71cb9fe6fcbd738351cfc87cd2206b3ea0ba7a30733`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: local coding artifacts

## Evidence boundary
prepared_not_observed for running-work-board: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
