# Prepared guidance: decision-prototype

Family: `decision-prototype`<br>
Category: `planning`<br>
Phase: `decision-prototype`<br>
Role: `planner`

## Contract
[omh] Uncertain technical choice for a spike: bounded decision prototype workflow: resolve one uncertain interaction, API, performance, or integration choice with a disposable, isolated experiment whose observed result feeds planning. Use when the user says: decision-prototype, decision prototype, prototype this uncertain choice before planning, prototype before planning, prototype the uncertain choice, run a small spike, small spike, spike solution.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- decision-prototype
- decision prototype
- prototype this uncertain choice before planning
- prototype before planning
- prototype the uncertain choice
- run a small spike
- small spike
- spike solution

## Required inputs
- decision question
- experiment budget
- scratch boundary
- measurement method

## Expected outputs
- decision_prototype/v1
- prepared prototype handoff with exact commands and expected observations
- observation ledger separating observed outputs from interpretation and confidence
- decision receipt for planning with supported option, rejected option, residual risk, and evidence limits

## Artifact expectations
- prepared decision_prototype/v1 record when a wrapper captures it: decision id and question, alternatives, hypothesis, target user or task, time/tool/file/command budget, executor or runtime and capability limits, scratch workspace identity, measurement method, stop conditions, observed results, interpretation, confidence, unresolved questions, keep or discard decision, and cleanup status
- prepared prototype handoff carrying exact commands and expected observations; it stays prepared_not_observed until a separate observation records outputs
- declared scratch workspace identity compatible with the existing worktree_session_isolation/v1 guidance when a temporary worktree is used
- metadata-only evidence references for executed runs; raw outputs, secrets, user data, and transcripts stay out of the record

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Keep the decision question, hypothesis, budget, scratch boundary, measurement method, and decision receipt in Hermes. When a selected executor or runtime (Codex, Claude Code, Hermes runtime/handoff, or a generic executor) will run the experiment, prepare an executor-neutral handoff with exact commands and expected observations; it stays `prepared_not_observed` until observed outputs exist. A prototype result is decision grounding only: promotion into production requires a separate accepted `ralplan` plan and its own implementation handoff.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-decision-prototype/SKILL.md`
- SHA256: `889ab7c588c777bace6a8fe5d0cfd238d487234b9ab5d09f438f5b6777f95b1a`

## Method references
- `decision-prototype/omh-decision-prototype/references/full-contract.md` (pinned `skills/omh-decision-prototype/references/full-contract.md`)
- `decision-prototype/omh-decision-prototype/references/procedure.md` (pinned `skills/omh-decision-prototype/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member decision-prototype is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
