# Prepared guidance: jev-action-check

Family: `typed-jev-assist`  
Category: `review`  
Phase: `jev-action-check`  
Role: `reviewer`

## Contract
[omh] Risky command screened by Jev: Jev action check before a risky command: secrets, outbound sends, blast radius; can only add a hold. Use when the user says: jev-action-check, jev action check, ask jev if this command is safe, jev risk check.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- jev-action-check
- jev action check
- ask jev if this command is safe
- jev risk check

## Required inputs
- the command or write
- the working directory
- the task the user stated

## Expected outputs
- the `action_check/v1` outcome: hold, refuse_recommended, or no_extra_hold
- the rule that fired

## Artifact expectations
- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under `<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, or question text

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `hold` with `rule: not_answered:<status>`, never Jev's answer.
- Record observed delegation results; use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Run in Hermes: build the ask, call `omh_jev_ask`, and report the numbers. Nothing is delegated; the partner workflow keeps its own verdict and Jev's answers are one more input to it.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-jev-action-check/SKILL.md`
- SHA256: `10bf10977fc5d8a10cb948262c279db7eb386b080c225615e7170451c9a1e31a`

## Method references
- `omh-jev-action-check/references/full-contract.md` (pinned `skills/omh-jev-action-check/references/full-contract.md`)
- `omh-jev-action-check/references/preset.md` (pinned `skills/omh-jev-action-check/references/preset.md`)

## Source gaps
- The source full-contract references absent references/procedure.md; preserve this gap and do not fabricate a procedure or provider.

## Blocked prerequisites
- The local catalog member jev-action-check is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
