from __future__ import annotations

import json
import os
import stat
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from _local_package import load_local_package

load_local_package()

import omj.local_store as local_store
from omj.config_adapter import ensure_external_dir, external_dirs, update_config


class AtomicStoreWriteTests(unittest.TestCase):
    def test_text_write_does_not_follow_preexisting_tmp_symlink(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.yaml"
            victim = root / "victim.txt"
            preexisting_tmp = root / f".{target.name}.tmp"
            original_victim = "DO NOT OVERWRITE\n"
            victim.write_text(original_victim, encoding="utf-8")
            preexisting_tmp.symlink_to(victim)

            try:
                local_store.atomic_write_text(target, "managed: true\n", private=True)
            except OSError:
                self.assertFalse(target.exists())
            else:
                self.assertEqual(target.read_text(encoding="utf-8"), "managed: true\n")
                self.assertFalse(target.is_symlink())

            self.assertEqual(victim.read_text(encoding="utf-8"), original_victim)
            self.assertTrue(preexisting_tmp.is_symlink())
            self.assertEqual(preexisting_tmp.resolve(), victim.resolve())

    def test_text_write_roundtrips_unicode_and_private_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "unicode.txt"
            content = "안전な設定 — café\n"

            local_store.atomic_write_text(target, content, private=True)

            self.assertEqual(target.read_text(encoding="utf-8"), content)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_json_write_roundtrips_unicode_and_private_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.json"
            payload = {
                "greeting": "안녕하세요, 世界 🌟",
                "nested": {"ключ": ["値", 0, False]},
            }

            local_store.atomic_write_json(target, payload, private=True)

            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), payload)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_bytes_write_roundtrips_binary_payload_and_private_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "payload.bin"
            payload = b"\x00\xff\x80\n\x00binary\x00"

            local_store.atomic_write_bytes(target, payload, private=True)

            self.assertEqual(target.read_bytes(), payload)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_nonprivate_new_file_mode_respects_umask_and_existing_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            created = root / "created.txt"
            preserved = root / "preserved.txt"
            old_umask = os.umask(0o022)
            try:
                local_store.atomic_write_text(created, "created\n")
                preserved.write_text("before\n", encoding="utf-8")
                preserved.chmod(0o640)
                local_store.atomic_write_text(preserved, "after\n")
            finally:
                os.umask(old_umask)

            self.assertEqual(stat.S_IMODE(created.stat().st_mode), 0o644)
            self.assertEqual(stat.S_IMODE(preserved.stat().st_mode), 0o640)

            restrictive = root / "restrictive.txt"
            old_umask = os.umask(0o077)
            try:
                local_store.atomic_write_text(restrictive, "restricted\n")
            finally:
                os.umask(old_umask)
            self.assertEqual(stat.S_IMODE(restrictive.stat().st_mode), 0o600)

    def test_replace_failure_preserves_target_and_cleans_only_new_tempfiles(self) -> None:
        for writer, suffix in (
            (
                lambda path: local_store.atomic_write_text(path, "new: true\n", private=True),
                ".yaml",
            ),
            (
                lambda path: local_store.atomic_write_json(path, {"new": "値"}, private=True),
                ".json",
            ),
        ):
            with self.subTest(suffix=suffix):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    target = root / f"config{suffix}"
                    victim = root / "operator-victim.txt"
                    operator_note = root / f".{target.name}.tmp"
                    operator_link = root / ".operator-link"
                    original_target = b"ORIGINAL TARGET BYTES\n"
                    original_victim = b"OPERATOR VICTIM\n"
                    target.write_bytes(original_target)
                    victim.write_bytes(original_victim)
                    operator_note.write_bytes(b"operator note: keep me\n")
                    operator_link.symlink_to(victim)
                    before = {entry.name for entry in root.iterdir()}

                    with mock.patch("os.replace", side_effect=OSError("forced replacement failure")):
                        with mock.patch("pathlib.Path.replace", side_effect=OSError("forced replacement failure")):
                            with self.assertRaises(OSError):
                                writer(target)

                    self.assertEqual(target.read_bytes(), original_target)
                    self.assertEqual(operator_note.read_bytes(), b"operator note: keep me\n")
                    self.assertTrue(operator_link.is_symlink())
                    self.assertEqual(operator_link.resolve(), victim.resolve())
                    self.assertEqual(victim.read_bytes(), original_victim)
                    self.assertEqual({entry.name for entry in root.iterdir()}, before)

    def test_encode_failure_preserves_target_and_operator_files_and_cleans_temp(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.yaml"
            victim = root / "operator-victim.txt"
            operator_note = root / f".{target.name}.tmp"
            operator_link = root / ".operator-link"
            target.write_bytes(b"ORIGINAL TARGET BYTES\n")
            victim.write_bytes(b"OPERATOR VICTIM\n")
            operator_note.write_bytes(b"operator note: keep me\n")
            operator_link.symlink_to(victim)
            before = {entry.name for entry in root.iterdir()}

            with self.assertRaises(UnicodeEncodeError):
                local_store.atomic_write_text(target, "invalid surrogate: \ud800", private=True)

            self.assertEqual(target.read_bytes(), b"ORIGINAL TARGET BYTES\n")
            self.assertEqual(operator_note.read_bytes(), b"operator note: keep me\n")
            self.assertTrue(operator_link.is_symlink())
            self.assertEqual(operator_link.resolve(), victim.resolve())
            self.assertEqual(victim.read_bytes(), b"OPERATOR VICTIM\n")
            self.assertEqual({entry.name for entry in root.iterdir()}, before)

    def test_keyboard_interrupt_preserves_target_and_operator_files_and_cleans_temp(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.yaml"
            victim = root / "operator-victim.txt"
            operator_note = root / f".{target.name}.tmp"
            operator_link = root / ".operator-link"
            target.write_bytes(b"ORIGINAL TARGET BYTES\n")
            victim.write_bytes(b"OPERATOR VICTIM\n")
            operator_note.write_bytes(b"operator note: keep me\n")
            operator_link.symlink_to(victim)
            before = {entry.name for entry in root.iterdir()}

            with mock.patch("os.replace", side_effect=KeyboardInterrupt):
                with mock.patch("pathlib.Path.replace", side_effect=KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        local_store.atomic_write_text(target, "new: true\n", private=True)

            self.assertEqual(target.read_bytes(), b"ORIGINAL TARGET BYTES\n")
            self.assertEqual(operator_note.read_bytes(), b"operator note: keep me\n")
            self.assertTrue(operator_link.is_symlink())
            self.assertEqual(operator_link.resolve(), victim.resolve())
            self.assertEqual(victim.read_bytes(), b"OPERATOR VICTIM\n")
            self.assertEqual({entry.name for entry in root.iterdir()}, before)

    def test_update_config_writes_real_mutation_through_atomic_boundary(self) -> None:
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "config.yaml"
            target.write_text("model: test\n", encoding="utf-8")
            managed_skill_dir = Path(tmp) / "managed-skills"

            result = update_config(target, lambda text: ensure_external_dir(text, managed_skill_dir))

            self.assertTrue(result.changed)
            self.assertTrue(result.written)
            self.assertEqual(external_dirs(target.read_text(encoding="utf-8")), [str(managed_skill_dir)])
            self.assertEqual(result.text, target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

