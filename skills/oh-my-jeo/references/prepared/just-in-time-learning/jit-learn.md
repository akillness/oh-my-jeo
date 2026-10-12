# Prepared guidance: jit-learn

Family: `just-in-time-learning`  
Category: `research`  
Phase: `learning-target`  
Role: `researcher`

## Contract
[omh] Blocked on a project by a knowledge gap: just-in-time learning workflow: select and confirm an immediate learning target, research credible sources, and prepare an application-first brief without popularity ranking. Use when the user says: jit-learn, learn next, learn now, blocker-specific learning target, highest-leverage learning target, immediate learning payoff, immediately applicable learning brief, source-backed learning brief.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- jit-learn
- learn next
- learn now
- blocker-specific learning target
- highest-leverage learning target
- immediate learning payoff
- immediately applicable learning brief
- source-backed learning brief
- 학습 주제
- 도움 되는 학습 주제
- 당장 적용할 학습 목표
- 책 팟캐스트 크리에이터 강의 학습 브리프

## Required inputs
- reviewed context
- urgency
- current level
- application window
- time/format constraints

## Expected outputs
- confirmed target statement: Learn X now so I can do/decide Y in context Z by T.
- source-backed Markdown learning brief
- Books section, including an explicit no-qualifying-candidate reason when empty
- Podcasts section, including an explicit no-qualifying-candidate reason when empty
- Creators section, including an explicit no-qualifying-candidate reason when empty
- Courses section, including an explicit no-qualifying-candidate reason when empty
- for every recommendation: title, format, creator/publisher, link, source class, time to first value, specific fit now, first application, and caveats
- competing learning targets, filtered-out defaults, unresolved gaps, and one recommended next action

## Artifact expectations
- prepared Markdown learning brief with observed source links and explicit retrieval gaps when a wrapper captures it

## Acceptance criteria
- At least one confirmation question was answered, no turn contained more than one question, and the shared interview ceiling was respected.
- Urgency/trigger, current level, application window, and the target statement are explicit before research.
- Every admitted recommendation is source-gated and popularity signals did not influence admission or rank.
- Books, Podcasts, Creators, and Courses are present with complete fields or an honest empty-section reason.
- Competing targets, filtered-out defaults, unresolved gaps, and one starting action are visible.
- The final status says the brief is prepared and does not claim consumption, learning, application, progress, or blocker resolution.

## Handoff policy
Keep reviewed-context interpretation, the bounded one-question-at-a-time interview, target selection, source research, and Markdown brief preparation in Hermes. Do not create a learner profile, take an external action, or claim that a recommendation was consumed, learned, applied, or resolved the blocker.

## Catalog rules
- quality_tier: source-gated
- contract_source: skills/omh-jit-learn/SKILL.md:71
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-jit-learn/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-jit-learn/SKILL.md`
- SHA256: `3097eda0864c1c91e4d9bc6fbdbe30f527ff45a328f8dbda587247a8fedf4b4b`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: reviewed context
- Required source input: urgency
- Required source input: current level

## Evidence boundary
prepared_not_observed for jit-learn: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
