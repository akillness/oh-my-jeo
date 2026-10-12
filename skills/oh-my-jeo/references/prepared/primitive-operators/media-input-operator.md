# Prepared guidance: media-input-operator

Family: `primitive-operators`<br>
Category: `media`<br>
Phase: `media-input-task`<br>
Role: `guide`

## Contract
[omh] Audio, video, or screenshot to process: user-sent media - audio, video, YouTube links, screenshots, receipts, OCR, meeting recordings, transcripts, timestamps, and clip summaries, gated for source, permission, and hallucination risk. Use when the user says: media-input-operator, media input operator, media input, audio transcription, audio transcript, transcribe audio, transcribe this audio, meeting recording.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- media-input-operator
- media input operator
- media input
- audio transcription
- audio transcript
- transcribe audio
- transcribe this audio
- meeting recording

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- media_input_task_card/v1
- media_source_scope/v1
- transcript_boundary/v1
- media_summary_plan/v1
- media_result_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- media_input_task_card/v1 metadata-only wrapper card when prepared
- media_source_scope/v1 with media type, source location, permission boundary, requested time range, and stop condition
- transcript_boundary/v1 separating supplied transcript, missing transcript, ASR/extraction requirement, language, speaker labels, and confidence gaps
- media_summary_plan/v1 naming action-item, timestamped, clip, chapter, quote, or evidence-linked summary method
- media_result_manifest/v1 only when supplied transcript, media file metadata, provider response, or observed transcript output exists

## Acceptance criteria
- Media type, source location, permission boundary, transcript availability, language, requested output, timestamp requirement, and stop condition are explicit.
- Downloads, uploads, ASR, transcript extraction, speaker labels, copyrighted media access, and provider setup are gated or marked missing.
- Transcript text, OCR output, screenshot text, receipt fields, timestamps, quotes, action items, and media-summary claims are reported only from observed media or supplied transcript/extraction evidence.

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
- Source path: `skills/omh-media-input/SKILL.md`
- SHA256: `7bb72c89c13ce8e064bfcd326e075664851456a5dfa7225559a64912e5ea18c9`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member media-input-operator is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
