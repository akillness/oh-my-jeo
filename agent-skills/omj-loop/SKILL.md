---
name: omj-loop
description: [omj] Cycle through interview, planning, research, building, and independent review until a real acceptance gate.
metadata:
  omj:
    portability: requires-omj-cli
    category: goal-loop
    phase: continuous-goal-loop
---

# Loop

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`loop` makes this workflow explicit: Cycle through interview, planning, research, building, and independent review until a real acceptance gate.

## Do Not Use When

- The user asks for one bounded delivery cycle; use `ultraprocess` or `ultragoal` instead.
- The user gives only a north-star outcome such as revenue, stars, or adoption and has not accepted a bounded first loop goal.
- The goal is too vague to name an observable problem, next artifact, verification signal, or stop condition.
- The goal depends mainly on external waiting, adoption, revenue, or community response without observable local next actions.
- The permission profile does not allow repeated research, handoff, queue, or feedback cycles.

## Examples

Good example:

- Prompt: loop improve the explicitly selected workflow pack through install, docs, QA, and feedback cycles.
- Expected behavior: Start a permission-scoped loop, maintain loop_cycle/v1 state, choose the next concrete task, and keep external outcomes as waiting states.
- Why: The request is long-horizon and needs repeated discovery, verification, feedback, and resume decisions.

Bad example:

- Prompt: ./loop merge this already reviewed one-line README fix.
- Expected behavior: Use a direct delivery or PR workflow instead of starting a persistent loop.
- Why: The task is bounded and should stop after merge evidence rather than create ongoing cycles.

## Completion Checklist

- The request is classified as task, project, north-star ambition, external-wait, or unclear before a loop starts.
- The current loop_status_card/v1 names the queue item, tick status, verification_plan, and next action.
- failure_mode_summary checks verification_gap, comprehension_debt, cognitive_surrender, and stalled_repetition before progress advances.
- Completion is backed by linked goal/runtime evidence; queued loop ticks alone are not observed work.
- A machine-decidable finish line, fenced paths, independent judge, prior approval for self-rule edits, and bounded acceptance-failure policy are recorded.
- Keep a per-item retry cap, require human approval before any self-rule edit, never self-grade loop completion, and stop rather than leave an unjudged item marked done.

## Recovery Notes

- If a queued tick is pending, show it as prepared queue state and use loop status/run-once before claiming progress.
- If feedback is unclear, ask one gate question or route back to research/plan rather than advancing the loop.
- If the goal turns into external waiting, record the waiting state and next observable signal instead of continuing locally.
- If context or budget is exhausted, checkpoint the loop artifact and continue from the latest loop_cycle/v1 state.
- If the finish line, fence, judge, or prior approval is missing, stop at prepared_not_observed and request the missing gate.

## Use When

Cycle through interview, planning, research, building, and independent review until a real acceptance gate.

Strong routing signals: `loop`, `./loop`, `$loop`, `goal loop`, `long horizon goal`, `never stop`, `research plan ultragoal feedback`, `token exhaustion resume`, `permission profile`, `star 10k`, `10k star`, `loop engineering`, `루프`, `목표 루프`, `장기 목표`, `끝까지`, `토큰 고갈`, `피드백 루프`

## Catalog Metadata

Category: `goal-loop`
Phase: `continuous-goal-loop`
Host-owned workflow responsibility
Quality tier: `loop-gated`

Quality bar:

- Treat direct `loop`, `./loop`, `$loop`, and OMJ invocations as start/continue, not pickers. Classify task/project/ambition/external-wait/unclear; reach real permission/evidence/verification/context/budget/wait gates.
- Expose interviewer/planner/researcher/builder/reviewer/loop-controller roles. Tiny tasks use one-cycle delivery. Reframe north-star ambition as bounded arena/observable problem/next goal/verification; never shrink ambition.
- Separate discovery/distribution/execution/verification/next-task/queue/ultragoal-handoff/feedback/wait/resume. Permission profile precedes dispatch/mutation/PR/merge/publication.
- Show automation/worktree/skill/connector/subagent states; separate prepared plans, observed executor work, linked goal completion, and external waits.
- Single-step/fan-out-and-synthesize/adversarial/tournament/triage patterns are metadata only. Keep scaffolds stable and summaries bounded; verifier lanes require risk or evidence.
- Use cheap inner-loop checks often, expensive outer-loop checks sparingly. Small-loop recipe: test as stop signal, plan -> execute -> verify, one task at a time.
- Warn on verification_gap, comprehension_debt, cognitive_surrender, and stalled_repetition before apparent self-steering.
- Require a machine-decidable finish line, fenced paths, independent judge and per-item retry cap. Human approval precedes self-rule edits; never self-grade. Stop at bounded acceptance failures; never mark unjudged items done.

Handoff policy:

Cycle through interview, planning, research, building, and independent review until a real acceptance gate. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- loopability assessment
- north-star goal summary when present
- bounded arena
- observable problem
- next verification
- goal reframe
- success criteria
- permission profile
- feedback or wait signal

Expected outputs:

- loopability_assessment/v1 task/project/ambition classification
- loop_start_card/v1 setup prompt
- loop_cycle/v1 state
- loop_engineering/v1 pipeline/building-block snapshot
- loop verification_policy for inner/outer checks
- loop failure_mode_summary over verification gap, comprehension debt, and cognitive surrender
- small-loop guidance: test as stop signal, plan -> execute -> verify, one task at a time
- loop_status_card/v1 next action
- loop_runtime/v1 queued tick with verification_plan refs
- loop_queue_handoff/v1 only when permitted
- executor-neutral handoff only when permitted
- external-wait or checkpoint boundary

Artifact expectations:

- metadata-only .omj/loops loop_cycle/v1 artifact with loopability_assessment/v1
- loop_engineering/v1 status over automation, worktree, skill, connector, subagent, verification policy, and failure modes
- loop_runtime/v1 queue entries with context_policy_ref, cost_policy_ref, and verification_plan
- loop_subagent_result_contract/v1 for prepared subagent handoffs
- loop_status_card/v1 wrapper payload with loopability_assessment, failure_mode_summary, and small_loop_guidance
- loop_start_card/v1 wrapper setup card
- linked goal_ledger/v1 only when completion evidence is required

Safety rules:

- Loop persistence never bypasses the selected permission profile.
- Runtime ticks are not evidence of worktree creation, subagent dispatch, connector I/O, implementation, review, CI, merge, publication, or completion.
- Require linked goal_ledger/v1 completion evidence, not loop state.
- Checkpoint/resume when context or token budget runs out; never claim completion.
- Market response, stars, and adoption stay waiting unless observed.
- Missing/failed verification returns to plan/research or waits; never bypass it.
- Green-looking status never hides comprehension debt or cognitive surrender.

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
[Source-owned procedural guidance](references/procedures/loop.md)
