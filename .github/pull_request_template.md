## Feature Report

### What Changed

-

### Why This Exists

-

### User / Operator Impact

-

### How It Works

-

### Files And Contracts Touched

-

## Validation

- [ ] `python3 -m unittest discover -s tests`
- [ ] `python3 -m compileall src`
- [ ] `python3 -m omj.cli docs workflows --check`
- [ ] `python3 -m omj.cli harness validate`
- [ ] `python3 -m omj.cli release checklist --json`
- [ ] `python3 -m omj.cli release hermes-smoke`
- [ ] `omj --help`
- [ ] `omj --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke release hermes-smoke --install-path setup --omj-command omj --include-command-smoke`
- [ ] Relevant workflow-learning review queue smoke, when learning contracts changed:
- [ ] Relevant dry-run or smoke command:
- [ ] Manual Hermes/TUI check, or explicit reason it was not run:

## Risk

-

## Compatibility / Rollout

-

## Release / Claims

- [ ] Release-channel impact considered (`stable`, `preview`, or `local`)
- [ ] Runtime/native capability claims are backed by evidence or marked as not observed
- [ ] Known manual Hermes checks are listed, including any `omj release hermes-smoke --live` gap

## Follow-Up

-
