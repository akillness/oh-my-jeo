# Prepared guidance: build-failure-triage

Family: `application-and-native-debug`<br>
Category: `verification`<br>
Phase: `build-failure-triage`<br>
Role: `reviewer`

## Contract
[omh] Build or CI failure to triage: classify build, typecheck, lint, test, CI, and DCO failures into minimal safe fix handoffs. Use when the user says: build-failure-triage, build failure triage, build failure, build-failure, build fix, build failed, build failing, compile error.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- build-failure-triage
- build failure triage
- build failure
- build-failure
- build fix
- build failed
- build failing
- compile error

## Required inputs
- failing command, CI job, PR check, or tool name
- fresh failure log, exit status, or observed check URL
- repo root, branch, PR, or changed files under investigation
- allowed remediation boundary: diagnose only, local fix handoff, or executor-owned patch
- dependency-install and network permission boundaries
- last known passing state when available

## Expected outputs
- build_failure_triage_plan/v1
- failure_log_digest/v1
- failure_cluster_matrix/v1
- root_cause_hypothesis_set/v1
- minimal_fix_handoff/v1 when remediation is requested
- rerun_plan/v1
- build_failure_triage_verdict/v1

## Artifact expectations
- build_failure_triage_plan/v1 with failing surface, freshness, affected files, allowed actions, and stop condition
- failure_log_digest/v1 preserves exact command/job, exit status, top frames, file paths, and omitted-log boundary
- failure_cluster_matrix/v1 groups syntax, type, lint, test assertion, flaky, dependency, config, DCO, and environment failures separately
- root_cause_hypothesis_set/v1 ranks likely causes with confidence and evidence instead of guessing from one line
- minimal_fix_handoff/v1 names the selected executor, affected files, smallest patch direction, and rejected broad refactors
- rerun_plan/v1 orders targeted rerun, broader local check, CI rerun, and stale-check blocker
- build_failure_triage_verdict/v1 returns FIX_READY, NEEDS_MORE_LOGS, BLOCKED_BY_ENVIRONMENT, or ROUTE_TO_VERIFICATION_GATE Artifact contracts: This label denotes the machine-enforcement level, not a skill quality score and not an observed evidence state.
- contract_id: `build_failure_triage_plan/v1`; enforcement_level: `guidance_only`; consumer_id: `none`

## Acceptance criteria
- The failing command/job, freshness, exit status, and log/source boundary are explicit.
- Failure clusters separate syntax/type/lint/test/dependency/config/environment/DCO causes.
- The proposed remediation is minimal, scoped to affected files, and separated from implementation evidence.
- The rerun ladder names targeted, broad local, CI, and DCO checks without claiming they already passed.
- The final verdict is FIX_READY, NEEDS_MORE_LOGS, BLOCKED_BY_ENVIRONMENT, or ROUTE_TO_VERIFICATION_GATE.

## Handoff policy
Keep failure collection, grouping, root-cause hypothesis, retry policy, and minimal-fix handoff in Hermes. Command reruns, code edits, dependency installs, CI reruns, and merge readiness require observed executor, wrapper, or user evidence.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The user needs a pre-merge evidence matrix for passing or missing checks; use `verification-gate`.
- Source routing exclusion: The user needs a code review of changed behavior rather than failing command triage; use `code-review`.
- Source routing exclusion: The user needs broad production readiness; use `production-audit`.
- Source routing exclusion: The user asks for incident or SLO review after deployment; use `reliability-review`.
- Source routing exclusion: A test passes on some runs and not others, or the code returns a wrong value whose cause is unknown; use `app-debugging`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-build-failure-triage/SKILL.md`
- SHA256: `cac62e7a8ab4720a8229b9c2aebd52e4cb2963e1763aec7fb3f5257cf592725b`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member build-failure-triage is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
