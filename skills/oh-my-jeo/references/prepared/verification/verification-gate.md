# Prepared guidance: verification-gate

Family: `verification`<br>
Category: `verification`<br>
Phase: `verification-gate`<br>
Role: `reviewer`

## Contract
[omh] Proof a change is done before merge: define and record build, lint, typecheck, test, security, docs, generated-output, and CI evidence before completion or merge. Use when the user says: verification-gate, verification gate, quality gate, release gate, test gate, build lint test, lint typecheck tests, verify before merge.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- verification-gate
- verification gate
- quality gate
- release gate
- test gate
- build lint test
- lint typecheck tests
- verify before merge
- merge readiness gate
- generated file
- generated artifact
- generated output
- source of truth
- regenerate instead of editing
- 検証ゲート
- 品質ゲート
- マージ前の検証
- リリース前チェック
- 검증 게이트
- 품질 게이트
- 테스트 게이트
- 머지 전 검증
- 빌드 린트 테스트
- 验证门禁
- 质量门禁
- 合并前验证
- 发布前检查

## Required inputs
- claim or change under verification
- expected behavior and risk surface
- available local commands and CI requirements
- fresh observed outputs or explicit not-run gaps

## Expected outputs
- verification_gate_plan/v1
- verification_matrix/v1
- generated_artifact_provenance/v1 when the change touches a path the repository declares generated
- observed_check_results/v1 when observed
- claim_verdict/v1
- rerun_or_blocker/v1
- not-evidence boundary

## Artifact expectations
- verification_matrix/v1 covering build, lint, typecheck, unit/integration/e2e tests, generated docs, static/security checks, diff hygiene, and CI/DCO when applicable
- observed_check_results/v1 with command (verbatim, not a description of it), source (this checkout, a CI job, or an operator report), exit status, summary (what the output said), scope (what that run covered, since a narrower run proves less), and freshness (when it ran, and whether the tree has moved since)
- claim_verdict/v1 with PASS, HOLD, or BLOCK and exact missing or failed checks
- generated_artifact_provenance/v1 with one row per touched generated path: the source of truth that produces it, the regeneration command, and the drift gate that catches it, or the single state `map_not_declared` when the repository declares no generated-artifact map

## Acceptance criteria
- The scenario, expected behavior, observed result, and pass/fail basis are named.
- Proposed fixes are separated from observed QA evidence.
- Missing or failed verification routes back to plan, fix, or a narrower test.

## Handoff policy
Hermes owns the gate contract and verdict narration. Running commands, CI, browser checks, external scanners, and code fixes require observed executor, wrapper, or operator evidence.

## Catalog rules
- quality_tier: verification-gated
- contract_source: skills/omh-verification-gate/SKILL.md:64
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - When a diff touches a declared generated path, name its source of truth and regeneration command before the edit rather than after a byte gate rejects it; a diff touching a generator and its output together is the correct shape, not a violation — load `references/generated-artifact-provenance.md` for the declaration and reporting rules.
- Catalog Metadata: - When the change answers to a written spec, plan, or issue, load `references/requirement-coverage-map.md` and map requirement to task to evidence under stable ids before claiming coverage.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-verification-gate/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-verification-gate/SKILL.md`
- SHA256: `327b4458de6d08432c89976d3450b40a892db8693a87dc46fb4fadcd54692296`

## Method references
- `omh-verification-gate/references/generated-artifact-provenance.md` (pinned `skills/omh-verification-gate/references/generated-artifact-provenance.md`)
- `omh-verification-gate/references/requirement-coverage-map.md` (pinned `skills/omh-verification-gate/references/requirement-coverage-map.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: claim or change under verification
- Required source input: expected behavior and risk surface
- Required source input: available local commands and CI requirements
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for verification-gate: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
