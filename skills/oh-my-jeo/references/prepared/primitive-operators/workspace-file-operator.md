# Prepared guidance: workspace-file-operator

Family: `primitive-operators`  
Category: `filesystem`  
Phase: `file-task`  
Role: `guide`

## Contract
[omh] Folder cleanup, renames, or deletions: policy overlay for local file tasks - add path scoping and destructive-action gates after preferring native file tools for ordinary list, search, organize, copy, move, and rename actions. Use when the user says: workspace-file-operator, workspace file operator, file operator, file operation, file operations, filesystem task, filesystem operation, file system task.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- workspace-file-operator
- workspace file operator
- file operator
- file operation
- file operations
- filesystem task
- filesystem operation
- file system task

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- workspace_file_task_card/v1
- file_operation_scope/v1
- file_observation_manifest/v1 when observed
- file_confirmation_gate/v1 when destructive
- next action
- prepared-vs-observed boundary

## Artifact expectations
- workspace_file_task_card/v1 metadata-only wrapper card when prepared
- file_operation_scope/v1 with path root, allowed operations, excluded paths, and stop condition
- file_observation_manifest/v1 only when directory listings, file stats, hashes, diffs, or operation output are observed
- session_file_activity/v1 (`omh quality-evidence file-activity --hermes-session <id> --json`) cited in that manifest for which workspace files a Hermes session's read_file, write_file, and patch calls named and the outcome Hermes recorded; never as file-content, hash, diff, test, review, CI, or merge evidence
- file_confirmation_gate/v1 for delete, overwrite, move, rename, chmod, archive mutation, or irreversible cleanup

## Acceptance criteria
- The path root, allowed file operations, excluded paths, destructive-operation policy, and stop condition are explicit.
- Delete, overwrite, move, rename, permission change, archive mutation, upload, and download are gated or marked missing.
- Directory listings, file contents, hashes, diffs, and operation results are reported only from observed file evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Route only on the source-defined description and triggers; do not treat nearest local contracts toolbelt-readiness, deliverable-package as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-files/SKILL.md`
- SHA256: `b0051a22d4b8ec86afc5594642c747fe099c316c702745e414ec75dac8d5c3a8`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member workspace-file-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
