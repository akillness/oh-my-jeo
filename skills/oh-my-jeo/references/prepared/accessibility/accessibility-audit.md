# Prepared guidance: accessibility-audit

Family: `accessibility`  
Category: `accessibility`  
Phase: `accessibility-audit`  
Role: `reviewer`

## Contract
[omh] Screen-reader or keyboard accessibility gaps: prepare WCAG, keyboard, focus, screen-reader, target-size, and reflow evidence gates for UI surfaces. Use when the user says: accessibility-audit, accessibility audit, a11y audit, a11y architect, wcag audit, wcag 2.2, wcag 2.2 aa, accessibility pass.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- accessibility-audit
- accessibility audit
- a11y audit
- a11y architect
- wcag audit
- wcag 2.2
- wcag 2.2 aa
- accessibility pass

## Required inputs
- target app, page, route, component, or design system
- platform: web, iOS, Android, desktop, TUI, or unknown
- available UI evidence: code, screenshots, DOM snapshots, accessibility tree, browser captures, or design specs
- interaction paths and critical tasks
- required standard or policy such as WCAG 2.2 AA
- known risk areas: keyboard traps, missing labels, low contrast, small targets, reflow, live regions, or CJK/localization
- observed accessibility evidence for PASS claims

## Expected outputs
- accessibility_audit_plan/v1
- wcag_success_criteria_matrix/v1
- semantic_structure_review/v1
- focus_and_keyboard_trace/v1 when observed
- screen_reader_announcement_map/v1 when observed
- target_size_and_pointer_review/v1
- contrast_and_reflow_review/v1
- accessibility_remediation_handoff/v1 when needed
- accessibility_audit_verdict/v1

## Artifact expectations
- accessibility_audit_plan/v1 with platform, surfaces, critical tasks, standard level, supplied evidence, and missing observations
- wcag_success_criteria_matrix/v1 covering perceivable, operable, understandable, robust requirements with PASS/HOLD/BLOCK per criterion
- semantic_structure_review/v1 with labels, roles, names, headings, landmarks, form errors, live regions, and state semantics
- focus_and_keyboard_trace/v1 only from observed keyboard navigation, tab order, focus appearance, skip/focus-trap checks, and critical interaction paths
- screen_reader_announcement_map/v1 only when announcements, accessible names, roles, values, hints, and dynamic updates are observed or supplied
- target_size_and_pointer_review/v1 with 24x24 CSS px / 44x44 mobile target expectations and pointer gesture alternatives
- contrast_and_reflow_review/v1 with measured contrast, zoom/reflow risk, clipping, overflow, and CJK/localized text concerns
- accessibility_audit_verdict/v1 returns PASS, HOLD, or BLOCK with missing evidence and remediation route

## Acceptance criteria
- The platform, target surfaces, critical tasks, WCAG level, supplied evidence, and missing observations are explicit.
- The wcag_success_criteria_matrix/v1 separates PASS/HOLD/BLOCK and maps each issue to user impact.
- Semantic structure, focus/keyboard, screen-reader announcements, target size/pointer, contrast/reflow, and form/status behavior are separate checks.
- PASS is unavailable unless evidence is fresh after the latest UI edit and covers critical tasks.
- Remediation, frontend implementation, visual QA, browser proof, CI, release, and merge remain separate observed states.

## Handoff policy
Keep accessibility scope, WCAG mapping, focus-flow expectations, screen-reader semantics, and remediation routing in Hermes. Automated scans, browser keyboard walks, screen-reader observations, contrast measurements, and code fixes require observed wrapper, executor, or user evidence.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The user needs initial frontend design or redesign planning before accessibility-specific review; use `frontend` first.
- Source routing exclusion: The user needs rendered layout, screenshot, CJK, or pixel-diff QA rather than accessibility semantics; use `visual-qa`.
- Source routing exclusion: The user needs a broad premium-quality gate across web, deck, PDF, or posters; use `design-quality-gate`.
- Source routing exclusion: The user asks to implement accessibility fixes directly; prepare a selected executor/runtime handoff after the audit or use the coding workflow.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-accessibility-audit/SKILL.md`
- SHA256: `90c554f1ed3cd2522c4c678f39de9a4aac8080c41c9ba9ffb0a3e1d712b3dca3`

## Method references
- `omh-accessibility-audit/references/a11y-rules.md` (pinned `skills/omh-accessibility-audit/references/a11y-rules.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member accessibility-audit is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
