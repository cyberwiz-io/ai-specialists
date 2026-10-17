# SPDX-License-Identifier: Apache-2.0
"""Assemble the downloadable archive in memory and compare it with the one on disk."""
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from .config import (ARCHIVE_PREFIX, GUIDE, LICENSE_FILES, MANIFEST, MODULE_MAP, PACK_DIR, PACK_SOURCES,
                     REGISTRY, STARTER, read, version)


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
