---
name: omj-wiki
description: [omj] Capture durable project knowledge in source-grounded Markdown artifacts.
metadata:
  omj:
    portability: portable
    category: knowledge
    phase: capture
---

# Wiki

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`wiki` makes this workflow explicit: Capture durable project knowledge in source-grounded Markdown artifacts.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: wiki: capture the final router architecture decisions and retrieval hints in the project knowledge base.
- Expected behavior: Write durable project knowledge with source context, staleness notes, and follow-up links.
- Why: The request is knowledge capture rather than planning or execution.

Bad example:

- Prompt: wiki: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `wiki`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- The durable fact, source evidence, retrieval hint, and staleness risk are recorded.
- Uncertain or conflicting knowledge is marked as review-needed rather than permanent truth.
- Separate coding or docs tasks are extracted instead of buried in notes.

## Recovery Notes

- If source evidence conflicts, route to memory or knowledge review before writing durable guidance.
- If the fact may be stale, record the staleness warning and next refresh action.

## Use When

Capture durable project knowledge in source-grounded Markdown artifacts.

Strong routing signals: `wiki`, `project wiki`, `memory`, `notes`

## Catalog Metadata

Category: `knowledge`
Phase: `capture`
Host-owned workflow responsibility
Quality tier: `knowledge-gated`

Quality bar:

- Capture durable facts with source evidence and retrieval hints.
- Mark stale or uncertain knowledge instead of presenting it as permanent truth.
- Extract separate coding tasks instead of burying them in notes.

Handoff policy:

Capture durable project knowledge in source-grounded Markdown artifacts. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- project fact
- source evidence
- target topic

Expected outputs:

- markdown note
- retrieval hint
- staleness warning when needed

Artifact expectations:

- repo-local markdown knowledge artifact

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
