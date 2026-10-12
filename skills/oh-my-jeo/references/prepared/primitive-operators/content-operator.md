# Prepared guidance: content-operator

Family: `primitive-operators`  
Category: `content`  
Phase: `content-task`  
Role: `guide`

## Contract
[omh] Product or company copy to publish or rewrite: scope publish-ready writing, rewriting, summarization, translation, release-note, newsletter, customer-copy, social-copy, README-copy, and email-draft work with audience, tone, style, source, review, and hallucination gates. Use when the user says: content-operator, content operator, content workflow, writing workflow, publish-ready writing, publish ready writing, release notes, release note draft.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- content-operator
- content operator
- content workflow
- writing workflow
- publish-ready writing
- publish ready writing
- release notes
- release note draft

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- content_task_card/v1
- source_scope/v1
- audience_tone_style/v1
- content_review_gate/v1
- content_output_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- content_task_card/v1 metadata-only wrapper card when prepared
- source_scope/v1 with supplied sources, missing sources, fact-risk, citation need, and no-invention rule
- audience_tone_style/v1 with audience, channel, language, tone, style guide, length, format, and accessibility constraints
- content_review_gate/v1 separating draft, reviewer approval, legal/compliance needs, publish/send/file-export authority, and stop condition
- content_output_manifest/v1 only when produced draft, revision diff, approval, export, publish, or delivery evidence is observed

## Acceptance criteria
- Audience, channel, language, tone, style guide, length, source scope, fact-risk, review owner, and stop condition are explicit.
- Missing facts, source gaps, claims needing citations, legal/compliance needs, approval, publish/send authority, and file-export needs are gated or marked missing.
- Published, sent, exported, approved, and fact-verified claims are reported only from observed evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Route only on the source-defined description and triggers; do not treat nearest local contracts toolbelt-readiness, deliverable-package as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-content-operator/SKILL.md`
- SHA256: `cb842f86a965133d2c74bc2a22e04e39fbab684d3301e6acff56a31e9acb3853`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member content-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
