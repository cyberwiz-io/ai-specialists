#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Carry out a prepared card eval run with Claude Code in headless mode: for every fixture still lacking a reply or
# grade, one fresh `claude -p` session writes the reply and another grades it. Each session starts outside the
# repository with memory and settings off and only the card-eval subject or grader instructions, so nothing but the
# prompt file reaches it. Each step is retried once. Usage: scripts/evals_headless.sh <run> [parallel sessions, default 6]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="${1:?usage: scripts/evals_headless.sh <run> [parallel]}"
PARALLEL="${2:-6}"
WORK="$ROOT/work/evals/$RUN"
[ -f "$WORK/run.json" ] || { echo "no prepared run at work/evals/$RUN; run scripts/evals.py prepare first" >&2; exit 1; }
MODEL="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["model"])' "$WORK/run.json")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 - "$ROOT/.claude/agents" "$TMP/agents.json" <<'PY'
import json, re, sys
agents = {}
for name in ("card-eval-subject", "card-eval-grader"):
    _, head, body = open(f"{sys.argv[1]}/{name}.md", encoding="utf-8").read().split("---", 2)
    tools = [t.strip() for t in re.search(r"^tools: (.*)$", head, re.M).group(1).split(",")]
    agents[name] = {"description": re.search(r"^description: (.*)$", head, re.M).group(1),
                    "prompt": body.strip(), "tools": tools}
json.dump(agents, open(sys.argv[2], "w"))
PY
mkdir -p "$TMP/cwd"
export WORK MODEL TMP
one() {
  local key="$1" step
  session() {
    (cd "$TMP/cwd" && echo "$2" | CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --setting-sources "" \
      --agents "$(cat "$TMP/agents.json")" --agent "$1" --model "$MODEL" --allowedTools "Read Write" \
      --permission-mode acceptEdits --add-dir "$WORK" > /dev/null 2>&1) || true
  }
  for step in 1 2; do
    [ -s "$WORK/outputs/$key.md" ] || session card-eval-subject \
      "Prompt file: \`$WORK/prompts/$key.subject.md\`. Output path: \`$WORK/outputs/$key.md\`."
  done
  [ -s "$WORK/outputs/$key.md" ] || { echo "missing reply $key"; return 0; }
  for step in 1 2; do
    [ -s "$WORK/grades/$key.json" ] || session card-eval-grader "Grader prompt: \`$WORK/prompts/$key.grader.md\`."
  done
  [ -s "$WORK/grades/$key.json" ] && echo "done $key" || echo "missing grade $key"
}
export -f one
cd "$ROOT"
python3 -B scripts/evals.py status --run "$RUN" | awk -F'\t' 'NF >= 3 {print $2}' | xargs -P "$PARALLEL" -I{} bash -c 'one "$1"' _ {}
python3 -B scripts/evals.py status --run "$RUN" | tail -1
