# SPDX-License-Identifier: Apache-2.0
import re
from zipfile import ZipFile

from test_pack import FixtureCase
from packlib import adapter, build, check, config, manifest

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def split(text):
    """Return (frontmatter dict, body) for a generated agent file."""
    _, front, body = text.split("---\n", 2)
    return dict(line.split(": ", 1) for line in front.strip().splitlines()), body


class AdapterTests(FixtureCase):
    def agents(self):
        folder = self.root / config.ADAPTER_AGENTS
        return {path.name: path.read_text(encoding="utf-8") for path in sorted(folder.glob("*.md"))}

    def test_one_valid_read_only_agent_per_card(self):
        files = self.agents()
        self.assertEqual(len(files), 124)
        for name, text in files.items():
            front, _ = split(text)
            self.assertEqual(front["name"] + ".md", name)
            self.assertRegex(front["name"], NAME)
            self.assertEqual(front["tools"], "Read, Grep, Glob", name)
            self.assertEqual(front["model"], "inherit")
            self.assertTrue(front["description"].startswith('"Materials-only specialist. '), name)
            self.assertNotIn("proactively", front["description"].lower())

    def test_agent_body_embeds_card_and_boundaries(self):
        families = manifest.load(self.root)
        files = self.agents()
        for family in families:
            for role in family["roles"]:
                _, body = split(files[adapter.agent_name(role) + ".md"])
                card = (self.root / role["path"]).read_text(encoding="utf-8").rstrip() + "\n"
                self.assertTrue(body.endswith("\n---\n\n" + card), role["id"])
                self.assertIn("## Boundaries", body)
                self.assertEqual("## Sensitive domains" in body, family["sensitive"], role["id"])
                if family["sensitive"]:
                    self.assertIn("**Safeguards:**", body)

    def test_generation_is_deterministic(self):
        before = self.agents()
        build.build(self.root)
        self.assertEqual(before, self.agents())

    def test_tampered_agent_fails_check(self):
        self.edit("adapters/claude-code/agents/security-threat-modeler.md",
                  lambda text: text.replace("Read, Grep, Glob", "Read, Grep, Glob, Bash"))
        self.assertFails("security-threat-modeler.md differs from sources")

    def test_card_edit_makes_agent_stale_and_build_fixes_it(self):
        self.edit("catalog/software-engineering/code-reviewer.md", lambda text: text.replace("clarity", "clarity and tone", 1))
        self.assertFails("software-engineering-code-reviewer.md differs from sources")
        build.build(self.root)
        check.check(self.root)

    def test_unknown_agent_file_is_stale(self):
        (self.root / config.ADAPTER_AGENTS / "ghost-role.md").write_text("x")
        self.assertFails("ghost-role.md: stale generated file")
        build.build(self.root)
        self.assertFalse((self.root / config.ADAPTER_AGENTS / "ghost-role.md").exists())

    def test_missing_agent_file_fails(self):
        (self.root / config.ADAPTER_AGENTS / "core-copywriter.md").unlink()
        self.assertFails("core-copywriter.md is missing")

    def test_coordinator_without_boundaries_fails_build(self):
        self.edit("pack/FAMILY-COORDINATOR.md", lambda text: text.replace("## Boundaries", "## Limits"))
        with self.assertRaisesRegex(ValueError, "no Boundaries section"):
            build.outputs(self.root)

    def test_release_archive_excludes_adapter(self):
        with ZipFile(self.release()) as bundled:
            names = bundled.namelist()
        self.assertFalse([name for name in names if "adapters/" in name or "/evals/" in name or ".claude/" in name])
