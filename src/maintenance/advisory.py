"""Exit-neutral, read-only OMJ configuration advisories.

Advisories describe local evidence only.  They do not mutate stores, probe a
provider, invoke Hermes, or turn an absent/unreadable source into a healthy
result.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..commands.providers import (
    _UNPINNED_PROVIDER_MARKERS,
    _base_url_host,
    _model_family,
    _model_config_values,
    _read_model_source,
    _routing_disagreements,
    _safe_model_ref,
)
from ..local_store import read_json_object_result
from ..paths import OmjPaths
from ..workflows.research_department import RESEARCH_DEPARTMENT_PLAN_SCHEMA_VERSION

CONTRACT = "omj_config_advice/v1"


@dataclass(frozen=True)
class AdviceEntry:
    check_id: str
    status: str
    remediation: str
    evidence_boundary: str
    observed: str
    read_only: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "severity": "info" if self.status == "ok" else "warning",
            "read_only": self.read_only,
            "remediation": self.remediation,
            "evidence_boundary": self.evidence_boundary,
            "observed": self.observed,
        }


@dataclass(frozen=True)
class AdvisoryReport:
    contract: str = CONTRACT
    entries: list[AdviceEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"contract": self.contract, "entries": [entry.to_dict() for entry in self.entries]}


def run_config_advisories(
    hermes_home: str | Path | None = None,
    *,
    omj_home: str | Path | None = None,
    discovery_home: str | Path | None = None,
) -> AdvisoryReport:
    """Inspect the selected local OMJ/Hermes paths without side effects."""
    hermes = Path(hermes_home).expanduser() if hermes_home is not None else Path.home() / ".hermes"
    omj = Path(omj_home).expanduser() if omj_home is not None else hermes.parent / ".omj"
    paths = OmjPaths(omj_home=omj, hermes_home=hermes)
    return AdvisoryReport(
        entries=[
            check_model_config(paths.hermes_config_path),
            check_local_plan_store(paths),
            check_local_store(paths),
        ]
    )


def check_model_config(config_path: Path) -> AdviceEntry:
    boundary = (
        "Local Hermes config metadata only; no provider, credential, network, model dispatch, "
        "or runtime-load claim."
    )
    source, text = _read_model_source(config_path)
    scalars: dict[str, str] = {}
    if text:
        try:
            scalars, _aliases = _model_config_values(text)
        except ValueError:
            source = {**source, "readable": False, "status": "unreadable"}
    source_status = str(source.get("status", ""))
    if source_status == "absent":
        return AdviceEntry(
            "model_config",
            "unobserved",
            "Create or select a Hermes config before asking OMJ to inspect model settings.",
            boundary,
            f"config absent: {config_path}",
        )
    if not bool(source.get("readable")):
        return AdviceEntry(
            "model_config",
            "unobserved",
            "Repair or replace the unreadable local Hermes config, then rerun doctor.",
            boundary,
            f"config unreadable: {config_path}",
        )

    default = _safe_model_ref(scalars.get("default", ""))
    provider = _safe_model_ref(scalars.get("provider", "")).casefold()
    base_url_host = _base_url_host(str(scalars.get("base_url", "")))
    if not default or not provider or provider in _UNPINNED_PROVIDER_MARKERS:
        return AdviceEntry(
            "model_config",
            "advice",
            "Pin the intended provider/default in the Hermes-owned config only when that choice is intentional; OMJ will not write it.",
            boundary,
            f"config observed; default={default or 'unset'}, provider={provider or 'unset'}, base_url={base_url_host or 'unset'}",
        )
    disagreements = _routing_disagreements(scalars)
    if disagreements:
        return AdviceEntry(
            "model_config",
            "advice",
            "Review the local model/base URL disagreement in the Hermes-owned config; OMJ reports it but does not activate or repair providers.",
            boundary,
            f"local routing disagreement; default_family={_model_family(default) or 'unset'}, base_url={base_url_host or 'unset'}",
        )
    return AdviceEntry(
        "model_config",
        "ok",
        "No local model selection disagreement observed.",
        boundary,
        f"config observed; default={default}, provider={provider}, base_url={base_url_host or 'unset'}",
    )


def check_local_plan_store(omj_home: Path | OmjPaths) -> AdviceEntry:
    boundary = "Local OMJ research-department plan files only; presence is not source retrieval, scheduling, execution, or delivery evidence."
    paths = _coerce_paths(omj_home)
    path = paths.research_department_plans_dir
    if not path.exists():
        return AdviceEntry("local_plan_store", "unobserved", "No local OMJ plan store is present; create one through the owning OMJ command if needed.", boundary, f"plan store absent: {path}")
    if not path.is_dir():
        return AdviceEntry("local_plan_store", "unobserved", "Repair the local OMJ plan-store path; it is not a directory.", boundary, f"plan store not a directory: {path}")
    try:
        files = sorted(item for item in path.iterdir() if item.is_file())
    except OSError:
        return AdviceEntry("local_plan_store", "unobserved", "Repair permissions or path access before relying on plan-store health.", boundary, f"plan store unreadable: {path}")
    if not files:
        return AdviceEntry("local_plan_store", "ok", "No local OMJ plans are currently stored.", boundary, f"plan store observed and unset: {path}")
    invalid = []
    for item in files:
        record, error = read_json_object_result(item)
        if error or record is None or record.get("schema_version") != RESEARCH_DEPARTMENT_PLAN_SCHEMA_VERSION:
            invalid.append(item.name)
    if invalid:
        return AdviceEntry("local_plan_store", "unobserved", "Repair unreadable or unsupported local OMJ plan files before relying on the plan store.", boundary, f"plan store invalid files: {', '.join(invalid[:5])}")
    return AdviceEntry("local_plan_store", "ok", "Local OMJ plan files are readable.", boundary, f"{len(files)} local plan file(s) observed")


def check_local_store(omj_home: Path | OmjPaths) -> AdviceEntry:
    boundary = "Local OMJ metadata store only; this does not prove memory admission, recall quality, Hermes-native storage, or provider execution."
    from ..workflows.memory import MEMORY_INDEX_SCHEMA_VERSION
    paths = _coerce_paths(omj_home)
    path = paths.memory_dir
    if not path.exists():
        return AdviceEntry("local_store", "unobserved", "No local OMJ store is present; initialize it through the owning OMJ memory command if needed.", boundary, f"store absent: {path}")
    if not path.is_dir():
        return AdviceEntry("local_store", "unobserved", "Repair the local OMJ store path; it is not a directory.", boundary, f"store not a directory: {path}")
    index = paths.memory_index_path
    if not index.exists():
        return AdviceEntry("local_store", "advice", "The local OMJ store exists without an index; run the owning memory/status command to inspect it.", boundary, f"store observed but index unset: {path}")
    state, error = read_json_object_result(index)
    if error or state is None:
        return AdviceEntry("local_store", "unobserved", "Repair unreadable local OMJ store metadata before relying on store health.", boundary, f"store index unreadable: {index}")
    if state.get("schema_version") != MEMORY_INDEX_SCHEMA_VERSION:
        return AdviceEntry("local_store", "unobserved", "Repair the unsupported local OMJ store index before relying on store health.", boundary, f"store index schema unsupported: {index}")
    return AdviceEntry("local_store", "ok", "Local OMJ store metadata is readable.", boundary, f"store observed: {index}")


def _coerce_paths(value: Path | OmjPaths) -> OmjPaths:
    if isinstance(value, OmjPaths):
        return value
    omj_home = Path(value).expanduser()
    return OmjPaths(omj_home=omj_home, hermes_home=omj_home.parent / ".hermes")


__all__ = ["AdviceEntry", "AdvisoryReport", "CONTRACT", "run_config_advisories", "check_model_config", "check_local_plan_store", "check_local_store"]
