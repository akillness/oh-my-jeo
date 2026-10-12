# Prepared guidance: live-info-operator

Family: `primitive-operators`  
Category: `live-info`  
Phase: `live-info-task`  
Role: `guide`

## Contract
[omh] Live rate, score, or local time a work task needs: policy overlay for live lookups - add provider, freshness, units, and source-quality gates after preferring native live-data tools for ordinary weather, finance, sports, maps, and time-zone requests. Use when the user says: live-info-operator, live info operator, live information, real time information, real-time information, weather today, current weather, weather forecast.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- live-info-operator
- live info operator
- live information
- real time information
- real-time information
- weather today
- current weather
- weather forecast

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- live_info_task_card/v1
- live_info_scope/v1
- freshness_boundary/v1
- live_info_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- live_info_task_card/v1 metadata-only wrapper card when prepared
- live_info_scope/v1 with domain, location or symbol, time window, provider preference, units, and stop condition
- freshness_boundary/v1 separating requested recency, provider timestamp, source quality, and stale-result handling
- live_info_result_manifest/v1 only when provider response, timestamp, quote/source id, or rendered result is observed

## Acceptance criteria
- Domain, location or symbol, time window, provider preference, freshness, units, and stop condition are explicit.
- Provider setup, API access, source quality, stale data, and missing location/symbol decisions are gated or marked missing.
- Weather, price, score, exchange-rate, time-zone, map, place, and traffic facts are reported only from observed provider evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Route only on the source-defined description and triggers; do not treat nearest local contracts toolbelt-readiness, deliverable-package as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-live-info/SKILL.md`
- SHA256: `31df680b2f1c9ab7d3ce011a8bdb14129c6658ab81a1059b2eeaedf7cc6bf55d`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member live-info-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
