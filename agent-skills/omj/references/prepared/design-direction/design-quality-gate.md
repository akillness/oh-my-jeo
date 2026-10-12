# Prepared guidance: design-quality-gate

Family: `design-direction`<br>
Category: `materials`<br>
Phase: `design-quality-gate`<br>
Role: `operator`

## Contract
[omh] Deliverable demands premium polish: enforce superior content, design, layout, publishing, and visual QA gates. Use when the user says: design-quality-gate, design quality gate, ui ux pro max, design pro max, frontend pro max, visual qa pro, premium design, high quality design.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- design-quality-gate
- design quality gate
- ui ux pro max
- design pro max
- frontend pro max
- visual qa pro
- premium design
- high quality design
- beautiful website
- frontend publishing
- publishing quality
- layout validation
- ppt design quality
- pdf design quality
- デザイン品質ゲート
- 公開品質のデザイン
- デザインの品質基準
- 웹사이트 디자인
- 프론트엔드 퍼블리싱
- 레이아웃 검증
- 더 뛰어나게
- 고퀄
- 设计质量门禁
- 发布级设计
- 设计质量标准

## Required inputs
- surface/channel
- audience and purpose
- source content or gaps
- style references
- ordinary-output baseline or competitor/reference quality bar
- viewport/page/export constraints
- observed render QA for completion claims

## Expected outputs
- design_quality_gate/v1
- content_quality_review/v1
- surface_quality_matrix/v1
- comparative_quality_rubric/v1
- layout_validation_plan/v1
- visual_qa_evidence/v1 when observed
- publishing_readiness/v1
- downstream route: frontend, materials-package, img-summary, or deliverable-package

## Artifact expectations
- design_quality_gate/v1 when prepared
- surface_quality_matrix/v1 with web: responsive viewport, deck/PPT: slide rhythm, PDF/poster: print-safe, and accessibility/CJK checks
- comparative_quality_rubric/v1 that names how this should be better than ordinary output
- visual_qa_evidence/v1 only from fresh screenshots/renders/observations
- export/publish evidence only when observed

## Acceptance criteria
- The surface, audience, source content, baseline/reference bar, and artifact type are named.
- The comparative_quality_rubric/v1 explains how the result must beat ordinary output.
- The surface_quality_matrix/v1 covers web, deck/PPT, PDF/poster, accessibility, and CJK-relevant checks as applicable.
- Prepared quality gates, generated artifacts, visual QA, export, publication, approval, and delivery remain separate states.
- The next action names whether to revise content, prepare implementation/export handoff, gather render evidence, or report blocked QA.

## Handoff policy
Keep the quality brief, reference selection, design rubric, content-structure review, and QA checklist in Hermes; delegate implementation or binary generation only after the surface, owner, references, and observed QA path are explicit.

## Catalog rules
- quality_tier: design-pro-gated
- contract_source: skills/omh-design-quality-gate/SKILL.md:68
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Define superior design quality with references, audience, hierarchy, style, and measurable QA gates. The bar is named, not relative: what a senior product designer at a top-tier product company (the Linear/Stripe/Supabase class) would sign off on — technically clean but flat output fails it. Load `references/design-critique-rubric.md` and judge every axis with named evidence.
- Catalog Metadata: - Require references/rubric plus fresh render QA before PASS.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-design-quality-gate/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-design-quality-gate/SKILL.md`
- SHA256: `b7f5fe57565af02b4daaf62392985a6307218c5e3f16405cf640caea45d11350`

## Method references
- `design-quality-gate/omh-design-quality-gate/references/design-critique-rubric.md` (pinned `skills/omh-design-quality-gate/references/design-critique-rubric.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: surface/channel
- Required source input: audience and purpose
- Required source input: source content or gaps

## Evidence boundary
prepared_not_observed for design-quality-gate: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
