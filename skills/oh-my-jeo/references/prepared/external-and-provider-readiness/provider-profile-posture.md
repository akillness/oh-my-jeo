# Prepared guidance: provider-profile-posture

Family: `external-and-provider-readiness`  
Category: `operations`  
Phase: `provider-profile-posture`  
Role: `operator`

## Contract
[omh] Provider credentials without exposure: prepare provider-profile metadata without reading secrets or calling providers. Use when the user says: provider-profile-posture, provider profile posture, provider profile readiness, secret presence confirmation, connector profile posture, 공급자 프로필 상태, 시크릿 존재 확인, 커넥터 준비 상태.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- provider-profile-posture
- provider profile posture
- provider profile readiness
- secret presence confirmation
- connector profile posture
- 공급자 프로필 상태
- 시크릿 존재 확인
- 커넥터 준비 상태

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- provider_profile_posture/v1
- metadata-only secret requirements
- allowed and prohibited actions

## Artifact expectations
- provider_profile_posture/v1 metadata-only preparation record

## Acceptance criteria
- Provider ID, profile ID, requested capabilities, and secret-presence metadata are explicit.
- No secret value, credential validation, provider call, model route, wallet, or payment action is claimed.
- Any host observation reference remains supplied metadata, not a live connector check.

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
- Source path: `skills/omh-provider-profile-posture/SKILL.md`
- SHA256: `155e9a6d64c0fb80d10c373c73d30428455de83ede5896c34b20fd13a240ef01`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member provider-profile-posture is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
