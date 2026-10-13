---
name: omj-deploy-and-monitor
description: [omj] Prepare release checklists, health signals, rollback criteria, and post-deploy status without claiming infrastructure execution.
metadata:
  omj:
    portability: portable
    category: monitoring
    phase: release-ops
---

# Deploy And Monitor

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`deploy-and-monitor` makes this workflow explicit: Prepare release checklists, health signals, rollback criteria, and post-deploy status without claiming infrastructure execution.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: deploy-and-monitor: prepare the release monitor, rollback signals, health checks, and post-deploy status card.
- Expected behavior: Create release monitoring guidance with deployment, metric, rollback, and observation boundaries.
- Why: The request is about deploy readiness and monitoring rather than code review alone.

Bad example:

- Prompt: deploy-and-monitor: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `deploy-and-monitor`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Prepare release checklists, health signals, rollback criteria, and post-deploy status without claiming infrastructure execution.

Strong routing signals: `deploy-and-monitor`, `deploy and monitor`, `deploy monitor`, `deployment monitoring`, `release monitor`, `post deploy`, `post-deploy`, `rollback`, `rollback gate`, `health check`, `incident watch`, `release health`, `배포 모니터링`, `배포 감시`, `롤백`, `헬스 체크`, `장애 감시`, `릴리즈 모니터링`

## Catalog Metadata

Category: `monitoring`
Phase: `release-ops`
Host-owned workflow responsibility
Quality tier: `release-gated`

Quality bar:

- Name release scope, target environment, health signals, rollback criteria, and evidence owner.
- Show pre-deploy, deploy decision, monitor, rollback, and post-deploy record as distinct stages.
- Mark health and rollback status unknown until observed evidence arrives.
- Convert fix follow-ups into separate accepted plans or executor handoffs.

Handoff policy:

Prepare release checklists, health signals, rollback criteria, and post-deploy status without claiming infrastructure execution. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- release scope
- environment
- health signals
- rollback owner

Expected outputs:

- pre-deploy checklist
- deploy decision gate
- monitoring watchlist
- rollback criteria
- post-deploy status boundary

Artifact expectations:

- release operation status record when the wrapper captures deploy or monitor observations

Safety rules:

- Do not claim deployment, health checks, rollback, or incident response happened from a prepared checklist.
- Keep release readiness, deploy decision, monitor signals, and rollback as separate evidence steps.
- Route code fixes discovered during monitoring as later executor handoffs.

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
