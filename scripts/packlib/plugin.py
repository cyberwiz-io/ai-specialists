# SPDX-License-Identifier: Apache-2.0
"""Generate the Claude Code marketplace, one plugin per family and the all-in-one bundle.

Formats (checked 2026-10-17): https://code.claude.com/docs/en/plugins-reference.md and
https://code.claude.com/docs/en/plugin-marketplaces.md. Plugin component paths may not leave the plugin folder, so each
family plugin carries its own copies of the skills and agents. The `ai-specialists-all` bundle has no copies: its
marketplace entry uses the repository root as its source and lists the root lead skills and every family's agents.

Each family plugin holds its role skills (user-invocable only, so 124 descriptions do not crowd the skill listing),
its team lead skill with the cards in references/, one worker agent per card and a copy of the cross-family reviewer.
The same lead folder is zipped for upload to claude.ai.
"""
import json
import re

from . import adapter, skills
from .config import ARCHIVE_PREFIX, MARKETPLACE, PLUGINS_DIR, REPOSITORY, SKILLS_DIR, read, version

MARKETPLACE_NAME = "ai-specialists"
BUNDLE = "ai-specialists-all"
PLUGIN_NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
OWNER = {"name": "cyberwiz-io"}
# Role skills in a plugin stay out of the model's skill listing; the worker agents and the lead cover routing.
ROLE_SKILL_EXTRA = ("disable-model-invocation: true",)
# The all-in-one bundle's always-loaded descriptions must stay well under Claude Code's 15,000-token agent warning.
BUNDLE_TOKEN_LIMIT = 7500


def semver(root):
    return version(root) + ".0"


def plugin_dir(family):
    return f"{PLUGINS_DIR}/{family['id']}"


def skill_dir(family):
    """The family's lead skill folder inside its plugin."""
    return f"{plugin_dir(family)}/skills/{skills.lead_name(family)}"


def _json(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def plugin_json(root, family):
    return _json({
        "name": family["id"], "version": semver(root),
        "description": f"{family['name']}: {len(family['roles'])} materials-only specialists as skills and subagents, "
                       f"with a team lead (/{family['id']}:{skills.lead_name(family)}). {family['purpose']}",
        "author": OWNER, "homepage": REPOSITORY, "repository": REPOSITORY, "license": "CC-BY-4.0",
        "keywords": ["specialists", "materials-only", "agent-skills", family["id"]]})


def bundle_agents(families):
    """Each worker agent once, from its own family plugin."""
    return [f"./{adapter.agent_path(role)}" for family in families for role in family["roles"]]


def bundle_skills(families):
    return [f"./{skills.lead_dir(family)}" for family in families] + [f"./{SKILLS_DIR}/{skills.SPECIALISTS}"]


def marketplace(root, families):
    entries = [{"name": family["id"], "source": "./" + plugin_dir(family),
                "description": f"{family['name']}: {family['purpose']}", "version": semver(root),
                "category": "productivity", "tags": ["materials-only", family["id"]]}
               for family in families]
    entries.append({
        "name": BUNDLE, "source": "./", "strict": False,
        "description": "Every family in one plugin: all 124 specialist subagents, the 17 team leads and the "
                       "cross-family /specialists lead.",
        "version": semver(root), "author": OWNER, "homepage": REPOSITORY, "repository": REPOSITORY,
        "license": "CC-BY-4.0", "category": "productivity", "tags": ["materials-only", "bundle"],
        "skills": bundle_skills(families), "agents": bundle_agents(families)})
    return _json({
        "name": MARKETPLACE_NAME, "owner": OWNER,
        "description": "Materials-only specialist skills, subagents and team leads, one plugin per family plus a bundle.",
        "metadata": {"description": "Materials-only specialist skills, subagents and team leads, one plugin per "
                                    "family plus a bundle.", "version": semver(root)},
        "plugins": entries})


def outputs(root, families):
    """Map every plugin file path to its bytes: marketplace, plugin manifests, skills, references and agents."""
    files = {MARKETPLACE: marketplace(root, families)}
    reviewer = skills.reviewer_role(families)
    orchestration = next(family for family in families if family["id"] == "orchestration")
    for family in families:
        base = plugin_dir(family)
        files[f"{base}/.claude-plugin/plugin.json"] = plugin_json(root, family)
        files.update(skills.folder(root, family, families, skill_dir(family), skills.lead_skill(root, family, families)))
        for role in family["roles"]:
            files[f"{base}/skills/{skills.role_name(role)}/SKILL.md"] = skills.role_skill(root, family, role, ROLE_SKILL_EXTRA)
            files[adapter.agent_path(role)] = adapter.render(root, family, role)
        if family is not orchestration:
            files[adapter.agent_path(reviewer, family["id"])] = adapter.render(root, orchestration, reviewer)
    files[f"{plugin_dir(orchestration)}/skills/{skills.SPECIALISTS}/SKILL.md"] = skills.specialists_skill(root, families)
    return files


def skill_archive_name(root, family):
    return f"{ARCHIVE_PREFIX}{version(root)}-skill-{family['id']}.zip"


def skill_members(family, generated):
    """The lead skill folder as it must appear in an upload ZIP: <name>/SKILL.md and <name>/references/..."""
    folder = skills.lead_dir(family) + "/"
    name = skills.lead_name(family)
    return {f"{name}/{path[len(folder):]}": data for path, data in generated.items() if path.startswith(folder)}


def _frontmatter(text):
    return skills.parse_frontmatter(text)[0]


def _tokens(chars):
    return (chars + 3) // 4


def bundle_description_tokens(families, generated):
    total = 0
    for path in bundle_skills(families):
        total += len(_frontmatter(generated[path[2:] + "/SKILL.md"].decode("utf-8"))["description"])
    for path in bundle_agents(families):
        total += len(_frontmatter(generated[path[2:]].decode("utf-8"))["description"])
    return _tokens(total)


def _plugin_entry_problems(root, entry, generated, families):
    failures, name = [], entry.get("name", "")
    if not PLUGIN_NAME.fullmatch(str(name)) or str(name).startswith(("claude", "anthropic")):
        failures.append(f"{MARKETPLACE}: bad plugin name {name!r}")
    source = entry.get("source", "")
    if not isinstance(source, str) or not source.startswith("./") or ".." in source:
        return failures + [f"{MARKETPLACE}: {name}: source must be a ./ path inside the repository"]
    folder = source[2:].rstrip("/")
    if entry.get("strict", True):
        manifest_path = f"{folder}/.claude-plugin/plugin.json"
        if manifest_path not in generated:
            return failures + [f"{MARKETPLACE}: {name}: {source} has no .claude-plugin/plugin.json"]
        manifest = json.loads(generated[manifest_path])
        if manifest.get("name") != name:
            failures.append(f"{manifest_path}: name {manifest.get('name')!r} differs from the marketplace entry {name}")
        for key in ("version", "description", "author"):
            if not manifest.get(key):
                failures.append(f"{manifest_path}: missing {key}")
        if manifest.get("version") != entry.get("version"):
            failures.append(f"{manifest_path}: version differs from the marketplace entry")
        if not any(path.startswith(folder + "/skills/") for path in generated):
            failures.append(f"{MARKETPLACE}: {name}: plugin has no skills")
    for path in entry.get("skills", []):
        if not path.startswith("./") or ".." in path or f"{path[2:]}/SKILL.md" not in generated:
            failures.append(f"{MARKETPLACE}: {name}: skill path {path} has no SKILL.md")
    for path in entry.get("agents", []):
        if not path.startswith("./") or ".." in path or path[2:] not in generated:
            failures.append(f"{MARKETPLACE}: {name}: agent path {path} does not exist")
    return failures


def problems(root, families, generated):
    """Failures in the shapes Claude Code and claude.ai require of the marketplace, plugins, skills and agents."""
    failures = []
    guide = read(root, "docs/INSTALL.md").decode("utf-8")
    try:
        market = json.loads(generated[MARKETPLACE])
    except (KeyError, json.JSONDecodeError) as error:
        return [f"{MARKETPLACE}: unreadable ({error})"]
    for key in ("name", "owner", "plugins"):
        if not market.get(key):
            failures.append(f"{MARKETPLACE}: missing {key}")
    names = [entry.get("name") for entry in market.get("plugins", [])]
    if len(set(names)) != len(names):
        failures.append(f"{MARKETPLACE}: duplicate plugin names")
    if sorted(names) != sorted([family["id"] for family in families] + [BUNDLE]):
        failures.append(f"{MARKETPLACE}: must list every family plugin and {BUNDLE}")
    for entry in market.get("plugins", []):
        failures += _plugin_entry_problems(root, entry, generated, families)
    for family in families:
        if f"`{family['id']}`" not in guide:
            failures.append(f"docs/INSTALL.md: does not list plugin {family['id']}")
    for path, data in generated.items():
        parts = path.split("/")
        text = data.decode("utf-8") if path.endswith(".md") else ""
        if path.endswith("/SKILL.md") and parts[0] in (SKILLS_DIR, PLUGINS_DIR):
            failures += skills.problems(path, text, parts[-2], spec_only=not is_plugin_role_skill(parts))
        if parts[0] == PLUGINS_DIR and len(parts) == 4 and parts[2] == "agents":
            failures += agent_problems(path, text)
        if "core-" in path or re.search(r"\bcore-[a-z]", text):
            failures.append(f"{path}: uses the retired core- prefix")
        for target in re.findall(r"\]\((references/[^)]+)\)", text) if path.endswith("/SKILL.md") else []:
            if path.rsplit("/", 1)[0] + "/" + target not in generated:
                failures.append(f"{path}: links to missing {target}")
    tokens = bundle_description_tokens(families, generated)
    if tokens > BUNDLE_TOKEN_LIMIT:
        failures.append(f"{BUNDLE}: always-loaded descriptions are about {tokens} tokens; keep them under {BUNDLE_TOKEN_LIMIT}")
    return failures


def is_plugin_role_skill(parts):
    """Role skill copies inside a plugin may add Claude Code keys; every other skill keeps to the spec for claude.ai."""
    return (parts[0] == PLUGINS_DIR and len(parts) == 5 and not parts[3].endswith("-lead")
            and parts[3] != skills.SPECIALISTS)


def agent_problems(path, text):
    """Worker agents: valid name, a short description, read-only tools and never the Agent tool."""
    failures = []
    try:
        fields = _frontmatter(text)
    except (ValueError, json.JSONDecodeError):
        return [f"{path}: unreadable frontmatter"]
    if fields.get("name") + ".md" != path.rsplit("/", 1)[-1] or not PLUGIN_NAME.fullmatch(fields.get("name", "")):
        failures.append(f"{path}: name must match the file name")
    if not 0 < len(fields.get("description", "")) <= 150:
        failures.append(f"{path}: description must be 1-150 characters")
    tools = [tool.strip() for tool in fields.get("tools", "").split(",")]
    if "Agent" in tools or any(tool.startswith("Agent(") for tool in tools):
        failures.append(f"{path}: worker agents may not have the Agent tool")
    if fields.get("disallowedTools") != adapter.DISALLOWED:
        failures.append(f"{path}: worker agents must set disallowedTools: {adapter.DISALLOWED}")
    if set(tools) != set(adapter.TOOLS.split(", ")) or len(tools) != 3:
        failures.append(f"{path}: worker tools must be exactly {adapter.TOOLS}")
    return failures
