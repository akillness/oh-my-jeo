"""Metadata-only what-if children of an accepted Hermes plan.

Variants preserve the accepted plan as the source of truth.  They record explicit
changes and references for review; they never imply acceptance, replay, dispatch,
or execution.
"""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

from ..local_store import atomic_write_json, ensure_dir
from ..paths import OmjPaths

PLAN_VARIANT_SCHEMA_VERSION = "plan_variant/v1"
PLAN_VARIANT_DELTA_SCHEMA_VERSION = "plan_variant_delta/v1"
PLAN_VARIANT_REF_SCHEMA_VERSION = "plan_variant_ref/v1"
PLAN_VARIANT_HANDOFF_SCHEMA_VERSION = "plan_variant_handoff/v1"
PLAN_VARIANT_PARENT_SCHEMA_VERSION = "hermes_plan/v1"
PLAN_VARIANT_PARENT_STATUS = "accepted"

PLAN_VARIANT_DELTA_DIMENSIONS = (
    "assumption",
    "scope",
    "coding_owner",
    "policy",
    "acceptance_criteria",
    "verification",
    "other",
)
PLAN_VARIANT_REF_KINDS = (
    "plan_artifact",
    "context_pack",
    "source",
    "evidence",
    "memory_record",
    "unknown",
)
PLAN_VARIANT_HANDOFF_DECISIONS = ("undecided", "parent_plan", "variant")
PLAN_VARIANT_HANDOFF_CANDIDATE_KINDS = ("parent_plan", "variant")
PLAN_VARIANT_PREPARED_STATE = "prepared_not_observed"
PLAN_VARIANT_HANDOFF_QUESTION = (
    "Which plan should become the next handoff: the accepted parent plan or this variant?"
)
PLAN_VARIANT_HANDOFF_BOUNDARY = (
    "Recording a decision here is intent only. The accepted plan artifact stays unchanged "
    "until a separate plan lifecycle command runs."
)
PLAN_VARIANT_CLAIM_BOUNDARY = (
    "A plan_variant/v1 record is a metadata-only what-if child of an accepted Hermes plan. "
    "It is not the accepted plan, not plan acceptance, and not replay, dispatch, execution, "
    "verification, review, CI, merge-readiness, or merge evidence."
)
PLAN_VARIANT_NOT_OBSERVED = (
    "plan_acceptance",
    "plan_replay",
    "tool_execution",
    "network_call",
    "coding_dispatch",
    "executor_result",
    "verification",
    "review",
)

PLAN_VARIANT_KEYS = (
    "schema_version", "variant_id", "variant_digest", "name", "rationale", "created_at",
    "parent_plan_path", "parent_plan_status", "parent_plan_schema_version", "parent_plan_sha256",
    "parent_task_statement_sha256", "deltas", "delta_count", "changed_inputs", "inherited_refs",
    "inherited_ref_count", "refs_requiring_reevaluation", "prepared_state", "next_handoff",
    "claim_boundary", "not_evidence_until_observed",
)
PLAN_VARIANT_DELTA_KEYS = ("schema_version", "dimension", "label", "parent_value", "variant_value", "reason")
PLAN_VARIANT_REF_KEYS = ("schema_version", "kind", "ref", "reviewed", "note")
PLAN_VARIANT_HANDOFF_KEYS = (
    "schema_version", "decision", "question", "requires_user_choice", "candidates", "boundary",
)
PLAN_VARIANT_HANDOFF_CANDIDATE_KEYS = ("kind", "ref", "digest")


def normalize_plan_variant_dimension(dimension: str | None) -> str:
    normalized = _key(dimension or "")
    aliases = {
        "assumption": "assumption", "assumptions": "assumption", "clarified assumption": "assumption",
        "scope": "scope", "goal": "scope", "non goal": "scope",
        "coding owner": "coding_owner", "owner": "coding_owner", "executor": "coding_owner",
        "policy": "policy", "constraint": "policy",
        "acceptance criteria": "acceptance_criteria", "acceptance": "acceptance_criteria",
        "verification": "verification", "verification plan": "verification", "other": "other",
    }
    return aliases.get(normalized, "other")


def normalize_plan_variant_ref_kind(kind: str | None) -> str:
    normalized = _key(kind or "").replace(" ", "_")
    return normalized if normalized in PLAN_VARIANT_REF_KINDS else "unknown"


def build_plan_variant_delta(
    dimension: str,
    label: str,
    parent_value: str,
    variant_value: str,
    reason: str = "",
) -> dict[str, object]:
    """Build one explicit difference between parent and variant."""
    return {
        "schema_version": PLAN_VARIANT_DELTA_SCHEMA_VERSION,
        "dimension": normalize_plan_variant_dimension(dimension),
        "label": str(label).strip(),
        "parent_value": str(parent_value).strip(),
        "variant_value": str(variant_value).strip(),
        "reason": str(reason).strip(),
    }


def build_plan_variant_ref(
    kind: str,
    ref: str,
    reviewed: bool = False,
    note: str = "",
) -> dict[str, object]:
    """Build one parent reference; only reviewed refs are inherited."""
    if not isinstance(reviewed, bool):
        raise ValueError("reviewed must be a boolean")
    return {
        "schema_version": PLAN_VARIANT_REF_SCHEMA_VERSION,
        "kind": normalize_plan_variant_ref_kind(kind),
        "ref": str(ref).strip(),
        "reviewed": reviewed,
        "note": str(note).strip(),
    }


def build_plan_variant(
    parent_artifact: dict[str, Any],
    name: str,
    deltas: Iterable[dict[str, Any]],
    refs: Iterable[dict[str, Any]] = (),
    created_at: str | None = None,
) -> dict[str, object]:
    """Build a deterministic ``plan_variant/v1`` child without mutating parent."""
    variant_name = str(name).strip()
    if not variant_name:
        raise ValueError("plan variant requires a name")
    parent_schema = str(parent_artifact.get("schema_version", ""))
    if parent_schema != PLAN_VARIANT_PARENT_SCHEMA_VERSION:
        raise ValueError(f"plan variant requires a {PLAN_VARIANT_PARENT_SCHEMA_VERSION} parent artifact")
    parent_status = str(parent_artifact.get("status", ""))
    if parent_status != PLAN_VARIANT_PARENT_STATUS:
        raise ValueError("plan variant requires an accepted parent plan")
    parent_sha256 = str(parent_artifact.get("sha256", ""))
    if not _is_sha256(parent_sha256):
        raise ValueError("plan variant requires a parent plan sha256 digest")
    normalized_deltas = [_coerce_delta(delta) for delta in deltas]
    if not normalized_deltas:
        raise ValueError("plan variant requires at least one delta")

    parent_path = str(parent_artifact.get("path", ""))
    if not parent_path.strip():
        raise ValueError("plan variant requires a parent plan path")
    supplied_refs = [
        build_plan_variant_ref(
            "plan_artifact",
            parent_path,
            reviewed=True,
            note="Accepted parent plan artifact; every input not named in deltas is inherited from it.",
        ),
        *(_coerce_ref(ref) for ref in refs),
    ]
    inherited = [ref for ref in supplied_refs if ref["reviewed"]]
    reevaluate = [ref for ref in supplied_refs if not ref["reviewed"]]
    digest = _variant_digest(parent_sha256, variant_name, normalized_deltas)
    variant_id = f"plan-variant-{digest[:12]}"
    return {
        "schema_version": PLAN_VARIANT_SCHEMA_VERSION,
        "variant_id": variant_id,
        "variant_digest": digest,
        "name": variant_name,
        "rationale": "",
        "created_at": "" if created_at is None else str(created_at).strip(),
        "parent_plan_path": parent_path,
        "parent_plan_status": parent_status,
        "parent_plan_schema_version": parent_schema,
        "parent_plan_sha256": parent_sha256,
        "parent_task_statement_sha256": str(parent_artifact.get("task_statement_sha256", "")),
        "deltas": normalized_deltas,
        "delta_count": len(normalized_deltas),
        "changed_inputs": [_changed_input_line(delta) for delta in normalized_deltas],
        "inherited_refs": inherited,
        "inherited_ref_count": len(inherited),
        "refs_requiring_reevaluation": reevaluate,
        "prepared_state": PLAN_VARIANT_PREPARED_STATE,
        "next_handoff": {
            "schema_version": PLAN_VARIANT_HANDOFF_SCHEMA_VERSION,
            "decision": "undecided",
            "question": PLAN_VARIANT_HANDOFF_QUESTION,
            "requires_user_choice": True,
            "candidates": [
                {"kind": "parent_plan", "ref": parent_path, "digest": parent_sha256},
                {"kind": "variant", "ref": variant_id, "digest": digest},
            ],
            "boundary": PLAN_VARIANT_HANDOFF_BOUNDARY,
        },
        "claim_boundary": PLAN_VARIANT_CLAIM_BOUNDARY,
        "not_evidence_until_observed": list(PLAN_VARIANT_NOT_OBSERVED),
    }


def validate_plan_variant(payload: dict[str, Any]) -> list[str]:
    """Return all contract violations; empty means valid."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["plan_variant must be an object"]
    errors.extend(_key_set_errors(payload, PLAN_VARIANT_KEYS, "plan_variant"))
    if payload.get("schema_version") != PLAN_VARIANT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PLAN_VARIANT_SCHEMA_VERSION}")
    if not str(payload.get("variant_id", "")).startswith("plan-variant-"):
        errors.append("variant_id must start with plan-variant-")
    if not _is_sha256(str(payload.get("variant_digest", ""))):
        errors.append("variant_digest must be a sha256 hex digest")
    if not str(payload.get("name", "")).strip():
        errors.append("name must not be empty")
    if payload.get("parent_plan_schema_version") != PLAN_VARIANT_PARENT_SCHEMA_VERSION:
        errors.append(f"parent_plan_schema_version must be {PLAN_VARIANT_PARENT_SCHEMA_VERSION}")
    if payload.get("parent_plan_status") != PLAN_VARIANT_PARENT_STATUS:
        errors.append(f"parent_plan_status must be {PLAN_VARIANT_PARENT_STATUS}")
    if not _is_sha256(str(payload.get("parent_plan_sha256", ""))):
        errors.append("parent_plan_sha256 must be a sha256 hex digest")
    task_digest = str(payload.get("parent_task_statement_sha256", ""))
    if task_digest and not _is_sha256(task_digest):
        errors.append("parent_task_statement_sha256 must be a sha256 hex digest when present")
    if payload.get("prepared_state") != PLAN_VARIANT_PREPARED_STATE:
        errors.append(f"prepared_state must be {PLAN_VARIANT_PREPARED_STATE}")
    if payload.get("claim_boundary") != PLAN_VARIANT_CLAIM_BOUNDARY:
        errors.append("claim_boundary must deny that a variant is the accepted plan or evidence")
    if not set(PLAN_VARIANT_NOT_OBSERVED).issubset(set(_string_list(payload.get("not_evidence_until_observed")))):
        errors.append("not_evidence_until_observed must include all plan-variant boundaries")

    deltas = payload.get("deltas")
    if not isinstance(deltas, list) or not deltas:
        errors.append("deltas must be a non-empty list")
    else:
        for index, delta in enumerate(deltas):
            errors.extend(f"deltas[{index}]: {error}" for error in _delta_errors(delta))
        if payload.get("delta_count") != len(deltas):
            errors.append("delta_count must match deltas")
        expected_changed_inputs = [_changed_input_line(delta) for delta in deltas if isinstance(delta, dict)]
        if payload.get("changed_inputs") != expected_changed_inputs:
            errors.append("changed_inputs must list one line per delta")

    if isinstance(deltas, list) and deltas and all(isinstance(delta, dict) and not _delta_errors(delta) for delta in deltas):
        expected_digest = _variant_digest(str(payload.get("parent_plan_sha256", "")), str(payload.get("name", "")), deltas)
        if payload.get("variant_digest") != expected_digest:
            errors.append("variant_digest does not match the parent, name, and deltas")
        if payload.get("variant_id") != f"plan-variant-{expected_digest[:12]}":
            errors.append("variant_id must match variant_digest")
    parent_path = str(payload.get("parent_plan_path", "")).strip()
    if not parent_path:
        errors.append("parent_plan_path must not be empty")
    inherited = payload.get("inherited_refs")
    if not isinstance(inherited, list) or not inherited:
        errors.append("inherited_refs must be a non-empty list")
    else:
        for index, ref in enumerate(inherited):
            errors.extend(f"inherited_refs[{index}]: {error}" for error in _ref_errors(ref))
            if isinstance(ref, dict) and not ref.get("reviewed"):
                errors.append(f"inherited_refs[{index}]: only reviewed references may be inherited")
        if payload.get("inherited_ref_count") != len(inherited):
            errors.append("inherited_ref_count must match inherited_refs")
        if parent_path and not any(
            isinstance(ref, dict)
            and ref.get("kind") == "plan_artifact"
            and ref.get("reviewed") is True
            and str(ref.get("ref", "")).strip() == parent_path
            for ref in inherited
        ):
            errors.append("inherited_refs must include the reviewed parent plan artifact")

    reevaluate = payload.get("refs_requiring_reevaluation")
    if not isinstance(reevaluate, list):
        errors.append("refs_requiring_reevaluation must be a list")
    else:
        for index, ref in enumerate(reevaluate):
            errors.extend(f"refs_requiring_reevaluation[{index}]: {error}" for error in _ref_errors(ref))
            if isinstance(ref, dict) and ref.get("reviewed"):
                errors.append(f"refs_requiring_reevaluation[{index}]: a reviewed reference belongs in inherited_refs")
    errors.extend(_handoff_errors(payload.get("next_handoff")))
    handoff = payload.get("next_handoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("candidates"), list) and len(handoff["candidates"]) == 2:
        candidates = handoff["candidates"]
        if all(isinstance(candidate, dict) for candidate in candidates):
            parent_candidate, variant_candidate = candidates
            if parent_candidate.get("ref") != payload.get("parent_plan_path") or parent_candidate.get("digest") != payload.get("parent_plan_sha256"):
                errors.append("next_handoff parent candidate must reference the accepted parent")
            if variant_candidate.get("ref") != payload.get("variant_id") or variant_candidate.get("digest") != payload.get("variant_digest"):
                errors.append("next_handoff variant candidate must reference this variant")
    return errors


def render_plan_variant_text(variant: dict[str, Any]) -> str:
    lines = [
        f"Plan variant: {variant.get('name', '')} ({variant.get('variant_id', '')})",
        f"Parent plan: {variant.get('parent_plan_path', '')}",
        f"Parent digest: {variant.get('parent_plan_sha256', '')} (unchanged by this variant)",
    ]
    rationale = str(variant.get("rationale", ""))
    if rationale:
        lines.append(f"Rationale: {rationale}")
    lines.extend(("", "Changed inputs:"))
    lines.extend(f"  - {line}" for line in _string_list(variant.get("changed_inputs")))
    lines.extend(("", "Inherited references:"))
    lines.extend(_ref_lines(variant.get("inherited_refs")))
    reevaluate = variant.get("refs_requiring_reevaluation")
    if isinstance(reevaluate, list) and reevaluate:
        lines.extend(("", "Re-evaluate before any handoff:"))
        lines.extend(_ref_lines(reevaluate))
    lines.extend(("", f"Next handoff: {variant.get('next_handoff', {}).get('decision', 'undecided') if isinstance(variant.get('next_handoff'), dict) else 'undecided'}"))
    handoff = variant.get("next_handoff")
    if isinstance(handoff, dict):
        lines.append(f"  {handoff.get('question', '')}")
        for candidate in handoff.get("candidates", []):
            if isinstance(candidate, dict):
                lines.append(f"  - {candidate.get('kind', '')}: {candidate.get('ref', '')}")
    lines.extend(("", f"Prepared state: {variant.get('prepared_state', '')}", str(variant.get("claim_boundary", ""))))
    return "\n".join(lines)


def write_plan_variant(paths: OmjPaths, variant: dict[str, Any]) -> dict[str, object]:
    """Persist metadata under the OMJ local store; parent artifact is untouched."""
    errors = validate_plan_variant(variant)
    if errors:
        raise ValueError("; ".join(errors))
    variants_dir = paths.omj_home / "plan-variants"
    ensure_dir(variants_dir, private=True)
    path = variants_dir / f"{variant['variant_id']}.json"
    atomic_write_json(path, dict(variant), private=True)
    return {
        "path": str(path),
        "kind": "plan_variant",
        "schema_version": PLAN_VARIANT_SCHEMA_VERSION,
        "variant_id": variant["variant_id"],
        "parent_plan_sha256": variant["parent_plan_sha256"],
    }


def _coerce_delta(delta: dict[str, Any]) -> dict[str, object]:
    return build_plan_variant_delta(
        str(delta.get("dimension", "")), str(delta.get("label", "")),
        str(delta.get("parent_value", "")), str(delta.get("variant_value", "")), str(delta.get("reason", "")),
    )


def _coerce_ref(ref: dict[str, Any]) -> dict[str, object]:
    reviewed = ref.get("reviewed", False)
    return build_plan_variant_ref(
        str(ref.get("kind", "")), str(ref.get("ref", "")), reviewed, str(ref.get("note", "")),
    )


def _changed_input_line(delta: dict[str, Any]) -> str:
    return f"{delta.get('dimension', 'other')} | {str(delta.get('label', '')) or 'unnamed input'}: {delta.get('parent_value', '')} -> {delta.get('variant_value', '')}"


def _ref_lines(refs: object) -> list[str]:
    if not isinstance(refs, list) or not refs:
        return ["  - None recorded."]
    lines: list[str] = []
    for ref in refs:
        if isinstance(ref, dict):
            note = str(ref.get("note", ""))
            lines.append(f"  - {ref.get('kind', 'unknown')}: {ref.get('ref', '')}{f' — {note}' if note else ''}")
    return lines or ["  - None recorded."]


def _delta_errors(delta: object) -> list[str]:
    if not isinstance(delta, dict):
        return ["delta must be an object"]
    errors = _key_set_errors(delta, PLAN_VARIANT_DELTA_KEYS, "delta")
    if delta.get("schema_version") != PLAN_VARIANT_DELTA_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PLAN_VARIANT_DELTA_SCHEMA_VERSION}")
    if delta.get("dimension") not in PLAN_VARIANT_DELTA_DIMENSIONS:
        errors.append("dimension is unsupported")
    if not str(delta.get("label", "")).strip():
        errors.append("label must not be empty")
    if str(delta.get("parent_value", "")) == str(delta.get("variant_value", "")):
        errors.append("parent_value and variant_value must differ")
    return errors


def _ref_errors(ref: object) -> list[str]:
    if not isinstance(ref, dict):
        return ["reference must be an object"]
    errors = _key_set_errors(ref, PLAN_VARIANT_REF_KEYS, "reference")
    if ref.get("schema_version") != PLAN_VARIANT_REF_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PLAN_VARIANT_REF_SCHEMA_VERSION}")
    if ref.get("kind") not in PLAN_VARIANT_REF_KINDS:
        errors.append("kind is unsupported")
    if not str(ref.get("ref", "")).strip():
        errors.append("ref must not be empty")
    if not isinstance(ref.get("reviewed"), bool):
        errors.append("reviewed must be a boolean")
    return errors


def _handoff_errors(handoff: object) -> list[str]:
    if not isinstance(handoff, dict):
        return ["next_handoff must be an object"]
    errors = _key_set_errors(handoff, PLAN_VARIANT_HANDOFF_KEYS, "next_handoff")
    if handoff.get("schema_version") != PLAN_VARIANT_HANDOFF_SCHEMA_VERSION:
        errors.append(f"next_handoff schema_version must be {PLAN_VARIANT_HANDOFF_SCHEMA_VERSION}")
    if handoff.get("decision") not in PLAN_VARIANT_HANDOFF_DECISIONS:
        errors.append("next_handoff decision is unsupported")
    if not isinstance(handoff.get("requires_user_choice"), bool):
        errors.append("next_handoff requires_user_choice must be a boolean")
    if handoff.get("boundary") != PLAN_VARIANT_HANDOFF_BOUNDARY:
        errors.append("next_handoff boundary must keep the accepted plan unchanged")
    candidates = handoff.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        errors.append("next_handoff must offer the parent plan and the variant")
        return errors
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"next_handoff candidates[{index}]: candidate must be an object")
            continue
        errors.extend(f"next_handoff candidates[{index}]: {error}" for error in _key_set_errors(candidate, PLAN_VARIANT_HANDOFF_CANDIDATE_KEYS, "candidate"))
        if candidate.get("kind") not in PLAN_VARIANT_HANDOFF_CANDIDATE_KINDS:
            errors.append(f"next_handoff candidates[{index}]: kind is unsupported")
    kinds = [candidate.get("kind") for candidate in candidates if isinstance(candidate, dict)]
    if kinds != list(PLAN_VARIANT_HANDOFF_CANDIDATE_KINDS):
        errors.append("next_handoff candidates must be the parent plan then the variant")
    return errors


def _key_set_errors(payload: object, expected: tuple[str, ...], label: str) -> list[str]:
    if not isinstance(payload, dict):
        return [f"{label} must be an object"]
    missing = sorted(set(expected) - set(payload))
    unexpected = sorted(set(payload) - set(expected))
    errors: list[str] = []
    if missing:
        errors.append(f"{label} is missing keys: {', '.join(missing)}")
    if unexpected:
        errors.append(f"{label} has unexpected keys: {', '.join(unexpected)}")
    return errors


def _string_list(value: object) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _variant_digest(parent_sha256: str, name: str, deltas: list[dict[str, object]]) -> str:
    parts = [parent_sha256, _key(name)]
    for delta in deltas:
        parts.extend(
            (
                str(delta["dimension"]),
                _key(str(delta["label"])),
                str(delta["parent_value"]),
                str(delta["variant_value"]),
            )
        )
    # Length-prefix each field so delimiters in user values cannot collide.
    seed = "".join(f"{len(part)}:{part}" for part in parts)
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())
