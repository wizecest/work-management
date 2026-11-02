"""Verify installation isolation and public packaging boundaries."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_release import build
from check_release import ROOT, public_paths
from install_skill import install


class ReleaseToolsTests(unittest.TestCase):
    def test_install_copies_only_skill_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as folder:
            target = install(Path(folder))
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertFalse((target / "README.md").exists())
            expected = {
                p.relative_to(ROOT / "skills/work-management").as_posix(): p.read_bytes()
                for p in public_paths() if p.is_relative_to(ROOT / "skills/work-management")
            }
            actual = {
                p.relative_to(target).as_posix(): p.read_bytes()
                for p in target.rglob("*") if p.is_file()
            }
            self.assertEqual(expected, actual)
            marker = target / "my-changes.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                install(Path(folder))
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_manifest_rejects_escaping_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for unsafe in ("../outside.txt", "/absolute.txt", "nested/../../file.txt"):
                (root / "release-files.json").write_text(json.dumps([unsafe]), encoding="utf-8")
                with self.assertRaises(ValueError):
                    public_paths(root)

    def test_manifest_rejects_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "release-files.json").write_text(
                json.dumps(["release-files.json", "RELEASE-FILES.JSON"]), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                public_paths(root)

    def test_package_exact_manifest_and_checksum_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = build(Path(folder))
            expected = {"work-management/" + p.relative_to(ROOT).as_posix() for p in public_paths()}
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(expected, set(bundle.namelist()))
                self.assertIsNone(bundle.testzip())
                for path in public_paths():
                    name = "work-management/" + path.relative_to(ROOT).as_posix()
                    self.assertEqual(path.read_bytes(), bundle.read(name))
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(digest, archive.with_suffix(".zip.sha256").read_text().split()[0])
            with self.assertRaises(FileExistsError):
                build(Path(folder))

    def test_package_rejects_output_inside_repository(self):
        with self.assertRaises(ValueError):
            build(ROOT / "dist")


if __name__ == "__main__":
    unittest.main()
