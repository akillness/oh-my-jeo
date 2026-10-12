---
name: omj-team
description: [omj] Coordinate independent work lanes with explicit ownership, verification, and integration boundaries.
metadata:
  omj:
    portability: portable
    category: execution
    phase: coordination
---

# Team

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`team` makes this workflow explicit: Coordinate independent work lanes with explicit ownership, verification, and integration boundaries.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: team: coordinate parallel agents for frontend polish, copy polish, and QA with worker ACKs.
- Expected behavior: Assign lanes, require worker ACK/result evidence, and keep integration verification separate.
- Why: The work benefits from multiple coordinated workers with disjoint ownership.

Bad example:

- Prompt: team: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `team`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Each lane has an owner, disjoint scope, expected output, and verification target.
- Worker ACK, dispatch, result, integration, and verification evidence are separated when wrappers record them.
- The integrated status names which lanes are observed, blocked, or still prepared_not_observed.

## Recovery Notes

- If two lanes are not independent, collapse them under one owner or re-plan before dispatch.
- If a worker has no ACK or result, mark that lane not_observed or blocked rather than infer progress.
- If integration reveals a shared-file conflict, stop lane fan-out and reassign ownership before continuing.

## Use When

Coordinate independent work lanes with explicit ownership, verification, and integration boundaries.

Strong routing signals: `team`, `$team`, `swarm`, `parallel agents`, `coordinated workers`

## Catalog Metadata

Category: `execution`
Phase: `coordination`
Host-owned workflow responsibility
Quality tier: `coordination-gated`

Quality bar:

- Split only independent lanes with explicit ownership and verification boundaries.
- Keep the coordinator and implementation owners explicit; report lane status only from evidence.
- Integrate lane evidence before reporting combined progress.

Handoff policy:

Coordinate independent work lanes with explicit ownership, verification, and integration boundaries. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- bounded lane definitions
- ownership boundaries
- verification target

Expected outputs:

- lane results
- integration summary
- combined verification evidence

Artifact expectations:

- delegation record only when separate participants are observed

Safety rules:

- Use parallel lanes only when work is independent.
- Keep shared-file edits under one owner.
- Record unobserved delegation as not_observed.

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
