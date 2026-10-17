# SPDX-License-Identifier: Apache-2.0
"""Paths, limits and safe file helpers shared by the pack tools."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "work", ".venv", "profiles", "campaigns", "__pycache__"}

MANIFEST = "catalog/families.json"
REGISTRY = "catalog/REGISTRY.jsonl"
STARTER = "pack/STARTER-PACK.md"
MODULES = "config/modules.json"
MODULE_MAP = "config/module-map.json"
REPO_MAP = "REPO-MAP.md"
PACK_DIR = "dist/packs"
PLUGINS_DIR = "plugins"
MARKETPLACE = ".claude-plugin/marketplace.json"
REPOSITORY = "https://github.com/cyberwiz-io/ai-specialists"
RELEASE_DIR = "work/release"
GUIDE = "docs/CARD-GUIDE.md"
DEFAULT_COORDINATOR = ("pack/FAMILY-COORDINATOR.md",)

# The marketing starter pack: the sections pasted together for a small business.
STARTER_SECTIONS = (
    "pack/COORDINATOR.md", "pack/MARKETING-WORKFLOW.md",
    "catalog/marketing-growth/marketing-strategist.md", "catalog/marketing-growth/copywriter.md",
    "catalog/marketing-growth/graphic-designer.md", "catalog/marketing-growth/quality-reviewer.md",
    "pack/CUSTOM-SPECIALISTS.md", "pack/BUSINESS-PROFILE.md",
)
PACK_SOURCES = (
    "pack/START-HERE.md", "pack/COORDINATOR.md", "pack/MARKETING-WORKFLOW.md",
    "pack/FAMILY-COORDINATOR.md", "pack/CUSTOM-SPECIALISTS.md", "pack/BUSINESS-PROFILE.md",
    "docs/INSTALL.md",
)
# Marketing keeps its workflow and optional-extras files beside the coordinator as skill references.
SKILL_EXTRAS = {"marketing-growth": ("pack/CUSTOM-SPECIALISTS.md", "pack/BUSINESS-PROFILE.md")}
LICENSE_FILES = ("NOTICE.md", "LICENSE.md", "LICENSES/CC-BY-4.0.txt", "LICENSES/Apache-2.0.txt")

CARD_MAX = 3500
# About 8,000 tokens at roughly four bytes per token, so a combined pack leaves at least half of a
# 16,000-token context window for the user's material and the reply. Families above it declare "packs".
PACK_MAX = 32000
ARCHIVE_PREFIX = "ai-specialists-"


def safe_path(root, name):
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe source path: {name}")
    return path


def read(root, name, overlay=None):
    """Read a source file; an overlay maps generated paths to their pending bytes."""
    if overlay and name in overlay:
        return overlay[name]
    return safe_path(root, name).read_bytes()


def version(root):
    value = read(root, "VERSION").decode("utf-8").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+", value):
        raise ValueError(f"VERSION must look like 1.0, found {value!r}")
    return value


def archive_name(root):
    """File name of the release archive; CI attaches it to the GitHub Release rather than committing it."""
    return f"{ARCHIVE_PREFIX}{version(root)}.zip"
