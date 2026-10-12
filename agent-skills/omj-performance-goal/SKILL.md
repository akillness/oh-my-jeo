---
name: omj-performance-goal
description: [omj] Measure a performance baseline and evaluator-backed improvements without weakening correctness gates.
metadata:
  omj:
    portability: portable
    category: optimization
    phase: measurement
---

# Performance Goal

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`performance-goal` makes this workflow explicit: Measure a performance baseline and evaluator-backed improvements without weakening correctness gates.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: performance-goal: benchmark recommendation latency, optimize hot paths safely, and prove no regressions.
- Expected behavior: Create a measurement-led optimization loop with baseline, change, verification, and regression evidence.
- Why: The request is performance optimization and needs measured before/after proof.

Bad example:

- Prompt: performance-goal: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `performance-goal`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Measure a performance baseline and evaluator-backed improvements without weakening correctness gates.

Strong routing signals: `performance-goal`, `performance goal`, `latency`, `throughput`, `benchmark`

## Catalog Metadata

Category: `optimization`
Phase: `measurement`
Host-owned workflow responsibility
Quality tier: `measurement-gated`

Quality bar:

- Name the metric, baseline, budget, and benchmark command before optimizing.
- Treat code-level optimization as executor work when edits are required.
- Report deltas only from observed benchmark evidence.

Handoff policy:

Measure a performance baseline and evaluator-backed improvements without weakening correctness gates. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- metric
- baseline
- budget
- benchmark command

Expected outputs:

- measurement delta
- implementation summary
- benchmark evidence

Artifact expectations:

- baseline and final benchmark evidence

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
