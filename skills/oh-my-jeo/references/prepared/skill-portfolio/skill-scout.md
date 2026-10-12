# Prepared guidance: skill-scout

Family: `skill-portfolio`  
Category: `operations`  
Phase: `skill-scout`  
Role: `operator`

## Contract
[omh] Existing skills to reuse before authoring: prepare a metadata-only search-before-creation report for local, marketplace, GitHub, and web skill candidates with risk review and adoption options. Use when the user says: skill-scout, skill scout, skill candidate, skill candidate search, skill discovery, find a skill, find skills, top skills.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- skill-scout
- skill scout
- skill candidate
- skill candidate search
- skill discovery
- find a skill
- find skills
- top skills
- popular skills
- famous hermes skills
- useful hermes skills
- hermes skills/plugin
- skills/plugin
- agentskills.io top skills
- is there a skill
- existing skill
- fork a skill
- extend a skill
- create skill after search
- new skill search
- skill adoption
- 스킬 스카우트
- 스킬 후보
- 스킬 찾기
- 스킬 검색
- 스킬 만들기 전
- 유명한 hermes skills
- 유명한 hermes skill
- 유용한 hermes skills
- 스킬 플러그인 후보
- 플러그인 찾아
- 플러그인 비교
- 없는 것 설치할지 비교
- 기존 스킬

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- skill_scout_query/v1
- local_skill_candidate_inventory/v1 when observed
- external_skill_candidate_risk_review/v1 when observed
- awesome_hermes_agent_coverage/v1 for upstream ecosystem comparison when requested
- skill_adoption_decision_matrix/v1
- skill_scout_recommendation/v1

## Artifact expectations
- skill_scout_query/v1 with intended workflow, triggers, domains/tools, and search keywords
- local_skill_candidate_inventory/v1 separating installed, bundled, marketplace, and repo-local matches when observed
- awesome_hermes_agent_coverage/v1 mapping upstream ecosystem entries to OMH covered, partial, or missing_candidate coverage statuses, matched OMH surfaces, rule_set_version, and matched_rule_id
- skill_adoption_decision_matrix/v1 ranking use existing, fork or extend, and create fresh options with trust gaps

## Acceptance criteria
- Intent, keywords, source scope, and stop condition are explicit.
- Local and external search evidence is separated from planned search.
- No install, copy, write, credential, or trust claim is made without observed review or implementation.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- quality_tier: workflow-surface-gated
- contract_source: skills/omh-skill-scout/SKILL.md:65
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-skill-scout/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-skill-scout/SKILL.md`
- SHA256: `0f889802c7a8b9ad0b3ccb36014a42486023cb96283817f6e29ff8272ae170a9`

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
prepared_not_observed for skill-scout: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
