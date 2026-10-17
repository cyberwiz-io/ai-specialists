# SPDX-License-Identifier: Apache-2.0
import json
import sys
from unittest import mock

from test_pack import FixtureCase
import evals as evals_cli
from packlib import config, evals, manifest

SCENARIOS = "evals/scenarios"


class EvalTests(FixtureCase):
    def scenario_path(self, name):
        return self.root / SCENARIOS / f"{name}.json"

    def change_scenario(self, name, change):
        path = self.scenario_path(name)
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def cli(self, *argv):
        with mock.patch.object(config, "ROOT", self.root):
            return evals_cli.main(list(argv))

    def assertCliFails(self, pattern, *argv):
        with mock.patch.object(sys, "stderr") as err:
            with self.assertRaises(SystemExit) as raised:
                self.cli(*argv)
        self.assertEqual(raised.exception.code, 1)
        self.assertRegex("".join(call.args[0] for call in err.write.call_args_list), pattern)

    def test_shipped_scenarios_load_and_selfcheck(self):
        scenarios = evals.load(self.root)
        self.assertGreaterEqual(len(scenarios), 6)
        self.assertEqual(evals.selfcheck(scenarios), len(scenarios))
        families = manifest.load(self.root)
        for sid, scenario in scenarios.items():
            self.assertTrue([r for r in manifest.roles(families) if evals.applies(scenario, r)], sid)

    def test_good_sample_passes_and_bad_sample_fails(self):
        scenario = evals.load(self.root)["request-to-publish"]
        self.assertEqual(evals.grade(scenario, scenario["samples"]["good"]), [])
        failures = evals.grade(scenario, scenario["samples"]["bad"])
        self.assertTrue(any("never claims an external action" in f for f in failures), failures)

    def test_selfcheck_catches_a_rule_that_cannot_fail(self):
        self.change_scenario("request-to-publish", lambda d: d["samples"].update(bad=d["samples"]["good"]))
        with self.assertRaisesRegex(ValueError, "request-to-publish: bad sample passes every rule"):
            evals.selfcheck(evals.load(self.root))

    def test_selfcheck_catches_a_rule_that_rejects_good_answers(self):
        self.change_scenario("request-to-publish", lambda d: d["samples"].update(good=d["samples"]["bad"]))
        with self.assertRaisesRegex(ValueError, "good sample fails"):
            evals.selfcheck(evals.load(self.root))

    def test_sensitive_scenario_applies_only_to_sensitive_roles(self):
        families = manifest.load(self.root)
        scenario = evals.load(self.root)["sensitive-final-decision"]
        self.assertTrue(evals.applies(scenario, evals.find_role(families, "security/threat-modeler")))
        self.assertFalse(evals.applies(scenario, evals.find_role(families, "software-engineering/code-reviewer")))

    def test_invalid_scenarios_fail_cleanly(self):
        cases = {
            "graders": (lambda d: d.update(graders=[]), "at least one grader"),
            "applies_to": (lambda d: d.update(applies_to=[]), "applies_to"),
            "pattern": (lambda d: d["graders"][0].update(must_match_any=["("]), "bad pattern"),
            "why": (lambda d: d["graders"][0].pop("why"), "plus why"),
            "samples": (lambda d: d.pop("samples"), "good and bad sample"),
            "id": (lambda d: d.update(id="other"), "file name must match"),
        }
        for label, (change, pattern) in cases.items():
            with self.subTest(label):
                path = self.scenario_path("missing-inputs")
                original = path.read_text()
                self.change_scenario("missing-inputs", change)
                with self.assertRaisesRegex(ValueError, pattern):
                    evals.load(self.root)
                path.write_text(original)

    def test_invalid_json_and_empty_folder_fail(self):
        self.scenario_path("missing-inputs").write_text("{")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            evals.load(self.root)
        for path in (self.root / SCENARIOS).glob("*.json"):
            path.unlink()
        with self.assertRaisesRegex(ValueError, "no scenarios found"):
            evals.load(self.root)

    def test_prompt_uses_the_adapter_text_without_frontmatter(self):
        families = manifest.load(self.root)
        role = evals.find_role(families, "security/threat-modeler")
        text = evals.prompt(self.root, families, role, evals.load(self.root)["sensitive-final-decision"])
        self.assertTrue(text.startswith("<!-- Generated from catalog/security/threat-modeler.md"))
        self.assertIn("# Threat modeler", text)
        self.assertIn("=== USER REQUEST ===", text)
        self.assertNotIn("tools: Read", text)

    def test_cli_grades_a_saved_response(self):
        scenarios = evals.load(self.root)
        folder = self.root / "work"
        folder.mkdir()
        good, bad = folder / "good.md", folder / "bad.md"
        good.write_text(scenarios["request-to-publish"]["samples"]["good"])
        bad.write_text(scenarios["request-to-publish"]["samples"]["bad"])
        self.cli("grade", "core/copywriter", "request-to-publish", str(good))
        self.assertCliFails("never claims an external action", "grade", "core/copywriter", "request-to-publish", str(bad))

    def test_cli_rejects_bad_input(self):
        self.assertCliFails("unknown role", "list", "nope/nothing")
        self.assertCliFails("unknown scenario", "prompt", "core/copywriter", "nope")
        self.assertCliFails("does not apply", "prompt", "software-engineering/code-reviewer", "sensitive-final-decision")
        self.assertCliFails("response file not found", "grade", "core/copywriter", "request-to-publish", "work/none.md")
        self.cli("selfcheck")
