# SPDX-License-Identifier: Apache-2.0
"""Load and validate the family and role manifest (catalog/families.json)."""
import json
import re

from .config import DEFAULT_COORDINATOR, MANIFEST, read

SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
MODELS = ("inherit", "sonnet", "haiku", "opus")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
# Default reasoning effort for each model tier; a role may set "effort" to override it. "inherit" leaves it to the host.
TIER_EFFORT = {"haiku": "low", "sonnet": "medium", "opus": "high", "inherit": None}
DEFAULT_MODEL = "sonnet"
ROLE_KEYS = {"slug", "name", "model", "effort", "commands"}


def _require(condition, message):
    if not condition:
        raise ValueError(f"{MANIFEST}: {message}")


def load(root):
    try:
        data = json.loads(read(root, MANIFEST).decode("utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{MANIFEST}: invalid JSON ({error})")
    _require(data.get("schema") == 1, "schema must be 1")
    families, seen_families, seen_ids, seen_packs = [], set(), set(), set()
    for family in data.get("families", []):
        fid = family.get("id", "")
        _require(SLUG.fullmatch(fid) is not None, f"bad family id {fid!r}")
        _require(fid not in seen_families, f"duplicate family {fid}")
        seen_families.add(fid)
        for key in ("name", "purpose", "flow"):
            _require(isinstance(family.get(key), str) and family[key], f"{fid}: missing {key}")
        _require(isinstance(family.get("sensitive"), bool), f"{fid}: sensitive must be true or false")
        _require(not family["sensitive"] or family.get("notes"), f"{fid}: sensitive family needs notes")
        model = family.get("model", DEFAULT_MODEL)
        _require(model in MODELS, f"{fid}: model must be one of {', '.join(MODELS)}")
        roles, slugs = [], set()
        for role in family.get("roles", []):
            slug = role.get("slug", "")
            unknown = sorted(set(role) - ROLE_KEYS)
            _require(not unknown, f"{fid}/{slug}: unknown key {', '.join(unknown)}")
            _require(SLUG.fullmatch(slug) is not None, f"{fid}: bad slug {slug!r}")
            _require(slug not in slugs, f"{fid}: duplicate slug {slug}")
            _require(isinstance(role.get("name"), str) and role["name"], f"{fid}/{slug}: missing name")
            slugs.add(slug)
            role_model = role.get("model", model)
            _require(role_model in MODELS, f"{fid}/{slug}: model must be one of {', '.join(MODELS)}")
            effort = role.get("effort", TIER_EFFORT[role_model])
            _require(effort is None or effort in EFFORTS, f"{fid}/{slug}: effort must be one of {', '.join(EFFORTS)}")
            _require(isinstance(role.get("commands", False), bool), f"{fid}/{slug}: commands must be true or false")
            role_id = f"{fid}/{slug}"
            _require(role_id not in seen_ids, f"duplicate role id {role_id}")
            seen_ids.add(role_id)
            roles.append({"id": role_id, "slug": slug, "name": role["name"], "family": fid,
                          "family_name": family["name"], "sensitive": family["sensitive"],
                          "model": role_model, "effort": effort, "commands": role.get("commands", False),
                          "path": f"catalog/{fid}/{slug}.md"})
        _require(roles, f"{fid}: no roles")
        packs = _packs(fid, family, roles, seen_packs)
        families.append({"id": fid, "name": family["name"], "sensitive": family["sensitive"],
                         "purpose": family["purpose"], "flow": family["flow"],
                         "notes": family.get("notes", ""),
                         "coordinator": tuple(family.get("coordinator", DEFAULT_COORDINATOR)),
                         "roles": roles, "packs": packs})
    _require(families, "no families")
    total = sum(len(f["roles"]) for f in families)
    _require(total == data.get("total"), f"total says {data.get('total')} but roster has {total}")
    return families


def _packs(fid, family, roles, seen):
    """Split a family into named combined packs; one pack named after the family when none are listed."""
    listed = family.get("packs")
    if listed is None:
        _require(fid not in seen, f"{fid}: pack id already used")
        seen.add(fid)
        return [{"id": fid, "name": family["name"], "roles": roles}]
    _require(isinstance(listed, list) and len(listed) >= 2, f"{fid}: packs must list at least two packs")
    by_slug, placed, packs = {role["slug"]: role for role in roles}, set(), []
    for pack in listed:
        pid = pack.get("id", "")
        _require(SLUG.fullmatch(pid) is not None and pid.startswith(fid + "-"),
                 f"{fid}: pack id {pid!r} must be a slug starting with {fid}-")
        _require(pid not in seen, f"{fid}: pack id {pid} already used")
        seen.add(pid)
        _require(isinstance(pack.get("name"), str) and pack["name"], f"{fid}/{pid}: missing pack name")
        slugs = pack.get("roles") or []
        _require(slugs, f"{fid}/{pid}: pack has no roles")
        for slug in slugs:
            _require(slug in by_slug, f"{fid}/{pid}: unknown role {slug}")
            _require(slug not in placed, f"{fid}: role {slug} is in more than one pack")
            placed.add(slug)
        packs.append({"id": pid, "name": pack["name"], "roles": [r for r in roles if r["slug"] in slugs]})
    missing = sorted(set(by_slug) - placed)
    _require(not missing, f"{fid}: roles in no pack: {', '.join(missing)}")
    return packs


def roles(families):
    return [role for family in families for role in family["roles"]]
