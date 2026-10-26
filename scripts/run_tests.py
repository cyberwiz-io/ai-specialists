# SPDX-License-Identifier: Apache-2.0
"""Run unittest checks, with a narrow maintenance scope or complete CI shards."""
import argparse
import json
import re
import subprocess
import sys
import unittest


# This is deliberately an exact list, not a general docs/config path filter.
# Product, card, other configuration and unknown changes keep complete coverage.
MAINTENANCE_SCOPE_API = 1
# The reviewed bootstrap introduces this selector. Only that exact pre-selector
# base can focus a PR that changes the selector or its calling workflow.
BOOTSTRAP_BASE = 'c24b434e0e0c867e95956c475ed5c64bd6be64ae'
MAINTENANCE_PATHS = {
    '.gitignore', 'CHANGELOG.md', 'CONTRIBUTING.md',
    'docs/INSTALL.md', 'docs/VALIDATION.md', 'docs/WINDOWS.md', 'docs/HOST-ACCEPTANCE.md', 'README.md',
    'adapters/codex/README.md', 'config/modules.json',
    'config/module-map.json', 'tests/test_source.py',
}
BOOTSTRAP_PATHS = {'.github/workflows/check.yml', 'scripts/run_tests.py', 'tests/test_run_tests.py'}
BOOTSTRAP_HOOK_PATHS = {'.claude/settings.json', '.claude/CLAUDE.md'}
MAINTENANCE_TESTS = ('test_source.py', 'test_run_tests.py')


def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True).stdout


def focused_patterns(base):
    """Return focused patterns only for the understood maintenance delta.

    A missing/invalid base, failed inventory, or unknown path preserves full
    coverage. Git's NUL-separated names keep spaces and shell syntax as data.
    """
    if not base:
        return None
    try:
        if not re.fullmatch(r'[0-9a-f]{40}', base):
            raise ValueError('base must be a full commit SHA')
        names = set(git('diff', '--name-only', '--no-renames', '-z', base, 'HEAD')
                    .decode('utf-8').rstrip('\0').split('\0')) - {''}
        allowed = MAINTENANCE_PATHS | (BOOTSTRAP_PATHS | BOOTSTRAP_HOOK_PATHS
                                      if base == BOOTSTRAP_BASE else set())
        if not names or not names <= allowed:
            return None
        for name in names & BOOTSTRAP_HOOK_PATHS:
            before = git('show', base + ':' + name)
            after = git('show', 'HEAD:' + name)
            old = b'python3 -B scripts/pack.py check'
            if before.count(old) != 1 or after != before.replace(old, b'python -B scripts/pack.py check', 1):
                return None
        if '.gitignore' in names:
            before = git('show', base + ':.gitignore')
            after = git('show', 'HEAD:.gitignore')
            if after != before + b'.venv-policy/\n':
                return None
        if 'config/modules.json' in names:
            before = json.loads(git('show', base + ':config/modules.json'))
            after = json.loads(git('show', 'HEAD:config/modules.json'))
            expected = json.loads(json.dumps(before))
            directories = expected['local_material']['directories']
            if '.venv-policy' not in directories:
                directories.append('.venv-policy')
            if after != expected:
                return None
        return MAINTENANCE_TESTS
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError,
            KeyError, TypeError, AttributeError) as error:
        print('Test scope unavailable; retaining complete coverage: ' + type(error).__name__,
              file=sys.stderr)
        return None


def shard(suite, index, count):
    if count not in (1, 2) or not 0 <= index < count:
        raise ValueError('expected shard 0/1 with count 1/2')

    def cases(items):
        for item in items:
            if isinstance(item, unittest.TestSuite):
                yield from cases(item)
            else:
                yield item

    discovered = list(cases(suite))
    if not discovered:
        raise ValueError('no tests discovered')
    return unittest.TestSuite(discovered[index::count])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shard-index', type=int, default=0)
    parser.add_argument('--shard-count', type=int, default=1)
    parser.add_argument('--changed-base', help='PR base commit; understood maintenance changes use focused checks')
    parser.add_argument('--plan', action='store_true', help='Print focused=true/false without running tests')
    args = parser.parse_args(argv)
    patterns = focused_patterns(args.changed_base)
    if args.plan:
        print('focused=' + str(patterns is not None).lower())
        return 0
    if patterns:
        suite = unittest.TestSuite(unittest.defaultTestLoader.discover('tests', pattern=pattern)
                                   for pattern in patterns)
    else:
        suite = unittest.defaultTestLoader.discover('tests')
    try:
        selected = shard(suite, args.shard_index, args.shard_count)
    except ValueError as error:
        parser.error(str(error))
    print(f'Shard {args.shard_index + 1}/{args.shard_count}: '
          f'{selected.countTestCases()}/{suite.countTestCases()} discovered tests', flush=True)
    return int(not unittest.TextTestRunner().run(selected).wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
