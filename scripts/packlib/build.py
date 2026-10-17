# SPDX-License-Identifier: Apache-2.0
"""Compute every generated file in memory, then write them together."""
from . import generate, manifest, modmap, plugin
from .config import MODULE_MAP, PACK_DIR, PLUGINS_DIR, REGISTRY, STARTER, read, safe_path


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
    generated.update(plugin.outputs(root, families))
    generated[MODULE_MAP] = modmap.generate(root, families, generated)
    return families, generated


def build(root):
    _, generated = outputs(root)
    destinations = {safe_path(root, name): data for name, data in generated.items()}
    for path, data in destinations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for stale in stale_files(root, generated):
        safe_path(root, stale).unlink()
    plugins = root / PLUGINS_DIR
    for folder in sorted(plugins.rglob("*"), reverse=True) if plugins.is_dir() else []:
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()


def stale_files(root, generated):
    """Generated-looking files that no longer have a source: old packs and anything left in plugins/."""
    found = []
    pack_dir, plugins = root / PACK_DIR, root / PLUGINS_DIR
    for path in sorted(pack_dir.glob("*.md")) if pack_dir.is_dir() else []:
        found.append(path.relative_to(root).as_posix())
    for path in sorted(plugins.rglob("*")) if plugins.is_dir() else []:
        if path.is_file() or path.is_symlink():
            found.append(path.relative_to(root).as_posix())
    return [name for name in found if name not in generated]
