# SPDX-License-Identifier: Apache-2.0
"""Compute every generated file in memory, then write them together."""
from . import adapter, generate, manifest, modmap
from .config import ADAPTER_AGENTS, MODULE_MAP, PACK_DIR, REGISTRY, STARTER, read, safe_path


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
        for pack in family["packs"]:
            generated[generate.pack_path(pack)] = generate.family_pack(root, family, pack, generated)
    generated.update(adapter.outputs(root, families))
    generated[MODULE_MAP] = modmap.generate(root, families, generated)
    return families, generated


def build(root):
    _, generated = outputs(root)
    destinations = {safe_path(root, name): data for name, data in generated.items()}
    for path, data in destinations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for folder in (PACK_DIR, ADAPTER_AGENTS):
        directory = root / folder
        if directory.is_dir():
            for stale in directory.glob("*.md"):
                if stale.relative_to(root).as_posix() not in generated:
                    safe_path(root, stale.relative_to(root).as_posix()).unlink()
