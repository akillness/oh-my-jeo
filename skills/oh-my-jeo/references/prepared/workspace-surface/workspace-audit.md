# Prepared guidance: workspace-audit

Family: `workspace-surface`  
Category: `operations`  
Phase: `workspace-audit`  
Role: `operator`

## Contract
[omh] Workspace setup inventory and gaps: map repository, skill, prompt, plugin, MCP, hook, config, and runtime surfaces before strengthening or operating OMH. Use when the user says: workspace-audit, workspace audit, repo surface audit, repository surface audit, workspace surface audit, repo inventory, surface inventory, skill inventory.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- workspace-audit
- workspace audit
- repo surface audit
- repository surface audit
- workspace surface audit
- repo inventory
- surface inventory
- skill inventory

## Required inputs
- workspace or repo root
- audit scope: repo, skills, prompts, plugins, MCP/tools, hooks, config, docs, runtime artifacts
- known constraints such as no secrets, no network, or read-only mode
- desired downstream decision or strengthening goal

## Expected outputs
- workspace_audit_plan/v1
- surface_inventory/v1
- capability_gap_matrix/v1
- config_security_findings/v1
- downstream_workflow_recommendation/v1
- not-evidence boundary

## Artifact expectations
- workspace_audit_plan/v1 with target root, scopes, exclusions, and read-only boundary
- surface_inventory/v1 with repo, skill, prompt, plugin, MCP/tool, hook, config, docs, and runtime surfaces when observed
- capability_gap_matrix/v1 with missing, duplicate, stale, risky, and high-leverage strengthening candidates
- redacted config_security_findings/v1 when secrets, permissions, or external integrations are mentioned

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Handoff policy
Keep the audit as Hermes-retained local evidence gathering. Prepare executor handoff only for later code changes, and record file reads, tool availability, config checks, and runtime observations only when observed.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: workspace-audit-gated
- source owner: skills/omh-workspace-audit/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-workspace-audit/SKILL.md`
- SHA256: `882803b50cb3a38a1bbb336cc1b025ff6ba085c994fe5dce22e2688e48852abd`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: workspace or repo root
- blocked until supplied or observed: audit scope: repo, skills, prompts, plugins, MCP/tools, hooks, config, docs, runtime artifacts
- blocked until supplied or observed: known constraints such as no secrets, no network, or read-only mode
- blocked until supplied or observed: desired downstream decision or strengthening goal
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
