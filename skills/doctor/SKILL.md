---
name: doctor
description: [omj] Hermes adaptation for diagnosing oh-my-jeo installation health.
metadata:
  hermes:
    tags: [workflow, oh-my-jeo, operator]
    category: operator
    phase: diagnostics
    role: tracker
    quality_tier: evidence-gated
---

# Doctor

This is a Hermes-native `doctor` workflow skill.

## Why This Exists

`doctor` exists to turn confusing install/setup states into grouped, local health evidence and the next repair action without treating a check as a fix.

## Do Not Use When

- The user is asking for a general product explanation rather than local health diagnostics.
- The requested change is a repository bug fix, not an installed-environment check.
- The wrapper wants to claim Hermes reload, skill execution, or plugin behavior that was not observed.

## Examples

Good example:

- Prompt: doctor after omj update says setup is next but Hermes skills still look stale.
- Expected behavior: Inspect managed skills, Hermes registration, runtime state, and next repair action with explicit proof boundaries.
- Why: The issue is local installation health and needs grouped diagnostic evidence.

Bad example:

- Prompt: doctor implement a new uninstall command UX.
- Expected behavior: Route to planning or implementation instead of health diagnostics.
- Why: That is product development work, not a local health check.

## Completion Checklist

- Command availability, managed skills, Hermes registration, runtime state, and optional surfaces are grouped separately.
- Blocking issues and warnings are separated, with one next repair action named for each blocking area.
- Plugin install, plugin import/register smoke, and Hermes runtime load are not collapsed into one claim.
- The final status says whether setup/update/doctor repaired anything or only observed health.

## Recovery Notes

- If managed skills are stale, recommend omj update or omj setup depending on whether registration also needs repair.
- If skills.external_dirs or Hermes config is missing, route to setup repair rather than editing hidden runtime state.
- If plugin register smoke fails, reinstall the plugin bundle with setup --with-plugin --force before claiming plugin readiness.
- If omj is missing from PATH, use the installer-reported absolute command path and then re-run doctor.

## OMJ Context Rail

- This skill is part of OMJ's Hermes workflow layer, not a standalone executor.
- Product context: OMJ is a Hermes-native workflow pack: it helps Hermes choose skills, shape work, prepare artifacts, show status, and hand off with observed evidence boundaries.
- Current lane: **Automation and status** (`automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `toolbelt-readiness`, `ops-observability-card`, `agent-ops-review`, `memory-curation-review`, `workflow-learning`, `doctor`, `skill`, `ask`, `cancel`) - scheduled ops, gateway cards, boards, tool readiness, status, health, and release/ops review.
- If the user intent belongs to another OMJ lane, hand back to `oh-my-jeo` or name the adjacent workflow instead of force-fitting this skill.
- Cross-skill context: Across every OMJ skill: match intent to a lane, name adjacent workflows, and do not dismiss OMJ because a generic tool can render or execute.
- Generic-tool checkpoint: image->img-summary; supplied paper->paper-learning; file->materials-package; search->web-research; code->ultraprocess/ralplan/review.
- Coverage: Every generated workflow skill carries this rail.
- Normal users talk to Hermes; OMJ CLI is backend, setup, verification, and wrapper infrastructure.
- Boundary: Prepared OMJ routing, prompts, cards, handoffs, or artifacts are not observed execution, image generation, delivery, review, CI, merge-readiness, or merge evidence.

## Use When

Use to diagnose OMJ installation and Hermes config registration.

    Strong routing signals: `doctor`, `$doctor`, `diagnose omj`, `installation health`

## Catalog Metadata

Category: `operator`
Phase: `diagnostics`
Hermes role: `tracker`
Quality tier: `evidence-gated`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate Hermes guidance from executor or wrapper behavior unless evidence proves the step happened.

Handoff policy:

Run directly as local health inspection; propose executor work only when a repo fix is required.

Required inputs:

- omj home
- Hermes home
- observed issue

Expected outputs:

- health checks
- fix guidance
- known proof boundary

Artifact expectations:

- doctor state summary when runtime artifacts are writable

Safety rules:

- Do not imply hidden Hermes runtime behavior.
- Use the smallest verification that can prove the claim.

## Harness Discipline

- Start from the representative harness registry in `oh-my-jeo` when the workflow needs coding, research, planning, goal execution, architecture, critique, QA, or documentation lanes.
- Prefer richer evidence and clearer stop conditions over adding more workflow names.
- Use specialist lanes only when they change the quality of the answer or verification.

## Runtime Evidence

Preferred harness for this skill: `qa-specialist`.

When local shell access or a bot wrapper is available, record metadata-only evidence:

```sh
omj runtime record --skill doctor --harness qa-specialist --status started
omj runtime delegate --run <run-id> --requested --not-observed --result not_observed
```

Record observed delegation results when Hermes or the wrapper exposes them. If delegation is unavailable, keep the result explicit as `not_available` or `not_observed`.

## Hermes Compatibility Contract

- Preserve the workflow intent, stop conditions, and verification discipline.
- Use Hermes-native tools, file operations, and subagent/delegation features when available.
- Do not require runtime tools, role prompts, or overlays that Hermes Agent does not expose.
- Respect `omj_target_topology/v1` when a wrapper reports it: bind state to the current target/thread, adapt only the parts of this workflow that benefit from multiple Hermes agents, and fall back to single-target behavior when `active_agent_count` is one.
- When target topology changes from one to many or many to one, give a concise setup-change comment or use the wrapper's apply action before treating the new topology as persistent.
- Treat wrapper-supplied memory/context summaries as advisory local context, not proof that opaque Hermes memory was read or changed.
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
