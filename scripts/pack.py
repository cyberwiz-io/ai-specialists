# SPDX-License-Identifier: Apache-2.0
"""Build, check, release and search the specialist pack using only the standard library."""
import argparse
import json
from pathlib import Path
import sys
from zipfile import BadZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packlib import build as builder, bundle, check as checker, config  # noqa: E402


def find(root, terms):
    """Registry rows that contain every search term, one line each."""
    text = config.read(root, config.REGISTRY).decode("utf-8")
    rows = []
    for line in text.splitlines()[1:]:
        if all(term.lower() in line.lower() for term in terms):
            row = json.loads(line)
            rows.append(f"{row['id']}\t{row['path']}\t{row['use_for']}")
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check", "release", "find"))
    parser.add_argument("terms", nargs="*", help="words to search for with the find command")
    parser.add_argument("--out", type=Path, help=f"release: folder for the archive (default {config.RELEASE_DIR})")
    parser.add_argument("--tag", help="release: the Git tag being released, which must be v plus VERSION")
    args = parser.parse_args(argv)
    try:
        if args.command == "find":
            rows = find(config.ROOT, args.terms)
            print("\n".join(rows) if rows else "No matching specialists")
            return
        if args.command == "build":
            builder.build(config.ROOT)
        families, generated = checker.check(config.ROOT)
        if args.command == "release":
            out = args.out or config.ROOT / config.RELEASE_DIR
            archive = bundle.release(config.ROOT, families, generated, out, args.tag)
    except (OSError, ValueError, BadZipFile) as error:
        parser.exit(1, f"Pack {args.command} failed: {error}\n")
    count = sum(len(family["roles"]) for family in families)
    print(f"PASS: version {config.version(config.ROOT)}, {count} specialists in {len(families)} families, "
          f"{len(generated)} generated files")
    if args.command == "release":
        print(archive)


if __name__ == "__main__":
    main()
