# Prepared guidance: long-document-reading

Family: `long-document`<br>
Category: `research`<br>
Phase: `long-document-reading`<br>
Role: `researcher`

## Contract
[omh] Huge PDF or document to read in full: read a very large PDF, contract, manual, or report through Hermes in page-anchored ranges with a coverage ledger. Use when the user says: long-document-reading, long document reading, summarize this pdf, read this pdf, process this pdf, go through this pdf, summarize this document, read this document.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- long-document-reading
- long document reading
- summarize this pdf
- read this pdf
- process this pdf
- go through this pdf
- summarize this document
- read this document

## Required inputs
- document path or attachment reference
- reading goal: full summary, clause or section lookup, obligations, or a question to answer
- page count and scanned-page flags when observed
- read budget when the host differs from the 100,000-character default
- output language when different from the source

## Expected outputs
- long_document_card/v1
- page count and source_state boundary
- page-range plan sized to the read budget
- chunk ledger with covered / next / missing page anchors
- per-range notes merged in page order
- scanned-range decisions and not-observed list

## Artifact expectations
- long_document_card/v1 metadata-only wrapper card when recorded

## Acceptance criteria
- The page count is observed or the card says it is not.
- Every ledger range is covered, or the missing ranges are listed with a reason.
- Every claim in the merged answer carries a page anchor.
- Scanned ranges are read, declined with a reason, or listed as missing.
- Not-observed boundaries remain visible: page_count, text_extraction, scanned_page_ocr, range_delegation, hosted_ocr, cross_range_consistency.

## Handoff policy
Keep document reading in Hermes: `read_file`, the built-in `pdf` skill scripts, `delegate_task` range children, and `vision_analyze` for scanned pages. Route file export to `materials-package`, paper tutoring to `paper-learning`, and source acquisition to `source-finder`.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: long-document-gated
- source owner: skills/omh-long-document-reading/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-long-document-reading/SKILL.md`
- SHA256: `879dce22c5769c86ebdc7b9a2615538de0ab6feb5a7becdf425403a204cd0c4c`

## Method references
- `long-document-reading/omh-long-document-reading/references/hermes-pdf-limits.md` (pinned `skills/omh-long-document-reading/references/hermes-pdf-limits.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: document path or attachment reference
- blocked until supplied or observed: reading goal: full summary, clause or section lookup, obligations, or a question to answer
- blocked until supplied or observed: page count and scanned-page flags when observed
- blocked until supplied or observed: read budget when the host differs from the 100,000-character default
- blocked until supplied or observed: output language when different from the source
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
