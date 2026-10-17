# SPDX-License-Identifier: Apache-2.0
"""Generate one GitHub Copilot custom agent per role, one per team lead and the cross-family lead.

Format: https://docs.github.com/en/copilot/reference/custom-agents-configuration (checked 2026-10-17). Copilot cannot
limit shell commands to an allowlist, so every role, code roles included, gets read and search only; leads also get
agent. No `model` field. Leads drop their references/ links, since these files sit outside any skill folder.
Not yet tested in Copilot.
"""
import json
import re

from . import adapter, skills
from .config import ADAPTERS_DIR

BASE = f"{ADAPTERS_DIR}/copilot/agents"
SUFFIX = ".agent.md"
ROLE_TOOLS = ["read", "search"]
LEAD_TOOLS = ["read", "search", "agent"]
WORKER_DENIED = {"agent", "edit", "execute", "web"}
BODY_MAX = 30000  # Copilot's limit on an agent's prompt
DESCRIPTION_MAX = 1024
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


def agent_path(name):
    return f"{BASE}/{name}{SUFFIX}"


def render(name, description, tools, body):
    head = ["---", f"name: {json.dumps(name)}", f"description: {json.dumps(description)}",
            f"tools: {json.dumps(tools)}", "---"]
    return ("\n".join(head) + "\n\n" + body.rstrip() + "\n").encode("utf-8")


def role_body(family, role, text):
    sensitive = f"{skills.SENSITIVE}\n\n" if family["sensitive"] else ""
    return (f"<!-- Generated from {role['path']} by scripts/pack.py build. Do not edit. -->\n\n"
            f"{adapter.NOTE}\n\n{sensitive}---\n\n{text}")


def outputs(root, families):
    files = {}
    for family in families:
        name = skills.lead_name(family)
        files[agent_path(name)] = render(name, skills.lead_description(family), LEAD_TOOLS,
                                         skills.lead_body(root, family, families, references=False))
        for role in family["roles"]:
            text = skills.card_text(root, role)
            files[agent_path(skills.role_name(role))] = render(
                skills.role_name(role), skills.description(role, text), ROLE_TOOLS, role_body(family, role, text))
    files[agent_path(skills.SPECIALISTS)] = render(skills.SPECIALISTS, skills.SPECIALISTS_DESCRIPTION, LEAD_TOOLS,
                                                   skills.specialists_body(root, families))
    return files


def _parse(text):
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("no frontmatter")
    front, body = text[4:].split("\n---\n", 1)
    fields = {}
    for line in front.splitlines():
        key, _, value = line.partition(": ")
        fields[key] = json.loads(value)
    return fields, body


def problems(root, families, generated):
    """Failures in the shape Copilot requires of custom agent files."""
    failures = []
    roles = {agent_path(skills.role_name(role)) for family in families for role in family["roles"]}
    leads = {agent_path(skills.lead_name(family)) for family in families} | {agent_path(skills.SPECIALISTS)}
    agents = {path for path in generated if path.startswith(BASE + "/")}
    if agents != roles | leads:
        failures.append(f"{BASE}: missing {sorted((roles | leads) - agents)}, unexpected {sorted(agents - roles - leads)}")
    for path in sorted(agents):
        try:
            fields, body = _parse(generated[path].decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as error:
            failures.append(f"{path}: unreadable frontmatter ({error})")
            continue
        name = fields.get("name", "")
        if not isinstance(name, str) or not skills.SKILL_NAME.fullmatch(name):
            failures.append(f"{path}: name {name!r} is not lowercase letters, digits and single hyphens")
        elif path.rsplit("/", 1)[-1] != name + SUFFIX:
            failures.append(f"{path}: file name differs from name {name}")
        description = fields.get("description")
        if not isinstance(description, str) or not description or len(description) > DESCRIPTION_MAX:
            failures.append(f"{path}: description must be 1-{DESCRIPTION_MAX} characters")
        if "model" in fields:
            failures.append(f"{path}: must not set model")
        if adapter.COMMAND_NOTE in body:
            failures.append(f"{path}: promises commands that Copilot agents cannot run")
        tools = fields.get("tools")
        if not isinstance(tools, list):
            failures.append(f"{path}: tools must be a list")
        elif path in roles and WORKER_DENIED & set(tools):
            failures.append(f"{path}: role agent has {', '.join(sorted(WORKER_DENIED & set(tools)))}")
        elif path in leads and "agent" not in tools:
            failures.append(f"{path}: lead needs the agent tool")
        if len(body) >= BODY_MAX:
            failures.append(f"{path}: body is {len(body)} characters; Copilot's limit is {BODY_MAX}")
        if "Generated from" not in body.lstrip().split("\n", 1)[0]:
            failures.append(f"{path}: missing the generated marker")
        for target in LINK.findall(body):
            if not target.startswith(("https://", "http://", "mailto:", "#")):
                failures.append(f"{path}: local link {target} would not resolve once copied")
    return failures
