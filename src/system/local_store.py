from __future__ import annotations

import json
import os
import secrets
import stat
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path, *, private: bool = False) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if private:
        path.chmod(0o700)


def ensure_file(path: Path, *, private: bool = False) -> None:
    if not path.exists():
        path.touch(mode=0o600 if private else 0o666)
    if private:
        path.chmod(0o600)


def can_write_dir(path: Path, *, probe_name: str = ".write-test", private: bool = False) -> bool:
    try:
        ensure_dir(path, private=private)
        probe = path / probe_name
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def _unlink_quietly(path: Path) -> None:
    # Best-effort cleanup of a tempfile we own; never raises over the
    # exception that is already propagating.
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def _open_exclusive_sibling(path: Path, *, attempts: int = 8) -> tuple[int, Path]:
    """Create and open a brand-new sibling of ``path`` with an unguessable name.

    ``O_CREAT | O_EXCL`` fails instead of following or truncating anything
    that already occupies a candidate name (a planted symlink, a file left
    by another process, a directory, ...), so this never writes through a
    pre-existing path. The random suffix (not the predictable
    ``.<name>.tmp`` convention) means an attacker cannot pre-plant a link at
    the name we will actually use. Creation mode ``0o666`` is masked by the
    process umask exactly like a normal ``open(..., "w")`` would be, so a
    public write lands on the same default mode a brand-new file would get.
    """
    last_error: OSError | None = None
    for _ in range(attempts):
        candidate = path.with_name(f".{path.name}.{secrets.token_hex(16)}.tmp")
        try:
            fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError as exc:
            last_error = exc
            continue
        return fd, candidate
    raise OSError(f"could not allocate a unique temporary file next to {path}") from last_error


def atomic_write_bytes(path: Path, data: bytes, *, private: bool = False) -> None:
    """Write ``data`` to ``path`` atomically; the canonical writer backing
    ``atomic_write_text``/``atomic_write_json`` and any raw-byte caller.

    Content lands at ``path`` in one of two states only: the previous bytes
    (untouched, on any failure) or the complete new content (after a single
    ``rename``). Nothing is ever written through a pre-planted temp-name
    symlink, and cleanup only ever removes the fresh tempfile this call
    itself created -- never a pre-existing file at that name, malicious or
    not.
    """
    ensure_dir(path.parent, private=private)
    preserved_mode: int | None = None
    if not private and path.exists():
        preserved_mode = stat.S_IMODE(path.stat().st_mode)
    fd, tmp = _open_exclusive_sibling(path)
    try:
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view) :]
            if private:
                os.fchmod(fd, 0o600)
            elif preserved_mode is not None:
                os.fchmod(fd, preserved_mode)
        finally:
            os.close(fd)
        tmp.replace(path)
    except BaseException:
        # Covers OSError (e.g. a failed rename) as well as KeyboardInterrupt
        # and any other interruption: the destination must keep its prior
        # bytes and only the tempfile we just created is removed.
        _unlink_quietly(tmp)
        raise
    if private:
        path.chmod(0o600)


def atomic_write_text(path: Path, text: str, *, private: bool = False) -> None:
    # Encoding happens before any filesystem mutation: a bad surrogate raises
    # UnicodeEncodeError with nothing on disk left to clean up.
    atomic_write_bytes(path, text.encode("utf-8"), private=private)


def atomic_write_json(path: Path, data: dict[str, Any], *, private: bool = False) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n", private=private)


def read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected JSON object")
    return data


def read_json_object_result(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return read_json_object(path), None
    except (OSError, JSONDecodeError, ValueError) as exc:
        return None, str(exc)


def read_jsonl_objects(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"{path}: {exc}"]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except JSONDecodeError as exc:
            errors.append(f"{path}:{index}: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path}:{index}: event must be an object")
            continue
        records.append(record)
    return records, errors
