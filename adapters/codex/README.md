# Codex

`python3 -B scripts/pack.py build` generates the plugin, leads, custom agents and marketplace. This README is maintained by hand.

## Install in an isolated test

Use a published release tag or a reviewed local checkout. Start with a new disposable project and an isolated `CODEX_HOME`; refuse to reuse either destination. In macOS Terminal:

These are proposed acceptance commands, not a verified install path on the current devices. The maintained ai-home launcher previously rejected redirected `CODEX_HOME`. If your launcher denies it, stop; retain its credential and permission controls and establish an approved route using the existing home. Never copy credential files into a test home. Use the client's supported login procedure where isolation is permitted.

```sh
test ! -e "$HOME/ai-specialists-codex-test" || { echo 'Destination exists; stop.' >&2; exit 1; }
mkdir -p "$HOME/ai-specialists-codex-test/project" "$HOME/ai-specialists-codex-test/home"
export CODEX_HOME="$HOME/ai-specialists-codex-test/home"
git clone --branch <release-tag> https://github.com/cyberwiz-io/ai-specialists "$HOME/ai-specialists-codex-test/source"
cd "$HOME/ai-specialists-codex-test/project"
codex plugin marketplace add "$HOME/ai-specialists-codex-test/source"
codex plugin add ai-specialists@ai-specialists
codex plugin list
```

The `codex plugin add` command installs the plugin. Confirm its availability with Codex's plugin controls. Before copying custom agents, check that the destination does not exist; copy only into the empty disposable project:

```sh
test ! -e .codex/agents || { echo 'Agent destination exists; stop.' >&2; exit 1; }
mkdir -p .codex/agents
cp "$HOME/ai-specialists-codex-test/source"/adapters/codex/agents/*.toml .codex/agents/
```

In Windows PowerShell, use native paths and the same collision checks:

```powershell
$root = Join-Path $HOME 'ai-specialists-codex-test'
if (Test-Path $root) { throw "Destination exists; stop: $root" }
New-Item -ItemType Directory -Force (Join-Path $root 'project'), (Join-Path $root 'home') | Out-Null
$env:CODEX_HOME = Join-Path $root 'home'
git clone --branch <release-tag> https://github.com/cyberwiz-io/ai-specialists (Join-Path $root 'source')
Set-Location (Join-Path $root 'project')
codex plugin marketplace add (Join-Path $root 'source')
codex plugin add ai-specialists@ai-specialists
codex plugin list
if (Test-Path '.codex/agents') { throw 'Agent destination exists; stop.' }
New-Item -ItemType Directory '.codex/agents' | Out-Null
Copy-Item (Join-Path $root 'source/adapters/codex/agents/*.toml') '.codex/agents/'
```

Replace `<release-tag>` with the exact release tag under test. For a reviewed local checkout, replace the GitHub clone command with `git clone --no-hardlinks /absolute/path/to/reviewed-checkout <test-root>/source` (use a native Windows source path in PowerShell), then run `git -C <test-root>/source checkout --detach <full-reviewed-commit>`. Verify `git -C <test-root>/source rev-parse HEAD` before installation. No 1.5 release tag is currently published. Ensure the Codex root session uses its supported read-only sandbox and approval controls before delegating; child TOML feature reductions are not a sandbox. In the test project, confirm the `security-lead` skill is discoverable, then run the fictional handoff and boundary probes in [host acceptance](../../docs/HOST-ACCEPTANCE.md). Inspect the actual subagent thread and tool trace for worker identity, the lead-supplied method, an allowed read, and host-denied write, command and nested-agent probes. Record requested and observed models. A prose refusal or self-reported identity is not proof of host enforcement. The lead may run the worker itself if it cannot delegate: record that as a failure of the delegation criterion, not as worker acceptance. Record any private installed-skill runtime check only in its approved private evidence location.

## Update and remove

For update acceptance, use a disposable marketplace source that advances from reviewed commit A to reviewed commit B, with changed plugin bytes and a higher plugin version at B. Claude Code retained old cached bytes on a same-version update; the Codex result remains unobserved. Record the full source commit and installed-file hashes at A in an ownership ledger; retain each installed version's path/hash entries. Advance only the task-owned source branch or local checkout to B, then run `codex plugin marketplace upgrade ai-specialists`. The copied `.codex/agents/*.toml` files need a separate update: record their exact paths and SHA-256 hashes at A. Before copying, require each destination to match its recorded A hash; stop on any user modification or unowned destination collision. Copy the corresponding B files from `<test-root>/source/adapters/codex/agents/` after verifying that checkout is exactly B, verify every destination against B, and record membership changes. Do not delete an A-only file until its exact task ownership and unchanged A bytes are confirmed. Marketplace refresh alone does not update these copied agents or prove that an installed plugin was refreshed; inspect installed bytes, and use supported plugin update or task-owned reinstall controls if needed. Restart the client, verify the cached source commit and changed installed-file hashes, rediscover the lead and worker, and repeat behavior and boundary checks. A fixed tag alone cannot prove a byte-changing update. If the installed bytes do not change, record an incomplete update; do not reset unrelated caches or installations. These update steps remain proposed until the trial records their results.

Remove only the test plugin and marketplace with Codex's supported controls; remove only the copied `.codex/agents/*.toml` files whose exact path and byte hash match the retained per-version installation ownership ledger, including any retained A-only files after confirming the disposable project is the one created above. Remove the test root only after confirming its exact path. Do not overwrite or delete any pre-existing config, agent, project, marketplace or plugin.

## Evidence and limits

Follow-up status, 2026-10-24: Mac Codex 0.164.0 traced an actual low-effort `gpt-5.6-luna` parent and `gpt-6-luna` custom project-planner handoff. Separate reader setup checks succeeded, but a later marker-reading child used the wrong generic role, and subsequent preflights exposed an additional connector despite a disable setting. No complete custom-role/read/boundary trial is accepted. Windows Codex 0.163.0 installed the exact 1.3.0 GitHub baseline through a genuine Orca terminal without redirecting its home or copying credentials; the managed ai-home launcher remains unsupported. These are partial observations. Current-candidate update, restart, repeated behavior, removal and complete native acceptance remain pending. See [validation](../../docs/VALIDATION.md) for the separate evidence and limits.

Historical evidence: a 2026-10-17 GitHub install attempt on Codex 0.163.0 (macOS) was refused at `codex plugin marketplace add` and `codex plugin list` because the local launcher rejected the redirected `CODEX_HOME`. An earlier cloud-container run added a marketplace from a local checkout and installed the plugin, but ran no model. Neither is a current host acceptance run. Current device versions are inventory only. Current Mac Studio acceptance is pending; Windows installation and catalog discovery are now observed (see [Windows](../../docs/WINDOWS.md)); full behavioral acceptance remains pending; see [host acceptance](../../docs/HOST-ACCEPTANCE.md) and [validation](../../docs/VALIDATION.md). A 2026-10-22 Mac session ran through the approved normal-home ai-home launcher, but two disposable-project sessions could not invoke the exact custom worker. Windows ai-home reports managed native launch unsupported. On macOS Codex 0.164.0, Orca's supported native entrypoint installed plugin 1.4.0 from exact GitHub commit `ce0ceb576c75bfeb80b237f58eb114c4dc3beec9` without redirecting the managed home or copying credentials. Native controls discovered the installed `ai-specialists:business-operations-lead`, and all 142 generated agent TOMLs were copied byte-for-byte into a disposable project. Existing unrelated plugin and marketplace listings were preserved. A subsequent parent session reported the required reader identity tools unavailable and stopped before delegation or boundary probes; no worker handoff or allowed read was observed. Installation and discovery are observed; complete acceptance, byte-changing update, restart repetition and owned removal remain pending. See [validation](../../docs/VALIDATION.md).

On 2026-10-23, a further protected normal-home functional check invoked the actual project-planner custom role and received its handoff. Native child activity resolved to `gpt-6-astra` while the parent selection covered `gpt-6.1-sol`; no allowed read was observed and the other probes were not attempted. This check used a copied 1.4 agent in an older disposable checkout and is unaccepted. A temporary shell-off environment-tools probe also reported no direct file reader. Neither check establishes plugin installation, a permission-denial event or current Codex acceptance; see [validation](../../docs/VALIDATION.md).

Codex plugin marketplaces do not supply custom agents, so the TOML files are copied separately. Custom agents inherit the parent sandbox and approval settings. Their generated files do not pin a model; observe the resolved child model and use a supported explicit override when selection requires one. Do not claim a custom agent is read-only based only on its TOML. References: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [plugin installation](https://developers.openai.com/codex/plugins/).
