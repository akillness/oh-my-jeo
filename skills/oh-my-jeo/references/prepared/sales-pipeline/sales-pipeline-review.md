# Prepared guidance: sales-pipeline-review

Family: `sales-pipeline`<br>
Category: `operations`<br>
Phase: `sales-pipeline-review`<br>
Role: `operator`

## Contract
[omh] CRM pipeline or sales forecast to review: turn a supplied CRM export or pipeline snapshot into an evidence-bound pipeline health, forecast, and follow-up review. Aliases: pipeline-review, forecast-review, deal-review. Use when the user says: sales-pipeline-review, sales pipeline review, pipeline review, pipeline health, pipeline coverage, deal review, deal health, sales forecast review.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- sales-pipeline-review
- sales pipeline review
- pipeline review
- pipeline health
- pipeline coverage
- deal review
- deal health
- sales forecast review

## Required inputs
- pipeline snapshot
- as-of time and review horizon
- currency, amount, stage, and forecast definitions
- prior forecast and actuals
- decision owner

## Expected outputs
- sales_pipeline_scope/v1
- sales_pipeline_health/v1
- sales_forecast_assessment/v1
- sales_outcome_learning_annex/v1
- sales_renewal_risk_annex/v1
- sales_pipeline_handoff/v1

## Artifact expectations
- prepared sales pipeline review brief when a wrapper captures it
- durable artifacts hold bounded aggregates, opaque source references, and only the account identifiers an approved handoff needs; raw export rows and message content are not persisted by default

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes reviews supplied records; it does not replace a CRM, store or sync CRM data, mutate opportunities, create dashboards or alerts, send outreach, book revenue, or claim seller or buyer commitments that were not observed.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-sales-pipeline-review/SKILL.md`
- SHA256: `772914984077a1ec970a012400622515dd303488a5a4c280a53b18f59c33afff`

## Method references
- `sales-pipeline-review/omh-sales-pipeline-review/references/full-contract.md` (pinned `skills/omh-sales-pipeline-review/references/full-contract.md`)
- `sales-pipeline-review/omh-sales-pipeline-review/references/procedure.md` (pinned `skills/omh-sales-pipeline-review/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member sales-pipeline-review is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
