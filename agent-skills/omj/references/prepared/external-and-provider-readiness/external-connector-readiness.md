# Prepared guidance: external-connector-readiness

Family: `external-and-provider-readiness`<br>
Category: `connector`<br>
Phase: `connector-readiness`<br>
Role: `guide`

## Contract
[omh] Evaluating a plugin, connector, or API for adoption: external connector readiness - assess whether a named plugin, connector, API, data provider, or multimodal route is safe, affordable, fresh, and observable; use executor-runtime-readiness for coding-owner choice and toolbelt-readiness for missing capability inventory. Use when the user says: external-connector-readiness, external connector readiness, connector readiness matrix, plugin readiness matrix, provider readiness, api readiness, connector adoption, external plugin adoption.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- external-connector-readiness
- external connector readiness
- connector readiness matrix
- plugin readiness matrix
- provider readiness
- api readiness
- connector adoption
- external plugin adoption

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- external_connector_readiness_card/v1
- connector_capability_matrix/v1
- auth_cost_boundary/v1
- live_data_freshness_policy/v1 when live data is required
- multimodal_routing_policy/v1 when screenshots, audio, video, or files are involved
- fallback_route_policy/v1
- connector_trial_manifest/v1 when observed
- memory_provider_posture/v1 when the candidate is an optional memory provider
- memory_provider_trial_comparison/v1 when two or more memory providers are trialled on one corpus
- realtime_voice_trial_receipt/v1 when a supplied realtime voice trial is observed
- realtime_voice_readiness/v1 verdict per voice dimension when a receipt is supplied
- next action
- prepared-vs-observed boundary

## Artifact expectations
- external_connector_readiness_card/v1 metadata-only wrapper card when prepared
- connector_capability_matrix/v1 with candidate, domain, read/write shape, modality, owner workflow, and fallback route
- auth_cost_boundary/v1 separating missing connector, missing credentials, paid/provider cost risk, quota, and user authority
- live_data_freshness_policy/v1 for requested recency, provider timestamp, stale-result handling, and source-quality thresholds
- multimodal_routing_policy/v1 for screenshot, audio, video, file, OCR, or visual QA evidence routes when needed
- connector_trial_manifest/v1 only when a provider response, capture id, query transcript, message id, or tool-call observation is recorded
- memory_provider_posture/v1 for an optional memory provider, covering identity scope, automatic hooks, storage boundary, synchronization, failure, retention, deletion, export/import, backup/restore, and portability, each marked ready, missing, risky, not_observed, or unknown
- memory_provider_trial_comparison/v1 built on the connector_trial_manifest/v1 pattern: one corpus and one query set per candidate, retrieval quality, latency, and cost each reported per provider or marked not_observed, plus the migration route and the rollback that was exercised rather than asserted
- realtime_voice_trial_receipt/v1 only when an authorized host, connector, or operator supplies the observed trial: connector build identity, requested versus observed stack, per-turn milestones on one declared timing reference, turn-integrity states, fallback path, interruption behavior, and spoken tool decisions
- realtime_voice_readiness/v1 with a pass, hold, or block state and reasons for turn integrity, latency, fallback, interruption, and tool safety, plus the separated connector-configured, synthetic-trial, actual-environment-trial, voice-turn, tool-action, and session-completed states

## Acceptance criteria
- Candidate connector, target domain, read/write scope, modality needs, provider owner, fallback workflow, and stop condition are explicit.
- Cost, quota, credential, permission, live-data freshness, multimodal capture, safety, and compliance boundaries are marked ready, missing, risky, or not_observed.
- Route live read-only lookups to live-info-operator, external writes to connector-operator, datasets/SQL to data-analysis, and missing tools to toolbelt-readiness before claiming results.
- Provider responses, screenshots, audio/video/file captures, query outputs, message ids, and external mutations are reported only from observed trial evidence.
- For a memory provider, disabling it, removing its local cache, deleting its remote memory, deleting the account, and switching away are reported as distinct operations with distinct postconditions.
- Unknown deletion, isolation, or write semantics block automatic writes and irreversible adoption instead of resolving to an OMH or Hermes default.
- For a realtime voice connector, keep turn integrity, latency, fallback, interruption, and spoken tool safety separate; report unsupported or unobserved dimensions as hold or block rather than as a pass.

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
- Source path: `skills/omh-external-connector-readiness/SKILL.md`
- SHA256: `e20e1cba2e2fe35516c16419c443575beb451256b31084e3bdf29fd1aa8cdb05`

## Method references
- `external-connector-readiness/omh-external-connector-readiness/references/memory-provider-trial.md` (pinned `skills/omh-external-connector-readiness/references/memory-provider-trial.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member external-connector-readiness is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
