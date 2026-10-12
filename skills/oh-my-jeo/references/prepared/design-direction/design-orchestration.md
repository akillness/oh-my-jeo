# Prepared guidance: design-orchestration

Family: `design-direction`<br>
Category: `materials`<br>
Phase: `design-orchestration`<br>
Role: `operator`

## Contract
[omh] Entire product design problem to delegate: prepare a bounded design direction, existing-lane composition, and executor-neutral handoff. Use when the user says: design-orchestration, design orchestration, design ownership, handle this product design, take on the design, デザインを任せる, デザイン全体を任せ, プロダクトデザインを任せ.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- design-orchestration
- design orchestration
- design ownership
- handle this product design
- take on the design
- デザインを任せる
- デザイン全体を任せ
- プロダクトデザインを任せ
- 디자인 맡겨
- 디자인 맡겨줘
- 디자인 전체 맡겨
- 프로덕트 디자인 맡겨
- 设计交给你
- 整体设计交给你
- 产品设计交给你

## Required inputs
- bounded target surface, audience, and primary task
- at least one opaque project, user, or Hermes context reference
- direction vocabulary and avoid-pattern selection
- executor selection and observed visual evidence remain pending

## Expected outputs
- design_orchestration/v1
- design_direction_set/v1 when the direction is still open
- design intent and opaque context-reference boundary
- prepared direction vocabulary
- downstream composition: design-quality-gate, frontend, accessibility-audit, visual-qa
- executor-neutral handoff with executor_selection_required
- visual evidence requirements with visual_verdict not_observed

## Artifact expectations
- design_orchestration/v1 with prepared_not_observed status
- design_direction_set/v1 offers two to four directions with chosen_option empty until the user picks
- a static self-contained preview file when one is written; no server, port, or browser launch
- no raw project source, prompt, asset, path, or URL retention
- no executor target, dispatch, implementation, render, QA PASS, review, CI, deployment, or merge claim

## Acceptance criteria
- The bounded intent, opaque context references, direction vocabulary, and avoid patterns are explicit.
- The four downstream lanes retain their direct ownership and the executor is still selection-required.
- The visual evidence contract keeps visual_verdict not_observed until fresh captures are recorded by the visual-QA owner.

## Handoff policy
Keep design intent, opaque project context references, deliberate direction, and existing-lane composition in Hermes; prepare an executor-neutral handoff only. The selected executor owns implementation, while existing visual-QA and web-QA paths own observed rendered evidence.

## Catalog rules
- quality_tier: design-orchestration-gated
- contract_source: skills/omh-design-orchestration/SKILL.md:65
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Reject generic default drift by naming hierarchy, palette, typography, layout, signature element, and avoid patterns deliberately — the direction vocabulary and anti-slop patterns live in the frontend skill's `omh-frontend/references/taste-foundations.md`; prepared directions inherit its named bar (technically clean but flat fails).
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-design-orchestration/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-design-orchestration/SKILL.md`
- SHA256: `f8389ac4733637a875545e3bc21215bc7b04628b856be0869302d3ed13c0219e`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: bounded target surface, audience, and primary task
- Required source input: at least one opaque project, user, or Hermes context reference
- Required source input: direction vocabulary and avoid-pattern selection
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for design-orchestration: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
