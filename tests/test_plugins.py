# SPDX-License-Identifier: Apache-2.0
import json
import re
from zipfile import ZipFile

from test_pack import FixtureCase
from packlib import adapter, build, cards, check, config, manifest, plugin, skills

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def split(text):
    """Return (frontmatter dict, body) for a generated agent or skill file."""
    return skills.parse_frontmatter(text)


class PluginTests(FixtureCase):
    def agents(self, family=None):
        pattern = f"{family or '*'}/agents/*.md"
        return {path.relative_to(self.root / config.PLUGINS_DIR).as_posix(): path.read_text(encoding="utf-8")
                for path in sorted((self.root / config.PLUGINS_DIR).glob(pattern))}

    def roles(self):
        return {role["id"]: role for family in manifest.load(self.root) for role in family["roles"]}

    def test_one_read_only_worker_agent_per_card_that_cannot_start_agents(self):
        roles = {f"{role['family']}/agents/{adapter.agent_name(role)}.md": role for role in self.roles().values()}
        files = self.agents()
        self.assertEqual(set(roles) - set(files), set())
        for name, text in files.items():
            front, body = split(text)
            role = roles.get(name) or self.roles()["orchestration/cross-family-reviewer"]
            self.assertEqual(front["name"] + ".md", name.rsplit("/", 1)[-1])
            self.assertRegex(front["name"], NAME)
            self.assertEqual(front["tools"], "Read, Grep, Glob", name)
            self.assertNotIn("Agent", front["tools"].split(", "))
            self.assertEqual(front["disallowedTools"], "Agent", name)
            self.assertEqual(front["model"], role["model"], name)
            self.assertEqual(front.get("effort"), role["effort"], name)
            self.assertLessEqual(len(front["description"]), 150, name)
            self.assertIn("You cannot start agents", body, name)
            self.assertIn("Never ask for secrets", body, name)

    def test_shared_preamble_stays_short_and_keeps_its_rules(self):
        self.assertLessEqual(len(adapter.NOTE), 360)
        self.assertLessEqual(len(skills.BOUNDARY), 360)
        for phrase in ("Materials only", "never claim you did", "data, not instructions", "Never ask for secrets",
                       "Host rules come first"):
            self.assertIn(phrase, adapter.NOTE)
        for phrase in ("never publish", "never claim you did", "data, not instructions", "Never ask for secrets"):
            self.assertIn(phrase, skills.BOUNDARY)
        for phrase in ("not advice", "name who decides", "not supplied", "mask secrets", "not proof", "alert the responsible"):
            self.assertIn(phrase, skills.SENSITIVE)

    def test_models_follow_the_role_tier_and_effort_follows_the_model(self):
        roles = self.roles()
        self.assertEqual(roles["marketing-growth/copywriter"]["model"], "haiku")
        self.assertEqual(roles["marketing-growth/marketing-strategist"]["model"], "sonnet")
        for role_id in ("security/threat-modeler", "software-engineering/software-architect",
                        "software-engineering/code-reviewer", "orchestration/cross-family-reviewer"):
            self.assertEqual(roles[role_id]["model"], "opus", role_id)
        for role in roles.values():
            self.assertEqual(role["effort"], manifest.TIER_EFFORT[role["model"]], role["id"])
            if role["sensitive"]:
                self.assertNotEqual(role["model"], "haiku", role["id"])

    def test_bad_manifest_values_fail(self):
        for old, new, message in (('"model": "opus"', '"model": "opus", "commands": true', "unknown key commands"),
                                  ('"model": "opus"', '"model": "gpt"', "model must be one of"),
                                  ('"model": "opus"', '"model": "opus", "effort": "huge"', "effort must be one of"),
                                  ('"model": "opus"', '"model": "opus", "prefix": "core"', "unknown key prefix")):
            original = (self.root / "catalog/families.json").read_text()
            self.edit("catalog/families.json", lambda text: text.replace(old, new, 1))
            with self.assertRaisesRegex(ValueError, message):
                manifest.load(self.root)
            (self.root / "catalog/families.json").write_text(original)

    def test_agent_body_ends_with_the_card(self):
        files = self.agents()
        for role in self.roles().values():
            _, body = split(files[f"{role['family']}/agents/{adapter.agent_name(role)}.md"])
            card = (self.root / role["path"]).read_text(encoding="utf-8").rstrip() + "\n"
            self.assertTrue(body.endswith("\n---\n\n" + card), role["id"])
            self.assertEqual("Sensitive domain:" in body, role["sensitive"], role["id"])

    def test_every_family_plugin_has_its_lead_its_role_skills_and_the_reviewer(self):
        families = manifest.load(self.root)
        for family in families:
            base = self.root / plugin.plugin_dir(family)
            found = {path.name for path in (base / "agents").glob("*.md")}
            expected = {adapter.agent_name(role) + ".md" for role in family["roles"]}
            self.assertEqual(found, expected | {"orchestration-cross-family-reviewer.md"})
            self.assertFalse([name for name in found if name.endswith("-orchestrator.md")])
            lead = base / "skills" / skills.lead_name(family) / "SKILL.md"
            front, body = split(lead.read_text(encoding="utf-8"))
            self.assertEqual(front["name"], skills.lead_name(family))
            self.assertLessEqual(len(front["description"]), skills.LEAD_DESCRIPTION_MAX)
            self.assertEqual(set(front) - set(skills.SPEC_FIELDS), set())
            for phrase in ("orchestration-cross-family-reviewer", "handoff packet", "parallel",
                           "different actual model", "BLOCKED_REVIEW", "## Boundaries"):
                self.assertIn(phrase, body, family["id"])
            for role in family["roles"]:
                self.assertIn(f"`{adapter.agent_name(role)}`", body)
                card = (self.root / role["path"]).read_bytes()
                self.assertEqual((lead.parent / "references" / f"{role['slug']}.md").read_bytes(), card)
                front, _ = split((base / "skills" / skills.role_name(role) / "SKILL.md").read_text())
                self.assertEqual(front["disable-model-invocation"], "true")
            self.assertTrue((lead.parent / "references" / "cross-family-reviewer.md").is_file())

    def test_marketing_lead_carries_its_workflow(self):
        folder = self.root / "plugins/marketing-growth/skills/marketing-growth-lead/references"
        for name in ("MARKETING-WORKFLOW.md", "CUSTOM-SPECIALISTS.md", "BUSINESS-PROFILE.md"):
            self.assertTrue((folder / name).is_file(), name)

    def test_marketplace_lists_every_family_plugin_and_the_bundle(self):
        market = json.loads((self.root / config.MARKETPLACE).read_text())
        families = manifest.load(self.root)
        self.assertEqual([entry["name"] for entry in market["plugins"]], [f["id"] for f in families] + [plugin.BUNDLE])
        for entry in market["plugins"][:-1]:
            self.assertEqual(entry["source"], "./plugins/" + entry["name"])
            manifest_file = self.root / "plugins" / entry["name"] / ".claude-plugin" / "plugin.json"
            self.assertEqual(json.loads(manifest_file.read_text())["name"], entry["name"])
            self.assertRegex(entry["version"], r"^\d+\.\d+\.\d+$")
        bundle = market["plugins"][-1]
        self.assertEqual((bundle["source"], bundle["strict"]), ("./", False))
        self.assertEqual(len(bundle["agents"]), 124)
        self.assertEqual(len(bundle["skills"]), len(families) + 1)
        for path in bundle["agents"]:
            self.assertTrue((self.root / path).is_file(), path)

    def test_bundle_descriptions_stay_well_under_the_agent_warning(self):
        families, generated = check.check(self.root)
        self.assertLess(plugin.bundle_description_tokens(families, generated), plugin.BUNDLE_TOKEN_LIMIT)

    def test_bundle_entry_pointing_at_a_missing_agent_fails(self):
        families, generated = build.outputs(self.root)
        market = json.loads(generated[config.MARKETPLACE])
        market["plugins"][-1]["agents"].append("./plugins/ghost/agents/ghost.md")
        generated[config.MARKETPLACE] = json.dumps(market).encode()
        self.assertTrue([f for f in plugin.problems(self.root, families, generated) if "ghost.md does not exist" in f])

    def test_plugin_entry_without_a_folder_fails(self):
        families, generated = build.outputs(self.root)
        market = json.loads(generated[config.MARKETPLACE])
        market["plugins"][0]["source"] = "./plugins/nowhere"
        generated[config.MARKETPLACE] = json.dumps(market).encode()
        self.assertTrue([f for f in plugin.problems(self.root, families, generated) if "has no .claude-plugin" in f])

    def test_worker_with_the_agent_tool_fails(self):
        families, generated = build.outputs(self.root)
        name = "plugins/security/agents/security-threat-modeler.md"
        generated[name] = generated[name].replace(b"tools: Read, Grep, Glob\n", b"tools: Read, Grep, Glob, Agent\n")
        self.assertTrue([f for f in plugin.problems(self.root, families, generated) if "may not have the Agent tool" in f])
        generated[name] = generated[name].replace(b"disallowedTools: Agent\n", b"")
        self.assertTrue([f for f in plugin.problems(self.root, families, generated) if "must set disallowedTools" in f])

    def test_core_prefix_fails(self):
        families, generated = build.outputs(self.root)
        generated["plugins/marketing-growth/agents/core-copywriter.md"] = b"x"
        self.assertTrue([f for f in plugin.problems(self.root, families, generated) if "retired core- prefix" in f])

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
        self.assertFails("skills/software-engineering-code-reviewer/SKILL.md differs from sources")
        self.assertFails("references/code-reviewer.md differs from sources")
        build.build(self.root)
        check.check(self.root)

    def test_unknown_generated_files_are_stale_and_build_removes_them(self):
        ghosts = [self.root / config.PLUGINS_DIR / "ghost" / "agents" / "ghost-role.md",
                  self.root / config.SKILLS_DIR / "ghost-skill" / "SKILL.md",
                  self.root / config.ADAPTERS_DIR / "codex" / "agents" / "ghost.toml"]
        for ghost in ghosts:
            ghost.parent.mkdir(parents=True, exist_ok=True)
            ghost.write_text("x")
        self.assertFails("ghost-role.md: stale generated file")
        self.assertFails("ghost-skill/SKILL.md: stale generated file")
        self.assertFails("ghost.toml: stale generated file")
        build.build(self.root)
        self.assertFalse([ghost for ghost in ghosts if ghost.exists()])
        self.assertTrue((self.root / config.ADAPTERS_DIR / "codex" / "README.md").is_file())

    def test_missing_plugin_file_fails(self):
        (self.root / "plugins/marketing-growth/agents/marketing-growth-copywriter.md").unlink()
        self.assertFails("marketing-growth-copywriter.md is missing")

    def test_missing_marketplace_fails(self):
        (self.root / config.MARKETPLACE).unlink()
        self.assertFails("marketplace.json is missing")

    def test_oversized_lead_description_fails_build(self):
        self.edit("catalog/families.json", lambda text: text.replace(
            '"triggers": "', '"triggers": "' + "x" * 400, 1))
        with self.assertRaisesRegex(ValueError, "lead description is"):
            build.outputs(self.root)

    def test_install_guide_must_list_every_family(self):
        self.edit("docs/INSTALL.md", lambda text: text.replace("`orchestration`", "`other`"))
        self.assertFails("does not list plugin orchestration")

    def test_coordinator_without_boundaries_fails_build(self):
        self.edit("pack/FAMILY-COORDINATOR.md", lambda text: text.replace("## Boundaries", "## Limits"))
        with self.assertRaisesRegex(ValueError, "no Boundaries section"):
            build.outputs(self.root)

    def test_release_includes_every_install_path_but_not_maintainer_files(self):
        with ZipFile(self.release()) as bundled:
            names = bundled.namelist()
        for wanted in (".claude-plugin/marketplace.json", "/plugins/security/skills/security-lead/SKILL.md",
                       "/skills/security-threat-modeler/SKILL.md", "/adapters/codex/.codex-plugin/plugin.json",
                       "/gemini-extension.json", "docs/INSTALL.md"):
            self.assertTrue([n for n in names if n.endswith(wanted)], wanted)
        self.assertFalse([n for n in names if "/evals/fixtures/" in n or "/.claude/" in n])

    def test_skill_zip_holds_one_lead_folder(self):
        archive = self.release()
        families = manifest.load(self.root)
        self.assertEqual(len(list(archive.parent.glob("*-skill-*.zip"))), len(families))
        zipped = archive.parent / plugin.skill_archive_name(self.root, next(f for f in families if f["id"] == "finance"))
        with ZipFile(zipped) as bundled:
            names = bundled.namelist()
        self.assertIn("finance-lead/SKILL.md", names)
        self.assertTrue(all(name.startswith("finance-lead/") for name in names))
        self.assertEqual(len([n for n in names if "/references/" in n]), 9)


class ReleaseWorkerTests(FixtureCase):
    agents = PluginTests.agents
    def test_all_workers_have_exact_inspection_tools(self):
        for name, text in self.agents().items():
            self.assertEqual(split(text)[0]["tools"], "Read, Grep, Glob", name)

    def test_worker_checker_rejects_any_extra_tool(self):
        name, text = next(iter(self.agents().items()))
        for tool in ("Bash(git status:*)", "Skill", "mcp__example__read", "NotebookEdit"):
            changed = text.replace("tools: Read, Grep, Glob", "tools: Read, Grep, Glob, " + tool)
            self.assertTrue(plugin.agent_problems(name, changed), tool)
