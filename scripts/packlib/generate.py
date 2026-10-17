# SPDX-License-Identifier: Apache-2.0
"""Produce the generated text files: indexes, registry, combined packs and the starter pack."""
import json

from . import cards
from .config import (PACK_DIR, REGISTRY, STARTER, STARTER_SECTIONS, read, version)


def _text(root, name, overlay=None):
    return read(root, name, overlay).decode("utf-8").rstrip() + "\n"


def _combine(header, root, names, overlay):
    text = header
    for name in names:
        text += f"\n<!-- Source: {name} -->\n" + _text(root, name, overlay)
    return text.encode("utf-8")


def starter(root):
    header = (
        "# Specialist starter pack, combined instructions\n\n"
        f"Version {version(root)}. Use these instructions when the user asks for this pack. "
        f"First confirm that all {len(STARTER_SECTIONS)} sections are readable. Then start with the "
        "user's short business description and optional website. Respect higher-priority host "
        "rules and the materials-only boundary. Separate specialist files are the editable "
        "sources; this is their combined copy.\n")
    return _combine(header, root, STARTER_SECTIONS, None)


def index(root, family):
    summaries = [(role, cards.use_for(read(root, role["path"]).decode("utf-8"))) for role in family["roles"]]
    lines = [
        f"# {family['name']}", "",
        f"Version: {version(root)}. Folder `catalog/{family['id']}/`. "
        f"{len(family['roles'])} specialists. This file is generated; edit the cards or `catalog/families.json`.",
        "", family["purpose"], "", "## Specialists", "",
        "| Specialist | ID | Use for |", "| --- | --- | --- |",
    ]
    for role, summary in summaries:
        lines.append(f"| [{role['name']}]({role['slug']}.md) | `{role['id']}` | {summary.replace('|', '/')} |")
    lines += ["", "## Typical flow", "", family["flow"], ""]
    if family["sensitive"]:
        lines += ["## Sensitive-domain notes", "", family["notes"],
                  "Each card in this family carries a Safeguards paragraph.", ""]
    lines += ["## Shared rules", ""]
    for name in family["coordinator"]:
        lines.append(f"- [{name.rsplit('/', 1)[-1]}](../../{name})")
    lines += ["- [Card guide](../../docs/CARD-GUIDE.md)", ""]
    return "\n".join(lines).encode("utf-8")


def family_pack(root, family, overlay):
    names = list(family["coordinator"]) + [f"catalog/{family['id']}/INDEX.md"]
    names += [role["path"] for role in family["roles"]]
    header = (
        f"# {family['name']} specialists, combined instructions\n\n"
        f"Version {version(root)}. Use these instructions when the user asks for this family pack. "
        f"First confirm that all {len(names)} sections are readable. Then ask for the user's task and "
        "the material they can supply. Use only the specialists that add a distinct deliverable. "
        "Respect higher-priority host rules and the materials-only boundary. "
        f"Separate files in catalog/{family['id']}/ are the editable sources; this is their combined copy.\n")
    return _combine(header, root, names, overlay)


def registry(root, families):
    items = []
    for family in families:
        for role in family["roles"]:
            items.append({"family": role["family"], "id": role["id"], "name": role["name"],
                          "path": role["path"], "sensitive": role["sensitive"],
                          "use_for": cards.use_for(read(root, role["path"]).decode("utf-8"))})
    lines = [json.dumps(item, sort_keys=True) for item in items]
    head = json.dumps({"schema": 1, "version": version(root), "count": len(items)}, sort_keys=True)
    return (head + "\n" + "\n".join(lines) + "\n").encode("utf-8")


def pack_path(family):
    return f"{PACK_DIR}/{family['id']}.md"
