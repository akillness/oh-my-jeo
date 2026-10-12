# Prepared guidance: agent-debug

Family: `agent-failure-and-eval`  
Category: `operations`  
Phase: `agent-debug`  
Role: `operator`

## Contract
[omh] Agent is stuck, looping, or drifting: capture a stuck, looping, drifting, or repeatedly failing agent run, diagnose the likely failure pattern, and prepare the smallest safe recovery action. Use when the user says: agent-debug, agent debug, agent debugging, agent introspection, agent self-debug, self-debug, self debugging, looping agent.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- agent-debug
- agent debug
- agent debugging
- agent introspection
- agent self-debug
- self-debug
- self debugging
- looping agent

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- agent_debug_report/v1
- agent_failure_capture/v1
- agent_failure_pattern_hypothesis/v1
- contained_recovery_action/v1

## Artifact expectations
- agent_debug_report/v1 from `omh quality-evidence agent-debug --hermes-session <id|latest> --observable <kind> --json` (or `--session-record <jsonl>`, `--turns N:M`): tool errors, identical retries after an error, background processes started without notify_on_complete, and compaction boundaries, each cited by session and message id or record line; treat a kind listed unavailable as unchecked
- agent_failure_capture/v1 and agent_failure_pattern_hypothesis/v1 in that payload: observed finding ids, unavailable evidence, and at least two competing hypotheses with evidence for and against
- contained_recovery_action/v1 proposing the smallest reversible step, never executed; sharing is the separate `agent-debug-export`, written only with --confirm-export

## Acceptance criteria
- Failure state, intended goal, recent tool sequence, and context pressure are captured.
- Diagnosis distinguishes repeated command/tool loops, context drift, environment mismatch, service errors, and wrong-hypothesis tests.
- Recovery action is contained, reversible, and does not claim implementation, verification, CI, merge, or future-loop fixes.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: workflow-surface-gated
- source owner: skills/omh-agent-debug/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-agent-debug/SKILL.md`
- SHA256: `bcab2434ebcf01f32d34a9493a154f233bbcd53b6f39418c2be9a4b8fec4fe08`

## Method references
- `omh-agent-debug/references/session-forensics.md` (pinned `skills/omh-agent-debug/references/session-forensics.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: user request
- blocked until supplied or observed: target context
- blocked until supplied or observed: delivery or status expectation
- blocked until supplied or observed: known missing evidence
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
