# Prepared guidance: agent-evaluation

Family: `agent-failure-and-eval`<br>
Category: `operations`<br>
Phase: `agent-evaluation`<br>
Role: `operator`

## Contract
[omh] Choosing between coding agents on evidence: compare executor or agent choices on reproducible tasks using quality, cost, time, tool, and evidence metrics. Use when the user says: agent-evaluation, agent evaluation, agent eval, agent benchmark, executor evaluation, executor benchmark, compare agents, compare codex claude.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- agent-evaluation
- agent evaluation
- agent eval
- agent benchmark
- executor evaluation
- executor benchmark
- compare agents
- compare codex claude

## Required inputs
- candidate executors or agents
- task set and fixtures
- success criteria and scoring rubric
- allowed tools, budget, timebox, and isolation policy
- observed run artifacts when comparing completed attempts

## Expected outputs
- paired_run_decision/v1
- not-evidence boundary

## Artifact expectations
- paired_run_decision/v1 with per-task input digests, explicit criteria, baseline and variant exposure, attempted-run and per-dispatch time budgets, signed observed_at receipt provenance, and a scoped Pareto outcome

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Handoff policy
Keep evaluation design and scoring in Hermes. Actual executor runs, costs, timings, tool calls, code edits, and review results must come from observed runtime or supplied artifacts.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: agent-eval-gated
- source owner: skills/omh-agent-evaluation/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-agent-evaluation/SKILL.md`
- SHA256: `36d9cde2944e8f413458f84b99d68f66d37a563833e35514c08676547f5994ea`

## Method references
- `agent-evaluation/omh-agent-evaluation/references/self-evaluation-loops.md` (pinned `skills/omh-agent-evaluation/references/self-evaluation-loops.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: candidate executors or agents
- blocked until supplied or observed: task set and fixtures
- blocked until supplied or observed: success criteria and scoring rubric
- blocked until supplied or observed: allowed tools, budget, timebox, and isolation policy
- blocked until supplied or observed: observed run artifacts when comparing completed attempts
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
