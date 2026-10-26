# SPDX-License-Identifier: Apache-2.0
"""Keep CI shards complete and preserve real test failures."""
import contextlib
import io
import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_tests


class TestShards(unittest.TestCase):
    def test_nested_suite_is_partitioned_once_without_omissions(self):
        cases = [unittest.FunctionTestCase(lambda: None) for _ in range(7)]
        suite = unittest.TestSuite([unittest.TestSuite(cases[:3]), unittest.TestSuite(cases[3:])])
        left = list(run_tests.shard(suite, 0, 2))
        right = list(run_tests.shard(suite, 1, 2))
        self.assertEqual(left, cases[::2])
        self.assertEqual(right, cases[1::2])
        self.assertEqual({id(t) for t in left} & {id(t) for t in right}, set())
        self.assertEqual(len(left) + len(right), len(cases))
        self.assertEqual(list(run_tests.shard(suite, 0, 1)), cases)

    def test_invalid_shard_is_rejected(self):
        suite = unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])
        for index, count in [(-1, 2), (2, 2), (0, 0), (0, 3)]:
            with self.subTest(index=index, count=count), self.assertRaises(ValueError):
                run_tests.shard(suite, index, count)

    def test_empty_discovery_is_rejected(self):
        with self.assertRaises(ValueError):
            run_tests.shard(unittest.TestSuite(), 0, 1)

    def test_success_and_failure_have_real_exit_statuses(self):
        def fail():
            self.fail('intentional fixture failure')
        for test, expected in [(lambda: None, 0), (fail, 1)]:
            suite = unittest.TestSuite([unittest.FunctionTestCase(test)])
            with self.subTest(expected=expected), mock.patch.object(
                    unittest.defaultTestLoader, 'discover', return_value=suite), \
                    contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_tests.main([]), expected)


class TestMaintenanceScope(unittest.TestCase):
    BASE = 'a' * 40

    def test_exact_maintenance_paths_select_both_regressions(self):
        names = '\0'.join(sorted(run_tests.MAINTENANCE_PATHS - {'config/modules.json', '.gitignore'})) + '\0'
        with mock.patch.object(run_tests, 'git', return_value=names.encode()) as git:
            self.assertEqual(run_tests.focused_patterns(self.BASE),
                             ('test_source.py', 'test_run_tests.py'))
        git.assert_called_once_with('diff', '--name-only', '--no-renames', '-z', self.BASE, 'HEAD')

    def test_selector_changes_focus_only_for_exact_reviewed_bootstrap_base(self):
        for base, expected in [(run_tests.BOOTSTRAP_BASE, run_tests.MAINTENANCE_TESTS),
                               (self.BASE, None)]:
            for name in run_tests.BOOTSTRAP_PATHS:
                with self.subTest(base=base, name=name), mock.patch.object(
                        run_tests, 'git', return_value=(name + '\0').encode()):
                    self.assertEqual(run_tests.focused_patterns(base), expected)

    def test_only_exact_ignore_addition_is_focused(self):
        before = b'work/\n.venv/\n'
        for after, expected in [(before + b'.venv-policy/\n', run_tests.MAINTENANCE_TESTS),
                                (before + b'new-source/\n', None),
                                (b'.venv-policy/\n', None),
                                (before + b'.venv-policy/\nsecret/\n', None)]:
            with self.subTest(after=after), mock.patch.object(run_tests, 'git', side_effect=[
                    b'.gitignore\0', before, after]):
                self.assertEqual(run_tests.focused_patterns(self.BASE), expected)

    def test_hook_python_replacement_is_exact_and_bootstrap_only(self):
        before = b'prefix python3 -B scripts/pack.py check suffix\n'
        expected = before.replace(b'python3 -B scripts/pack.py check', b'python -B scripts/pack.py check')
        for name in run_tests.BOOTSTRAP_HOOK_PATHS:
            with self.subTest(name=name), mock.patch.object(run_tests, 'git', side_effect=[
                    (name + '\0').encode(), before, expected]):
                self.assertEqual(run_tests.focused_patterns(run_tests.BOOTSTRAP_BASE),
                                 run_tests.MAINTENANCE_TESTS)
            with self.subTest(name=name), mock.patch.object(run_tests, 'git', return_value=(name + '\0').encode()):
                self.assertIsNone(run_tests.focused_patterns(self.BASE))
            for invalid in (before, expected + b'other change\n', expected.replace(b'suffix', b'altered')):
                with self.subTest(name=name, invalid=invalid), mock.patch.object(run_tests, 'git', side_effect=[
                        (name + '\0').encode(), before, invalid]):
                    self.assertIsNone(run_tests.focused_patterns(run_tests.BOOTSTRAP_BASE))

    def test_hook_replacement_requires_exactly_one_old_command(self):
        for before in (b'no check command', b'python3 -B scripts/pack.py check\n' * 2):
            with self.subTest(before=before), mock.patch.object(run_tests, 'git', side_effect=[
                    b'.claude/settings.json\0', before,
                    before.replace(b'python3 -B scripts/pack.py check', b'python -B scripts/pack.py check')]):
                self.assertIsNone(run_tests.focused_patterns(run_tests.BOOTSTRAP_BASE))

    def test_unknown_product_and_card_paths_keep_complete_coverage(self):
        for name in ('catalog/security/threat-modeler.md', 'scripts/packlib/config.py',
                     'scripts/packlib/source.py',
                     'docs/RELEASE.md', 'docs/INSTALL.md\nother', 'unknown with spaces'):
            with self.subTest(name=name), mock.patch.object(
                    run_tests, 'git', return_value=('docs/INSTALL.md\0' + name + '\0').encode()):
                self.assertIsNone(run_tests.focused_patterns(self.BASE))

    def test_missing_base_and_empty_change_set_keep_complete_coverage(self):
        self.assertIsNone(run_tests.focused_patterns(None))
        with mock.patch.object(run_tests, 'git', return_value=b''):
            self.assertIsNone(run_tests.focused_patterns(self.BASE))

    def test_failed_inventory_and_invalid_base_keep_complete_coverage(self):
        for error in (OSError('missing git'), subprocess.CalledProcessError(1, ['git'])):
            with self.subTest(error=type(error).__name__), mock.patch.object(
                    run_tests, 'git', side_effect=error), contextlib.redirect_stderr(io.StringIO()):
                self.assertIsNone(run_tests.focused_patterns(self.BASE))
        with mock.patch.object(run_tests, 'git') as git, contextlib.redirect_stderr(io.StringIO()):
            self.assertIsNone(run_tests.focused_patterns('--malicious-option'))
            git.assert_not_called()

    def test_only_policy_environment_reservation_is_a_focused_config_change(self):
        before = {'local_material': {'directories': ['.claude/skills']}, 'modules': ['unchanged']}
        after = {'local_material': {'directories': ['.claude/skills', '.venv-policy']},
                 'modules': ['unchanged']}
        with mock.patch.object(run_tests, 'git', side_effect=[
                b'config/modules.json\0', json.dumps(before).encode(), json.dumps(after).encode()]):
            self.assertEqual(run_tests.focused_patterns(self.BASE), run_tests.MAINTENANCE_TESTS)
        after['modules'] = ['different']
        with mock.patch.object(run_tests, 'git', side_effect=[
                b'config/modules.json\0', json.dumps(before).encode(), json.dumps(after).encode()]):
            self.assertIsNone(run_tests.focused_patterns(self.BASE))

    def test_malformed_config_keeps_complete_coverage(self):
        with mock.patch.object(run_tests, 'git', side_effect=[b'config/modules.json\0', b'{}', b'{}']), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertIsNone(run_tests.focused_patterns(self.BASE))

    def test_plan_does_not_discover_or_execute_tests(self):
        for patterns, expected in [(run_tests.MAINTENANCE_TESTS, 'focused=true\n'),
                                   (None, 'focused=false\n')]:
            output = io.StringIO()
            with mock.patch.object(run_tests, 'focused_patterns', return_value=patterns), \
                    mock.patch.object(unittest.defaultTestLoader, 'discover') as discover, \
                    contextlib.redirect_stdout(output):
                self.assertEqual(run_tests.main(['--plan']), 0)
            self.assertEqual(output.getvalue(), expected)
            discover.assert_not_called()

    def test_focused_checks_preserve_both_success_and_failure(self):
        def fail():
            self.fail('intentional focused fixture failure')
        for test, expected in [(lambda: None, 0), (fail, 1)]:
            with self.subTest(expected=expected), mock.patch.object(
                    run_tests, 'focused_patterns', return_value=run_tests.MAINTENANCE_TESTS), \
                    mock.patch.object(unittest.defaultTestLoader, 'discover', side_effect=[
                        unittest.TestSuite([unittest.FunctionTestCase(lambda: None)]),
                        unittest.TestSuite([unittest.FunctionTestCase(test)])]) as discover, \
                    contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_tests.main([]), expected)
            self.assertEqual(discover.call_args_list, [
                mock.call('tests', pattern='test_source.py'),
                mock.call('tests', pattern='test_run_tests.py')])
