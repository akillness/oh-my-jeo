# Prepared guidance: command-operator

Family: `primitive-operators`<br>
Category: `command`<br>
Phase: `command-task`<br>
Role: `guide`

## Contract
[omh] Shell command or test-suite execution: policy overlay for terminal commands - add cwd, environment, safety, and result-evidence gates after preferring native shell tools for ordinary CLI, package-manager, and test runs. Use when the user says: command-operator, command operator, terminal command, terminal task, shell command, shell task, cli command, command execution.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- command-operator
- command operator
- terminal command
- terminal task
- shell command
- shell task
- cli command
- command execution

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- command_task_card/v1
- command_scope/v1
- command_safety_gate/v1
- command_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- command_task_card/v1 metadata-only wrapper card when prepared
- command_scope/v1 with command text, working directory, environment assumptions, timeout, and stop condition
- command_safety_gate/v1 separating read-only, write/mutation, network, credential, and destructive-risk commands
- command_result_manifest/v1 only when exit code, stdout/stderr, logs, or terminal transcript are observed

## Acceptance criteria
- Command text, working directory, environment assumptions, timeout, safety level, and stop condition are explicit.
- Destructive, credential, network, filesystem mutation, install, deploy, and production commands are gated or marked missing.
- Exit codes, stdout/stderr, test results, package-manager effects, and filesystem mutations are reported only from observed command evidence.

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
- Source path: `skills/omh-terminal/SKILL.md`
- SHA256: `242f733a773d99f885623728fde1fca4594fe2d039fe4f070d18a0a6d10ff58c`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member command-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
