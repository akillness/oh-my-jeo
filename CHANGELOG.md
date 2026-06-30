# Changelog


## Unreleased

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
