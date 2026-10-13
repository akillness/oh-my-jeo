# Prepared guidance: git-workflow

Family: `commit-and-git`<br>
Category: `verification`<br>
Phase: `git-repair`<br>
Role: `reviewer`

## Contract
[omh] Git branch in trouble -- a merge conflict, a commit that broke something, history to repair: plan the resolution, the bisect, or the rewrite, name what is already pushed first, and force-push only with `--force-with-lease`. Use when the user says: git-workflow, git workflow, merge conflict, merge conflicts, rebase conflict, resolve the conflict, resolve this conflict, conflict markers.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- git-workflow
- git workflow
- merge conflict
- merge conflicts
- rebase conflict
- resolve the conflict
- resolve this conflict
- conflict markers

## Required inputs
- the branch or branches involved and their upstreams
- what is already pushed, and who else may have fetched it
- the conflict, the regression, or the history problem as observed
- for a bisect: a known good commit, a known bad commit, and the command that tells them apart
- the repository's merge policy: merge commits, squash, or rebase

## Expected outputs
- pushed_state_inventory/v1
- git_repair_plan/v1
- conflict_resolution_plan/v1 when files conflict
- bisect_plan/v1 when a regression is hunted
- history_rewrite_plan/v1 when commits are rewritten
- observed_git_result/v1 when observed

## Artifact expectations
- pushed_state_inventory/v1 lists each branch with its local head, its remote head, whether they match, and whether anyone else may have the remote commits
- git_repair_plan/v1 orders the steps, marks each one that rewrites history, and names the recovery point (a backup ref or reflog entry) before it
- conflict_resolution_plan/v1 decides each conflicted hunk by what both sides intended, and re-derives generated or counted files from their producer instead of picking a side
- bisect_plan/v1 names the good and bad commits and the exact test command, so each step is a run rather than a judgement
- history_rewrite_plan/v1 uses `--force-with-lease` for every force-push and says which collaborators must re-fetch

## Acceptance criteria
- The pushed-state inventory names every branch the plan touches.
- Every rewriting step has a recovery point in front of it.
- Every force-push in the plan uses `--force-with-lease`.
- Generated and counted files in a conflict are re-derived, not picked.
- Resolution, bisect verdict, and push are reported only from observed output.

## Handoff policy
Keep the pushed-state inventory, the step plan, and the recovery points in Hermes. Every git command is run by the user or the executor; a resolution, a bisect verdict, or a rewrite is recorded only from their observed output.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: history-safety-gated
- source owner: skills/omh-git-workflow/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-git-workflow/SKILL.md`
- SHA256: `0cebabc56c4a5c3442f7a7098869b766f4ed7685fdf37bcf97c2d877c1e2759b`

## Method references
- `git-workflow/omh-git-workflow/references/git-repair-method.md` (pinned `skills/omh-git-workflow/references/git-repair-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the branch or branches involved and their upstreams
- blocked until supplied or observed: what is already pushed, and who else may have fetched it
- blocked until supplied or observed: the conflict, the regression, or the history problem as observed
- blocked until supplied or observed: for a bisect: a known good commit, a known bad commit, and the command that tells them apart
- blocked until supplied or observed: the repository's merge policy: merge commits, squash, or rebase
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
