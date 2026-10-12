# Prepared guidance: app-debugging

Family: `application-and-native-debug`  
Category: `verification`  
Phase: `app-root-cause`  
Role: `reviewer`

## Contract
[omh] Application code misbehaves -- a wrong value, a flaky test, a lost update: reproduce it first, form competing hypotheses, discriminate them with the cheapest observation, and only then fix the demonstrated root cause. Use when the user says: app-debugging, app debugging, application debugging, root cause, root-cause, find the root cause, root cause analysis, flaky test.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- app-debugging
- app debugging
- application debugging
- root cause
- root-cause
- find the root cause
- root cause analysis
- flaky test

## Required inputs
- the wrong behaviour as observed, and the behaviour that was expected
- the command, request, or test that shows it, and how often it shows it
- language, framework, and what changed recently when known
- logs, stack traces, or failing assertions already captured
- observed reproduction and verification evidence for any root-cause or fix claim

## Expected outputs
- reproduction_record/v1
- competing_hypotheses/v1 with at least three hypotheses on distinct axes
- discriminating_observation_plan/v1
- root_cause_record/v1
- fix_handoff/v1 blocked until reproduction_record/v1 reads observed
- observed_fix_verification/v1 when observed

## Artifact expectations
- reproduction_record/v1 names the exact command, the input, the observed output, the expected output, and the hit rate over N runs; it reads observed or not_observed and nothing between
- competing_hypotheses/v1 spans distinct axes -- input and state, ordering and timing, environment and build, dependency behaviour -- rather than three phrasings of one guess
- discriminating_observation_plan/v1 orders the observations cheapest first and names, for each, which hypotheses its result eliminates
- root_cause_record/v1 cites the observation that demonstrated the cause and the one that ruled out each rival
- fix_handoff/v1 carries the reproduction as the regression test that must fail before the fix and pass after it

## Acceptance criteria
- The reproduction names its command, observed output, expected output, and hit rate, and reads observed before any fix is prepared.
- At least three hypotheses on distinct axes were written before the first observation was chosen.
- Each observation records which hypotheses its result eliminated.
- The root cause cites the demonstrating observation and the observation that ruled out each rival.
- The fix handoff carries the reproduction as a regression test that fails before and passes after.

## Handoff policy
Keep the symptom statement, the hypothesis set, the discriminating observations, and the root-cause verdict in Hermes. Record every reproduction run, probe output, and fix verification only from executor or wrapper observed evidence.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The fault is a crash, memory corruption, or core dump in a compiled native binary that needs a debugger session; use `native-debugging`.
- Source routing exclusion: The build, compile, or CI job fails the same way on every run; use `build-failure-triage`.
- Source routing exclusion: The subject is an agent or workflow run that misbehaved rather than the application code; use `agent-debug`.
- Source routing exclusion: The cause is already demonstrated and the request is to judge whether the fix is proven; use `verification-gate`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-app-debugging/SKILL.md`
- SHA256: `e60fe09f8b5bceff2ff7bf6344a85d6a289d9bb683b1f301294f587521099a47`

## Method references
- `omh-app-debugging/references/hypothesis-and-race-method.md` (pinned `skills/omh-app-debugging/references/hypothesis-and-race-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member app-debugging is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
