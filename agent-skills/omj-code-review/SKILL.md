---
name: omj-code-review
description: [omj] Review code bug-first; cite concrete evidence and separate findings from accepted fixes.
metadata:
  omj:
    portability: portable
    category: review
    phase: critique
---

# Code Review

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`code-review` makes this workflow explicit: Review code bug-first; cite concrete evidence and separate findings from accepted fixes.

## Do Not Use When

- The user asks to implement the fix rather than review existing code or claims.
- There is no diff, file set, claim, artifact, or expected behavior to review.
- The request is broad product critique, strategy, or planning rather than code or evidence review.

## Examples

Good example:

- Prompt: $code-review review this PR for install/update UX regressions and missing tests.
- Expected behavior: Lead with ranked findings, cite concrete evidence, then list open questions and test gaps.
- Why: The task is explicitly review-shaped and has a behavioral risk surface.

Bad example:

- Prompt: $code-review add the missing setup flag and commit it.
- Expected behavior: Route implementation to a selected executor/runtime after review findings are established.
- Why: Review can identify the issue, but code mutation is a separate execution step.

## Completion Checklist

- Findings come first and are ranked by severity before summary or praise.
- Every finding cites file, diff, command output, artifact, or expected behavior evidence.
- No-issue reviews still name residual risk, missing tests, and independent review evidence if unavailable.
- Fix implementation, architecture follow-up, and CI/merge claims stay separate from the review result.

## Recovery Notes

- If no diff, file set, PR, or artifact is available, inspect the requested target or ask one target question before reviewing.
- If tests fail or are missing, cite the exact command gap and do not approve the change as verified.
- If independent review evidence is unavailable, say so directly instead of implying a second reviewer passed it.

## Use When

Review code bug-first; cite concrete evidence and separate findings from accepted fixes.

Strong routing signals: `code-review`, `$code-review`, `review`, `audit`, `find bugs`, `release gate`, `claim audit`, `evidence audit`, `README claim`, `what actually happened`, `code review`, `review gate`, `리뷰`, `코드 리뷰`, `리뷰까지`, `릴리즈 전`, `실제 코드와 맞는가`, `실제로 뭐 했는지`, `검증된 결과`

## Catalog Metadata

Category: `review`
Phase: `critique`
Host-owned workflow responsibility
Quality tier: `finding-evidence-gated`

Quality bar:

- Lead with ranked findings grounded in file, diff, command, or artifact evidence.
- Separate review findings from fix implementation; fixes become executor work.
- Say clearly when no actionable issue is found and name remaining test gaps.

Handoff policy:

Review code bug-first; cite concrete evidence and separate findings from accepted fixes. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- diff or files
- expected behavior
- test evidence

Expected outputs:

- ranked findings
- open questions
- test gaps

Artifact expectations:

- critic run record when review evidence is captured

Safety rules:

- Findings come before summaries.
- Cite concrete evidence for every finding.
- Say clearly when no issue is found.

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
