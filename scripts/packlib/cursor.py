# SPDX-License-Identifier: Apache-2.0
"""Generate the Cursor plugin manifests beside the Claude Code family plugins.

Formats (checked 2026-10-17): https://cursor.com/docs/plugins , https://cursor.com/docs/reference/plugins and
https://github.com/cursor/plugin-template . Cursor discovers skills/<name>/SKILL.md and agents/*.md by default, so each
family plugin folder only gains .cursor-plugin/plugin.json, and the repository root gains .cursor-plugin/marketplace.json.
Not yet tested on a host.
"""
import json
import re

from . import skills
from .config import REPOSITORY
from .plugin import MARKETPLACE_NAME, OWNER, plugin_dir, semver

MARKETPLACE = ".cursor-plugin/marketplace.json"
NAME = re.compile(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?")


def _json(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def manifest_path(family):
    return f"{plugin_dir(family)}/.cursor-plugin/plugin.json"


def plugin_json(root, family):
    return _json({
        "name": family["id"], "version": semver(root),
        "description": f"{family['name']}: {len(family['roles'])} materials-only specialists as skills and agents, "
                       f"with a team lead ({skills.lead_name(family)}). {family['purpose']}",
        "author": OWNER, "homepage": REPOSITORY, "repository": REPOSITORY, "license": "CC-BY-4.0",
        "keywords": ["specialists", "materials-only", "agent-skills", family["id"]]})


def marketplace(root, families):
    return _json({
        "name": MARKETPLACE_NAME, "owner": OWNER,
        "metadata": {"description": "Materials-only specialist skills, agents and team leads, one plugin per family.",
                     "version": semver(root)},
        "plugins": [{"name": family["id"], "source": "./" + plugin_dir(family),
                     "description": f"{family['name']}: {family['purpose']}"} for family in families]})


def outputs(root, families):
    files = {MARKETPLACE: marketplace(root, families)}
    for family in families:
        files[manifest_path(family)] = plugin_json(root, family)
    return files


def problems(root, families, generated):
    """Failures in the Cursor marketplace and plugin manifests."""
    try:
        market = json.loads(generated[MARKETPLACE])
    except (KeyError, json.JSONDecodeError) as error:
        return [f"{MARKETPLACE}: unreadable ({error})"]
    failures = []
    if not NAME.fullmatch(str(market.get("name", ""))):
        failures.append(f"{MARKETPLACE}: bad marketplace name {market.get('name')!r}")
    entries = market.get("plugins", [])
    names = [entry.get("name") for entry in entries]
    for family in families:
        if names.count(family["id"]) != 1:
            failures.append(f"{MARKETPLACE}: must list {family['id']} exactly once")
    for entry in entries:
        name, source = entry.get("name"), entry.get("source", "")
        if not NAME.fullmatch(str(name)):
            failures.append(f"{MARKETPLACE}: bad plugin name {name!r}")
        if not isinstance(source, str) or not source.startswith("./") or ".." in source:
            failures.append(f"{MARKETPLACE}: {name}: source must be a ./ path inside the repository")
            continue
        path = f"{source[2:].rstrip('/')}/.cursor-plugin/plugin.json"
        if path not in generated:
            failures.append(f"{MARKETPLACE}: {name}: {source} has no .cursor-plugin/plugin.json")
            continue
        try:
            manifest = json.loads(generated[path])
        except json.JSONDecodeError as error:
            failures.append(f"{path}: unreadable ({error})")
            continue
        if manifest.get("name") != name:
            failures.append(f"{path}: name {manifest.get('name')!r} differs from the marketplace entry {name}")
        if not NAME.fullmatch(str(manifest.get("name", ""))):
            failures.append(f"{path}: bad plugin name {manifest.get('name')!r}")
    return failures
