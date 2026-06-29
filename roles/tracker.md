# Tracker

This OMJ role is a responsibility descriptor, not a runtime agent.

Own runtime status, target topology, executor session, measurement, tool readiness, and observability narration.

## OMJ Role Context

Use this role as OMJ workflow-layer responsibility context: route the user's request to the nearest skill, name adjacent OMJ workflows when the work crosses lanes, and keep status/evidence boundaries visible.

Normal users talk to Hermes; role names help Hermes explain ownership and next action without making the user learn backend OMJ commands.

Role selection is prepared guidance only. It is not worker dispatch, tool execution, file generation, delivery, review, CI, merge-readiness, or merge evidence.

## Legacy Aliases

- `hybrid-measurement`

## Owns

- Observed runtime, target, executor, and status-card state
- Tool, MCP, credential, token, cost, latency, and run-history readiness gaps
- Progress narration without upgrading missing evidence

## Primary Skills

- `performance-goal`
- `agent-board`
- `executor-runtime-readiness`
- `toolbelt-readiness`
- `ops-observability-card`
- `doctor`
- `skill`
- `cancel`

## Primary Harnesses

- `measurement`
- `status`
- `tool-readiness`
- `operator-health`

## Wrapper Actions

- `show_status`
- `refresh_status`
- `choose_executor`

## Evidence Boundary

A tracker role can report status and missing evidence; it is not proof that an executor, worker, tool, MCP server, CI job, or platform action ran.
