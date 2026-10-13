---
name: omj-source-finder
description: [omj] Prepare typed paper, web, dataset, repository, presentation, or document candidates and acquisition status before downstream work.
metadata:
  omj:
    portability: portable
    category: research
    phase: source-acquisition
---

# Source Finder

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`source-finder` makes this workflow explicit: Prepare typed paper, web, dataset, repository, presentation, or document candidates and acquisition status before downstream work.

## Do Not Use When

- The user asks for current citations, fact-finding, or source-backed synthesis; use `web-research`.
- The user supplies a paper/PDF/arXiv/DOI/excerpt and wants explanation; use `paper-learning`.
- The user asks for recurring monitoring, source inbox, or Scout/Analyst/Briefer operations; use `research-department`.
- The user asks to export, convert, render, package, or attach a file; use `materials-package` or `deliverable-package`.
- The user asks for an image card or visual summary; use `img-summary`.

## Examples

Good example:

- Prompt: source-finder find papers, datasets, and GitHub repos for evaluating browser agent benchmarks.
- Expected behavior: Prepare source_finder_plan/v1 with typed candidates, acquisition states, missing observed evidence, and downstream choices.
- Why: The user needs source candidates before deciding whether to learn, research, package, or implement.

Bad example:

- Prompt: source-finder find current citations and summarize what the sources say.
- Expected behavior: Route to `web-research` because the user asks for current evidence and synthesis, not candidate acquisition status.
- Why: Source-finder prepares acquisition lifecycle metadata; web-research owns current evidence synthesis.

## Completion Checklist

- Source kinds, source boundaries, and downstream intent are named.
- Each candidate has a source_candidate/v1 shape and acquisition state.
- Observed states include provenance before being treated as evidence.
- The next downstream workflow is recommended without claiming it ran.
- Search, download, clone, extraction, hash, license, verification, and downstream processing gaps are explicit.

## Recovery Notes

- If the user asks for facts or citations, route to `web-research`.
- If a candidate lacks a link or file reference, keep it candidate_prepared and ask for the next observable source step.
- If the user wants to process a selected source, route to the downstream workflow instead of continuing source acquisition.

## Use When

Prepare typed paper, web, dataset, repository, presentation, or document candidates and acquisition status before downstream work.

Strong routing signals: `source-finder`, `source finder`, `source acquisition`, `source intake`, `find papers and datasets`, `find datasets and repos`, `find papers`, `find datasets`, `find github repos`, `find oss repos`, `find presentations`, `find public slides`, `find docs and specs`, `find source candidates`, `download candidate`, `source candidate`, `acquisition status`, `자료 후보`, `출처 후보`, `논문 데이터셋 찾아`, `깃허브 저장소 찾아`, `공개 발표자료 찾아`, `문서 스펙 찾아`

## Catalog Metadata

Category: `research`
Phase: `source-acquisition`
Host-owned workflow responsibility
Quality tier: `source-acquisition-gated`

Quality bar:

- Name source kinds from: paper, web_link, dataset, github_repo, presentation, docs_spec, unknown.
- Record acquisition state from: candidate_prepared, link_observed, download_link_prepared, download_observed, file_hash_recorded, text_extraction_observed, license_checked, verification_observed, downstream_selected.
- Separate candidate preparation, observed link, observed download, file hash, text extraction, license check, verification, and downstream selection.
- Attach observation provenance before treating any acquisition state as evidence.
- Recommend the next downstream workflow without pretending that downstream work already ran.

Handoff policy:

Prepare typed paper, web, dataset, repository, presentation, or document candidates and acquisition status before downstream work. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- source target or topic
- desired source kinds
- source boundaries or exclusion criteria
- downstream intent when known

Expected outputs:

- source_finder_plan/v1
- source_candidate/v1
- source_candidate_set/v1
- source_acquisition_status/v1
- downstream workflow recommendation
- not-evidence boundary

Artifact expectations:

- source_finder_plan/v1 under .omj/source-finder when a wrapper or CLI records it

Safety rules:

- Do not claim web search, download, repository clone, file extraction, file hash verification, license verification, or source correctness from a prepared candidate.
- Do not redefine research-department's source_inbox/v1; source-finder owns source_candidate_set/v1 and source_acquisition_status/v1 only.
- Route current citations and source-backed synthesis to `web-research`, supplied-paper explanation to `paper-learning`, recurring monitoring to `research-department`, file export to `materials-package`, and image cards to `img-summary`.

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
