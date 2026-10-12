from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.resources
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


PREPARED_INDEX_SCHEMA_VERSION = "prepared_guidance_index/v1"
PREPARED_MEMBER_SCHEMA_VERSION = "prepared_guidance_member/v1"
PREPARED_MANIFEST_SCHEMA_VERSION = "prepared_guidance_source_manifest/v1"
PREPARED_NOT_OBSERVED = True

_MEMBER_FIELDS = (
    "canonical_id",
    "family_id",
    "description",
    "triggers",
    "category",
    "phase",
    "role",
    "source_folder",
    "source_path",
    "source_sha256",
    "required_inputs",
    "expected_outputs",
    "artifact_expectations",
    "acceptance_criteria",
    "handoff_policy",
    "catalog_rules",
    "local_contract_ids",
    "references",
    "source_gaps",
    "blocked_prerequisites",
    "evidence_boundary",
)
_REFERENCE_FIELDS = ("relative_path", "content", "source_path", "source_sha256")
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _static_members() -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for module_name in ("prepared_data_1", "prepared_data_2", "prepared_data_3", "prepared_data_4"):
        module = __import__(f"{__package__}.{module_name}", fromlist=["PREPARED_MEMBERS"])
        records.extend(deepcopy(dict(record)) for record in module.PREPARED_MEMBERS)
    return tuple(records)


# Kept as a public, patchable sequence for release/catalog validators.  The
# packaged manifest remains the source-of-truth for ids and pinned metadata.
PREPARED_MEMBERS: tuple[dict[str, Any], ...] = _static_members()


def _manifest_resource():
    return importlib.resources.files(__package__).joinpath("prepared_sources.json")


def _load_manifest() -> dict[str, Any]:
    resource = _manifest_resource()
    try:
        raw = resource.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise ValueError("prepared guidance manifest is missing: src/skills/prepared_sources.json") from exc
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"prepared guidance manifest is invalid JSON: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("prepared guidance manifest must be an object")
    return manifest


def _manifest_members(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    members = manifest.get("members")
    if isinstance(members, Mapping):
        return {str(key): dict(value) for key, value in members.items() if isinstance(value, Mapping)}
    if isinstance(members, Sequence) and not isinstance(members, (str, bytes)):
        output: dict[str, dict[str, Any]] = {}
        for value in members:
            if isinstance(value, Mapping) and value.get("canonical_id"):
                output[str(value["canonical_id"])] = dict(value)
        return output
    return {}


def _safe_relative(value: object, *, label: str) -> str:
    path = str(value or "").strip()
    parts = path.replace("\\", "/").split("/")
    if not path or path.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe {label}: {path!r}")
    return "/".join(parts)


def _member_records(members: object | None) -> list[dict[str, Any]]:
    value = PREPARED_MEMBERS if members is None else members
    if isinstance(value, Mapping):
        return [dict(record) for record in value.values() if isinstance(record, Mapping)]
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("prepared guidance members must be a sequence or mapping")
    return [dict(record) for record in value if isinstance(record, Mapping)]


def prepared_guidance_errors(members: object | None = None) -> list[str]:
    errors: list[str] = []
    try:
        manifest = _load_manifest()
    except ValueError as exc:
        return [str(exc)]

    if manifest.get("schema_version") != PREPARED_MANIFEST_SCHEMA_VERSION:
        errors.append("prepared guidance manifest has an unsupported schema_version")
    for field in ("source_repository", "source_commit"):
        if not isinstance(manifest.get(field), str) or not str(manifest[field]).strip():
            errors.append(f"prepared guidance manifest missing {field}")
    manifest_members = _manifest_members(manifest)
    if not manifest_members:
        errors.append("prepared guidance manifest members must be a non-empty mapping")

    try:
        records = _member_records(members)
    except ValueError as exc:
        return errors + [str(exc)]
    seen_ids: set[str] = set()
    seen_sources: dict[str, str] = {}
    seen_refs: dict[str, str] = {}
    manifest_ids = set(manifest_members)
    if members is None and set(record.get("canonical_id") for record in records) != manifest_ids:
        errors.append("prepared guidance data and manifest member ids differ")
    for record in records:
        canonical_id = str(record.get("canonical_id") or "")
        if not _SAFE_ID.fullmatch(canonical_id):
            errors.append(f"invalid canonical_id: {canonical_id!r}")
            continue
        if canonical_id in seen_ids:
            errors.append(f"duplicate canonical_id: {canonical_id}")
        seen_ids.add(canonical_id)
        if canonical_id not in manifest_members:
            errors.append(f"unknown canonical_id: {canonical_id}")
            continue
        if set(record) != set(_MEMBER_FIELDS):
            missing = sorted(set(_MEMBER_FIELDS) - set(record))
            extra = sorted(set(record) - set(_MEMBER_FIELDS))
            if missing:
                errors.append(f"{canonical_id}: missing member fields: {', '.join(missing)}")
            if extra:
                errors.append(f"{canonical_id}: unexpected member fields: {', '.join(extra)}")
        manifest_record = manifest_members[canonical_id]
        for field in ("family_id", "source_path", "source_sha256", "expected_outputs", "acceptance_criteria"):
            if field in manifest_record and record.get(field) != manifest_record.get(field):
                errors.append(f"{canonical_id}: {field} differs from frozen manifest")
        try:
            source_path = _safe_relative(record.get("source_path"), label=f"{canonical_id} source_path")
        except ValueError as exc:
            errors.append(str(exc))
            source_path = ""
        source_sha = str(record.get("source_sha256") or "")
        if not _HEX_SHA256.fullmatch(source_sha):
            errors.append(f"{canonical_id}: source_sha256 must be a lowercase SHA256")
        if source_path:
            previous = seen_sources.get(source_path)
            if previous and previous != canonical_id:
                errors.append(f"duplicate source_path {source_path}: {previous}, {canonical_id}")
            seen_sources[source_path] = canonical_id
        references = record.get("references")
        if not isinstance(references, (list, tuple)):
            errors.append(f"{canonical_id}: references must be a sequence")
            references = ()
        manifest_references = manifest_record.get("references", ())
        if not isinstance(manifest_references, Sequence) or isinstance(manifest_references, (str, bytes)):
            errors.append(f"{canonical_id}: manifest references must be a sequence")
            manifest_references = ()
        manifest_refs_by_path = {
            str(reference.get("relative_path")): reference
            for reference in manifest_references
            if isinstance(reference, Mapping) and reference.get("relative_path")
        }
        if len(manifest_refs_by_path) != len(manifest_references):
            errors.append(f"{canonical_id}: manifest references contain duplicate or malformed paths")
        record_reference_paths = {
            str(reference.get("relative_path"))
            for reference in references
            if isinstance(reference, Mapping) and reference.get("relative_path")
        }
        if record_reference_paths != set(manifest_refs_by_path):
            errors.append(f"{canonical_id}: references differ from frozen manifest")
        for reference in references:
            if not isinstance(reference, Mapping):
                errors.append(f"{canonical_id}: reference must be an object")
                continue
            missing = [field for field in _REFERENCE_FIELDS if field not in reference]
            if missing:
                errors.append(f"{canonical_id}: reference missing fields: {', '.join(missing)}")
                continue
            try:
                relative_path = _safe_relative(reference.get("relative_path"), label=f"{canonical_id} reference relative_path")
                ref_source = _safe_relative(reference.get("source_path"), label=f"{canonical_id} reference source_path")
            except ValueError as exc:
                errors.append(str(exc))
                continue
            ref_sha = str(reference.get("source_sha256") or "")
            manifest_reference = manifest_refs_by_path.get(relative_path)
            if manifest_reference is None:
                errors.append(f"{canonical_id}: reference is absent from frozen manifest: {relative_path}")
            else:
                for field in ("source_path", "source_sha256"):
                    if str(reference.get(field) or "") != str(manifest_reference.get(field) or ""):
                        errors.append(f"{canonical_id}: reference {field} differs from frozen manifest for {relative_path}")
            content = reference.get("content")
            if not isinstance(content, str) or not content.strip():
                errors.append(f"{canonical_id}: reference content must be non-empty text")
            elif hashlib.sha256(content.encode("utf-8")).hexdigest() != ref_sha:
                errors.append(f"{canonical_id}: reference content hash mismatch for {relative_path}")
            if not _HEX_SHA256.fullmatch(ref_sha):
                errors.append(f"{canonical_id}: reference source_sha256 must be a lowercase SHA256")
            previous = seen_refs.get(ref_source)
            if previous and previous != canonical_id:
                errors.append(f"duplicate reference source_path {ref_source}: {previous}, {canonical_id}")
            seen_refs[ref_source] = canonical_id
    if members is None and len(records) != len(manifest_members):
        errors.append(f"prepared guidance member count mismatch: {len(records)} != {len(manifest_members)}")
    manifest_count = manifest.get("member_count")
    if manifest_count is not None and manifest_count != len(manifest_members):
        errors.append("prepared guidance manifest member_count is incorrect")
    return errors


def validate_prepared_guidance_catalog(members: object | None = None) -> bool:
    errors = prepared_guidance_errors(members)
    if errors:
        raise ValueError("; ".join(errors))
    return True


def _record_map() -> dict[str, dict[str, Any]]:
    validate_prepared_guidance_catalog()
    return {str(record["canonical_id"]): dict(record) for record in PREPARED_MEMBERS}


def _entry_path(record: Mapping[str, Any]) -> str:
    family_id = _safe_relative(record.get("family_id"), label="family_id")
    canonical_id = _safe_relative(record.get("canonical_id"), label="canonical_id")
    return f"oh-my-jeo/references/prepared/{family_id}/{canonical_id}.md"


def _source_status(record: Mapping[str, Any]) -> str:
    return "source_pinned_prepared_not_observed" if record.get("source_sha256") else "source_unpinned_prepared_not_observed"


def prepared_guidance_index() -> dict[str, object]:
    validate_prepared_guidance_catalog()
    records = _record_map()
    entries = []
    for canonical_id in sorted(records):
        record = records[canonical_id]
        entries.append(
            {
                "canonical_id": canonical_id,
                "family_id": record["family_id"],
                "description": record["description"],
                "reference_path": _entry_path(record),
                "source_status": _source_status(record),
                "source_gaps": list(record["source_gaps"]),
            }
        )
    return {
        "schema_version": PREPARED_INDEX_SCHEMA_VERSION,
        "source_commit": _load_manifest()["source_commit"],
        "member_count": len(entries),
        "family_count": len({entry["family_id"] for entry in entries}),
        "entries": entries,
        "prepared_not_observed": PREPARED_NOT_OBSERVED,
    }


def prepared_guidance_member(canonical_id: str) -> dict[str, object]:
    wanted = str(canonical_id or "").strip()
    if not _SAFE_ID.fullmatch(wanted):
        raise ValueError(f"unknown prepared guidance member: {canonical_id!r}")
    record = _record_map().get(wanted)
    if record is None:
        raise ValueError(f"unknown prepared guidance member: {wanted}")
    output = deepcopy(record)
    output.update(
        {
            "schema_version": PREPARED_MEMBER_SCHEMA_VERSION,
            "reference_path": _entry_path(record),
            "source_status": _source_status(record),
            "prepared_not_observed": PREPARED_NOT_OBSERVED,
        }
    )
    return output


def _contract_markdown(record: Mapping[str, Any]) -> str:
    def bullets(value: object) -> str:
        if isinstance(value, (list, tuple)):
            return "\n".join(f"- {item}" for item in value) or "- None declared"
        return f"- {value}"

    refs = record.get("references", ())
    ref_lines = []
    for reference in refs if isinstance(refs, (list, tuple)) else ():
        if isinstance(reference, Mapping):
            ref_lines.append(f"- `{reference.get('relative_path')}` (pinned `{reference.get('source_path')}`)")
    references = "\n".join(ref_lines) or "- No source-specific method reference is declared; do not invent one."
    gaps = bullets(record.get("source_gaps", ()))
    prerequisites = bullets(record.get("blocked_prerequisites", ()))
    return (
        f"# Prepared guidance: {record['canonical_id']}\n\n"
        f"Family: `{record['family_id']}`  \nCategory: `{record['category']}`  \nPhase: `{record['phase']}`  \nRole: `{record['role']}`\n\n"
        f"## Contract\n{record['description']}\n\n"
        "This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.\n\n"
        f"## Triggers\n{bullets(record['triggers'])}\n\n"
        f"## Required inputs\n{bullets(record['required_inputs'])}\n\n"
        f"## Expected outputs\n{bullets(record['expected_outputs'])}\n\n"
        f"## Artifact expectations\n{bullets(record['artifact_expectations'])}\n\n"
        f"## Acceptance criteria\n{bullets(record['acceptance_criteria'])}\n\n"
        f"## Handoff policy\n{record['handoff_policy']}\n\n"
        f"## Catalog rules\n{bullets(record['catalog_rules'])}\n\n"
        f"## Pinned source\n- Repository: `rlaope/oh-my-hermes`\n- Commit: `{_load_manifest()['source_commit']}`\n- Source path: `{record['source_path']}`\n- SHA256: `{record['source_sha256']}`\n\n"
        f"## Method references\n{references}\n\n"
        f"## Source gaps\n{gaps}\n\n"
        f"## Blocked prerequisites\n{prerequisites}\n\n"
        f"## Evidence boundary\n{record['evidence_boundary']}\n"
    )


def prepared_guidance_reference_templates():
    from .render import SkillReferenceTemplate

    validate_prepared_guidance_catalog()
    records = _record_map()
    templates = []
    seen_source_paths: set[str] = set()
    for canonical_id in sorted(records):
        record = records[canonical_id]
        templates.append(SkillReferenceTemplate("oh-my-jeo", _entry_path(record).split("/", 1)[1], _contract_markdown(record)))
        family = _safe_relative(record["family_id"], label="family_id")
        canonical = _safe_relative(record["canonical_id"], label="canonical_id")
        for reference in record.get("references", ()):
            source_path = _safe_relative(reference["source_path"], label="reference source_path")
            if source_path in seen_source_paths:
                continue
            seen_source_paths.add(source_path)
            relative = _safe_relative(reference["relative_path"], label="reference relative_path")
            templates.append(
                SkillReferenceTemplate(
                    "oh-my-jeo",
                    f"references/prepared/{family}/{canonical}/{relative}",
                    str(reference["content"]),
                )
            )
    return tuple(templates)


__all__ = [
    "PREPARED_MEMBERS",
    "prepared_guidance_errors",
    "prepared_guidance_index",
    "prepared_guidance_member",
    "prepared_guidance_reference_templates",
    "validate_prepared_guidance_catalog",
]
