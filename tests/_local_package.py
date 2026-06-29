from __future__ import annotations

import importlib.util
from importlib.machinery import ModuleSpec
import sys
from types import ModuleType
from pathlib import Path


def load_local_package() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src"

    if "omj" not in sys.modules:
        package_dir = source_root / "omj"
        module = ModuleType("omj")
        module.__file__ = str(package_dir)
        module.__package__ = "omj"
        module.__path__ = [str(package_dir), str(source_root)]  # type: ignore[attr-defined]
        module.__spec__ = ModuleSpec("omj", loader=None, is_package=True)
        sys.modules["omj"] = module

        from omj.version import __version__

        module.__version__ = __version__

    _load_omj_alias(source_root)


def _load_omj_alias(source_root: Path) -> None:
    """Register the shipped ``omj`` brand namespace (aliases ``omj``).

    The on-disk ``src/omj/__init__.py`` is the single source of truth for the
    alias finder, so we execute it directly instead of re-implementing it here.
    """

    if "omj" in sys.modules:
        return

    omj_init = source_root / "omj" / "__init__.py"
    spec = importlib.util.spec_from_file_location("omj", omj_init)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load omj package from {omj_init}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["omj"] = module
    spec.loader.exec_module(module)
