# Prepared guidance: model-finetuning

Family: `model-finetuning`<br>
Category: `planning`<br>
Phase: `model-finetuning`<br>
Role: `planner`

## Contract
[omh] Fine-tuning a model on your own data -- SFT, DPO, RLVR or a LoRA adapter: decide first whether prompting or retrieval already closes the gap, choose the method from the data you have, and promote a checkpoint only when it beats the untuned baseline on a held-out eval. Use when the user says: model-finetuning, model finetuning, model fine-tuning, fine-tune a model, fine-tune the model, fine tune a model, fine tune the model, fine-tune.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- model-finetuning
- model finetuning
- model fine-tuning
- fine-tune a model
- fine-tune the model
- fine tune a model
- fine tune the model
- fine-tune

## Required inputs
- the task the model fails at, and the held-out examples that show the failure
- what prompting, few-shot examples, or retrieval were already tried, and what they scored
- the data available: demonstrations, ranked or paired preferences, or answers a program can check
- the base model, its license, and the compute or provider the operator will train on
- observed eval scores for the untuned baseline and every candidate checkpoint

## Expected outputs
- finetune_decision/v1
- training_method_choice/v1
- training_data_plan/v1
- baseline_comparison/v1
- checkpoint_promotion_gate/v1

## Artifact expectations
- finetune_decision/v1 names the measured gap on the held-out eval and what prompting, few-shot, and retrieval scored against it, and returns `do_not_finetune` when one of them closes the gap -- a complete outcome, reached before any training step
- training_method_choice/v1 picks SFT, DPO, or RLVR from the shape of the data -- demonstrations, preference pairs, or a verifiable reward -- and full weights or an adapter, and names the failure mode of the method chosen
- training_data_plan/v1 names each source and its license, the dedupe and filtering, and a held-out split drawn before training and checked for overlap with the training set
- baseline_comparison/v1 runs the same held-out eval on the untuned baseline and each candidate, per metric, plus a regression check on general capability the task does not cover
- checkpoint_promotion_gate/v1 promotes a checkpoint only when it beats the untuned baseline by a stated margin with no regression past a stated tolerance, and otherwise keeps the baseline serving

## Acceptance criteria
- The fine-tune decision is stated, and `do_not_finetune` was considered first.
- The method is chosen from the data's shape and its failure mode is named.
- The held-out split was drawn before training and checked for overlap.
- Promotion cites the same eval observed on the untuned baseline and the candidate.
- OMH ran nothing, and every score cites observed output or is marked unverified.

## Handoff policy
Keep the fine-tune decision, the method choice, the data plan, the baseline comparison, and the promotion gate in Hermes. Losses, eval scores, and comparisons are recorded only from executor, operator, or wrapper observed output; OMH never launches a training run, calls a model, or runs an eval.

## Catalog rules
- Source first step: Ask what the untuned model and the best prompt score on the held-out examples before discussing any method.
- Source first step: Ask what shape the data has -- demonstrations, preference pairs, or answers a program can check.
- Source routing exclusion: The ask is onboarding a new model generation into OMH's routing, calibration, or pricing; use `model-optimization`.
- Source routing exclusion: The ask is serving an existing model behind an endpoint or benchmarking that endpoint; use `inference-serving`.
- Source routing exclusion: The ask is building an application on top of a hosted model -- RAG, structured output, prompt versions; use `llm-app-dev`.
- Source routing exclusion: The ask is learning from an OMH run, a missed route, or a skill improvement candidate; use `workflow-learning`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts plan, best-practice-research as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-model-finetuning/SKILL.md`
- SHA256: `3a888f3b0c821a4b2c9844ceab6ec259e16b50f1a096e49a3d6d8522c38610e8`

## Method references
- `omh-model-finetuning/references/finetuning-method.md` (pinned `skills/omh-model-finetuning/references/finetuning-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member model-finetuning is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the fine-tune decision, the method choice, the data plan, the baseline comparison, and the promotion gate in Hermes. Losses, eval scores, and comparisons are recorded only from executor, operator, or wrapper observed output; OMH never launches a training run, calls a model, or runs an eval. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
