# Prepared guidance: frontend

Family: `design-direction`<br>
Category: `materials`<br>
Phase: `frontend-design`<br>
Role: `operator`

## Contract
[omh] Building or polishing a web or terminal UI: prepare design-system-driven web and terminal (TUI) UI creation, redesign, polish, accessibility, performance, and visual QA handoffs. Use when the user says: frontend, front-end, front end, frontend skill, in the frontend, on the frontend, to the frontend, web ui.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- frontend
- front-end
- front end
- frontend skill
- in the frontend
- on the frontend
- to the frontend
- web ui
- ui ux
- ui/ux
- landing page
- web app layout
- responsive layout
- responsive design
- design system
- component polish
- layout polish
- visual polish
- styling
- animation
- motion design
- smooth scroll
- smooth scrolling
- scroll animation
- scroll animations
- parallax scroll
- parallax hero
- parallax effect
- chart styling
- chart theming
- chart colors
- dashboard charts
- style the charts
- theme the charts
- tooltip
- footer design
- better footer
- site footer
- website footer
- neobrutalism
- neobrutalism style
- neobrutalist
- neo brutalism
- neo-brutalism
- logo marquee
- marquee animation
- scrolling marquee
- split text animation
- split-text animation
- shadcn
- component registry
- accessibility
- wcag
- lighthouse
- core web vitals
- make it beautiful
- make it premium
- make it less ai
- ai-looking ui
- ai slop ui
- generic ui
- broken layout
- layout broken
- frontend qa
- frontend layout
- tui design
- terminal ui design
- tui layout
- フロントエンド
- ランディングページ
- レスポンシブ対応
- デザインシステム
- 画面のUI実装
- スムーススクロール
- スクロールアニメーション
- パララックス
- チャートのスタイル
- チャートスタイル
- フッターデザイン
- ネオブルータリズム
- ロゴマーキー
- 프론트엔드
- 웹 ui
- 웹 화면
- 랜딩페이지
- 레이아웃
- 레이아웃 깨짐
- 깨짐
- 디자인 자연스럽게
- 자연스러운 디자인
- 화려하게
- 고급스럽게
- 부드러운 스크롤
- 스크롤 부드럽게
- 스크롤 애니메이션
- 패럴랙스
- ai 티
- ai틱
- ai 틱
- 반응형
- 접근성
- 차트 스타일
- 차트 스타일링
- 차트 테마
- 푸터 디자인
- 네오브루탈리즘
- 로고 마키
- 마키 애니메이션
- 스플릿 텍스트
- 前端
- 落地页
- 响应式布局
- 设计系统
- 平滑滚动
- 滚动动画
- 视差滚动
- 图表样式
- 页脚设计
- 新粗野主义
- 跑马灯

## Required inputs
- target app, page, route, or component
- audience and primary user task
- existing design system or missing-system gap
- style references or quality bar
- initial generation mode or redesign mode
- DESIGN.md or design-system source of truth when available
- framework/stack when known
- routes, states, breakpoints, and locale/CJK risks
- accessibility and performance constraints
- observed browser evidence for completion claims

## Expected outputs
- frontend_design_brief/v1
- frontend_initial_generation_contract/v1 when greenfield
- design_system_contract/v1
- design_reference_selection/v1
- reference_packet/v1 when supplied
- frontend_route_state_matrix/v1
- frontend_component_state_inventory/v1
- frontend_implementation_handoff/v1
- accessibility_performance_expectations/v1
- visual_qa_required/v1
- observed_browser_evidence/v1 when observed

## Artifact expectations
- frontend_design_brief/v1 when prepared
- frontend_initial_generation_contract/v1 declares DESIGN.md/design-system work, reference lane, token extraction, reusable primitives, and visual QA path before new UI code
- design_system_contract/v1 with layout, spacing, typography, color, component, motion, and responsive rules
- design_reference_selection/v1 names supplied references or the domain-fit style direction and explicitly avoids copying third-party logos, assets, or brand copy
- frontend_route_state_matrix/v1 with pages, states, viewports, CJK/locale, empty/loading/error, and interaction states
- frontend_component_state_inventory/v1 with default, hover, focus, active, disabled, loading, empty, and error states for reusable primitives
- frontend_implementation_handoff/v1 for the selected executor/runtime
- browser screenshots, accessibility reports, Lighthouse/Core Web Vitals, and visual QA only when observed

## Acceptance criteria
- The target page/component, audience, primary task, references, and quality bar are named.
- Greenfield work includes frontend_initial_generation_contract/v1 before implementation handoff.
- The design_system_contract/v1 covers typography, spacing, palette, components, layout, motion, and responsive rules.
- The frontend_route_state_matrix/v1 covers pages, 375/768/1280-style breakpoints, empty/loading/error, interaction, and CJK/locale risks.
- The frontend_component_state_inventory/v1 covers reusable primitives and their default/hover/focus/active/disabled/loading/empty/error states.
- The handoff names the executor/runtime owner and keeps code, browser, Lighthouse, accessibility, deployment, and visual QA evidence observed-only.
- The next action is prepare_frontend_handoff, route to visual-qa, or report the missing evidence blocker.

## Handoff policy
Keep product framing, reference selection, design-system contract, viewport/state matrix, and implementation brief in Hermes. Record code changes, browser screenshots, Lighthouse/Core Web Vitals, accessibility scans, and visual QA only from executor or wrapper observed evidence.

## Catalog rules
- quality_tier: frontend-design-gated
- contract_source: skills/omh-frontend/SKILL.md:70
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Hold the named bar: what a senior product designer at a top-tier product company (the Linear/Stripe/Supabase class) would sign off on — technically clean but flat output fails it. Load `references/taste-foundations.md`, name one primary taste direction, and reject the anti-slop patterns it lists.
- Catalog Metadata: - Name the model's own default aesthetic before inheriting it — the editorial prior of cream grounds, serif display faces, and muted terracotta accents suits editorial, portfolio, and hospitality briefs and is a failure mode on dashboards, developer tools, fintech, and data-dense UIs. Treat a generic negation ("don't make it look AI", "make it minimal") as unactionable: an override counts only when it carries concrete tokens, a hex palette and a typeface stack recorded in DESIGN.md. Run the review prompts in `references/taste-foundations.md` over framework blue, glass and gradient surfaces, default UI typefaces, bounce easing, blanket shadows, eyebrow/title/description stuffing, uniform column grids, and CJK body under the 14px Korean floor.
- Catalog Metadata: - When the target surface is a terminal UI (TUI), load `references/tui-craft.md` and hold the same bar there: default widgets are scaffolding, not finished UI; borders spent sparingly with spacing and a muted-color ladder doing the hierarchy; one named terminal aesthetic; verification rendered at 80x24 and 120x40 minimum with the pasted output as the screenshot-equivalent.
- Catalog Metadata: - Use references and domain fit to avoid generic AI-looking frontend output; when the user supplies a visual reference, load `references/reference-token-extraction.md` and extract tokens into the contract instead of eyeballing.
- Catalog Metadata: - Prepare a concrete design-system contract before implementation handoff: load `references/design-system-contract.md` and write DESIGN.md before the first component — no component code before the contract exists.
- Catalog Metadata: - Scroll-driven motion is a decision with a bill: load `references/scroll-motion-libraries.md`, take the native path (CSS `scroll-behavior`, scroll-driven animations, `IntersectionObserver`, scroll-snap) unless one interpolated scroll position feeds several consumers, and when a library is chosen (Lenis is the reviewed record) name its reduced-motion branch, anchors, nested scroll, teardown, and INP budget in the contract.
- Catalog Metadata: - Copied component source is the project's to fix: before adopting from a shadcn-style registry, load `references/component-registry-adoption.md` (license, dependencies, reduced motion, ARIA, keyboard/touch, token mapping, one hero effect per view). Theme charts through tokens, not config literals: load `references/chart-styling.md`.
- Catalog Metadata: - State performance as a budget, not an adjective: load `references/web-vitals-budgets.md`, name one metric with its published bar (LCP, INP, CLS), the device and network class it is judged on, the route and load shape, and the baseline captured under that same profile - before the change. A budget chosen after seeing the result describes what happened instead of gating it.
- Catalog Metadata: - After implementation lands on a web surface, load `references/screenshot-loop.md` and require the screenshot iteration loop live-environment-first: capture the running UI at 1440/768/375px, compare against the supplied target or DESIGN.md, list every difference triaged Blocker/High/Medium/Nit with its capture attached, fix, and recapture until the difference list is empty.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-frontend/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-frontend/SKILL.md`
- SHA256: `8469297df68b61ed17919318b6899deac2318260ee437ab06abd3dfe67f75dec`

## Method references
- `omh-frontend/references/chart-styling.md` (pinned `skills/omh-frontend/references/chart-styling.md`)
- `omh-frontend/references/component-registry-adoption.md` (pinned `skills/omh-frontend/references/component-registry-adoption.md`)
- `omh-frontend/references/design-system-contract.md` (pinned `skills/omh-frontend/references/design-system-contract.md`)
- `omh-frontend/references/reference-token-extraction.md` (pinned `skills/omh-frontend/references/reference-token-extraction.md`)
- `omh-frontend/references/screenshot-loop.md` (pinned `skills/omh-frontend/references/screenshot-loop.md`)
- `omh-frontend/references/scroll-motion-libraries.md` (pinned `skills/omh-frontend/references/scroll-motion-libraries.md`)
- `omh-frontend/references/taste-foundations.md` (pinned `skills/omh-frontend/references/taste-foundations.md`)
- `omh-frontend/references/tui-craft.md` (pinned `skills/omh-frontend/references/tui-craft.md`)
- `omh-frontend/references/web-vitals-budgets.md` (pinned `skills/omh-frontend/references/web-vitals-budgets.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: target app, page, route, or component
- Required source input: audience and primary user task
- Required source input: existing design system or missing-system gap
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for frontend: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
