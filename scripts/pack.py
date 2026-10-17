# SPDX-License-Identifier: Apache-2.0
"""Build, check and search the specialist pack using only the standard library."""
import argparse
import json
from pathlib import Path
import sys
from zipfile import BadZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packlib import build as builder, check as checker, config  # noqa: E402


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
    parser.add_argument("command", choices=("build", "check", "find"))
    parser.add_argument("terms", nargs="*", help="words to search for with the find command")
    args = parser.parse_args(argv)
    try:
        if args.command == "find":
            rows = find(config.ROOT, args.terms)
            print("\n".join(rows) if rows else "No matching specialists")
            return
        if args.command == "build":
            builder.build(config.ROOT)
        families, generated = checker.check(config.ROOT)
    except (OSError, ValueError, BadZipFile) as error:
        parser.exit(1, f"Pack check failed: {error}\n")
    count = sum(len(family["roles"]) for family in families)
    print(f"PASS: version {config.version(config.ROOT)}, {count} specialists in {len(families)} families, "
          f"{len(generated)} generated files and the archive")


if __name__ == "__main__":
    main()
