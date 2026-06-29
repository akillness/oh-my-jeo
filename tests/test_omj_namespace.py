"""Real-verification tests for the completed ``omh`` -> ``omj`` rename.

``omj`` (oh-my-jeo) is now the canonical brand, implementation, CLI, runtime
home, env, plugin-bundle, and ABI identity.  ``omh`` survives only as a thin
*deprecated* backward-compatibility alias whose every name resolves to the
*same* module object as its ``omj`` counterpart — not a duplicate copy of
runtime state and not a dangling console-script alias.

These tests pin both halves of that contract:
  * ``omh.<x>`` IS ``omj.<x>`` (object identity, single runtime singleton);
  * the live ABI/packaging/chat surfaces all read ``omj``.
See ``.ouroboros/seeds/full-rename-seed.yaml``.
"""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from _local_package import load_local_package

load_local_package()


class OmjIsCanonicalOmhIsAliasTests(unittest.TestCase):
    def test_top_level_import_exposes_shared_version(self) -> None:
        import omh
        import omj

        # Same version string, sourced from the canonical implementation.
        self.assertEqual(omh.__version__, omj.__version__)

    def test_submodules_resolve_to_the_same_objects(self) -> None:
        import omh.routing
        import omh.wrapper.contract
        import omj.routing
        import omj.wrapper.contract

        # Shallow submodule identity through the alias.
        self.assertIs(omh.routing, omj.routing)
        # Deep submodule identity — guards against the PathFinder re-loading a
        # second copy of ``contract`` via the aliased parent's ``__path__``.
        self.assertIs(omh.wrapper.contract, omj.wrapper.contract)

    def test_from_import_yields_one_canonical_callable(self) -> None:
        from omh.commands.main import main as omh_main
        from omj.commands.main import main as omj_main
        from omj.routing.recommend import recommend_skills

        self.assertIs(omh_main, omj_main)
        self.assertTrue(callable(recommend_skills))

    def test_runtime_singletons_are_not_forked(self) -> None:
        # Importing through either brand must register exactly one module under
        # the canonical ``omj`` name, so module-level state stays a singleton.
        import sys

        import omh.runtime.records as via_omh
        import omj.runtime.records as via_omj

        self.assertIs(via_omh, via_omj)
        self.assertIs(sys.modules["omj.runtime.records"], via_omj)


class OmjAliasPreservesCanonicalMetadataTests(unittest.TestCase):
    """Aliasing must not corrupt the shared ``omj.*`` import metadata.

    Because ``omh.<sub>`` is the *same object* as ``omj.<sub>``, the import
    machinery's ``_init_module_attrs(override=True)`` pass would otherwise
    overwrite the canonical ``__name__``/``__spec__``/``__loader__`` with the
    alias values, silently breaking ``importlib.resources`` and name-based
    introspection on ``omj.*``.  These tests pin the repair.
    """

    def test_importing_via_omh_keeps_canonical_name_and_loader(self) -> None:
        import omh.wrapper.contract  # noqa: F401  (triggers the alias path)
        import omj.wrapper.contract

        self.assertEqual(omj.wrapper.contract.__name__, "omj.wrapper.contract")
        self.assertIsNotNone(omj.wrapper.contract.__spec__)
        self.assertEqual(omj.wrapper.contract.__spec__.name, "omj.wrapper.contract")
        # The loader must remain a real source loader, not the alias shim, or
        # resource lookups degrade to the empty CompatibilityFiles adapter.
        loader_name = type(omj.wrapper.contract.__spec__.loader).__name__
        self.assertNotIn("OmhAlias", loader_name)

    def test_packaged_plugin_bundle_resources_resolve_after_omh_import(self) -> None:
        from importlib import resources

        import omh.plugin_bundle.omj.metadata  # noqa: F401  (triggers the alias path)

        bundle = resources.files("omj.plugin_bundle.omj")
        # A working traversable resolves the real packaged file; the degraded
        # adapter raises FileNotFoundError on ``is_file()``.
        self.assertTrue((bundle / "plugin.yaml").is_file())


class OmjPackagingIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = tomllib.loads(
            Path("pyproject.toml").read_text(encoding="utf-8")
        )["project"]

    def test_distribution_is_rebranded(self) -> None:
        self.assertEqual(self.project["name"], "oh-my-jeo")
        self.assertNotIn("oh-my-hermes", self.project["name"])

    def test_repository_url_points_at_oh_my_jeo(self) -> None:
        urls = self.project["urls"]
        self.assertEqual(urls["Repository"], "https://github.com/akillness/oh-my-jeo")
        for value in urls.values():
            self.assertNotIn("rlaope/oh-my-hermes", value)

    def test_both_brand_console_scripts_resolve_to_real_callables(self) -> None:
        scripts = self.project["scripts"]
        # The canonical ``omj`` plus the deprecated ``omh`` alias are both shipped.
        self.assertIn("omj", scripts)
        self.assertIn("omh", scripts)
        self.assertEqual(scripts["omj"], "omj.cli:main")
        self.assertEqual(scripts["omh"], "omj.cli:main")
        for target in {scripts["omj"], scripts["omh"]}:
            module_name, _, attr = target.partition(":")
            module = __import__(module_name, fromlist=[attr])
            self.assertTrue(callable(getattr(module, attr)), target)


class OmjRenameIsCompleteTests(unittest.TestCase):
    """Pin the *completed* rename: the live ABI/chat surfaces read ``omj``.

    The earlier Stage-4 freeze deliberately kept the ABI on ``omh``; the user
    later approved finishing the rename, so these tests now assert the opposite
    invariant — every advertised tool, the bundle name, and the canonical
    self-reference token are ``omj``, while ``omh`` is only a synonym for
    legacy chat input.  See ``.ouroboros/seeds/full-rename-seed.yaml``.
    """

    def test_hermes_plugin_abi_uses_the_omj_token(self) -> None:
        from importlib import resources

        from omj.plugin_bundle.omj.metadata import PROVIDED_TOOLS

        self.assertEqual(
            PROVIDED_TOOLS,
            (
                "omj_capabilities",
                "omj_context",
                "omj_gather_evidence",
                "omj_hud",
                "omj_interact",
                "omj_probe",
                "omj_recommend",
                "omj_role",
                "omj_status",
            ),
        )
        # No tool may carry the retired ``omh_`` ABI prefix.
        for tool in PROVIDED_TOOLS:
            self.assertFalse(tool.startswith("omh_"), tool)

        bundle = resources.files("omj.plugin_bundle.omj")
        self.assertTrue((bundle / "plugin.yaml").is_file())
        manifest = (bundle / "plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("name: omj", manifest)
        self.assertNotIn("name: omh", manifest)
        for tool in PROVIDED_TOOLS:
            self.assertIn(f"  - {tool}", manifest)

    def test_chat_self_reference_is_omj_with_omh_kept_as_synonym(self) -> None:
        from omj.routing import intent

        match = intent._matched_omj_system_target_cues
        # ``omj`` is the canonical token and never duplicates.
        self.assertEqual(match("why did omj route this"), ("omj",))
        self.assertEqual(match("please improve omj routing"), ("omj",))
        # The deprecated ``omh`` name still resolves to the canonical token.
        self.assertEqual(match("why did omh route this"), ("omj",))
        # A request naming both brands is not double-counted.
        self.assertEqual(match("does omj or omh own this"), ("omj",))
        # Legacy/long-form brand spellings stay recognized.
        self.assertIn("oh-my-hermes", match("evaluate oh-my-hermes quality"))
        self.assertIn("oh-my-jeo", match("evaluate oh-my-jeo quality"))
        # Unrelated requests are not mis-claimed as system-target.
        self.assertEqual(match("build a web app for invoices"), ())

    def test_internal_namespace_is_importable_via_both_brands(self) -> None:
        import omh.plugin_bundle.omj.metadata as via_omh
        import omj.plugin_bundle.omj.metadata as via_omj

        self.assertIs(via_omh, via_omj)
        self.assertEqual(via_omj.__name__, "omj.plugin_bundle.omj.metadata")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
