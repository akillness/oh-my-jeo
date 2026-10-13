---
name: omj-ralph
description: [omj] Continue concrete accepted work through implementation, verification, and review with one accountable owner.
metadata:
  omj:
    portability: portable
    category: execution
    phase: completion
---

# Ralph

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ralph` makes this workflow explicit: Continue concrete accepted work through implementation, verification, and review with one accountable owner.

## Do Not Use When

- The request is casual chat, a status-only acknowledgement, or another workflow has stronger routing evidence.
- The user needs implementation, review, CI, merge, or external publishing evidence that has not been delegated or observed.

## Examples

Good example:

- Prompt: ralph: finish the invoice export recovery until the smoke test passes or a blocker is recorded.
- Expected behavior: Keep one completion owner, track evidence after every recovery step, and stop only on pass, block, or explicit cancel.
- Why: The request needs persistent completion pressure with an observable stop condition.

Bad example:

- Prompt: ralph: treat casual chat or unaccepted work as if this workflow already produced verified results.
- Expected behavior: Ask a clarification question or route to a narrower workflow instead of forcing `ralph`.
- Why: The request lacks required inputs or would overclaim unobserved work.

## Completion Checklist

- Ruling: decision, reason, reversible, in-scope, cost if wrong.
- Load `references/loop-design-review.md` for machine-decidable finish line, independent judge, and bounded retries.

## Recovery Notes

- If the selected executor is unavailable, ask for an available coding owner before retrying.
- If dispatch or result evidence is missing, keep the handoff prepared_not_observed and expose the next observable action.

## Use When

Continue concrete accepted work through implementation, verification, and review with one accountable owner.

Strong routing signals: `ralph`, `$ralph`, `finish until done`, `persistent execution`, `self-referential loop`

## Catalog Metadata

Category: `execution`
Phase: `completion`
Host-owned workflow responsibility
Quality tier: `handoff-gated`

Quality bar:

- Do not enter a finish-until-done loop until scope, acceptance criteria, and verification commands are concrete.
- For coding edits, prepare and track selected runtime evidence instead of implying unobserved work happened.
- Report completion only from observed execution and verification evidence.

Handoff policy:

Keep as compatibility guidance; for implementation, ask the wrapper to prepare/track the selected coding runtime path instead of hiding execution inside chat narration.

Required inputs:

- concrete scope
- acceptance criteria
- verification commands

Expected outputs:

- completed work summary
- verification evidence
- remaining risks

Artifact expectations:

- goal-execution run record
- checkpoint or final evidence when available

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
