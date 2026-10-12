---
name: omj-meeting-brief
description: [omj] Prepare an agenda, discussion prompts, decisions, and a meeting record template.
metadata:
  omj:
    portability: portable
    category: meeting
    phase: preparation
---

# Meeting Brief

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`meeting-brief` makes this workflow explicit: Prepare an agenda, discussion prompts, decisions, and a meeting record template.

## Do Not Use When

- The user needs observed meeting minutes, decisions, or action items but has not provided notes.
- The request is strategy synthesis without a meeting audience, agenda, or decision ceremony.
- The follow-up is implementation work that already has accepted requirements and should become a plan or handoff.

## Examples

Good example:

- Prompt: Prepare a meeting agenda for a leadership sync on setup UX, plugin bridge defaults, and release risk.
- Expected behavior: Prepare agenda topics, prompts, decisions needed, and a record template with unknowns marked.
- Why: The request is preparation for a meeting and should separate prep from observed outcomes.

Bad example:

- Prompt: meeting-brief summarize what the team decided yesterday.
- Expected behavior: Ask for meeting notes or route to an ops/status summary with explicit evidence gaps.
- Why: A prepared agenda cannot be treated as observed minutes or decisions.

## Completion Checklist

- The agenda, participants or audience, decisions needed, and record template are named.
- Meeting prep, observed minutes, accepted decisions, and action ownership are separate states.
- Missing context that would change the meeting structure is surfaced.

## Recovery Notes

- If participants, purpose, or decision owner are missing, ask for the one field that changes the agenda.
- If minutes or decisions were not observed, keep the output as prep rather than record.

## Use When

Prepare an agenda, discussion prompts, decisions, and a meeting record template.

Strong routing signals: `meeting-brief`, `meeting brief`, `meeting agenda`, `agenda`, `discussion prompts`, `decisions needed`, `record template`, `meeting topics`, `회의 주제`, `회의 아젠다`, `아젠다`, `회의 준비`, `논의 질문`, `결정할 것`, `기록 템플릿`

## Catalog Metadata

Category: `meeting`
Phase: `preparation`
Host-owned workflow responsibility
Quality tier: `facilitation-gated`

Quality bar:

- Turn context into agenda topics, prompts, decisions needed, and a record template.
- Keep prep distinct from actual meeting minutes or accepted decisions.
- Identify missing context that would change the meeting structure.

Handoff policy:

Prepare an agenda, discussion prompts, decisions, and a meeting record template. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- meeting goal
- audience
- known context
- decision topics

Expected outputs:

- agenda
- discussion prompts
- decisions needed
- action-item template

Artifact expectations:

- meeting brief or record template when the wrapper captures it

Safety rules:

- Do not claim the meeting happened from a prepared agenda.
- Separate proposed action items from observed decisions.
- Use a later status or decision record for actual meeting outcomes.

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
