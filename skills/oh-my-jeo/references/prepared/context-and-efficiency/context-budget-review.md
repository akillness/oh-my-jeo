# Prepared guidance: context-budget-review

Family: `context-and-efficiency`<br>
Category: `observability`<br>
Phase: `context-budget-review`<br>
Role: `tracker`

## Contract
[omh] Context window or token budget at risk: plan compact context, token/cost budgets, summarization checkpoints, and overflow recovery before long agent work. Use when the user says: context-budget-review, context budget review, context budget, token budget review, token budget, prompt budget, prompt caching, prompt cache.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- context-budget-review
- context budget review
- context budget
- token budget review
- token budget
- prompt budget
- prompt caching
- prompt cache

## Required inputs
- task or workflow scope
- expected duration, artifacts, and handoff surfaces
- available context sources and must-keep facts
- token, cost, latency, or message-size constraints when known

## Expected outputs
- context_budget_plan/v1
- must_keep_context_pack/v1
- must_keep_item_class_delta/v1 when a pack replaces an earlier one
- summarization_checkpoint_plan/v1
- budget_risk_register/v1
- overflow_recovery_route/v1
- not-evidence boundary

## Artifact expectations
- context_budget_plan/v1 with scope, max visible context, source priority, discard rules, and checkpoint cadence
- must_keep_context_pack/v1 with durable facts, file refs, decisions, PR/CI state, and blocked assumptions
- must_keep_item_class_delta/v1 naming the item class that lost entries rather than reporting a digest difference, over the closed vocabulary prohibitions, decisions, open_questions, requirements, paths, pr_state, verification_gaps
- summarization_checkpoint_plan/v1 with when to compact, what to preserve, and how to verify continuity
- budget_risk_register/v1 separating estimated cost/token/latency risk from provider-observed truth

## Acceptance criteria
- The run or workflow scope, metric window, failure modes, and cost/latency boundary are named.
- Local telemetry, provider truth, billing truth, and completion evidence are separate states.
- Warnings name the next measurement or operator review action.

## Handoff policy
Keep budget design and status narration in Hermes. Provider billing, exact token usage, runtime compaction, and executor cost evidence require observed wrapper, runtime, or provider data.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The user asks for live token/cost telemetry; use `ops-observability-card`.
- Source routing exclusion: The user asks to continue a loopable goal; use `loop` unless budget planning is the explicit blocker.
- Source routing exclusion: The task is a short one-step answer with no meaningful context risk.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-context-budget-review/SKILL.md`
- SHA256: `12360627394861d52f22a27438a25dd81be94ed4b8e1d1aabc21c23c3e347126`

## Method references
- `context-budget-review/omh-context-budget-review/references/cache-placement.md` (pinned `skills/omh-context-budget-review/references/cache-placement.md`)
- `context-budget-review/omh-context-budget-review/references/route-capacity.md` (pinned `skills/omh-context-budget-review/references/route-capacity.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member context-budget-review is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
