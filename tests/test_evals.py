# SPDX-License-Identifier: Apache-2.0
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import evals as evals_cli  # noqa: E402
from packlib import build, check, evals, manifest  # noqa: E402
from test_pack import FixtureCase  # noqa: E402

ROLE = "security/access-review-analyst"


class FixtureFileTests(FixtureCase):
    def test_frozen_heldout_bytes_cannot_change(self):
        path = self.root / "evals/heldout/release.json"
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertFails("frozen held-out")

    def change(self, family, change):
        path = self.root / evals.FIXTURE_DIR / f"{family}.json"
        data = json.loads(path.read_text())
        change(data["fixtures"])
        path.write_text(json.dumps(data))

    def first(self, family="security", role=ROLE):
        def apply(fixtures):
            return next(f for f in fixtures if f["role"] == role and f["kind"] == "task")
        return apply

    def edit_first(self, change, family="security", role=ROLE):
        self.change(family, lambda fixtures: change(self.first(family, role)(fixtures)))

    def test_every_card_has_a_task_and_every_family_a_boundary(self):
        families = manifest.load(self.root)
        fixtures = evals.load(self.root, families)
        tasks = {f["role"] for f in fixtures if f["kind"] == "task"}
        self.assertEqual(tasks, {role["id"] for role in manifest.roles(families)})
        self.assertEqual({f["family"]["id"] for f in fixtures if f["kind"] == "boundary"},
                         {family["id"] for family in families})

    def test_role_without_task_fixture_fails(self):
        self.change("security", lambda fixtures: fixtures.remove(self.first()(fixtures)))
        self.assertFails(f"no task fixture for {ROLE}")

    def test_family_without_boundary_fixture_fails(self):
        self.change("finance", lambda fixtures: [f.update(kind="task") for f in fixtures])
        self.assertFails("finance.json: needs at least one boundary fixture")

    def test_missing_fixture_file_fails(self):
        (self.root / evals.FIXTURE_DIR / "ai-ml.json").unlink()
        self.assertFails("ai-ml.json: fixture file is missing")

    def test_unknown_family_file_fails(self):
        (self.root / evals.FIXTURE_DIR / "astrology.json").write_text("{}")
        self.assertFails("astrology.json: not a manifest family")

    def test_unknown_role_fails(self):
        self.edit_first(lambda f: f.update(role="security/nobody", id="security/nobody/x"))
        self.assertFails("role security/nobody is not in family security")

    def test_duplicate_id_fails(self):
        self.change("security", lambda fixtures: fixtures.append(dict(self.first()(fixtures))))
        self.assertFails("duplicate fixture id")

    def test_id_must_extend_role(self):
        self.edit_first(lambda f: f.update(id="security/threat-modeler/x"))
        self.assertFails("id must be the role id, a slash and a slug")

    def test_bad_kind_and_empty_traits_fail(self):
        self.edit_first(lambda f: f.update(kind="smoke", traits=[]))
        self.assertFails("kind must be one of task, boundary")
        self.assertFails("traits needs at least one item")

    def test_missing_field_fails(self):
        self.edit_first(lambda f: f.pop("must_not"))
        self.assertFails("missing must_not")

    def test_invalid_json_fails(self):
        (self.root / evals.FIXTURE_DIR / "ai-ml.json").write_text("{")
        self.assertFails("ai-ml.json: invalid JSON")

    def test_real_looking_email_fails_and_example_passes(self):
        self.edit_first(lambda f: f["input"].append("owner: dana@harborlane.com"))
        self.assertFails("email domain harborlane.com is not an example domain")
        self.edit_first(lambda f: f["input"].__setitem__(-1, "owner: dana@harborlane.example"))
        build.build(self.root)
        check.check(self.root)

    def test_real_web_address_fails(self):
        self.edit_first(lambda f: f["input"].append("see https://www.realcompany.io/pricing"))
        self.assertFails("web address domain www.realcompany.io is not an example domain")

    def test_secret_like_string_fails_and_placeholder_passes(self):
        self.edit_first(lambda f: f["input"].append("api_key = abc123"))
        self.assertFails("secret-like string")
        self.edit_first(lambda f: f["input"].__setitem__(-1, "api_key = <REDACTED>"))
        build.build(self.root)
        check.check(self.root)

    def test_named_standard_fails(self):
        self.edit_first(lambda f: f["traits"].append("Maps findings to NIST controls"))
        self.assertFails("names a standard or regulation")


class RunTests(FixtureCase):
    def test_prepared_prompt_hashes_survive_platform_text_translation(self):
        from unittest import mock
        families, generated = check.check(self.root)
        fixture = evals.load(self.root, families)[0]
        original = Path.write_text
        def translated(path, text, *args, **kwargs):
            return original(path, text.replace("\n", "\r\n"), *args, **kwargs)
        with mock.patch.object(Path, "write_text", translated):
            folder = evals.prepare(self.root, families, generated, [fixture], "newline", {})
        record = json.loads((folder / "run.json").read_bytes())
        for name in ("subject", "grader"):
            item = record["fixtures"][0]
            payload = (self.root / item[name + "_prompt"]).read_bytes()
            self.assertNotIn(b"\r", payload)
            self.assertEqual(evals._sha(payload.decode()), item[name + "_sha256"])

    def test_prepare_rejects_duplicate_ids_before_writing(self):
        families, generated = check.check(self.root)
        fixture = evals.load(self.root, families)[0]
        with self.assertRaisesRegex(ValueError, "distinct"):
            evals.prepare(self.root, families, generated, [fixture, fixture], "duplicate", {})
        self.assertFalse((self.root / "work/evals/duplicate").exists())

    def prepare(self, run="t1", **selection):
        argv = ["prepare", "--run", run, "--host", "Test host", "--model", "test-model"]
        for name, value in selection.items():
            argv += [f"--{name}", value]
        with contextlib.redirect_stdout(io.StringIO()):
            evals_cli.main(argv, root=self.root)
        return evals.load_run(self.root, run)

    def cli_fails(self, argv, pattern):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            evals_cli.main(argv, root=self.root)
        self.assertRegex(stderr.getvalue(), pattern)

    def answer(self, record, verdicts=None, skip=()):
        """Write a reply and a grade for each fixture; verdicts maps fixture id to {section: verdict}."""
        for fixture in record["fixtures"]:
            if fixture["id"] in skip:
                continue
            (self.root / fixture["output"]).write_text("A reply.\n")
            chosen = (verdicts or {}).get(fixture["id"], {})
            grade = {"fixture": fixture["id"], "notes": ""}
            for section, allowed in evals.SCORED.items():
                grade[section] = [{"item": item, "verdict": chosen.get(section, allowed[0]), "evidence": "quote", "quote": "A reply."}
                                  for item in fixture[section]]
            (self.root / fixture["grade"]).write_text(json.dumps(grade))

    def test_prepare_writes_prompts_for_one_role(self):
        record = self.prepare(role=ROLE)
        self.assertEqual({f["role"] for f in record["fixtures"]}, {ROLE})
        self.assertEqual((record["host"], record["model"], record["grader"]), ("Test host", "test-model", "test-model"))
        fixture = record["fixtures"][0]
        self.assertEqual(fixture["pack"], "dist/packs/security-governance.md")
        card = (self.root / "catalog/security/access-review-analyst.md").read_text()
        self.assertEqual(fixture["acceptance"], evals.criteria(card))
        self.assertEqual(len(fixture["acceptance"]), 4)
        subject = (self.root / fixture["subject_prompt"]).read_text()
        self.assertIn((self.root / "dist/packs/security-governance.md").read_text().rstrip(), subject)
        self.assertIn(f"`{ROLE}`", subject)
        self.assertNotIn("Acceptance criteria", subject)
        grader = (self.root / fixture["grader_prompt"]).read_text()
        self.assertIn((self.root / fixture["pack"]).read_text().rstrip(), grader)
        for item in fixture["acceptance"] + fixture["traits"] + fixture["must_not"]:
            self.assertIn(item, grader)
        self.assertIn(fixture["output"], grader)
        self.assertIn(fixture["grade"], grader)

    def test_prepare_selects_family_and_kind(self):
        record = self.prepare(family="finance", kind="boundary")
        self.assertTrue(record["fixtures"])
        self.assertTrue(all(f["family"] == "finance" and f["kind"] == "boundary" for f in record["fixtures"]))

    def test_prepare_refuses_existing_run_bad_name_and_empty_selection(self):
        self.prepare(role=ROLE)
        self.cli_fails(["prepare", "--run", "t1", "--host", "h", "--model", "m", "--role", ROLE], "already exists")
        self.cli_fails(["prepare", "--run", "../escape", "--host", "h", "--model", "m"], "must be a slug")
        self.cli_fails(["prepare", "--run", "t2", "--host", "h", "--model", "m", "--role", "x/y"], "no fixtures match")

    def test_prepare_refuses_a_failing_pack_check(self):
        (self.root / evals.FIXTURE_DIR / "ai-ml.json").unlink()
        self.cli_fails(["prepare", "--run", "t1", "--host", "h", "--model", "m"], "fixture file is missing")

    def test_status_tracks_progress(self):
        record = self.prepare(family="ai-ml")
        _, need_output, need_grade = evals.status(self.root, "t1")
        self.assertEqual(len(need_output), len(record["fixtures"]))
        self.answer(record, skip={record["fixtures"][0]["id"]})
        (self.root / record["fixtures"][1]["grade"]).unlink()
        _, need_output, need_grade = evals.status(self.root, "t1")
        self.assertEqual([f["id"] for f in need_output], [record["fixtures"][0]["id"]])
        self.assertEqual([f["id"] for f in need_grade], [record["fixtures"][1]["id"]])

    def test_report_outcomes(self):
        record = self.prepare(family="ai-ml")
        ids = [f["id"] for f in record["fixtures"]]
        self.answer(record, {ids[1]: {"traits": "partial"}, ids[2]: {"must_not": "violated"}})
        text = evals.report(self.root, "t1").read_text()
        self.assertIn(f"| `{ids[0]}` | {record['fixtures'][0]['kind']} | PASS |", text)
        self.assertIn(f"| `{ids[1]}` | {record['fixtures'][1]['kind']} | PARTIAL |", text)
        self.assertIn(f"| `{ids[2]}` | {record['fixtures'][2]['kind']} | FAIL |", text)
        for field in ("Pack version", "Commit", "Host", "Tools", "Model under test", "## Inputs", "## Limits"):
            self.assertIn(field, text)
        self.assertIn("test-model", text)
        self.assertIn(f"### `{ids[2]}`: FAIL", text)
        self.assertNotIn(f"### `{ids[0]}`", text)

    def test_report_fails_on_missing_reply_or_grade(self):
        record = self.prepare(role=ROLE)
        self.cli_fails(["report", "--run", "t1"], "reply is missing or empty")
        self.answer(record)
        (self.root / record["fixtures"][0]["grade"]).unlink()
        self.cli_fails(["report", "--run", "t1"], "grade is missing")

    def test_report_rejects_changed_items_and_bad_verdicts(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        path = self.root / record["fixtures"][0]["grade"]
        grade = json.loads(path.read_text())
        grade["acceptance"][0]["item"] = "Something easier"
        path.write_text(json.dumps(grade))
        with self.assertRaisesRegex(ValueError, "acceptance items must match the prepared list"):
            evals.report(self.root, "t1")
        grade["acceptance"][0]["item"] = record["fixtures"][0]["acceptance"][0]
        grade["must_not"][0]["verdict"] = "pass"
        path.write_text(json.dumps(grade))
        with self.assertRaisesRegex(ValueError, "must_not verdict 'pass' is not one of clear, violated"):
            evals.report(self.root, "t1")
        path.write_text("not json")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            evals.report(self.root, "t1")

    def test_compare_flags_a_card_whose_pass_rate_fell(self):
        record = self.prepare(family="ai-ml")
        self.answer(record)
        evals.report(self.root, "t1")
        with contextlib.redirect_stdout(io.StringIO()):
            evals_cli.main(["baseline", "--run", "t1"], root=self.root)
        self.assertEqual(json.loads((self.root / evals.BASELINE).read_text())["model"], "test-model")
        build.build(self.root)  # the module map digests the baseline file
        self.prepare("t2", family="ai-ml")
        self.answer(evals.load_run(self.root, "t2"))
        with contextlib.redirect_stdout(io.StringIO()):
            evals_cli.main(["compare", "--run", "t2"], root=self.root)
        self.assertIn("No card's pass rate fell", (self.root / "work/evals/t2/REGRESSION.md").read_text())
        worse = record["fixtures"][0]
        self.prepare("t3", family="ai-ml")
        self.answer(evals.load_run(self.root, "t3"), {worse["id"]: {"traits": "fail"}})
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as exit_:
            evals_cli.main(["compare", "--run", "t3"], root=self.root)
        self.assertEqual(exit_.exception.code, 3)
        self.assertIn(f"fell\t{worse['role']}", out.getvalue())
        self.assertIn(f"`{worse['id']}`", (self.root / "work/evals/t3/REGRESSION.md").read_text())

    def test_baseline_lays_a_later_run_over_an_earlier_one(self):
        record = self.prepare(family="ai-ml")
        worse = record["fixtures"][0]
        self.answer(record, {worse["id"]: {"traits": "fail"}})
        self.prepare("t2", role=worse["role"])
        self.answer(evals.load_run(self.root, "t2"))
        with contextlib.redirect_stdout(io.StringIO()):
            evals_cli.main(["baseline", "--run", "t1", "--run", "t2"], root=self.root)
        data = json.loads((self.root / evals.BASELINE).read_text())
        self.assertEqual(data["run"], "t1 + t2")
        self.assertEqual(data["roles"][worse["role"]]["passed"], data["roles"][worse["role"]]["total"])
        self.assertEqual(sorted(data["roles"]), sorted({f["role"] for f in record["fixtures"]}))

    def test_heldout_is_valid_and_distinct(self):
        families = manifest.load(self.root)
        challenges = evals.heldout(self.root, families)
        self.assertEqual(len(challenges), 6)
        self.assertFalse({f["id"] for f in challenges} & {f["id"] for f in evals.load(self.root, families)})

    def test_changed_prompt_is_rejected(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        (self.root / record["fixtures"][0]["subject_prompt"]).write_text("changed")
        with self.assertRaisesRegex(ValueError, "prompt hash mismatch"):
            evals.report(self.root, "t1")

    def test_empty_evidence_is_rejected(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        path = self.root / record["fixtures"][0]["grade"]
        grade = json.loads(path.read_text())
        grade["acceptance"][0]["evidence"] = "  "
        path.write_text(json.dumps(grade))
        with self.assertRaisesRegex(ValueError, "non-empty text"):
            evals.report(self.root, "t1")

    def test_changed_rubric_or_models_are_incomparable(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        evals.save_baseline(self.root, "t1")
        baseline = json.loads((self.root / evals.BASELINE).read_text())
        baseline["fixtures"][record["fixtures"][0]["id"]]["rubric_sha256"] = "different"
        (self.root / evals.BASELINE).write_text(json.dumps(baseline))
        with self.assertRaisesRegex(ValueError, "incomparable baseline"):
            evals.compare(self.root, "t1")
        baseline["model"] = "another-model"
        (self.root / evals.BASELINE).write_text(json.dumps(baseline))
        with self.assertRaisesRegex(ValueError, "requested model"):
            evals.compare(self.root, "t1")

    def test_changed_shared_instructions_are_incomparable(self):
        first = self.prepare(role=ROLE)
        self.answer(first)
        evals.save_baseline(self.root, "t1")
        self.edit("pack/FAMILY-COORDINATOR.md", lambda text: text.replace("one task or project", "one job or project"))
        build.build(self.root)
        second = self.prepare(run="t2", role=ROLE)
        self.answer(second)
        with self.assertRaisesRegex(ValueError, "incomparable baseline"):
            evals.compare(self.root, "t2")

    def test_changed_harness_is_incomparable(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        evals.save_baseline(self.root, "t1")
        record["harness_sha256"]["scripts/evals_runner.py"] = "0" * 64
        (self.root / "work/evals/t1/run.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "harness"):
            evals.compare(self.root, "t1")

    def test_baseline_cannot_mix_harnesses(self):
        first = self.prepare(role=ROLE)
        second = self.prepare(run="t2", role=ROLE)
        self.answer(first)
        self.answer(second)
        second["harness_sha256"]["scripts/evals_runner.py"] = "0" * 64
        (self.root / "work/evals/t2/run.json").write_text(json.dumps(second))
        with self.assertRaisesRegex(ValueError, "harness"):
            evals.save_baseline(self.root, ["t1", "t2"])

    def test_compare_needs_a_baseline(self):
        record = self.prepare(role=ROLE)
        self.answer(record)
        (self.root / evals.BASELINE).write_text('{"schema": 1, "run": null, "roles": {}}\n')
        self.cli_fails(["compare", "--run", "t1"], "holds no baseline yet")

    def test_report_needs_a_prepared_run(self):
        self.cli_fails(["report", "--run", "never"], "run.json is missing")


if __name__ == "__main__":
    unittest.main()
