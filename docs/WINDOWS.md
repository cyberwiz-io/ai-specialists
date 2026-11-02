# Windows candidate availability

AI Specialists 1.5 (plugin version 1.5.0) remains a release candidate. Access to
its current Git source does not require a stable release or published ZIP.
The catalog contains portable instructions; loading it does not execute the
maintenance scripts or macOS tools.

## Native commands

From a checkout in PowerShell, use a Python 3.9+ executable as an argument,
including quotes when its path contains spaces:

```powershell
python -B scripts/pack.py check
python -B scripts/pack.py find debugging
```

The existing native evaluator is `python -B scripts/evals_runner.py`; the
`evals_headless.sh` wrapper requires Bash and is unnecessary on Windows.
Evaluations still require an explicit evaluation request. No evaluations ran
for this compatibility repair.

Use `Join-Path`, `Copy-Item -LiteralPath`, and argument arrays instead of POSIX
path concatenation or shell command strings. For copied custom agents, retain
an ownership/hash ledger and refuse to overwrite user modifications, as the
[Codex adapter](../adapters/codex/README.md) describes.

AppleScript, `launchd`, Metal/MLX, Xcode and iOS Simulator require macOS. A
workflow that actually requires one of them must return
`UNSUPPORTED_PLATFORM: requires macOS`, without executing it or claiming success.
On Windows use the host's native file APIs, native supported browser/desktop
adapter, and an available Windows model runtime where the task permits those
alternatives. This is an explicit platform limit, not a failure to load the
portable catalog. Windows does not emulate those Apple capabilities.

## Existing client update mechanisms

Use the configured GitHub marketplace, retaining unrelated plugins:

```powershell
codex plugin marketplace upgrade ai-specialists
codex plugin add ai-specialists@ai-specialists
claude plugin marketplace update ai-specialists
claude plugin update ai-specialists-all@ai-specialists --scope user
```

Inspect the marketplace Git SHA and compare installed files with that revision.
A same-version cache can remain stale; an update command reporting success is
insufficient. If necessary, use the client's native removal and installation
commands for only this plugin, then recheck its files. Do not delete cache trees
manually. Custom Codex agent copies require their separate owned-file update.
Other Agent Skills hosts can reference this checkout's `skills/` through their
supported local skill-directory setting; Git updates then reach that reference.
Do not install a scheduler or copy credentials.

Start a new conversation after an update. Preserve active sessions; a changed
cache or catalog does not establish that an existing conversation reloaded it.
Orca inventories client skills but does not itself replace client plugin updates.

## Validation environments

Create future policy-check environments under the native temporary directory,
outside the checkout. For example, choose a new task-specific name under
`$env:TEMP`, refuse an existing destination, then use `python -m venv` with that
exact path and install only `PyYAML==6.0.3`. Invoke its `Scripts/python.exe` on
Windows (`bin/python` on macOS/Linux). Record the path, check for links and usage,
and remove it through a permitted native cleanup after its last use. Never
bypass a cleanup rejection.

The legacy `.venv-policy` location is reserved as local material: untracked
contents do not become pack source. Tracked files remain in inventory and are
checked; absent Git metadata does not silently hide unknown material.

## Observed scope, 2026-10-26

Before repair, both configured GitHub marketplaces referenced
`c24b434e0e0c867e95956c475ed5c64bd6be64ae`. Claude Code 2.1.308 enabled
`ai-specialists-all` 1.5.0, and Codex CLI 0.164.0 enabled `ai-specialists` 1.5.0.
Orca discovered the `specialists` lead from both client plugin caches. The
current Codex conversation also exposed the 18 lead skills. These observations
establish installation and discovery, not full worker behavior or enforcement.

The previously reported 23 Windows failures belong to the separate shared-skills
repository, not the AI Specialists suite. Targeted reproduction found 19 cutover
and four vendor-fetch failures. Their repairs must be verified in that repository;
no complete AI Specialists suite is needed or claimed for this maintenance task.

Antigravity's native plugin installer also processed all 142 skills and listed
`ai-specialists` 1.5.0 enabled. Pi's existing `skills` setting now references the
18 lead directories in the maintained checkout. These are installation/configuration
observations; fresh model turns for those clients are not established by them.
Hermes has a shared skills directory but no native executable was found on PATH;
its Windows runtime loading remains unverified.
