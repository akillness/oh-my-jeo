"""Read-only pairwise OMJ profile isolation diagnostics.

The report compares only resolved path metadata and selected environment values;
it never opens, writes, or executes a profile.  Unknown is retained when a
Hermes home was omitted or a path could not be resolved.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Mapping

PROFILE_ISOLATION_SCHEMA_VERSION: Final[str] = "profile_isolation/v1"
VERDICT_ISOLATED: Final[str] = "isolated"
VERDICT_LEAKED: Final[str] = "leaked"
VERDICT_UNKNOWN: Final[str] = "unknown"
PROFILE_ISOLATION_VERDICTS: Final[tuple[str, ...]] = (VERDICT_ISOLATED, VERDICT_LEAKED, VERDICT_UNKNOWN)

SURFACE_CONFIG: Final[str] = "config"
SURFACE_CACHE: Final[str] = "cache"
SURFACE_PLUGIN_STATE: Final[str] = "plugin_state"
SURFACE_FILES: Final[str] = "files"
SURFACE_ENV: Final[str] = "env"
PROFILE_ISOLATION_SURFACES: Final[tuple[str, ...]] = (
    SURFACE_CONFIG,
    SURFACE_CACHE,
    SURFACE_PLUGIN_STATE,
    SURFACE_FILES,
    SURFACE_ENV,
)

REASON_DISTINCT_PATHS: Final[str] = "distinct_paths"
REASON_SAME_PATH: Final[str] = "same_resolved_path"
REASON_NESTED_PATH: Final[str] = "one_path_contains_the_other"
REASON_HOME_NOT_SUPPLIED: Final[str] = "home_not_supplied"
REASON_PATH_UNRESOLVABLE: Final[str] = "path_could_not_be_resolved"
REASON_ENV_UNSET: Final[str] = "environment_variable_unset"
REASON_ENV_PINS_PROFILE: Final[str] = "environment_variable_pins_one_profile"
REASON_ENV_PINS_NEITHER: Final[str] = "environment_variable_pins_neither_profile"

REASON_TEXT: Final[dict[str, str]] = {
    REASON_DISTINCT_PATHS: "The two profiles resolve this artifact to different paths, neither inside the other.",
    REASON_SAME_PATH: "Both profiles resolve this artifact to one path, so either can observe and overwrite the other's.",
    REASON_NESTED_PATH: "One profile's path lies inside the other's tree, so writes under the inner one land inside the outer profile.",
    REASON_HOME_NOT_SUPPLIED: "This artifact lives under a Hermes home, and at least one profile supplied none; it was not inspected.",
    REASON_PATH_UNRESOLVABLE: "The path could not be resolved, so the two paths could not be compared.",
    REASON_ENV_UNSET: "The variable is unset in the inspected environment, so it pins neither profile.",
    REASON_ENV_PINS_PROFILE: "The variable pins one of these profiles for invocations that do not override it.",
    REASON_ENV_PINS_NEITHER: "The variable is set to a home that is neither of these two profiles.",
}

PROFILE_ISOLATION_CLAIM_BOUNDARY: Final[str] = (
    "An isolation report compares resolved OMJ/Hermes paths and environment metadata only; "
    "nothing was opened, written, or executed, and no invocation was observed under either profile. "
    "An isolated surface covers only its named artifacts; unknown was not inspected."
)

_OMJ: Final[str] = "omj_home"
_HERMES: Final[str] = "hermes_home"
_SURFACE_ARTIFACTS: Final[dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]]] = {
    SURFACE_CONFIG: (
        ("setup_profile", _OMJ, ("setup-profile.json",)),
        ("runtime_state", _OMJ, ("runtime", "state.json")),
        ("hermes_config", _HERMES, ("config.yaml",)),
    ),
    SURFACE_CACHE: (
        ("runtime_runs", _OMJ, ("runtime", "runs")),
        ("runtime_spills", _OMJ, ("runtime", "output-spills")),
    ),
    SURFACE_PLUGIN_STATE: (
        ("plugin_host_observations", _OMJ, ("runtime", "plugin_host_observations.jsonl")),
        ("installed_plugin_bundle", _HERMES, ("plugins", "omj")),
    ),
    SURFACE_FILES: (
        ("managed_skills", _OMJ, ("skills",)),
        ("install_manifest", _OMJ, ("manifest.json",)),
        ("memory_records", _OMJ, ("memory",)),
    ),
}
_ENV_VARIABLES: Final[tuple[tuple[str, str], ...]] = (("OMJ_HOME", _OMJ), ("HERMES_HOME", _HERMES))


@dataclass(frozen=True)
class ProfileRef:
    ref: str
    omj_home: Path
    hermes_home: Path | None


def parse_profile_ref(text: str) -> ProfileRef:
    raw = str(text or "").strip()
    if not raw:
        raise ValueError("a profile reference needs an OMJ home path")
    omj_text, separator, hermes_text = raw.partition(",")
    omj_text, hermes_text = omj_text.strip(), hermes_text.strip()
    if not omj_text:
        raise ValueError(f"profile reference {raw!r} names no OMJ home")
    if separator and not hermes_text:
        raise ValueError(f"profile reference {raw!r} ends in a comma but names no Hermes home")
    return ProfileRef(raw, Path(omj_text).expanduser(), Path(hermes_text).expanduser() if hermes_text else None)


def compare_profile_isolation(
    first: ProfileRef,
    second: ProfileRef,
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    environment = dict(os.environ if env is None else env)
    surfaces = [_path_surface(surface, first, second) for surface in PROFILE_ISOLATION_SURFACES if surface in _SURFACE_ARTIFACTS]
    surfaces.append(_env_surface(first, second, environment))
    counts = {verdict: 0 for verdict in PROFILE_ISOLATION_VERDICTS}
    for surface in surfaces:
        counts[str(surface["verdict"])] += 1
    return {
        "schema_version": PROFILE_ISOLATION_SCHEMA_VERSION,
        "profiles": [_profile_row(first), _profile_row(second)],
        "surfaces": surfaces,
        "leaked_surfaces": [str(row["surface"]) for row in surfaces if row["verdict"] == VERDICT_LEAKED],
        "unknown_surfaces": [str(row["surface"]) for row in surfaces if row["verdict"] == VERDICT_UNKNOWN],
        "summary": {"surfaces": len(surfaces), "isolated": counts[VERDICT_ISOLATED], "leaked": counts[VERDICT_LEAKED], "unknown": counts[VERDICT_UNKNOWN]},
        "reason_codes": dict(REASON_TEXT),
        "claim_boundary": PROFILE_ISOLATION_CLAIM_BOUNDARY,
        "read_only": True,
    }


def _profile_row(profile: ProfileRef) -> dict[str, Any]:
    return {"ref": profile.ref, "omj_home": str(profile.omj_home), "hermes_home": str(profile.hermes_home) if profile.hermes_home is not None else ""}


def _path_surface(surface: str, first: ProfileRef, second: ProfileRef) -> dict[str, Any]:
    artifacts = _SURFACE_ARTIFACTS[surface]
    roots = [home for home in (_OMJ, _HERMES) if any(entry[1] == home for entry in artifacts)]
    findings = [_compare_artifact(home, home, (), first, second) for home in roots]
    findings.extend(_compare_artifact(name, home, segments, first, second) for name, home, segments in artifacts)
    return {"surface": surface, "verdict": _roll_up([str(row["verdict"]) for row in findings]), "findings": findings}


def _compare_artifact(name: str, home: str, segments: tuple[str, ...], first: ProfileRef, second: ProfileRef) -> dict[str, Any]:
    left, right = _artifact_path(first, home, segments), _artifact_path(second, home, segments)
    if left is None or right is None:
        return _finding(name, VERDICT_UNKNOWN, REASON_HOME_NOT_SUPPLIED, left, right)
    try:
        left_resolved, right_resolved = left.resolve(), right.resolve()
    except (OSError, RuntimeError, ValueError):
        return _finding(name, VERDICT_UNKNOWN, REASON_PATH_UNRESOLVABLE, left, right)
    if left_resolved == right_resolved:
        return _finding(name, VERDICT_LEAKED, REASON_SAME_PATH, left, right, shared_path=str(left_resolved))
    containing = _containing_path(left_resolved, right_resolved)
    if containing is not None:
        return _finding(name, VERDICT_LEAKED, REASON_NESTED_PATH, left, right, shared_path=str(containing))
    return _finding(name, VERDICT_ISOLATED, REASON_DISTINCT_PATHS, left, right)


def _artifact_path(profile: ProfileRef, home: str, segments: tuple[str, ...]) -> Path | None:
    root = profile.omj_home if home == _OMJ else profile.hermes_home
    return None if root is None else root.joinpath(*segments)


def _containing_path(left: Path, right: Path) -> Path | None:
    if left in right.parents:
        return left
    if right in left.parents:
        return right
    return None


def _env_surface(first: ProfileRef, second: ProfileRef, environment: Mapping[str, str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for variable, home in _ENV_VARIABLES:
        raw = str(environment.get(variable, "") or "").strip()
        if not raw:
            findings.append(_env_finding(variable, VERDICT_ISOLATED, REASON_ENV_UNSET, ""))
            continue
        try:
            pinned = Path(raw).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            findings.append(_env_finding(variable, VERDICT_UNKNOWN, REASON_PATH_UNRESOLVABLE, raw))
            continue
        pins = [profile.ref for profile in (first, second) if _env_pins(pinned, _artifact_path(profile, home, ()))]
        findings.append(_env_finding(variable, VERDICT_LEAKED if pins else VERDICT_ISOLATED, REASON_ENV_PINS_PROFILE if pins else REASON_ENV_PINS_NEITHER, raw, pins=pins))
    return {"surface": SURFACE_ENV, "verdict": _roll_up([str(row["verdict"]) for row in findings]), "findings": findings}


def _env_pins(pinned: Path, home: Path | None) -> bool:
    if home is None:
        return False
    try:
        resolved = home.resolve()
    except (OSError, RuntimeError, ValueError):
        return False
    return pinned == resolved or resolved in pinned.parents


def _finding(artifact: str, verdict: str, reason: str, left: Path | None, right: Path | None, *, shared_path: str = "") -> dict[str, Any]:
    return {"artifact": artifact, "verdict": verdict, "reason": reason, "reason_text": REASON_TEXT[reason], "path_a": str(left) if left is not None else "", "path_b": str(right) if right is not None else "", "shared_path": shared_path}


def _env_finding(variable: str, verdict: str, reason: str, value: str, *, pins: list[str] | None = None) -> dict[str, Any]:
    return {"artifact": variable, "verdict": verdict, "reason": reason, "reason_text": REASON_TEXT[reason], "value": value, "pins": list(pins or [])}


def _roll_up(verdicts: list[str]) -> str:
    if VERDICT_LEAKED in verdicts:
        return VERDICT_LEAKED
    if VERDICT_UNKNOWN in verdicts or not verdicts:
        return VERDICT_UNKNOWN
    return VERDICT_ISOLATED


__all__ = [
    "PROFILE_ISOLATION_CLAIM_BOUNDARY", "PROFILE_ISOLATION_SCHEMA_VERSION", "PROFILE_ISOLATION_SURFACES", "PROFILE_ISOLATION_VERDICTS",
    "ProfileRef", "VERDICT_ISOLATED", "VERDICT_LEAKED", "VERDICT_UNKNOWN", "compare_profile_isolation", "parse_profile_ref",
]
