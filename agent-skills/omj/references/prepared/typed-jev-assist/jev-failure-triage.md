# Prepared guidance: jev-failure-triage

Family: `typed-jev-assist`<br>
Category: `review`<br>
Phase: `jev-failure-triage`<br>
Role: `reviewer`

## Contract
[omh] Failing run handed to Jev for a next move: Jev failure triage: retry, fix a dependency, ask for access, or change approach on a failing run. Use when the user says: jev-failure-triage, jev failure triage, ask jev if this failure is transient.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- jev-failure-triage
- jev failure triage
- ask jev if this failure is transient

## Required inputs
- the failing command
- an excerpt of its error output
- how many times it was already retried

## Expected outputs
- the `failure_triage/v1` policy result
- the next move with the rule that fired

## Artifact expectations
- one metadata-only `omh_jev_ask_record/v1` ledger row per ask under `<omh_home>/jev/asks.jsonl`: hashes, counts, status, usage, cost; never the key, `state`, or question text

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Report the tool's status, ask_id, served model, and cost source; a non-answer is `not_observed` with `rule: not_answered:<status>`, never Jev's answer.
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
- Source path: `skills/omh-jev-failure-triage/SKILL.md`
- SHA256: `0ba2151732035f078ca20f5ce3caabf26fc963d9fa878fbe48b74c287bae2954`

## Method references
- `jev-failure-triage/omh-jev-failure-triage/references/full-contract.md` (pinned `skills/omh-jev-failure-triage/references/full-contract.md`)
- `jev-failure-triage/omh-jev-failure-triage/references/preset.md` (pinned `skills/omh-jev-failure-triage/references/preset.md`)

## Source gaps
- The source full-contract references absent references/procedure.md; preserve this gap and do not fabricate a procedure or provider.

## Blocked prerequisites
- The local catalog member jev-failure-triage is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
