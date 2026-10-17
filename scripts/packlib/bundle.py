# SPDX-License-Identifier: Apache-2.0
"""Assemble the release archives in memory, write them outside the tracked tree and verify the written copies."""
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from . import plugin
from .config import (ARCHIVE_PREFIX, GUIDE, LICENSE_FILES, MANIFEST, MODULE_MAP, PACK_SOURCES, archive_name,
                     read, version)


def members(root, families, generated):
    prefix = f"{ARCHIVE_PREFIX}{version(root)}/"
    names = list(PACK_SOURCES) + [GUIDE, MANIFEST] + list(LICENSE_FILES)
    names += [role["path"] for family in families for role in family["roles"]]
    data = {prefix + name: read(root, name) for name in names}
    for name, payload in generated.items():
        if name != MODULE_MAP:
            data[prefix + name] = payload
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
    if any(path.is_symlink() for path in paths.values()):
        raise ValueError(f"Unsafe archive destination in {out}")
    failures = []
    for name, payloads in expected.items():
        paths[name].write_bytes(pack(payloads))
        failures += compare(paths[name], payloads)
    if failures:
        raise ValueError("\n".join(failures))
    return paths[archive_name(root)]
