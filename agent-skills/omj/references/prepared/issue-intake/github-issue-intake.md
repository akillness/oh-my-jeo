# Prepared guidance: github-issue-intake

Family: `issue-intake`<br>
Category: `github-ops`<br>
Phase: `issue-intake`<br>
Role: `operator`

## Contract
[omh] Chat report that should become a GitHub issue: turn a public chat report into a confirmed, verified issue package. Use when the user says: github-issue-intake, github issue intake, issue intake, file this as an issue, file a github issue, open a github issue, create a github issue, submit a github issue.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- github-issue-intake
- github issue intake
- issue intake
- file this as an issue
- file a github issue
- open a github issue
- create a github issue
- submit a github issue

## Required inputs
- public report or summary
- source boundary
- explicit target repository
- desired outcome
- scope boundary
- missing evidence

## Expected outputs
- github_issue_intake/v1
- direction check
- duplicate status
- issue package or connector handoff
- read-back verification or explicit blocker

## Artifact expectations
- github_issue_intake/v1 metadata-only wrapper card when recorded

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Handoff policy
Keep intake, direction check, and confirmation in Hermes; hand the confirmed package to an authorized Hermes-native/wrapper connector for the single scoped create_issue write, and hand implementation to a coding workflow only after separate maintainer authorization.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The report only wants classification or signal clustering; use feedback-triage instead.
- Source routing exclusion: The event concerns an already-existing issue, PR, review, or CI run; use github-event-ops instead.
- Source routing exclusion: The user wants implementation; coding stays a separate follow-up lane with its own maintainer authority.
- Source routing exclusion: The report describes a security vulnerability; redirect to the private SECURITY.md path.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-github-issue-intake/SKILL.md`
- SHA256: `61f28c00357350c3724ff479daba4bdce500abaf35f0fc15fc6ec91e15152069`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member github-issue-intake is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
