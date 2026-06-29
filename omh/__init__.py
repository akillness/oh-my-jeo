"""omh — deprecated backward-compatibility alias for the oh-my-jeo ``omj`` package.

The canonical brand and implementation namespace is now ``omj`` (oh-my-jeo).
``omh`` survives only as a thin alias so that legacy ``import omh`` /
``from omh.routing import ...`` call sites keep working.  Every ``omh`` and
``omh.<submodule>`` name resolves to the *same module object* as its ``omj``
counterpart (object identity, not a copy), via an import hook installed below.

Prefer ``omj`` in new code; ``omh`` may be removed in a future release.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import sys

_PREFIX = "omh"
_TARGET = "omj"


class _OmhAliasLoader(importlib.abc.Loader):
    """Load an ``omh.*`` name by returning the matching ``omj.*`` module."""

    # Import attributes the import machinery rewrites via
    # ``_init_module_attrs(override=True)`` between ``create_module`` and
    # ``exec_module``.  Because an ``omh.*`` name aliases the *same* object as
    # its ``omj.*`` counterpart, that rewrite would otherwise clobber the
    # canonical ``omj`` metadata (``__name__``/``__spec__``/``__loader__``),
    # which breaks ``importlib.resources`` and ``__name__``-based introspection
    # on ``omj.*`` (e.g. the packaged Hermes plugin bundle).
    _CANONICAL_ATTRS = ("__name__", "__loader__", "__package__", "__spec__", "__path__", "__file__")

    def create_module(self, spec: importlib.machinery.ModuleSpec):
        target_name = _TARGET + spec.name[len(_PREFIX):]
        module = importlib.import_module(target_name)
        self._canonical = {
            attr: getattr(module, attr) for attr in self._CANONICAL_ATTRS if hasattr(module, attr)
        }
        sys.modules[spec.name] = module
        return module

    def exec_module(self, module) -> None:
        for attr, value in getattr(self, "_canonical", {}).items():
            setattr(module, attr, value)


class _OmhAliasFinder(importlib.abc.MetaPathFinder):
    """Resolve ``omh.<anything>`` to the ``omj`` implementation."""

    def find_spec(self, fullname, path=None, target=None):
        # ``omh`` itself is this real on-disk alias package; never alias the root.
        if not fullname.startswith(_PREFIX + "."):
            return None
        return importlib.machinery.ModuleSpec(fullname, _OmhAliasLoader())


def _install() -> None:
    if not any(isinstance(finder, _OmhAliasFinder) for finder in sys.meta_path):
        # Must precede the path-based finder so ``omh.wrapper.contract`` keeps
        # object identity with ``omj.wrapper.contract`` instead of being loaded
        # a second time off ``src/wrapper``.
        sys.meta_path.insert(0, _OmhAliasFinder())


_install()

# Re-export the canonical implementation's version so ``import omh`` behaves
# like ``import omj`` for top-level attribute access too.
import omj as _omj  # noqa: E402

__version__ = _omj.__version__
