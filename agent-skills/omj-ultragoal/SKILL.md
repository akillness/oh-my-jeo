---
name: omj-ultragoal
description: [omj] Maintain durable .omj/goals ledgers, checkpoint progress, and require final evidence gates.
metadata:
  omj:
    portability: requires-omj-cli
    category: execution
    phase: durable-goals
---

# Ultragoal

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ultragoal` makes this workflow explicit: Maintain durable .omj/goals ledgers, checkpoint progress, and require final evidence gates.

## Do Not Use When

- The request is a single-turn answer, quick diagnosis, or small edit that does not need a durable ledger.
- Acceptance criteria, current checkpoint, and final gate expectations are too vague to make a goal inspectable.
- The user expects hidden code execution rather than explicit executor ownership and observed verification evidence.

## Examples

Good example:

- Prompt: $ultragoal turn OMJ skill quality into a durable goal with rubrics, generated skill sync, tests, and a PR gate.
- Expected behavior: Create or update a goal ledger, split the story into verifiable checkpoints, and close only after generated docs, skills, and tests match.
- Why: The task has multiple milestones and a final quality gate that should be inspectable across interruptions.

Bad example:

- Prompt: $ultragoal what does this one error mean?
- Expected behavior: Route to diagnosis or a direct answer instead of creating a durable goal.
- Why: A narrow explanation does not need checkpointed long-running state.

## Completion Checklist

- The goal_ledger/v1 names the current criteria, checkpoints, blockers, and next action.
- The goal_completion_gate/v1 result passes from required evidence, not from a summary-only message.
- All explicitly linked coding milestones have matching observed runtime evidence or are still named as gaps.
- The final user-facing status says complete, blocked, or continue with the exact remaining checkpoint.

## Recovery Notes

- If the goal ledger is stale or missing, inspect .omj/goals and ask which checkpoint to resume before continuing.
- If a blocker checkpoint exists, keep the goal open and record the blocker plus the smallest unblock action.
- If linked runtime evidence is missing, keep coding milestones prepared_not_observed and do not close the goal.

## Use When

Maintain durable .omj/goals ledgers, checkpoint progress, and require final evidence gates.

Strong routing signals: `ultragoal`, `$ultragoal`, `durable goal`, `multi-goal`, `goal ledger`

## Catalog Metadata

Category: `execution`
Phase: `durable-goals`
Host-owned workflow responsibility
Quality tier: `checkpoint-gated`

Quality bar:

- Keep goal state durable, inspectable, and separate from chat narration.
- Checkpoint every success, blocker, and final quality gate with fresh evidence.
- Reject completion with a summary-only goal_completion_gate/v1 result until required criteria, blockers, and explicitly linked runtime runs are satisfied.
- Tell the user the next action through goal_status_card/v1 or goal_continuation/v1 instead of ending with vague follow-up copy.
- For coding milestones, use prepared runtime handoffs and observed runtime evidence rather than hidden execution claims.

Handoff policy:

Maintain durable .omj/goals ledgers, checkpoint progress, and require final evidence gates. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- goal statement
- acceptance criteria
- current checkpoint or missing criteria

Expected outputs:

- goal_ledger/v1 updates
- checkpoint evidence
- goal_completion_gate/v1 result
- completion or blocker summary

Artifact expectations:

- metadata-only .omj/goals ledger
- goal_status_card/v1 or goal_continuation/v1 wrapper payload
- runtime run record only for explicitly linked coding milestones

Safety rules:

- Do not imply hidden host or executor runtime behavior.
- Use the smallest verification that can prove the claim.

## Execution and Handoff Discipline

1. State the target, constraints, acceptance criteria, authority, and stop condition before work.
2. Planning and coordination do not take ownership of code implicitly. Keep the selected first-class coding owner explicit, including the current host when selected.
3. Read supporting references only when needed using available host file tools; loading guidance is not dispatch or plan acceptance.
4. Take acceptance only from the user's actual answer. A timeout, dismissal, or missing answer leaves the plan unaccepted; prepare no handoff and start nothing.
5. A selected owner, task card, plan, or prepared handoff stays `prepared_not_observed` until observed execution evidence exists. Preserve failures and unresolved criteria.
6. Verify behavior with the smallest relevant observed check. Current loader admission is not evidence of a live session; local fresh files do not prove host discovery, execution, review, CI, or merge.
7. Network operations, configuration or memory writes, external publishing, and new authority remain separately approval-gated. Do not activate unsupported services.

## Supporting Context

[Native and historical provenance](../omj/references/native-provenance.md)
