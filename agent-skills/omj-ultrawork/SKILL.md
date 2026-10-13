---
name: omj-ultrawork
description: [omj] Execute accepted disjoint lanes with dependency, red/green, ruling, and evidence-ledger discipline.
metadata:
  omj:
    portability: requires-omj-cli
    category: execution
    phase: parallel-delivery
---

# Ultrawork

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ultrawork` makes this workflow explicit: Execute accepted disjoint lanes with dependency, red/green, ruling, and evidence-ledger discipline.

## Do Not Use When

- The work touches the same files or invariants in ways that need one owner.
- The plan is not accepted, lane boundaries are unclear, or verification commands are missing.
- The user expects hidden coding execution rather than explicit ownership and observed results.

## Examples

Good example:

- Prompt: $ultrawork split the accepted docs refresh, CLI output polish, and test updates into parallel implementation lanes.
- Expected behavior: Create disjoint lane prompts with acceptance criteria, verification commands, and review evidence requirements.
- Why: The work can be split cleanly and benefits from parallel execution discipline.

Bad example:

- Prompt: $ultrawork refactor the central router in five agents at once.
- Expected behavior: Keep one owner or re-plan boundaries before parallelization.
- Why: Shared core logic makes parallel edits likely to conflict or hide regressions.

## Completion Checklist

- All work lanes are disjoint by file, invariant, or responsibility before preparing parallel handoffs.
- Each lane has acceptance criteria, verification command, worker protocol expectation, and review owner.
- Worker ACK, dispatch, result, review, CI, and merge evidence are observed or explicitly missing.
- Integration verification ran after lane results before the final status claims completion.

## Recovery Notes

- If lanes are non-disjoint, collapse to one owner or route back to ultragoal before coding starts.
- If a worker does not ACK or return a result, keep that lane blocked/not_observed and expose the retry or reassignment action.
- If a worktree or shared-file conflict appears, pause parallel delivery and re-plan ownership before more edits.

## Use When

Execute accepted disjoint lanes with dependency, red/green, ruling, and evidence-ledger discipline.

Strong routing signals: `ultrawork`, `$ultrawork`, `parallel work`, `parallel implementation`, `high throughput`

## Catalog Metadata

Category: `execution`
Phase: `parallel-delivery`
Host-owned workflow responsibility
Quality tier: `handoff-gated`

Quality bar:

- Require disjoint lane ownership before preparing multiple coding runtime handoffs.
- Attach acceptance criteria, verification commands, and review expectations to each lane.
- Keep dispatch, execution, review, CI, and merge status evidence separate.
- Load `references/execution-rulings.md`, `references/dependency-topology.md`, `references/service-contract.md`, and `references/tdd-red-green.md`.

Handoff policy:

Keep the workflow name for compatibility, but convert coding lanes into explicit selected runtime handoffs with disjoint scope, verification, review evidence, worker protocol, and worktree guidance.

Required inputs:

- accepted plan
- lane list
- disjoint file or responsibility scopes
- verification commands

Expected outputs:

- runtime handoff prompts or lane instructions
- status summary
- review/CI evidence requirements

Artifact expectations:

- prepared coding delegation record per implementation lane when wrappers can record them

Safety rules:

- Do not start parallel coding without disjoint ownership boundaries.
- Keep orchestration and implementation ownership explicit, even when the current host is the selected coding owner.
- Record unobserved executor work as prepared_not_observed or not_observed.

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
[Source-owned procedural guidance](references/procedures/ultrawork.md)
