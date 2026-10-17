# SPDX-License-Identifier: Apache-2.0
"""Assemble the release archive in memory, write it outside the tracked tree and verify the written copy."""
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

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
    """Write the archive into out, verify it and return its path. A tag must name this VERSION, such as v1.0."""
    if tag is not None and tag != f"v{version(root)}":
        raise ValueError(f"tag {tag!r} does not match VERSION {version(root)}; expected v{version(root)}")
    expected = members(root, families, generated)
    out.mkdir(parents=True, exist_ok=True)
    archive = out / archive_name(root)
    if archive.is_symlink():
        raise ValueError(f"Unsafe archive destination: {archive}")
    archive.write_bytes(pack(expected))
    failures = compare(archive, expected)
    if failures:
        raise ValueError("\n".join(failures))
    return archive
