from __future__ import annotations

from pathlib import Path

_SOURCE_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "omj"
_SOURCE_ROOT = _SOURCE_PACKAGE.parent

# Source checkouts expose src/omj/ as the compatibility package and the
# readable implementation folders directly under src/ as omj subpackages.
__path__ = [str(_SOURCE_PACKAGE), str(_SOURCE_ROOT)]

from .version import __version__
