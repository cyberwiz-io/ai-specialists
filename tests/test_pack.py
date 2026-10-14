# SPDX-License-Identifier: Apache-2.0
import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pack", ROOT / "scripts/pack.py")
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)


class PackTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "work").mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=ROOT / "work"))
        self.addCleanup(self.clean_fixture)
        names = ["pack/" + name for name in pack.SECTIONS]
        names += ["pack/START-HERE.md"] + list(pack.LICENSE_FILES)
        for name in names:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes())
        pack.build(self.root)

    def clean_fixture(self):
        # Remove only this test's inventoried files, then its empty directories.
        for path in sorted(self.root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink()
        self.root.rmdir()

    def test_build_is_valid_and_reproducible(self):
        pack.check(self.root)
        first = (self.root / pack.ARCHIVE).read_bytes()
        pack.build(self.root)
        self.assertEqual(first, (self.root / pack.ARCHIVE).read_bytes())

    def test_modified_source_requires_rebuild(self):
        path = self.root / "pack/COORDINATOR.md"
        path.write_text(path.read_text() + "\nA changed instruction.\n")
        with self.assertRaisesRegex(ValueError, "Combined instructions differ"):
            pack.check(self.root)
        pack.build(self.root)
        pack.check(self.root)

    def test_missing_role_section_fails(self):
        path = self.root / "pack/specialists/copywriter.md"
        path.write_text(path.read_text().replace("**Acceptance:**", "**Checks:**"))
        pack.build(self.root)
        with self.assertRaisesRegex(ValueError, "missing Acceptance"):
            pack.check(self.root)

    def test_wrong_version_fails(self):
        path = self.root / "pack/COORDINATOR.md"
        path.write_text(path.read_text().replace("Version: 0.1", "Version: 0.2"))
        pack.build(self.root)
        with self.assertRaisesRegex(ValueError, "expected one Version"):
            pack.check(self.root)

    def test_broken_or_escaping_link_fails(self):
        for target in ("missing.md", "../outside.md"):
            with self.subTest(target=target):
                (self.root / "README.md").write_text(f"[Bad]({target})")
                with self.assertRaisesRegex(ValueError, "invalid local link"):
                    pack.check(self.root)

    def test_zip_rejects_extra_file(self):
        with ZipFile(self.root / pack.ARCHIVE, "a") as bundle:
            bundle.writestr("private-profile.md", "Not an approved member")
        with self.assertRaisesRegex(ValueError, "ZIP membership differs"):
            pack.check(self.root)

    def test_zip_rejects_changed_bytes(self):
        expected = pack.members(self.root)
        with ZipFile(self.root / pack.ARCHIVE, "w") as bundle:
            for index, (name, data) in enumerate(expected.items()):
                bundle.writestr(name, b"changed" if index == 0 else data)
        with self.assertRaisesRegex(ValueError, "ZIP bytes differ"):
            pack.check(self.root)

    def test_source_symlink_is_rejected(self):
        target = self.root / "pack/COORDINATOR.md"
        target.rename(self.root / "coordinator-original.md")
        target.symlink_to(self.root / "coordinator-original.md")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            pack.build(self.root)

    def test_missing_license_does_not_replace_outputs(self):
        before = (self.root / "pack/STARTER-PACK.md").read_bytes()
        archive = (self.root / pack.ARCHIVE).read_bytes()
        (self.root / "LICENSES/CC-BY-4.0.txt").unlink()
        with self.assertRaises(FileNotFoundError):
            pack.build(self.root)
        self.assertEqual(before, (self.root / "pack/STARTER-PACK.md").read_bytes())
        self.assertEqual(archive, (self.root / pack.ARCHIVE).read_bytes())

    def test_destination_symlink_is_rejected(self):
        path = self.root / pack.ARCHIVE
        path.unlink()
        path.symlink_to(self.root / "LICENSE.md")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            pack.build(self.root)


if __name__ == "__main__":
    unittest.main()
