"""Offline request, model-contract, and sensitive-data verdicts.

This module is deliberately a local comparison surface.  It does not choose an
executor, call a model, read credentials, mutate configuration, or make a
provider/network request.  Catalog and contract rows are metadata only; the
runtime that eventually runs a request owns availability and execution facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
import unicodedata
from typing import Final, Iterable, Mapping, Sequence


# ---------------------------------------------------------------------------
# Request complexity

REQUEST_COMPLEXITY_SCHEMA_VERSION: Final[str] = "request_complexity/v1"
COMPLEXITY_MODEL_RECOMMENDATION_SCHEMA_VERSION: Final[str] = (
    "complexity_model_recommendation/v1"
)
COMPLEXITY_TIERS: Final[tuple[str, ...]] = ("light", "standard", "deep")
COMPLEXITY_TIER_THRESHOLDS: Final[tuple[tuple[str, int], ...]] = (
    ("deep", 8),
    ("standard", 4),
)
COMPLEXITY_CLAIM_BOUNDARY: Final[str] = (
    "A complexity score is a deterministic reading of request text and an optional routed skill. "
    "It is recommendation input only: not a route, model choice, owner selection, provider "
    "availability, cost, execution, review, CI, or merge evidence. No model or network call is made."
)
COMPLEXITY_LENGTH_BANDS: Final[tuple[tuple[str, int, int], ...]] = (
    ("brief", 0, 0),
    ("medium", 200, 1),
    ("long", 600, 2),
)
COMPLEXITY_SKILL_CLASS_WEIGHTS: Final[dict[str, int]] = {
    "delegate_coding_and_ship": 2,
    "plan_and_decide": 1,
    "operate_and_observe": 1,
    "learn_and_gather": 1,
}
COMPLEXITY_TIER_MODEL_CLASSES: Final[dict[str, str]] = {
    "light": "quick",
    "standard": "unspecified-high",
    "deep": "deep",
}
COMPLEXITY_TIER_EFFORTS: Final[dict[str, str]] = {
    "light": "low",
    "standard": "medium",
    "deep": "high",
}
COMPLEXITY_RECOMMENDATION_STATUSES: Final[tuple[str, ...]] = (
    "recommended",
    "superseded_by_user_override",
)
COMPLEXITY_CHAIN_STATUSES: Final[tuple[str, ...]] = (
    "resolved",
    "class_not_in_chains",
    "no_chain_config",
)

_MAX_COUNTED_PATHS: Final[int] = 20
_MAX_COUNTED_SUBTASKS: Final[int] = 10
_PATH_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![\w./-])[\w][\w./-]*/[\w./-]*\.[a-z]{1,6}(?![\w])|"
    r"(?<![\w./-])[\w][\w.-]*\.(?:py|ts|tsx|js|jsx|go|rs|java|rb|md|json|yaml|yml|toml|sh|sql|css|html)(?![\w])"
)
_ORDERED_STEP_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^\s*(?:\d+[.)]|[-*+])\s+\S")


@dataclass(frozen=True)
class ComplexitySignal:
    name: str
    weight: int
    describe: str
    phrases: tuple[str, ...] = ()


COMPLEXITY_SIGNALS: Final[tuple[ComplexitySignal, ...]] = (
    ComplexitySignal(
        "architecture_keywords",
        3,
        "Design-level work changes system shape, not only individual lines.",
        (
            "architecture", "architectural", "rearchitect", "re-architect", "redesign",
            "restructure", "refactor", "rewrite", "migration", "migrate", "schema change",
            "data model", "design doc", "decouple",
        ),
    ),
    ComplexitySignal(
        "impact_system_wide",
        3,
        "The stated blast radius covers a whole surface rather than one place.",
        (
            "system-wide", "system wide", "across the codebase", "across the repo",
            "across every", "across all", "entire codebase", "entire repo", "whole codebase",
            "every module", "every service", "every caller", "all callers", "all services",
            "end-to-end", "end to end", "everywhere",
        ),
    ),
    ComplexitySignal(
        "risk_keywords",
        2,
        "Security, concurrency, compatibility, or data-integrity failure is costly.",
        (
            "security", "vulnerability", "authentication", "authorization", "credential", "secret",
            "injection", "concurrency", "concurrent", "race condition", "deadlock", "thread safety",
            "thread-safe", "data loss", "corruption", "rollback", "backwards compatibility",
            "backward compatibility",
        ),
    ),
    ComplexitySignal(
        "debugging_keywords",
        2,
        "The request asks for investigation before repair.",
        (
            "root cause", "root-cause", "regression", "stack trace", "traceback", "reproduce",
            "reproduction", "flaky", "intermittent", "why does it fail", "why is it failing",
            "bisect", "heisenbug",
        ),
    ),
    ComplexitySignal(
        "fanout_intent",
        2,
        "Parallel or split work is explicitly requested.",
        (
            "in parallel", "parallelize", "parallelise", "fanout", "fan out", "fan-out",
            "concurrently", "multiple agents", "several agents", "split the work", "split it up",
            "at the same time",
        ),
    ),
    ComplexitySignal(
        "exhaustive_search",
        4,
        "Every occurrence must be found; recall is part of correctness.",
        (
            "find every", "find all", "every reference", "all references", "every usage", "all usages",
            "every occurrence", "all occurrences", "every call site", "all call sites",
            "every definition", "every instance of", "all instances of", "enumerate every",
            "enumerate all", "exhaustive", "exhaustively",
        ),
    ),
    ComplexitySignal(
        "simple_request",
        -2,
        "The request is phrased as a one-line edit or lookup.",
        (
            "typo", "one-liner", "one liner", "single line", "one line", "rename",
            "bump the version", "bump version", "quick question", "just tell me", "what is",
            "what does", "where is", "print the", "list the files", "add a comment", "fix the spelling",
        ),
    ),
)
COMPLEXITY_DERIVED_SIGNAL_NAMES: Final[tuple[str, ...]] = (
    "subtasks_many", "cross_file", "message_length", "routed_skill_class"
)
COMPLEXITY_SIGNAL_NAMES: Final[tuple[str, ...]] = tuple(
    [signal.name for signal in COMPLEXITY_SIGNALS] + list(COMPLEXITY_DERIVED_SIGNAL_NAMES)
)


def _normalized_phrase(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def complexity_class_for_skill(routed_skill: str) -> str:
    name = str(routed_skill or "").strip()
    if not name:
        return ""
    # Keep the family vocabulary owned by the existing capability catalog.  A
    # missing optional catalog must make the signal unknown, not invent a class.
    try:
        from ..capabilities.families import family_id_for_workflow
    except (ImportError, ModuleNotFoundError):
        return ""
    try:
        value = family_id_for_workflow(name)
    except (AttributeError, KeyError, TypeError, ValueError):
        return ""
    return str(value or "")


def _matched_phrases(folded: str, phrases: Sequence[str]) -> list[str]:
    return sorted({phrase for phrase in phrases if _normalized_phrase(phrase) in folded})


def _signal_payload(name: str, weight: int, describe: str, evidence: Sequence[str]) -> dict[str, object]:
    return {"name": name, "weight": weight, "describe": describe, "evidence": list(evidence)}


def _subtask_count(folded: str, text: str) -> int:
    return min(len(_ORDERED_STEP_RE.findall(text)) + folded.count(" then "), _MAX_COUNTED_SUBTASKS)


def _path_count(text: str) -> int:
    return min(len({match.casefold() for match in _PATH_RE.findall(text)}), _MAX_COUNTED_PATHS)


def _length_band(text: str) -> tuple[str, int]:
    length = len(text.strip())
    band, weight = COMPLEXITY_LENGTH_BANDS[0][0], COMPLEXITY_LENGTH_BANDS[0][2]
    for candidate, minimum, candidate_weight in COMPLEXITY_LENGTH_BANDS:
        if length >= minimum:
            band, weight = candidate, candidate_weight
    return band, weight


def score_request_complexity(message: str, *, routed_skill: str = "") -> dict[str, object]:
    """Score request wording into bounded, explainable complexity tiers."""
    text = str(message or "")
    folded = _normalized_phrase(text)
    skill = str(routed_skill or "").strip()
    skill_class = complexity_class_for_skill(skill)
    signals: list[dict[str, object]] = []
    for signal in COMPLEXITY_SIGNALS:
        evidence = _matched_phrases(folded, signal.phrases)
        if evidence:
            signals.append(_signal_payload(signal.name, signal.weight, signal.describe, evidence))

    subtasks = _subtask_count(folded, text)
    if subtasks >= 3:
        signals.append(_signal_payload(
            "subtasks_many", 4,
            "Three or more enumerated or chained steps were requested at once.",
            [f"subtask_estimate={subtasks}"],
        ))
    paths = _path_count(text)
    if paths >= 2:
        signals.append(_signal_payload(
            "cross_file", 2,
            "Two or more distinct files are named, so the change spans a seam.",
            [f"path_count={paths}"],
        ))
    band, band_weight = _length_band(text)
    if band_weight:
        signals.append(_signal_payload(
            "message_length", band_weight,
            "Longer requests carry more stated scope; length corroborates, never decides.",
            [f"length_band={band}", f"characters={len(text.strip())}"],
        ))
    class_weight = COMPLEXITY_SKILL_CLASS_WEIGHTS.get(skill_class, 0)
    if class_weight:
        signals.append(_signal_payload(
            "routed_skill_class", class_weight,
            "The routed capability family is typically heavier work.",
            [f"routed_skill={skill}", f"routed_skill_class={skill_class}"],
        ))

    score = sum(int(entry["weight"]) for entry in signals)
    return {
        "schema_version": REQUEST_COMPLEXITY_SCHEMA_VERSION,
        "score": score,
        "tier": tier_for_score(score),
        "signals": signals,
        "routed_skill": skill,
        "routed_skill_class": skill_class,
        "thresholds": [{"tier": tier, "min_score": bound} for tier, bound in COMPLEXITY_TIER_THRESHOLDS],
        "claim_boundary": COMPLEXITY_CLAIM_BOUNDARY,
    }


def tier_for_score(score: int) -> str:
    for tier, bound in COMPLEXITY_TIER_THRESHOLDS:
        if int(score) >= bound:
            return tier
    return COMPLEXITY_TIERS[0]


def _signal_entries(complexity: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw = complexity.get("signals")
    return [entry for entry in raw if isinstance(entry, Mapping)] if isinstance(raw, list) else []


def recommend_model_for_complexity(
    complexity: Mapping[str, object],
    *,
    chains: Mapping[str, Sequence[tuple[str, str]]] | None = None,
    requested_model: str = "",
    requested_effort: str = "",
) -> dict[str, object]:
    """Prepare a class/effort recommendation without selecting or running a model."""
    tier = str(complexity.get("tier") or COMPLEXITY_TIERS[0])
    if tier not in COMPLEXITY_TIER_MODEL_CLASSES:
        tier = COMPLEXITY_TIERS[0]
    model_class = COMPLEXITY_TIER_MODEL_CLASSES[tier]
    tier_effort = COMPLEXITY_TIER_EFFORTS[tier]

    chain_entries: list[dict[str, str]] = []
    chain_status = "no_chain_config"
    if chains is not None:
        chain_status = "class_not_in_chains"
        raw_chain = chains.get(model_class, ())
        if isinstance(raw_chain, (list, tuple)):
            for item in raw_chain:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    model, effort = item[0], item[1]
                    chain_entries.append({"model": str(model), "reasoning_effort": str(effort)})
                elif isinstance(item, Mapping):
                    model = item.get("model", item.get("model_id", ""))
                    if model:
                        chain_entries.append({
                            "model": str(model),
                            "reasoning_effort": str(item.get("reasoning_effort", item.get("effort", ""))),
                        })
        if chain_entries:
            chain_status = "resolved"

    model = str(requested_model or "").strip()
    effort = str(requested_effort or "").strip()
    overridden = bool(model or effort)
    head = chain_entries[0] if chain_entries else {}
    resolved_effort = effort or head.get("reasoning_effort", "") or tier_effort
    resolved = {"model": head["model"], "reasoning_effort": resolved_effort} if head else {}
    payload: dict[str, object] = {
        "schema_version": COMPLEXITY_MODEL_RECOMMENDATION_SCHEMA_VERSION,
        "status": "superseded_by_user_override" if overridden else "recommended",
        "tier": tier,
        "score": int(complexity.get("score") or 0),
        "model_class": model_class,
        "reasoning_effort": resolved_effort,
        "chain_status": chain_status,
        "chain": chain_entries,
        "resolved": resolved,
        "signals": [{"name": entry.get("name", ""), "weight": entry.get("weight", 0)} for entry in _signal_entries(complexity)],
        "claim_boundary": COMPLEXITY_CLAIM_BOUNDARY,
    }
    if overridden:
        payload["user_override"] = {"model": model, "reasoning_effort": effort}
        payload["override_note"] = (
            "An explicit requested model or effort is disclosed as caller-owned input; this function "
            "does not validate, select, dispatch, or execute it."
        )
    return payload


# ---------------------------------------------------------------------------
# Model contract coverage

MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION: Final[str] = "model_contract_coverage/v1"
MODEL_CONTRACT_COVERAGE_CLAIM_BOUNDARY: Final[str] = (
    "This deterministic report compares supplied model identifiers with local contract metadata. "
    "Exact, inherited, or dated metadata is not evidence of provider availability, account entitlement, "
    "cost at runtime, served models, owner selection, dispatch, or execution."
)
MODEL_CONTRACT_COVERAGE_STATUSES: Final[tuple[str, ...]] = (
    "exact", "declared_inheritance", "dated_snapshot", "intentional_exclusion", "missing"
)

_MODEL_CONTRACTS: Final[dict[str, Mapping[str, object]]] = {
    "gpt-6-sol": {
        "schema_version": "model_contract/v1",
        "model_id": "gpt-6-sol",
        "family": "gpt",
        "reasoning_mode": "standard",
        "service_tier": "standard",
        "reasoning_efforts": ("low", "medium", "high", "xhigh", "max"),
        "effort_floor": "low",
        "data_handling": {
            "training_use": "not_recorded",
            "retention": "not_recorded",
            "account_scope": "vendor-documented default; negotiated agreement may differ; not account-level evidence",
        },
    },
    "deepseek-v4.1-flash": {
        "schema_version": "model_contract/v1",
        "model_id": "deepseek-v4.1-flash",
        "family": "deepseek",
        "reasoning_mode": "thinking",
        "service_tier": "standard",
        "reasoning_efforts": (),
        "effort_floor": "",
        "data_handling": {
            "training_use": "not_recorded",
            "retention": "not_recorded",
            "account_scope": "vendor-documented default; negotiated agreement may differ; not account-level evidence",
        },
    },
}
MODEL_CONTRACTS: Final[dict[str, Mapping[str, object]]] = _MODEL_CONTRACTS
DECLARED_MODEL_CONTRACT_PROJECTIONS: Final[dict[str, Mapping[str, str]]] = {
    "deepseek-flash": {
        "contract_model_id": "deepseek-v4.1-flash",
        "reasoning_mode": "thinking",
        "service_tier": "standard",
    },
}
TRAINING_USE_EXCLUDED: Final[str] = "excluded"
TRAINING_USE_INCLUDED: Final[str] = "included"
TRAINING_USE_NOT_RECORDED: Final[str] = "not_recorded"
RETENTION_NONE: Final[str] = "none"
RETENTION_BOUNDED: Final[str] = "bounded"
RETENTION_INDEFINITE: Final[str] = "indefinite"
RETENTION_NOT_RECORDED: Final[str] = "not_recorded"
_DECLARED_PROJECTIONS = DECLARED_MODEL_CONTRACT_PROJECTIONS
_MODEL_DOCS: Final[dict[str, tuple[str, ...]]] = {model: () for model in _MODEL_CONTRACTS}
_DATED_SNAPSHOT_SUFFIX: Final[re.Pattern[str]] = re.compile(
    r"^(?P<base>.+)-(?P<date>\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))$"
)


def _unqualified_model_id(value: object) -> str:
    normalized = str(value or "").strip().casefold()
    return normalized.rsplit("/", 1)[-1] if "/" in normalized else normalized


def _projection(model_id: object) -> dict[str, str] | None:
    requested = str(model_id or "").strip()
    canonical = _unqualified_model_id(requested)
    if not canonical:
        return None
    if canonical in _MODEL_CONTRACTS:
        contract = _MODEL_CONTRACTS[canonical]
        return {
            "schema_version": "model_contract_projection/v1",
            "requested_model": requested,
            "canonical_model_id": canonical,
            "contract_model_id": canonical,
            "reasoning_mode": str(contract.get("reasoning_mode", "standard")),
            "service_tier": str(contract.get("service_tier", "standard")),
            "provenance": "exact",
        }
    declared = _DECLARED_PROJECTIONS.get(canonical)
    if declared is not None and str(declared.get("contract_model_id", "")) in _MODEL_CONTRACTS:
        return {
            "schema_version": "model_contract_projection/v1",
            "requested_model": requested,
            "canonical_model_id": canonical,
            "contract_model_id": str(declared["contract_model_id"]),
            "reasoning_mode": str(declared.get("reasoning_mode", "standard")),
            "service_tier": str(declared.get("service_tier", "standard")),
            "provenance": "declared_inheritance",
        }
    match = _DATED_SNAPSHOT_SUFFIX.match(canonical)
    if match and not _DATED_SNAPSHOT_SUFFIX.match(match.group("base")):
        base = _projection(match.group("base"))
        if base is not None:
            return {
                **base,
                "requested_model": requested,
                "canonical_model_id": canonical,
                "provenance": "dated_snapshot",
            }
    return None


def _contract_for(model_id: object, contracts: Mapping[str, Mapping[str, object]]) -> Mapping[str, object] | None:
    canonical = _unqualified_model_id(model_id)
    if contracts is _MODEL_CONTRACTS:
        projection = _projection(model_id)
        return _MODEL_CONTRACTS.get(str(projection["contract_model_id"])) if projection else None
    for key, contract in contracts.items():
        if _unqualified_model_id(key) == canonical:
            return contract
    return None


_OPAQUE_REFERENCE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
_SENSITIVE_REF_MARKERS: Final[tuple[str, ...]] = (
    "secret", "token", "password", "private-key", "api_key", "apikey", "credential", "authorization", "bearer",
)
_SECRET_VALUE_RE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"(?:^|[^a-z0-9])(?:sk|pk|rk|xox[a-z]?)[_-][a-z0-9_-]{8,}", re.IGNORECASE),
    re.compile(r"(?:^|[^a-z0-9])(?:gh[oprs]|github_pat|npm|whsec|glpat)[_-][a-z0-9_-]{16,}", re.IGNORECASE),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b", re.IGNORECASE),
)


def _safe_ref(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a safe opaque metadata reference")
    ref = value.strip()
    lowered = ref.casefold()
    if not _OPAQUE_REFERENCE.fullmatch(ref) or any(marker in lowered for marker in _SENSITIVE_REF_MARKERS):
        raise ValueError(f"{field} must be a safe opaque metadata reference")
    if any(pattern.search(ref) for pattern in _SECRET_VALUE_RE):
        raise ValueError(f"{field} must be a safe opaque metadata reference")
    return ref


def _stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _digest(value: object) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _entry_model_id(entry: object, *, field: str) -> str:
    if isinstance(entry, str):
        return _safe_ref(entry, field=field)
    if isinstance(entry, Mapping):
        return _safe_ref(entry.get("model_id", entry.get("model", entry.get("id", ""))), field=field)
    raise ValueError(f"{field} entries must be model ids or objects")


def _validate_inventory(inventory: Mapping[str, object]) -> None:
    if not any(field in inventory for field in ("models", "available_models", "model_discovery")):
        raise ValueError("inventory must include models, available_models, or model_discovery")
    for field in ("models", "available_models"):
        value = inventory.get(field)
        if field in inventory and not isinstance(value, (list, tuple)):
            raise ValueError(f"inventory {field} must be a JSON array")
    raw_models = inventory.get("models", ())
    if isinstance(raw_models, (list, tuple)):
        for entry in raw_models:
            _entry_model_id(entry, field="inventory models")
    available = inventory.get("available_models", ())
    if isinstance(available, (list, tuple)):
        for entry in available:
            if not isinstance(entry, Mapping):
                raise ValueError("inventory available_models entries must be objects")
            _entry_model_id(entry, field="inventory available_models")
    discovery = inventory.get("model_discovery")
    if "model_discovery" in inventory:
        if not isinstance(discovery, Mapping):
            raise ValueError("inventory model_discovery must be an object")
        observations = discovery.get("observations")
        if not isinstance(observations, (list, tuple)):
            raise ValueError("inventory model_discovery.observations must be a JSON array")
        for entry in observations:
            if not isinstance(entry, Mapping):
                raise ValueError("inventory model_discovery observations must be objects")
            _entry_model_id(entry, field="inventory model_discovery")


def _inventory_refs(inventory: Mapping[str, object]) -> tuple[tuple[str, ...], dict[str, dict[str, object]]]:
    identities: dict[str, set[str]] = {}
    evidence: dict[str, set[tuple[str, str]]] = {}

    def add(value: object, *, source: str, status: str) -> None:
        ref = _entry_model_id(value, field="model_id")
        key = ref.casefold()
        identities.setdefault(key, set()).add(ref)
        evidence.setdefault(key, set()).add((str(source or "supplied_models"), str(status or "supplied")))

    raw_models = inventory.get("models", ())
    if isinstance(raw_models, (list, tuple)):
        for entry in raw_models:
            if isinstance(entry, str):
                add(entry, source="supplied_models", status="supplied")
            elif isinstance(entry, Mapping):
                model = _entry_model_id(entry, field="models.model_id")
                provider = str(entry.get("provider", "")).strip()
                add(model if "/" in model or not provider else f"{provider}/{model}", source=str(entry.get("source", "supplied_models")), status=str(entry.get("status", "supplied")))
    available = inventory.get("available_models", ())
    if isinstance(available, (list, tuple)):
        for entry in available:
            if isinstance(entry, Mapping):
                model = _entry_model_id(entry, field="available_models.model_id")
                provider = str(entry.get("provider", "")).strip()
                add(model if "/" in model or not provider else f"{provider}/{model}", source="available_models", status="configured")
    discovery = inventory.get("model_discovery")
    observations = discovery.get("observations", ()) if isinstance(discovery, Mapping) else ()
    if isinstance(observations, (list, tuple)):
        for entry in observations:
            if isinstance(entry, Mapping):
                model = _entry_model_id(entry, field="model_discovery.observations.model_id")
                provider = str(entry.get("provider", "")).strip()
                add(model if "/" in model or not provider else f"{provider}/{model}", source=str(entry.get("source", "model_discovery")), status=str(entry.get("status", "observed")))

    refs = tuple(min(identities[key], key=lambda value: (value.casefold(), value)) for key in sorted(identities))
    records = {
        key: {
            "identities": sorted(identities[key], key=lambda value: (value.casefold(), value)),
            "records": [{"source": source, "status": status} for source, status in sorted(evidence[key])],
        }
        for key in sorted(identities)
    }
    return refs, records


def _normalized_refs(values: Iterable[str]) -> tuple[str, ...]:
    by_key: dict[str, str] = {}
    for value in values:
        ref = _safe_ref(value, field="model reference")
        key = ref.casefold()
        if key not in by_key or (ref.casefold(), ref) < (by_key[key].casefold(), by_key[key]):
            by_key[key] = ref
    return tuple(by_key[key] for key in sorted(by_key))


def _missing_dimensions(*, status: str) -> dict[str, object]:
    return {
        "contract": {"status": status},
        "data_handling": {"verdict": VERDICT_UNKNOWN, "reason": REASON_NO_DOCUMENTED_CONTRACT, "status": status},
        "docs": {"paths": [], "sources": [], "status": status},
        "effort": {"reasoning_efforts": [], "status": status},
        "family_recognition": {"family": "", "status": status},
        "price": {"status": "absent", "reason": "no local pricing evidence"},
        "provider_eligibility": {"families": [], "status": "unknown", "reason": "provider readiness is not observed"},
    }


def _covered_dimensions(requested_model: str, contract: Mapping[str, object], projection: Mapping[str, str]) -> dict[str, object]:
    contract_id = str(projection["contract_model_id"])
    efforts = [str(value) for value in contract.get("reasoning_efforts", ())] if isinstance(contract.get("reasoning_efforts", ()), (list, tuple)) else []
    verdict = model_data_handling_verdict(requested_model, contracts=_MODEL_CONTRACTS)
    family = str(contract.get("family", ""))
    return {
        "contract": {"provenance": str(projection.get("provenance", "")), "schema_version": str(contract.get("schema_version", "")), "status": "covered"},
        "data_handling": {"training_use": verdict.get("training_use", ""), "retention": verdict.get("retention", ""), "verdict": verdict["verdict"], "reason": verdict["reason"], "status": "covered" if verdict["verdict"] != VERDICT_UNKNOWN else "missing"},
        "docs": {"paths": list(_MODEL_DOCS.get(contract_id, ())), "sources": [], "status": "missing"},
        "effort": {"floor": str(contract.get("effort_floor", "")), "reasoning_efforts": efforts, "status": "covered" if efforts else "missing"},
        "family_recognition": {"family": family, "status": "recognized" if family else "missing"},
        "price": {"status": "absent", "reason": "no local pricing evidence"},
        "provider_eligibility": {"families": [], "status": "unknown", "reason": "provider readiness is not observed"},
    }


def build_model_contract_coverage(
    inventory: Mapping[str, object],
    *,
    required_models: Iterable[str] = (),
    recommended_models: Iterable[str] = (),
    intentional_exclusions: Iterable[str] = (),
) -> dict[str, object]:
    """Compare a caller-supplied local inventory with exact declared metadata."""
    if not isinstance(inventory, Mapping):
        raise ValueError("model contract inventory must be a JSON object")
    _validate_inventory(inventory)
    inventory_models, inventory_evidence = _inventory_refs(inventory)
    required_refs = _normalized_refs(required_models)
    recommended_refs = _normalized_refs(recommended_models)
    exclusion_refs = _normalized_refs(intentional_exclusions)
    model_by_key: dict[str, str] = {}
    for refs in (inventory_models, recommended_refs, exclusion_refs, required_refs):
        for model in refs:
            model_by_key.setdefault(model.casefold(), model)
    all_models = tuple(model_by_key[key] for key in sorted(model_by_key))
    present = frozenset(value.casefold() for value in inventory_models)
    required = frozenset(value.casefold() for value in required_refs)
    recommended = frozenset(value.casefold() for value in recommended_refs)
    exclusions = frozenset(value.casefold() for value in exclusion_refs)
    inventory_status = str(inventory.get("inventory_status", inventory.get("status", "observed"))).strip().casefold() or "observed"
    if inventory_status not in {"observed", "cold", "unavailable"}:
        raise ValueError("inventory status must be one of observed, cold, unavailable")
    comparison_seed = {"models": list(inventory_models), "source": str(inventory.get("source", "supplied_json")), "status": inventory_status}
    inventory_record = {"digest": _digest(comparison_seed), "model_count": len(inventory_models), "source": comparison_seed["source"], "status": inventory_status, "supplied_digest": str(inventory.get("digest", ""))}

    rows: list[dict[str, object]] = []
    for requested_model in all_models:
        key = requested_model.casefold()
        excluded = key in exclusions
        projection = None if excluded else _projection(requested_model)
        status = "intentional_exclusion" if excluded else (str(projection.get("provenance", "")) if projection else "missing")
        if status == "missing" and key in required:
            actionability = "required_missing"
        elif status == "missing" and key in recommended:
            actionability = "recommended_missing"
        elif status == "missing":
            actionability = "optional_discovery"
        elif status == "intentional_exclusion":
            actionability = "intentional_exclusion"
        else:
            actionability = "covered"
        contract = _MODEL_CONTRACTS.get(str(projection["contract_model_id"])) if projection else None
        dimensions = _covered_dimensions(requested_model, contract, projection) if contract is not None and projection is not None else _missing_dimensions(status=status)
        evidence = inventory_evidence.get(key, {})
        rows.append({
            "actionability": actionability,
            "canonical_model_id": str(projection["canonical_model_id"]) if projection else _unqualified_model_id(requested_model),
            "contract_model_id": str(projection["contract_model_id"]) if projection else None,
            "dimensions": dimensions,
            "inventory_evidence": {"digest": inventory_record["digest"], "identities": list(evidence.get("identities", [])), "present": key in present, "records": list(evidence.get("records", [])), "source": inventory_record["source"], "status": inventory_record["status"]},
            "requested_model": requested_model,
            "status": status,
        })

    status_counts = {status: 0 for status in MODEL_CONTRACT_COVERAGE_STATUSES}
    action_counts = {name: 0 for name in ("required_missing", "recommended_missing", "optional_discovery")}
    for row in rows:
        status_counts[str(row["status"])] += 1
        if str(row["actionability"]) in action_counts:
            action_counts[str(row["actionability"])] += 1
    if inventory_status == "cold":
        outcome = "cold_inventory"
    elif inventory_status == "unavailable":
        outcome = "unavailable_inventory"
    elif action_counts["required_missing"]:
        outcome = "required_gaps"
    elif action_counts["recommended_missing"]:
        outcome = "recommended_gaps"
    elif action_counts["optional_discovery"]:
        outcome = "optional_gaps"
    else:
        outcome = "covered"
    comparison = {
        "inventory": inventory_record,
        "models": rows,
        "requirements": {"intentional_exclusions": list(exclusion_refs), "recommended_models": list(recommended_refs), "required_models": list(required_refs)},
        "summary": {**action_counts, "outcome": outcome, "status_counts": status_counts, "total_models": len(rows)},
    }
    return {"blocking": bool(action_counts["required_missing"]), "claim_boundary": MODEL_CONTRACT_COVERAGE_CLAIM_BOUNDARY, "comparison": comparison, "comparison_digest": _digest(comparison), "schema_version": MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION}


def coverage_exit_code(report: Mapping[str, object]) -> int:
    return 1 if report.get("blocking") is True else 0


# ---------------------------------------------------------------------------
# Sensitive-data policy

DATA_HANDLING_VERDICT_SCHEMA_VERSION: Final[str] = "model_data_handling_verdict/v1"
SENSITIVE_WORK_CHAIN_SCHEMA_VERSION: Final[str] = "sensitive_work_chain/v1"
VERDICT_PERMITTING: Final[str] = "documented_permitting"
VERDICT_CONFLICTING: Final[str] = "documented_conflicting"
VERDICT_UNKNOWN: Final[str] = "unknown"
DATA_HANDLING_VERDICTS: Final[tuple[str, ...]] = (VERDICT_PERMITTING, VERDICT_CONFLICTING, VERDICT_UNKNOWN)
REASON_DOCUMENTED_DEFAULT_PERMITS: Final[str] = "documented_default_permits"
REASON_TRAINING_USE_INCLUDES: Final[str] = "documented_default_trains_on_input"
REASON_RETENTION_INDEFINITE: Final[str] = "documented_default_retains_indefinitely"
REASON_NO_DOCUMENTED_CONTRACT: Final[str] = "no_documented_contract"
REASON_AXIS_NOT_DECLARED: Final[str] = "data_handling_axis_not_declared"
REASON_POLICY_NOT_RECORDED: Final[str] = "data_handling_policy_not_recorded"
REASON_TEXT: Final[dict[str, str]] = {
    REASON_DOCUMENTED_DEFAULT_PERMITS: "The documented default excludes training use and records bounded or no retention; this is not account-level permission.",
    REASON_TRAINING_USE_INCLUDES: "The documented default uses input for training, so sensitive work is excluded.",
    REASON_RETENTION_INDEFINITE: "The documented default retains input indefinitely, so sensitive work is excluded.",
    REASON_NO_DOCUMENTED_CONTRACT: "No exact or explicitly declared contract resolves, so policy is unknown and excluded.",
    REASON_AXIS_NOT_DECLARED: "A contract resolves but declares no data_handling axis, so policy is unknown and excluded.",
    REASON_POLICY_NOT_RECORDED: "The data-handling axis is present but its training/retention policy is not recorded, so it cannot permit.",
}
SENSITIVE_WORK_CHAIN_CLAIM_BOUNDARY: Final[str] = (
    "A data-handling verdict reads only the vendor-documented default recorded in a local contract. "
    "It is not account agreement, provider availability, owner selection, execution, or a decision that "
    "the caller's message is sensitive; sensitivity is an explicit caller declaration."
)


def model_data_handling_verdict(
    model_id: str,
    *,
    contracts: Mapping[str, Mapping[str, object]] = _MODEL_CONTRACTS,
) -> dict[str, object]:
    """Return documented permitting, conflicting, or unknown policy for one id."""
    contract = _contract_for(model_id, contracts)
    if contract is None:
        return _policy_verdict(model_id, VERDICT_UNKNOWN, REASON_NO_DOCUMENTED_CONTRACT)
    axis = contract.get("data_handling")
    if not isinstance(axis, Mapping):
        return _policy_verdict(model_id, VERDICT_UNKNOWN, REASON_AXIS_NOT_DECLARED)
    training_use = str(axis.get("training_use", "not_recorded"))
    retention = str(axis.get("retention", "not_recorded"))
    training_excluded = training_use in {"excluded", "excluded_by_default"}
    training_included = training_use in {"included", "included_by_default"}
    if training_use == "not_recorded" or retention == "not_recorded":
        return _policy_verdict(model_id, VERDICT_UNKNOWN, REASON_POLICY_NOT_RECORDED, training_use=training_use, retention=retention)
    if training_included:
        return _policy_verdict(model_id, VERDICT_CONFLICTING, REASON_TRAINING_USE_INCLUDES, training_use=training_use, retention=retention)
    if not training_excluded:
        return _policy_verdict(model_id, VERDICT_UNKNOWN, REASON_POLICY_NOT_RECORDED, training_use=training_use, retention=retention)
    if retention not in {"none", "bounded"}:
        return _policy_verdict(model_id, VERDICT_CONFLICTING, REASON_RETENTION_INDEFINITE, training_use=training_use, retention=retention)
    return _policy_verdict(model_id, VERDICT_PERMITTING, REASON_DOCUMENTED_DEFAULT_PERMITS, training_use=training_use, retention=retention)


def _policy_verdict(model_id: str, verdict: str, reason: str, *, training_use: str = "", retention: str = "") -> dict[str, object]:
    return {
        "schema_version": DATA_HANDLING_VERDICT_SCHEMA_VERSION,
        "model": model_id,
        "verdict": verdict,
        "reason": reason,
        "reason_text": REASON_TEXT[reason],
        "training_use": training_use,
        "retention": retention,
        "claim_boundary": SENSITIVE_WORK_CHAIN_CLAIM_BOUNDARY,
    }


def data_handling_filtered_chain(
    model_ids: Sequence[str] | Iterable[str],
    *,
    work_is_sensitive: bool,
    contracts: Mapping[str, Mapping[str, object]] = _MODEL_CONTRACTS,
) -> dict[str, object]:
    requested = [str(model_id or "").strip() for model_id in model_ids if str(model_id or "").strip()]
    if not work_is_sensitive:
        return {
            "schema_version": SENSITIVE_WORK_CHAIN_SCHEMA_VERSION,
            "work_is_sensitive": False,
            "applied": False,
            "chain": list(requested),
            "entries": [],
            "excluded": [],
            "summary": {"requested": len(requested), "permitted": len(requested), "excluded_conflicting_policy": 0, "excluded_unknown_policy": 0},
            "reason_codes": dict(REASON_TEXT),
            "claim_boundary": SENSITIVE_WORK_CHAIN_CLAIM_BOUNDARY,
        }
    entries = [model_data_handling_verdict(model_id, contracts=contracts) for model_id in requested]
    kept = [str(entry["model"]) for entry in entries if entry["verdict"] == VERDICT_PERMITTING]
    excluded = [entry for entry in entries if entry["verdict"] != VERDICT_PERMITTING]
    return {
        "schema_version": SENSITIVE_WORK_CHAIN_SCHEMA_VERSION,
        "work_is_sensitive": True,
        "applied": True,
        "chain": kept,
        "entries": entries,
        "excluded": excluded,
        "summary": {
            "requested": len(requested),
            "permitted": len(kept),
            "excluded_conflicting_policy": sum(1 for entry in excluded if entry["verdict"] == VERDICT_CONFLICTING),
            "excluded_unknown_policy": sum(1 for entry in excluded if entry["verdict"] == VERDICT_UNKNOWN),
        },
        "reason_codes": dict(REASON_TEXT),
        "claim_boundary": SENSITIVE_WORK_CHAIN_CLAIM_BOUNDARY,
    }


__all__ = [
    "COMPLEXITY_CLAIM_BOUNDARY", "COMPLEXITY_CHAIN_STATUSES", "COMPLEXITY_LENGTH_BANDS",
    "COMPLEXITY_MODEL_RECOMMENDATION_SCHEMA_VERSION", "COMPLEXITY_RECOMMENDATION_STATUSES",
    "COMPLEXITY_SIGNAL_NAMES", "COMPLEXITY_SIGNALS", "COMPLEXITY_SKILL_CLASS_WEIGHTS",
    "COMPLEXITY_TIER_EFFORTS", "COMPLEXITY_TIER_MODEL_CLASSES", "COMPLEXITY_TIER_THRESHOLDS", "COMPLEXITY_TIERS",
    "DATA_HANDLING_VERDICTS", "DATA_HANDLING_VERDICT_SCHEMA_VERSION", "DECLARED_MODEL_CONTRACT_PROJECTIONS",
    "MODEL_CONTRACTS", "MODEL_CONTRACT_COVERAGE_CLAIM_BOUNDARY", "MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION",
    "MODEL_CONTRACT_COVERAGE_STATUSES", "REASON_AXIS_NOT_DECLARED", "REASON_DOCUMENTED_DEFAULT_PERMITS",
    "REASON_NO_DOCUMENTED_CONTRACT", "REASON_POLICY_NOT_RECORDED", "REASON_RETENTION_INDEFINITE", "REASON_TEXT",
    "REASON_TRAINING_USE_INCLUDES", "RETENTION_BOUNDED", "RETENTION_INDEFINITE", "RETENTION_NONE", "RETENTION_NOT_RECORDED",
    "SENSITIVE_WORK_CHAIN_CLAIM_BOUNDARY", "SENSITIVE_WORK_CHAIN_SCHEMA_VERSION", "TRAINING_USE_EXCLUDED",
    "TRAINING_USE_INCLUDED", "TRAINING_USE_NOT_RECORDED", "VERDICT_CONFLICTING", "VERDICT_PERMITTING", "VERDICT_UNKNOWN",
    "build_model_contract_coverage", "complexity_class_for_skill", "coverage_exit_code", "data_handling_filtered_chain",
    "model_data_handling_verdict", "recommend_model_for_complexity", "score_request_complexity", "tier_for_score",
]
