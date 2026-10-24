# SPDX-License-Identifier: Apache-2.0
"""Keep CI shards complete and preserve real test failures."""
import contextlib
import io
from pathlib import Path
import sys
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
