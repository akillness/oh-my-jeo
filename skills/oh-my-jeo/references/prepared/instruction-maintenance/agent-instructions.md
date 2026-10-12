# Prepared guidance: agent-instructions

Family: `instruction-maintenance`  
Category: `planning`  
Phase: `agent-instructions`  
Role: `planner`

## Contract
[omh] Agent instruction file for a repo -- AGENTS.md, CLAUDE.md, a Cursor rule: write or update what an agent cannot derive from the code, inside a marked region, with every command verified or marked unverified and no counts that drift. Use when the user says: agent-instructions, agents.md, claude.md, gemini.md, copilot-instructions.md, .cursorrules, cursor rules, cursor rule.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- agent-instructions
- agents.md
- claude.md
- gemini.md
- copilot-instructions.md
- .cursorrules
- cursor rules
- cursor rule

## Required inputs
- which instruction files exist, where they sit, and which agents read them
- the build, test, lint, and regenerate commands the repository uses
- which files are generated, from what source, and which gate checks them
- the pitfalls that have cost time, each with what it cost
- observed output for every command written into the file

## Expected outputs
- instruction_file_inventory/v1
- command_verification_record/v1
- instruction_region_update/v1
- drift_refusal_note/v1 when a requested line would record a count or a line number

## Artifact expectations
- instruction_file_inventory/v1 lists every instruction file, its path, the agents that read it, and which one is closest to each directory, since the closest file wins
- command_verification_record/v1 marks every command verified, with the observed exit status and when, or unverified, and nothing is written as verified without an observed run
- instruction_region_update/v1 replaces only the text between `<!-- omh:agent-instructions:begin -->` and `<!-- omh:agent-instructions:end -->`, and inserts the markers once when absent, so every hand-written section outside them is left byte-for-byte
- drift_refusal_note/v1 names each requested count, line number, or other value the code already states, and writes the command or the file that derives it instead

## Acceptance criteria
- Every instruction file and its reader are listed.
- Every command is marked verified with an observed run, or unverified.
- Only the marked region changed, and hand-written text is byte-for-byte.
- No count, line number, or value the code already states was written.
- Every generated file names its source, its regenerate command, and its gate.

## Handoff policy
Keep the section plan, the command verification record, and the region update in Hermes. Every command's outcome is recorded only from executor, operator, or wrapper observed output; the file is written by the executor, and only inside its marked region.

## Catalog rules
- Source first step: List every instruction file and which agent reads it before proposing a section.
- Source first step: Run or ask for the observed run of each command before marking it verified.
- Source routing exclusion: The ask is distilling repeated lessons into reviewed rule candidates; use `rules-distill`.
- Source routing exclusion: The ask is a reading path through the codebase for a new engineer; use `codebase-onboarding`.
- Source routing exclusion: The ask is project terminology alignment -- reviewing the terms this project uses and correcting inconsistent vocabulary; use `context`.
- Source routing exclusion: The ask is user-facing product documentation; use `product-docs`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts plan, code-review as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-agent-instructions/SKILL.md`
- SHA256: `acdb8eb6a411cc1e4b0345151fda6d70f443fb0ccf170d037c18b960aeb91fe9`

## Method references
- `omh-agent-instructions/references/instruction-file-method.md` (pinned `skills/omh-agent-instructions/references/instruction-file-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member agent-instructions is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the section plan, the command verification record, and the region update in Hermes. Every command's outcome is recorded only from executor, operator, or wrapper observed output; the file is written by the executor, and only inside its marked region. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
