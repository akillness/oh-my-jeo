---
name: omj-agent-ops-review
description: [omj] Explain agent progress, blockers, gates, throughput, and bounded read-only session evidence without claiming unseen work.
metadata:
  omj:
    portability: requires-omj-cli
    category: operator
    phase: manager-review
---

# Agent Ops Review

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`agent-ops-review` makes this workflow explicit: Explain agent progress, blockers, gates, throughput, and bounded read-only session evidence without claiming unseen work.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMJ to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: agent-ops-review inspect a bounded session read-only, separate source roles, and prepare an export for my review.
- Expected behavior: Produce `prepare_agent_ops_review` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface without hiding execution.

Bad example:

- Prompt: agent-ops-review post the diagnosis to an issue because I agreed with it.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMJ guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The session/turn range, expected behavior, observed behavior, and one observable are bounded before reads.
- Forensics are read-only, capped, source-role and authorship aware, and partial counts are labelled rather than inferred.
- Exports are prepared only; exact text of third-party content is shown and separately approved before any send.
- Load `references/session-forensics.md` for read-only source-role, exact-text approval, and leak-aware export.

## Recovery Notes

- If the requested range or observable is missing, ask for that boundary instead of reading an unbounded session.
- If replay, reset, mutation, or export writing is requested, stop for its separate user approval and keep diagnosis read-only.
- If source-role or count evidence is capped, report the partial result and gap rather than infer a complete timeline; leak scanning is not guaranteed even when approved.

## Use When

Explain agent progress, blockers, gates, throughput, and bounded read-only session evidence without claiming unseen work.

Strong routing signals: `agent-ops-review`, `agent-debug`, `agent ops review`, `agent productivity`, `operator productivity`, `manager view`, `quality dashboard`, `throughput review`, `agent work quality`, `coding progress quality`, `coding progress`, `codex progress`, `codex status`, `coding agent status`, `where is codex`, `research coding review status`, `ai agent manager`, `third-party manager`, `session forensics`, `debug session`, `bounded session`, `관리자 입장`, `Codex 작업`, `Codex 작업이 어디까지`, `코덱스 작업`, `작업이 어디까지`, `진행됐는지`, `진행되었는지`, `작업 생산량`, `처리량`, `품질 퀄리티`, `작업 품질`, `진행상황`, `리서치 코딩 리뷰`

## Catalog Metadata

Category: `operator`
Phase: `manager-review`
Host-owned workflow responsibility
Quality tier: `workflow-surface-gated`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Explain agent progress, blockers, gates, throughput, and bounded read-only session evidence without claiming unseen work. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- agent-ops-review/v1 card or guidance
- next action
- prepared-vs-observed boundary

Artifact expectations:

- agent-ops-review/v1 metadata-only runtime or wrapper card when recorded

Safety rules:

- An agent ops review card is not source retrieval, executor dispatch, coding progress, implementation, review, verification, CI, merge-readiness, merge, platform delivery, provider billing, or live runtime telemetry evidence.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

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
[Source-owned procedural guidance](references/procedures/agent-ops-review.md)
