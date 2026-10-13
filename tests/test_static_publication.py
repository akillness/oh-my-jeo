from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import unquote, urlsplit


REPO = Path(__file__).resolve().parents[1]
SITE = REPO / "site"
CANONICAL_ICON = REPO / "assets" / "oh-my-jeo-icon.png"
WORKFLOWS = REPO / ".github" / "workflows"
CANONICAL_SOCIAL_IMAGE = "https://akillness.github.io/oh-my-jeo/assets/oh-my-jeo-icon.png"


class _StaticMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[dict[str, str]] = []
        self.icons: list[dict[str, str]] = []
        self.metadata: dict[str, list[str]] = {}
        self.anchors: list[dict[str, object]] = []
        self._anchor_stack: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "a":
            anchor: dict[str, object] = {"attrs": attributes, "images": []}
            self._anchor_stack.append(anchor)
        elif tag == "img":
            self.images.append(attributes)
            if self._anchor_stack:
                images = self._anchor_stack[-1]["images"]
                assert isinstance(images, list)
                images.append(attributes)
        elif tag == "link" and "icon" in attributes.get("rel", "").split():
            self.icons.append(attributes)
        elif tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.metadata.setdefault(key, []).append(attributes.get("content", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor_stack:
            self.anchors.append(self._anchor_stack.pop())


def _static_pages() -> list[Path]:
    return [SITE / "index.html", SITE / "docs" / "index.html", *sorted((SITE / "docs").glob("*/index.html"))]


def _parse(path: Path) -> _StaticMarkupParser:
    parser = _StaticMarkupParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser

def _workflow_job_runners(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_jobs = False
    current_job: str | None = None
    runners: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if indent == 0 and stripped == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if indent == 0 and stripped:
            break
        if not stripped or stripped.startswith("#"):
            continue
        if indent == 2 and stripped.endswith(":"):
            current_job = stripped[:-1]
            continue
        if current_job and indent == 4 and stripped.startswith("runs-on:"):
            runners[current_job] = stripped.split(":", 1)[1].strip().strip("'\"")
    return runners


def _prepare_script() -> str:
    lines = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8").splitlines()
    marker = next(index for index, line in enumerate(lines) if line.strip() == "- name: Prepare static site")
    run_index = marker + 1
    if lines[run_index].strip() != "run: |":
        raise AssertionError("Pages prepare step is no longer a literal shell block")
    run_indent = len(lines[run_index]) - len(lines[run_index].lstrip())
    body_indent: int | None = None
    body: list[str] = []
    for line in lines[run_index + 1 :]:
        if not line.strip():
            body.append("")
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= run_indent:
            break
        body_indent = indent if body_indent is None else body_indent
        body.append(line[body_indent:])
    script = "\n".join(body).rstrip() + "\n"
    for command in (
        "rm -rf _site",
        "mkdir -p _site/assets",
        "cp -R site/. _site/",
        "cp assets/oh-my-jeo-icon.png _site/assets/oh-my-jeo-icon.png",
    ):
        if command not in script:
            raise AssertionError(f"reviewed Pages prepare step lost required command: {command}")
    return script


def _resolve_artifact_reference(page: Path, reference: str, artifact: Path) -> Path:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        raise AssertionError(f"expected a local static reference, got {reference!r}")
    if not parsed.path:
        raise AssertionError(f"empty static reference in {page}")
    target = (page.parent / unquote(parsed.path)).resolve()
    try:
        target.relative_to(artifact.resolve())
    except ValueError as exc:
        raise AssertionError(f"static reference escapes Pages artifact: {page} -> {reference}") from exc
    if not target.is_file():
        raise AssertionError(f"static reference is not published: {page} -> {reference}")
    return target


def _is_home_link(anchor: dict[str, object], page: Path, artifact: Path) -> bool:
    attrs = anchor["attrs"]
    assert isinstance(attrs, dict)
    href = attrs.get("href", "")
    if not isinstance(href, str) or not href:
        return False
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return False
    return (page.parent / unquote(parsed.path)).resolve() == artifact.resolve()


class StaticPublicationTests(unittest.TestCase):
    def test_ci_and_pages_jobs_pin_verified_ubuntu_runner(self) -> None:
        expected_runners = {
            "ci.yml": {"test": "ubuntu-24.04"},
            "pages.yml": {"build": "ubuntu-24.04", "deploy": "ubuntu-24.04"},
        }
        for workflow_name, expected in expected_runners.items():
            with self.subTest(workflow=workflow_name):
                self.assertEqual(_workflow_job_runners(WORKFLOWS / workflow_name), expected)

    def test_pages_prepare_publishes_all_eight_pages_and_local_media(self) -> None:
        source_pages = _static_pages()
        self.assertEqual(len(source_pages), 8, "the Pages surface must cover home, docs landing, and six feature pages")

        with TemporaryDirectory(prefix="omj-pages-static-") as temporary_directory:
            workspace = Path(temporary_directory)
            shutil.copytree(SITE, workspace / "site")
            (workspace / "assets").mkdir()
            for filename in ("hermes-agent-hero.png", "oh-my-jeo-icon.png"):
                shutil.copy2(REPO / "assets" / filename, workspace / "assets" / filename)

            subprocess.run(
                ["bash", "-euo", "pipefail", "-c", _prepare_script()],
                cwd=workspace,
                check=True,
                capture_output=True,
                text=True,
            )

            artifact = workspace / "_site"
            published_icon = (artifact / "assets" / "oh-my-jeo-icon.png").resolve()
            self.assertEqual(published_icon.read_bytes(), CANONICAL_ICON.read_bytes())

            for source_page in source_pages:
                relative_page = source_page.relative_to(SITE)
                artifact_page = artifact / relative_page
                self.assertTrue(artifact_page.is_file(), relative_page.as_posix())
                parsed = _parse(artifact_page)

                self.assertEqual(len(parsed.icons), 1, relative_page.as_posix())
                icon_target = _resolve_artifact_reference(artifact_page, parsed.icons[0]["href"], artifact)
                self.assertEqual(icon_target, published_icon, relative_page.as_posix())

                self.assertTrue(parsed.images, relative_page.as_posix())
                for image in parsed.images:
                    _resolve_artifact_reference(artifact_page, image["src"], artifact)

    def test_brand_home_links_are_unambiguously_named_and_decorative(self) -> None:
        source_pages = _static_pages()
        with TemporaryDirectory(prefix="omj-pages-a11y-") as temporary_directory:
            workspace = Path(temporary_directory)
            shutil.copytree(SITE, workspace / "site")
            artifact = workspace / "site"
            for source_page in source_pages:
                relative_page = source_page.relative_to(SITE)
                page = artifact / relative_page
                parsed = _parse(page)
                home_links = [anchor for anchor in parsed.anchors if _is_home_link(anchor, page, artifact)]
                self.assertEqual(len(home_links), 1, relative_page.as_posix())
                attrs = home_links[0]["attrs"]
                images = home_links[0]["images"]
                self.assertIsInstance(attrs, dict)
                self.assertEqual(attrs.get("aria-label"), "oh-my-jeo home", relative_page.as_posix())
                self.assertEqual(len(images), 1, relative_page.as_posix())
                self.assertEqual(images[0].get("alt"), "", relative_page.as_posix())

    def test_home_social_card_uses_square_icon_and_image_alt(self) -> None:
        parsed = _parse(SITE / "index.html")
        self.assertEqual(parsed.metadata.get("twitter:card"), ["summary"])
        self.assertEqual(parsed.metadata.get("twitter:image"), [CANONICAL_SOCIAL_IMAGE])
        image_alt = parsed.metadata.get("twitter:image:alt")
        self.assertIsNotNone(image_alt)
        self.assertEqual(len(image_alt or []), 1)
        self.assertTrue((image_alt or [""])[0].strip())


if __name__ == "__main__":
    unittest.main()
