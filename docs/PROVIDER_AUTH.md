# Provider-Auth Readiness (metadata-only)

OMJ is a Hermes-native wrapper orchestration layer, not an LLM router or network
service. Authentication and model routing belong to the selected coding owner
(`codex`, `claude-code`, `hermes`, an oh-my runtime, or a generic executor), not
to OMJ.

The provider-auth surface borrows the *provider taxonomy* used by coding
runtimes such as `jeo-code` and turns it into executor-neutral, metadata-only
descriptors plus a host-configuration diagnostic. It exists so Hermes can
explain which credentials a chosen coding owner needs and whether the host
appears configured — without OMJ ever logging in, calling a model API, or
touching the network.

## What it covers

Borrowed taxonomy, mirrored as descriptors in `src/catalogs/provider_auth.py`:

- OAuth providers: Anthropic (Claude Pro/Max), OpenAI (ChatGPT/Codex), Google
  (Gemini Code Assist), and Antigravity.
- Local keyless endpoints: LM Studio (`http://localhost:1234/v1`) and Ollama
  (`http://localhost:11434`, override via `OLLAMA_HOST`).
- OpenAI-compatible cloud API providers (api-key): xAI, Moonshot (Kimi), Groq,
  DeepSeek, Mistral, OpenRouter, Together, Cerebras, Fireworks, NVIDIA, and
  Hugging Face. Add another by adding one catalog row.

Each descriptor records the auth kind (`oauth` / `api_key` / `local_endpoint`),
the host environment variables that signal configuration, the default endpoint,
which OMJ coding owners can consume it, and the login hint.

## Use

```sh
omj providers list
omj providers inspect anthropic
omj providers inspect lmstudio
omj providers doctor
omj providers doctor --json
```

`omj providers doctor` reports host configuration using environment-variable
**presence only**:

- `configured` — a required API key env var is present.
- `missing` — an api-key provider with no env var set.
- `host_managed` — an OAuth credential owned by the runtime's own store; OMJ does
  not read it. An API-key env override (e.g. `ANTHROPIC_API_KEY`) is the only
  host-detectable signal and flips `configured` to true without proving the
  OAuth login itself.
- `local_default` / `local_override` — a keyless local endpoint at its default
  URL, or overridden via env. Reachability is **not** checked.

## Capability boundary

The diagnostic reports environment-variable presence only. It never reads or
echoes secret values, never contacts a provider, and is not authentication,
login, reachability, or successful-inference evidence. Provider-auth descriptors
are prepared context, not execution, review, CI, merge-readiness, or merge
evidence.
