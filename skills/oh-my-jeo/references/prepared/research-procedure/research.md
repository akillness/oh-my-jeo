# Prepared guidance: research

Family: `research-procedure`<br>
Category: `research`<br>
Phase: `decision-grounding`<br>
Role: `researcher`

## Contract
[omh] Deep dive before a decision: deep research engine - grounding for specs and decisions: study open-source reference implementations with pinned refs, gather live web evidence with citation discipline, verify contested claims, and distill a decision-grounding dossier that planning consumes; for a decision brief use research-brief, for upstream guidance use web-research. Use when the user says: research plan, literature review, research literature, review recent papers, deep research, deep-research, exhaustive research, saturation research.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- research plan
- literature review
- research literature
- review recent papers
- deep research
- deep-research
- exhaustive research
- saturation research

## Required inputs
- research question
- output audience - a human reader or a coding agent - asked before retrieval and never inferred
- output format when the reader is human - markdown, a print-ready page, or both
- output language when the reader is human - declared, never inferred from the request
- target user/task if usability matters
- usability/quality dimension if applicable
- source boundaries
- candidate reference implementations or repos when relevant
- declared depth or wave budget when exhaustive grounding is requested - never inferred from phrasing
- freshness, jurisdiction, or version constraints
- requested as-of date or interval when the question is point-in-time

## Expected outputs
- source-backed synthesis
- links or citations
- source-quality notes
- reference-implementation notes with pinned versions or permalinks
- verified-claims ledger with an unresolved and refuted annex
- plan-feed block: decision drivers, viable options with evidence, rejected candidates with reasons, risks, open questions
- confidence and residual uncertainty
- product_evidence_loop/v1
- deep_research_dossier/v1
- research_briefing/v1 with its markdown and print-ready page when the reader is human
- temporal_source_receipt/v1 per historical claim and temporal_evidence_surfaces/v1 when the question is point-in-time

## Artifact expectations
- research notes with source URLs, retrieval dates, source-quality notes, and per-reference mechanism, tradeoff, license, and pinned-ref notes when the wrapper captures them

## Acceptance criteria
- The research question, source boundaries, recency assumptions, and confidence level are named.
- Observed sources, inference, synthesis, and unresolved retrieval gaps are separated.
- Follow-up planning or handoff uses the research summary without calling it execution evidence.

## Handoff policy
Run as a Hermes-side research lane when web or repository access is available; Hermes and its delegated readers study sources, distill evidence or the dossier before any planning or coding handoff, and never treat research as implementation.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: source-gated
- source owner: skills/ulw-research/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/ulw-research/SKILL.md`
- SHA256: `90170cd524122c559233b11bdd3d857a355061a04afd045c8e6ea220a3c2fe9d`

## Method references
- `ulw-research/references/briefing-format.md` (pinned `skills/ulw-research/references/briefing-format.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: research question
- blocked until supplied or observed: output audience - a human reader or a coding agent - asked before retrieval and never inferred
- blocked until supplied or observed: output format when the reader is human - markdown, a print-ready page, or both
- blocked until supplied or observed: output language when the reader is human - declared, never inferred from the request
- blocked until supplied or observed: target user/task if usability matters
- blocked until supplied or observed: usability/quality dimension if applicable
- blocked until supplied or observed: source boundaries
- blocked until supplied or observed: candidate reference implementations or repos when relevant
- blocked until supplied or observed: declared depth or wave budget when exhaustive grounding is requested - never inferred from phrasing
- blocked until supplied or observed: freshness, jurisdiction, or version constraints
- blocked until supplied or observed: requested as-of date or interval when the question is point-in-time
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
