# Prepared guidance: visual-qa

Family: `design-direction`<br>
Category: `materials`<br>
Phase: `visual-qa`<br>
Role: `operator`

## Contract
[omh] Rendered UI needing a visual verdict: prepare observed-only rendered QA gates for web, frontend, image, document, and TUI surfaces. Use when the user says: visual-qa, visual qa, visual QA, visual quality assurance, visual check, web qa, web visual qa, screenshot qa.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- visual-qa
- visual qa
- visual QA
- visual quality assurance
- visual check
- web qa
- web visual qa
- screenshot qa
- screenshot check
- analyze this screenshot
- screenshot layout problems
- ui layout problems
- pixel diff
- image diff
- visual diff
- render qa
- render check
- browser screenshot
- browser qa
- browser interaction qa
- click path
- click-path audit
- dead link check
- console error check
- network failure check
- keyboard navigation check
- viewport check
- responsive check
- ui looks wrong
- looks broken
- layout broken
- broken layout
- text clipping
- cjk clipping
- cjk layout
- tui check
- terminal ui check
- スクリーンショットで確認
- レイアウト崩れ
- 画面崩れ
- 見た目のQA
- 비주얼 qa
- 비주얼QA
- 시각 qa
- 시각 검증
- 화면 검증
- 스크린샷 검증
- 스크린샷 ui 레이아웃
- 스크린샷 UI 레이아웃
- 스크린샷 레이아웃 문제
- 렌더 검증
- 픽셀 diff
- 픽셀 비교
- 화면 깨짐
- 레이아웃 깨짐
- 글자 잘림
- 한글 줄바꿈
- 터미널 ui
- 截图检查
- 页面错位
- 视觉验收
- 布局错乱

## Required inputs
- surface type
- target URL, route, file, image, or TUI command when available
- intended design, baseline, or reference
- pages, states, viewports, and locales to cover
- complete page/state/viewport enumeration rather than a sample
- target repository and exact source revision
- known risk areas such as CJK, overflow, responsiveness, or accessibility
- motion and interaction states that need capture
- browser interaction paths, mutating-flow boundary, and test credentials policy when a live web UI is in scope
- console, network, accessibility, and keyboard navigation checks required for browser QA claims
- render/capture evidence bound to the target repository and revision for completion claims

## Expected outputs
- visual_qa_plan/v1
- web_visual_qa_package/v2
- viewport_state_capture_matrix/v1
- message_attachment_projection/v1 for chat attachments
- web_visual_qa_message_card/v1 for chat message summaries
- render_capture_manifest/v1 when observed
- browser_interaction_trace/v1 when observed
- console_network_health/v1 when observed
- click_path_state_trace/v1 when observed
- accessibility_keyboard_trace/v1 when observed
- visual_diff_evidence/v1 when observed
- visual_hotspot_review/v1 when observed
- motion_interaction_capture/v1 when observed
- dual_oracle_visual_review/v1 when observed
- cjk_layout_findings/v1 when applicable
- visual_qa_verdict/v1
- retry_or_blocker/v1

## Artifact expectations
- visual_qa_plan/v1 with pages, states, viewports, references, and exact target repository/revision lineage
- web_visual_qa_package/v2 with target_lineage, unique required_viewports, capture source_lineage, blocking_violations, criteria, reviews, auto routing, and observed-only cost policy
- viewport_state_capture_matrix/v1 enumerates every route/page, 375/768/1280-style viewport, scroll position, modal/tab state, and CJK-heavy region to capture
- message_attachment_projection/v1 maps eligible observed captures to attachment candidates without claiming delivery
- web_visual_qa_message_card/v1 projects recorded criteria, captures, routing, cost policy, and attachment hints into chat-safe copy
- render_capture_manifest/v1 only from captures whose source lineage matches the target package
- browser_interaction_trace/v1 only from observed journey runs with read-only or staging-safe boundaries recorded
- console_network_health/v1 records observed console errors, failed requests, status codes, and ignored third-party noise
- click_path_state_trace/v1 maps each touchpoint to its handler, state reads/writes, final UI state, and undo/race/stale-closure risks
- accessibility_keyboard_trace/v1 records observed focus order, keyboard reachability, and automated scan boundaries
- visual_diff_evidence/v1 only when the wrapper/executor records objective diff output such as dimensionsMatch, diffRatio, similarityScore, alphaChannelIntact, and hotspots
- motion_interaction_capture/v1 only when motion frames are observed before, during, and after transition
- visual_hotspot_review/v1 maps diff hotspots, TUI overflow lines, or screenshot regions to visual causes
- dual_oracle_visual_review/v1 only when independent read-only review evidence exists
- visual_qa_verdict/v1 with the integer 0-100 score, PASS/REVISE/BLOCK, and difference/suggestion pairs
- PASS unavailable until capture repository/revision lineage exactly matches the package target, every required viewport is captured, and all supplied blocking findings are resolved
- web_qa_observation_run/v1 and web_qa_comparison/v1 only from a host_web_qa_adapter_receipt/v1 imported through `omh web-qa observation`: seven independently observed channels or a named blocker per cell

## Acceptance criteria
- Interaction, console/network, click-path, keyboard/accessibility, diff, hotspot, motion, dual-review evidence, and blocker status are separate fields.
- The verdict is PASS, REVISE, or BLOCK with concrete evidence IDs and exact missing evidence or fix requirements.
- Implementation fixes stay separate from the observed verdict, routed back to the executor/frontend workflow and rechecked against the resulting revision.

## Handoff policy
Keep the QA plan, evidence manifest, target-lineage rule, and verdict narration in Hermes. Screenshots, TUI captures, image diffs, browser runs, OCR/CJK checks, and oracle reviews are observed evidence supplied by the wrapper, executor, or user.

## Catalog rules
- quality_tier: visual-qa-gated
- contract_source: skills/omh-visual-qa/SKILL.md:65
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Score every round through `references/visual-verdict-contract.md`: integer 0-100 score, PASS/REVISE/BLOCK, and a differences list pairing each observed problem with the smallest fix.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-visual-qa/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-visual-qa/SKILL.md`
- SHA256: `fd2f822e85dd8b5f0bc9bed0f2b1aa20d3b16889d6cb32d5c78db1b302543d30`

## Method references
- `omh-visual-qa/references/visual-verdict-contract.md` (pinned `skills/omh-visual-qa/references/visual-verdict-contract.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: surface type
- Required source input: target URL, route, file, image, or TUI command when available
- Required source input: intended design, baseline, or reference
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for visual-qa: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
