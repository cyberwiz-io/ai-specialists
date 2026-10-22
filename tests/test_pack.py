# SPDX-License-Identifier: Apache-2.0
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pack as pack_cli  # noqa: E402
from packlib import build, bundle, cards, check, config, manifest, skills  # noqa: E402

COPY_SKIP = shutil.ignore_patterns(".git", "work", "__pycache__", "dist")


class FixtureCase(unittest.TestCase):
    """Each test works on a private copy of the repository sources."""

    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=COPY_SKIP)
        build.build(self.root)

    def edit(self, name, change):
        path = self.root / name
        path.write_text(change(path.read_text()))

    def release(self, tag=None):
        families, generated = check.check(self.root)
        return bundle.release(self.root, families, generated, self.root / config.RELEASE_DIR, tag)

    def assertFails(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            check.check(self.root)


class BuildTests(FixtureCase):
    def test_build_is_valid_and_reproducible(self):
        first = self.release().read_bytes()
        build.build(self.root)
        self.assertEqual(first, self.release().read_bytes())

    def test_repository_ships_the_full_catalog(self):
        families, generated = check.check(self.root)
        self.assertEqual(len(families), 17)
        self.assertEqual(sum(len(f["roles"]) for f in families), 124)
        lines = (self.root / config.REGISTRY).read_text().splitlines()
        rows = [json.loads(line) for line in lines[1:]]
        self.assertEqual(json.loads(lines[0])["count"], 124)
        self.assertEqual(len({row["id"] for row in rows}), 124)
        self.assertTrue(all(len(data) <= config.PACK_MAX for name, data in generated.items()
                            if name.startswith(config.PACK_DIR)))

    def test_modified_source_requires_rebuild(self):
        self.edit("pack/COORDINATOR.md", lambda text: text + "\nA changed instruction.\n")
        self.assertFails("Combined instructions differ")
        build.build(self.root)
        check.check(self.root)

    def test_review_contract_cannot_be_removed_by_rebuild(self):
        self.edit("pack/FAMILY-COORDINATOR.md", lambda text: text.replace(
            "different actual model", "fresh reviewer context"))
        build.build(self.root)
        self.assertFails("review contract missing 'different actual model'")

    def test_review_contract_rejects_removed_source_guards(self):
        cases = (
            ("pack/COORDINATOR.md", "BLOCKED_MODEL/COST", "unknown cost"),
            ("pack/COORDINATOR.md", "BLOCKED_MODEL/COST; do not claim ready or complete",
             "BLOCKED_MODEL/COST; no cheapest claim"),
            ("pack/FAMILY-COORDINATOR.md", "or uncertain work is nontrivial", "or uncertain work is trivial"),
            ("pack/COORDINATOR.md", "from every author", "from any author"),
            ("pack/FAMILY-COORDINATOR.md", "from every author", "from any author"),
            ("catalog/orchestration/cross-family-reviewer.md", "from every author model", "from any author model"),
            ("catalog/marketing-growth/quality-reviewer.md", "Same-model review is BLOCKED_REVIEW.", "Same-model review may pass."),
            ("catalog/orchestration/cross-family-reviewer.md", "host-observed", "claimed"),
            ("catalog/orchestration/cross-family-reviewer.md", "byte hash", "version"),
            ("pack/FAMILY-COORDINATOR.md", "prefer local only at equal known total cost", "prefer local"),
            ("catalog/marketing-growth/quality-reviewer.md", "Changed bytes void review", "changes may be accepted"),
            ("catalog/marketing-growth/quality-reviewer.md", "BLOCKED_REVIEW", "pending"),
            ("catalog/orchestration/task-router.md", "different actual model", "fresh context"),
        )
        for name, phrase, replacement in cases:
            with self.subTest(name=name):
                source = (self.root / name).read_text()
                self.edit(name, lambda text: text.replace(phrase, replacement))
                build.build(self.root)
                self.assertFails(f"review contract missing {phrase!r}")
                (self.root / name).write_text(source)
                build.build(self.root)

    def test_review_contract_checks_generated_leads(self):
        with mock.patch.object(skills, "LEAD_STEPS", skills.LEAD_STEPS.replace(
                "untrusted task data", "ordinary output")):
            self.assertFails("review contract missing 'untrusted task data'")

    def test_review_contract_checks_generated_model_override_and_manifest(self):
        definition = ("may stay inline with a stated reason. Behavior, policy, configuration, "
                      "security-sensitive or uncertain work is nontrivial; mechanical formatting "
                      "needs an exception reason.")
        cases = [
            (phrase, phrase) for phrase in (
                "supported per-call model override", "host-observed model IDs",
                "manifest of the exact artifact/version, byte hash",
                "prefer eligible local only at equal known cost",
                "from every author model",
                "No new charges through model selection or overrides.")
        ]
        cases += [
            ("BLOCKED_MODEL/COST; do not claim ready or complete",
             "mark BLOCKED_MODEL/COST; do not claim ready or complete."),
            ("or uncertain work is nontrivial", definition),
            ("mechanical formatting needs an exception reason", definition),
        ]
        for phrase, required in cases:
            with self.subTest(phrase=phrase), mock.patch.object(
                    skills, "LEAD_STEPS", skills.LEAD_STEPS.replace(phrase, "omitted")):
                self.assertFails(f"review contract missing {required!r}")

    def test_card_edit_makes_index_and_packs_stale(self):
        self.edit("catalog/security/threat-modeler.md", lambda text: text.replace("**Use for:** ", "**Use for:** Edited. "))
        self.assertFails("catalog/security/INDEX.md differs from sources")
        build.build(self.root)
        check.check(self.root)

    def test_stale_generated_files_fail_and_are_removed(self):
        stale = self.root / "dist/packs/old-family.md"
        stale.write_text("old")
        self.assertFails("old-family.md: stale generated file")
        build.build(self.root)
        self.assertFalse(stale.exists())
        check.check(self.root)

    def test_pack_size_cap(self):
        with mock.patch.object(check, "PACK_MAX", 100):
            self.assertFails("combined pack exceeds 100 bytes; split the family")

    def test_every_pack_fits_a_small_context_window(self):
        _, generated = check.check(self.root)
        packs = {name: len(data) for name, data in generated.items() if name.startswith(config.PACK_DIR)}
        self.assertLessEqual(config.PACK_MAX, 32000)
        self.assertEqual([name for name, size in packs.items() if size > config.PACK_MAX], [])

    def test_missing_license_does_not_replace_outputs(self):
        before = (self.root / config.STARTER).read_bytes()
        self.edit("pack/COORDINATOR.md", lambda text: text + "\nA changed instruction.\n")
        (self.root / "LICENSES/CC-BY-4.0.txt").unlink()
        self.assertFails("release archive input is unreadable")
        build.build(self.root)
        self.assertNotEqual(before, (self.root / config.STARTER).read_bytes())
        self.assertFails("release archive input is unreadable")

    def test_missing_card_stops_build_and_check(self):
        (self.root / "catalog/finance/budget-planner.md").unlink()
        self.assertFails("budget-planner.md: card file is missing")
        with self.assertRaises(FileNotFoundError):
            build.build(self.root)

    def test_source_symlink_is_rejected(self):
        target = self.root / "pack/COORDINATOR.md"
        target.rename(self.root / "coordinator-original.md")
        target.symlink_to(self.root / "coordinator-original.md")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            build.build(self.root)

    def test_destination_symlink_is_rejected(self):
        path = self.root / config.STARTER
        path.unlink()
        path.symlink_to(self.root / "LICENSE.md")
        with self.assertRaisesRegex(ValueError, "Unsafe source path"):
            build.build(self.root)


class CardRuleTests(FixtureCase):
    CARD = "catalog/software-engineering/code-reviewer.md"
    SENSITIVE = "catalog/security/threat-modeler.md"

    def rebuild_and_fail(self, pattern):
        build.build(self.root)
        self.assertFails(pattern)

    def test_missing_label_fails(self):
        self.edit(self.CARD, lambda text: text.replace("**Acceptance:**", "**Checks:**"))
        self.rebuild_and_fail("missing Acceptance")

    def test_label_order_fails(self):
        def swap(text):
            return text.replace("**Inputs:**", "**Temp:**").replace("**Method:**", "**Inputs:**").replace("**Temp:**", "**Method:**")
        self.edit(self.CARD, swap)
        self.rebuild_and_fail("labels must appear in the order")

    def test_repeated_label_fails(self):
        self.edit(self.SENSITIVE, lambda text: text.replace("**Safeguards:**", "**Safeguards:** **Safeguards:**"))
        self.rebuild_and_fail("more than one label")

    def test_wrong_card_version_and_id_fail(self):
        self.edit(self.CARD, lambda text: text.replace("Version: 1.1.", "Version: 0.9."))
        self.rebuild_and_fail("expected one Version 1.1")
        self.edit(self.CARD, lambda text: text.replace("software-engineering/code-reviewer", "software-engineering/other"))
        self.rebuild_and_fail("header must read")

    def test_wrong_document_version_fails(self):
        self.edit("pack/COORDINATOR.md", lambda text: text.replace("Version: 1.1", "Version: 0.2"))
        self.rebuild_and_fail("pack/COORDINATOR.md: expected one Version 1.1")

    def test_sensitive_card_needs_safeguards(self):
        self.edit(self.SENSITIVE, lambda text: text.replace("**Safeguards:**", "**Notes:**"))
        self.rebuild_and_fail("missing Safeguards")

    def test_safeguards_must_cover_all_terms(self):
        self.edit(self.SENSITIVE, lambda text: re.sub("escalat", "pass along", text, flags=re.I))
        self.rebuild_and_fail("Safeguards must address 'escalat'")

    def test_unruled_out_word_fails_but_negated_use_passes(self):
        self.edit(self.CARD, lambda text: text + "\nThe role will deploy the change.\n")
        self.rebuild_and_fail("'deploy' appears without ruling it out")
        self.edit(self.CARD, lambda text: text.replace("The role will deploy the change.", "The role does not deploy the change."))
        build.build(self.root)
        check.check(self.root)

    def test_named_standard_fails(self):
        self.edit(self.CARD, lambda text: text.replace("**Inputs:** ", "**Inputs:** Follow OWASP guidance. "))
        self.rebuild_and_fail("names a standard or regulation")

    def test_unknown_handoff_role_fails(self):
        self.edit(self.CARD, lambda text: text + "\nAlso see `software-engineering/nobody`.\n")
        self.rebuild_and_fail("unknown role software-engineering/nobody")

    def test_boundary_sentence_required(self):
        self.edit(self.CARD, lambda text: text.replace("All Coordinator boundaries apply", "Boundaries are loose"))
        self.rebuild_and_fail("Handoff must state that all Coordinator boundaries apply")

    def test_oversized_card_fails(self):
        self.edit(self.CARD, lambda text: text + "\n" + "x" * 4000 + "\n")
        self.rebuild_and_fail("card exceeds")

    def test_unlisted_card_file_fails(self):
        (self.root / "catalog/finance/surprise.md").write_text("# Surprise\n")
        self.assertFails("surprise.md: not in finance manifest")

    def test_unlisted_family_folder_fails(self):
        (self.root / "catalog/extras").mkdir()
        self.assertFails("catalog/extras: folder is not a manifest family")

    def test_duplicate_deliverable_fails(self):
        source = (self.root / self.CARD).read_text()
        deliver = cards.parse(source)["paragraphs"]["Deliver"]
        other = "catalog/software-engineering/test-designer.md"
        current = cards.parse((self.root / other).read_text())["paragraphs"]["Deliver"]
        self.edit(other, lambda text: text.replace(current, deliver))
        self.rebuild_and_fail("Deliver duplicates")


class ManifestTests(FixtureCase):
    def change_manifest(self, change):
        path = self.root / config.MANIFEST
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_total_mismatch_fails(self):
        self.change_manifest(lambda data: data.update(total=123))
        with self.assertRaisesRegex(ValueError, "total says 123 but roster has 124"):
            manifest.load(self.root)

    def test_duplicate_slug_fails(self):
        self.change_manifest(lambda data: data["families"][0]["roles"].append(data["families"][0]["roles"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate slug"):
            manifest.load(self.root)

    def test_sensitive_family_requires_notes(self):
        self.change_manifest(lambda data: data["families"][0].pop("notes"))
        with self.assertRaisesRegex(ValueError, "sensitive family needs notes"):
            manifest.load(self.root)

    def test_invalid_json_fails(self):
        (self.root / config.MANIFEST).write_text("{")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            manifest.load(self.root)


class NavigationTests(FixtureCase):
    def test_broken_or_escaping_link_fails(self):
        for target in ("missing.md", "../outside.md"):
            with self.subTest(target=target):
                (self.root / "docs/ROADMAP.md").write_text(f"[Bad]({target})")
                self.assertFails("invalid local link")

    def test_repo_map_must_link_every_family(self):
        self.edit("REPO-MAP.md", lambda text: text.replace("catalog/finance/INDEX.md", "catalog/finance/"))
        self.assertFails("REPO-MAP.md: does not link catalog/finance/INDEX.md")

    def test_file_outside_every_module_fails(self):
        (self.root / "notes.md").write_text("# Notes\n")
        self.assertFails("notes.md is not covered by any module")

    def test_local_plugin_eval_results_are_ignored(self):
        results = self.root / "plugins/security/evals/results/2026-10-17T00-00-00-000Z"
        results.mkdir(parents=True)
        (results / "aggregate-result.json").write_text("{}\n")
        check.check(self.root)

    def test_module_map_edit_is_detected(self):
        self.edit(config.MODULE_MAP, lambda text: text.replace('"digest": "', '"digest": "0'))
        self.assertFails("config/module-map.json differs from sources")

    def test_module_pattern_matching_nothing_fails(self):
        self.edit(config.MODULES, lambda text: text.replace('"tests/*.py"', '"tests/*.nothing"'))
        with self.assertRaisesRegex(ValueError, "matches no files"):
            build.build(self.root)


class ArchiveTests(FixtureCase):
    def test_release_writes_verified_archive_outside_tracked_tree(self):
        archive = self.release("v1.1")
        self.assertEqual(archive, self.root / config.RELEASE_DIR / "ai-specialists-1.1.zip")
        check.check(self.root)  # work/ is ignored, so a local release never fails the check

    def test_release_rejects_mismatched_tag(self):
        with self.assertRaisesRegex(ValueError, "tag 'v2.0' does not match VERSION 1.1"):
            self.release("v2.0")
        self.assertFalse((self.root / config.RELEASE_DIR).exists())

    def test_release_rejects_symlinked_destination(self):
        out = self.root / config.RELEASE_DIR
        out.mkdir(parents=True)
        (out / config.archive_name(self.root)).symlink_to(self.root / "LICENSE.md")
        with self.assertRaisesRegex(ValueError, "Unsafe archive destination"):
            self.release()

    def test_committed_archive_fails_check(self):
        for name in ("downloads/ai-specialists-1.0.zip", "docs/extra.zip"):
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(b"old")
                self.assertFails(f"{name}: archives are not committed")
                path.unlink()

    def test_zip_rejects_extra_file(self):
        archive = self.release()
        with ZipFile(archive, "a") as bundled:
            bundled.writestr("private-profile.md", "Not an approved member")
        families, generated = check.check(self.root)
        self.assertEqual(bundle.compare(archive, bundle.members(self.root, families, generated)),
                         ["ZIP membership differs from the approved files"])

    def test_zip_rejects_changed_bytes(self):
        archive = self.release()
        with ZipFile(archive) as bundled:
            members = {name: bundled.read(name) for name in bundled.namelist()}
        first = sorted(members)[0]
        with ZipFile(archive, "w") as bundled:
            for name, data in members.items():
                bundled.writestr(name, b"changed" if name == first else data)
        families, generated = check.check(self.root)
        self.assertEqual(bundle.compare(archive, bundle.members(self.root, families, generated)),
                         [f"ZIP bytes differ: {first}"])

    def test_unreadable_zip_fails_cleanly(self):
        archive = self.release()
        archive.write_bytes(b"not a zip")
        with self.assertRaises(BadZipFile):
            bundle.compare(archive, {})

    def test_archive_contains_cards_packs_and_licenses(self):
        with ZipFile(self.release()) as bundled:
            names = bundled.namelist()
        prefix = "ai-specialists-1.1/"
        for required in ("catalog/security/threat-modeler.md", "dist/packs/finance.md",
                         "dist/packs/security-engineering.md", "dist/packs/security-governance.md",
                         "dist/packs/security-operations.md", "pack/STARTER-PACK.md", "LICENSES/Apache-2.0.txt", "catalog/REGISTRY.jsonl"):
            self.assertIn(prefix + required, names)
        self.assertFalse([name for name in names if "/work/" in name or "/profiles/" in name])
        self.assertNotIn(prefix + "dist/packs/security.md", names)


class SplitPackTests(FixtureCase):
    def change_manifest(self, change):
        path = self.root / config.MANIFEST
        data = json.loads(path.read_text())
        change(next(family for family in data["families"] if family["id"] == "security")["packs"])
        path.write_text(json.dumps(data))

    def test_security_cards_each_appear_in_exactly_one_pack(self):
        families, generated = check.check(self.root)
        security = next(family for family in families if family["id"] == "security")
        packs = {name: data.decode("utf-8") for name, data in generated.items()
                 if name.startswith(config.PACK_DIR + "/security")}
        self.assertEqual(sorted(packs), ["dist/packs/security-engineering.md", "dist/packs/security-governance.md",
                                        "dist/packs/security-operations.md"])
        for role in security["roles"]:
            holders = [name for name, text in packs.items() if f"<!-- Source: {role['path']} -->" in text]
            self.assertEqual(len(holders), 1, role["path"])
        for text in packs.values():
            self.assertIn("pack/FAMILY-COORDINATOR.md", text)
            self.assertIn("catalog/security/INDEX.md", text)
            self.assertIn("When a handoff names a role outside this pack", text)

    def test_unsplit_family_keeps_single_pack(self):
        _, generated = check.check(self.root)
        text = generated["dist/packs/finance.md"].decode("utf-8")
        self.assertIn("the user asks for this family pack", text)
        self.assertNotIn("outside this pack", text)

    def test_role_in_no_pack_fails(self):
        self.change_manifest(lambda packs: packs[-1]["roles"].remove("privacy-engineer"))
        with self.assertRaisesRegex(ValueError, "roles in no pack: privacy-engineer"):
            manifest.load(self.root)

    def test_role_in_two_packs_fails(self):
        self.change_manifest(lambda packs: packs[1]["roles"].append("threat-modeler"))
        with self.assertRaisesRegex(ValueError, "role threat-modeler is in more than one pack"):
            manifest.load(self.root)

    def test_unknown_role_fails(self):
        self.change_manifest(lambda packs: packs[1]["roles"].append("nobody"))
        with self.assertRaisesRegex(ValueError, "unknown role nobody"):
            manifest.load(self.root)

    def test_pack_id_must_extend_family_id(self):
        self.change_manifest(lambda packs: packs[0].update(id="finance"))
        with self.assertRaisesRegex(ValueError, "must be a slug starting with security-"):
            manifest.load(self.root)

    def test_duplicate_pack_id_fails(self):
        self.change_manifest(lambda packs: packs[1].update(id="security-engineering"))
        with self.assertRaisesRegex(ValueError, "pack id security-engineering already used"):
            manifest.load(self.root)

    def test_single_pack_split_fails(self):
        self.change_manifest(lambda packs: packs.__delitem__(slice(1, None)))
        with self.assertRaisesRegex(ValueError, "at least two packs"):
            manifest.load(self.root)


class FindTests(FixtureCase):
    def test_find_matches_all_terms(self):
        rows = pack_cli.find(self.root, ["threat", "security"])
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].startswith("security/threat-modeler\t"))

    def test_find_without_match_is_empty(self):
        self.assertEqual(pack_cli.find(self.root, ["zzzz-not-a-role"]), [])


if __name__ == "__main__":
    unittest.main()
