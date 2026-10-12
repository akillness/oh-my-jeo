# Prepared guidance: release-cut

Family: `version-release`<br>
Category: `planning`<br>
Phase: `release-cut`<br>
Role: `planner`

## Contract
[omh] Shipping a versioned release -- tag it, stage it behind a canary, or roll back the last deploy: decide what goes in, the version, the rollout stages, and a rollback with its trigger and exact command before it is needed. Use when the user says: release-cut, release cut, cut a release, cut the release, cut a new release, tag a release, tag the release, release candidate.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- release-cut
- release cut
- cut a release
- cut the release
- cut a new release
- tag a release
- tag the release
- release candidate

## Required inputs
- the changes since the last release, and the current version and versioning scheme
- how a release is cut here: the workflow or command, the approval gates, and every version surface it bumps
- the deploy target, the traffic split available, and the health signals with their normal range
- the rollback mechanism: redeploy of the previous artifact, a flag, or a revert, and who may run it
- observed evidence for any published, promoted, or rolled-back claim

## Expected outputs
- release_scope/v1
- release_plan/v1
- rollout_stages/v1 when the release is staged
- rollback_trigger/v1
- release_readiness_verdict/v1

## Artifact expectations
- release_scope/v1 lists what goes in and what is held back, and derives the version from the change classes: a breaking change, a feature, or a fix
- release_plan/v1 orders the cut: freeze the release branch, bump every version surface, tag, run the release workflow, pass its approval gate, publish, and curate the notes
- rollout_stages/v1 gives each stage its traffic share, its bake time, and the promotion criterion read from a named health signal
- rollback_trigger/v1 names the signal and threshold that trigger the rollback, the exact command that performs it, and who runs it
- release_readiness_verdict/v1 reads ready only when a named rollback trigger and its exact command are stated; otherwise it names what is missing

## Acceptance criteria
- The contents, the held items, and the version are stated.
- Every rollout stage has a traffic share, a bake time, and a promotion criterion.
- The rollback trigger names a signal, a threshold, and the exact command.
- The readiness verdict is ready only when the trigger and the command are named.
- Nothing was tagged, published, deployed, or rolled back by OMH.

## Handoff policy
Keep the release contents, the version decision, the rollout stages, the rollback trigger and command, and the readiness verdict in Hermes. Tags, workflow runs, approvals, published artifacts, canary metrics, and every rollback are recorded only from executor, operator, CI, or wrapper observed output; OMH prepares and never publishes, tags, or deploys.

## Catalog rules
- Source first step: State what goes in, what is held back, and the version before proposing the cut.
- Source first step: Name the rollback trigger and its exact command before the first stage ships.
- Source routing exclusion: The rollout is already running and the ask is watching its health signals and post-deploy status; use `deploy-and-monitor`.
- Source routing exclusion: Production is down or degraded and the work is commanding the incident; use `live-incident-response`.
- Source routing exclusion: The ask is a readiness audit across observability, security, and operations before launch; use `production-audit`.
- Source routing exclusion: The ask is drafting the commit message or the pull request description for a change; use `commit-pr-authoring`.
- Source routing exclusion: The app ships through the App Store or Google Play -- signing, a TestFlight or Play testing-track beta, a phased release, a store hotfix; use `mobile-release`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts deploy-and-monitor as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-release-cut/SKILL.md`
- SHA256: `eae75507d98e6f4dfdbcfce89d05a674e64b31112dd3178ead2bc1c33a8146a6`

## Method references
- `release-cut/omh-release-cut/references/release-and-rollback-method.md` (pinned `skills/omh-release-cut/references/release-and-rollback-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member release-cut is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the release contents, the version decision, the rollout stages, the rollback trigger and command, and the readiness verdict in Hermes. Tags, workflow runs, approvals, published artifacts, canary metrics, and every rollback are recorded only from executor, operator, CI, or wrapper observed output; OMH prepares and never publishes, tags, or deploys. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
