# Release Process

This project ships a conservative Hermes skill layer. A release is ready only
when install behavior, generated workflow docs, runtime evidence validation, and
public claims are all checked.

## Channels

| Channel | Purpose | Install target |
| --- | --- | --- |
| `stable` | Pinned user installs and support reproduction | Hermes skill tap plus published Git tag archive such as `v<version>` |
| `preview` | Latest `main` for early testing | Hermes skill tap plus `main` branch archive |
| `local` | Maintainer smoke tests from local fixtures | Explicit local source or package URL |

Hermes-native skill install:

```sh
hermes skills tap add akillness/oh-my-jeo
hermes skills install akillness/oh-my-jeo/skills/oh-my-jeo --yes
```

Pinned stable install:

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | OMJ_CHANNEL=stable OMJ_VERSION=<version> sh
```

Preview install:

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | sh
```

Preview update with an auditable source ref:

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | OMJ_SOURCE_REF=main@<sha> sh
```

Custom archive:

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | OMJ_PACKAGE_URL=https://github.com/akillness/oh-my-jeo/archive/refs/tags/v<version>.zip sh
```

Advanced one-shot setup compatibility smoke:

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | OMJ_RUN_SETUP=1 OMJ_PROFILE_PACKS=cto-loop OMJ_RUN_DOCTOR=0 sh
```

## Required Checks

Run before tagging:

```sh
python3 -m unittest discover -s tests
python3 -m compileall src
python3 -m omj.cli docs workflows --check
python3 -m omj.cli harness validate
python3 -m omj.cli release checklist --json
python3 -m omj.cli release skill-content-smoke --json
python3 -m omj.cli release product-readiness --version 1.0.1 --json
python3 -m omj.cli release evidence-bundle --version 1.0.1 --write --json
python3 -m omj.cli cases demo --all --json
python3 -m omj.cli cases artifact --all --json
python3 -m omj.cli cases replay --json
python3 -m omj.cli cases readiness --json
python3 -m omj.cli --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke learning review --all
python3 -m omj.cli --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke install --dry-run --channel stable --version 1.0.1
python3 -m omj.cli --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke setup --dry-run --channel stable --version 1.0.1
python3 -m omj.cli --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke probe
python3 -m omj.cli release hermes-smoke
python3 -m omj.cli release install-smoke
omj release install-smoke --live --repo-root "$PWD" --install-script "$PWD/install.sh"
omj --help
omj --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke release hermes-smoke --install-path setup --omj-command omj --include-command-smoke
uv build
python3 -m venv /tmp/omj-wheel-smoke
/tmp/omj-wheel-smoke/bin/python -m pip install --upgrade dist/oh_my_jeo-1.0.1-py3-none-any.whl
/tmp/omj-wheel-smoke/bin/omj --help
/tmp/omj-wheel-smoke/bin/omj release skill-content-smoke --json
/tmp/omj-wheel-smoke/bin/omj --omj-home /tmp/omj-wheel-home --hermes-home /tmp/hermes-wheel-home release hermes-smoke --install-path setup --omj-command /tmp/omj-wheel-smoke/bin/omj --include-command-smoke
/tmp/omj-wheel-smoke/bin/omj --omj-home /tmp/omj-wheel-home --hermes-home /tmp/hermes-wheel-home setup --dry-run --channel stable --version 1.0.1
OMJ_PYTHON=/tmp/omj-wheel-smoke/bin/python OMJ_PACKAGE_URL=file://$PWD/dist/oh_my_jeo-1.0.1-py3-none-any.whl OMJ_VENV_DIR=/tmp/omj-installer-venv OMJ_BIN_DIR=/tmp/omj-installer-bin sh install.sh
/tmp/omj-installer-bin/omj --omj-home /tmp/omj-installer-home --hermes-home /tmp/omj-installer-hermes setup --dry-run
```

The checklist command renders the same release gates as a deterministic
`release_readiness_checklist/v1` contract:

```sh
omj release checklist --version 1.0.1
omj release checklist --version 1.0.1 --json
```

It is plan-only: it does not run checks, mutate Hermes, create tags, or publish
GitHub releases. Treat it as the operator-facing index of the evidence that must
be attached before a stable tag.

The checklist also gates the G1-G10 use-case demo cards through
`omj cases demo --all --json`. That proves OMJ can render wrapper-safe
use-case projections with route, action, status-card, and evidence-boundary
metadata. It is not evidence that cron, connectors, files, memory updates,
executors, reviews, CI, merges, or delivery actually ran.

It also gates the G1-G10 use-case artifact bundle through
`omj cases artifact --all --json`. That proves OMJ can render local prepared
runbooks with operator steps and proof surfaces for each use case. It is not
evidence that those runbooks were accepted, executed, delivered, reviewed,
verified, merged, or billed by any runtime.

The same gate replays G1-G10 natural-language use-case fixtures through
`omj cases replay --json`. That proves deterministic routing for the checked-in
synthetic English/Korean operator corpus. It is not evidence that a live Hermes
profile selected the route in chat or that any connector, executor, review, CI,
merge, delivery, or billing event happened.

The readiness rollup, `omj cases readiness --json`, combines the catalog,
demo-card, artifact-bundle, replay, and optional local artifact-store states
into one operator-readable card. It should be ready before a release, but it
still proves only local deterministic contracts, not live Hermes selection or
runtime execution.

The product readiness rollup sits one level above use cases:

```sh
omj release product-readiness --version 1.0.1 --json
```

It checks the generated skill content, G1-G10 readiness, parity matrix, and
release checklist shape in one operator-readable card. It is useful for release
notes and maintainer handoff, but it is still local deterministic evidence only:
it does not run the checklist, mutate Hermes, dispatch executors, review code,
pass CI, merge, deliver messages, or spend provider budget.

When the local release story is ready, write an attachable evidence bundle:

```sh
omj release evidence-bundle --version 1.0.1 --write --json
```

The bundle writes `omj_release_evidence_bundle/v1` under
`.omj/runtime/release-evidence/` with the checklist, product readiness,
skill-content smoke, use-case readiness, and parity snapshots. It is useful for
release PRs and notes, but it is still local deterministic evidence only; live
Hermes smoke, CI, review, merge, delivery, and GitHub release publication must
be observed separately.

## Hermes CLI Install Smoke

The release gate includes a deterministic smoke plan for the real Hermes CLI
path. Plan mode is safe for CI because it does not touch the current Hermes
profile:

```sh
python3 -m omj.cli release hermes-smoke
```

The installer gate separately checks the user-facing `curl ... | sh` entry
point without depending on curl or GitHub. Plan mode reports the isolated target
and remains unobserved:

```sh
python3 -m omj.cli release install-smoke
```

Live mode executes the local `install.sh` in a temporary HOME with an isolated
OMJ virtual environment and bin directory. It installs from the local checkout,
does not run setup through the installer, and then runs installed-command
smoke. It does not mutate the operator's real Hermes profile or prove a later
Hermes chat selected OMJ:

```sh
omj release install-smoke --live --repo-root "$PWD" --install-script "$PWD/install.sh"
```

The plan includes two release-contract subchecks:

- `installed_command_smoke`: first resolves the installed `omj` command path,
  then proves the console script can run `omj --help` and render the setup-path
  smoke plan.
- `first_use_status_smoke`: documents the first Hermes chat/status path and
  locks that pre-handoff status cards do not expose executor open/result
  actions.

Run the installed command smoke in CI or a release shell after installing OMJ:

```sh
command -v omj
omj --help
omj release skill-content-smoke --json
omj release product-readiness --version 1.0.1 --json
omj release evidence-bundle --version 1.0.1 --write --json
omj --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke release hermes-smoke --install-path setup --omj-command omj --include-command-smoke
```

`release skill-content-smoke` is non-mutating package-content evidence. It
checks that the command package can render the router awareness primer and the
generated workflow context rails that keep direct skill invocation inside the
broader OMJ model. It also checks all-skill awareness lane coverage, full
capability manifest context, bundled role context, standalone plugin capability
fallback coverage, playbook capability context, fallback routing/context/boundary
fields, bounded prompt context budgets, and bounded capability payload budgets so
the shared OMJ mental model stays present without becoming prompt bloat or
manifest bloat. It does not prove Hermes loaded those skills or selected them in
chat.
In short, this gate preserves bounded context budgets while still giving Hermes
enough OMJ workflow context to route well.

For release candidates, run exactly one live smoke against the target Hermes
profile and paste the JSON result into the release note. Use the native tap
path when Hermes skill taps are available:

```sh
omj release hermes-smoke --live --install-path tap --target-confirmed
```

Use the bootstrap path when validating the installer-managed `skills.external_dirs`
route instead:

```sh
omj release hermes-smoke --live --install-path setup --target-confirmed
```

For an isolated smoke profile, bind the target home explicitly instead of
confirming the ambient default profile:

```sh
omj --omj-home /tmp/omj-smoke --hermes-home /tmp/hermes-smoke release hermes-smoke --live --install-path setup
```

The live smoke runs the selected Hermes install path plus:

```sh
hermes skills tap list
hermes skills list --enabled-only
hermes skills check oh-my-jeo
hermes skills inspect akillness/oh-my-jeo/skills/oh-my-jeo
```

Passing the tap smoke means Hermes CLI install/list/check/inspect commands
succeeded for the target profile. Passing the setup smoke means OMJ managed
skill setup, Hermes list/check visibility, and `omj doctor` succeeded for the
target profile. It still does not prove a later Hermes chat session selected
OMJ unless that chat response is observed separately.

Runtime evidence smoke:

```sh
run_json="$(python3 -m omj.cli --omj-home /tmp/omj-smoke runtime record --skill oh-my-jeo --harness coding-handling --status started)"
run_id="$(printf '%s' "$run_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["run"]["run_id"])')"
python3 -m omj.cli --omj-home /tmp/omj-smoke runtime delegate --run "$run_id" --requested --not-observed --result not_observed
python3 -m omj.cli --omj-home /tmp/omj-smoke runtime wrapper --run "$run_id" --prompt-dispatched --response-observed --completion-status completed
python3 -m omj.cli --omj-home /tmp/omj-smoke runtime validate --run "$run_id"
python3 -m omj.cli --omj-home /tmp/omj-smoke runtime export --redacted
```

## Release Notes Must Include

- Release version and channel.
- Hermes skill tap/install wording and bootstrap install target used for smoke testing.
- Update path tested.
- Workflow docs generation status.
- Harness catalog validation status.
- Runtime validation status.
- Workflow learning review queue status when workflow-learning contracts changed.
- Capability probe status.
- Install script smoke status, including whether it was plan-only or live.
- Hermes CLI install smoke status, including whether it was plan-only or live.
- Plugin bundle status when `omj setup` changed.
- GitHub Pages workflow status when public site copy changed.
- Known manual Hermes checks that could not be automated.
- Any public claim that depends on wrapper evidence rather than Hermes-native
  capability evidence.

## Known Gap Language

Use explicit proof-boundary language:

- "Prompt-level routing guidance" when only installed skills are involved.
- "Wrapper-observed" when evidence comes from a bot or shell wrapper.
- "Not observed" when specialist delegation metadata is unavailable.

Do not claim native Hermes runtime use from plugin installation alone.
`plugin_distribution_ready` means the local bundle exists and passed local
import/register smoke; `native_integration_claim_ready` still requires observed
Hermes active runtime-load, hook/tool-use, or status-query evidence. Session-end
and plugin-unload observations are historical evidence only.
