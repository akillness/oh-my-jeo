# Prepared guidance: commit-pr-authoring

Family: `commit-and-git`<br>
Category: `verification`<br>
Phase: `commit-pr-authoring`<br>
Role: `reviewer`

## Contract
[omh] Commit message or pull-request body to write for a change: draft it in the repository's own convention, with `Tested:` listing only commands observed to run and everything prepared but not run under `Not-tested:`. Use when the user says: commit-pr-authoring, commit message, commit messages, write the commit message, draft the commit message, commit body, squash message, pr body.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- commit-pr-authoring
- commit message
- commit messages
- write the commit message
- draft the commit message
- commit body
- squash message
- pr body

## Required inputs
- the change: the diff, the staged files, or the branch compared with its base
- the repository's PR template and a sample of its recent commit log
- the commands that ran for this change, each with its observed exit status
- the commands that were prepared, planned, or skipped, and why
- the issue or goal the change closes, when there is one

## Expected outputs
- repo_convention_read/v1
- evidence_ledger/v1
- commit_message_draft/v1
- pr_body_draft/v1 when a PR is being opened

## Artifact expectations
- repo_convention_read/v1 names the template path, the subject shape and trailers seen in the recent log, and the sign-off rule, or says which of them was not found
- evidence_ledger/v1 lists every command with observed or not_observed; observed carries the exit status and where it was seen
- commit_message_draft/v1 and pr_body_draft/v1 take `Tested:` and the validation section only from observed ledger rows

## Acceptance criteria
- The convention read names the template and log sample it drew from.
- Every `Tested:` entry maps to an observed ledger row with its exit status.
- Every prepared, skipped, or unobserved command is under `Not-tested:` with its reason.
- Nothing was committed, pushed, or opened by OMH.

## Handoff policy
Keep the convention read, the drafted text, and the evidence ledger in Hermes. The commit, the push, and opening the PR are executor or user actions; OMH never performs them, and a command reaches `Tested:` only from an observed run record.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: evidence-ledger-gated
- source owner: skills/omh-commit-pr-authoring/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-commit-pr-authoring/SKILL.md`
- SHA256: `0ceaee44829a03cdcf6d0333ee0d828f1c6d078c025f81ef56e35b3076031ea4`

## Method references
- `commit-pr-authoring/omh-commit-pr-authoring/references/commit-and-pr-conventions.md` (pinned `skills/omh-commit-pr-authoring/references/commit-and-pr-conventions.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the change: the diff, the staged files, or the branch compared with its base
- blocked until supplied or observed: the repository's PR template and a sample of its recent commit log
- blocked until supplied or observed: the commands that ran for this change, each with its observed exit status
- blocked until supplied or observed: the commands that were prepared, planned, or skipped, and why
- blocked until supplied or observed: the issue or goal the change closes, when there is one
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
