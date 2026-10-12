# Prepared guidance: skill-health

Family: `skill-portfolio`  
Category: `operations`  
Phase: `skill-health`  
Role: `operator`

## Contract
[omh] OMH skill portfolio health overview: prepare a metadata-only OMH skill portfolio dashboard with stale surfaces, observed failure signals, pending amendments, and top actions. Use when the user says: skill-health, skill health, skill portfolio health, skill dashboard, skill health dashboard, skill failure pattern dashboard, skill failure patterns, pending skill amendments.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- skill-health
- skill health
- skill portfolio health
- skill dashboard
- skill health dashboard
- skill failure pattern dashboard
- skill failure patterns
- pending skill amendments
- skill amendments
- 스킬 헬스
- 스킬 상태
- 스킬 대시보드
- 스킬 실패 패턴
- 스킬 개선 후보
- 스킬 보류 수정

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- catalog, generated, reference, harness, and capability-surface status
- observed failure signals, or an explicit statement that none were supplied
- pending amendment review slots and top safe actions with owner lane and verification path

## Artifact expectations
- skill_health_card/v1 metadata-only wrapper card recording surface status, observed-only failure signals, pending amendments, and the non-mutation boundary

## Acceptance criteria
- Dashboard scope, source surfaces, stale/duplicate criteria, and stop condition are explicit.
- Install/setup health is routed to doctor; catalog operations are routed to skill; failure retrospectives are routed to workflow-learning.
- No skill, prompt, doc, memory, or model behavior is claimed changed until a reviewed implementation records evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- quality_tier: workflow-surface-gated
- contract_source: skills/omh-skill-health/SKILL.md:64
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-skill-health/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-skill-health/SKILL.md`
- SHA256: `9ce7b238853c2ba35b2bfabfa81817b624576b92b76ced004879ca3dfcea9d49`

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
prepared_not_observed for skill-health: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
