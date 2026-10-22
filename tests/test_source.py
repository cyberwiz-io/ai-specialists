# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from packlib import build, check, config, source


class SourceTests(unittest.TestCase):
    def test_tracked_archive_in_runtime_directory_is_rejected(self):
        self.write("work/committed.zip", "fixture")
        self.git("add", "work/committed.zip")
        self.assertTrue(check.check_archives(self.root))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.write("config/modules.json", json.dumps({"local_material": {
            "directories": [".claude/skills", ".agents/skills", ".codex/agents"],
            "files": [".codex/hooks.json"],
            "sources": [".claude/skills/card-evals"]}}))
        self.write(".claude/skills/card-evals/SKILL.md", "owned")
        self.write("README.md", "source")
        self.git("init", "-q")
        self.git("add", "config/modules.json", "README.md", ".claude/skills/card-evals")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def test_external_install_is_not_read_or_copied(self):
        external = Path(self.tmp.name) / "private"
        external.mkdir()
        (external / "SKILL.md").write_text("[private](missing.md)")
        (self.root / ".claude/skills/installed").symlink_to(external, target_is_directory=True)
        self.write(".agents/skills/copied/SKILL.md", "installed")
        self.write(".codex/hooks.json", "local")
        names = source.files(self.root)
        self.assertIn(".claude/skills/card-evals/SKILL.md", names)
        self.assertFalse(any("installed" in n or "copied" in n for n in names))
        destination = Path(self.tmp.name) / "fixture"
        source.copy(self.root, destination)
        self.assertFalse((destination / ".agents/skills").exists())
        self.assertFalse((destination / ".codex/hooks.json").exists())
        self.assertEqual((destination / "README.md").read_text(), "source")

    def test_tracked_source_overrides_local_install_location(self):
        self.write(".agents/skills/owned/SKILL.md", "tracked")
        self.git("add", ".agents/skills/owned/SKILL.md")
        self.assertIn(".agents/skills/owned/SKILL.md", source.files(self.root))

    def test_new_ordinary_source_and_explicit_source_are_retained(self):
        self.write("docs/new.md", "new")
        self.assertIn("docs/new.md", source.files(self.root))
        self.assertIn(".claude/skills/card-evals/SKILL.md", source.files(self.root))

    def test_source_symlink_and_missing_tracked_source_fail(self):
        path = self.root / "README.md"
        path.unlink()
        path.symlink_to(Path(self.tmp.name) / "missing")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            source.copy(self.root, Path(self.tmp.name) / "copy")
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            source.copy(self.root, Path(self.tmp.name) / "other")

    def test_tracked_symlink_inside_local_root_is_rejected(self):
        path = self.root / ".agents/skills/escape"
        path.parent.mkdir(parents=True)
        path.symlink_to(Path(self.tmp.name), target_is_directory=True)
        self.git("add", ".agents/skills/escape")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            source.copy(self.root, Path(self.tmp.name) / "copy")

    def test_no_git_does_not_hide_source(self):
        import shutil
        shutil.rmtree(self.root / ".git")
        self.write(".agents/skills/unknown/SKILL.md", "source")
        with self.assertRaisesRegex(ValueError, "Unclassified local material"):
            source.files(self.root)

    def test_generated_cleanup_does_not_own_local_agents_skills(self):
        self.write(".agents/skills/local/SKILL.md", "preserve")
        self.write(".agents/plugins/stale.json", "stale")
        self.assertEqual(build.stale_files(self.root, {}), [".agents/plugins/stale.json"])

    def test_parent_symlink_even_inside_root_is_rejected(self):
        self.write("real/file.md", "source")
        (self.root / "link").symlink_to(self.root / "real", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            config.safe_path(self.root, "link/file.md")

    def test_absolute_and_traversal_paths_are_rejected(self):
        for name in ("../outside", "/tmp/outside", "docs/../README.md"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe source path"):
                config.safe_path(self.root, name)
