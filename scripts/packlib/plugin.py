# SPDX-License-Identifier: Apache-2.0
"""Generate the Claude Code marketplace and one plugin per family: a skill with the cards as references, plus subagents.

The same skill folder is zipped for upload to claude.ai, so a user never has to paste a combined pack.
"""
import json
import re

from . import adapter, cards
from .config import MARKETPLACE, PLUGINS_DIR, REPOSITORY, SKILL_EXTRAS, ARCHIVE_PREFIX, read, version

MARKETPLACE_NAME = "ai-specialists"
SKILL_NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
NAME_MAX, DESCRIPTION_MAX = 64, 1024
OWNER = {"name": "cyberwiz-io"}


def semver(root):
    return version(root) + ".0"


def plugin_dir(family):
    return f"{PLUGINS_DIR}/{family['id']}"


def skill_dir(family):
    return f"{plugin_dir(family)}/skills/{family['id']}"


def _json(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def _text(root, name):
    return read(root, name).decode("utf-8").rstrip() + "\n"


def description(family):
    names = ", ".join(role["name"] for role in family["roles"])
    text = (f"{family['name']}: {family['purpose']} Roles: {names}. "
            "Materials only; never publishes, sends or runs anything.")
    if len(text) > DESCRIPTION_MAX:
        raise ValueError(f"{family['id']}: skill description is {len(text)} characters; the limit is {DESCRIPTION_MAX}")
    return text


def _references(family):
    """Reference files other than the cards: the first coordinator is the skill body, the rest are read on demand."""
    return list(family["coordinator"][1:]) + list(SKILL_EXTRAS.get(family["id"], ()))


def skill_md(root, family):
    rows = ["| Specialist | ID | Use for |", "| --- | --- | --- |"]
    for role in family["roles"]:
        summary = cards.use_for(read(root, role["path"]).decode("utf-8")).replace("|", "/")
        rows.append(f"| [{role['name']}](references/{role['slug']}.md) | `{role['id']}` | {summary} |")
    extras = _references(family)
    lines = [
        "---", f"name: {family['id']}", "allowed-tools: Read Grep Glob", f"description: {json.dumps(description(family))}", "---", "",
        f"<!-- Generated from catalog/{family['id']}/ and {family['coordinator'][0]} by scripts/pack.py build. Do not edit. -->",
        "", f"# {family['name']} specialists", "",
        f"Version {version(root)}. Use this skill when the user asks for work in this area. First ask for their task and "
        "the material they can supply. Select only the specialists that add a distinct deliverable. Each specialist is a "
        "card in `references/`: read a card only when you select that specialist, and follow it with the coordinator "
        "rules below. This skill's files take the place of the \"sections\" that a pasted pack would hold.", "",
        "## Specialists", "", *rows, "",
        "A handoff may name a role that is not listed here. It belongs to another family plugin: write the handoff note "
        f"and tell the user to add that family with `/plugin install <family>@{MARKETPLACE_NAME}` (or its skill on claude.ai).",
        "", "## Typical flow", "", family["flow"], ""]
    if family["sensitive"]:
        lines += ["## Sensitive-domain notes", "", family["notes"],
                  "Each card in this family carries a Safeguards paragraph.", ""]
    if extras:
        lines += ["## More files", ""]
        lines += [f"- [{name.rsplit('/', 1)[-1]}](references/{name.rsplit('/', 1)[-1]})" for name in extras]
        lines.append("")
    lines += ["---", "", _text(root, family["coordinator"][0])]
    return "\n".join(lines).encode("utf-8")


def plugin_json(root, family):
    return _json({
        "name": family["id"], "version": semver(root),
        "description": f"{family['name']}: {len(family['roles'])} materials-only specialists as one skill, specialist subagents and a team orchestrator. "
                       f"{family['purpose']}",
        "author": OWNER, "homepage": REPOSITORY, "repository": REPOSITORY, "license": "CC-BY-4.0",
        "keywords": ["specialists", "materials-only", family["id"]]})


def marketplace(root, families):
    return _json({
        "name": MARKETPLACE_NAME, "owner": OWNER,
        "metadata": {"description": "Materials-only specialist skills, subagents and team orchestrators, one plugin per family.",
                     "version": semver(root)},
        "plugins": [{"name": family["id"], "source": "./" + plugin_dir(family),
                     "description": f"{family['name']}: {family['purpose']}", "version": semver(root),
                     "category": "productivity", "tags": ["materials-only", family["id"]]}
                    for family in families]})


def outputs(root, families):
    """Map every plugin file path to its bytes: marketplace, plugin manifests, skills, references and agents."""
    files = {MARKETPLACE: marketplace(root, families)}
    for family in families:
        files[f"{plugin_dir(family)}/.claude-plugin/plugin.json"] = plugin_json(root, family)
        files[f"{skill_dir(family)}/SKILL.md"] = skill_md(root, family)
        for role in family["roles"]:
            files[f"{skill_dir(family)}/references/{role['slug']}.md"] = read(root, role["path"])
            files[adapter.agent_path(role)] = adapter.render(root, family, role)
        files[adapter.orchestrator_path(family)] = adapter.render_orchestrator(root, family)
        for name in _references(family):
            files[f"{skill_dir(family)}/references/{name.rsplit('/', 1)[-1]}"] = read(root, name)
    return files


def skill_archive_name(root, family):
    return f"{ARCHIVE_PREFIX}{version(root)}-skill-{family['id']}.zip"


def skill_members(family, generated):
    """The skill folder as it must appear in an upload ZIP: <name>/SKILL.md and <name>/references/..."""
    folder = skill_dir(family) + "/"
    return {f"{family['id']}/{name[len(folder):]}": data for name, data in generated.items() if name.startswith(folder)}


def problems(root, families, generated):
    """Failures in the shapes Claude Code and claude.ai require of plugins and skills."""
    failures = []
    guide = read(root, "docs/INSTALL.md").decode("utf-8")
    for family in families:
        fid = family["id"]
        if f"`{fid}`" not in guide:
            failures.append(f"docs/INSTALL.md: does not list plugin {fid}")
        if not SKILL_NAME.fullmatch(fid) or len(fid) > NAME_MAX or "claude" in fid or "anthropic" in fid:
            failures.append(f"{fid}: not a valid skill name")
        text = generated[f"{skill_dir(family)}/SKILL.md"].decode("utf-8")
        front = text.split("---\n", 2)[1]
        if "allowed-tools: Read Grep Glob\n" not in front:
            failures.append(f"{skill_dir(family)}/SKILL.md: missing allowed-tools, so card reads would prompt for permission")
        if f"name: {fid}\n" not in front or len(json.loads(front.split("description: ", 1)[1])) > DESCRIPTION_MAX:
            failures.append(f"{skill_dir(family)}/SKILL.md: bad name or description")
        for target in re.findall(r"\]\((references/[^)]+)\)", text):
            if f"{skill_dir(family)}/{target}" not in generated:
                failures.append(f"{skill_dir(family)}/SKILL.md: links to missing {target}")
    return failures
