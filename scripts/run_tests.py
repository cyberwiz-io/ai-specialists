# SPDX-License-Identifier: Apache-2.0
"""Run the complete unittest discovery, optionally split across two CI jobs."""
import argparse
import unittest


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
    args = parser.parse_args(argv)
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
