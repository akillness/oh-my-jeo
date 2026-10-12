# Prepared guidance: llm-app-dev

Family: `llm-application-build`<br>
Category: `delivery`<br>
Phase: `llm-app-dev`<br>
Role: `operator`

## Contract
[omh] LLM-powered feature to build: LLM app development: prepare a build handoff for an LLM-powered feature with a pinned provider boundary, schema-first outputs, versioned prompt files, grounded retrieval, and an eval suite as a shipped deliverable. Use when the user says: llm-app-dev, llm app development, llm application development, build an llm app, build an llm feature, llm feature development, build a rag pipeline, rag pipeline.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- llm-app-dev
- $llm-app-dev
- llm app development
- llm application development
- build an llm app
- build an llm feature
- llm feature development
- build a rag pipeline
- rag pipeline
- retrieval augmented generation
- structured output schema
- json schema output
- prompt versioning
- llm eval suite
- golden set
- LLMアプリ開発
- LLM機能開発
- RAGパイプライン構築
- 構造化出力スキーマ
- プロンプトのバージョン管理
- LLM評価セット
- llm 앱 개발
- llm 애플리케이션 개발
- llm 기능 개발
- rag 파이프라인
- rag 파이프라인 구축
- 구조화된 출력 스키마
- 프롬프트 버전 관리
- llm 평가셋
- 골든셋
- 大模型应用开发
- 检索增强生成
- 结构化输出模式
- 提示词版本管理
- 评测集

## Required inputs
- the feature the model is supposed to perform
- the exact provider and model ID under consideration
- the shape of the output the caller consumes
- the failing cases that must not regress

## Expected outputs
- rail decisions across provider boundary, structured output, prompt artifacts, retrieval grounding, evaluation
- the output schema and the validate-and-repair path for a response that does not match it
- the prompt artifact layout and its version identifier
- the eval deliverables - golden set, task-level validators, baseline-vs-candidate comparison
- the executor handoff and what stays unobserved until a run produces it

## Artifact expectations
- prompt files committed under version control with a version identifier the call site records, so a response can be traced to the prompt that produced it
- a golden set committed beside the code as data, not as prose in a chat log

## Acceptance criteria
- Every rail - provider boundary, structured output, prompt artifacts, retrieval grounding, evaluation - is either decided or explicitly deferred with a reason.
- One client boundary owns the model ID, credentials, timeout, retry, and backoff, and no credential appears in source, prompts, tests, or examples.
- The model ID is exact, and it is recorded next to any result meant to be compared.
- Every model response is validated against a declared schema, with a bounded repair path and a loud failure - no prose scraping.
- Prompts are files with a version identifier, and system rules, task instruction, and injected context are separated.
- Untrusted retrieved or user-supplied content is fenced from the instruction channel and cannot change the task.
- The eval deliverables - golden set, task-level validators, baseline-vs-candidate comparison - exist as committed artifacts, and retrieval is evaluated before generation when retrieval is in the path.
- Token, latency, and cost figures come from an observed run or stay null; no design output is reported as an eval result, implementation, review, CI, or merge evidence.
- If the feature communicates through a public board, the destination carries a public-audience label, each action class names its own authority and outbound data, the exact draft and its host-recorded approval reference travel with the request through compaction and executor handoff, and no publication is reported without an observed connector result.

## Handoff policy
Keep the rail choices, schema shape, prompt-artifact layout, and eval design in Hermes as a prepared build handoff. Prepare a selected executor/runtime handoff for the code itself, and record provider calls, eval runs, token counts, and cost only from observed run artifacts.

## Catalog rules
- quality_tier: delivery-gated
- contract_source: skills/omh-llm-app-dev/SKILL.md:77
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Decide the rails in order - provider boundary, structured output, prompt artifacts, retrieval grounding, evaluation - and say which are deferred rather than leaving them unnamed. Load `references/build-rails.md` for the per-rail decision and its failure mode.
- Catalog Metadata: - Ship the eval suite as a deliverable, not a follow-up: golden set, task-level validators, baseline-vs-candidate comparison, with deterministic validators wherever the task allows one. Load `references/eval-harness.md` for the golden-set shape, the corpus-hygiene checks that run before a score is quoted, the validator ladder, and the comparison record.
- Catalog Metadata: - When the user asks for communication through a public board, treat the destination as a public external disclosure even when the account is authenticated: give read, search, register, profile, reply, publish their own authority and outbound-data expectation, show the exact destination, the public-audience label, and the complete outbound payload before a host-recorded approval, and reconcile an ambiguous send by read-back or receipt before any retry. Load `references/public-board.md` for the per-action authority table, the untrusted-peer rules, and what survives compaction and handoff.
- Catalog Metadata: - When the feature presents or acts on business records; enforces a cumulative business limit; stores facts about a person, load `references/stateful-contracts.md`. Provenance is not authorization, follow-up references resolve against the final-order receipt, limits are checked on resulting state inside one atomic apply boundary, and stored user facts are host-validated and deletable. A feature with none of those properties records that and skips this conditional contract.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-llm-app-dev/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-llm-app-dev/SKILL.md`
- SHA256: `744ba340ab2332d10315c350a05cc82c55371e0522038beecc2772644c54f6a3`

## Method references
- `omh-llm-app-dev/references/build-rails.md` (pinned `skills/omh-llm-app-dev/references/build-rails.md`)
- `omh-llm-app-dev/references/eval-harness.md` (pinned `skills/omh-llm-app-dev/references/eval-harness.md`)
- `omh-llm-app-dev/references/public-board.md` (pinned `skills/omh-llm-app-dev/references/public-board.md`)
- `omh-llm-app-dev/references/stateful-contracts.md` (pinned `skills/omh-llm-app-dev/references/stateful-contracts.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the feature the model is supposed to perform
- Required source input: the exact provider and model ID under consideration
- Required source input: the shape of the output the caller consumes
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for llm-app-dev: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
