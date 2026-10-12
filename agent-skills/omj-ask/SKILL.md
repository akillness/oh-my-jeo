---
name: omj-ask
description: [omj] Consult an explicitly configured external advisor only when useful; evaluate advice and authorize mutations separately.
metadata:
  omj:
    portability: portable
    category: review
    phase: external-advice
---

# Ask

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ask` makes this workflow explicit: Consult an explicitly configured external advisor only when useful; evaluate advice and authorize mutations separately.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: ask: ask Claude as an external advisor to critique this plugin bridge plan before implementation.
- Expected behavior: Prepare an advisor prompt, capture the response boundary, and summarize reusable critique.
- Why: The user wants outside review before committing to a direction.

Bad example:

- Prompt: ask: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ask`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Recovery Notes

- If the reviewed target is missing, inspect the requested artifact or ask one target question.
- If independent verification is unavailable, report the gap and avoid an approval-style claim.

## Use When

Consult an explicitly configured external advisor only when useful; evaluate advice and authorize mutations separately.

Strong routing signals: `ask`, `$ask`, `external advisor`, `claude`, `gemini`

## Catalog Metadata

Category: `review`
Phase: `external-advice`
Host-owned workflow responsibility
Quality tier: `evidence-gated`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate workflow guidance from executor or wrapper behavior unless evidence proves the step happened.

Handoff policy:

Consult an explicitly configured external advisor only when useful; evaluate advice and authorize mutations separately. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- question
- context summary
- why external advice helps

Expected outputs:

- advisor summary
- accepted/rejected advice
- decision note

Artifact expectations:

- advisor transcript reference only when explicitly captured

Safety rules:

- Use only when configured and materially useful.
- Treat advisor output as evidence to evaluate, not authority.
- Do not send secrets or private prompts without explicit opt-in.

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
