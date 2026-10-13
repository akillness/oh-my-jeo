from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

SCAN_SCHEMA_VERSION = "plugin_bundle_import_scan/v1"
ABSOLUTE_CORE_IMPORT = "absolute_core_import"
ESCAPING_RELATIVE_IMPORT = "escaping_relative_import"
UNREADABLE_MODULE = "unreadable_module"
_GUARDING_EXCEPTION_NAMES = frozenset({"ImportError", "Exception", "BaseException"})
_TYPE_CHECKING_NAMES = frozenset({"TYPE_CHECKING", "typing.TYPE_CHECKING"})


def scan_bundle_core_imports(bundle_dir: Path, *, core_package: str = "omj") -> dict[str, Any]:
    """Statically inspect every installed Python module for hostless imports."""
    if not bundle_dir.is_dir():
        return _payload(bundle_dir, scanned=False, reason="plugin_bundle_not_installed")
    try:
        module_paths = bundle_module_paths(bundle_dir)
    except OSError as error:
        return _payload(
            bundle_dir,
            scanned=False,
            reason="plugin_bundle_unreadable",
            detail=f"{type(error).__name__}: {error}",
        )
    findings: list[dict[str, Any]] = []
    unguarded: set[str] = set()
    guarded_optional: set[str] = set()
    for path in module_paths:
        module_findings, module_unguarded, module_guarded = _module_findings(path, bundle_dir, core_package)
        findings.extend(module_findings)
        unguarded.update(module_unguarded)
        guarded_optional.update(module_guarded)
    return {
        **_payload(
            bundle_dir,
            scanned=True,
            reason="no_unguarded_core_imports" if not findings else "unguarded_core_imports",
            module_count=len(module_paths),
            findings=findings,
        ),
        "unguarded_imports": sorted(unguarded),
        "guarded_optional_imports": sorted(guarded_optional),
    }


def bundle_module_paths(bundle_dir: Path) -> tuple[Path, ...]:
    return tuple(sorted(bundle_dir.rglob("*.py")))


def describe_findings(findings: list[dict[str, Any]], *, limit: int = 5) -> str:
    shown = [
        f"{finding['module']}:{finding['line']} `{finding['statement']}`"
        for finding in findings[:limit]
    ]
    remaining = len(findings) - len(shown)
    if remaining > 0:
        shown.append(f"(+{remaining} more)")
    return "; ".join(shown)


def _payload(bundle_dir: Path, *, scanned: bool, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema_version": SCAN_SCHEMA_VERSION,
        "scanned": scanned,
        "ok": reason != "unguarded_core_imports",
        "reason": reason,
        "bundle_dir": str(bundle_dir),
        "module_count": 0,
        "findings": [],
        "unguarded_imports": [],
        "guarded_optional_imports": [],
        **extra,
    }


def _module_findings(path: Path, bundle_dir: Path, core_package: str) -> tuple[list[dict[str, Any]], set[str], set[str]]:
    module = path.relative_to(bundle_dir).as_posix()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as error:
        return (
            [{"module": module, "line": getattr(error, "lineno", 0) or 0, "kind": UNREADABLE_MODULE, "statement": f"{type(error).__name__}: {error}"}],
            set(),
            set(),
        )
    collector = _Collector(module=module, max_relative_level=len(path.relative_to(bundle_dir).parts), core_package=core_package)
    collector.visit_body(tree.body, guarded=False)
    return collector.findings, collector.unguarded, collector.guarded_optional


class _Collector:
    def __init__(self, *, module: str, max_relative_level: int, core_package: str) -> None:
        self.module = module
        self.max_relative_level = max_relative_level
        self.core_package = core_package
        self.findings: list[dict[str, Any]] = []
        self.unguarded: set[str] = set()
        self.guarded_optional: set[str] = set()

    def visit_body(self, body: list[ast.stmt], *, guarded: bool) -> None:
        for node in body:
            self.visit(node, guarded=guarded)

    def visit(self, node: ast.stmt, *, guarded: bool) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.Import):
            self._record_import(node, guarded=guarded)
        elif isinstance(node, ast.ImportFrom):
            self._record_import_from(node, guarded=guarded)
        elif isinstance(node, ast.Try):
            catches = _catches_import_error(node)
            self.visit_body(node.body, guarded=guarded or catches)
            for handler in node.handlers:
                self.visit_body(handler.body, guarded=guarded)
            self.visit_body(node.orelse, guarded=guarded)
            self.visit_body(node.finalbody, guarded=guarded)
        elif isinstance(node, ast.If):
            self.visit_body(node.body, guarded=guarded or _is_type_checking_test(node.test))
            self.visit_body(node.orelse, guarded=guarded)
        elif isinstance(node, ast.ClassDef):
            self.visit_body(node.body, guarded=guarded)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            self.visit_body(node.body, guarded=guarded)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            self.visit_body(node.body, guarded=guarded)
            self.visit_body(node.orelse, guarded=guarded)

    def _record_import(self, node: ast.Import, *, guarded: bool) -> None:
        for alias in node.names:
            name = alias.name.split(".", 1)[0]
            if guarded:
                self.guarded_optional.add(name)
            elif alias.name == self.core_package or alias.name.startswith(f"{self.core_package}."):
                self.unguarded.add(self.core_package)
                self._add(node, ABSOLUTE_CORE_IMPORT)
                return

    def _record_import_from(self, node: ast.ImportFrom, *, guarded: bool) -> None:
        if node.level:
            if node.level > self.max_relative_level and not guarded:
                self._add(node, ESCAPING_RELATIVE_IMPORT)
            return
        module = node.module or ""
        name = module.split(".", 1)[0]
        if guarded:
            self.guarded_optional.add(name)
        elif module == self.core_package or module.startswith(f"{self.core_package}."):
            self.unguarded.add(self.core_package)
            self._add(node, ABSOLUTE_CORE_IMPORT)

    def _add(self, node: ast.stmt, kind: str) -> None:
        self.findings.append({"module": self.module, "line": node.lineno, "kind": kind, "statement": " ".join(ast.unparse(node).split())})


def _catches_import_error(node: ast.Try) -> bool:
    for handler in node.handlers:
        if handler.type is None:
            return True
        candidates = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        if any(_exception_name(candidate) in _GUARDING_EXCEPTION_NAMES for candidate in candidates):
            return True
    return False


def _exception_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _is_type_checking_test(node: ast.expr) -> bool:
    if isinstance(node, ast.Name):
        return node.id in _TYPE_CHECKING_NAMES
    if isinstance(node, ast.Attribute):
        return node.attr == "TYPE_CHECKING"
    return False


__all__ = [
    "ABSOLUTE_CORE_IMPORT",
    "ESCAPING_RELATIVE_IMPORT",
    "SCAN_SCHEMA_VERSION",
    "UNREADABLE_MODULE",
    "bundle_module_paths",
    "describe_findings",
    "scan_bundle_core_imports",
]
