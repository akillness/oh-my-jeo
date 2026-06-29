# OMJ Agent Install Protocol

Canonical install reference for AI agents and operators. Execute top to bottom,
then report the observed result. Normal users should use Hermes chat and
installed skills; `omj` is bootstrap, repair, doctor, and backend verifier
infrastructure.

## Prerequisites

```sh
command -v python3 >/dev/null || echo "MISSING: python3 is required"
command -v git >/dev/null || echo "MISSING: git is required for source installs"
command -v hermes >/dev/null || echo "NOTE: Hermes Agent command not found in PATH"
```

If Hermes is not available, continue only when the target environment uses a
hosted wrapper that manages Hermes separately. Do not claim Hermes-visible
readiness until the target Hermes runtime or wrapper has been checked.

## Step 1: Install OMJ

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | sh
```

The installer prepares the local `omj` command only. It does not run setup,
register Hermes skill directories, install profile packs, or run doctor by
default. Run setup explicitly because it is the repairable, repeatable step:

```sh
omj setup
```

If `command -v omj` is still empty after install, use the absolute command path
printed by the installer or add that directory to `PATH`, then continue with
doctor. Treat this as a command availability warning, not proof that Hermes
registration failed.

Expected local result:

- generated skills are installed under `~/.omj/skills`;
- Hermes config includes that directory in `skills.external_dirs`;
- the managed plugin bridge is installed under `~/.hermes/plugins/omj`;
- normal users can talk to Hermes instead of running backend commands.

## Step 2: Verify

```sh
omj doctor
```

Report:

- `ok`;
- top-level `recommended_next_action`;
- whether the `command_path` check found `omj` on PATH or only an absolute path
  is available;
- any check with `severity: blocking`;
- any check with `severity: warning`;
- whether the target Hermes runtime still needs restart/reload.

Install success means a Hermes-usable skill path is configured and doctor has no
blocking checks. It does not mean Hermes has already reloaded the skills,
loaded the plugin bridge, executed code, reviewed a PR, passed CI, or merged.

For release-candidate verification, add the Hermes CLI smoke. Plan mode is safe
and non-mutating:

```sh
omj release hermes-smoke
```

When the operator explicitly wants to prove the current Hermes profile can
install, list, check, and inspect OMJ, run one live smoke:

```sh
omj release hermes-smoke --live --install-path tap --target-confirmed
```

Use `--install-path setup` instead when the release must prove the `omj setup`
bootstrap path. Passing either live smoke still does not prove a later Hermes
chat session selected OMJ unless that chat response is observed separately.

## Optional Hermes Skill Tap

If the target Hermes environment supports skill taps, this is the native front
door:

```sh
hermes skills tap add akillness/oh-my-jeo
hermes skills install akillness/oh-my-jeo/skills/oh-my-jeo --yes
```

Install direct workflow skills only when the user wants them exposed as explicit
Hermes skill choices:

```sh
hermes skills install deep-interview
hermes skills install ralplan
hermes skills install web-research
hermes skills install feedback-triage
hermes skills install ops-review
hermes skills install code-review
```

The tap path and `omj setup` path should converge on the same user experience:
Hermes can see OMJ guidance and the user talks to Hermes.

## Plugin Bridge And Profile Packs

`omj setup` installs `~/.hermes/plugins/omj` and lets doctor verify local
manifest, import, and register smoke checks. It does not patch Hermes core,
implement Discord or Slack transports, start a network service, or prove Hermes
loaded the plugin. Runtime plugin use must be observed separately.

Profile packs are setup choices, not curl-download choices. Add them when setup
runs:

```sh
omj setup --profile-pack cto-loop
```

## First Hermes Prompt

After install and any required Hermes restart/reload, try:

```text
Use OMJ request-to-handoff for: I want to safely add a feature to this repo.
```

Expected behavior:

- Hermes explains why `request-to-handoff` is the right first workflow;
- Hermes names the responsible role such as `planner` or
  `handoff-guide`;
- Hermes gives the next action, such as clarify, accept plan, choose executor,
  or show status;
- Hermes keeps prepared handoff separate from observed execution evidence.

## Failure Report Template

```text
OMJ install result:
- install command:
- omj setup output summary:
- omj doctor ok:
- recommended_next_action:
- blocking checks:
- warning checks:
- Hermes restart/reload performed:
- first Hermes prompt tried:
- observed Hermes response:
```

Do not ask the user for Discord, Slack, GitHub, Vercel, Supabase, or deploy
credentials for the normal OMJ install path.
