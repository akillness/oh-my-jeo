# Prepared guidance: codebase-uml

Family: `code-intelligence`<br>
Category: `planning`<br>
Phase: `codebase-uml`<br>
Role: `planner`

## Contract
[omh] Architecture picture of a codebase: turn a repository into one readable, interface-level PlantUML architecture picture - packages or modules, the public symbols other units actually import, bounded import edges - and get it rendered to a single PNG a chat surface can show. Use when the user says: codebase-uml, codebase uml, uml, plantuml, uml diagram, class diagram, package diagram, module diagram.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- codebase-uml
- codebase uml
- uml
- plantuml
- uml diagram
- class diagram
- package diagram
- module diagram

## Required inputs
- repo root or current workspace
- view: whole repo at package level, one area by `--focus <path>`, or module level for a subsystem
- delivery target (chat attachment, PR, doc) which fixes the format: PNG for chat, SVG only when asked
- renderer readiness from the command's render plan (`plantuml` on PATH, or `PLANTUML_JAR` plus `java`)

## Expected outputs
- codebase_uml/v1 model (units, interfaces, edges, omissions) via `omh codegraph uml --json`
- PlantUML source written by `omh codegraph uml --output <file>.puml`
- uml_render_plan/v1 naming the exact render command or the blocker
- one rendered PNG (or SVG on request) attached to the reply, with the omissions legend visible
- not-evidence boundary

## Artifact expectations
- codebase_uml/v1 with `view` (level, depth, focus, caps), `nodes` carrying fan-in-ranked public interfaces, weighted `edges`, `layout` hardening, and `omissions` counts
- uml_render_plan/v1 with `status`, `renderer`, `layout_engine`, `command`, `blockers`, and `notes`
- the rendered image path only after the render command is observed to exit 0 and the file exists

## Acceptance criteria
- The view (package, focus, or module) matches the question asked, and only one view was rendered unless more were requested.
- The render command and its observed result are recorded before the image is claimed.
- The legend's omissions were read back to the user in the reply.
- Follow-up exploration used narrower generated views, not recollection of the first picture.

## Handoff policy
Keep diagram scoping, the `omh codegraph uml` source generation, and the render command in Hermes; the render runs through Hermes' own terminal tool and the image is attached by the chat surface. A generated `.puml` is prepared context; the picture exists only when the render command's exit status and output file are observed, and neither is architecture proof, review, CI, or merge evidence.

## Catalog rules
- Source routing exclusion: The user wants the local code index refreshed or a task-scoped handoff pack, not a picture; use `codegraph-refresh`.
- Source routing exclusion: The user wants a narrative first-read tour, reading path, or glossary; use `codebase-onboarding`.
- Source routing exclusion: The user wants a summary card, thumbnail, or explainer image of a PR, meeting, or release rather than a structural diagram; use `img-summary`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts plan as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-codebase-uml/SKILL.md`
- SHA256: `2342c510401082490fb87dca8c046d63d8b19c8ae2dcbef0c04314d8df544487`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member codebase-uml is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep diagram scoping, the `omh codegraph uml` source generation, and the render command in Hermes; the render runs through Hermes' own terminal tool and the image is attached by the chat surface. A generated `.puml` is prepared context; the picture exists only when the render command's exit status and output file are observed, and neither is architecture proof, review, CI, or merge evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
