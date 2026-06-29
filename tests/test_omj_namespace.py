"""Real-verification tests for the completed ``omh`` -> ``omj`` rename.

``omj`` (oh-my-jeo) is the single canonical brand, implementation, CLI, runtime
home, env, plugin-bundle, and ABI identity.  The previously shipped ``omh``
backward-compatibility alias (import package and console script) has been
**removed** — the project is now ``omj`` only.  ``oh-my-hermes`` survives solely
as upstream license/provenance attribution in ``NOTICE``/``LICENSE``/``README``
because oh-my-jeo is an MIT derivative of oh-my-hermes; it is no longer a live
import name, console script, ABI token, or chat cue.

These tests pin both halves of that contract:
  * the ``omh`` import namespace and console script no longer exist;
  * every live ABI/packaging/chat surface reads ``omj`` and only ``omj``.
"""

from __future__ import annotations

import importlib
import sys
import tomllib
import unittest
from pathlib import Path

from _local_package import load_local_package

load_local_package()


class OmhAliasIsFullyRemovedTests(unittest.TestCase):
    def test_omh_top_level_import_is_gone(self) -> None:
        sys.modules.pop("omh", None)
        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module("omh")

    def test_omh_submodule_imports_are_gone(self) -> None:
        for name in ("omh.routing", "omh.wrapper.contract", "omh.commands.main"):
            sys.modules.pop(name, None)
            with self.subTest(name=name):
                with self.assertRaises(ModuleNotFoundError):
                    importlib.import_module(name)

    def test_omh_package_directories_do_not_exist(self) -> None:
        self.assertFalse(Path("omh").exists())
        self.assertFalse(Path("src/omh").exists())

    def test_omj_canonical_imports_still_resolve(self) -> None:
        import omj
        import omj.routing
        import omj.wrapper.contract
        from omj.commands.main import main as omj_main
        from omj.routing.recommend import recommend_skills

        self.assertTrue(omj.__version__)
        self.assertEqual(omj.wrapper.contract.__name__, "omj.wrapper.contract")
        self.assertTrue(callable(omj_main))
        self.assertTrue(callable(recommend_skills))

    def test_packaged_plugin_bundle_resources_resolve(self) -> None:
        from importlib import resources

        bundle = resources.files("omj.plugin_bundle.omj")
        self.assertTrue((bundle / "plugin.yaml").is_file())


class OmjPackagingIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pyproject = tomllib.loads(
            Path("pyproject.toml").read_text(encoding="utf-8")
        )
        self.project = self.pyproject["project"]

    def test_distribution_is_rebranded(self) -> None:
        self.assertEqual(self.project["name"], "oh-my-jeo")
        self.assertNotIn("oh-my-hermes", self.project["name"])

    def test_repository_url_points_at_oh_my_jeo(self) -> None:
        urls = self.project["urls"]
        self.assertEqual(urls["Repository"], "https://github.com/akillness/oh-my-jeo")
        for value in urls.values():
            self.assertNotIn("rlaope/oh-my-hermes", value)

    def test_only_omj_console_script_is_shipped(self) -> None:
        scripts = self.project["scripts"]
        self.assertEqual(scripts.get("omj"), "omj.cli:main")
        self.assertNotIn("omh", scripts)
        module_name, _, attr = scripts["omj"].partition(":")
        module = __import__(module_name, fromlist=[attr])
        self.assertTrue(callable(getattr(module, attr)))

    def test_setuptools_packaging_drops_the_omh_alias(self) -> None:
        tool = self.pyproject["tool"]["setuptools"]
        self.assertNotIn("omh", tool["packages"])
        self.assertIn("omj", tool["packages"])
        self.assertNotIn("omh", tool["package-dir"])
        self.assertEqual(tool["package-dir"]["omj"], "src/omj")


class OmjRenameIsCompleteTests(unittest.TestCase):
    """Pin the *completed, omj-only* rename across live ABI/chat surfaces."""

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
        for tool in PROVIDED_TOOLS:
            self.assertFalse(tool.startswith("omh_"), tool)

        bundle = resources.files("omj.plugin_bundle.omj")
        self.assertTrue((bundle / "plugin.yaml").is_file())
        manifest = (bundle / "plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("name: omj", manifest)
        self.assertNotIn("name: omh", manifest)
        for tool in PROVIDED_TOOLS:
            self.assertIn(f"  - {tool}", manifest)

    def test_chat_self_reference_is_omj_only(self) -> None:
        from omj.routing import intent

        match = intent._matched_omj_system_target_cues
        # ``omj`` is the canonical token and never duplicates.
        self.assertEqual(match("why did omj route this"), ("omj",))
        self.assertEqual(match("please improve omj routing"), ("omj",))
        # The canonical long-form brand resolves to itself.
        self.assertEqual(match("evaluate oh-my-jeo quality"), ("oh-my-jeo",))
        self.assertEqual(match("evaluate oh my jeo quality"), ("oh my jeo",))
        # A request naming the brand twice is not double-counted.
        self.assertEqual(match("does omj or oh-my-jeo own this"), ("omj", "oh-my-jeo"))
        # The retired ``omh`` / ``oh-my-hermes`` brand is no longer a live cue.
        self.assertEqual(match("why did omh route this"), ())
        self.assertEqual(match("evaluate oh-my-hermes quality"), ())
        # Unrelated requests are not mis-claimed as system-target.
        self.assertEqual(match("build a web app for invoices"), ())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
