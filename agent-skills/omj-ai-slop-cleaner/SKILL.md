---
name: omj-ai-slop-cleaner
description: [omj] Scope behavior-preserving cleanup and require regression checks before and after edits.
metadata:
  omj:
    portability: portable
    category: maintenance
    phase: cleanup
---

# Ai Slop Cleaner

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ai-slop-cleaner` makes this workflow explicit: Scope behavior-preserving cleanup and require regression checks before and after edits.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: $ai-slop-cleaner remove duplicated router branches and lock behavior with regression tests before refactoring.
- Expected behavior: Plan cleanup, preserve behavior, delete or simplify code, and prove it with targeted tests.
- Why: The request is maintenance cleanup with regression risk.

Bad example:

- Prompt: ai-slop-cleaner: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ai-slop-cleaner`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- The selected coding or runtime owner is named before any implementation claim.
- Prepared handoff, dispatch, execution, verification, review, CI, and merge states are separated.
- The final status cites observed runtime evidence or keeps the work prepared_not_observed.

## Recovery Notes

- If the selected executor is unavailable, ask for an available coding owner before retrying.
- If dispatch or result evidence is missing, keep the handoff prepared_not_observed and expose the next observable action.

## Use When

Scope behavior-preserving cleanup and require regression checks before and after edits.

Strong routing signals: `ai-slop-cleaner`, `$ai-slop-cleaner`, `cleanup`, `deslop`, `refactor`, `risky`, `behavior-preserving refactor`, `risk analysis`, `refactor workflow`, `legacy refactor`, `리팩터링`, `리팩토링`, `위험 분석`, `변경 범위 제한`, `회귀 테스트`

## Catalog Metadata

Category: `maintenance`
Phase: `cleanup`
Host-owned workflow responsibility
Quality tier: `regression-gated`

Quality bar:

- Lock current behavior with regression checks before non-trivial cleanup.
- Prefer deletion, reuse, and boundary repair over new abstractions.
- Rerun verification after cleanup before claiming behavior is preserved.

Handoff policy:

Scope behavior-preserving cleanup and require regression checks before and after edits. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- target smell
- current behavior
- regression checks

Expected outputs:

- small cleanup diff
- before/after verification
- residual risk

Artifact expectations:

- cleanup plan and regression evidence for non-trivial work

Safety rules:

- Lock behavior with tests before risky cleanup.
- Prefer deletion and existing utilities over new layers.
- Do not add dependencies for cleanup unless explicitly requested.

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
