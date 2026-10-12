# Prepared guidance: connector-operator

Family: `primitive-operators`  
Category: `connector`  
Phase: `connector-task`  
Role: `guide`

## Contract
[omh] Email, Slack, or Jira action to perform: external app actions - email, Slack, Discord, Notion, Linear, Jira, CRM, and similar providers, scoped with auth, payload, confirmation, and result-evidence gates. Use when the user says: connector-operator, connector operator, external app action, external connector action, saas action, api action, send email, email customer.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- connector-operator
- connector operator
- external app action
- external connector action
- saas action
- api action
- send email
- email customer

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- connector_task_card/v1
- connector_scope/v1
- connector_auth_boundary/v1
- connector_confirmation_gate/v1 when mutating or sending
- connector_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- connector_task_card/v1 metadata-only wrapper card when prepared
- connector_scope/v1 with provider, target object, allowed action, payload summary, and stop condition
- connector_auth_boundary/v1 separating missing connector, missing credentials, user-supplied authority, and credential-use prohibition
- connector_confirmation_gate/v1 for sending, ticket mutation, external write, webhook delivery, CRM/database update, or irreversible provider action
- connector_result_manifest/v1 only when provider response, message id, ticket id, API transcript, or delivery receipt is observed

## Acceptance criteria
- Provider, target object, allowed action, payload summary, authority, confirmation policy, and stop condition are explicit.
- Credentials, missing connector setup, external writes, sends, ticket mutations, calendar invites, CRM updates, and webhook delivery are gated or marked missing.
- Message ids, ticket ids, provider responses, delivery receipts, and API effects are reported only from observed connector evidence.

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
- Source path: `skills/omh-apps/SKILL.md`
- SHA256: `fd17d1e8702a7630cd3e2b4e121b4de4911a5dd16ae0f1254cb83c1332bbcd26`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member connector-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
