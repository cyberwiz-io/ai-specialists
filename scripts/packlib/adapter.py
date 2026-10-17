# SPDX-License-Identifier: Apache-2.0
"""Render one read-only Claude Code subagent per specialist card; the plugin generator places them in each family plugin."""
import json
import re

from . import cards
from .config import PLUGINS_DIR, read

TOOLS = "Read, Grep, Glob"
NOTE = (
    "You are running as a Claude Code subagent with read-only tools. You cannot run commands, edit files, "
    "browse, or contact anyone, and you must not claim that you did. Work from the material the user supplies "
    "or points you to, and return the deliverable as text. A handoff line is a recommendation for the main "
    "conversation to act on; you cannot call another specialist yourself.")


def agent_name(role):
    return role["id"].replace("/", "-")


def agent_path(role):
    return f"{PLUGINS_DIR}/{role['family']}/agents/{agent_name(role)}.md"


def _sections(text):
    """Map second-level headings of a coordinator file to their full section text."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return {parts[i].strip(): f"## {parts[i].strip()}\n\n{parts[i + 1].strip()}\n" for i in range(1, len(parts) - 1, 2)}


def boundaries(root, family):
    """The Boundaries (and, for sensitive families, Sensitive domains) sections of the family's coordinator."""
    wanted = ["Boundaries"] + (["Sensitive domains"] if family["sensitive"] else [])
    found = {}
    for name in family["coordinator"]:
        for heading, body in _sections(read(root, name).decode("utf-8")).items():
            found.setdefault(heading, body)
    if "Boundaries" not in found:
        raise ValueError(f"{', '.join(family['coordinator'])}: no Boundaries section to embed in the adapter")
    return "\n".join(found[heading] for heading in wanted if heading in found)


def render(root, family, role):
    card = read(root, role["path"]).decode("utf-8").rstrip() + "\n"
    summary = cards.use_for(card)
    head = "\n".join([
        "---",
        f"name: {agent_name(role)}",
        f"description: {json.dumps('Materials-only specialist. ' + summary)}",
        f"tools: {TOOLS}",
        "model: inherit",
        "---"])
    body = (f"{head}\n\n<!-- Generated from {role['path']} by scripts/pack.py build. Do not edit. -->\n\n"
            f"{NOTE}\n\n{boundaries(root, family)}\n---\n\n{card}")
    return body.encode("utf-8")


def outputs(root, families):
    """Map each adapter file path to its bytes."""
    return {agent_path(role): render(root, family, role) for family in families for role in family["roles"]}
