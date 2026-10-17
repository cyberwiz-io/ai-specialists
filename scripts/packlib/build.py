# SPDX-License-Identifier: Apache-2.0
"""Compute every generated file in memory, then write them together."""
from . import bundle, generate, manifest, modmap
from .config import (DOWNLOADS, MODULE_MAP, PACK_DIR, REGISTRY, STARTER, archive_name, read, safe_path)


def outputs(root):
    """Return (families, generated) where generated maps repository paths to bytes."""
    families = manifest.load(root)
    for role in manifest.roles(families):
        read(root, role["path"])  # a missing card stops the build before anything is written
    generated = {}
    for family in families:
        generated[f"catalog/{family['id']}/INDEX.md"] = generate.index(root, family)
    generated[STARTER] = generate.starter(root)
    generated[REGISTRY] = generate.registry(root, families)
    for family in families:
        generated[generate.pack_path(family)] = generate.family_pack(root, family, generated)
    generated[MODULE_MAP] = modmap.generate(root, families, generated)
    return families, generated


def build(root):
    families, generated = outputs(root)
    archive = archive_name(root)
    payload = bundle.pack(bundle.members(root, families, generated))
    destinations = {safe_path(root, name): data for name, data in generated.items()}
    destinations[safe_path(root, archive)] = payload
    for path, data in destinations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    expected = set(generated) | {archive}
    for pattern, folder in (("*.md", PACK_DIR), ("*.zip", DOWNLOADS)):
        directory = root / folder
        if directory.is_dir():
            for stale in directory.glob(pattern):
                if stale.relative_to(root).as_posix() not in expected:
                    safe_path(root, stale.relative_to(root).as_posix()).unlink()
