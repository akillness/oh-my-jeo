from __future__ import annotations

from typing import Any

from ..capabilities.families import capability_family_projection, validate_disabled_families
from ..executors import CODING_EXECUTOR_TARGETS
from ..local_store import atomic_write_json, read_json_object, utc_now
from ..paths import OmjPaths
from .team import inspect_operating_model, operating_model_ids


SETUP_PROFILE_SCHEMA_VERSION = "setup_profile/v1"
PROJECT_MEMORY_POLICY_SCHEMA_VERSION = "project_memory_policy/v1"
PARALLELISM_POLICY_SCHEMA_VERSION = "parallelism_policy/v1"
PROJECT_MEMORY_MODES = ("off", "review-first", "auto-safe")

# Parallelism is routing metadata only. It never starts workers or changes
# Hermes' own scheduler.
PARALLELISM_POLICY_FIELDS = frozenset(
    {"schema_version", "default_concurrency", "global_concurrency", "lane_budget_default", "per_owner"}
)

SETUP_PROFILE_CATEGORIES = (
    {
        "id": "hermes-retained",
        "choice": "1",
        "label": "Hermes answers and plans",
        "default_executor": "hermes",
        "description": "Keep research, planning, interviews, triage, and status narration in Hermes.",
    },
    {
        "id": "prompt-only-coding",
        "choice": "2",
        "label": "Other coding agent",
        "default_executor": "generic",
        "description": "Prepare copy-ready prompts for Claude Code, generic agents, or other tools.",
    },
    {
        "id": "codex-lifecycle",
        "choice": "3",
        "label": "Codex",
        "default_executor": "codex",
        "description": "Use Codex as the default coding agent and track dispatch, result, review, CI, and merge evidence when selected.",
    },
    {
        "id": "plugin-runtime",
        "choice": "4",
        "label": "Oh-my runtime",
        "default_executor": "omx-runtime",
        "description": "Use an oh-my runtime profile when the user has one.",
    },
    {
        "id": "safety-first",
        "choice": "5",
        "label": "Ask every time",
        "default_executor": "choose",
        "description": "Ask the user before choosing a coding agent and preserve prepared-vs-observed boundaries.",
    },
)

_CATEGORY_BY_ID = {str(item["id"]): item for item in SETUP_PROFILE_CATEGORIES}
_CATEGORY_BY_CHOICE = {str(item["choice"]): item for item in SETUP_PROFILE_CATEGORIES}
_CATEGORY_ID_BY_EXECUTOR = {
    "choose": "safety-first",
    "hermes": "hermes-retained",
    "codex": "codex-lifecycle",
    "claude-code": "prompt-only-coding",
    "generic": "prompt-only-coding",
    "omx-runtime": "plugin-runtime",
    "omo-runtime": "plugin-runtime",
    "omc-runtime": "plugin-runtime",
}

def setup_profile_choices() -> list[dict[str, str]]:
    return [{key: str(value) for key, value in item.items()} for item in SETUP_PROFILE_CATEGORIES]


def build_setup_profile(
    values: list[str] | tuple[str, ...] | None = None,
    *,
    default_executor: str | None = None,
    operating_model: str | None = None,
    memory_mode: str | None = None,
    parallelism_policy: dict[str, Any] | None = None,
    capability_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model_id = _normalize_operating_model(operating_model)
    model = inspect_operating_model(model_id)["model"]
    model_default_executor = str(model.get("default_executor", "choose")) if operating_model else None
    executor_hint = default_executor or model_default_executor
    selected = _selected_categories(values, default_executor=executor_hint)
    resolved_executor = _default_executor_for_categories(selected, default_executor=executor_hint)
    memory_policy = build_project_memory_policy(memory_mode)
    profile: dict[str, Any] = {
        "schema_version": SETUP_PROFILE_SCHEMA_VERSION,
        "updated_at": utc_now(),
        "selected_categories": [str(item["id"]) for item in selected],
        "operating_model_schema_version": "operating_model/v1",
        "operating_model_id": model_id,
        "default_executor": resolved_executor,
        "dispatch_policy": "ask_before_dispatch" if resolved_executor in {"codex", "choose"} else "prepare_only",
        "memory_mode": memory_policy["mode"],
        "memory_policy": memory_policy,
        "normal_user_surface": "Hermes Agent chat and installed Hermes skills",
        "local_only": True,
        "network_calls": False,
        "hidden_execution": False,
        "choices": setup_profile_choices(),
        "claim_boundary": "Setup records routing defaults only; it does not prove Hermes used a skill or any executor ran.",
        "hermes_auto_install": None,
        "hermes_auto_install_recorded_at": None,
    }
    if parallelism_policy is not None:
        profile["parallelism_policy"] = validate_parallelism_policy(parallelism_policy)
    if capability_policy is not None:
        profile["capability_policy"] = _validate_capability_policy(capability_policy)
    return profile


def write_setup_profile(
    paths: OmjPaths,
    values: list[str] | tuple[str, ...] | None = None,
    *,
    default_executor: str | None = None,
    operating_model: str | None = None,
    memory_mode: str | None = None,
    parallelism_policy: dict[str, Any] | None = None,
    capability_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    existing = read_setup_profile(paths)
    if isinstance(existing, dict):
        _validate_existing_policies(existing)
    if memory_mode is None and isinstance(existing, dict):
        prior_mode = existing.get("memory_mode")
        if isinstance(prior_mode, str) and prior_mode in PROJECT_MEMORY_MODES:
            memory_mode = prior_mode
    if parallelism_policy is None and isinstance(existing, dict):
        prior_parallelism = existing.get("parallelism_policy")
        if prior_parallelism is not None:
            parallelism_policy = prior_parallelism
    if capability_policy is None and isinstance(existing, dict):
        prior_capability = existing.get("capability_policy")
        if prior_capability is not None:
            capability_policy = prior_capability
    profile = build_setup_profile(
        values,
        default_executor=default_executor,
        operating_model=operating_model,
        memory_mode=memory_mode,
        parallelism_policy=parallelism_policy,
        capability_policy=capability_policy,
    )
    generated = {
        "schema_version", "updated_at", "selected_categories",
        "operating_model_schema_version", "operating_model_id", "default_executor",
        "dispatch_policy", "memory_mode", "memory_policy", "normal_user_surface",
        "local_only", "network_calls", "hidden_execution", "choices", "claim_boundary",
        "hermes_auto_install", "hermes_auto_install_recorded_at", "parallelism_policy",
        "capability_policy",
    }
    if isinstance(existing, dict):
        for key, value in existing.items():
            if key not in generated:
                profile[key] = value
        if existing.get("hermes_auto_install") is not None:
            profile["hermes_auto_install"] = existing.get("hermes_auto_install")
            profile["hermes_auto_install_recorded_at"] = existing.get("hermes_auto_install_recorded_at")
    atomic_write_json(paths.setup_profile_path, profile, private=True)
    return profile


def read_setup_profile(paths: OmjPaths) -> dict[str, Any] | None:
    return read_json_object(paths.setup_profile_path)


def accepted_parallelism_policy(paths: OmjPaths) -> dict[str, Any] | None:
    """Return the selected profile's validated prepared parallelism policy.

    A missing profile or absent policy is the baseline ``None``. A present but
    malformed profile/policy raises ``ValueError`` so consumers cannot mistake
    corrupt operator state for an unconfigured policy.
    """
    profile = read_setup_profile(paths)
    if not isinstance(profile, dict):
        return None
    if "parallelism_policy" not in profile or profile["parallelism_policy"] is None:
        return None
    try:
        return validate_parallelism_policy(profile["parallelism_policy"])
    except ValueError as error:
        raise ValueError(f"stored parallelism policy is invalid: {error}") from error


def accepted_disabled_families(paths: OmjPaths) -> frozenset[str]:
    """Return canonical disabled capability families from the selected profile."""
    profile = read_setup_profile(paths)
    if not isinstance(profile, dict):
        return frozenset()
    policy = profile.get("capability_policy")
    if policy is None:
        return frozenset()
    validated = _validate_capability_policy(policy)
    return validate_disabled_families(validated["disabled_families"])


def require_enabled_workflow(workflow: str, paths: OmjPaths | None = None) -> None:
    """Refuse selected-home disabled workflows before preparing their actions."""
    projection = capability_family_projection(
        disabled_families=accepted_disabled_families(paths) if paths is not None else None
    )
    if workflow in projection["disabled_workflows"]:
        raise ValueError(f"workflow {workflow!r} is disabled by the selected-home capability policy")


def _validate_existing_policies(profile: dict[str, Any]) -> None:
    if "parallelism_policy" in profile and profile["parallelism_policy"] is not None:
        validate_parallelism_policy(profile["parallelism_policy"])
    if "capability_policy" in profile and profile["capability_policy"] is not None:
        _validate_capability_policy(profile["capability_policy"])


def _validate_capability_policy(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("capability policy must be an object")
    disabled = value.get("disabled_families")
    if not isinstance(disabled, list):
        raise ValueError("capability policy disabled_families must be a list")
    try:
        validate_disabled_families(disabled)
    except ValueError as error:
        raise ValueError(str(error)) from error
    return dict(value)


def record_hermes_auto_install_consent(paths: OmjPaths, consent: bool) -> dict[str, Any]:
    """Persist an explicit operator decision on Hermes runtime auto-install.

    Called after an operator answers the bare `omj` welcome prompt, or after an
    explicit `omj setup --with-hermes`/`--autopilot` opt-in. Once recorded, the
    decision (yes or no) is never asked again; `omj` reads it back to decide
    whether to auto-install a missing Hermes runtime without prompting.
    """

    existing = read_setup_profile(paths)
    if isinstance(existing, dict):
        _validate_existing_policies(existing)
    profile = dict(existing) if isinstance(existing, dict) else build_setup_profile()
    profile["hermes_auto_install"] = bool(consent)
    profile["hermes_auto_install_recorded_at"] = utc_now()
    atomic_write_json(paths.setup_profile_path, profile, private=True)
    return profile


def setup_profile_categories_for_executor(executor: str) -> list[str]:
    executor_value = _normalize_executor(executor)
    return [_CATEGORY_ID_BY_EXECUTOR[executor_value]]


def build_project_memory_policy(mode: str | None = None) -> dict[str, object]:
    normalized = _normalize_memory_mode(mode)
    return {
        "schema_version": PROJECT_MEMORY_POLICY_SCHEMA_VERSION,
        "mode": normalized,
        "capture_enabled": normalized != "off",
        "recall_enabled": normalized != "off",
        "review_required": normalized == "review-first",
        "auto_approve_safe": normalized == "auto-safe",
        "store_scope": "project_local",
        "redaction_policy": "metadata_only",
        "backend": "local_json",
        "optional_backend_extension": True,
        "claim_boundary": "Project memory configures OMJ-local prepared context only; it does not mutate Hermes global or internal memory.",
    }

def validate_parallelism_policy(value: Any) -> dict[str, Any]:
    """Validate and return an independent JSON-safe parallelism policy copy."""
    if not isinstance(value, dict) or not value:
        raise ValueError("parallelism policy must be a non-empty object")
    result = dict(value)
    owner_keys = {str(key) for key in value}
    if owner_keys & set(CODING_EXECUTOR_TARGETS):
        for owner, config in value.items():
            if str(owner) == "choose":
                raise ValueError("parallelism policy cannot target the unresolved choose executor")
            if str(owner) not in CODING_EXECUTOR_TARGETS:
                raise ValueError(f"unsupported parallelism owner: {owner}")
            _validate_parallelism_config(str(owner), config)
        return result
    unknown = owner_keys - PARALLELISM_POLICY_FIELDS
    if unknown:
        raise ValueError(f"unsupported parallelism policy fields: {', '.join(sorted(unknown))}")
    for field in ("default_concurrency", "global_concurrency", "lane_budget_default"):
        if field in value:
            _validate_positive_int(field, value[field])
    per_owner = value.get("per_owner")
    if per_owner is not None:
        if not isinstance(per_owner, dict):
            raise ValueError("parallelism policy per_owner must be an object")
        for owner, config in per_owner.items():
            if str(owner) not in CODING_EXECUTOR_TARGETS or str(owner) == "choose":
                raise ValueError(f"unsupported parallelism owner: {owner}")
            _validate_parallelism_config(str(owner), config)
    return result


def _validate_positive_int(field: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"parallelism policy {field} must be a positive integer")


def _validate_parallelism_config(owner: str, value: Any) -> None:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"parallelism policy for {owner} must be an object")
    for field, setting in value.items():
        if str(field) not in {"max_workers", "concurrency", "lane_budget", "global_limit"}:
            raise ValueError(f"unsupported parallelism setting for {owner}: {field}")
        _validate_positive_int(f"{owner}.{field}", setting)


def _selected_categories(
    values: list[str] | tuple[str, ...] | None,
    *,
    default_executor: str | None = None,
) -> list[dict[str, object]]:
    if not values:
        if default_executor:
            return [_CATEGORY_BY_ID[setup_profile_categories_for_executor(default_executor)[0]]]
        return [_CATEGORY_BY_ID["hermes-retained"]]
    selected: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        item = _CATEGORY_BY_CHOICE.get(value) or _CATEGORY_BY_ID.get(value)
        if not item:
            valid = ", ".join(sorted(set(_CATEGORY_BY_CHOICE) | set(_CATEGORY_BY_ID)))
            raise ValueError(f"unsupported setup profile choice: {value}; expected one of {valid}")
        item_id = str(item["id"])
        if item_id not in seen:
            selected.append(item)
            seen.add(item_id)
    return selected


def _default_executor_for_categories(selected: list[dict[str, object]], *, default_executor: str | None = None) -> str:
    if default_executor:
        return _normalize_executor(default_executor)
    ids = {str(item["id"]) for item in selected}
    if "safety-first" in ids:
        return "choose"
    if "codex-lifecycle" in ids:
        return "codex"
    if "plugin-runtime" in ids:
        return "omx-runtime"
    if "prompt-only-coding" in ids:
        return "generic"
    return "hermes"


def _normalize_executor(value: str) -> str:
    executor = str(value).strip()
    if executor not in CODING_EXECUTOR_TARGETS:
        valid = ", ".join(CODING_EXECUTOR_TARGETS)
        raise ValueError(f"unsupported setup default executor: {executor}; expected one of {valid}")
    return executor


def _normalize_operating_model(value: str | None) -> str:
    model = str(value or "solo-operator").strip()
    valid = operating_model_ids()
    if model not in valid:
        raise ValueError(f"unsupported operating model: {model}; expected one of {', '.join(valid)}")
    return model


def _normalize_memory_mode(value: str | None) -> str:
    mode = str(value or "review-first").strip()
    if mode not in PROJECT_MEMORY_MODES:
        raise ValueError(f"unsupported memory mode: {mode}; expected one of {', '.join(PROJECT_MEMORY_MODES)}")
    return mode
