# Prepared guidance: maestro

Family: `external-maestro`<br>
Category: `execution`<br>
Phase: `external-handoff`<br>
Role: `handoff-guide`

## Contract
[omh] Coding owner already chosen, handoff pending: prepares the handoff for the coding agent you already chose, composing its prompt from that agent's own installed skills; never selects the owner and never executes the work itself. Use when the user says: ulw-maestro, coding handoff, prepare the handoff, prepare a coding handoff, hand off the coding work, external executor handoff, handoff prompt, delegation prompt.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- $maestro
- ulw-maestro
- coding handoff
- prepare the handoff
- prepare a coding handoff
- hand off the coding work
- external executor handoff
- handoff prompt
- delegation prompt
- コーディング委任
- 委任プロンプト
- ハンドオフを準備
- 外部の実行エージェントに渡す
- 코딩 위임
- 위임 프롬프트
- 핸드오프 준비
- 외부 실행기 위임
- 코딩 에이전트에 넘기
- 编码委托
- 移交提示词
- 准备交接
- 交给编码代理

## Required inputs
- explicit coding-owner choice for this run
- task or unit description
- the chosen profile's discovered executor skill set

## Expected outputs
- a composed executor prompt arranged by the unit's role recipe
- the handoff mode and dispatchability state named up front
- a captured session or thread id, or an explicit unsteerable note

## Artifact expectations
- prepared external handoff record when a wrapper can record it

## Acceptance criteria
- The selected coding or runtime owner is named before any implementation claim.
- Prepared handoff, dispatch, execution, verification, review, CI, and merge states are separated.
- The final status cites observed runtime evidence or keeps the work prepared_not_observed.
- When Hermes is the selected coding owner this engine does not apply -- Hermes-native selection uses the Hermes runtime path, never this engine.
- Dispatch never merges: collect each unit's fanout_unit_result/v1 evidence, verify the integrated combination of units (not just each one alone -- disjoint file scopes can still conflict at integration), and report merged/unmerged per unit in the closing brief. Merging the unit branches remains an explicit operator or reviewing-agent action; a dispatch receipt is never merge evidence.
- The closing brief ends with the observed `omh_run_summary` summary_text verbatim, or an explicit run-summary not_available line -- never a model-estimated number.

## Handoff policy
Convert an explicitly chosen external coding owner into a prepared handoff: claude-code as a prompt-only `coding_prompt_handoff/v1` (never dispatchable, never described as a run), codex as a dispatchable `coding_executor_handoff/v1`, and omx-runtime/omo-runtime/omc-runtime as `coding_runtime_handoff/v1`. This engine loads only after that choice is made -- absent an explicit coding-owner choice, work runs inside the Hermes harness and no external coding CLI is selected -- and it never substitutes for the Hermes harness path or picks the owner itself.

## Catalog rules
- quality_tier: handoff-gated
- contract_source: skills/ulw-maestro/SKILL.md:69
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Compose the prompt from the selected profile's DISCOVERED skills via `omh coding executor-skills --profile <profile>`: arrange the returned skills by the unit's role recipe, one named skill per step, using each skill's own invocation string verbatim (`/name`, `/pack:name` from its manifest, `$name` for a codex pack) -- never a guessed prefix. Empty discovery gets one explicit line -- "no installed skills discovered for <profile>; prompt composed generically" -- then compose generically. Load `references/executor-prompt-composition.md` for the full procedure.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/ulw-maestro/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/ulw-maestro/SKILL.md`
- SHA256: `d25cef43f089909e86823251ebf733ff842a7e15454d858e5aeb942fdfa8b6c2`

## Method references
- `maestro/ulw-maestro/references/executor-prompt-composition.md` (pinned `skills/ulw-maestro/references/executor-prompt-composition.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: explicit coding-owner choice for this run
- Required source input: task or unit description
- Required source input: the chosen profile's discovered executor skill set
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for maestro: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
