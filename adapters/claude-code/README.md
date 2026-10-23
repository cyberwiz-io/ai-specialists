# Claude Code

`python3 -B scripts/pack.py build` generates the marketplace and plugins. This README is maintained by hand.

## Install in an isolated test

Use a published release tag or a reviewed local checkout. Start with a new disposable project and a new Claude config directory; stop if either destination already exists. In macOS Terminal:

```sh
test ! -e "$HOME/ai-specialists-claude-test" || { echo 'Destination exists; stop.' >&2; exit 1; }
mkdir -p "$HOME/ai-specialists-claude-test/project" "$HOME/ai-specialists-claude-test/config"
export CLAUDE_CONFIG_DIR="$HOME/ai-specialists-claude-test/config"
git clone --branch <release-tag> https://github.com/cyberwiz-io/ai-specialists "$HOME/ai-specialists-claude-test/source"
cd "$HOME/ai-specialists-claude-test/project"
claude plugin marketplace add "$HOME/ai-specialists-claude-test/source" --scope project
claude plugin install security@ai-specialists --scope project
claude plugin list
claude plugin details security@ai-specialists
```

In Windows PowerShell, use the same sequence with native paths and refuse an existing root:

```powershell
$root = Join-Path $HOME 'ai-specialists-claude-test'
if (Test-Path $root) { throw "Destination exists; stop: $root" }
New-Item -ItemType Directory -Force (Join-Path $root 'project'), (Join-Path $root 'config') | Out-Null
$env:CLAUDE_CONFIG_DIR = Join-Path $root 'config'
git clone --branch <release-tag> https://github.com/cyberwiz-io/ai-specialists (Join-Path $root 'source')
Set-Location (Join-Path $root 'project')
claude plugin marketplace add (Join-Path $root 'source') --scope project
claude plugin install security@ai-specialists --scope project
claude plugin list
claude plugin details security@ai-specialists
```

Replace `<release-tag>` with the exact release tag under test. For a reviewed local checkout, replace the GitHub clone command with `git clone --no-hardlinks /absolute/path/to/reviewed-checkout <test-root>/source` (use a native Windows source path in PowerShell), then run `git -C <test-root>/source checkout --detach <full-reviewed-commit>`. Verify `git -C <test-root>/source rev-parse HEAD` before installation. No 1.2 release tag is currently published. For a family other than `security`, use its exact marketplace name. The `ai-specialists-all` bundle is also available. In a session opened in the test project, verify the installed component inventory with `claude plugin details`, then invoke the lead (for example, `/security:security-lead`) and run the fictional handoff and boundary probes in [host acceptance](../../docs/HOST-ACCEPTANCE.md). Use the subagent/task trace to verify the worker identity, lead-supplied method, actual read, and host-denied write, command and nested-agent probes. Record requested and observed models. Do not count self-reported identity or prose refusals as proof of host enforcement. Record any private installed-skill runtime check only in its approved private evidence location.

## Update and remove

For update acceptance, use a disposable marketplace source that advances from reviewed commit A to reviewed commit B, with changed plugin bytes. Record the full source commit and installed-file hashes at A. Advance only the task-owned source branch or local checkout to B, then run `claude plugin marketplace update ai-specialists` and `claude plugin update security@ai-specialists --scope project`. Restart the client, verify the cached source commit and changed installed-file hashes, rediscover the lead and worker, and repeat behavior and boundary checks. A fixed tag alone cannot prove a byte-changing update. If the installed bytes do not change, record an incomplete update; do not reset unrelated caches or installations. These update steps remain proposed until the trial records their results.

Uninstall only the project-scoped plugin with `claude plugin uninstall security@ai-specialists --scope project`, then remove only the project-scoped marketplace declaration with `claude plugin marketplace remove ai-specialists --scope project`. Remove the test root only after confirming it is the exact disposable directory created above. Do not delete or overwrite an existing config, project, marketplace or plugin.

## Evidence

Historical evidence: Claude Code 2.1.302 passed `claude plugin validate --strict` and a local `--plugin-dir` smoke test; a GitHub marketplace install was not part of that record. Current device versions are inventory only. The four current macOS/Windows Claude Code and Codex acceptance runs are pending; see [host acceptance](../../docs/HOST-ACCEPTANCE.md) and [validation](../../docs/VALIDATION.md). Partial 2026-10-22 Mac and Windows trials installed business-operations from the candidate GitHub branch and traced native workers, with behavior and review gaps. They do not establish this complete install/update/removal procedure; see the partial observations in [validation](../../docs/VALIDATION.md).

References: [subagents](https://code.claude.com/docs/en/sub-agents), [plugins](https://code.claude.com/docs/en/plugins-reference.md), and [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces.md).
