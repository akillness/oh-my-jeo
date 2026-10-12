---
name: omj-web-research
description: [omj] Gather current source-backed evidence with primary sources, citations, freshness, confidence, and retrieval gaps.
metadata:
  omj:
    portability: portable
    category: research
    phase: current-evidence
---

# Web Research

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`web-research` makes this workflow explicit: Gather current source-backed evidence with primary sources, citations, freshness, confidence, and retrieval gaps.

## Do Not Use When

- The user asks for a full plan-to-PR delivery cycle; use `ultraprocess` or a planning workflow after research instead.
- The request is purely local repo inspection with no external, current, citation, or source-comparison need.
- The user needs coding execution, review, CI, or merge evidence rather than research synthesis.

## Examples

Good example:

- Prompt: 웹서치해서 최신 자료와 출처를 정리해줘.
- Expected behavior: Use available host research tools, state source boundaries and freshness, and summarize citations, confidence, and retrieval gaps.
- Why: The request explicitly asks for web search, current material, and sources without asking for implementation.

Bad example:

- Prompt: 웹리서치부터 계획, 구현, 리뷰, 문서, PR까지 한 사이클로 끝내줘.
- Expected behavior: Route to `ultraprocess` because the user asked for a bounded delivery cycle, not a research-only lane.
- Why: Research is only one stage of the requested delivery process.

## Completion Checklist

- The research question, source boundaries, recency assumptions, and confidence level are named.
- Observed sources, inference, synthesis, and unresolved retrieval gaps are separated.
- Follow-up planning or handoff uses the research summary without calling it execution evidence.

## Recovery Notes

- If sources cannot be accessed, state the retrieval gap and use only observed local context.
- If evidence is thin or one-sided, lower confidence and ask for a narrower source boundary.

## Use When

Gather current source-backed evidence with primary sources, citations, freshness, confidence, and retrieval gaps.

Strong routing signals: `web-research`, `web research`, `web search`, `search the web`, `internet search`, `latest`, `fresh sources`, `current sources`, `current web evidence`, `source-backed research`, `source search`, `find sources`, `find citations`, `citation check`, `evidence scan`, `source diversity`, `retrieval gap`, `look up`, `lookup`, `investigate`, `research plan`, `웹서치`, `웹 서치`, `웹 검색`, `인터넷 검색`, `검색해줘`, `검색해서`, `최신 자료`, `최신 출처`, `자료 찾아`, `조사`, `근거`, `출처`, `고객 피드백`

## Catalog Metadata

Category: `research`
Phase: `current-evidence`
Host-owned workflow responsibility
Quality tier: `source-gated`

Quality bar:

- Ask for the research question, source boundaries, freshness, jurisdiction, and version assumptions before retrieval.
- Use official or primary sources first when current or external facts matter, then add source diversity when the topic is contested.
- Separate direct evidence, citation links, retrieval dates, inference, confidence, and residual uncertainty.
- Name retrieval gaps when the selected host cannot access the web.
- Summarize research before any coding handoff; research is not implementation evidence.

Handoff policy:

Gather current source-backed evidence with primary sources, citations, freshness, confidence, and retrieval gaps. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- research question
- source boundaries
- freshness, jurisdiction, or version constraints

Expected outputs:

- source-backed synthesis
- links or citations
- source-quality notes
- confidence and residual uncertainty

Artifact expectations:

- research notes with source URLs, retrieval dates, and source-quality notes when the wrapper captures them

Safety rules:

- Prefer official or primary sources when they can answer the question.
- Check source diversity and conflicts before summarizing contested or unstable topics.
- Separate quoted evidence from inference.
- State retrieval limits, dates, and missing-source gaps for unstable facts.

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
