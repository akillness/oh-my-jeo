---
name: omj-ultraqa
description: [omj] Design adversarial scenarios and run bounded hypothesis, flaky-test, race, and fix-verification loops.
metadata:
  omj:
    portability: portable
    category: verification
    phase: qa
---

# Ultraqa

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ultraqa` makes this workflow explicit: Design adversarial scenarios and run bounded hypothesis, flaky-test, race, and fix-verification loops.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: $ultraqa test the setup wizard with hostile install paths, stale config, and missing PATH cases.
- Expected behavior: Generate adversarial QA scenarios, expected signals, observed results, and fix-or-retry routing.
- Why: The request asks for verification pressure and hostile scenarios.

Bad example:

- Prompt: ultraqa: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ultraqa`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Load `references/hypothesis-and-race-method.md`.

## Recovery Notes

- If the expected behavior is unclear, route back to plan before running adversarial checks.
- If verification fails, return to fix or research with the failed signal instead of advancing.

## Use When

Design adversarial scenarios and run bounded hypothesis, flaky-test, race, and fix-verification loops.

Strong routing signals: `ultraqa`, `$ultraqa`, `adversarial qa`, `hostile scenarios`, `e2e qa`, `real-world qa`, `qa scenario`, `release qa`, `장애 상황`, `쿠버네티스 장애`, `적절히 진단`, `검증 체크리스트`, `릴리즈 전 gate`

## Catalog Metadata

Category: `verification`
Phase: `qa`
Host-owned workflow responsibility
Quality tier: `scenario-gated`

Quality bar:

- Generate hostile scenarios from changed behavior and known risk areas.
- Report pass/fail evidence separately from proposed fixes.
- Delegate code mutations discovered by QA to the selected coding executor.
- Run same reproduction command after each fix; third failed attempt: escalate; no fourth fix.

Handoff policy:

Design adversarial scenarios and run bounded hypothesis, flaky-test, race, and fix-verification loops. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- changed behavior
- acceptance criteria
- known risk areas

Expected outputs:

- adversarial scenarios
- pass/fail evidence
- fix recommendations

Artifact expectations:

- QA scenario evidence
- runtime verification summary

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
[Source-owned procedural guidance](references/procedures/ultraqa.md)
