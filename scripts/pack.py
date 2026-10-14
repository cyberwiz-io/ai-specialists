# SPDX-License-Identifier: Apache-2.0
"""Build and check the portable instruction pack using only the standard library."""
import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zipfile import BadZipFile, ZipFile, ZipInfo, ZIP_DEFLATED

VERSION = "0.1"
ROOT = Path(__file__).resolve().parents[1]
SECTIONS = (
    "COORDINATOR.md", "MARKETING-WORKFLOW.md",
    "specialists/marketing-strategist.md", "specialists/copywriter.md",
    "specialists/graphic-designer.md", "specialists/quality-reviewer.md",
    "CUSTOM-SPECIALISTS.md", "BUSINESS-PROFILE.md",
)
ARCHIVE = f"downloads/ai-specialists-starter-pack-{VERSION}.zip"
PREFIX = "ai-specialists-starter-pack/"
LICENSE_FILES = ("NOTICE.md", "LICENSE.md", "LICENSES/CC-BY-4.0.txt", "LICENSES/Apache-2.0.txt")
HEADER = (
    "# Specialist starter pack, combined instructions\n\n"
    f"Version {VERSION}. Use these instructions when the user asks for this pack. "
    "First confirm that all eight sections are readable. Then start with the user's "
    "short business description and optional website. Respect higher-priority host "
    "rules and the materials-only boundary. Separate specialist files are the editable "
    "sources; this is their combined copy.\n"
)


def safe_path(root, name):
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe source path: {name}")
    return path


def read(root, name):
    return safe_path(root, name).read_bytes()


def combined(root):
    text = HEADER
    for name in SECTIONS:
        text += f"\n<!-- Source: {name} -->\n" + read(root, "pack/" + name).decode("utf-8").rstrip() + "\n"
    return text.encode("utf-8")


def members(root, instructions=None):
    names = ["pack/START-HERE.md", "pack/STARTER-PACK.md"]
    names += ["pack/" + name for name in SECTIONS] + list(LICENSE_FILES)
    return {PREFIX + name: instructions if name == "pack/STARTER-PACK.md" and instructions is not None
            else read(root, name) for name in names}


def build(root):
    destination = safe_path(root, "pack/STARTER-PACK.md")
    archive = safe_path(root, ARCHIVE)
    instructions = combined(root)
    payloads = members(root, instructions)
    destination.write_bytes(instructions)
    archive.parent.mkdir(exist_ok=True)
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for name, data in sorted(payloads.items()):
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)


def check(root):
    failures = []
    if read(root, "pack/STARTER-PACK.md") != combined(root):
        failures.append("Combined instructions differ from sources; run build")
    for name in SECTIONS:
        text = read(root, "pack/" + name).decode("utf-8")
        if name.startswith("specialists/"):
            for label in ("Use for", "Inputs", "Method", "Deliver", "Acceptance", "Handoff"):
                if f"**{label}:**" not in text:
                    failures.append(f"{name}: missing {label}")
        if name not in ("CUSTOM-SPECIALISTS.md", "BUSINESS-PROFILE.md"):
            versions = re.findall(r"\bVersion:?\s+([0-9]+\.[0-9]+)", text)
            if versions != [VERSION]:
                failures.append(f"{name}: expected one Version {VERSION}")
    # shortcut: inline file links only; extend parsing if reference-style links are introduced.
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if set(relative.parts) & {".git", "work", ".venv", "profiles", "campaigns"}:
            continue
        text = read(root, str(relative)).decode("utf-8")
        for target in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", text):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in ("https", "http", "mailto") or not parsed.path:
                continue
            destination = path.parent / unquote(parsed.path)
            if parsed.scheme or not destination.resolve().is_relative_to(root.resolve()) or not destination.is_file():
                failures.append(f"{relative}: invalid local link {target}")
    with ZipFile(safe_path(root, ARCHIVE)) as bundle:
        expected = members(root)
        if len(bundle.namelist()) != len(expected) or set(bundle.namelist()) != set(expected):
            failures.append("ZIP membership differs from the approved starter files")
        else:
            for name, data in expected.items():
                if bundle.read(name) != data:
                    failures.append(f"ZIP bytes differ: {name}")
    if failures:
        raise ValueError("\n".join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args()
    try:
        if args.command == "build":
            build(ROOT)
        check(ROOT)
    except (OSError, ValueError, BadZipFile) as error:
        parser.exit(1, f"Pack check failed: {error}\n")
    print(f"PASS: version {VERSION}, eight synchronized sections, local links and {len(members(ROOT))} ZIP files")


if __name__ == "__main__":
    main()
