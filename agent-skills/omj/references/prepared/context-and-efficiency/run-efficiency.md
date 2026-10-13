# Prepared guidance: run-efficiency

Family: `context-and-efficiency`<br>
Category: `observability`<br>
Phase: `run-efficiency`<br>
Role: `tracker`

## Contract
[omh] Run efficiency and context usage report: report supplied local run efficiency while provider and host data stay unobserved. Use when the user says: run-efficiency, run efficiency report, local run efficiency, context utilization, tool duration report, 실행 효율 리포트, 컨텍스트 사용량, 도구 지연 시간.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- run-efficiency
- run efficiency report
- local run efficiency
- context utilization
- tool duration report
- 실행 효율 리포트
- 컨텍스트 사용량
- 도구 지연 시간

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- run_efficiency_report/v1
- context utilization
- not_observed provider and host gaps

## Artifact expectations
- run_efficiency_report/v1 metadata-only report
- supplied `session_activity_receipt/v1` when available; unavailable metrics stay unavailable, never zero

## Acceptance criteria
- The run ID, context budget, surfaces, and supplied observations are explicit.
- Provider billing, cron, and host claims remain not_observed unless separately recorded.
- The report does not intercept, route, or execute provider or host work.

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
- Source path: `skills/omh-run-efficiency/SKILL.md`
- SHA256: `55d3f2ea146cfc156cf89841d0bc092bb6818ebaa388bdae32ec2fcb5003851d`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member run-efficiency is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
