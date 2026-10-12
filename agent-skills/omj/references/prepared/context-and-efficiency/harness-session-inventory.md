# Prepared guidance: harness-session-inventory

Family: `context-and-efficiency`<br>
Category: `observability`<br>
Phase: `harness-session-inventory`<br>
Role: `tracker`

## Contract
[omh] Lost track of agent sessions and worktrees: normalize Codex, Claude Code, Hermes, OpenCode, Cursor, MCP host, worktree, and wrapper session metadata into one drift-aware inventory. Use when the user says: harness-session-inventory, harness session inventory, session inventory, session adapter, session adapters, harness sessions, mcp inventory, mcp config inventory.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- harness-session-inventory
- harness session inventory
- session inventory
- session adapter
- session adapters
- harness sessions
- mcp inventory
- mcp config inventory

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- harness_session_inventory/v1 card or guidance
- harness_session_adapter_matrix/v1
- mcp_inventory_drift_report/v1
- mcp_tool_name_compatibility/v1
- worktree_lifecycle_snapshot/v1
- session_progress_slots/v1
- next action
- prepared-vs-observed boundary

## Artifact expectations
- harness_session_inventory/v1 metadata-only runtime or wrapper card when recorded
- harness_session_adapter_matrix/v1 with observed, prepared, missing, and stale adapters
- mcp_inventory_drift_report/v1 with secret-redacted config/source drift only
- mcp_tool_name_compatibility/v1 with secret-redacted config/source drift only: agents use `omh harness mcp-tool-name-compatibility --snapshot <path>` for supplied naming metadata; config-only and unsupported adapters stay unobserved, ambiguous names are never selected, and no tools are invoked
- worktree_lifecycle_snapshot/v1 with merge-conflict and cleanup candidates when observed

## Acceptance criteria
- The inventory scope names the harnesses, sessions, MCP hosts, connector configs, and worktrees being compared.
- Prepared, observed, missing, stale, and drifted entries are separated before any health or progress claim.
- The next action says whether to load a host, verify a connector, inspect a worktree, dispatch an executor, or stay blocked.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-harness-session-inventory/SKILL.md`
- SHA256: `7ebb04c6161e714a2f7926fa8c453bcdd8eb4ebe964136c591793b39f58ea04f`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member harness-session-inventory is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
