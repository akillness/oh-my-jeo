from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import os
import time
from typing import Callable

from ..local_store import atomic_write_text


@dataclass(frozen=True)
class ConfigChange:
    changed: bool
    message: str
    text: str


class ConfigWriteRefused(RuntimeError):
    """Base class for refusing a config write that could lose user data."""


class ConfigConcurrentUpdate(ConfigWriteRefused):
    """Another writer changed config.yaml while this mutation was running."""


@dataclass(frozen=True)
class ConfigUpdate:
    changed: bool
    written: bool
    message: str
    text: str
    attempts: int
    lock_enforced: bool = False


@dataclass(frozen=True)
class _InlineExternalDirs:
    matched: bool
    supported: bool
    values: list[str]


_BARE_YAML_NULLS = {"null", "Null", "NULL", "~"}
_UNSUPPORTED_EXTERNAL_DIRS_SHAPE = "unsupported skills.external_dirs shape; use a YAML block list or inline list"
_DUPLICATE_EXTERNAL_DIRS_SHAPE = "duplicate skills.external_dirs entries are unsupported; keep one YAML block list or inline list"


def _normalize(value: str | Path) -> str:
    return os.path.normpath(os.path.expanduser(str(value).strip()))


def _normalize_home(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def _paths_equivalent(left: str | Path, right: str | Path) -> bool:
    """Compare paths by expanded realpath while preserving stored spelling."""
    try:
        return Path(left).expanduser().resolve(strict=False) == Path(right).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return str(left).strip() == str(right).strip()


def _parse_inline_list(value: str) -> list[str] | None:
    value = value.strip()
    if value == "[]":
        return []
    if not (value.startswith("[") and value.endswith("]")):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    items = []
    for raw in inner.split(","):
        item = raw.strip().strip("'\"")
        if not item:
            return None
        items.append(item)
    return items


def _format_external_dirs(values: list[str]) -> list[str]:
    return ["  external_dirs:", *[f"    - {value}" for value in values]]


def _external_dir_item_value(line: str) -> str | None:
    if line.startswith("    - ") or line.startswith("  - "):
        return line.strip()[2:].strip().strip("'\"")
    return None


def _external_dir_item_prefix(line: str) -> str | None:
    if line.startswith("    - "):
        return "    - "
    if line.startswith("  - "):
        return "  - "
    return None


def _classify_inline_external_dirs(line: str) -> _InlineExternalDirs:
    # Readers stay non-throwing for doctor/probe stability: unsupported inline
    # scalars mean "no valid dirs observed". Mutations remain strict and reject
    # matched-but-unsupported shapes instead of guessing YAML semantics.
    match = re.match(r"^  external_dirs:\s*(?P<value>\S.*)$", line)
    if not match:
        return _InlineExternalDirs(False, False, [])
    value = match.group("value").strip()
    if value in _BARE_YAML_NULLS:
        return _InlineExternalDirs(True, True, [])
    parsed = _parse_inline_list(value)
    if parsed is None:
        return _InlineExternalDirs(True, False, [])
    return _InlineExternalDirs(True, True, parsed)


def _validate_external_dirs_mutation_shape(config_text: str) -> None:
    in_skills = False
    external_dirs_declarations = 0
    for line in config_text.splitlines():
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            in_skills = stripped == "skills:"
            continue
        if in_skills and line.startswith("  ") and not line.startswith("    "):
            inline = _classify_inline_external_dirs(line)
            if inline.matched or stripped == "external_dirs:":
                external_dirs_declarations += 1
                if external_dirs_declarations > 1:
                    raise ValueError(_DUPLICATE_EXTERNAL_DIRS_SHAPE)
                if inline.matched and not inline.supported:
                    raise ValueError(_UNSUPPORTED_EXTERNAL_DIRS_SHAPE)


def external_dirs(config_text: str) -> list[str]:
    lines = config_text.splitlines()
    result: list[str] = []
    in_skills = False
    in_external = False
    for line in lines:
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            in_skills = stripped == "skills:"
            in_external = False
            continue
        if in_skills and in_external:
            value = _external_dir_item_value(line)
            if value is not None:
                result.append(value)
                continue
        if in_skills and line.startswith("  ") and not line.startswith("    "):
            inline = _classify_inline_external_dirs(line)
            if inline.matched:
                if inline.supported:
                    result.extend(inline.values)
                in_external = False
                continue
            in_external = stripped == "external_dirs:"
            continue
    return result
def external_dir_registered(values: list[str], target: str | Path) -> bool:
    """Return whether a textual external-dir entry denotes ``target``."""
    return any(_paths_equivalent(value, target) for value in values)



def _plugin_node(line: str) -> tuple[str, dict[str, list[str]]] | tuple[str, None]:
    """Classify a top-level plugins node without importing a YAML parser."""
    stripped = line.strip()
    if not stripped.startswith("plugins:"):
        return ("other", None)
    rest = stripped[len("plugins:"):].strip()
    if not rest:
        return ("block", None)
    if not (rest.startswith("{") and rest.endswith("}")):
        return ("unreadable", None)
    values: dict[str, list[str]] = {"enabled": [], "disabled": []}
    for field in rest[1:-1].split(","):
        key, sep, raw = field.partition(":")
        if not sep or key.strip().strip("'\"") not in values:
            continue
        key = key.strip().strip("'\"")
        parsed = _parse_inline_list(raw.strip())
        if parsed is None:
            return ("unreadable", None)
        values[key] = [item.strip().strip("'\"") for item in parsed]
    return ("flow", values)


def _plugin_list_shape(rest: str) -> tuple[str, list[str]]:
    value = rest.strip()
    if value == "" or value in _BARE_YAML_NULLS:
        return "block", []
    parsed = _parse_inline_list(value)
    if parsed is not None:
        return ("inline" if parsed else "empty"), parsed
    if value[:1] in {"'", '"'} or value.startswith("{") or "#" in value:
        return "scalar", []
    return "scalar", []


def plugin_enablement(config_text: str) -> dict[str, list[str]]:
    """Read plugins.enabled and plugins.disabled in supported Hermes shapes."""
    result = {"enabled": [], "disabled": []}
    in_plugins = False
    current = ""
    for line in config_text.splitlines():
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            node, flow = _plugin_node(line)
            in_plugins = node == "block"
            current = ""
            if node == "flow" and flow is not None:
                result = flow
            continue
        if not in_plugins or not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                result[current].append(stripped[2:].strip().strip("'\""))
            continue
        if line.startswith("  ") and not line.startswith("    "):
            key, _, rest = stripped.partition(":")
            key = key.strip().strip("'\"")
            if key not in result:
                current = ""
                continue
            shape, values = _plugin_list_shape(rest)
            if shape in {"inline", "empty"}:
                result[key] = values
                current = ""
            elif shape == "block":
                current = key
            else:
                result[key] = []
                current = ""
    return result


def plugin_is_enabled(config_text: str, name: str) -> bool:
    listed = plugin_enablement(config_text)
    return name in listed["enabled"] and name not in listed["disabled"]


def plugin_enablement_is_readable(config_text: str) -> bool:
    return all(_plugin_node(line)[0] != "unreadable" for line in config_text.splitlines() if line.strip().startswith("plugins:"))


def plugins_enabled_extension_error(config_text: str, name: str) -> str:
    enabled_keys = 0
    in_plugins = False
    for line in config_text.splitlines():
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            node, _flow = _plugin_node(line)
            in_plugins = node == "block"
            if node == "flow":
                return f"setup extends a plain `plugins:` block; unsupported flow plugins node `{stripped}`"
            if node == "unreadable":
                listed = plugin_enablement(config_text)
                if name not in listed["enabled"] and name not in listed["disabled"]:
                    return f"setup extends a plain `plugins:` block; unsupported plugins node `{stripped}`"
            continue
        if in_plugins and line.startswith("  ") and not line.startswith("    "):
            key, _, rest = stripped.partition(":")
            if key.strip() == "enabled":
                enabled_keys += 1
                if enabled_keys > 1:
                    return "duplicate plugins.enabled entries are unsupported"
                if _plugin_list_shape(rest)[0] == "scalar":
                    return f"unsupported plugins.enabled shape ({rest.strip()!r}); use a YAML block list or inline list"
    return ""


def _plugin_item_indent(lines: list[str], plugins_index: int) -> str:
    for line in lines[plugins_index + 1:]:
        if line.strip() and not line.startswith(" "):
            break
        if line.strip().startswith("- "):
            return line[: len(line) - len(line.lstrip(" "))]
    return "    "


def ensure_plugin_enabled(config_text: str, name: str = "omj") -> ConfigChange:
    refusal = plugins_enabled_extension_error(config_text, name)
    if refusal:
        raise ValueError(refusal)
    listed = plugin_enablement(config_text)
    if name in listed["disabled"]:
        return ConfigChange(False, f"{name} is explicitly disabled; leaving it alone", config_text)
    if name in listed["enabled"]:
        return ConfigChange(False, "plugin already enabled", config_text)
    lines = config_text.splitlines()
    plugins_index = next((idx for idx, line in enumerate(lines) if line.strip() == "plugins:" and not line.startswith(" ")), None)
    if plugins_index is None:
        text = (config_text.rstrip() + f"\n\nplugins:\n  enabled:\n    - {name}\n").lstrip("\n")
        return ConfigChange(True, "appended plugins.enabled", text)
    indent = _plugin_item_indent(lines, plugins_index)
    for idx in range(plugins_index + 1, len(lines)):
        line = lines[idx]
        if line.strip() and not line.startswith(" "):
            break
        if line.strip().startswith("- "):
            continue
        if line.startswith("  ") and not line.startswith("    "):
            key, _, rest = line.strip().partition(":")
            if key.strip() != "enabled":
                continue
            shape, values = _plugin_list_shape(rest)
            if shape in {"inline", "empty"}:
                lines[idx:idx + 1] = ["  enabled:", *[f"{indent}- {value}" for value in [*values, name]]]
                return ConfigChange(True, "expanded plugins.enabled", "\n".join(lines) + "\n")
            if shape == "scalar":
                raise ValueError(f"unsupported plugins.enabled shape ({rest.strip()!r}); use a YAML block list or inline list")
            insert_at = idx + 1
            while insert_at < len(lines) and lines[insert_at].strip().startswith("- "):
                insert_at += 1
            lines.insert(insert_at, f"{indent}- {name}")
            return ConfigChange(True, "added plugin to plugins.enabled", "\n".join(lines) + "\n")
    lines[plugins_index + 1:plugins_index + 1] = ["  enabled:", f"{indent}- {name}"]
    return ConfigChange(True, "inserted plugins.enabled", "\n".join(lines) + "\n")


def remove_plugin_enabled(config_text: str, name: str = "omj") -> ConfigChange:
    listed = plugin_enablement(config_text)
    if name not in listed["enabled"]:
        return ConfigChange(False, f"{name} is not in plugins.enabled", config_text)
    refusal = plugins_enabled_extension_error(config_text, name)
    if refusal:
        return ConfigChange(False, refusal, config_text)
    in_plugins = False
    current = False
    output: list[str] = []
    changed = False
    for line in config_text.splitlines(keepends=True):
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            in_plugins = stripped == "plugins:"
            current = False
        if in_plugins and line.startswith("  ") and not line.startswith("    "):
            key, _, rest = stripped.partition(":")
            current = key.strip().strip("'\"") == "enabled"
            if current and _plugin_list_shape(rest)[0] == "inline":
                values = rest.strip()[1:-1].split(",")
                remaining = [value for value in values if value.strip().strip("'\"") != name]
                if len(remaining) != len(values):
                    changed = True
                    output.append(line[:line.index("[") + 1] + ",".join(remaining) + line[line.rindex("]"):])
                    continue
        if in_plugins and current and line.startswith(("    - ", "  - ")) and stripped[2:].strip().strip("'\"") == name:
            changed = True
            continue
        output.append(line)
    if not changed:
        return ConfigChange(False, f"{name} is not in plugins.enabled", config_text)
    return ConfigChange(True, "removed plugin from plugins.enabled", "".join(output))

def ensure_external_dir(config_text: str, skill_dir: str | Path) -> ConfigChange:
    _validate_external_dirs_mutation_shape(config_text)
    target = _normalize(skill_dir)
    if any(_paths_equivalent(value, target) for value in external_dirs(config_text)):
        return ConfigChange(False, "external dir already present", config_text)

    lines = config_text.splitlines()
    if not lines:
        text = f"skills:\n  external_dirs:\n    - {target}\n"
        return ConfigChange(True, "created skills.external_dirs", text)

    skills_index = next((idx for idx, line in enumerate(lines) if line.strip() == "skills:" and not line.startswith(" ")), None)
    if skills_index is None:
        text = config_text.rstrip() + f"\n\nskills:\n  external_dirs:\n    - {target}\n"
        return ConfigChange(True, "appended skills.external_dirs", text)

    external_index = None
    for idx in range(skills_index + 1, len(lines)):
        line = lines[idx]
        if line and not line.startswith(" "):
            break
        if line.startswith("  ") and not line.startswith("    "):
            inline = _classify_inline_external_dirs(line)
            if inline.matched:
                if not inline.supported:
                    raise ValueError(_UNSUPPORTED_EXTERNAL_DIRS_SHAPE)
                values = inline.values
                if any(_paths_equivalent(value, target) for value in values):
                    return ConfigChange(False, "external dir already present", config_text)
                lines[idx:idx + 1] = _format_external_dirs([*values, target])
                return ConfigChange(True, "expanded inline external_dirs", "\n".join(lines) + "\n")
            if line.strip() == "external_dirs:":
                external_index = idx
                break

    if external_index is None:
        lines[skills_index + 1:skills_index + 1] = ["  external_dirs:", f"    - {target}"]
        return ConfigChange(True, "inserted skills.external_dirs", "\n".join(lines) + "\n")

    insert_at = external_index + 1
    item_prefix = "    - "
    while insert_at < len(lines):
        prefix = _external_dir_item_prefix(lines[insert_at])
        if prefix is None:
            break
        item_prefix = prefix
        insert_at += 1
    lines.insert(insert_at, f"{item_prefix}{target}")
    return ConfigChange(True, "added external dir", "\n".join(lines) + "\n")


def remove_external_dir(config_text: str, skill_dir: str | Path) -> ConfigChange:
    _validate_external_dirs_mutation_shape(config_text)
    target = _normalize(skill_dir)
    lines = config_text.splitlines()
    changed = False
    output: list[str] = []
    in_skills = False
    in_external = False
    for line in lines:
        stripped = line.strip()
        if not line.startswith(" ") and stripped:
            in_skills = stripped == "skills:"
            in_external = False
            output.append(line)
            continue
        if in_skills and in_external:
            value = _external_dir_item_value(line)
            if value is not None:
                if _paths_equivalent(value, target):
                    changed = True
                    continue
                output.append(line)
                continue
        if in_skills and line.startswith("  ") and not line.startswith("    "):
            inline = _classify_inline_external_dirs(line)
            if inline.matched:
                if not inline.supported:
                    raise ValueError(_UNSUPPORTED_EXTERNAL_DIRS_SHAPE)
                values = [value for value in inline.values if not _paths_equivalent(value, target)]
                if len(values) != len(inline.values):
                    changed = True
                    output.extend(_format_external_dirs(values))
                    in_external = False
                    continue
            in_external = stripped == "external_dirs:"
            output.append(line)
            continue
        output.append(line)
    if not changed:
        return ConfigChange(False, "external dir absent", config_text)
    return ConfigChange(True, "removed external dir", "\n".join(output).rstrip() + "\n")


def omj_home_setting(config_text: str) -> tuple[bool, str | None]:
    """Read the plugin-owned home leaf using the copied plugin's scanner."""
    from ..plugin_bundle.omj.runtime_paths import omj_home_setting as scan_home

    return scan_home(config_text)


def _block_end(lines: list[str], start: int, stop: int, parent_indent: int) -> int:
    for index in range(start, stop):
        line = lines[index]
        if line.strip() and len(line) - len(line.lstrip(" ")) <= parent_indent:
            return index
    return stop


def ensure_omj_home_binding(config_text: str, omj_home: str | Path) -> ConfigChange:
    """Record the selected absolute OMJ store only when the profile is unset."""
    for line in config_text.splitlines():
        if not line.startswith(" ") and _plugin_node(line)[0] in {"flow", "unreadable"}:
            raise ValueError("OMJ home binding requires a plain `plugins:` block; unsupported plugins node")
    value = _normalize_home(omj_home)
    try:
        found, _current = omj_home_setting(config_text)
    except ValueError as exc:
        return ConfigChange(False, f"{exc}; OMJ home binding left unchanged", config_text)
    if found:
        return ConfigChange(False, "plugins.entries.omj.settings.omj_home already set", config_text)
    lines = config_text.splitlines()
    if not lines:
        return ConfigChange(True, "recorded plugins.entries.omj.settings.omj_home", "plugins:\n  entries:\n    omj:\n      settings:\n        omj_home: '" + value + "'\n")
    plugins_index = next((idx for idx, line in enumerate(lines) if line.strip() == "plugins:" and not line.startswith(" ")), None)
    if plugins_index is None:
        text = config_text.rstrip() + "\n\nplugins:\n  entries:\n    omj:\n      settings:\n        omj_home: '" + value + "'\n"
        return ConfigChange(True, "recorded plugins.entries.omj.settings.omj_home", text)
    plugins_end = _block_end(lines, plugins_index + 1, len(lines), 0)
    entries_index = next((idx for idx in range(plugins_index + 1, plugins_end) if lines[idx].strip() == "entries:" and len(lines[idx]) - len(lines[idx].lstrip(" ")) == 2), None)
    if entries_index is None:
        lines[plugins_end:plugins_end] = ["  entries:", "    omj:", "      settings:", f"        omj_home: '{value}'"]
    else:
        entries_end = _block_end(lines, entries_index + 1, plugins_end, 2)
        omj_index = next((idx for idx in range(entries_index + 1, entries_end) if lines[idx].strip() == "omj:" and len(lines[idx]) - len(lines[idx].lstrip(" ")) == 4), None)
        if omj_index is None:
            lines[entries_end:entries_end] = ["    omj:", "      settings:", f"        omj_home: '{value}'"]
        else:
            omj_end = _block_end(lines, omj_index + 1, entries_end, 4)
            settings_index = next((idx for idx in range(omj_index + 1, omj_end) if lines[idx].strip() == "settings:" and len(lines[idx]) - len(lines[idx].lstrip(" ")) == 6), None)
            if settings_index is None:
                lines[omj_end:omj_end] = ["      settings:", f"        omj_home: '{value}'"]
            else:
                settings_end = _block_end(lines, settings_index + 1, omj_end, 6)
                lines[settings_end:settings_end] = [f"        omj_home: '{value}'"]
    text = "\n".join(lines).rstrip() + "\n"
    try:
        found, written = omj_home_setting(text)
    except ValueError:
        return ConfigChange(False, "OMJ home binding shape is unreadable; left unchanged", config_text)
    if not found or written != value:
        return ConfigChange(False, "OMJ home binding could not be read back; left unchanged", config_text)
    return ConfigChange(True, "recorded plugins.entries.omj.settings.omj_home", text)


def plugin_omj_home_setting(config_text: str) -> str:
    try:
        found, value = omj_home_setting(config_text)
    except ValueError:
        return ""
    return value or "" if found else ""


def ensure_plugin_omj_home(config_text: str, omj_home: str | Path) -> ConfigChange:
    return ensure_omj_home_binding(config_text, omj_home)

def remove_plugin_omj_home(config_text: str, expected: str | Path) -> ConfigChange:
    current = plugin_omj_home_setting(config_text)
    if not current or not _paths_equivalent(current, _normalize_home(expected)):
        return ConfigChange(False, "OMJ home binding is not the owned value", config_text)
    lines = config_text.splitlines(keepends=True)
    stack: list[tuple[int, str]] = []
    matches: list[int] = []
    for index, line in enumerate(lines):
        body = line.strip()
        if not body or body.startswith(("#", "-")):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, separator, raw = body.partition(":")
        if not separator or (raw and not raw[0].isspace()):
            continue
        while stack and stack[-1][0] >= indent:
            stack.pop()
        key = key.strip().strip("'\"")
        if tuple(item[1] for item in stack) + (key,) == ("plugins", "entries", "omj", "settings", "omj_home"):
            matches.append(index)
        if not raw.strip() or raw.strip().startswith(("&", "!")):
            stack.append((indent, key))
    if len(matches) != 1:
        return ConfigChange(False, "OMJ home binding is ambiguous or absent; left unchanged", config_text)
    del lines[matches[0]]
    return ConfigChange(True, "removed plugins.entries.omj.settings.omj_home", "".join(lines))


def remove_omj_home_binding(config_text: str, expected: str | Path) -> ConfigChange:
    return remove_plugin_omj_home(config_text, expected)

def update_config(
    path: Path,
    mutate: Callable[[str], ConfigChange],
    *,
    omj_home: str | Path | None = None,
    dry_run: bool = False,
    attempts: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> ConfigUpdate:
    """Read, derive and atomically write one config without clobbering races."""
    rounds = max(int(attempts), 1)
    for attempt in range(1, rounds + 1):
        before_exists = path.exists()
        before = path.read_bytes() if before_exists else None
        text = read_config(path)
        change = mutate(text)
        if not change.changed or dry_run:
            return ConfigUpdate(change.changed, False, change.message, change.text, attempt)
        after_exists = path.exists()
        after = path.read_bytes() if after_exists else None
        if before_exists != after_exists or before != after:
            if attempt < rounds:
                sleep(0.005 * attempt)
                continue
            raise ConfigConcurrentUpdate(f"config.yaml changed during update: {path}")
        if path.is_symlink():
            raise ConfigWriteRefused("config.yaml is a symlink; refusing to rewrite it")
        atomic_write_text(path, change.text)
        return ConfigUpdate(True, True, change.message, change.text, attempt)
    raise ConfigConcurrentUpdate(f"config.yaml kept changing during update: {path}")

def read_config(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_config(path: Path, text: str) -> None:
    atomic_write_text(path, text)
