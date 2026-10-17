# SPDX-License-Identifier: Apache-2.0
import json
import re

from test_pack import FixtureCase
from packlib import build, codex, config, copilot, cursor, gemini, manifest, plugin_evals, skills, stats
import pack as pack_cli

try:
    import tomllib
except ImportError:  # Python before 3.11
    tomllib = None


class SkillTests(FixtureCase):
    def test_every_card_has_a_spec_only_root_skill_with_a_short_description(self):
        families = manifest.load(self.root)
        folders = {path.parent.name for path in (self.root / config.SKILLS_DIR).glob("*/SKILL.md")}
        expected = {skills.role_name(role) for family in families for role in family["roles"]}
        expected |= {skills.lead_name(family) for family in families} | {skills.SPECIALISTS}
        self.assertEqual(folders, expected)
        for name in folders:
            text = (self.root / config.SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertEqual(skills.problems(name, text, name), [], name)
            front, body = skills.parse_frontmatter(text)
            self.assertEqual(set(front) - set(skills.SPEC_FIELDS), set(), name)
            self.assertLessEqual(len(front["description"]), skills.LEAD_DESCRIPTION_MAX, name)
            self.assertIn("Boundaries: materials only", body)

    def test_role_skill_description_starts_from_the_use_for_line(self):
        role = next(r for f in manifest.load(self.root) for r in f["roles"] if r["id"] == "security/threat-modeler")
        text = skills.card_text(self.root, role)
        found = skills.description(role, text)
        self.assertTrue(found.startswith("Threat modeler. Use for listing how a described system"))
        self.assertLessEqual(len(found), skills.DESCRIPTION_TARGET + 20)

    def test_skill_name_rules(self):
        good = (self.root / "skills/security-threat-modeler/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(skills.problems("x", good, "security-threat-modeler"), [])
        cases = ((good, "other-folder", "does not match its folder"),
                 (good.replace("name: security-threat-modeler", "name: Security_Threat"), "Security_Threat", "lowercase"),
                 (good.replace("name: security-threat-modeler", "name: " + "a" * 65), "a" * 65, "1-64"),
                 (good.replace("allowed-tools: Read Grep Glob", "allowed-tools: Grep"), "security-threat-modeler",
                  "allowed-tools must include Read"),
                 (good.replace("license: CC-BY-4.0", "license: CC-BY-4.0\nmodel: opus"), "security-threat-modeler",
                  "outside the Agent Skills spec"),
                 (re.sub(r'description: ".*?"\n', 'description: "' + "x" * 1100 + '"\n', good), "security-threat-modeler",
                  "description must be"))
        for text, folder, message in cases:
            self.assertTrue([f for f in skills.problems("x", text, folder) if message in f], message)

    def test_lead_without_references_links_no_cards(self):
        families = manifest.load(self.root)
        family = families[0]
        body = skills.lead_body(self.root, family, families, references=False)
        self.assertNotIn("](references/", body)
        self.assertIn(skills.lead_name(family), body)


class HostTests(FixtureCase):
    def outputs(self):
        return build.outputs(self.root)

    def test_every_host_adapter_passes_its_own_checks(self):
        families, generated = self.outputs()
        for host in build.HOSTS:
            self.assertEqual(host.problems(self.root, families, generated), [], host.__name__)

    def test_codex_plugin_carries_leads_and_parseable_agents(self):
        families, generated = self.outputs()
        meta = json.loads(generated["adapters/codex/.codex-plugin/plugin.json"])
        self.assertEqual(meta["skills"], "./skills/")
        market = json.loads(generated[".agents/plugins/marketplace.json"])
        self.assertEqual(market["plugins"][0]["source"]["path"], "./adapters/codex")
        agents = [name for name in generated if name.startswith("adapters/codex/agents/")]
        self.assertEqual(len(agents), 124 + len(families) + 1)
        if tomllib:
            data = tomllib.loads(generated["adapters/codex/agents/security-threat-modeler.toml"].decode())
            self.assertEqual(data["name"], "security-threat-modeler")
            self.assertEqual(data["features"]["shell_tool"], False)
            self.assertNotIn("model", data)
            self.assertIn("# Threat modeler", data["developer_instructions"])

    def test_codex_agent_with_sandbox_mode_fails(self):
        families, generated = self.outputs()
        name = "adapters/codex/agents/security-threat-modeler.toml"
        generated[name] = generated[name].replace(b"\n[features]", b'\nsandbox_mode = "danger-full-access"\n[features]', 1)
        self.assertTrue(codex.problems(self.root, families, generated))

    def test_copilot_roles_are_read_only_and_leads_can_call_agents(self):
        families, generated = self.outputs()
        role = skills.parse_frontmatter(generated["adapters/copilot/agents/security-threat-modeler.agent.md"].decode())[0]
        lead = skills.parse_frontmatter(generated["adapters/copilot/agents/security-lead.agent.md"].decode())[0]
        self.assertNotIn("agent", json.dumps(role.get("tools")))
        self.assertIn("agent", json.dumps(lead.get("tools")))
        name = "adapters/copilot/agents/security-threat-modeler.agent.md"
        generated[name] = generated[name].replace(b'"search"', b'"search", "edit"', 1)
        self.assertTrue(copilot.problems(self.root, families, generated))

    def test_gemini_and_cursor_manifests(self):
        families, generated = self.outputs()
        extension = json.loads(generated["gemini-extension.json"])
        self.assertEqual(extension["name"], "ai-specialists")
        self.assertNotIn("contextFileName", extension)
        market = json.loads(generated[".cursor-plugin/marketplace.json"])
        self.assertEqual([entry["name"] for entry in market["plugins"]], [family["id"] for family in families])
        generated["gemini-extension.json"] = b'{"name": "Bad Name"}'
        self.assertTrue(gemini.problems(self.root, families, generated))
        del generated["plugins/security/.cursor-plugin/plugin.json"]
        self.assertTrue(cursor.problems(self.root, families, generated))


class StatsAndEvalTests(FixtureCase):
    def test_stats_reports_every_plugin_and_skips_hidden_skills(self):
        found = {row["output"]: row for row in stats.rows(self.root)}
        self.assertIn("plugin security", found)
        self.assertIn("bundle ai-specialists-all", found)
        self.assertGreater(found["plugin security"]["demand"], found["plugin security"]["always"])
        self.assertLess(found["bundle ai-specialists-all"]["always"], found["skills/ (npx skills, Gemini)"]["always"])
        self.assertIn("| plugin security |", stats.table(list(found.values())))
        always, _, _ = stats.measure(self.root / "plugins/security/skills/security-threat-modeler/SKILL.md")
        self.assertEqual(always, 0)

    def test_stats_command_prints_a_table(self):
        from contextlib import redirect_stdout
        from io import StringIO
        out = StringIO()
        with redirect_stdout(out):
            pack_cli.main(["stats", "--root", str(self.root)])
        self.assertIn("| Output |", out.getvalue())

    def test_security_plugin_eval_suite_has_tasks_a_boundary_and_a_team_case(self):
        cases = sorted((self.root / "plugins/security/evals").glob("*/case.yaml"))
        self.assertEqual(len(cases), 7)
        kinds = [json.loads(path.read_text())["tags"][0] for path in cases]
        self.assertEqual(sorted(kinds), ["boundary"] + ["task"] * 5 + ["team"])
        team = json.loads((self.root / "plugins/security/evals/tutoring-app-launch/case.yaml").read_text())
        self.assertIn("tool_used", [grader["type"] for grader in team["graders"]])

    def test_eval_suite_naming_an_unknown_fixture_fails_build(self):
        self.edit("evals/plugin/security.json", lambda text: text.replace(
            "security/threat-modeler/library-lending-app", "security/threat-modeler/no-such-fixture"))
        with self.assertRaisesRegex(ValueError, "no-such-fixture is not a security fixture"):
            plugin_evals.outputs(self.root, manifest.load(self.root))
