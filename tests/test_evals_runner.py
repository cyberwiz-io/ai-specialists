# SPDX-License-Identifier: Apache-2.0
"""Exercise the runner with a fake CLI; never invoke a model provider."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evals_runner

HARNESS_NAMES = ("scripts/evals.py", "scripts/packlib/evals.py", "scripts/evals_runner.py",
                 "scripts/evals_headless.sh", ".claude/agents/card-eval-subject.md",
                 ".claude/agents/card-eval-grader.md")


class RunnerTests(unittest.TestCase):
    def test_native_transport_preserves_prompt_and_response_bytes(self):
        import base64
        self.fake.write_text('''import base64, json, sys
data = sys.stdin.buffer.read()
result = {'result': base64.b64encode(data).decode(), 'modelUsage': {'native-model': {}}}
sys.stdout.buffer.write(json.dumps(result).encode() + b'\\r\\n')
sys.stderr.buffer.write(b'diagnostic\\r\\n')
''')
        prompt = 'First line\nSecond line: café\n'
        reply, receipt = evals_runner.session([sys.executable, str(self.fake)], prompt, 'native-model', 5)
        self.assertEqual(base64.b64decode(reply), prompt.encode('utf-8'))
        raw = json.dumps({'result': reply, 'modelUsage': {'native-model': {}}}).encode() + b'\r\n'
        self.assertEqual(receipt['input_sha256'], hashlib.sha256(prompt.encode('utf-8')).hexdigest())
        self.assertEqual(receipt['response_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(receipt['stderr_sha256'], hashlib.sha256(b'diagnostic\r\n').hexdigest())

    def test_affirmative_grade_requires_quote_from_reply(self):
        from packlib import evals
        fixture = {'id': 'one', 'grade': 'grade.json', 'acceptance': ['Useful'], 'traits': [], 'must_not': []}
        grade = {'fixture': 'one', 'acceptance': [{'item': 'Useful', 'verdict': 'pass',
                 'evidence': 'Useful result', 'quote': 'invented quote'}], 'traits': [], 'must_not': []}
        self.assertTrue(evals.check_grade(fixture, grade, reply='A reply'))
        grade['acceptance'][0]['quote'] = 'A reply'
        self.assertEqual(evals.check_grade(fixture, grade, reply='A reply'), [])

    def test_grade_json_accepts_only_plain_or_single_fenced_document(self):
        expected = {"fixture": "one"}
        for text in ('{"fixture":"one"}', '```json\n{"fixture":"one"}\n```'):
            self.assertEqual(evals_runner.grade_json(text), expected)
        for text in ('Comment\n```json\n{}\n```', '```json\n{}\n```\nIgnored text', '{} {}'):
            with self.assertRaises(ValueError):
                evals_runner.grade_json(text)

    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name)
        self.folder = self.root / 'work/evals/test'
        self.folder.mkdir(parents=True)
        self.fake = self.root / 'fake.py'
        self.fake.write_text('''import json, sys, time
prompt = sys.stdin.read()
model = sys.argv[sys.argv.index('--model') + 1]
assert sys.argv[sys.argv.index('--tools') + 1] == ''
assert '--no-session-persistence' in sys.argv
assert sys.argv[sys.argv.index('--setting-sources') + 1] == ''
assert '--strict-mcp-config' in sys.argv
assert json.loads(sys.argv[sys.argv.index('--mcp-config') + 1]) == {'mcpServers': {}}
assert '--disable-slash-commands' in sys.argv
if 'TIMEOUT' in prompt: time.sleep(2)
if 'DENIED' in prompt:
    print('permission denied', file=sys.stderr); sys.exit(7)
if 'BAD' in prompt: print('invalid'); sys.exit(0)
if 'INVALIDGRADE' in prompt:
    print(json.dumps({'result': '{}'})); sys.exit(0)
if 'GRADE' in prompt:
    result = json.dumps({'fixture': 'one', 'acceptance': [{'item': 'Useful', 'verdict': 'pass', 'evidence': 'A reply', 'quote': 'A reply'}], 'traits': [], 'must_not': []})
else: result = 'A reply'
print(json.dumps({'result': result, 'is_error': False, **({'modelUsage': {model: {}}} if 'UNKNOWN' not in prompt else {})}))
''')
        self.fixture = {'id': 'one', 'key': 'one', 'acceptance': ['Useful'], 'traits': [], 'must_not': []}
        for key, content in [('subject_prompt', 'SUBJECT'), ('grader_prompt', 'GRADE')]:
            path = self.folder / (key + '.md')
            path.write_text(content)
            self.fixture[key] = str(path.relative_to(self.root))
            self.fixture[key.replace('_prompt', '_sha256')] = hashlib.sha256(content.encode()).hexdigest()
        for key in ['output', 'grade']:
            self.fixture[key] = str((self.folder / key).relative_to(self.root))
        for name in HARNESS_NAMES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((name + '\n').encode())
        self.record = {'model': 'subject-model', 'grader': 'grader-model', 'fixtures': [self.fixture],
                       'harness_sha256': {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest()
                                          for name in HARNESS_NAMES}}
        self.save()

    def save(self):
        (self.folder / 'run.json').write_text(json.dumps(self.record))

    def run_fake(self, **kwargs):
        return evals_runner.run(self.root, 'test', command=[sys.executable, str(self.fake)], **kwargs)

    def change_prompt(self, value):
        (self.root / self.fixture['subject_prompt']).write_text(value)
        self.fixture['subject_sha256'] = hashlib.sha256(value.encode()).hexdigest()
        self.save()

    def test_separate_models_and_observed_identity_and_resume(self):
        self.assertEqual(self.run_fake(), 0)
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(receipt['subject']['requested_model'], 'subject-model')
        self.assertEqual(receipt['grader']['reported_models'], ['grader-model'])
        self.assertEqual(receipt['status'], 'complete')
        self.fake.unlink()  # Valid, unchanged completion is reused without another CLI call.
        self.assertEqual(self.run_fake(), 0)

    def test_permission_failure_is_incomplete_and_not_retried(self):
        self.change_prompt('DENIED')
        self.assertEqual(self.run_fake(), 1)
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(receipt['error'], 'permission')
        self.assertFalse((self.root / self.fixture['grade']).exists())

    def test_timeout_and_malformed_response_fail(self):
        self.change_prompt('TIMEOUT')
        self.assertEqual(self.run_fake(timeout=0.05), 1)
        self.change_prompt('BAD')
        self.assertEqual(self.run_fake(), 1)

    def test_changed_prompt_and_output_refused(self):
        (self.root / self.fixture['subject_prompt']).write_text('tampered')
        self.assertEqual(self.run_fake(), 1)
        self.change_prompt('SUBJECT')
        self.assertEqual(self.run_fake(), 0)
        (self.root / self.fixture['output']).write_text('changed')
        self.assertEqual(self.run_fake(), 1)

    def test_missing_identity_is_not_invented(self):
        self.change_prompt('UNKNOWN')
        self.assertEqual(self.run_fake(), 0)
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(receipt['subject']['reported_models'], [])
        self.assertEqual(receipt['subject']['identity_source'], 'unobserved')

    def test_invalid_grades_preserve_reply_and_raw_attempts_without_replay(self):
        path = self.root / self.fixture['grader_prompt']
        path.write_text('INVALIDGRADE')
        self.fixture['grader_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        self.assertEqual(self.run_fake(), 1)
        self.assertEqual((self.root / self.fixture['output']).read_bytes(), b'A reply')
        self.assertFalse((self.root / self.fixture['grade']).exists())
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(len(receipt['grader_attempts']), 2)
        for attempt in receipt['grader_attempts']:
            raw = (self.root / attempt['raw_path']).read_bytes()
            self.assertEqual(raw, b'{}')
            self.assertEqual(hashlib.sha256(raw).hexdigest(), attempt['raw_sha256'])
        self.fake.unlink()
        self.assertEqual(self.run_fake(), 1)  # Existing evidence cannot be replayed or overwritten.
        self.assertEqual((self.root / self.fixture['output']).read_bytes(), b'A reply')

    def test_changed_harness_is_refused_before_any_session(self):
        from unittest import mock
        (self.root / HARNESS_NAMES[0]).write_bytes(b'changed')
        with mock.patch.object(evals_runner, 'session') as native:
            with self.assertRaisesRegex(ValueError, 'harness'):
                self.run_fake()
            native.assert_not_called()

    def test_missing_or_incomplete_harness_coverage_is_refused(self):
        from unittest import mock
        original = dict(self.record['harness_sha256'])
        for hashes in (None, {}, {HARNESS_NAMES[0]: original[HARNESS_NAMES[0]]},
                       dict(original, extra='0' * 64)):
            self.record['harness_sha256'] = hashes
            self.save()
            with mock.patch.object(evals_runner, 'session') as native:
                with self.assertRaisesRegex(ValueError, 'harness'):
                    self.run_fake()
                native.assert_not_called()

    def test_only_invalid_grade_gets_one_fresh_retry(self):
        from unittest import mock
        good = json.dumps({'fixture': 'one', 'acceptance': [{'item': 'Useful', 'verdict': 'pass',
                           'evidence': 'A reply', 'quote': 'A reply'}], 'traits': [], 'must_not': []})
        with mock.patch.object(evals_runner, 'session', side_effect=[
                ('A reply', {'requested_model': 'subject-model'}),
                ('{}', {'requested_model': 'grader-model'}),
                (good, {'requested_model': 'grader-model'})]) as native:
            self.assertEqual(self.run_fake(), 0)
            self.assertEqual(native.call_count, 3)
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(receipt['status'], 'complete')
        self.assertEqual(len(receipt['grader_attempts']), 2)

    def test_valid_failing_grade_is_not_retried(self):
        from unittest import mock
        failed = json.dumps({'fixture': 'one', 'acceptance': [{'item': 'Useful', 'verdict': 'fail',
                             'evidence': 'Not useful', 'quote': ''}], 'traits': [], 'must_not': []})
        with mock.patch.object(evals_runner, 'session', side_effect=[
                ('A reply', {'requested_model': 'subject-model'}),
                (failed, {'requested_model': 'grader-model'})]) as native:
            self.assertEqual(self.run_fake(), 0)
            self.assertEqual(native.call_count, 2)
        receipt = json.loads((self.folder / 'execution.json').read_text())['fixtures']['one']
        self.assertEqual(len(receipt['grader_attempts']), 1)

    def test_multiple_fixtures_all_must_complete(self):
        other = dict(self.fixture, id='two', key='two')
        for key in ('output', 'grade'):
            other[key] += '2'
        self.record['fixtures'].append(other)
        self.save()
        # The fake grader names fixture one; fixture two must fail validation.
        self.assertEqual(self.run_fake(parallel=2), 1)
        statuses = json.loads((self.folder / 'execution.json').read_text())['fixtures']
        self.assertEqual(statuses['one']['status'], 'complete')
        self.assertEqual(statuses['two']['status'], 'failed')

    def test_completed_receipt_survives_later_interruption(self):
        from unittest import mock
        import time
        other = dict(self.fixture, id='two', key='two')
        for key in ('output', 'grade'):
            other[key] += '2'
        self.record['fixtures'].append(other)
        self.save()
        calls = []
        def session(command, prompt, model, timeout):
            calls.append(prompt)
            if len(calls) == 3:
                deadline = time.monotonic() + 2
                while not (self.folder / 'execution.json').exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue((self.folder / 'execution.json').exists())
                raise RuntimeError('interrupted')
            reply = 'A reply' if len(calls) == 1 else json.dumps({
                'fixture': 'one', 'acceptance': [{'item': 'Useful', 'verdict': 'pass',
                'evidence': 'Useful', 'quote': 'A reply'}], 'traits': [], 'must_not': []})
            return reply, {'requested_model': model}
        with mock.patch.object(evals_runner, 'session', side_effect=session):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                self.run_fake()
        receipt = json.loads((self.folder / 'execution.json').read_text())
        self.assertEqual(receipt['fixtures']['one']['status'], 'complete')

    def test_invalid_run_and_parallel(self):
        for name in ['../escape', '']:
            with self.assertRaises(ValueError):
                evals_runner.run(self.root, name)
        for parallel in [0, 9]:
            with self.assertRaises(ValueError):
                self.run_fake(parallel=parallel)


if __name__ == '__main__':
    unittest.main()
