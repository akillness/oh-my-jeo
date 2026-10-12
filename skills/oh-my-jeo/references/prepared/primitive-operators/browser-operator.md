# Prepared guidance: browser-operator

Family: `primitive-operators`  
Category: `browser`  
Phase: `browser-task`  
Role: `guide`

## Contract
[omh] Browser login, click, or form task: policy overlay for browser tasks - add auth, confirmation, and observed-trace gates after preferring the native browser for ordinary URL, click, login, and form actions. Use when the user says: browser-operator, browser operator, browser task, browser operation, browser automation, browser session, webpage operation, web page operation.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- browser-operator
- browser operator
- browser task
- browser operation
- browser automation
- browser session
- webpage operation
- web page operation

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- browser_task_card/v1
- browser_interaction_scope/v1
- browser_auth_boundary/v1
- browser_observation_manifest/v1 when observed
- browser_confirmation_gate/v1 when destructive
- browser_adapter_capabilities/v1 when acquired
- browser_session_lease/v1 when acquired
- browser_page_state/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- browser_task_card/v1 metadata only
- browser_interaction_scope/v1: URL, allowed/prohibited actions, stop condition
- browser_auth_boundary/v1: supplied/missing/prohibited credentials
- browser_observation_manifest/v1: observed screenshots/DOM notes/console/network/click traces only
- Leases: docs/BROWSER-ADAPTER.md; owner/adapter/version/task scope, cached capabilities, digest-only state, exact revision handles.
- browser_skill_promotion/v1: `omh web-qa promotion diff`, `approve` its exact digest, then `promote` one receipt; SKILL.md alone commits visibility

## Acceptance criteria
- Specify URL, allowed/prohibited actions, auth boundary, stop condition.
- Gate credentials/login/payment/purchase/destruction/scraping/export; observed traces only.
- Host request admission (not enablement/adapter presence) gates schemas/context/callbacks/writes. Refuse foreign/stale/expired/released/ambiguous targets; no index fallback.
- omh_browser blocks native browser_*; inert by default. Opted-in effects need exact approval: docs/BROWSER-EFFECTS.md.

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
- Source path: `skills/omh-browser/SKILL.md`
- SHA256: `8529cab9578cb9309b6a3d2146ac727ff42bcf8039ddd400a1896e7d6f31d8e2`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member browser-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
