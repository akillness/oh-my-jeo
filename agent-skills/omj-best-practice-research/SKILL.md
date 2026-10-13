---
name: omj-best-practice-research
description: [omj] Research bounded official or upstream guidance before decisions that depend on current facts.
metadata:
  omj:
    portability: portable
    category: research
    phase: evidence
---

# Best Practice Research

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`best-practice-research` makes this workflow explicit: Research bounded official or upstream guidance before decisions that depend on current facts.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: best-practice-research: check official docs and upstream examples before we choose the plugin packaging pattern.
- Expected behavior: Gather primary-source guidance, compare options, and separate evidence from recommendation.
- Why: The request needs citation-backed best-practice research before implementation.

Bad example:

- Prompt: best-practice-research: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `best-practice-research`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- The research question, source boundaries, recency assumptions, and confidence level are named.
- Observed sources, inference, synthesis, and unresolved retrieval gaps are separated.
- Follow-up planning or handoff uses the research summary without calling it execution evidence.

## Recovery Notes

- If sources cannot be accessed, state the retrieval gap and use only observed local context.
- If evidence is thin or one-sided, lower confidence and ask for a narrower source boundary.

## Use When

Research bounded official or upstream guidance before decisions that depend on current facts.

Strong routing signals: `best-practice-research`, `best practice`, `official docs`, `upstream guidance`

## Catalog Metadata

Category: `research`
Phase: `evidence`
Host-owned workflow responsibility
Quality tier: `source-gated`

Quality bar:

- Use official or upstream sources first and name the version/environment assumptions.
- Map applicability to the user's local context before recommending action.
- Preserve residual uncertainty instead of overstating best practice.

Handoff policy:

Research bounded official or upstream guidance before decisions that depend on current facts. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- chosen technology
- question
- version or environment constraints

Expected outputs:

- source-backed guidance
- applicability notes
- residual uncertainty

Artifact expectations:

- research notes or citations when the wrapper captures them

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
