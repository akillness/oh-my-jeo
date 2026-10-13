---
name: omj-reliability-review
description: [omj] Review incident, SLO, and error-budget evidence; prepare accepted remediation and claim closure only from observed results.
metadata:
  omj:
    portability: portable
    category: reliability
    phase: incident-and-slo-review
---

# Reliability Review

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`reliability-review` makes this workflow explicit: Review incident, SLO, and error-budget evidence; prepare accepted remediation and claim closure only from observed results.

## Do Not Use When

- The user only needs a generic status report or leadership deck.
- No service, incident, SLO, metric, or reliability source boundary is available.
- The request is implementation of remediation rather than review of reliability evidence.

## Examples

Good example:

- Prompt: reliability-review 장애 포스트모템과 SLO 에러버짓 상태를 검토해줘.
- Expected behavior: Prepare a reliability artifact that separates metrics/references, assumptions, missing evidence, and remediation follow-ups.
- Why: The request is reliability evidence review with closure-sensitive claims.

Bad example:

- Prompt: reliability-review make a monthly PPT report for leadership.
- Expected behavior: Use `report-package` unless the report specifically asks for reliability evidence review.
- Why: Report packaging and reliability validation are independent operations surfaces.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Review incident, SLO, and error-budget evidence; prepare accepted remediation and claim closure only from observed results.

Strong routing signals: `reliability-review`, `reliability review`, `incident review`, `incident postmortem`, `postmortem`, `post-mortem`, `slo review`, `slo`, `sla`, `error budget`, `service reliability`, `reliability followup`, `remediation tracking`, `sre review`, `장애 리뷰`, `장애 회고`, `포스트모템`, `사후 분석`, `에러버짓`, `에러 버짓`, `서비스 신뢰성`, `신뢰성 검증`, `재발 방지`

## Catalog Metadata

Category: `reliability`
Phase: `incident-and-slo-review`
Host-owned workflow responsibility
Quality tier: `reliability-gated`

Quality bar:

- Name service, incident/time window, SLO/error-budget target, source references, and missing observations.
- Separate supplied metrics, incident notes, assumptions, and remediation follow-ups.
- Keep closure and remediation status unobserved until evidence is supplied.

Handoff policy:

Review incident, SLO, and error-budget evidence; prepare accepted remediation and claim closure only from observed results. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- service or incident scope
- time window
- metric/source references
- known remediation items or gaps

Expected outputs:

- reliability review
- evidence and missing-evidence list
- remediation follow-up boundary

Artifact expectations:

- operation_artifact/v1 reliability-review artifact when a wrapper or CLI records it

Safety rules:

- Do not claim SLO pass, healthy error budget, incident closure, or remediation completion without source, metric, or reference evidence.
- Do not treat a reliability narrative as verification, review, CI, merge, or deploy evidence.
- Route code remediation through a separate accepted plan or executor handoff.

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
