# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from packlib import bundle, generate


class ArchiveBoundaryTests(unittest.TestCase):
    def test_combined_pack_rebases_source_links(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "catalog/family").mkdir(parents=True)
            (root / "catalog/family/INDEX.md").write_text("[Role](role.md)\n")
            combined = generate._combine("header", root, ["catalog/family/INDEX.md"], {}, "dist/packs/family.md")
            self.assertIn(b"](../../catalog/family/role.md)", combined)

    def test_complete_links_pass_and_missing_documents_fail(self):
        payload = {"pack/START-HERE.md": b"[Map](../REPO-MAP.md)", "REPO-MAP.md": b"# Map"}
        self.assertEqual(bundle.payload_problems(payload), [])
        del payload["REPO-MAP.md"]
        self.assertTrue(any("missing local link" in x for x in bundle.payload_problems(payload)))

    def test_paths_and_private_members_fail(self):
        for name in ("../escape", "/absolute", "C:/drive", "a\\b", "work/private.md",
                     ".claude/settings.json", ".agents/skills/private/SKILL.md"):
            with self.subTest(name=name):
                self.assertTrue(bundle.payload_problems({name: b"x"}))

    def test_fragment_checks(self):
        self.assertEqual(bundle.payload_problems({"README.md": b"[Read](#setup)\n# Setup\n"}), [])
        self.assertTrue(bundle.payload_problems({"README.md": b"[Read](#absent)\n# Setup\n"}))

    def test_duplicate_members_are_rejected(self):
        import tempfile
        from zipfile import ZipFile
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("root/README.md", b"first")
                archive.writestr("root/README.md", b"second")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                bundle.read_archive(path)
