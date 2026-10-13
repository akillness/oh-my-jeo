---
name: omj-plan
description: [omj] Create a structured plan with target, constraints, acceptance criteria, and explicit acceptance before implementation.
metadata:
  omj:
    portability: portable
    category: planning
    phase: plan
---

# Plan

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`plan` makes this workflow explicit: Create a structured plan with target, constraints, acceptance criteria, and explicit acceptance before implementation.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: plan: handle a planning request that needs explicit evidence boundaries and a clear stop condition.
- Expected behavior: Run `plan` only after naming the target, evidence boundary, and stop condition.
- Why: The request matches the catalog use case and keeps observed evidence separate from prepared guidance.

Bad example:

- Prompt: plan: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `plan`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- The plan names current state, target state, non-goals, and the next decision boundary.
- Review Focus names at most five requirement-implied uncovered inputs, each paired with its expected behavior and owning test or task, or states none found when no unmapped input remains.
- Every acceptance criterion maps to a task and verification scenario; target-state coverage gaps are explicit.
- Keep each step one checkable action sized proportionate to the change; sizing bands are recorded where scope warrants them.
- The plan remains unapproved until the user explicitly accepts the plan; a prepared handoff is not approval or execution evidence.
- Before the plan is offered for acceptance, answer four questions for test authoring: what behavior changes, what regression it plausibly prevents, what the closest existing coverage is, and whether it touches a production-unused seam.

## Recovery Notes

- If current or target state is missing, stop and ask for the smallest decision-changing fact before planning further.
- If a criterion lacks a task or verification scenario, keep the plan blocked rather than silently accepting a gap.
- If the user has not explicitly accepted the plan, keep the plan awaiting, do not prepare an implementation handoff, and do not start implementation.

## Use When

Create a structured plan with target, constraints, acceptance criteria, and explicit acceptance before implementation.

Strong routing signals: `plan`, `$plan`, `implementation plan`, `strategy`, `task breakdown`, `safe feature`, `safely add a feature`, `add a feature`, `feature request`, `new feature`, `product triage`, `bug triage`, `issue triage`, `reproduction plan`, `workflow hub`, `coding handoff`, `답할 차례`, `준비할 차례`, `project template`, `재현 계획`, `요구사항 정리`, `작업 허브`, `작업 허브가 필요`, `github pr workflow`, `상태와 다음 행동`, `프로젝트별 운영`

## Catalog Metadata

Category: `planning`
Phase: `plan`
Host-owned workflow responsibility
Quality tier: `acceptance-gated`

Quality bar:

- Make goals, non-goals, risks, acceptance criteria, and verification shape explicit.
- Keep draft plans unapproved until the user's actual answer accepts them; a wrapper may carry the user's answer and its response status/value but cannot originate acceptance.
- Only prepare coding handoff guidance after the plan is accepted.
- Bound Review Focus to five inputs and pass the four-question test-authoring gate.
- Take plan acceptance only from the answer the user gave — the response status and value the question tool returns, or the user's own reply — never from the wording of the question you asked: when the acceptance question times out, is dismissed, or returns with no answer, the plan stays unaccepted, so record no acceptance, prepare no handoff, and start nothing; a missing answer is not a refusal either, so ask again later or report the plan as awaiting acceptance.

Handoff policy:

Create a structured plan with target, constraints, acceptance criteria, and explicit acceptance before implementation. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- requirements
- constraints
- known facts
- non-goals

Expected outputs:

- plan
- acceptance criteria
- verification strategy

Artifact expectations:

- plan artifact when durable execution will follow

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
