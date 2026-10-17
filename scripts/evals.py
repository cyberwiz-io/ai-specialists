# SPDX-License-Identifier: Apache-2.0
"""List, prompt, grade and self-check the fixture evals for specialist cards, using only the standard library."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packlib import config, evals, manifest  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "prompt", "grade", "selfcheck"))
    parser.add_argument("role", nargs="?", help="role ID such as software-engineering/code-reviewer")
    parser.add_argument("scenario", nargs="?", help="scenario id")
    parser.add_argument("response", nargs="?", type=Path, help="grade: file holding the saved response")
    args = parser.parse_args(argv)
    root = config.ROOT
    try:
        scenarios = evals.load(root)
        if args.command == "selfcheck":
            print(f"PASS: {evals.selfcheck(scenarios)} scenarios; good samples pass and bad samples fail")
            return
        families = manifest.load(root)
        if args.command == "list":
            roles = [evals.find_role(families, args.role)] if args.role else manifest.roles(families)
            for sid, scenario in scenarios.items():
                count = sum(evals.applies(scenario, role) for role in roles)
                if count:
                    print(f"{sid}\t{count} role(s)\t{scenario['source']}")
            return
        if not (args.role and args.scenario):
            parser.error(f"{args.command} needs a role ID and a scenario id")
        role = evals.find_role(families, args.role)
        if args.scenario not in scenarios:
            raise ValueError(f"unknown scenario {args.scenario!r}; known: {', '.join(scenarios)}")
        scenario = scenarios[args.scenario]
        if not evals.applies(scenario, role):
            raise ValueError(f"scenario {args.scenario} does not apply to {role['id']}")
        if args.command == "prompt":
            print(evals.prompt(root, families, role, scenario))
            return
        if not args.response:
            parser.error("grade needs a response file")
        if not args.response.is_file():
            raise ValueError(f"response file not found: {args.response}")
        failures = evals.grade(scenario, args.response.read_text(encoding="utf-8"))
        if failures:
            raise ValueError("\n".join(failures))
        print(f"PASS: {role['id']} / {args.scenario} (keyword rules only)")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Eval {args.command} failed: {error}\n")


if __name__ == "__main__":
    main()
