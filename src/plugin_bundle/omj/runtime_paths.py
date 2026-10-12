"""Offline, host-aware OMJ runtime home binding.

The copied plugin cannot depend on Hermes internals or a YAML package.  It uses
one small block-style scanner for the profile setting and otherwise selects the
store from trusted callback kwargs, explicit operator arguments, profile config,
then process defaults.  No value is cached: every callback binds before I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat
from typing import Any

class RuntimeBindingError(ValueError):
    """The selected runtime home is absent, malformed, or not attributable."""


@dataclass(frozen=True)
class RuntimeHomes:
    omj_home: Path
    hermes_home: Path


_VARIABLE = re.compile(r"\$(?:\{(?:env:)?([A-Za-z_][A-Za-z_0-9]*)\}|([A-Za-z_][A-Za-z_0-9]*))|%([A-Za-z_][A-Za-z_0-9]*)%")
_MISSING = object()
_MAX_CONFIG_FILE_BYTES = 262_144

def _canonical(value: str | Path, *, relative_to: Path | None = None) -> Path:
    raw = str(value).strip()
    if not raw or "\x00" in raw:
        raise RuntimeBindingError("OMJ runtime home must be a nonblank path")
    path = Path(raw).expanduser()
    if relative_to is not None and not path.is_absolute():
        path = relative_to / path
    try:
        return path.resolve()
    except (OSError, RuntimeError) as exc:
        raise RuntimeBindingError("OMJ runtime home could not be resolved") from exc


def _yaml_leaf(raw: str) -> str | None:
    value = raw.strip()
    if not value or value.startswith("#") or value.lower() in {"null", "~"}:
        return None
    if value[:1] in {"'", '"'}:
        quote = value[0]
        end = value.find(quote, 1)
        remainder = value[end + 1 :].strip() if end > 0 else ""
        if end <= 0 or (remainder and not remainder.startswith("#")):
            raise RuntimeBindingError("OMJ profile configuration is unreadable or invalid")
        return value[1:end]
    return re.split(r"\s+#", value, maxsplit=1)[0].rstrip()


def omj_home_setting(config_text: str) -> tuple[bool, str | None]:
    """Return the raw profile ``plugins.entries.omj.settings.omj_home`` leaf.

    This intentionally supports only the block mapping shape Hermes writes.  It
    avoids guessing at inline mappings, aliases, or YAML scalar coercion.
    """
    stack: list[tuple[int, str]] = []
    found: tuple[bool, str | None] = (False, None)
    target = ("plugins", "entries", "omj", "settings", "omj_home")
    for line in str(config_text or "").splitlines():
        if "\t" in line[: len(line) - len(line.lstrip(" \t"))]:
            raise RuntimeBindingError("OMJ profile configuration is tab-indented")
        body = line.strip()
        if not body or body.startswith("#") or body.startswith("-"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, separator, raw = body.partition(":")
        if not separator or (raw and not raw[0].isspace()):
            continue
        key = key.strip().strip("'\"")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = tuple(item[1] for item in stack) + (key,)
        if path == target:
            found = (True, _yaml_leaf(raw))
        # A nonempty value is a scalar/inline mapping, not a block to descend.
        if not raw.strip() or raw.strip().startswith(("&", "!")):
            stack.append((indent, key))
    return found


def _configured_home(hermes_home: Path) -> Path | object:
    config_path = hermes_home / "config.yaml"
    flags = os.O_RDONLY | os.O_NONBLOCK
    try:
        fd = os.open(config_path, flags)
    except FileNotFoundError:
        return _MISSING
    except OSError as exc:
        raise RuntimeBindingError("OMJ profile configuration is unreadable or invalid") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > _MAX_CONFIG_FILE_BYTES:
            return _MISSING
        raw = os.read(fd, _MAX_CONFIG_FILE_BYTES + 1)
    except OSError as exc:
        raise RuntimeBindingError("OMJ profile configuration is unreadable or invalid") from exc
    finally:
        os.close(fd)
    if len(raw) > _MAX_CONFIG_FILE_BYTES:
        return _MISSING
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeBindingError("OMJ profile configuration is unreadable or invalid") from exc
    found, raw = omj_home_setting(text)
    if not found:
        return _MISSING
    if raw is None:
        raise RuntimeBindingError("OMJ profile omj_home binding is blank")
    names = {next(group for group in match.groups() if group is not None) for match in _VARIABLE.finditer(raw)}
    unsupported = names - {"HOME", "HERMES_HOME"}
    if unsupported:
        raise RuntimeBindingError("OMJ profile omj_home binding uses an unavailable variable")
    value = raw
    for name in names:
        replacement = str(hermes_home if name == "HERMES_HOME" else Path.home())
        value = re.sub(rf"\$(?:\{{(?:env:)?{name}\}}|{name})|%{name}%", replacement, value)
    return _canonical(value, relative_to=hermes_home)


def resolve_homes(
    omj_home: str | Path | None = None,
    hermes_home: str | Path | None = None,
    *,
    host_kwargs: dict[str, Any] | None = None,
) -> RuntimeHomes:
    """Resolve one OMJ/Hermes pair before any reader or observation I/O.

    Trusted host callback kwargs outrank explicit model/operator arguments;
    profile-owned configuration outranks ambient environment.  Empty values are
    ignored and never silently replace a selected home.
    """
    host = host_kwargs or {}
    host_hermes = host.get("hermes_home")
    host_omj = host.get("omj_home")
    selected_hermes = host_hermes or hermes_home or os.environ.get("HERMES_HOME") or "~/.hermes"
    hermes = _canonical(selected_hermes)
    selected_omj = host_omj or omj_home
    if selected_omj:
        return RuntimeHomes(_canonical(selected_omj, relative_to=hermes), hermes)
    configured = _configured_home(hermes)
    if configured is not _MISSING:
        return RuntimeHomes(configured, hermes)
    ambient = os.environ.get("OMJ_HOME") or "~/.omj"
    return RuntimeHomes(_canonical(ambient, relative_to=hermes), hermes)


def resolve_handler_homes(args: dict[str, Any] | None, kwargs: dict[str, Any] | None) -> RuntimeHomes:
    values = args if isinstance(args, dict) else {}
    return resolve_homes(
        values.get("omj_home") or None,
        values.get("hermes_home") or None,
        host_kwargs=kwargs,
    )


def binding_diagnostic(selected: Path, hermes_home: Path, config_text: str) -> tuple[bool, str]:
    """Return ``(ok, diagnostic)`` for doctor without mutating config."""
    selected = _canonical(selected)
    hermes_home = _canonical(hermes_home)
    try:
        found, raw = omj_home_setting(config_text)
    except RuntimeBindingError as exc:
        return False, str(exc)
    if not found:
        return False, "plugins.entries.omj.settings.omj_home is missing"
    if raw is None:
        return False, "plugins.entries.omj.settings.omj_home is blank"
    try:
        configured = _configured_home_from_raw(raw, hermes_home)
    except RuntimeBindingError as exc:
        return False, str(exc)
    if configured != selected:
        return False, f"plugin binds {configured}; doctor selected {selected}"
    return True, f"plugin binding selects {selected}"


def _configured_home_from_raw(raw: str, hermes_home: Path) -> Path:
    names = {next(group for group in match.groups() if group is not None) for match in _VARIABLE.finditer(raw)}
    unsupported = names - {"HOME", "HERMES_HOME"}
    if unsupported:
        raise RuntimeBindingError("OMJ profile omj_home binding uses an unavailable variable")
    value = raw
    for name in names:
        replacement = str(hermes_home if name == "HERMES_HOME" else Path.home())
        value = re.sub(rf"\$(?:\{{(?:env:)?{name}\}}|{name})|%{name}%", replacement, value)
    return _canonical(value, relative_to=hermes_home)