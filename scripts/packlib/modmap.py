# SPDX-License-Identifier: Apache-2.0
"""Generate config/module-map.json from config/modules.json and the family manifest."""
import fnmatch
import hashlib
import json

from .config import MODULES, SKIP_DIRS, client_index, is_untracked_client_install, read, safe_path, version

COVERED_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".yml", ".yaml", ".toml"}
UNTRACKED_DIRS = {"LICENSES", "dist"}
IGNORED = ("plugins/*/evals/results/*",)  # local `claude plugin eval` output, git-ignored
FAMILY_INVARIANT = "Materials only: no external actions, no capability promises, fictional examples."


def expand(root, patterns, overlay):
    """Sorted repository-relative files matching glob patterns (including pending generated files)."""
    found = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(root).as_posix())
        found.update(name for name in overlay if fnmatch.fnmatchcase(name, pattern))
    return sorted(found)


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


def generate(root, families, overlay):
    spec, records = modules(root, families, overlay)
    covered = set()
    for record in records:
        for pattern in record["paths"]:
            if not expand(root, [pattern], overlay):
                raise ValueError(f"module {record['id']}: pattern {pattern} matches no files")
        files = expand(root, record["paths"], overlay)
        covered.update(files)
        record["files"] = len(files)
        record["digest"] = digest(root, files, overlay)
    result = {"schema": 2, "version": version(root), "entry": spec.get("entry", "REPO-MAP.md"),
              "generated": sorted(spec.get("generated", [])), "modules": records}
    return (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")


def covered_paths(root, families, overlay):
    """Files explicitly assigned to a repository module, including generated files."""
    _, records = modules(root, families, overlay)
    return {name for record in records for name in expand(root, record["paths"], overlay)}


def uncovered(root, families, overlay, index=None):
    spec, records = modules(root, families, overlay)
    covered = set()
    for record in records:
        covered.update(expand(root, record["paths"], overlay))
    generated = spec.get("generated", [])
    index = index or client_index(root)
    missing = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if set(relative.parts) & (SKIP_DIRS | UNTRACKED_DIRS) or not path.is_file():
            continue
        name = relative.as_posix()
        if any(fnmatch.fnmatchcase(name, pattern) for pattern in IGNORED):
            continue
        if is_untracked_client_install(root, relative, covered | set(overlay), index):
            continue
        if path.suffix in COVERED_SUFFIXES and name not in covered \
                and not any(fnmatch.fnmatchcase(name, pattern) for pattern in generated):
            missing.append(name)
    return missing
