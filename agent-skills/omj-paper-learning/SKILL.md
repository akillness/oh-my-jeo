---
name: omj-paper-learning
description: [omj] Explain a supplied paper at the selected level, section by section, preserving source grounding and a full coverage ledger.
metadata:
  omj:
    portability: portable
    category: research
    phase: paper-learning
---

# Paper Learning

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`paper-learning` makes this workflow explicit: Explain a supplied paper at the selected level, section by section, preserving source grounding and a full coverage ledger.

## Do Not Use When

- The request asks to export, convert, render, or package a file; use `materials-package`.
- The request asks for daily/weekly paper monitoring, digest, source inbox, or Scout/Analyst/Briefer operations; use `research-department`.
- The request asks to find current papers or sources when no supplied paper exists; use `web-research`.
- The request asks for a visual/image card; use `img-summary`.
- The request asks to implement or reproduce the paper's code; prepare a coding handoff only after a paper learning or reproduction plan is accepted.

## Examples

Good example:

- Prompt: paper-learning 이 논문 PDF를 아주 쉽게 설명해줘. 내용은 줄이지 말고 섹션별로.
- Expected behavior: Prepare paper_learning_card/v1, ask or record level=very_easy, mark PDF extraction/source_state evidence, then explain section-by-section with a coverage ledger.
- Why: The user supplied a paper/PDF explanation intent with an explicit level and coverage-preserving constraint.

Bad example:

- Prompt: paper-learning 이 PDF를 PPT로 변환해서 공유용 파일 만들어줘.
- Expected behavior: Route to `materials-package` because the user wants file conversion/export, not conceptual paper explanation.
- Why: PDF file output and render QA are material packaging work, not paper learning evidence.

## Completion Checklist

- The selected explanation level is one of: very_easy, moderate, expert, choose.
- The source_state is recorded and scoped to observed text or extraction evidence.
- The coverage ledger lists observed, missing, or prepared sections before claiming completion.
- The explanation is section-aware and does not compress away claims, equations, figures, limitations, or reproducibility notes.
- Not-observed boundaries remain visible: full_pdf_extraction, figure_ocr, external_citation_check, math_proof_validation, code_or_benchmark_reproduction, peer_review_or_claim_correctness.

## Recovery Notes

- If no paper text is observed, prepare the learning card from metadata only and ask for an attachment, excerpt, or extraction evidence.
- If only an abstract or excerpt is supplied, label the result as excerpt explanation and list missing sections.
- If context is too long, continue section-by-section and keep covered / next / missing state in the ledger.
- If the user asks for validation, citation checking, math proof review, or reproduction, create a separate observed-evidence or coding handoff path.

## Use When

Explain a supplied paper at the selected level, section by section, preserving source grounding and a full coverage ledger.

Strong routing signals: `paper-learning`, `paper learning`, `paper-explainer`, `paper explainer`, `paper explanation`, `explain this paper`, `explain this arxiv paper`, `paper walkthrough`, `research paper explanation`, `arxiv paper explain`, `pdf paper explain`, `paper pdf explanation`, `explain the attached paper`, `explain this pdf paper`, `without dropping details`, `very easy paper explanation`, `moderate paper explanation`, `expert paper explanation`, `논문 설명`, `논문 해설`, `논문 쉽게 설명`, `논문 아주 쉽게`, `논문 적당한 난이도`, `논문 전문가급`, `이 논문 설명해줘`, `이 논문 PDF 설명해줘`, `논문 PDF 쉽게 설명`, `논문 내용 줄이지 말고`

## Catalog Metadata

Category: `research`
Phase: `paper-learning`
Host-owned workflow responsibility
Quality tier: `paper-learning-gated`

Quality bar:

- Ask for or state the explanation level before drafting: very easy, moderate, or expert.
- Record source_state as one of: metadata_only, excerpt_text_observed, file_text_extraction_observed, full_text_observed, unknown_or_missing.
- Preserve the coverage policy `coverage_preserving_not_lossy_summary` through a section-by-section ledger.
- Explain by chunks when the source is long; keep each chunk linked to coverage_ledger status.
- List missing sections and not-observed claims before presenting the explanation as complete.

Handoff policy:

Explain a supplied paper at the selected level, section by section, preserving source grounding and a full coverage ledger. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- paper identity or attachment reference
- observed text scope or extraction evidence
- explanation level: very_easy, moderate, expert, or choose
- coverage scope: full paper, selected sections, or supplied excerpt
- output language when different from the source

Expected outputs:

- paper_learning_card/v1
- explanation level metadata
- source_state boundary
- coverage ledger
- section-by-section explanation outline
- missing-section and not-observed list

Artifact expectations:

- paper_learning_card/v1 under .omj/paper-learning when a wrapper or CLI records it

Safety rules:

- Do not claim full PDF extraction, figure OCR, external citation checking, math validation, code reproduction, peer review, or full-paper coverage without observed evidence.
- A pasted abstract or excerpt supports only excerpt explanation until the remaining sections are observed.
- Level changes may change scaffolding, vocabulary, analogies, and critique depth, but must not drop substantive content.
- End each chunk with covered / next / missing rather than done unless the coverage ledger is complete.

## Execution and Handoff Discipline

1. State the target, constraints, acceptance criteria, authority, and stop condition before work.
2. Planning and coordination do not take ownership of code implicitly. Keep the selected first-class coding owner explicit, including the current host when selected.
3. Read supporting references only when needed using available host file tools; loading guidance is not dispatch or plan acceptance.
4. Take acceptance only from the user's actual answer. A timeout, dismissal, or missing answer leaves the plan unaccepted; prepare no handoff and start nothing.
5. A selected owner, task card, plan, or prepared handoff stays `prepared_not_observed` until observed execution evidence exists. Preserve failures and unresolved criteria.
6. Verify behavior with the smallest relevant observed check. Current loader admission is not evidence of a live session; local fresh files do not prove host discovery, execution, review, CI, or merge.
7. Network operations, configuration or memory writes, external publishing, and new authority remain separately approval-gated. Do not activate unsupported services.

## Supporting Context

[Native and historical provenance](../omj/references/native-provenance.md)
