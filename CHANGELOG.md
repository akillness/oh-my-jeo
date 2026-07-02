# Changelog


## Unreleased

- OMJ is now Hermes-first out of the box. A plain `omj setup` (interactive or
  `--yes`) records **Hermes** as the default coding owner
  (`default_executor: hermes`, `dispatch_policy: prepare_only`) instead of
  `choose`; the interactive wizard lists Hermes as option 1; and the
  `solo-operator` operating model defaults to the Hermes runtime handoff.
  Zero-config chat/plan/delegate interactions resolve to a prepared Hermes
  runtime handoff (`executor_resolution.source: hermes_baseline`) instead of
  demanding an executor choice; storing `--default-executor choose` restores
  ask-every-time behavior. Bare `omj` now opens with a local Hermes-first
  status block (runtime detection via `hermes --version` plus the recorded
  default owner) — detection only, never an install. `coding delegate`,
  `loop start-card`, `demo orchestration`, the HUD idle label, the menubar
  fallback, and the plugin status summary all follow the same Hermes
  baseline. Prepared-vs-observed boundaries are unchanged: the Hermes
  runtime handoff stays `prepared_not_observed` until wrapper evidence
  exists, and the Hermes runtime install remains opt-in
  (`omj hermes install --apply`, `omj setup --with-hermes`).

## 1.3.1 - 2026-07-02

- Fixed unbounded growth of the global observation journal
  (`runtime/journal/events.jsonl`): every lifecycle event ever recorded for
  the life of an OMJ home directory was appended to a single file that was
  never rotated or capped, and both writes (`append_observation_event`
  re-reads the whole file to validate event ordering) and reads (HUD polling,
  `omj hud --watch`, status/journal projection) fully re-parsed it every
  time. During a long persistent workflow (e.g. `ralph`) this made
  per-operation memory/CPU cost grow without bound for as long as the
  process or a `--watch` poller kept running -- observed as a steady memory
  increase over the session. The journal is now trimmed to the most recent
  `OBSERVATION_JOURNAL_EVENT_LIMIT` (2000) events, oldest-first, after every
  append, mirroring the `queue_trimmed_count`/`feedback_trimmed_count`
  bounded-history convention already shipped for the `loop` workflow in
  1.2.1. See `_trim_observation_journal` in `src/workflows/observation_journal.py`.


## 1.3.0 - 2026-07-01

- Coding-delegation prompts now embed reviewed project memory as literal
  prompt text: when a coding handoff carries a `memory_recall_pack`, OMJ
  appends a hardened `<project_memory>` block onto the prepared
  `prompt_template` (and `*_prompt` fields), so Codex/Claude Code/generic
  executor prompts actually contain prior-session learnings instead of only a
  JSON sidecar. Ports jeo-code's `memoryPromptSection`/`frameMemory`
  convention: `failed_attempt` records render under `## Failed Attempts`
  ahead of every other record (matching `omj memory recall`'s failure-first
  order), the block is framed as DATA, embedded `<project_memory>` tags in
  captured text are neutralized, and the block is char-capped. Persisted
  lifecycle/runtime artifacts strip the block back out of the stored
  `prompt_template` so persisted records still keep only a compact recall
  summary, matching the existing `included_records` redaction. See
  `render_memory_prompt_section` in `src/workflows/memory.py` and
  `docs/MEMORY.md`.
- Every coding-delegation prompt template now carries a failure-capture nudge
  telling the selected executor to run
  `omj memory record-failure "<approach>" --cause "<why>"` itself if the
  delegated task stalls or fails, before finishing -- closing the loop from
  "prompt tells you about past failures" to "prompt also tells you to record
  new ones."
- The OMJ MCP bridge (`omj mcp serve`) now exposes the same failure-first
  memory loop as two allowlisted tools: `omj_memory_recall` (query-relevant
  `failed_attempt` first, same ordering as `omj memory recall`) and
  `omj_memory_record_failure` (deterministic, no-LLM dead-end capture, same
  review-gate as the CLI). `omj mcp manifest`, `omj mcp config-recipe`, and
  `omj setup --with-mcp` now report all five bridge tools instead of three;
  the Codex TOML recipe's `enabled_tools` list is generated from the live
  tool registry so it can no longer drift out of sync. See
  `docs/ARCHITECTURE.md` and `docs/MEMORY.md`.



## 1.2.1 - 2026-07-01

- Fixed unbounded growth of the `loop` workflow's persisted runtime state:
  `cycle["runtime"]["queue"]` and the `cycle["cycles"]` feedback history now
  trim their oldest resolved entries once a 200-item bound is exceeded
  (`queue_trimmed_count` / `feedback_trimmed_count`), instead of growing the
  on-disk JSON without limit across long-running loop sessions.
- Fixed `tick_loop_runtime` enqueuing a duplicate queue item and racing the
  cycle phase forward on every tick even while the loop was still parked on
  an unresolved `prepared_not_observed`, `blocked_by_permission`, or
  `blocked_by_wait` item. Repeated ticks against a blocked loop now just
  increment `runtime["skipped_tick_count"]` and refresh `phase`/`next_action`
  without enqueuing a duplicate; a real advancing tick resets the counter.
- Added a `stalled_repetition` failure mode that surfaces a warning in
  `loop_status_card/v1` once a loop has been ticked 3+ times without the
  pending queue item being observed/resolved, instead of the stall staying
  silently invisible. See `src/workflows/goal_loop.py`.


## 1.2.0 - 2026-07-01

- Ported jeo-code's failure-first (OKF) memory philosophy into OMJ project
  memory: added a first-class `failed_attempt` record type and a deterministic,
  no-LLM `omj memory record-failure "<approach>" --cause "<why>"` capture path
  (also `omj memory capture --type failed_attempt`). Captured dead ends stay
  bounded, redacted, and pass through the normal review-first / auto-safe gate.
- `omj memory recall` now surfaces a query-relevant `failed_attempt` ahead of
  every other record (`failure_first` flag), gated on a genuine query token/tag
  hit so an unrelated dead end never crowds out relevant context. Failed
  attempts get a 90-day staleness default and no forced TTL.
- The `memory-keeper` role now owns failure-first dead-end capture; regenerated
  `docs/ROLES.md`, `roles/memory-keeper.md`, and the bundled
  `role-memory-keeper.md` reference. Documented the model in `docs/MEMORY.md`.

- `install.sh` now bootstraps Hermes by default (`OMJ_AUTOPILOT=1`): a single
  `curl ... | sh` installs the `omj` command, registers the managed skills with
  Hermes, runs the upstream Hermes runtime installer if it is missing (network,
  mutating), and verifies with `omj doctor`. Set `OMJ_AUTOPILOT=0` to install the
  command only.
- Added `omj setup --autopilot/--no-autopilot`: a one-shot, non-interactive
  bootstrap that implies `--with-hermes`, runs the runtime install, and ends in a
  doctor health check (`steps.autopilot`) reported honestly as `verified` or
  `needs_attention`.
- The setup summary now surfaces the Hermes runtime install outcome and the
  autopilot verification result (en/ko/ja/zh).
- The doctor step in `install.sh` is no longer an install gate: a warning (for
  example a still-missing Hermes runtime) no longer aborts an otherwise
  successful install under `set -e`.

## 1.1.0 - 2026-06-29

- Ported the jeo-code spec-first workflow disciplines onto OMJ's routing and
  evidence-boundary layer: `deep-interview` now scores ambiguity and freezes an
  immutable requirements seed (acceptance criteria + non-goals) at ambiguity
  ≈ 0.2 or less.
- Strengthened role contracts in `src/catalogs/roles.py`: planner keeps
  contested decisions explicit (disagreement-preserving), handoff-guide owns
  ordered subgoals with failure feed-forward, and reviewer emits a structured
  terminal verdict (`CLEAR/WATCH/BLOCK` readiness, `APPROVE/COMMENT/REQUEST-CHANGES`
  review) with a severity + evidence floor — APPROVE is review-approved, not
  merged, and an open CRITICAL/HIGH forces BLOCK/REQUEST-CHANGES.
- Added `docs/WORKFLOW_PIPELINE.md` (jeo-code comparison + gap-closure table)
  and a concise `assets/omj-spec-pipeline.svg` visualization.
- Drastically refreshed `README.md`: spec-first pipeline section, SVG diagram,
  CI/release/tests badges.

## 1.0.0 - 2026-06-09

- Added the initial `omj` installer and Hermes skill workflow pack.
- Added a direct `src/` package layout for future growth.
- Added generated routing catalog and rendered skill content.
- Added open-source project operations files and GitHub templates.
