# SPDX-License-Identifier: Apache-2.0
"""Release metadata fails closed; no network or publishing in these tests."""
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('release_gate', Path(__file__).parents[1] / 'scripts/release_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.sha, self.tree = 'a' * 40, 'b' * 40
        report = 'Independent reviewer checked the exact candidate; no blocking findings.'
        self.record = dict(head=self.sha, tree=self.tree, reviewer='Separate subscription reviewer',
                           report=report, report_sha256=hashlib.sha256(report.encode()).hexdigest(),
                           verdict='PASS', blocking_findings=[])
        self.comment = dict(body=gate.MARKER + json.dumps(self.record), user={'login': 'maintainer'}, id=12)

    def verify(self, comments=None, permission='write'):
        return gate.verify_review(comments if comments is not None else [self.comment],
                                  self.sha, self.tree, lambda _: permission)

    def test_valid_attestation(self):
        self.assertEqual(self.verify()['comment_id'], 12)

    def test_missing_or_untrusted_attestation(self):
        for comments, permission in [([], 'admin'), ([self.comment], 'read')]:
            with self.subTest(permission=permission), self.assertRaises(ValueError):
                self.verify(comments, permission)

    def test_every_review_binding_is_required(self):
        for key, value in [('head', 'c' * 40), ('tree', 'd' * 40), ('reviewer', ''),
                           ('report_sha256', '0' * 64), ('verdict', 'BLOCKING'),
                           ('blocking_findings', ['unfixed']), ('report', '')]:
            record = dict(self.record, **{key: value})
            comment = dict(self.comment, body=gate.MARKER + json.dumps(record))
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify([comment])

    def test_newer_revocation_cannot_fall_back_to_old_pass(self):
        revoked = dict(self.comment, id=13, body=gate.MARKER + '{bad json')
        with self.assertRaises(ValueError):
            self.verify([self.comment, revoked])

    def test_untrusted_comments_cannot_revoke_trusted_review(self):
        other = dict(self.comment, id=13, user={'login': 'outsider'}, body=gate.MARKER + '{}')
        result = gate.verify_review([self.comment, other], self.sha, self.tree,
                                   lambda login: 'admin' if login == 'maintainer' else 'read')
        self.assertEqual(result['comment_id'], 12)

    def test_checks_require_exact_sha_app_and_success(self):
        checks = [dict(name=name, head_sha=self.sha, conclusion='success', status='completed',
                       app={'slug': 'github-actions'}, id=i) for i, name in enumerate(gate.REQUIRED_CHECKS)]
        gate.verify_checks(checks, self.sha)
        for field, value in [('head_sha', 'c' * 40), ('conclusion', 'skipped'),
                             ('status', 'in_progress'), ('app', {'slug': 'other'})]:
            broken = [dict(c) for c in checks]
            broken[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.verify_checks(broken, self.sha)
        with self.assertRaises(ValueError):
            gate.verify_checks(checks[1:], self.sha)

    def test_latest_check_failure_wins(self):
        checks = [dict(name=name, head_sha=self.sha, conclusion='success', status='completed',
                       app={'slug': 'github-actions'}, id=i) for i, name in enumerate(gate.REQUIRED_CHECKS)]
        checks.append(dict(checks[0], id=100, conclusion='failure'))
        with self.assertRaises(ValueError):
            gate.verify_checks(checks, self.sha)

    def test_merged_pr_mapping(self):
        pr = dict(merged=True, merge_commit_sha=self.sha, base={'ref': 'main', 'repo': {'full_name': 'o/r'}})
        gate.verify_pr(pr, 'o/r', self.sha)
        for field, value in [('merged', False), ('merge_commit_sha', 'c' * 40), ('base', {'ref': 'other'})]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.verify_pr(dict(pr, **{field: value}), 'o/r', self.sha)


class CheckoutProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        previous = os.getcwd()
        os.chdir(self.temp.name)
        self.addCleanup(os.chdir, previous)
        self.git('init', '-q')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'tag.gpgsign', 'false')
        self.git('config', 'core.hooksPath', self.temp.name + '/no-hooks')
        self.git('config', 'user.name', 'Fixture Reviewer')
        self.git('config', 'user.email', 'fixture@example.invalid')
        Path('VERSION').write_text('1.1\n')
        self.git('add', 'VERSION')
        self.git('commit', '-qm', 'candidate')
        self.sha = self.git('rev-parse', 'HEAD')
        self.tree = self.git('rev-parse', 'HEAD^{tree}')
        self.git('update-ref', 'refs/remotes/origin/main', self.sha)
        self.git('tag', 'v1.1')

    @staticmethod
    def git(*args):
        return subprocess.check_output(['git', *args], text=True, stderr=subprocess.DEVNULL).strip()

    def test_exact_candidate_and_tag_pass(self):
        gate.verify_checkout(self.sha, self.tree, 'v1.1')

    def test_wrong_version_and_reviewed_tree_fail(self):
        for tree, tag in [(self.tree, 'v9.0'), ('c' * 40, 'v1.1')]:
            with self.subTest(tree=tree, tag=tag), self.assertRaises(ValueError):
                gate.verify_checkout(self.sha, tree, tag)

    def test_off_main_candidate_fails(self):
        Path('extra').write_text('new tree')
        self.git('add', 'extra')
        self.git('commit', '-qm', 'not on main')
        sha = self.git('rev-parse', 'HEAD')
        with self.assertRaises(subprocess.CalledProcessError):
            gate.verify_checkout(sha, self.git('rev-parse', 'HEAD^{tree}'), 'v1.1')

    def test_moved_tag_and_wrong_checkout_fail(self):
        Path('extra').write_text('new tree')
        self.git('add', 'extra')
        self.git('commit', '-qm', 'next')
        next_sha = self.git('rev-parse', 'HEAD')
        with self.assertRaises(ValueError):
            gate.verify_checkout(self.sha, self.tree, 'v1.1')
        self.git('tag', '-f', 'v1.1', next_sha)
        self.git('checkout', '-q', self.sha)
        with self.assertRaises(ValueError):
            gate.verify_checkout(self.sha, self.tree, 'v1.1')
