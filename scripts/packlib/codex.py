# SPDX-License-Identifier: Apache-2.0
"""Generate the Codex plugin (lead skills only), one Codex custom agent per role and lead, and the repo marketplace.

Formats (checked 2026-10-17): https://developers.openai.com/codex/plugins/build ,
https://learn.chatgpt.com/docs/build-skills and https://learn.chatgpt.com/codex/agent-configuration/subagents .
Only the team leads and the cross-family lead go in the plugin, because Codex budgets its skill listing at about 2% of
context (8,000 characters when unknown) and 142 descriptions would not fit; single-role skills come from the root
`skills/` folder via `npx skills add`. Plugins carry no agents, so users copy `agents/*.toml` into `.codex/agents/`.
No `model` (Codex model names differ) and no `sandbox_mode` (not overridable per agent). Not yet tested in Codex.
"""
import json
import re

from . import adapter, skills
from .config import ADAPTERS_DIR, REPOSITORY
from .plugin import OWNER, semver

try:
    import tomllib
except ImportError:  # Python before 3.11: problems() falls back to a key check
    tomllib = None

BASE = f"{ADAPTERS_DIR}/codex"
PLUGIN_JSON = f"{BASE}/.codex-plugin/plugin.json"
MARKETPLACE = ".agents/plugins/marketplace.json"
NAME = "ai-specialists"
LEAD_EFFORT = "medium"
# Codex has no "max" reasoning effort; its highest is "xhigh".
EFFORT = {"max": "xhigh"}
DESCRIPTION_MAX = 1024


def _json(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def plugin_json(root, families):
    return _json({
        "name": NAME, "version": semver(root),
        "description": f"Materials-only team leads for {len(families)} specialist families plus a cross-family "
                       "lead. They plan, brief the specialist agents, review and return one deliverable.",
        "author": OWNER, "homepage": REPOSITORY, "repository": REPOSITORY, "license": "CC-BY-4.0",
        "keywords": ["specialists", "materials-only", "agent-skills", "team-lead"],
        "skills": "./skills/",
        "interface": {"displayName": "AI Specialists",
                      "shortDescription": "Materials-only specialist team leads for plans, drafts and reviews.",
                      "developerName": "cyberwiz-io", "category": "Productivity"}})


def marketplace():
    return _json({
        "name": NAME, "interface": {"displayName": "AI Specialists"},
        "plugins": [{"name": NAME, "source": {"source": "local", "path": f"./{BASE}"},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": "Productivity"}]})


def toml_multiline(text):
    """A TOML multi-line basic string whose value is exactly text."""
    text = text.replace("\\", "\\\\")
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: f"\\u{ord(m.group()):04x}", text)
    tail = '\\"' if text.endswith('"') else ""  # a closing quote must not touch the delimiter
    text = text[:-1] if tail else text
    text = text.replace('""', '"\\"')  # no three unescaped quotes in a row
    return f'"""\n{text}{tail}"""'


def agent_toml(source, name, description, instructions, effort=None, shell=True):
    lines = [f"# Generated from {source} by scripts/pack.py build. Do not edit.",
             f"name = {json.dumps(name)}", f"description = {json.dumps(description)}"]
    if effort:
        lines.append(f"model_reasoning_effort = {json.dumps(EFFORT.get(effort, effort))}")
    lines.append(f"developer_instructions = {toml_multiline(instructions)}")
    if not shell:
        lines += ["", "[features]", "shell_tool = false"]
    return ("\n".join(lines) + "\n").encode("utf-8")


def role_instructions(family, role, text):
    sensitive = "\n\n" + skills.SENSITIVE if family["sensitive"] else ""
    return f"{adapter.note(role)}{sensitive}\n\n---\n\n{text}"


def agent_path(name):
    return f"{BASE}/agents/{name}.toml"


def outputs(root, families):
    files = {PLUGIN_JSON: plugin_json(root, families), MARKETPLACE: marketplace()}
    for family in families:
        name = skills.lead_name(family)
        files.update(skills.folder(root, family, families, f"{BASE}/skills/{name}",
                                   skills.lead_skill(root, family, families)))
        files[agent_path(name)] = agent_toml(
            f"catalog/{family['id']}/", name, skills.lead_description(family),
            skills.lead_body(root, family, families, references=False), LEAD_EFFORT)
        for role in family["roles"]:
            text = skills.card_text(root, role)
            files[agent_path(skills.role_name(role))] = agent_toml(
                role["path"], skills.role_name(role), skills.description(role, text),
                role_instructions(family, role, text), role["effort"], role["commands"])
    files[f"{BASE}/skills/{skills.SPECIALISTS}/SKILL.md"] = skills.specialists_skill(root, families)
    files[agent_path(skills.SPECIALISTS)] = agent_toml(
        "catalog/", skills.SPECIALISTS, skills.SPECIALISTS_DESCRIPTION, skills.specialists_body(root, families),
        LEAD_EFFORT)
    return files


def _parse(text):
    if tomllib:
        return tomllib.loads(text)
    fields = {}  # minimal fallback: top-level keys present, simple strings decoded
    for line in text.splitlines():
        key, sep, value = line.partition(" = ")
        if sep and re.fullmatch(r"[a-z_]+", key):
            fields[key] = json.loads(value) if value.startswith('"') and not value.startswith('"""') else value
    if "shell_tool = false" in text:
        fields["features"] = {"shell_tool": False}
    return fields


def _agent_problems(path, data, role):
    text = data.decode("utf-8")
    try:
        fields = _parse(text)
    except (ValueError, json.JSONDecodeError) as error:
        return [f"{path}: unreadable TOML ({error})"]
    failures, stem = [], path.rsplit("/", 1)[-1][:-len(".toml")]
    if fields.get("name") != stem:
        failures.append(f"{path}: name {fields.get('name')!r} differs from the file name")
    description = fields.get("description")
    if not isinstance(description, str) or not description or len(description) > DESCRIPTION_MAX:
        failures.append(f"{path}: description must be 1-{DESCRIPTION_MAX} characters")
    if not fields.get("developer_instructions"):
        failures.append(f"{path}: missing developer_instructions")
    tables = [fields] + [value for value in fields.values() if isinstance(value, dict)]
    if any("sandbox_mode" in table or "model" in table for table in tables):
        failures.append(f"{path}: must not set model or sandbox_mode")
    if role is not None and not role["commands"] and fields.get("features", {}).get("shell_tool") is not False:
        failures.append(f"{path}: read-only role needs [features] shell_tool = false")
    if not text.startswith("# Generated from "):
        failures.append(f"{path}: missing the generated marker")
    return failures


def problems(root, families, generated):
    """Failures in the shapes Codex requires of the plugin, marketplace, skills and custom agents."""
    failures = []
    try:
        manifest = json.loads(generated[PLUGIN_JSON])
        market = json.loads(generated[MARKETPLACE])
    except (KeyError, json.JSONDecodeError) as error:
        return [f"{BASE}: plugin.json or {MARKETPLACE} unreadable ({error})"]
    for key in ("name", "version"):
        if not manifest.get(key):
            failures.append(f"{PLUGIN_JSON}: missing {key}")
    if manifest.get("skills") != "./skills/":
        failures.append(f"{PLUGIN_JSON}: skills must be ./skills/")
    elif not any(path.startswith(f"{BASE}/skills/") for path in generated):
        failures.append(f"{PLUGIN_JSON}: skills folder is empty")
    for entry in market.get("plugins", []):
        path = entry.get("source", {}).get("path", "")
        folder = path[2:].rstrip("/") if path.startswith("./") and ".." not in path else None
        if folder is None or f"{folder}/.codex-plugin/plugin.json" not in generated:
            failures.append(f"{MARKETPLACE}: {entry.get('name')}: {path} has no .codex-plugin/plugin.json")
        elif json.loads(generated[f"{folder}/.codex-plugin/plugin.json"]).get("name") != entry.get("name"):
            failures.append(f"{MARKETPLACE}: {entry.get('name')}: name differs from its plugin.json")
    if not market.get("plugins"):
        failures.append(f"{MARKETPLACE}: no plugins")
    roles = {agent_path(skills.role_name(role)): role for family in families for role in family["roles"]}
    expected = set(roles) | {agent_path(skills.lead_name(f)) for f in families} | {agent_path(skills.SPECIALISTS)}
    agents = {path for path in generated if path.startswith(f"{BASE}/agents/")}
    if agents != expected:
        failures.append(f"{BASE}/agents: missing {sorted(expected - agents)}, unexpected {sorted(agents - expected)}")
    for path in sorted(agents):
        failures += _agent_problems(path, generated[path], roles.get(path))
    for path, data in generated.items():
        if path.startswith(f"{BASE}/skills/") and path.endswith("/SKILL.md"):
            failures += skills.problems(path, data.decode("utf-8"), path.split("/")[-2], spec_only=True)
    return failures
