# Prepared guidance: prompt-import-readiness

Family: `external-and-provider-readiness`<br>
Category: `prompt`<br>
Phase: `prompt-import-readiness`<br>
Role: `guide`

## Contract
[omh] Importing prompt files for Hermes: prompt import readiness - review and normalize external CLI-agent prompt files before offering slash-command candidates; use external-connector-readiness for plugin or API adoption and toolbelt-readiness for missing runtime capabilities. Use when the user says: prompt-import-readiness, prompt import readiness, slash prompt import, slash prompts import, slash command prompt import, prompt library import, prompt folder import, prompt directory import.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- prompt-import-readiness
- prompt import readiness
- slash prompt import
- slash prompts import
- slash command prompt import
- prompt library import
- prompt folder import
- prompt directory import

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- prompt_import_readiness_card/v1
- prompt_compatibility_audit/v1 for explicitly named local files
- prompt_source_inventory/v1
- prompt_format_matrix/v1
- argument_interpolation_policy/v1
- slash_command_collision_report/v1
- prompt_trust_review/v1
- prompt_import_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- prompt_import_readiness_card/v1 metadata-only wrapper card when prepared
- prompt_compatibility_audit/v1 with bounded source metadata, format classification, argument syntax, collisions, and review reasons for explicitly named local files
- prompt_source_inventory/v1 with source directory, agent family, file count, format claim, and review state
- prompt_format_matrix/v1 separating YAML frontmatter, TOML frontmatter, raw markdown/text, and unsupported formats
- argument_interpolation_policy/v1 for $ARGUMENTS, $1-$9, {{args}}, named placeholders, escaping, and missing argument handling
- slash_command_collision_report/v1 with command names, aliases, existing Hermes commands, and conflict resolution policy
- prompt_trust_review/v1 with source trust, prompt-injection risk, secret leakage risk, license/source notes, and review owner
- prompt_import_manifest/v1 only when file reads, parsed prompts, generated slash-command candidates, or dry-run output are observed

## Acceptance criteria
- Prompt sources, agent family, expected file formats, argument syntax, slash-command names, trust level, and stop condition are explicit.
- Explicit-path audit reads and compatibility results are observed only in their audit output; source discovery, command registration, prompt mutation, slash-command activation, and dry-run execution remain marked not_observed.
- Route broad candidate discovery to skill-scout, prompt/tool safety to security-safety-review, missing CLIs or directories to toolbelt-readiness, and approved implementation to a selected executor handoff.
- Imported prompts, generated command files, registry updates, and dry-run results are reported only from observed prompt-import evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-prompt-import-readiness/SKILL.md`
- SHA256: `bf93aea9e50cfd8abc0b24809f00540786039e375935b404c1f0070b8253229d`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member prompt-import-readiness is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
