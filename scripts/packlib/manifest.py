# SPDX-License-Identifier: Apache-2.0
"""Load and validate the family and role manifest (catalog/families.json)."""
import json
import re

from .config import DEFAULT_COORDINATOR, MANIFEST, read

SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def _require(condition, message):
    if not condition:
        raise ValueError(f"{MANIFEST}: {message}")


def load(root):
    try:
        data = json.loads(read(root, MANIFEST).decode("utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{MANIFEST}: invalid JSON ({error})")
    _require(data.get("schema") == 1, "schema must be 1")
    families, seen_families, seen_ids = [], set(), set()
    for family in data.get("families", []):
        fid = family.get("id", "")
        _require(SLUG.fullmatch(fid) is not None, f"bad family id {fid!r}")
        _require(fid not in seen_families, f"duplicate family {fid}")
        seen_families.add(fid)
        for key in ("name", "purpose", "flow"):
            _require(isinstance(family.get(key), str) and family[key], f"{fid}: missing {key}")
        _require(isinstance(family.get("sensitive"), bool), f"{fid}: sensitive must be true or false")
        _require(not family["sensitive"] or family.get("notes"), f"{fid}: sensitive family needs notes")
        roles, slugs = [], set()
        for role in family.get("roles", []):
            slug = role.get("slug", "")
            _require(SLUG.fullmatch(slug) is not None, f"{fid}: bad slug {slug!r}")
            _require(slug not in slugs, f"{fid}: duplicate slug {slug}")
            _require(isinstance(role.get("name"), str) and role["name"], f"{fid}/{slug}: missing name")
            slugs.add(slug)
            role_id = f"{role.get('prefix', fid)}/{slug}"
            _require(role_id not in seen_ids, f"duplicate role id {role_id}")
            seen_ids.add(role_id)
            roles.append({"id": role_id, "slug": slug, "name": role["name"], "family": fid,
                          "family_name": family["name"], "sensitive": family["sensitive"],
                          "path": f"catalog/{fid}/{slug}.md"})
        _require(roles, f"{fid}: no roles")
        families.append({"id": fid, "name": family["name"], "sensitive": family["sensitive"],
                         "purpose": family["purpose"], "flow": family["flow"],
                         "notes": family.get("notes", ""),
                         "coordinator": tuple(family.get("coordinator", DEFAULT_COORDINATOR)),
                         "roles": roles})
    _require(families, "no families")
    total = sum(len(f["roles"]) for f in families)
    _require(total == data.get("total"), f"total says {data.get('total')} but roster has {total}")
    return families


def roles(families):
    return [role for family in families for role in family["roles"]]
