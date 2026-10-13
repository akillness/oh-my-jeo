---
name: omj-deliverable-package
description: [omj] Track documents and attachments through prepared, generated, QA, approved, and attached states using observed evidence.
metadata:
  omj:
    portability: portable
    category: deliverables
    phase: package-status
---

# Deliverable Package

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`deliverable-package` makes this workflow explicit: Track documents and attachments through prepared, generated, QA, approved, and attached states using observed evidence.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMJ to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: deliverable-package turn this research into PPT and PDF with attachment status.
- Expected behavior: Produce `prepare_deliverable_package` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface without hiding execution.

Bad example:

- Prompt: deliverable-package claim the PDF was attached without observed file evidence.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMJ guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The deliverable type, audience, source inputs, QA ladder, and delivery boundary are named.
- Prepared generation, generated file, render QA, approval, attachment, and delivery are separate states.
- The next action says whether to generate, revise, QA, approve, attach, or deliver.

## Recovery Notes

- If generation tooling is missing, prepare a prompt or package handoff and mark file output not_observed.
- If QA or attachment evidence is missing, keep generated/delivered states separate and show the next check.

## Use When

Track documents and attachments through prepared, generated, QA, approved, and attached states using observed evidence.

Strong routing signals: `deliverable-package`, `deliverable mode`, `file attachment`, `attach file`, `attachment status`, `file delivery`, `file deliverable status`, `generated file`, `자료`, `첨부`, `첨부 상태`, `전달 상태`

## Catalog Metadata

Category: `deliverables`
Phase: `package-status`
Host-owned workflow responsibility
Quality tier: `workflow-surface-gated`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Track documents and attachments through prepared, generated, QA, approved, and attached states using observed evidence. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- deliverable-package/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- deliverable-package/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- A deliverable package card is not binary generation, render QA, formula recalculation, approval, upload, attachment, or delivery evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

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
