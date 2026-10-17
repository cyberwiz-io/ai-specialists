# SPDX-License-Identifier: Apache-2.0
"""Load fixture scenarios and grade a saved response with keyword rules. A smoke test, not a quality measure."""
import fnmatch
import json
import re

from . import adapter, manifest
from .config import read

SCENARIO_DIR = "evals/scenarios"
SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
RULES = ("must_match_any", "must_not_match")


def _fail(name, message):
    raise ValueError(f"{name}: {message}")


def _validate(name, data):
    if not isinstance(data, dict) or not SLUG.fullmatch(str(data.get("id", ""))):
        _fail(name, "needs a slug id")
    if name != f"{SCENARIO_DIR}/{data['id']}.json":
        _fail(name, "file name must match the scenario id")
    for key in ("source", "prompt"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            _fail(name, f"missing {key}")
    applies = data.get("applies_to")
    if not isinstance(applies, list) or not applies or not all(isinstance(item, str) for item in applies):
        _fail(name, "applies_to must list role-id patterns or 'sensitive'")
    graders = data.get("graders")
    if not isinstance(graders, list) or not graders:
        _fail(name, "needs at least one grader")
    for grader in graders:
        rules = [rule for rule in RULES if rule in grader]
        if len(rules) != 1 or not grader.get("why"):
            _fail(name, "each grader needs one of must_match_any or must_not_match, plus why")
        patterns = grader[rules[0]]
        if not isinstance(patterns, list) or not patterns:
            _fail(name, f"{rules[0]} must list patterns")
        for pattern in patterns:
            try:
                re.compile(pattern)
            except (re.error, TypeError) as error:
                _fail(name, f"bad pattern {pattern!r} ({error})")
    samples = data.get("samples")
    if not isinstance(samples, dict) or not all(isinstance(samples.get(k), str) and samples[k] for k in ("good", "bad")):
        _fail(name, "needs good and bad sample responses")
    return data


def load(root):
    """Return {scenario id: scenario}, validating every file."""
    folder = root / SCENARIO_DIR
    scenarios = {}
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        name = path.relative_to(root).as_posix()
        try:
            data = json.loads(read(root, name).decode("utf-8"))
        except json.JSONDecodeError as error:
            _fail(name, f"invalid JSON ({error})")
        scenarios[_validate(name, data)["id"]] = data
    if not scenarios:
        raise ValueError(f"{SCENARIO_DIR}: no scenarios found")
    return scenarios


def applies(scenario, role):
    for pattern in scenario["applies_to"]:
        if (pattern == "sensitive" and role["sensitive"]) or fnmatch.fnmatchcase(role["id"], pattern):
            return True
    return False


def find_role(families, role_id):
    for role in manifest.roles(families):
        if role["id"] == role_id:
            return role
    raise ValueError(f"unknown role {role_id!r}; find one with: python3 -B scripts/pack.py find <words>")


def grade(scenario, response):
    """Return failure strings; an empty list means every keyword rule held."""
    failures = []
    for grader in scenario["graders"]:
        if "must_match_any" in grader:
            if not any(re.search(p, response, re.I) for p in grader["must_match_any"]):
                failures.append(f"missing: {grader['why']}")
        else:
            hit = next((m.group(0) for p in grader["must_not_match"] for m in [re.search(p, response, re.I)] if m), None)
            if hit:
                failures.append(f"found {hit!r}: {grader['why']}")
    return failures


def prompt(root, families, role, scenario):
    """The adapter agent text for this role (frontmatter removed) followed by the scenario request."""
    family = next(f for f in families if f["id"] == role["family"])
    text = adapter.render(root, family, role).decode("utf-8").split("\n---\n", 1)[1].strip()
    return f"{text}\n\n=== USER REQUEST ===\n{scenario['prompt']}\n"


def selfcheck(scenarios):
    """Every scenario's good sample must pass and its bad sample must fail, proving the rules discriminate."""
    problems = []
    for sid, scenario in scenarios.items():
        if grade(scenario, scenario["samples"]["good"]):
            problems.append(f"{sid}: good sample fails: {grade(scenario, scenario['samples']['good'])}")
        if not grade(scenario, scenario["samples"]["bad"]):
            problems.append(f"{sid}: bad sample passes every rule")
    if problems:
        raise ValueError("\n".join(problems))
    return len(scenarios)
