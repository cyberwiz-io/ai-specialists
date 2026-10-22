# SPDX-License-Identifier: Apache-2.0
"""Generate config/module-map.json from config/modules.json and the family manifest."""
import fnmatch
import hashlib
import json
from pathlib import Path

from .config import MODULES, SKIP_DIRS, read, safe_path, version
from . import source

COVERED_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".yml", ".yaml", ".toml"}
UNTRACKED_DIRS = {"LICENSES", "dist"}
IGNORED = ("plugins/*/evals/results/*",)  # local `claude plugin eval` output, git-ignored
FAMILY_INVARIANT = "Materials only: no external actions, no capability promises, fictional examples."


def expand(root, patterns, overlay, inventory=None):
    """Sorted repository-relative files matching glob patterns (including pending generated files)."""
    names = set(source.files(root) if inventory is None else inventory) | set(overlay)
    return sorted(name for name in names if any(fnmatch.fnmatchcase(name, p) for p in patterns))


def digest(root, files, overlay):
    lines = "".join(f"{name}\0{hashlib.sha256(read(root, name, overlay)).hexdigest()}\n" for name in files)
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def load_spec(root):
    try:
        spec = json.loads(read(root, MODULES).decode("utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{MODULES}: invalid JSON ({error})")
    for module in spec.get("modules", []):
        for key in ("id", "purpose", "guide", "paths"):
            if not module.get(key):
                raise ValueError(f"{MODULES}: module {module.get('id', '?')} lacks {key}")
    return spec


def modules(root, families, overlay):
    spec = load_spec(root)
    checks = spec.get("checks", [])
    records = [dict(module) for module in spec["modules"]]
    for family in families:
        records.append({
            "id": f"family-{family['id']}", "purpose": family["purpose"],
            "guide": f"catalog/{family['id']}/INDEX.md", "paths": [f"catalog/{family['id']}/*.md"],
            "interfaces": [f"catalog/{family['id']}/INDEX.md"], "dependencies": ["instructions"],
            "invariants": [FAMILY_INVARIANT]})
    for record in records:
        for key in ("interfaces", "dependencies", "consumers", "invariants"):
            record.setdefault(key, [])
        record.setdefault("checks", checks)
        record["paths"] = sorted(record["paths"])
    return spec, records


def generate(root, families, overlay, inventory=None):
    spec, records = modules(root, families, overlay)
    inventory = source.files(root) if inventory is None else inventory
    covered = set()
    for record in records:
        for pattern in record["paths"]:
            if not expand(root, [pattern], overlay, inventory):
                raise ValueError(f"module {record['id']}: pattern {pattern} matches no files")
        files = expand(root, record["paths"], overlay, inventory)
        covered.update(files)
        record["files"] = len(files)
        record["digest"] = digest(root, files, overlay)
    result = {"schema": 2, "version": version(root), "entry": spec.get("entry", "REPO-MAP.md"),
              "generated": sorted(spec.get("generated", [])), "modules": records}
    return (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")


def uncovered(root, families, overlay, inventory=None):
    spec, records = modules(root, families, overlay)
    inventory = source.files(root) if inventory is None else inventory
    covered = set()
    for record in records:
        covered.update(expand(root, record["paths"], overlay, inventory))
    generated = spec.get("generated", [])
    missing = []
    for name in inventory:
        relative = Path(name)
        if set(relative.parts) & (SKIP_DIRS | UNTRACKED_DIRS):
            continue
        if any(fnmatch.fnmatchcase(name, pattern) for pattern in IGNORED):
            continue
        if relative.suffix in COVERED_SUFFIXES and name not in covered \
                and not any(fnmatch.fnmatchcase(name, pattern) for pattern in generated):
            missing.append(name)
    return missing
