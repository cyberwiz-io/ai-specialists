# SPDX-License-Identifier: Apache-2.0
"""Assemble the release archives in memory, write them outside the tracked tree and verify the written copies."""
from io import BytesIO
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import subprocess
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from . import plugin
from .config import (ADAPTERS_DIR, ARCHIVE_PREFIX, GUIDE, LICENSE_FILES, MANIFEST, MODULE_MAP, PACK_SOURCES, archive_name,
                     REPOSITORY, read, version)

PUBLIC_DOCUMENTS = ("README.md", "VERSION", "CHANGELOG.md", "REPO-MAP.md", "CONTRIBUTING.md",
                    "docs/INSTALL.md", "docs/VALIDATION.md", "docs/CARD-GUIDE.md", "docs/ROADMAP.md")
LINK = re.compile(r"(!?\[[^\]\n]*\]\()([^)\n]+)(\))")
PRIVATE_ROOTS = {"work", "profiles", "campaigns", ".git", ".claude", ".codex", ".env"}


def payload_problems(payloads):
    """Validate only supplied archive bytes, with no source-checkout fallback."""
    failures = []
    for name, data in payloads.items():
        parts = PurePosixPath(name).parts
        if not name or name.startswith("/") or ".." in parts or "\\" in name or ":" in name:
            failures.append(f"unsafe archive path: {name}")
            continue
        if set(parts) & PRIVATE_ROOTS or name.startswith(".agents/skills/"):
            failures.append(f"private/local archive member: {name}")
        if not name.endswith(".md"):
            continue
        for match in LINK.finditer(data.decode("utf-8")):
            target = match.group(2).strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in ("http", "https", "mailto"):
                continue
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path))) \
                if parsed.path else name
            if parsed.scheme or dest not in payloads:
                failures.append(f"{name}: missing local link {target}")
            elif parsed.fragment and dest.endswith(".md"):
                headings = re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", payloads[dest].decode("utf-8"), re.M)
                anchors = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
                if unquote(parsed.fragment) not in anchors:
                    failures.append(f"{name}: missing local fragment {target}")
    return failures


def read_archive(path):
    """Read a single-root ZIP after validating names, duplicates and file modes."""
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"{path.name}: duplicate archive members")
        roots = {n.split("/", 1)[0] for n in names}
        if len(roots) != 1 or any("/" not in n for n in names):
            raise ValueError(f"{path.name}: expected one archive root")
        for item in archive.infolist():
            if item.filename.startswith("/") or ".." in PurePosixPath(item.filename).parts \
                    or "\\" in item.filename or ":" in item.filename \
                    or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f"{path.name}: unsafe archive member")
        payloads = {n.split("/", 1)[1]: archive.read(n) for n in names}
    failures = payload_problems(payloads)
    if failures:
        raise ValueError("\n".join(failures))
    return payloads


def provenance(root):
    result = {"source_commit": None, "source_tree": None, "draft": True}
    if not (root / ".git").exists():
        return result
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    result.update(source_commit=git("rev-parse", "HEAD"), source_tree=git("rev-parse", "HEAD^{tree}"),
                  draft=bool(git("status", "--porcelain", "--untracked-files=normal")))
    return result


def members(root, families, generated):
    prefix = f"{ARCHIVE_PREFIX}{version(root)}/"
    names = list(PACK_SOURCES) + list(PUBLIC_DOCUMENTS) + [GUIDE, MANIFEST] + list(LICENSE_FILES)
    names += sorted(path.relative_to(root).as_posix() for path in (root / "docs").glob("*.md"))
    names += [role["path"] for family in families for role in family["roles"]]
    names += sorted(path.relative_to(root).as_posix() for path in (root / ADAPTERS_DIR).glob("*/README.md"))
    data = {prefix + name: read(root, name) for name in names}
    for name, payload in generated.items():
        if name != MODULE_MAP:
            data[prefix + name] = payload
    revision = provenance(root)["source_commit"] or f"v{version(root)}"
    # Maintenance references remain useful without shipping maintainer configuration or tests.
    for name, payload in list(data.items()):
        if not name.endswith(".md"):
            continue
        def link(match):
            target = match.group(2).strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                return match.group(0)
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
            if dest in data:
                return match.group(0)
            if not dest.startswith(prefix):
                raise ValueError(f"{name}: link leaves archive: {target}")
            relative = dest[len(prefix):]
            read(root, relative)  # broken or unsafe source references must not become plausible URLs
            url = f"{REPOSITORY}/blob/{revision}/{relative}"
            if parsed.fragment:
                url += "#" + parsed.fragment
            return match.group(1) + url + match.group(3)
        data[name] = LINK.sub(link, payload.decode("utf-8")).encode("utf-8")
    failures = payload_problems({name[len(prefix):]: value for name, value in data.items()})
    if failures:
        raise ValueError("\n".join(failures))
    return data


def pack(payloads):
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as bundle:
        for name, data in sorted(payloads.items()):
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    return buffer.getvalue()


def compare(archive, expected):
    """Return failure strings comparing a ZIP on disk with the expected members."""
    with ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(expected) or set(names) != set(expected):
            return ["ZIP membership differs from the approved files"]
        return [f"ZIP bytes differ: {name}" for name, data in expected.items() if bundle.read(name) != data]


def release(root, families, generated, out, tag=None):
    """Write the release archive and one upload-ready skill ZIP per family into out, verify them and return the release path. A tag must name this VERSION, such as v1.0."""
    if tag is not None and tag != f"v{version(root)}":
        raise ValueError(f"tag {tag!r} does not match VERSION {version(root)}; expected v{version(root)}")
    expected = {archive_name(root): members(root, families, generated)}
    for family in families:
        expected[plugin.skill_archive_name(root, family)] = plugin.skill_members(family, generated)
    out.mkdir(parents=True, exist_ok=True)
    paths = {name: out / name for name in expected}
    if any(path.is_symlink() for path in list(paths.values()) + [out / "RELEASE.json", out / "SHA256SUMS"]):
        raise ValueError(f"Unsafe archive destination in {out}")
    failures = []
    for name, payloads in expected.items():
        paths[name].write_bytes(pack(payloads))
        failures += compare(paths[name], payloads)
    if failures:
        raise ValueError("\n".join(failures))
    record = {"schema": 1, "version": version(root), **provenance(root),
              "archives": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(paths.items())}}
    (out / "RELEASE.json").write_bytes((json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    checksums = dict(record["archives"])
    checksums["RELEASE.json"] = hashlib.sha256((out / "RELEASE.json").read_bytes()).hexdigest()
    (out / "SHA256SUMS").write_bytes("".join(f"{digest}  {name}\n" for name, digest in sorted(checksums.items())).encode("utf-8"))
    return paths[archive_name(root)]
