from __future__ import annotations

from typing import Any

from ..version import __version__
from ..paths import OmjPaths
from ..plugin_bundle.omj.runtime_reader import read_omj_hud


def build_hud_payload(
    paths: OmjPaths,
    *,
    preset: str = "focused",
    limit: int = 3,
    token_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return read_omj_hud(
        omj_home=paths.omj_home,
        hermes_home=paths.hermes_home,
        preset=preset,
        limit=limit,
        token_metadata=token_metadata or {},
        package_version=__version__,
    )
