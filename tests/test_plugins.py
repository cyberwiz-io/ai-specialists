# SPDX-License-Identifier: Apache-2.0
import json
import re
from zipfile import ZipFile

from test_pack import FixtureCase
from packlib import adapter, build, cards, check, config, manifest, plugin

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def split(text):
    """Return (frontmatter dict, body) for a generated agent or skill file."""
    _, front, body = text.split("---\n", 2)
    return dict(line.split(": ", 1) for line in front.strip().splitlines()), body


class PluginTests(FixtureCase):
    def agents(self):
        return {path.name: path.read_text(encoding="utf-8")
                for path in sorted((self.root / config.PLUGINS_DIR).glob("*/agents/*.md"))}

    def specialists(self):
        return {name: text for name, text in self.agents().items() if not name.endswith("-orchestrator.md")}

    def test_one_valid_delegating_agent_per_card(self):
        files = self.specialists()
        self.assertEqual(len(files), 124)
        roles = {adapter.agent_name(role) + ".md": role for family in manifest.load(self.root) for role in family["roles"]}
        for name, text in files.items():
            front, body = split(text)
            self.assertEqual(front["name"] + ".md", name)
            self.assertRegex(front["name"], NAME)
            expected = adapter.COMMAND_TOOLS if roles[name]["commands"] else "Read, Grep, Glob, Agent"
            self.assertEqual(front["tools"], expected, name)
            self.assertEqual(front["model"], roles[name]["model"], name)
            self.assertNotIn("proactively", front["description"].lower())
            self.assertLessEqual(len(json.loads(front["description"])), 150, name)
            self.assertIn("Never delegate to a general-purpose agent", body, name)

    def test_only_the_named_roles_run_commands_and_only_from_the_allowlist(self):
        runners = {role["id"] for family in manifest.load(self.root) for role in family["roles"] if role["commands"]}
        self.assertEqual(runners, {"software-engineering/code-reviewer", "software-engineering/debugging-analyst"})
        for pattern in adapter.COMMAND_PATTERNS:
            self.assertRegex(pattern, r"^[a-z0-9 -]+:\*$|^python3 -m [a-z]+:\*$")
        tools = adapter.COMMAND_TOOLS.split(", ")
        self.assertEqual([tool for tool in tools if tool.startswith("Bash") and not tool.endswith(":*)")], [])
        self.assertFalse({"Edit", "Write", "WebFetch", "Bash"} & set(tools))

    def test_writing_roles_run_on_a_cheaper_model_and_judgment_roles_inherit(self):
        models = {role["id"]: role["model"] for family in manifest.load(self.root) for role in family["roles"]}
        self.assertEqual(models["marketing-growth/copywriter"], "sonnet")
        self.assertEqual(models["software-engineering/technical-writer"], "sonnet")
        for role_id in ("software-engineering/code-reviewer", "security/threat-modeler", "finance/model-reviewer",
                        "legal-compliance/contract-reader", "people-hr/review-drafter"):
            self.assertEqual(models[role_id], "inherit", role_id)
        for family in manifest.load(self.root):
            front, _ = split(self.agents()[adapter.orchestrator_name(family) + ".md"])
            self.assertEqual(front["model"], "inherit", family["id"])

    def test_bad_model_or_commands_value_fails_the_manifest(self):
        self.edit("catalog/families.json", lambda text: text.replace(
            '"commands": true', '"commands": "yes"', 1))
        with self.assertRaisesRegex(ValueError, "commands must be true or false"):
            manifest.load(self.root)
        self.edit("catalog/families.json", lambda text: text.replace(
            '"commands": "yes"', '"model": "gpt"', 1))
        with self.assertRaisesRegex(ValueError, "model must be one of"):
            manifest.load(self.root)

    def test_every_family_has_an_orchestrator_that_can_only_call_its_roster(self):
        files = self.agents()
        for family in manifest.load(self.root):
            front, body = split(files[adapter.orchestrator_name(family) + ".md"])
            self.assertEqual(front["name"], adapter.orchestrator_name(family))
            self.assertRegex(front["name"], NAME)
            allowed = ", ".join(adapter.agent_type(role) for role in family["roles"])
            self.assertEqual(front["tools"], f"Agent({allowed}), Read, Grep, Glob", family["id"])
            self.assertLessEqual(len(json.loads(front["description"])), 150, family["id"])
            for role in family["roles"]:
                self.assertIn(f"`{adapter.agent_type(role)}`", body)
            self.assertIn("## Boundaries", body)
            self.assertIn("## Sensitive domains" if family["id"] != "marketing-growth" else "## Start small", body)

    def test_agent_types_carry_the_plugin_prefix_the_agent_tool_needs(self):
        role = manifest.load(self.root)[0]["roles"][0]
        self.assertEqual(adapter.agent_type(role), f"{role['family']}:{role['family']}-{role['slug']}")

    def test_orchestrator_name_collision_fails_build(self):
        family = manifest.load(self.root)[0]
        clash = dict(family["roles"][0], slug="orchestrator", id=family["id"] + "/orchestrator")
        with self.assertRaisesRegex(ValueError, "collides with the orchestrator"):
            adapter.outputs(self.root, [dict(family, roles=[clash])])

    def test_agent_preamble_is_short_and_keeps_the_hard_rules(self):
        files = self.agents()
        for family in manifest.load(self.root):
            for role in family["roles"]:
                _, body = split(files[adapter.agent_name(role) + ".md"])
                preamble = body.split("\n---\n\n", 1)[0]
                self.assertLessEqual(len(preamble.encode()), 2500 if family["sensitive"] else 1200, role["id"])
                run = "cannot run other commands" if role["commands"] else "cannot run commands"
                for phrase in ("read-only", run, "no path to do it", "task data",
                               "Never request credentials or secrets", "Name the specialists you consulted"):
                    self.assertIn(phrase, preamble, role["id"])
                if family["sensitive"]:
                    for phrase in ("Pressure", "No specifics from memory", "Right to share", "Empty is not safe",
                                   "Live matters", "Standing header"):
                        self.assertIn(phrase, preamble, role["id"])

    def test_brief_cuts_at_a_clause_and_keeps_short_sentences(self):
        short = "# R\n\nID: a/b. Version: 1.0.\n\n**Use for:** writing a memo. Not a letter.\n"
        self.assertEqual(cards.brief(short), "Writing a memo.")
        long = ("# R\n\nID: a/b. Version: 1.0.\n\n**Use for:** planning a launch for one product: audiences, channels, "
                "messages, timing, owners and the measures that show whether it worked. Not ads.\n")
        self.assertEqual(cards.brief(long), "Planning a launch for one product.")

    def test_agent_body_ends_with_the_card(self):
        files = self.agents()
        for family in manifest.load(self.root):
            for role in family["roles"]:
                _, body = split(files[adapter.agent_name(role) + ".md"])
                card = (self.root / role["path"]).read_text(encoding="utf-8").rstrip() + "\n"
                self.assertTrue(body.endswith("\n---\n\n" + card), role["id"])
                self.assertEqual("## Sensitive domain" in body, family["sensitive"], role["id"])
                if family["sensitive"]:
                    self.assertIn("**Safeguards:**", body)

    def test_agents_live_in_their_family_plugin(self):
        for family in manifest.load(self.root):
            found = {path.name for path in (self.root / plugin.plugin_dir(family) / "agents").glob("*.md")}
            self.assertEqual(found, {adapter.agent_name(role) + ".md" for role in family["roles"]}
                             | {adapter.orchestrator_name(family) + ".md"})

    def test_marketplace_lists_every_family_plugin(self):
        market = json.loads((self.root / config.MARKETPLACE).read_text())
        families = manifest.load(self.root)
        self.assertEqual([entry["name"] for entry in market["plugins"]], [f["id"] for f in families])
        for entry in market["plugins"]:
            self.assertEqual(entry["source"], "./plugins/" + entry["name"])
            manifest_file = self.root / "plugins" / entry["name"] / ".claude-plugin" / "plugin.json"
            self.assertEqual(json.loads(manifest_file.read_text())["name"], entry["name"])
            self.assertRegex(entry["version"], r"^\d+\.\d+\.\d+$")

    def test_skill_has_valid_frontmatter_and_card_references(self):
        for family in manifest.load(self.root):
            folder = self.root / plugin.skill_dir(family)
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            front, body = split(text)
            self.assertEqual(front["name"], family["id"])
            self.assertEqual(front["allowed-tools"], "Read Grep Glob")
            self.assertLessEqual(len(json.loads(front["description"])), 1024)
            self.assertIn("Materials only", front["description"])
            self.assertIn("# Family coordinator" if family["id"] != "marketing-growth" else "Coordinator", body)
            for role in family["roles"]:
                card = (self.root / role["path"]).read_bytes()
                self.assertEqual((folder / "references" / (role["slug"] + ".md")).read_bytes(), card)
                self.assertIn(f"(references/{role['slug']}.md)", body)

    def test_marketing_skill_carries_its_workflow(self):
        folder = self.root / "plugins" / "marketing-growth" / "skills" / "marketing-growth" / "references"
        for name in ("MARKETING-WORKFLOW.md", "CUSTOM-SPECIALISTS.md", "BUSINESS-PROFILE.md"):
            self.assertTrue((folder / name).is_file(), name)

    def test_generation_is_deterministic(self):
        before = self.agents()
        build.build(self.root)
        self.assertEqual(before, self.agents())

    def test_tampered_agent_fails_check(self):
        self.edit("plugins/security/agents/security-threat-modeler.md",
                  lambda text: text.replace("Read, Grep, Glob", "Read, Grep, Glob, Bash"))
        self.assertFails("security-threat-modeler.md differs from sources")

    def test_card_edit_makes_every_copy_stale_and_build_fixes_it(self):
        self.edit("catalog/software-engineering/code-reviewer.md", lambda text: text.replace("clarity", "clarity and tone", 1))
        self.assertFails("software-engineering-code-reviewer.md differs from sources")
        self.assertFails("references/code-reviewer.md differs from sources")
        build.build(self.root)
        check.check(self.root)

    def test_unknown_plugin_file_is_stale_and_build_removes_it(self):
        ghost = self.root / config.PLUGINS_DIR / "ghost" / "agents" / "ghost-role.md"
        ghost.parent.mkdir(parents=True)
        ghost.write_text("x")
        self.assertFails("ghost-role.md: stale generated file")
        build.build(self.root)
        self.assertFalse(ghost.parent.parent.exists())

    def test_missing_plugin_file_fails(self):
        (self.root / "plugins/marketing-growth/agents/marketing-growth-copywriter.md").unlink()
        self.assertFails("marketing-growth-copywriter.md is missing")

    def test_missing_orchestrator_fails(self):
        (self.root / "plugins/finance/agents/finance-orchestrator.md").unlink()
        self.assertFails("finance-orchestrator.md is missing")

    def test_orchestrator_with_extra_tool_fails_check(self):
        self.edit("plugins/finance/agents/finance-orchestrator.md",
                  lambda text: text.replace("Read, Grep, Glob\n", "Read, Grep, Glob, Bash\n", 1))
        self.assertFails("finance-orchestrator.md differs from sources")

    def test_missing_marketplace_fails(self):
        (self.root / config.MARKETPLACE).unlink()
        self.assertFails("marketplace.json is missing")

    def test_oversized_description_fails_build(self):
        self.edit("catalog/families.json", lambda text: text.replace(
            '"purpose": "Defensive security planning', '"purpose": "' + "x" * 1100 + ' Defensive security planning', 1))
        with self.assertRaisesRegex(ValueError, "skill description is"):
            build.outputs(self.root)

    def test_install_guide_must_list_every_family(self):
        self.edit("docs/INSTALL.md", lambda text: text.replace("`orchestration`", "`other`"))
        self.assertFails("does not list plugin orchestration")

    def test_coordinator_without_boundaries_fails_build(self):
        self.edit("pack/FAMILY-COORDINATOR.md", lambda text: text.replace("## Boundaries", "## Limits"))
        with self.assertRaisesRegex(ValueError, "no Boundaries section"):
            build.outputs(self.root)

    def test_release_includes_plugins_and_skill_zips_but_not_maintainer_files(self):
        with ZipFile(self.release()) as bundled:
            names = bundled.namelist()
        self.assertTrue([n for n in names if n.endswith(".claude-plugin/marketplace.json")])
        self.assertTrue([n for n in names if "/plugins/security/skills/security/SKILL.md" in n])
        self.assertFalse([n for n in names if "/evals/" in n or "/.claude/" in n or "adapters/" in n])
        self.assertTrue([n for n in names if n.endswith("docs/INSTALL.md")])

    def test_skill_zip_holds_one_skill_folder(self):
        archive = self.release()
        families = manifest.load(self.root)
        self.assertEqual(len(list(archive.parent.glob("*-skill-*.zip"))), len(families))
        zipped = archive.parent / plugin.skill_archive_name(self.root, next(f for f in families if f["id"] == "finance"))
        with ZipFile(zipped) as bundled:
            names = bundled.namelist()
        self.assertIn("finance/SKILL.md", names)
        self.assertTrue(all(name.startswith("finance/") for name in names))
        self.assertEqual(len([n for n in names if "/references/" in n]), 8)
