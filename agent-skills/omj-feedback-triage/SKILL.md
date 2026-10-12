---
name: omj-feedback-triage
description: [omj] Cluster feedback, bugs, and feature requests before choosing research, planning, or an accepted coding handoff.
metadata:
  omj:
    portability: portable
    category: triage
    phase: feedback
---

# Feedback Triage

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`feedback-triage` makes this workflow explicit: Cluster feedback, bugs, and feature requests before choosing research, planning, or an accepted coding handoff.

## Do Not Use When

- The request already contains an accepted product decision and asks for implementation.
- There are no feedback items, source boundary, or product area to classify.
- The user wants current market research rather than triage of supplied signals.

## Examples

Good example:

- Prompt: Cluster these customer payment failure reports and feature requests before we plan fixes.
- Expected behavior: Cluster bug signals and feature asks, rank severity or opportunity, and recommend research, planning, or coding as a next workflow.
- Why: The input is mixed feedback that needs classification before delivery decisions.

Bad example:

- Prompt: feedback-triage implement the accepted billing fix now.
- Expected behavior: Route to planning or coding handoff instead of re-triaging.
- Why: The decision is already accepted, so triage would add delay without improving evidence.

## Completion Checklist

- The source boundary, signal clusters, severity, and follow-up lane are named.
- Bug, feature, research, strategy, and coding handoff outcomes stay separate.
- The next workflow is recommended before any implementation claim.

## Recovery Notes

- If feedback lacks source or severity, ask for the missing signal before coding handoff.
- If the item is actually a plan or research request, route to that workflow instead of triage.

## Use When

Cluster feedback, bugs, and feature requests before choosing research, planning, or an accepted coding handoff.

Strong routing signals: `feedback-triage`, `customer-feedback-triage`, `feedback triage`, `customer feedback`, `feedback cluster`, `bug or feature`, `feature request triage`, `payment failure feedback`, `feedback trends`, `payment failure`, `payment failure issue`, `payment failure reports`, `고객 피드백`, `피드백`, `피드백 분류`, `피드백을 모아서`, `결제 실패`, `결제 실패 이슈`, `결제 실패 피드백`, `결제 오류`, `고객 불만`, `버그 제보`, `버그 기능 요청`, `기능 요청`

## Catalog Metadata

Category: `triage`
Phase: `feedback`
Host-owned workflow responsibility
Quality tier: `triage-gated`

Quality bar:

- Name the source boundary before clustering feedback.
- Classify signals into bug, feature, research, or strategy follow-up without overclaiming evidence.
- Recommend the next workflow instead of jumping straight to coding.

Handoff policy:

Cluster feedback, bugs, and feature requests before choosing research, planning, or an accepted coding handoff. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- feedback items or summary
- source boundary
- product area

Expected outputs:

- clusters
- severity or opportunity ranking
- next workflow recommendation

Artifact expectations:

- feedback triage record when a wrapper captures it

Safety rules:

- Do not turn feedback into a roadmap, implementation plan, or coding handoff by default.
- Separate bug signal, feature ask, severity, opportunity, and missing evidence.
- Route code changes only after explicit user intent or accepted planning evidence.

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
