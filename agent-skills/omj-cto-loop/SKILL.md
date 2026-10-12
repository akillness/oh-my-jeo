---
name: omj-cto-loop
description: [omj] Turn operating signals into roadmap decisions, technical tradeoffs, delivery risk, release readiness, and accepted follow-up handoffs.
metadata:
  omj:
    portability: portable
    category: leadership
    phase: operating-loop
---

# Cto Loop

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`cto-loop` makes this workflow explicit: Turn operating signals into roadmap decisions, technical tradeoffs, delivery risk, release readiness, and accepted follow-up handoffs.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: cto-loop: run the PM, dev, QA, security, and ops loop for this risky billing launch.
- Expected behavior: Prepare the CTO operating model with role responsibilities, gates, blockers, and status boundaries.
- Why: The request needs a leadership operating loop, not just a generic plan.

Bad example:

- Prompt: cto-loop: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `cto-loop`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Turn operating signals into roadmap decisions, technical tradeoffs, delivery risk, release readiness, and accepted follow-up handoffs.

Strong routing signals: `cto-loop`, `cto loop`, `cto`, `cto pm`, `pm dev qa security ops`, `roadmap technical tradeoffs`, `technical tradeoff`, `delivery risk`, `release readiness`, `technical leadership loop`, `leadership operating loop`, `engineering leadership`, `CTO 구조`, `PM 구조`, `로드맵`, `아키텍처 트레이드오프`, `기술 리더십`, `출시 준비`

## Catalog Metadata

Category: `leadership`
Phase: `operating-loop`
Host-owned workflow responsibility
Quality tier: `decision-gated`

Quality bar:

- Separate product priority, architecture tradeoff, delivery risk, release risk, and follow-up owner.
- Tie recommendations to observed signals or mark assumptions.
- Record accepted decisions separately from draft recommendations.
- Prepare executor handoffs only for accepted implementation follow-ups.

Handoff policy:

Turn operating signals into roadmap decisions, technical tradeoffs, delivery risk, release readiness, and accepted follow-up handoffs. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- operating signals
- roadmap or release scope
- known risks
- decision owner

Expected outputs:

- priority frame
- architecture tradeoffs
- delivery risks
- decision note
- follow-up handoff candidates

Artifact expectations:

- leadership loop record or status summary when a wrapper captures decisions and follow-ups

Safety rules:

- Do not treat a CTO loop recommendation as an accepted roadmap decision.
- Do not imply CTO, PM, QA, Security, or Ops runtime agents exist without observed wrapper evidence.
- Separate strategy decisions from implementation handoffs and release evidence.

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
