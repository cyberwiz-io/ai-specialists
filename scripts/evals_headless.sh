#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Compatibility entrypoint; Windows can invoke scripts/evals_runner.py directly.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 -B "$ROOT/scripts/evals_runner.py" "$@"
