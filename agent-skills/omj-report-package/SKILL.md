---
name: omj-report-package
description: [omj] Turn supplied inputs into a report, executive brief, slide outline, or upload package without claiming delivery.
metadata:
  omj:
    portability: portable
    category: reporting
    phase: package-outline
---

# Report Package

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`report-package` makes this workflow explicit: Turn supplied inputs into a report, executive brief, slide outline, or upload package without claiming delivery.

## Do Not Use When

- The user needs SLO, incident, or error-budget review; use `reliability-review`.
- The user asks for a live `.pptx` deck file rather than a PPT-ready outline.
- The request is meeting minutes, scrum history, or action-item tracking.

## Examples

Good example:

- Prompt: report-package 월간 리더십 보고서 PPT outline 만들어줘.
- Expected behavior: Prepare a report package with sections, assumptions, missing inputs, and Markdown/JSON outline scope.
- Why: The request is packaging known information for reporting, not reliability validation or code work.

Bad example:

- Prompt: report-package prove our SLO passed and close the incident.
- Expected behavior: Route to `reliability-review` and require metric or incident evidence.
- Why: Report packaging cannot satisfy reliability closure evidence.

## Completion Checklist

- The reporting window, inputs, audience, narrative, and evidence gaps are named.
- Draft report, generated package, approval, and delivery are separate states.
- The next action says whether to gather evidence, generate, revise, approve, or deliver.

## Recovery Notes

- If input evidence is incomplete, mark the section as pending rather than fabricating a report claim.
- If delivery or attachment is unavailable, keep the report package prepared_not_observed.

## Use When

Turn supplied inputs into a report, executive brief, slide outline, or upload package without claiming delivery.

Strong routing signals: `report-package`, `report package`, `weekly report`, `monthly report`, `executive report`, `exec brief`, `leadership deck`, `status package`, `ppt outline`, `presentation outline`, `slide outline`, `upload package`, `보고서 패키지`, `주간 보고서`, `월간 보고서`, `경영진 보고`, `리더십 보고`, `PPT`, `피피티`, `슬라이드`, `발표자료`, `업로드 패키지`

## Catalog Metadata

Category: `reporting`
Phase: `package-outline`
Host-owned workflow responsibility
Quality tier: `report-gated`

Quality bar:

- Name audience, reporting period, sections, supplied facts, assumptions, and missing data.
- Keep report packaging independent from reliability review unless explicitly requested.
- Export only Markdown/JSON outlines unless a separate presentation tool produces a binary deck.

Handoff policy:

Turn supplied inputs into a report, executive brief, slide outline, or upload package without claiming delivery. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- audience
- reporting period or scope
- supplied facts
- missing data or assumptions

Expected outputs:

- report package
- PPT-ready Markdown or JSON outline
- assumptions and missing-input list

Artifact expectations:

- operation_artifact/v1 report-package artifact when a wrapper or CLI records it

Safety rules:

- Do not claim source review completion from a prepared report package.
- Do not claim stakeholder approval or presentation delivery without observed evidence.
- Do not couple report packages to SLO, incident, or error-budget evidence by default.

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
