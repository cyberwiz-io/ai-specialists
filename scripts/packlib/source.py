# SPDX-License-Identifier: Apache-2.0
"""Repository inventory, distinct from client-local installations and generated ownership."""
import json
import os
from pathlib import Path
import shutil
import subprocess

from .config import MODULES, SKIP_DIRS, read, safe_path


def tracked_files(root):
    """None without this checkout's Git metadata; never borrow a parent repository."""
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                                check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Cannot establish tracked source inventory") from error
    return set(result.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""}


def files(root):
    """Include tracked files and new source; never walk installed symlink targets.

    Reserved installation locations are declared in modules.json. New repository
    source there must be explicitly owned or staged. No-Git trees fail closed.
    """
    root = Path(root)
    tracked = tracked_files(root)
    local = json.loads(read(root, MODULES)).get("local_material", {})
    directories = local.get("directories", [])
    owned = local.get("sources", [])
    local_files = local.get("files", [])

    def beneath(name, paths):
        return any(name == p or name.startswith(p + "/") for p in paths)

    def installed(name):
        candidate = not beneath(name, owned) and (name in local_files or beneath(name, directories))
        if tracked is None and candidate and not any(p.startswith(name + "/") for p in owned):
            raise ValueError(f"Unclassified local material without Git inventory: {name}")
        return tracked is not None and name not in tracked and candidate

    found = set(tracked or ())
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in list(dirs):
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            if name in SKIP_DIRS:
                dirs.remove(name)
            elif path.is_symlink():
                dirs.remove(name)
                if not installed(relative):
                    safe_path(root, relative)
                    found.add(relative)
            elif installed(relative) and not any(p.startswith(relative + "/") for p in owned) \
                    and not any(p.startswith(relative + "/") for p in tracked or ()):
                dirs.remove(name)
        for name in names:
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            if name == ".git" or installed(relative):
                continue
            if path.is_symlink():
                safe_path(root, relative)
            found.add(relative)
    return sorted(found)


def copy(root, destination):
    """Copy validated repository inputs, never dereference a source symlink."""
    names = files(root)
    paths = [(name, safe_path(root, name)) for name in names]
    for name, path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Repository source is missing or not a file: {name}")
    for name, path in paths:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
