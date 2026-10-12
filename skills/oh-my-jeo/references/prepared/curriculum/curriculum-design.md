# Prepared guidance: curriculum-design

Family: `curriculum`<br>
Category: `planning`<br>
Phase: `curriculum-design`<br>
Role: `planner`

## Contract
[omh] Team training or course that needs a syllabus: turn a learning goal into a teachable curriculum, assessment plan, and learner-ready sequence. Use when the user says: curriculum design, learning objectives, assessment plan, 커리큘럼 설계, 학습 목표, 평가 계획.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- curriculum design
- learning objectives
- assessment plan
- 커리큘럼 설계
- 학습 목표
- 평가 계획

## Required inputs
- learners
- learning goal
- prerequisites
- constraints

## Expected outputs
- curriculum_learner_outcome_brief/v1
- curriculum_alignment_map/v1
- curriculum_sequence_design/v1
- curriculum_validation_disposition/v1

## Artifact expectations
- prepared curriculum design brief when a wrapper captures it

## Acceptance criteria
- The plan names goals, non-goals, assumptions, acceptance criteria, and verification shape.
- Draft recommendations, accepted decisions, and executor handoffs are separate states.
- Rejected options or unresolved tradeoffs are recorded before handoff.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes designs an instructional plan; it does not create an LMS course, enroll learners, grade submissions, certify learning, publish materials, or claim learning outcomes occurred.

## Catalog rules
- quality_tier: planning-gated
- contract_source: skills/omh-curriculum-design/SKILL.md:65
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: Procedure: load `references/procedure.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-curriculum-design/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-curriculum-design/SKILL.md`
- SHA256: `b875809f5ca70f5ac59274e4ec520b16ad19457151c6a1f0799de810335c2e06`

## Method references
- `omh-curriculum-design/references/procedure.md` (pinned `skills/omh-curriculum-design/references/procedure.md`)

## Source gaps
- The source names `references/procedure.md`; retain the verified source method only and do not infer an OMJ provider or runtime from it.

## Blocked prerequisites
- Required source input: learners
- Required source input: learning goal
- Required source input: prerequisites
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for curriculum-design: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
