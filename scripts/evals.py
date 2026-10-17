# SPDX-License-Identifier: Apache-2.0
"""Prepare, track and report card evaluation runs. Claude Code runs the subagents; see the card-evals skill."""
import argparse
from datetime import date
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packlib import check as checker, config, evals  # noqa: E402

DEFAULT_TOOLS = ("Claude Code; each fixture ran in a fresh subject subagent and was graded by a separate fresh "
                 "grader subagent, both limited to Read and Write for the harness files")


def commit(root):
    """Current commit, marked when the working tree has uncommitted changes."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "catalog", "pack", "evals", "dist"],
                               cwd=root, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown (not a Git checkout)"
    return head.stdout.strip() + (" with uncommitted changes" if dirty.stdout.strip() else "")


def prepare(root, args, today=None):
    families, generated = checker.check(root)
    fixtures = evals.select(evals.load(root, families), args.family, args.role, args.kind)
    meta = {"version": config.version(root), "commit": commit(root), "host": args.host, "tools": args.tools,
            "model": args.model, "grader": args.grader or args.model, "date": (today or date.today()).isoformat()}
    folder = evals.prepare(root, families, generated, fixtures, args.run, meta)
    return folder, len(fixtures)


def main(argv=None, root=None):
    root = root or config.ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    first = commands.add_parser("prepare", help="write prompts for a new run under work/evals/<run>/")
    first.add_argument("--run", required=True, help="new run name, a slug such as 2026-10-17-security")
    first.add_argument("--host", required=True, help="host that runs the subagents, such as 'Claude Code (cloud)'")
    first.add_argument("--model", required=True, help="model under test, as the host reports it")
    first.add_argument("--grader", help="grader model, if different from --model")
    first.add_argument("--tools", default=DEFAULT_TOOLS, help="tools available to the subagents")
    first.add_argument("--family", help="only this family")
    first.add_argument("--role", help="only this role ID")
    first.add_argument("--kind", choices=evals.KINDS, help="only task or boundary fixtures")
    commands.add_parser("baseline", help="save reviewed runs' per-card pass counts as evals/baseline.json; "
                        "with several --run, a later run replaces an earlier one for the cards it ran").add_argument(
        "--run", required=True, action="append")
    for name, text in (("status", "list fixtures still lacking a reply or grade"),
                       ("report", "validate every reply and grade, then write REPORT.md"),
                       ("compare", "write REGRESSION.md; exit 3 when a card's pass rate fell below the baseline")):
        commands.add_parser(name, help=text).add_argument("--run", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            folder, count = prepare(root, args)
            print(f"Prepared {count} fixtures in {folder.relative_to(root).as_posix()}")
        elif args.command == "status":
            record, need_output, need_grade = evals.status(root, args.run)
            for fixture in need_output:
                print(f"needs reply\t{fixture['key']}\t{fixture['subject_prompt']}\t{fixture['output']}")
            for fixture in need_grade:
                print(f"needs grade\t{fixture['key']}\t{fixture['grader_prompt']}\t{fixture['grade']}")
            done = len(record["fixtures"]) - len(need_output) - len(need_grade)
            print(f"{done} of {len(record['fixtures'])} fixtures replied and graded")
        elif args.command == "baseline":
            path = evals.save_baseline(root, args.run)
            print(f"Baseline written to {path.relative_to(root).as_posix()}")
        elif args.command == "compare":
            path, drops = evals.compare(root, args.run)
            print(f"Comparison written to {path.relative_to(root).as_posix()}; {len(drops)} cards fell")
            for role in drops:
                print(f"fell\t{role}")
            if drops:
                sys.exit(3)
        else:
            path = evals.report(root, args.run)
            print(f"Report written to {path.relative_to(root).as_posix()}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Eval {args.command} failed: {error}\n")


if __name__ == "__main__":
    main()
