# SPDX-License-Identifier: Apache-2.0
"""Produce the generated text files: indexes, registry, combined packs and the starter pack."""
import json
import posixpath
import re
from urllib.parse import urlsplit

from . import cards
from .config import (PACK_DIR, REGISTRY, STARTER, STARTER_SECTIONS, read, version)


def _text(root, name, overlay=None):
    return read(root, name, overlay).decode("utf-8").rstrip() + "\n"


def _combine(header, root, names, overlay, destination):
    text = header
    for name in names:
        def rebase(match):
            target = match.group(2)
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                return match.group(0)
            path = posixpath.normpath(posixpath.join(posixpath.dirname(name), parsed.path))
            relative = posixpath.relpath(path, posixpath.dirname(destination))
            if parsed.fragment:
                relative += "#" + parsed.fragment
            return match.group(1) + relative + ")"
        body = re.sub(r"(!?\[[^\]\n]*\]\()([^)\n]+)\)", rebase, _text(root, name, overlay))
        text += f"\n<!-- Source: {name} -->\n" + body
    return text.encode("utf-8")


def starter(root):
    header = (
        "# Specialist starter pack, combined instructions\n\n"
        f"Version {version(root)}. Use these instructions when the user asks for this pack. "
        f"First confirm that all {len(STARTER_SECTIONS)} sections are readable. Then start with the "
        "user's short business description and optional website. Respect higher-priority host "
        "rules and the materials-only boundary. Separate specialist files are the editable "
        "sources; this is their combined copy.\n")
    return _combine(header, root, STARTER_SECTIONS, None, STARTER)


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


def family_pack(root, family, pack, overlay):
    names = list(family["coordinator"]) + [f"catalog/{family['id']}/INDEX.md"]
    names += [role["path"] for role in pack["roles"]]
    others = [other for other in family["packs"] if other is not pack]
    scope = "the user asks for this family pack"
    if others:
        scope = (f"the user asks for the {pack['name']} pack. It holds {len(pack['roles'])} of the "
                 f"{len(family['roles'])} {family['name']} specialists; the index lists them all. The others are in "
                 + "; ".join(f"{other['name']} ({pack_path(other)})" for other in others)
                 + ". When a handoff names a role outside this pack, write the handoff note and tell the user "
                 "which pack holds that role")
    header = (
        f"# {pack['name']} specialists, combined instructions\n\n"
        f"Version {version(root)}. Use these instructions when {scope}. "
        f"First confirm that all {len(names)} sections are readable. Then ask for the user's task and "
        "the material they can supply. Use only the specialists that add a distinct deliverable. "
        "Respect higher-priority host rules and the materials-only boundary. "
        f"Separate files in catalog/{family['id']}/ are the editable sources; this is their combined copy.\n")
    return _combine(header, root, names, overlay, pack_path(pack))


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


def pack_path(pack):
    return f"{PACK_DIR}/{pack['id']}.md"
