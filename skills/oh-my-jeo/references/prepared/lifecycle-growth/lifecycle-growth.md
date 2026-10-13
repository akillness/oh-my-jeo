# Prepared guidance: lifecycle-growth

Family: `lifecycle-growth`<br>
Category: `strategy`<br>
Phase: `lifecycle-growth`<br>
Role: `operator`

## Contract
[omh] Churn or weak activation among users: turn an observed onboarding, activation, retention, re-engagement, referral, or monetization problem into one consent-safe in-app journey or growth experiment plan with a bounded readout and an explicit decision. Use when the user says: lifecycle-growth, lifecycle growth, lifecycle marketing, lifecycle messaging, in-app journey, in-app message campaign, onboarding journey, onboarding nudge.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- lifecycle-growth
- lifecycle growth
- lifecycle marketing
- lifecycle messaging
- in-app journey
- in-app message campaign
- onboarding journey
- onboarding nudge

## Required inputs
- lifecycle objective and stage
- target segment
- event schema and baseline
- channels or product surfaces
- consent and policy constraints
- experiment budget
- decision owner

## Expected outputs
- lifecycle_growth_brief/v1
- audience_trigger_policy/v1
- lifecycle_safety_policy/v1
- growth_experiment_plan/v1
- growth_measurement_readout/v1
- growth_handoff_disposition/v1

## Artifact expectations
- prepared lifecycle-growth plan and readout, as metadata-only records with safe references, when a wrapper captures them

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Keep lifecycle framing, audience and safety policy, experiment design, and readout interpretation in Hermes. A prepared journey or experiment plan is not a send, a flag change, a delivered message, a displayed treatment, a user action, a business outcome, or a causal result. Hand external sends and flag mutations to `connector-operator`, copy to `content-operator`, supplied-data calculation to `data-analysis`, recurring scheduling to `automation-blueprint`, and validated product changes to `product-brief`, each only after the human approval gate and only reported from observed evidence.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: decision-gated
- source owner: skills/omh-lifecycle-growth/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-lifecycle-growth/SKILL.md`
- SHA256: `a7a43439df50a0fd5e9cbdf9bfbaa50655aa547af968f4490b1598242f5308d9`

## Method references
- `lifecycle-growth/omh-lifecycle-growth/references/full-contract.md` (pinned `skills/omh-lifecycle-growth/references/full-contract.md`)
- `lifecycle-growth/omh-lifecycle-growth/references/procedure.md` (pinned `skills/omh-lifecycle-growth/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: lifecycle objective and stage
- blocked until supplied or observed: target segment
- blocked until supplied or observed: event schema and baseline
- blocked until supplied or observed: channels or product surfaces
- blocked until supplied or observed: consent and policy constraints
- blocked until supplied or observed: experiment budget
- blocked until supplied or observed: decision owner
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
