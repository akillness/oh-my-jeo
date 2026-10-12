---
name: omj-ultraprocess
description: [omj] Carry one accepted task through source research, reviewed planning, selected implementation, review, and PR preparation.
metadata:
  omj:
    portability: portable
    category: process
    phase: single-cycle-plan-to-pr
---

# Ultraprocess

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ultraprocess` makes this workflow explicit: Carry one accepted task through source research, reviewed planning, selected implementation, review, and PR preparation.

## Do Not Use When

- The user wants an open-ended feedback loop or long-horizon campaign; use `loop` instead.
- The task is still ambiguous enough that a deep interview is required before planning.
- No repo, product, or delivery surface is available to support a plan-to-PR cycle.

## Examples

Good example:

- Prompt: $ultraprocess research this setup bug, plan the fix, implement, review, sync docs, and prepare a PR.
- Expected behavior: Run exactly one delivery cycle and report which stages are observed, prepared, or blocked.
- Why: The user explicitly asks for the full but bounded delivery path ending at PR readiness.

Bad example:

- Prompt: $ultraprocess keep improving the project until it becomes popular.
- Expected behavior: Route to `loop` or ask for a bounded goal rather than promise endless delivery.
- Why: Popularity and indefinite improvement need long-horizon loop management, not one PR-ready cycle.

## Completion Checklist

- Research and codebase context are captured before implementation handoff.
- A ralplan-style or reviewed plan names acceptance criteria, risks, and verification commands.
- The implementation owner is selected and handoff, dispatch, run, review, CI, and PR readiness are separated.
- The code-review gate is observed or explicitly marked not_observed.
- Docs sync is checked when behavior, setup, commands, examples, or public claims changed.
- An in-scope reversible Ruling records the decision, reason, and cost-if-wrong before execution.
- The four tests-first questions have meaningful answers, and independent review rounds remain within the cap with fresh evidence.

## Recovery Notes

- If the task expands beyond one delivery cycle, stop and route to loop with the current evidence as input.
- If no implementation owner is selected, keep the work prepared_not_observed and ask for an available coding owner.
- If review, CI, docs sync, or PR evidence is missing, report the stage gap instead of saying the process is complete.
- If the Ruling, tests-first answers, fresh reviewer, or review cap is missing, keep execution blocked and name the exact gate.

## Use When

Carry one accepted task through source research, reviewed planning, selected implementation, review, and PR preparation.

Strong routing signals: `ultraprocess`, `$ultraprocess`, `./ultraprocess`, `/ultraprocess`, `single-cycle delivery`, `one-cycle delivery`, `end-to-end process`, `delivery process`, `research plan implement review docs pr`, `plan implement review docs pr`, `ralplan ultragoal code-review`, `codebase source research planning implementation review docs sync pr`, `docs sync`, `pr-ready`, `prepare a pr`, `sync docs and prepare a pr`, `code-review sync docs and prepare a pr`, `delegate to codex`, `send to codex`, `codex implement`, `codex progress tracking`, `codex session tracking`, `make a pr`, `open a pr`, `끝까지 해줘`, `PR까지`, `계획 구현 리뷰 문서 PR`, `기획 구현 리뷰 문서 PR`, `코드베이스 조사 웹리서치 계획 구현 리뷰 문서 최신화 PR`, `codex로 구현`, `코덱스로 구현`, `codex에게 맡기`, `codex로 맡기`, `코덱스에게 맡기`, `코딩 에이전트에게 맡기`, `구현하게 맡기고 진행상태 추적`, `진행상태 추적`, `진행 상태 추적`, `문서 최신화 PR`

## Catalog Metadata

Category: `process`
Phase: `single-cycle-plan-to-pr`
Host-owned workflow responsibility
Quality tier: `process-gated`

Quality bar:

- Complete exactly one plan-to-PR delivery cycle, then stop with status, evidence gaps, or a next recommended workflow.
- Start with codebase/source research and a ralplan-style decision record before implementation handoff.
- Use ultragoal or the selected executor/runtime path for implementation, with acceptance criteria and verification commands attached.
- Run code-review as a gate after implementation evidence exists; review preparation alone is not review evidence.
- Add docs-specialist sync when public behavior, commands, setup, examples, or claims changed.
- End with a PR-ready or PR-observed report that separates prepared, executed, reviewed, verified, CI, and PR evidence.

Handoff policy:

Carry one accepted task through source research, reviewed planning, selected implementation, review, and PR preparation. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- task statement
- repo or workspace context
- executor preference or choose-at-handoff policy
- verification expectations

Expected outputs:

- ralplan-ready context and plan
- ultragoal or selected executor/runtime handoff
- code-review gate
- docs sync checklist
- single-cycle PR-ready summary with observed evidence and gaps

Artifact expectations:

- process checklist or runtime record when a wrapper can observe the stages
- prepared handoff artifact only after implementation owner selection
- docs-specialist claim check when public behavior changes

Safety rules:

- Do not skip planning when the request is broad, risky, or user-visible.
- Do not continue into a repeated feedback loop; recommend `loop` when the user wants ongoing cycles.
- Do not claim implementation, review, CI, merge readiness, or PR creation without observed executor or GitHub evidence.
- Keep web research source-backed and permission-aware; do not run hidden network or LLM calls from OMJ core.
- Run docs sync only when behavior, setup, commands, or public claims changed.

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
