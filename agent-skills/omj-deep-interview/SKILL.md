---
name: omj-deep-interview
description: [omj] Clarify materially ambiguous requirements one question at a time before planning or execution.
metadata:
  omj:
    portability: portable
    category: clarification
    phase: discovery
---

# Deep Interview

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`deep-interview` makes this workflow explicit: Clarify materially ambiguous requirements one question at a time before planning or execution.

## Do Not Use When

- The request already has concrete scope, acceptance criteria, and verification commands.
- The missing information is discoverable from the repository or local artifacts without asking the user.
- The user asked for immediate read-only analysis and the ambiguity does not change the answer.

## Examples

Good example:

- Prompt: $deep-interview before planning Discord and Slack routing, ask what each channel owns and what evidence counts.
- Expected behavior: Ask one decision-changing question at a time, then produce goals, non-goals, and acceptance criteria.
- Why: The request explicitly rejects assumptions and needs product boundaries before implementation.

Bad example:

- Prompt: $deep-interview fix this failing test; the traceback and expected behavior are attached.
- Expected behavior: Proceed to diagnosis or implementation instead of interviewing.
- Why: The required facts are already available, so more questions would slow the workflow.

## Completion Checklist

- One decision-changing question is asked per turn or the structured batch contract is explicit.
- The clarified brief records current ambiguity, goals, non-goals, decision boundaries, and acceptance criteria.
- Only an explicit user answer or question-tool response changes awaiting to accepted or refused; timeout, dismissal, and no answer do not.
- Idea approval is not later plan, handoff, dispatch, code, review, CI, or merge authorization.

## Recovery Notes

- If the user does not answer, keep the interview awaiting and do not infer refusal or acceptance.
- If the user approves the idea but no plan acceptance exists, route to planning without preparing implementation handoff.

## Use When

Clarify materially ambiguous requirements one question at a time before planning or execution.

Strong routing signals: `deep-interview`, `$deep-interview`, `interview`, `don't assume`, `clarify`, `feature shaping`, `ambiguous product request`, `one question`, `온보딩`, `부드럽게`, `모호한 제품 요청`, `기획자`, `개발자 사이`

## Catalog Metadata

Category: `clarification`
Phase: `discovery`
Host-owned workflow responsibility
Quality tier: `clarity-gated`

Quality bar:

- Ask exactly one blocking question per turn unless the wrapper explicitly supports a structured batch.
- Tie each question to a missing decision that changes the plan, handoff, or stop condition.
- The locked seed must carry non-goals and acceptance criteria so planning and delegation read one fixed contract.

Handoff policy:

Clarify materially ambiguous requirements one question at a time before planning or execution. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- initial request
- known repo facts
- current ambiguity

Expected outputs:

- clarified brief
- non-goals
- decision boundaries

Artifact expectations:

- clarity summary or transcript when the wrapper supports it

Safety rules:

- Ask one question at a time.
- Gather discoverable repo facts before asking the user.
- Stop clarifying once ambiguity is low (about 0.2 or less) and lock the requirements seed against further drift.
- This idea agreement does not authorize a later plan, handoff, dispatch, code edit, review, CI, or merge.

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
