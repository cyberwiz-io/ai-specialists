# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_release import verify
from packlib.bundle import PUBLIC_DOCUMENTS


class ReleaseVerifierTests(unittest.TestCase):
    version = "1.1"
    main = f"ai-specialists-{version}.zip"
    family = f"ai-specialists-{version}-skill-research.zip"

    def make_release(self, folder, *, family_skill=True):
        payload = {name: b"doc\n" for name in PUBLIC_DOCUMENTS}
        payload["VERSION"] = self.version.encode()
        payload["catalog/families.json"] = b'{"families":[{"id":"research"}]}'
        payload["extra.txt"] = b"payload"
        with ZipFile(folder / self.main, "w", ZIP_DEFLATED) as archive:
            for name, value in payload.items():
                archive.writestr(f"ai-specialists-{self.version}/{name}", value)
        if family_skill:
            with ZipFile(folder / self.family, "w", ZIP_DEFLATED) as archive:
                archive.writestr("research/SKILL.md", b"# Research\n")
        archives = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in folder.glob("*.zip")}
        record = {"schema": 1, "version": self.version, "draft": False,
                  "source_commit": "a" * 40, "source_tree": "b" * 40,
                  "archives": archives}
        (folder / "RELEASE.json").write_text(json.dumps(record), encoding="utf-8")
        sums = dict(archives)
        sums["RELEASE.json"] = hashlib.sha256((folder / "RELEASE.json").read_bytes()).hexdigest()
        (folder / "SHA256SUMS").write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(sums.items())), encoding="utf-8")
        return record

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.record = self.make_release(self.folder)

    def tearDown(self):
        self.temp.cleanup()

    def test_symlinked_metadata_is_rejected_before_reading(self):
        for name in ("SHA256SUMS", "RELEASE.json"):
            path = self.folder / name
            data = path.read_bytes()
            path.unlink()
            path.symlink_to(self.folder / "missing-external")
            with self.assertRaisesRegex(ValueError, "Unsafe release metadata"):
                verify(self.folder)
            path.unlink()
            path.write_bytes(data)

    def test_valid_artifacts_verify(self):
        self.assertEqual(verify(self.folder), self.record)

    def test_archive_corruption_fails_checksum(self):
        with (self.folder / self.main).open("ab") as archive:
            archive.write(b"corruption")
        with self.assertRaisesRegex(ValueError, "Checksum"):
            verify(self.folder)

    def test_checksum_file_must_match_exact_asset_membership(self):
        with (self.folder / "SHA256SUMS").open("a") as sums:
            sums.write(f"{'0' * 64}  unexpected.zip\n")
        with self.assertRaisesRegex(ValueError, "membership"):
            verify(self.folder)

    def test_archive_version_must_match_provenance(self):
        self.record["version"] = "9.9"
        (self.folder / "RELEASE.json").write_text(json.dumps(self.record), encoding="utf-8")
        sums = dict(self.record["archives"])
        sums["RELEASE.json"] = hashlib.sha256((self.folder / "RELEASE.json").read_bytes()).hexdigest()
        (self.folder / "SHA256SUMS").write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(sums.items())), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Main archive missing"):
            verify(self.folder)

    def test_draft_and_missing_provenance_require_explicit_override(self):
        self.record["draft"] = True
        self._rewrite_record()
        with self.assertRaisesRegex(ValueError, "draft or missing"):
            verify(self.folder)
        self.assertEqual(verify(self.folder, allow_draft=True), self.record)
        self.record["draft"] = False
        self.record["source_tree"] = None
        self._rewrite_record()
        with self.assertRaisesRegex(ValueError, "draft or missing"):
            verify(self.folder)

    def test_archive_provenance_digest_must_match_checksum(self):
        self.record["archives"][self.family] = "0" * 64
        (self.folder / "RELEASE.json").write_text(json.dumps(self.record), encoding="utf-8")
        sums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.folder.glob("*.zip")}
        sums["RELEASE.json"] = hashlib.sha256((self.folder / "RELEASE.json").read_bytes()).hexdigest()
        (self.folder / "SHA256SUMS").write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(sums.items())), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Provenance and checksums differ"):
            verify(self.folder)

    def test_required_public_document_must_be_in_main_archive(self):
        self._rewrite_main_without("docs/INSTALL.md")
        self._refresh_archive_hashes()
        with self.assertRaisesRegex(ValueError, "Required documents missing"):
            verify(self.folder)

    def test_family_archive_must_contain_lead_skill(self):
        with ZipFile(self.folder / self.family, "w", ZIP_DEFLATED) as archive:
            archive.writestr("research/README.md", b"No lead skill")
        self._refresh_archive_hashes()
        with self.assertRaisesRegex(ValueError, "lead skill missing"):
            verify(self.folder)

    def _rewrite_record(self):
        (self.folder / "RELEASE.json").write_text(json.dumps(self.record), encoding="utf-8")
        sums = dict(self.record["archives"])
        sums["RELEASE.json"] = hashlib.sha256((self.folder / "RELEASE.json").read_bytes()).hexdigest()
        (self.folder / "SHA256SUMS").write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(sums.items())), encoding="utf-8")

    def _rewrite_main_without(self, missing):
        path = self.folder / self.main
        with ZipFile(path) as archive:
            members = {name: archive.read(name) for name in archive.namelist()
                       if not name.endswith("/" + missing)}
        with ZipFile(path, "w", ZIP_DEFLATED) as archive:
            for name, data in members.items():
                archive.writestr(name, data)

    def _refresh_archive_hashes(self):
        self.record["archives"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in self.folder.glob("*.zip")}
        self._rewrite_record()


if __name__ == "__main__":
    unittest.main()
