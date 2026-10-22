# SPDX-License-Identifier: Apache-2.0
"""Verify downloaded release bytes without using a source checkout as link fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from packlib import bundle


def verify(folder, allow_draft=False):
    if folder.is_symlink() or any((folder / name).is_symlink() for name in ("RELEASE.json", "SHA256SUMS")):
        raise ValueError("Unsafe release metadata or directory")
    record = json.loads((folder / "RELEASE.json").read_text(encoding="utf-8"))
    if not allow_draft and (record.get("draft") is not False or not all(
            re.fullmatch(r"[a-f0-9]{40}", record.get(key) or "") for key in ("source_commit", "source_tree"))):
        raise ValueError("Release provenance is draft or missing")
    sums = {}
    for line in (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match or match[2] in sums:
            raise ValueError("Invalid or duplicate checksum entry")
        sums[match[2]] = match[1]
    expected = set(record["archives"]) | {"RELEASE.json"}
    if set(sums) != expected or {p.name for p in folder.glob("*.zip")} != set(record["archives"]):
        raise ValueError("Release asset membership differs")
    for name, digest in sums.items():
        path = folder / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Checksum mismatch or unsafe asset: {name}")
    if any(sums.get(name) != digest for name, digest in record["archives"].items()):
        raise ValueError("Provenance and checksums differ")
    main = f"ai-specialists-{record['version']}.zip"
    if main not in record["archives"]:
        raise ValueError("Main archive missing")
    payload = bundle.read_archive(folder / main)
    missing = set(bundle.PUBLIC_DOCUMENTS) - set(payload)
    if missing:
        raise ValueError("Required documents missing: " + ", ".join(sorted(missing)))
    if payload["VERSION"].decode().strip() != record["version"]:
        raise ValueError("Archive version differs from provenance")
    manifest = json.loads(payload["catalog/families.json"])
    expected_skills = {f"ai-specialists-{record['version']}-skill-{f['id']}.zip" for f in manifest["families"]}
    if set(record["archives"]) != expected_skills | {main}:
        raise ValueError("Family archive membership differs")
    for name in expected_skills:
        if "SKILL.md" not in bundle.read_archive(folder / name):
            raise ValueError(f"{name}: lead skill missing")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--allow-draft", action="store_true", help="test an unpublished working-tree artifact")
    args = parser.parse_args()
    try:
        record = verify(args.folder, args.allow_draft)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Release verification failed: {error}\n")
    print(f"PASS: {len(record['archives'])} archives, version {record['version']}, draft={record['draft']}")


if __name__ == "__main__":
    main()
