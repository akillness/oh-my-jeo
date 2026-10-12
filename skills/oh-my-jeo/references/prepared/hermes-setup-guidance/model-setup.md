# Prepared guidance: model-setup

Family: `hermes-setup-guidance`<br>
Category: `hermes-setup`<br>
Phase: `setup`<br>
Role: `guide`

## Contract
[omh] Model and provider configuration changes: diagnose role-slot model configuration, guide provider connection, and apply changes only after diff approval. Use when the user says: model-setup, hermes model setup, set up my models, set up my model, configure my models, configure model provider, connect my model provider, set up model role slots.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- model-setup
- hermes model setup
- set up my models
- set up my model
- configure my models
- configure model provider
- connect my model provider
- set up model role slots

## Required inputs
- metadata-only discovery report and its source/candidate states
- user confirmation of which discovered models and providers are currently active
- target Hermes role alias (main, realtime-search, or design), semantic category, X-platform domain, or external coding owner
- optional user-edited recommendation overrides

## Expected outputs
- source-labeled candidate inventory separating historical observation from confirmed-active models
- editable editorial recommendation chains resolved only against confirmed-active compatible candidates
- Hermes-native alias/provider preview or a separate Maestro ordered external-handoff recommendation
- verification checklist or an incomplete non-blocking setup advisory with exact next actions

## Artifact expectations
- model_discovery/v1 metadata-only report when local discovery runs
- model_recommendation_resolution/v3 recommendation result when a chain is resolved
- omh_model_activation/v1 setup receipt when the setup surface captures it

## Acceptance criteria
- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- Every emitted metadata identifier passed the safe allowlist and every candidate retains a closed source state.
- Hermes-native configuration and Maestro external-handoff recommendations are reported as separate owner surfaces.
- Every requested write was previewed, explicitly approved, digest-checked, and re-verified; unresolved model items did not block unrelated setup.

## Handoff policy
Keep Hermes-native model setup in Hermes: inspect its config, provider plugins, auth presence, and aliases, then use Hermes-native config/auth flows for an approved change. Maestro coordinates prepared external coding handoffs for Codex, Claude Code, OMO/OMC/OMX, and generic owners; it is not an executor and never owns Hermes aliases, providers, skill execution, or Kanban model selection. Diagnosis uses local Hermes config/auth commands and reads only config plus auth/plugin presence; it never reads `.env` values, credential material, or session prose. Show the exact Hermes-native command/config preview, bind it to the inspected config digest, and apply only after explicit approval; verify by re-inspecting Hermes state. A prepared Hermes binding or Maestro handoff is not model invocation, dispatch, or execution evidence.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: hermes-setup-gated
- source owner: skills/omh-model-setup/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-model-setup/SKILL.md`
- SHA256: `ba7bec0b39bb499b6a67279b44835cd4253cdc461c6f044bd7fa855098c428d1`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: metadata-only discovery report and its source/candidate states
- blocked until supplied or observed: user confirmation of which discovered models and providers are currently active
- blocked until supplied or observed: target Hermes role alias (main, realtime-search, or design), semantic category, X-platform domain, or external coding owner
- blocked until supplied or observed: optional user-edited recommendation overrides
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
