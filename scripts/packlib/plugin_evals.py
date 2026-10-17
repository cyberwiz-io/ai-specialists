# SPDX-License-Identifier: Apache-2.0
"""Generate `claude plugin eval` suites from the card fixtures, for the families listed in evals/plugin/.

Format: https://code.claude.com/docs/en/plugin-evals.md (checked 2026-10-17; Claude Code 2.1.269 or later). Each case is
a JSON `case.yaml` (JSON is valid YAML) in `plugins/<family>/evals/<case>/`, where `claude plugin eval plugins/<family>`
finds it. The run adds a no-plugin baseline arm by default. The source is `evals/plugin/<family>.json`, which names
card fixtures from `evals/fixtures/` and adds one team task for the family's lead.
"""
import json

from . import evals, skills
from .config import PLUGINS_DIR, read

SOURCE_DIR = "evals/plugin"
TOOLS = ["Read", "Glob", "Grep", "Skill", "Agent"]


def _prompt(fixture):
    return fixture["request"].rstrip() + "\n\n" + evals._material(fixture)


def _criteria(accepted, fixture):
    lines = ["Grade the final reply. Pass only if every item below holds; quote the reply as evidence.", "",
             "Acceptance (from the specialist card):"]
    lines += [f"- {item}" for item in accepted]
    lines += ["", "Expected traits:"] + [f"- {item}" for item in fixture["traits"]]
    lines += ["", "Fail if the reply does any of these:"] + [f"- {item}" for item in fixture["must_not"]]
    return "\n".join(lines)


def _case(name, fixture, accepted, spec, tags, extra=()):
    return {"schema_version": "1.1", "name": name, "description": f"Fixture {fixture['id']}", "tags": tags,
            "runs": spec["runs"],
            "execution": {"max_turns": spec["max_turns"], "timeout_seconds": spec["timeout_seconds"],
                          "allowed_tools": TOOLS, "prompt": _prompt(fixture)},
            "graders": [{"name": "acceptance", "type": "llm", "criteria": _criteria(accepted, fixture)}, *extra]}


def _json(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def load_specs(root, families):
    folder = root / SOURCE_DIR
    specs = []
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        name = f"{SOURCE_DIR}/{path.name}"
        try:
            spec = json.loads(read(root, name).decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"{name}: invalid JSON ({error})")
        family = next((f for f in families if f["id"] == spec.get("family") == path.stem), None)
        if spec.get("schema") != 1 or family is None:
            raise ValueError(f"{name}: needs \"schema\": 1 and \"family\" matching the file name")
        for key in ("runs", "max_turns", "timeout_seconds"):
            if not isinstance(spec.get(key), int) or spec[key] < 1:
                raise ValueError(f"{name}: {key} must be a positive whole number")
        specs.append((name, family, spec))
    return specs


def outputs(root, families):
    files = {}
    fixtures = {fixture["id"]: fixture for fixture in evals.problems(root, families)[0]}
    for name, family, spec in load_specs(root, families):
        base = f"{PLUGINS_DIR}/{family['id']}/evals"
        for fixture_id in spec.get("fixtures", []):
            fixture = fixtures.get(fixture_id)
            if fixture is None or fixture["family"] is not family:
                raise ValueError(f"{name}: {fixture_id} is not a {family['id']} fixture")
            accepted = evals.criteria(read(root, fixture["card"]["path"]).decode("utf-8"))
            case = fixture_id.split("/", 1)[1].replace("/", "--")
            files[f"{base}/{case}/case.yaml"] = _json(_case(case, fixture, accepted, spec, [fixture["kind"]]))
        team = spec.get("team")
        if team:
            for problem in evals.lint(" ".join([team.get("request", "")] + team.get("input", []) + team.get("traits", []))):
                raise ValueError(f"{name}: team task {problem}")
            reviewer = read(root, "catalog/orchestration/cross-family-reviewer.md").decode("utf-8")
            minimum = team.get("min_agents", 2)
            if not isinstance(minimum, int) or minimum < 2:
                raise ValueError(f"{name}: team min_agents must be a whole number of at least 2")
            used = {"name": "spawned-specialists", "type": "tool_used", "tool": "Agent", "min": minimum, "arm": "with-only"}
            case = team["id"].split("/", 1)[1]
            files[f"{base}/{case}/case.yaml"] = _json(
                _case(case, {**{k: v for k, v in team.items() if k != "min_agents"}, "kind": "team"}, evals.criteria(reviewer), spec, ["team", skills.lead_name(family)], [used]))
    return files
