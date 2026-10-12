---
name: omj-idea-to-deploy
description: [omj] Shape an idea into decisions, an accepted plan, implementation handoff, verification, release, rollback, and monitoring gates.
metadata:
  omj:
    portability: portable
    category: delivery
    phase: app-delivery-loop
---

# Idea To Deploy

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`idea-to-deploy` makes this workflow explicit: Shape an idea into decisions, an accepted plan, implementation handoff, verification, release, rollback, and monitoring gates.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: idea-to-deploy: turn this onboarding idea into a scoped plan, implementation handoff, QA gate, and release path.
- Expected behavior: Prepare the idea-to-release lane while keeping implementation, QA, and deploy evidence observed-only.
- Why: The request spans product shaping through deploy readiness instead of a single task.

Bad example:

- Prompt: idea-to-deploy: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `idea-to-deploy`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Shape an idea into decisions, an accepted plan, implementation handoff, verification, release, rollback, and monitoring gates.

Strong routing signals: `idea-to-deploy`, `idea to deploy`, `from idea to deploy`, `plan to deploy`, `idea to launch`, `ship this idea`, `ship this feature`, `launch this feature`, `product delivery loop`, `app delivery loop`, `complete product loop`, `end-to-end app operation`, `완제품 루프`, `아이디어부터 배포`, `기획부터 배포`, `출시까지`, `앱 운영 루프`

## Catalog Metadata

Category: `delivery`
Phase: `app-delivery-loop`
Host-owned workflow responsibility
Quality tier: `delivery-gated`

Quality bar:

- Name the idea, user value, decision owner, non-goals, and success metric before planning delivery.
- Expose idea, decision, plan, handoff, verification, release, deploy, and monitor stages as separate status steps.
- Prepare coding handoffs only after plan acceptance and selected executor/runtime choice.
- Mark deploy, monitoring, and rollback as unobserved until the wrapper or operator records evidence.

Handoff policy:

Shape an idea into decisions, an accepted plan, implementation handoff, verification, release, rollback, and monitoring gates. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- product idea
- target user or customer signal
- success metric
- repo or app context

Expected outputs:

- stage rail
- decision gates
- executor handoff criteria
- verification and deploy/monitor status boundaries

Artifact expectations:

- app delivery loop status record when the wrapper captures stage acceptance or observations

Safety rules:

- Do not claim implementation, deploy, health checks, rollback, or monitoring happened from a prepared loop.
- Keep coding, release, and monitoring observations as separate evidence gates.
- Ask for missing success metric, release scope, or executor choice before preparing a handoff.

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
