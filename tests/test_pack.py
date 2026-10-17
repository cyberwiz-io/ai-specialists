# SPDX-License-Identifier: Apache-2.0
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pack as pack_cli  # noqa: E402
from packlib import build, cards, check, config, manifest  # noqa: E402

COPY_SKIP = shutil.ignore_patterns(".git", "work", "__pycache__", "downloads", "dist")


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

    def assertFails(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            check.check(self.root)


class BuildTests(FixtureCase):
    def test_build_is_valid_and_reproducible(self):
        check.check(self.root)
        archive = self.root / config.archive_name(self.root)
        first = archive.read_bytes()
        build.build(self.root)
        self.assertEqual(first, archive.read_bytes())

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

    def test_card_edit_makes_index_and_packs_stale(self):
        self.edit("catalog/security/threat-modeler.md", lambda text: text.replace("**Use for:** ", "**Use for:** Edited. "))
        self.assertFails("catalog/security/INDEX.md differs from sources")
        build.build(self.root)
        check.check(self.root)

    def test_stale_generated_files_fail_and_are_removed(self):
        stale = self.root / "dist/packs/old-family.md"
        stale.write_text("old")
        zipped = self.root / "downloads/ai-specialists-0.1.zip"
        zipped.write_bytes(b"old")
        self.assertFails("old-family.md: stale generated file")
        build.build(self.root)
        self.assertFalse(stale.exists() or zipped.exists())
        check.check(self.root)

    def test_pack_size_cap(self):
        with mock.patch.object(check, "PACK_MAX", 100):
            self.assertFails("combined pack exceeds 100 bytes")

    def test_missing_license_does_not_replace_outputs(self):
        before = (self.root / config.STARTER).read_bytes()
        archive = (self.root / config.archive_name(self.root)).read_bytes()
        (self.root / "LICENSES/CC-BY-4.0.txt").unlink()
        with self.assertRaises(FileNotFoundError):
            build.build(self.root)
        self.assertEqual(before, (self.root / config.STARTER).read_bytes())
        self.assertEqual(archive, (self.root / config.archive_name(self.root)).read_bytes())

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
        path = self.root / config.archive_name(self.root)
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

    def test_wrong_card_version_and_id_fail(self):
        self.edit(self.CARD, lambda text: text.replace("Version: 1.0.", "Version: 0.9."))
        self.rebuild_and_fail("expected one Version 1.0")
        self.edit(self.CARD, lambda text: text.replace("software-engineering/code-reviewer", "software-engineering/other"))
        self.rebuild_and_fail("header must read")

    def test_wrong_document_version_fails(self):
        self.edit("pack/COORDINATOR.md", lambda text: text.replace("Version: 1.0", "Version: 0.2"))
        self.rebuild_and_fail("pack/COORDINATOR.md: expected one Version 1.0")

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

    def test_module_map_edit_is_detected(self):
        self.edit(config.MODULE_MAP, lambda text: text.replace('"digest": "', '"digest": "0'))
        self.assertFails("config/module-map.json differs from sources")

    def test_module_pattern_matching_nothing_fails(self):
        self.edit(config.MODULES, lambda text: text.replace('"tests/*.py"', '"tests/*.nothing"'))
        with self.assertRaisesRegex(ValueError, "matches no files"):
            build.build(self.root)


class ArchiveTests(FixtureCase):
    def test_zip_rejects_extra_file(self):
        with ZipFile(self.root / config.archive_name(self.root), "a") as bundle:
            bundle.writestr("private-profile.md", "Not an approved member")
        self.assertFails("ZIP membership differs")

    def test_zip_rejects_changed_bytes(self):
        archive = self.root / config.archive_name(self.root)
        with ZipFile(archive) as bundle:
            members = {name: bundle.read(name) for name in bundle.namelist()}
        first = sorted(members)[0]
        with ZipFile(archive, "w") as bundle:
            for name, data in members.items():
                bundle.writestr(name, b"changed" if name == first else data)
        self.assertFails("ZIP bytes differ")

    def test_unreadable_zip_fails_cleanly(self):
        (self.root / config.archive_name(self.root)).write_bytes(b"not a zip")
        self.assertFails("cannot read archive")

    def test_archive_contains_cards_packs_and_licenses(self):
        with ZipFile(self.root / config.archive_name(self.root)) as bundle:
            names = bundle.namelist()
        prefix = "ai-specialists-1.0/"
        for required in ("catalog/security/threat-modeler.md", "dist/packs/finance.md",
                         "pack/STARTER-PACK.md", "LICENSES/Apache-2.0.txt", "catalog/REGISTRY.jsonl"):
            self.assertIn(prefix + required, names)
        self.assertFalse([name for name in names if "/work/" in name or "/profiles/" in name])


class FindTests(FixtureCase):
    def test_find_matches_all_terms(self):
        rows = pack_cli.find(self.root, ["threat", "security"])
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].startswith("security/threat-modeler\t"))

    def test_find_without_match_is_empty(self):
        self.assertEqual(pack_cli.find(self.root, ["zzzz-not-a-role"]), [])


if __name__ == "__main__":
    unittest.main()
