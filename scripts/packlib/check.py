# SPDX-License-Identifier: Apache-2.0
"""Verify cards, generated files, links, size limits, eval fixtures and archive inputs. Raises ValueError listing every failure."""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from . import bundle, cards, evals, manifest, modmap
from .build import outputs
from .config import PACK_DIR, PACK_MAX, REPO_MAP, SKIP_DIRS, STARTER, read, safe_path, version

VERSION_MENTION = re.compile(r"\bVersion:?\s+([0-9]+\.[0-9]+)")
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")


def check_cards(root, families, current):
    failures, known = [], {role["id"] for role in manifest.roles(families)}
    delivered = {}
    for family in families:
        folder = root / "catalog" / family["id"]
        expected = {role["slug"] + ".md" for role in family["roles"]} | {"INDEX.md"}
        for path in sorted(folder.glob("*")) if folder.is_dir() else []:
            if path.name not in expected:
                failures.append(f"catalog/{family['id']}/{path.name}: not in {family['id']} manifest")
        for role in family["roles"]:
            if not (root / role["path"]).is_file():
                failures.append(f"{role['path']}: card file is missing")
                continue
            text = read(root, role["path"]).decode("utf-8")
            failures += cards.check(role, text, current, known)
            deliver = cards.parse(text)["paragraphs"].get("Deliver", "")
            if deliver and deliver in delivered:
                failures.append(f"{role['path']}: Deliver duplicates {delivered[deliver]}")
            delivered[deliver] = role["path"]
    catalog = root / "catalog"
    for path in sorted(catalog.iterdir()) if catalog.is_dir() else []:
        if path.is_dir() and path.name not in {family["id"] for family in families}:
            failures.append(f"catalog/{path.name}: folder is not a manifest family")
    return failures


def check_versions(root, generated, current):
    names = ["pack/COORDINATOR.md", "pack/MARKETING-WORKFLOW.md", "pack/FAMILY-COORDINATOR.md"]
    failures = []
    for name in names + sorted(n for n in generated if n.endswith("/INDEX.md")):
        text = read(root, name, generated).decode("utf-8")
        if VERSION_MENTION.findall(text) != [current]:
            failures.append(f"{name}: expected one Version {current}")
    return failures


def check_generated(root, generated):
    failures = []
    for name, data in generated.items():
        path = root / name
        if not path.is_file():
            failures.append(f"{name} is missing; run build")
        elif safe_path(root, name).read_bytes() != data:
            failures.append("Combined instructions differ from sources; run build" if name == STARTER
                            else f"{name} differs from sources; run build")
        if name.startswith(PACK_DIR) and len(data) > PACK_MAX:
            failures.append(f"{name}: combined pack exceeds {PACK_MAX} bytes; split the family with \"packs\"")
    directory = root / PACK_DIR
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        if path.relative_to(root).as_posix() not in generated:
            failures.append(f"{path.relative_to(root).as_posix()}: stale generated file; run build")
    return failures


def check_archives(root):
    """Release archives are attached to GitHub Releases by CI, never committed."""
    failures = []
    for path in sorted(root.rglob("*.zip")):
        relative = path.relative_to(root)
        if not set(relative.parts) & SKIP_DIRS:
            failures.append(f"{relative.as_posix()}: archives are not committed; "
                            "run release, and let CI attach it to the GitHub Release")
    return failures


def check_links(root):
    failures = []
    # shortcut: inline file links only; extend parsing if reference-style links are introduced.
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if set(relative.parts) & (SKIP_DIRS | {"dist"}):  # dist/ copies are generated from checked sources
            continue
        text = read(root, relative.as_posix()).decode("utf-8")
        for target in LINK.findall(text):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in ("https", "http", "mailto") or not parsed.path:
                continue
            destination = path.parent / unquote(parsed.path)
            if parsed.scheme or not destination.resolve().is_relative_to(root.resolve()) or not destination.is_file():
                failures.append(f"{relative}: invalid local link {target}")
    return failures


def check_navigation(root, families, generated):
    failures = []
    if not (root / REPO_MAP).is_file():
        return [f"{REPO_MAP} is missing"]
    text = read(root, REPO_MAP).decode("utf-8")
    for family in families:
        if f"catalog/{family['id']}/INDEX.md" not in text:
            failures.append(f"{REPO_MAP}: does not link catalog/{family['id']}/INDEX.md")
    failures += [f"{name} is not covered by any module in config/modules.json"
                 for name in modmap.uncovered(root, families, generated)]
    return failures


def check(root):
    current = version(root)
    families = manifest.load(root)
    failures = check_cards(root, families, current)
    if any("card file is missing" in failure for failure in failures):
        raise ValueError("\n".join(failures))
    families, generated = outputs(root)
    failures += check_versions(root, generated, current)
    failures += check_generated(root, generated)
    failures += check_links(root)
    failures += check_navigation(root, families, generated)
    failures += check_archives(root)
    failures += evals.problems(root, families)[1]
    try:
        bundle.members(root, families, generated)
    except OSError as error:
        failures.append(f"release archive input is unreadable ({error})")
    if failures:
        raise ValueError("\n".join(failures))
    return families, generated
