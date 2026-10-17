# SPDX-License-Identifier: Apache-2.0
"""Generate the Gemini CLI extension manifest at the repository root.

Formats (checked 2026-10-17): https://geminicli.com/docs/extensions/reference/ ,
https://geminicli.com/docs/extensions/releasing/ and https://geminicli.com/docs/cli/skills/ . Gemini discovers skills in
the extension's skills/<name>/SKILL.md, and the root skills/ folder already holds every generated skill, so the
manifest is the only extra file. It sits at the root so `gemini extensions install <repository>` finds it. No
contextFileName is set: nothing loads into every conversation beyond the skill descriptions. Not yet tested on a host.
"""
import json
import re

from .config import SKILLS_DIR
from .plugin import MARKETPLACE_NAME, semver

MANIFEST = "gemini-extension.json"
NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def description(families):
    roles = sum(len(family["roles"]) for family in families)
    return (f"Materials-only specialist skills and team leads: {roles} role skills, {len(families)} family leads and "
            "the cross-family specialists lead. Plans, drafts and reviews only.")


def outputs(root, families):
    data = {"name": MARKETPLACE_NAME, "version": semver(root), "description": description(families)}
    return {MANIFEST: (json.dumps(data, indent=2) + "\n").encode("utf-8")}


def problems(root, families, generated):
    """Failures in the extension manifest and the skills it relies on."""
    try:
        data = json.loads(generated[MANIFEST])
    except (KeyError, json.JSONDecodeError) as error:
        return [f"{MANIFEST}: unreadable ({error})"]
    if not isinstance(data, dict):
        return [f"{MANIFEST}: must be a JSON object"]
    failures, name = [], data.get("name")
    if not isinstance(name, str) or not NAME.fullmatch(name) or name != MARKETPLACE_NAME:
        failures.append(f"{MANIFEST}: name must be {MARKETPLACE_NAME!r}, found {name!r}")
    if data.get("version") != semver(root):
        failures.append(f"{MANIFEST}: version must be {semver(root)}")
    if not str(data.get("description", "")).strip():
        failures.append(f"{MANIFEST}: missing description")
    if "contextFileName" in data:
        failures.append(f"{MANIFEST}: must not set contextFileName")
    if not any(re.fullmatch(rf"{SKILLS_DIR}/[^/]+/SKILL\.md", path) for path in generated):
        failures.append(f"{MANIFEST}: no {SKILLS_DIR}/*/SKILL.md for the extension to load")
    return failures
