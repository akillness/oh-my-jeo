---
name: loop
description: [omj] Hermes Loop workflow: agentic interviewer -> planner -> researcher -> builder -> reviewer cycles until a real gate.
metadata:
  hermes:
    tags: [workflow, oh-my-jeo, goal-loop]
    category: goal-loop
    phase: continuous-goal-loop
    role: planner
    quality_tier: loop-gated
---

# Loop

This is a Hermes-native `loop` workflow skill.

## Why This Exists

`loop` exists for goals whose correct implementation cannot be known upfront but can be discovered through bounded cycles of definition, action, verification, and revision without confusing planned cycles with observed progress.

## Do Not Use When

- The user asks for one bounded delivery cycle; use `ultraprocess` or `ultragoal` instead.
- The user gives only a north-star outcome such as revenue, stars, or adoption and has not accepted a bounded first loop goal.
- The goal is too vague to name an observable problem, next artifact, verification signal, or stop condition.
- The goal depends mainly on external waiting, adoption, revenue, or community response without observable local next actions.
- The permission profile does not allow repeated research, handoff, queue, or feedback cycles.

## Examples

Good example:

- Prompt: ./loop make OMJ a credible Hermes workflow pack with install, docs, QA, and feedback cycles.
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

## OMJ Context Rail

- This skill is part of OMJ's Hermes workflow layer, not a standalone executor.
- Product context: OMJ is a Hermes-native workflow pack: it helps Hermes choose skills, shape work, prepare artifacts, show status, and hand off with observed evidence boundaries.
- Current lane: **Intent -> plan** (`oh-my-jeo`, `deep-interview`, `plan`, `ralplan`, `ultragoal`, `ultraprocess`, `loop`, `ralph`, `performance-goal`) - ambiguous goals, plans, one-cycle delivery, durable goals, and loopable projects.
- If the user intent belongs to another OMJ lane, hand back to `oh-my-jeo` or name the adjacent workflow instead of force-fitting this skill.
- Cross-skill context: Across every OMJ skill: match intent to a lane, name adjacent workflows, and do not dismiss OMJ because a generic tool can render or execute.
- Generic-tool checkpoint: image->img-summary; supplied paper->paper-learning; file->materials-package; search->web-research; code->ultraprocess/ralplan/review.
- Coverage: Every generated workflow skill carries this rail.
- Normal users talk to Hermes; OMJ CLI is backend, setup, verification, and wrapper infrastructure.
- Boundary: Prepared OMJ routing, prompts, cards, handoffs, or artifacts are not observed execution, image generation, delivery, review, CI, merge-readiness, or merge evidence.

## Use When

Use for high-level goals or direct loop invocation; start/continue through interviewer, planner, researcher, builder, reviewer, and loop controller until a real gate.

    Strong routing signals: `loop`, `./loop`, `$loop`, `goal loop`, `long horizon goal`, `never stop`, `research plan ultragoal feedback`, `token exhaustion resume`, `permission profile`, `star 10k`, `10k star`, `loop engineering`, `루프`, `목표 루프`, `장기 목표`, `끝까지`, `토큰 고갈`, `피드백 루프`

## Catalog Metadata

Category: `goal-loop`
Phase: `continuous-goal-loop`
Hermes role: `planner`
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

Hermes owns loop roles, verification tiers, deterministic ticks, loop_engineering/v1 status, feedback, and permissions. Prepare concrete executor/runtime/worktree/connector/verifier handoffs; require linked completion evidence.

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

## Harness Discipline

- Start from the representative harness registry in `oh-my-jeo` when the workflow needs coding, research, planning, goal execution, architecture, critique, QA, or documentation lanes.
- Prefer richer evidence and clearer stop conditions over adding more workflow names.
- Use specialist lanes only when they change the quality of the answer or verification.

## Runtime Evidence

Preferred harness for this skill: `goal-loop`.

When local shell access or a bot wrapper is available, record metadata-only evidence:

```sh
omj runtime record --skill loop --harness goal-loop --status started
omj runtime delegate --run <run-id> --requested --not-observed --result not_observed
```

Record observed delegation results when Hermes or the wrapper exposes them. If delegation is unavailable, keep the result explicit as `not_available` or `not_observed`.

## Hermes Compatibility Contract

- Preserve the workflow intent, stop conditions, and verification discipline.
- Use Hermes-native tools, file operations, and subagent/delegation features when available.
- Do not require runtime tools, role prompts, or overlays that Hermes Agent does not expose.
- Respect `omj_target_topology/v1` when a wrapper reports it: bind state to the current target/thread, adapt only the parts of this workflow that benefit from multiple Hermes agents, and fall back to single-target behavior when `active_agent_count` is one.
- When target topology changes from one to many or many to one, give a concise setup-change comment or use the wrapper's apply action before treating the new topology as persistent.
- When wrapper metadata includes `memory_review_card/v1` or `handoff_context_pack/v1`, treat it as reviewed OMJ-local or wrapper-supplied context only. Use conflict-free context summaries to shape plans and handoffs, but do not claim Hermes internal memory was read or changed.
- When a runtime-specific mechanism appears in imported instructions, translate it to a Hermes-native artifact:
  - goal tools -> `.omj/goals/` ledgers, `goal_completion_gate/v1`, `goal_status_card/v1`, `goal_continuation/v1`, or explicit checklists with named next actions,
  - question renderers -> one concise question in the current Hermes interface,
  - native subagents -> Hermes delegation when available, otherwise sequential lanes,
  - shell bridge commands -> optional bridge mode only.

## Execution Rules

1. Load supporting context with `skills_list` / `skill_view` when needed.
2. State the workflow target, constraints, validation evidence, and stop condition.
3. Keep progress evidence-backed.
4. Verify with the smallest relevant test or inspection before claiming completion.
5. If Hermes cannot provide a required runtime capability, say so and use the fallback above.
