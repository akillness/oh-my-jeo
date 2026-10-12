# Prepared guidance: apple-design

Family: `design-direction`  
Category: `materials`  
Phase: `apple-design`  
Role: `operator`

## Contract
[omh] Designing or reviewing an iOS, macOS, or Apple-style UI: prepare native Apple UI or Apple marketing product-visual direction, review, and improvement briefs with evidence-backed remediation handoffs. Use when the user says: apple-design, apple design, apple ui design, apple hig, human interface guidelines, ios design guidelines, macos app design, apple-inspired web.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- apple-design
- apple design
- apple ui design
- apple hig
- human interface guidelines
- ios design guidelines
- macos app design
- apple-inspired web
- liquid glass review
- liquid glass design
- apple 3d hero
- apple-style 3d
- apple product render
- apple product visual
- apple studio lighting
- apple-style landing visual
- apple product page

## Required inputs
- mode: design, review, or improve
- visual target: Apple marketing/product visual, native Apple application, or Apple-inspired web UI
- target, surface/state, supplied evidence, and available execution constraints

## Expected outputs
- apple_design_brief/v1
- apple_visual_direction/v1
- apple_design_finding/v1 with severity, location/evidence, impact, source/applicability, fix, owner, and missing checks
- two to four design directions before visual work when direction is open
- composed remediation route to frontend, design-quality-gate, accessibility-audit, visual-qa, or award-bar-score

## Artifact expectations
- prepared Apple design brief with observations and hypotheses distinguished
- prepared product-visual handoff when no authorized execution path exists
- visual status not_observed when no supplied screen, capture, or rendered surface exists
- no Apple certification, accessibility PASS, visual PASS, or implementation claim from a prepared brief

## Acceptance criteria
- Target, convention, state, and evidence are explicit.
- Each direction or finding names evidence, source applicability, owner, and missing verification; product visuals name original art direction.
- Implementation remains with the selected coding owner; accessibility and visual completion remain not_observed until their existing lanes record evidence.

## Handoff policy
Hermes directs; selected owners implement and existing lanes observe.

## Catalog rules
- quality_tier: apple-design-gated
- contract_source: skills/omh-apple-design/SKILL.md:64
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Load `references/platform-foundations.md`, `references/materials-and-accessibility.md`, `references/product-visual-production.md`, `references/web-production-libraries.md`, and `references/review-playbook.md` for their named boundaries.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-apple-design/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-apple-design/SKILL.md`
- SHA256: `fdfaa6a6664154ff8e838951ca7232748b1db86ced8cf84ee66ed3e0aec10cb8`

## Method references
- `omh-apple-design/references/materials-and-accessibility.md` (pinned `skills/omh-apple-design/references/materials-and-accessibility.md`)
- `omh-apple-design/references/platform-foundations.md` (pinned `skills/omh-apple-design/references/platform-foundations.md`)
- `omh-apple-design/references/product-visual-production.md` (pinned `skills/omh-apple-design/references/product-visual-production.md`)
- `omh-apple-design/references/review-playbook.md` (pinned `skills/omh-apple-design/references/review-playbook.md`)
- `omh-apple-design/references/web-production-libraries.md` (pinned `skills/omh-apple-design/references/web-production-libraries.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: mode: design, review, or improve
- Required source input: visual target: Apple marketing/product visual, native Apple application, or Apple-inspired web UI
- Required source input: target, surface/state, supplied evidence, and available execution constraints

## Evidence boundary
prepared_not_observed for apple-design: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
