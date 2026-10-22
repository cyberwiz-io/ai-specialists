#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify maintainer-attested independent review and exact release provenance.

Trusts GitHub collaborator permissions and the coordinator's truthful attestation;
this is not a cryptographic proof of reviewer independence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

MARKER = 'AI-SPECIALISTS-REVIEW: '
REQUIRED_CHECKS = ('acceptance', 'policy-compliance', 'security-acceptance',
                   'Analyze (python)', 'Analyze (actions)')


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def api(path):
    return json.loads(command('gh', 'api', path))


def pages(path, key=None):
    result = []
    for page in range(1, 101):
        data = api(f'{path}{"&" if "?" in path else "?"}per_page=100&page={page}')
        items = data[key] if key else data
        result.extend(items)
        if len(items) < 100:
            return result
    raise ValueError('GitHub pagination limit exceeded; cannot establish complete evidence')


def verify_review(comments, head, tree, permission):
    trusted = [c for c in comments if c.get('body', '').startswith(MARKER)
               and permission(c['user']['login']) in ('write', 'maintain', 'admin')]
    if not trusted:
        raise ValueError('No authorized coordinator attestation of independent review')
    comment = max(trusted, key=lambda c: (c.get('updated_at', c.get('created_at', '')), c['id']))
    record = json.loads(comment['body'][len(MARKER):])
    if not isinstance(record, dict):
        raise ValueError('Review attestation must be an object')
    report = record.get('report')
    if (record.get('head') != head or record.get('tree') != tree
            or not isinstance(record.get('reviewer'), str) or not record['reviewer'].strip()
            or not isinstance(report, str) or not report.strip()
            or record.get('report_sha256') != hashlib.sha256(report.encode('utf-8')).hexdigest()
            or record.get('verdict') != 'PASS' or record.get('blocking_findings') != []):
        raise ValueError('Review missing, stale, malformed, changed or blocking')
    return dict(record, comment_id=comment['id'], attester=comment['user']['login'])


def verify_checks(checks, sha):
    for name in REQUIRED_CHECKS:
        names = {name, 'candidate-checks / ' + name, 'candidate-security / ' + name}
        matching = [c for c in checks if c.get('name') in names and c.get('head_sha') == sha
                    and c.get('app', {}).get('slug') == 'github-actions']
        latest = max(matching, key=lambda c: c['id']) if matching else {}
        if latest.get('status') != 'completed' or latest.get('conclusion') != 'success':
            raise ValueError(f'Missing successful exact-commit check: {name}')


def verify_pr(pr, repo, sha):
    if (pr.get('merged') is not True or pr.get('merge_commit_sha') != sha
            or pr.get('base', {}).get('ref') != 'main'
            or pr.get('base', {}).get('repo', {}).get('full_name') != repo):
        raise ValueError('Candidate is not the mapped merged PR on repository main')


def verify_checkout(sha, tree, tag):
    if command('git', 'rev-parse', 'HEAD') != sha:
        raise ValueError('Checkout does not match candidate SHA')
    subprocess.run(['git', 'merge-base', '--is-ancestor', sha, 'origin/main'], check=True)
    if command('git', 'rev-parse', f'{sha}^{{tree}}') != tree:
        raise ValueError('Merged candidate tree differs from reviewed PR tree; review again')
    version = Path('VERSION').read_text().strip()
    if tag != f'v{version}':
        raise ValueError('Release tag differs from VERSION')
    if command('git', 'rev-parse', f'refs/tags/{tag}^{{commit}}') != sha:
        raise ValueError('Tag does not identify the exact candidate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('review', 'provenance', 'release'))
    parser.add_argument('--repo', required=True)
    parser.add_argument('--pr', required=True, type=int)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--tag')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo):
        raise ValueError('Invalid repository')
    if not re.fullmatch(r'[0-9a-f]{40}', args.sha) or args.pr < 1:
        raise ValueError('An exact SHA and positive PR number are required')
    prefix = f'repos/{args.repo}'
    pr = api(f'{prefix}/pulls/{args.pr}')
    head = pr['head']['sha']
    tree = api(f'{prefix}/git/commits/{head}')['tree']['sha']
    if args.mode == 'review' and args.sha != head:
        raise ValueError('Review target differs from current PR head')
    evidence = verify_review(pages(f'{prefix}/issues/{args.pr}/comments'), head, tree,
                             lambda login: api(f'{prefix}/collaborators/{login}/permission')['permission'])
    if args.mode != 'review':
        verify_pr(pr, args.repo, args.sha)
        verify_checkout(args.sha, tree, args.tag)
        if any(r['tag_name'] == args.tag for r in pages(f'{prefix}/releases')):
            raise ValueError('Release already exists; never replace assets or notes')
        if args.mode == 'release':
            verify_checks(pages(f'{prefix}/commits/{args.sha}/check-runs', 'check_runs'), args.sha)
    print(json.dumps({'sha': args.sha, 'reviewed_head': head, 'tree': tree,
                      'review_comment_id': evidence['comment_id'], 'attester': evidence['attester'],
                      'reviewer': evidence['reviewer'], 'report_sha256': evidence['report_sha256']}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Release gate failed: {error}')
