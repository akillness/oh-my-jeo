"""Provider-auth readiness catalog (metadata-only).

OMJ is a Hermes-native wrapper orchestration layer, not an LLM router or network
service. This catalog borrows the *provider taxonomy* used by coding runtimes
such as ``jeo-code`` (OAuth providers like Anthropic/Claude and Antigravity,
keyless local endpoints like LM Studio and Ollama, and OpenAI-compatible cloud
API providers) and turns it into executor-neutral, metadata-only descriptors.

What this module does:

- Describe each provider's auth shape (``oauth`` / ``api_key`` /
  ``local_endpoint``), the host environment variables that signal it is
  configured, default endpoints, and which OMJ coding owners can consume it.
- Diagnose host configuration using *presence only* of environment variables.

What this module deliberately never does:

- Perform OAuth flows, token exchange, credential storage, or any network call.
- Read or echo secret values. Diagnostics report which env var *names* are
  present, never their values.
- Claim that a provider is reachable, authenticated, or wired into a runtime.
  Authentication and model routing belong to the selected coding owner
  (``codex``, ``claude-code``, ``hermes``, an oh-my runtime, or a generic
  executor), not to OMJ.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from ..coding.executors import EXECUTOR_PROFILES


PROVIDER_AUTH_CONTRACT_VERSION = "omj_provider_auth_surface/v1"

AUTH_KINDS = ("oauth", "api_key", "local_endpoint")

PROVIDER_AUTH_BOUNDARY_RULE = (
    "Provider-auth records are metadata-only descriptors borrowed from coding-runtime provider taxonomy. "
    "OMJ does not perform OAuth, token exchange, credential storage, model API calls, or any network request. "
    "Authentication and model routing are owned by the selected coding owner, not by OMJ."
)
PROVIDER_AUTH_CHAT_RULE = (
    "Normal users talk to Hermes; provider-auth descriptors help Hermes explain which credentials a chosen coding "
    "owner needs and whether the host appears configured, without making the user learn backend OMJ commands."
)
PROVIDER_AUTH_DIAGNOSTIC_BOUNDARY = (
    "A provider-auth readiness diagnostic reports host environment configuration presence only. "
    "It never reads secret values, never contacts a provider, and is not authentication, login, reachability, "
    "or successful inference evidence."
)

# Diagnostic statuses, all metadata-only.
STATUS_CONFIGURED = "configured"  # required API key env var present
STATUS_MISSING = "missing"  # api_key required but no env var present
STATUS_HOST_MANAGED = "host_managed"  # OAuth credential lives in the runtime's own store; OMJ does not read it
STATUS_LOCAL_DEFAULT = "local_default"  # keyless local endpoint at its default URL; reachability not checked
STATUS_LOCAL_OVERRIDE = "local_override"  # local endpoint overridden via env; reachability not checked


@dataclass(frozen=True)
class ProviderAuthDefinition:
    id: str
    label: str
    auth_kind: str
    provider_family: str
    consumed_by: tuple[str, ...]
    api_key_env: tuple[str, ...] = ()
    endpoint_env: tuple[str, ...] = ()
    default_endpoint: str = ""
    requires_secret: bool = True
    login_hint: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "auth_kind": self.auth_kind,
            "provider_family": self.provider_family,
            "consumed_by": list(self.consumed_by),
            "api_key_env": list(self.api_key_env),
            "endpoint_env": list(self.endpoint_env),
            "default_endpoint": self.default_endpoint,
            "requires_secret": self.requires_secret,
            "login_hint": self.login_hint,
            "note": self.note,
            "chat_rule": PROVIDER_AUTH_CHAT_RULE,
            "boundary_rule": PROVIDER_AUTH_BOUNDARY_RULE,
            "runtime_claim": "descriptor_not_runtime_router",
        }


_OAUTH = (
    ProviderAuthDefinition(
        id="anthropic",
        label="Anthropic (Claude Pro/Max)",
        auth_kind="oauth",
        provider_family="anthropic",
        consumed_by=("claude-code", "hermes", "generic"),
        api_key_env=("ANTHROPIC_API_KEY",),
        endpoint_env=("ANTHROPIC_BASE_URL",),
        default_endpoint="https://api.anthropic.com",
        requires_secret=True,
        login_hint="Host runtime runs the Anthropic OAuth (PKCE) login and stores the token in its own credential store.",
        note="OAuth login is owned by the coding runtime. An ANTHROPIC_API_KEY env var, when set, is a host-detectable override.",
    ),
    ProviderAuthDefinition(
        id="openai",
        label="OpenAI (ChatGPT/Codex)",
        auth_kind="oauth",
        provider_family="openai",
        consumed_by=("codex", "generic"),
        api_key_env=("OPENAI_API_KEY",),
        endpoint_env=("OPENAI_BASE_URL",),
        default_endpoint="https://api.openai.com/v1",
        requires_secret=True,
        login_hint="Host runtime runs the ChatGPT/Codex OAuth login; an OPENAI_API_KEY env var, when set, takes precedence.",
        note="ChatGPT/Codex OAuth is served via the Codex Responses backend by the runtime. OMJ only detects the API-key override env.",
    ),
    ProviderAuthDefinition(
        id="google",
        label="Google (Gemini Code Assist)",
        auth_kind="oauth",
        provider_family="google",
        consumed_by=("hermes", "generic"),
        api_key_env=("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        endpoint_env=(),
        default_endpoint="https://cloudcode-pa.googleapis.com",
        requires_secret=True,
        login_hint="Host runtime runs the gemini-cli OAuth login (Cloud Code Assist); a GEMINI_API_KEY env var, when set, takes precedence.",
        note="OAuth uses an auto-discovered project owned by the runtime. OMJ only detects the API-key override env.",
    ),
    ProviderAuthDefinition(
        id="antigravity",
        label="Antigravity (Google)",
        auth_kind="oauth",
        provider_family="google",
        consumed_by=("generic", "hermes"),
        api_key_env=(),
        endpoint_env=(),
        default_endpoint="",
        requires_secret=True,
        login_hint="Host runtime runs the Antigravity OAuth login and stores the token in its own credential store.",
        note="Antigravity has no API-key env override; readiness is host-managed by the coding runtime.",
    ),
)

_LOCAL = (
    ProviderAuthDefinition(
        id="lmstudio",
        label="LM Studio (local)",
        auth_kind="local_endpoint",
        provider_family="local",
        consumed_by=("generic", "hermes"),
        api_key_env=(),
        endpoint_env=("LMSTUDIO_BASE_URL",),
        default_endpoint="http://localhost:1234/v1",
        requires_secret=False,
        login_hint="Run LM Studio locally; the OpenAI-compatible server is keyless on its default port.",
        note="Keyless local OpenAI-compatible server. OMJ never contacts it; reachability is not part of this diagnostic.",
    ),
    ProviderAuthDefinition(
        id="ollama",
        label="Ollama (local)",
        auth_kind="local_endpoint",
        provider_family="local",
        consumed_by=("generic", "hermes"),
        api_key_env=(),
        endpoint_env=("OLLAMA_HOST",),
        default_endpoint="http://localhost:11434",
        requires_secret=False,
        login_hint="Run Ollama locally; set OLLAMA_HOST to point at a non-default endpoint.",
        note="Keyless local server. OMJ never contacts it; reachability is not part of this diagnostic.",
    ),
)


def _api(id: str, label: str, env: str, base: str) -> ProviderAuthDefinition:
    return ProviderAuthDefinition(
        id=id,
        label=label,
        auth_kind="api_key",
        provider_family="openai_compatible",
        consumed_by=("generic", "hermes"),
        api_key_env=(env,),
        endpoint_env=(),
        default_endpoint=base,
        requires_secret=True,
        login_hint=f"Set {env} in the host runtime environment.",
        note="OpenAI-compatible cloud API. Add more providers by adding one catalog row.",
    )


_API = (
    _api("xai", "xAI (Grok)", "XAI_API_KEY", "https://api.x.ai/v1"),
    _api("kimi", "Moonshot (Kimi)", "MOONSHOT_API_KEY", "https://api.moonshot.ai/v1"),
    _api("groq", "Groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    _api("deepseek", "DeepSeek", "DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
    _api("mistral", "Mistral", "MISTRAL_API_KEY", "https://api.mistral.ai/v1"),
    _api("openrouter", "OpenRouter", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    _api("together", "Together", "TOGETHER_API_KEY", "https://api.together.xyz/v1"),
    _api("cerebras", "Cerebras", "CEREBRAS_API_KEY", "https://api.cerebras.ai/v1"),
    _api("fireworks", "Fireworks", "FIREWORKS_API_KEY", "https://api.fireworks.ai/inference/v1"),
    _api("nvidia", "NVIDIA", "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1"),
    _api("huggingface", "Hugging Face", "HF_TOKEN", "https://router.huggingface.co/v1"),
    _api("perplexity", "Perplexity", "PERPLEXITY_API_KEY", "https://api.perplexity.ai"),
    _api("cohere", "Cohere", "COHERE_API_KEY", "https://api.cohere.ai/compatibility/v1"),
    _api("ai21", "AI21 Labs", "AI21_API_KEY", "https://api.ai21.com/studio/v1"),
    _api("sambanova", "SambaNova", "SAMBANOVA_API_KEY", "https://api.sambanova.ai/v1"),
    _api("deepinfra", "DeepInfra", "DEEPINFRA_API_KEY", "https://api.deepinfra.com/v1/openai"),
    _api("hyperbolic", "Hyperbolic", "HYPERBOLIC_API_KEY", "https://api.hyperbolic.xyz/v1"),
    _api("novita", "Novita", "NOVITA_API_KEY", "https://api.novita.ai/v3/openai"),
    _api("baseten", "Baseten", "BASETEN_API_KEY", "https://inference.baseten.co/v1"),
    _api("lambda", "Lambda", "LAMBDA_API_KEY", "https://api.lambda.ai/v1"),
    _api("dashscope", "Alibaba (Qwen/DashScope)", "DASHSCOPE_API_KEY", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    _api("zhipu", "Zhipu (GLM)", "ZHIPUAI_API_KEY", "https://open.bigmodel.cn/api/paas/v4"),
    _api("minimax", "MiniMax", "MINIMAX_API_KEY", "https://api.minimaxi.com/v1"),
    _api("inception", "Inception (Mercury)", "INCEPTION_API_KEY", "https://api.inceptionlabs.ai/v1"),

)


_PROVIDER_AUTH: tuple[ProviderAuthDefinition, ...] = (*_OAUTH, *_LOCAL, *_API)
_PROVIDER_INDEX = {definition.id: definition for definition in _PROVIDER_AUTH}


def list_provider_auth() -> dict[str, object]:
    return {
        "schema_version": PROVIDER_AUTH_CONTRACT_VERSION,
        "providers": [definition.to_dict() for definition in _PROVIDER_AUTH],
        "auth_kinds": list(AUTH_KINDS),
        "boundary": PROVIDER_AUTH_BOUNDARY_RULE,
    }


def get_provider_auth(provider_id: str) -> dict[str, object]:
    definition = _PROVIDER_INDEX.get(provider_id)
    if definition is None:
        raise KeyError(provider_id)
    return {
        "schema_version": PROVIDER_AUTH_CONTRACT_VERSION,
        "provider": definition.to_dict(),
        "boundary": PROVIDER_AUTH_BOUNDARY_RULE,
    }


def _env_present(env: Mapping[str, str], names: tuple[str, ...]) -> list[str]:
    """Return the subset of env var *names* that are present and non-empty.

    Only names are returned, never values, to keep diagnostics secret-free.
    """

    present: list[str] = []
    for name in names:
        value = env.get(name)
        if value is not None and value.strip():
            present.append(name)
    return present


def _diagnose_one(definition: ProviderAuthDefinition, env: Mapping[str, str]) -> dict[str, object]:
    api_present = _env_present(env, definition.api_key_env)
    endpoint_present = _env_present(env, definition.endpoint_env)

    if definition.auth_kind == "api_key":
        status = STATUS_CONFIGURED if api_present else STATUS_MISSING
        configured = bool(api_present)
    elif definition.auth_kind == "local_endpoint":
        status = STATUS_LOCAL_OVERRIDE if endpoint_present else STATUS_LOCAL_DEFAULT
        configured = True  # keyless local providers need no OMJ-visible secret
    else:  # oauth
        status = STATUS_HOST_MANAGED
        # OAuth credentials live in the runtime's own store; OMJ cannot observe
        # them as metadata. An API-key env override is the only host-detectable
        # signal, and it does not prove the OAuth login itself.
        configured = bool(api_present)

    return {
        "id": definition.id,
        "label": definition.label,
        "auth_kind": definition.auth_kind,
        "provider_family": definition.provider_family,
        "consumed_by": list(definition.consumed_by),
        "status": status,
        "configured": configured,
        "api_key_env_present": api_present,
        "api_key_env_expected": list(definition.api_key_env),
        "endpoint_env_present": endpoint_present,
        "default_endpoint": definition.default_endpoint,
        "requires_secret": definition.requires_secret,
        "login_hint": definition.login_hint,
        "boundary": PROVIDER_AUTH_DIAGNOSTIC_BOUNDARY,
    }


def diagnose_provider_auth(env: Mapping[str, str] | None = None) -> dict[str, object]:
    """Diagnose host provider-auth configuration using env-presence metadata only.

    Never reads or echoes secret values. Never contacts a provider.
    """

    resolved = os.environ if env is None else env
    results = [_diagnose_one(definition, resolved) for definition in _PROVIDER_AUTH]
    configured_ids = [item["id"] for item in results if item["configured"]]
    missing_required = [item["id"] for item in results if item["status"] == STATUS_MISSING]
    host_managed = [item["id"] for item in results if item["status"] == STATUS_HOST_MANAGED]
    return {
        "schema_version": PROVIDER_AUTH_CONTRACT_VERSION,
        "providers": results,
        "summary": {
            "total": len(results),
            "configured": len(configured_ids),
            "missing_required": len(missing_required),
            "host_managed": len(host_managed),
            "configured_ids": configured_ids,
            "missing_required_ids": missing_required,
            "host_managed_ids": host_managed,
        },
        "boundary": PROVIDER_AUTH_DIAGNOSTIC_BOUNDARY,
    }


def _validate_catalog() -> None:
    """Internal integrity guard exercised by tests."""

    seen: set[str] = set()
    seen_api_env: set[str] = set()
    seen_api_endpoint: set[str] = set()
    for definition in _PROVIDER_AUTH:
        assert definition.auth_kind in AUTH_KINDS, definition.id
        assert definition.id not in seen, f"duplicate provider id: {definition.id}"
        seen.add(definition.id)
        for owner in definition.consumed_by:
            assert owner in EXECUTOR_PROFILES, f"{definition.id}: unknown owner {owner}"
        if definition.auth_kind == "api_key":
            assert definition.api_key_env, f"{definition.id}: api_key provider needs api_key_env"
            primary_env = definition.api_key_env[0]
            assert primary_env not in seen_api_env, (
                f"{definition.id}: duplicate api_key env var {primary_env}"
            )
            seen_api_env.add(primary_env)
            assert definition.default_endpoint, f"{definition.id}: api provider needs endpoint"
            assert definition.default_endpoint not in seen_api_endpoint, (
                f"{definition.id}: duplicate endpoint {definition.default_endpoint}"
            )
            seen_api_endpoint.add(definition.default_endpoint)
        if definition.auth_kind == "local_endpoint":
            assert not definition.requires_secret, f"{definition.id}: local endpoint must be keyless"
