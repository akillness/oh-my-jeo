# Prepared guidance: achievements

Family: `achievements`  
Category: `observability`  
Phase: `telemetry-card`  
Role: `tracker`

## Contract
[omh] Hermes badges unlocked and achievement progress: achievements observation: summarize hermes-achievements badges, tiers, recent unlocks, and progress from local plugin artifacts. Use when the user says: achievements, achievement, badges, badge, my badges, show achievements, achievement summary, unlocked badges.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- achievements
- achievement
- badges
- badge
- my badges
- show achievements
- achievement summary
- unlocked badges
- badge progress
- achievement tier
- recent unlocks
- badge share card
- 実績
- バッジ
- 成就
- 徽章
- 업적
- 배지
- 뱃지
- 도전과제
- 업적 요약

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- hermes_achievements_observation/v1 summary or badge list
- recent unlocks and progress hints
- next action
- prepared-vs-observed boundary

## Artifact expectations
- hermes_achievements_observation/v1 metadata-only payload from `omh achievements` when recorded
- supplied `session_activity_receipt/v1` when available; unavailable metrics stay unavailable, never zero

## Acceptance criteria
- The run or workflow scope, metric window, failure modes, and cost/latency boundary are named.
- Local telemetry, provider truth, billing truth, and completion evidence are separate states.
- Warnings name the next measurement or operator review action.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- quality_tier: workflow-surface-gated
- contract_source: skills/omh-achievements/SKILL.md:64
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-achievements/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-achievements/SKILL.md`
- SHA256: `b815d39bc264004faca4cc7684dc58af435a7a2b106aa0cfe47ae4e33200cfab`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: user request
- Required source input: target context
- Required source input: delivery or status expectation
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for achievements: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
