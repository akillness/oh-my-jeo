# OMJ Spec-First Workflow Pipeline

This document records what the `jeo-code` agent harness does well in its
workflow and system-prompt design, compares it with OMJ's routing-and-evidence
catalog, and defines the strengthened OMJ spec-first staged pipeline that adopts
the missing disciplines.

OMJ remains a **routing and evidence-boundary guidance layer for Hermes chat**,
not a hidden executor. The pipeline below is a prepared contract Hermes can
follow; observed runtime evidence still gates every status advance.

## 1. What jeo-code's workflow does well

`jeo-code` is an execution harness whose bundled skills form one linear,
verified pipeline, and whose subagent system prompts use strict contracts.

Pipeline:


deep-dive ─▶ deep-interview ─▶ ralplan ─▶ team ─▶ ultragoal
(trace root    (Socratic         (planner+   (per-task   (verify acceptance
 cause, 3      ambiguity gate,    architect+  executor    criteria + evidence
 parallel      freeze immutable   critic       loop)       report)
 lanes)        seed at ≤0.2)      blueprint)


Distinctive strengths:

1. **Quantified ambiguity gate.** `deep-interview` does not leave clarity to
   feel; it scores ambiguity (Goal/Constraints/Success weighting) and freezes a
   seed only at **ambiguity ≤ 0.2**.
2. **Immutable seed/spec.** Requirements become a frozen contract; planning and
   execution read the seed, not a moving target.
3. **Multi-role planning that preserves disagreement.** `ralplan` runs planner,
   architect, and critic and explicitly does **not collapse contested decisions
   to one verdict** — it records competing options and flags human judgment
   calls.
4. **Per-task execution discipline.** `team`/executor decompose work into
   **ordered subgoals, verify one before the next, and feed the facts a failed
   task exposes into the next attempt** instead of retrying unchanged.
5. **Severity-rated review with an evidence floor.** Architect/critic rate
   findings `CRITICAL/HIGH/MEDIUM/LOW`, never `APPROVE` with an open
   CRITICAL/HIGH, and treat **"a clean verdict is not the absence of
   inspection"** — a no-issue verdict must name the files actually examined.
6. **Structured verdict tokens + read-only/write separation.** Critic returns
   `[OKAY]/[ITERATE]/[REJECT]`, architect returns `CLEAR/WATCH/BLOCK` plus
   `APPROVE/COMMENT/REQUEST CHANGES`; non-mutating agents never get mutating
   tools; every agent has an explicit `output_contract`.

## 2. Where OMJ already matched it

OMJ was already strong on evidence discipline that jeo-code states more
implicitly:

- **Prepared vs observed vs blocked** state separation and overclaim guards on
  every skill (`SkillDefinition.safety_rules`, `quality_bar`, `final_checklist`).
- A **role taxonomy** (`src/catalogs/roles.py`) with per-role evidence
  boundaries.
- **Orchestration patterns** (`docs/ORCHESTRATION_PATTERNS.md`):
  `clarify_then_plan`, `plan_execute_verify`, `adversarial_review`,
  `team_staged_pipeline` — the building blocks of a staged pipeline.
- A `deep-interview` clarification skill and `ralplan` consensus-planning skill
  that already record rejected options and unresolved tradeoffs.

## 3. Gaps closed in this change

| jeo-code discipline | OMJ before | OMJ after |
| --- | --- | --- |
| Quantified ambiguity gate | "stop once ambiguity is low enough" (qualitative) | `deep-interview` now stops and **freezes an immutable seed at ambiguity ≈ 0.2 or less**; planner role owns the same threshold |
| Immutable seed | implicit "clarified brief" | `deep-interview` emits a **frozen requirements seed**; planner role freezes it so planning reads a frozen contract |
| Disagreement preservation | "rejected options recorded" | planner role keeps **contested decisions explicit with competing options and a human judgment-call flag** |
| Subgoal + failure feed-forward | not stated | handoff-guide role owns **ordered subgoals, verify-one-before-next, feed failure lessons forward** |
| Severity ratings + evidence floor | "findings ranked by severity" (review skill) | reviewer role owns **CRITICAL/HIGH/MEDIUM/LOW findings, never clears an open CRITICAL/HIGH, and names the files actually inspected** |
| Structured verdict tokens | review/QA skills returned prose verdicts | reviewer role owns a **structured terminal verdict — `CLEAR/WATCH/BLOCK` for readiness and `APPROVE/COMMENT/REQUEST-CHANGES` for review — where `APPROVE` is review-approved, not merged, and an open CRITICAL/HIGH forces BLOCK or REQUEST-CHANGES** |

These live in `src/catalogs/roles.py` (planner, reviewer, handoff-guide) and the
`deep-interview` skill in `src/skills/catalog.py`, and regenerate into
`roles/*.md`, `docs/ROLES.md`, `docs/WORKFLOWS.md`, and the bundled references.

## 4. The strengthened OMJ pipeline


clarify ─▶ seed ─▶ plan ─▶ execute ─▶ verify ─▶ complete


| Stage | OMJ skill(s) | Owner role | Gate before advancing |
| --- | --- | --- | --- |
| **Clarify** | `deep-interview`, `feedback-triage` | planner | One blocking question per turn; discoverable repo facts gathered first |
| **Seed** | `deep-interview` output | planner | **Ambiguity ≈ 0.2 or less**, then freeze an immutable requirements seed with acceptance criteria |
| **Plan** | `plan`, `ralplan` | planner | Goals/non-goals/acceptance/verification named; contested decisions kept explicit, not collapsed |
| **Execute** | `team`, `loop`, `ralph`, executor/runtime handoff | handoff-guide | Ordered subgoals, verify one before next, feed failure lessons forward; observed runtime evidence per lane |
| **Verify** | `code-review`, `ultraqa` | reviewer | Severity-rated findings; no clean verdict without naming inspected files; never clear an open CRITICAL/HIGH; emit a structured `CLEAR/WATCH/BLOCK` (or `APPROVE/COMMENT/REQUEST-CHANGES`) verdict |
| **Complete** | `ultragoal`, completion status | handoff-guide / reviewer | Acceptance criteria checked against observed evidence, not narration |

Orchestration-pattern mapping: `clarify_then_plan` covers Clarify→Seed→Plan,
`plan_execute_verify` covers Plan→Execute→Verify, `team_staged_pipeline` covers
multi-lane Execute, and `adversarial_review` covers the Verify gate.

## 5. Evidence rule (unchanged)

Every stage above is prepared guidance. A frozen seed, a plan, a prepared
handoff, or a review card is **not** execution, dispatch, CI, merge, or delivery
evidence. Status only advances from prepared to observed when a wrapper or
operator records matching runtime evidence — the same contract enforced across
the rest of OMJ.
