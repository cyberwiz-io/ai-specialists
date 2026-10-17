#!/usr/bin/env python3
"""Pinned portable static policy checks. Not a tamper-proof external verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION = "1.0.2"
AGGREGATE_COMMAND_HASHES = {"62552449ecc0a32a1fdc5ca95a627af1e72cca49361e3f1a5d30a254a38d876c", "71526fe783280cab1cc7b671ebf5f9306f2d429707b1b3e282e7916dffb6473b"}

def check(root):
    errors = []
    try:
        import yaml
    except ImportError:
        return ["Install the pinned validation dependency: PyYAML==6.0.3"]
    try:
        cfg = json.loads((root / ".engineering/optimization.json").read_text())
        lock = json.loads((root / ".engineering/policy-lock.json").read_text())
    except (OSError, ValueError) as exc:
        return ["Missing or invalid policy configuration: " + type(exc).__name__]
    if not isinstance(cfg, dict) or not isinstance(lock, dict):
        return ["Policy configuration must be an object"]
    if not isinstance(lock.get("source_commit"), str):
        return ["Source commit must be a string"]
    if lock.get("version") != VERSION or not re.fullmatch(r"[0-9a-f]{40}", lock.get("source_commit", "")):
        errors.append("Invalid policy version or immutable source commit")
    expected = {".engineering/policy.md", ".engineering/check.py"}
    if set(lock.get("sha256", {})) != expected:
        errors.append("Policy lock must cover policy and checker exactly")
    for name, digest in lock.get("sha256", {}).items():
        if name not in expected:
            continue
        p = root / name
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != digest:
            errors.append("Pinned bytes differ: " + name)
    for name, token in [("AGENTS.md", ".engineering/policy.md"), ("CLAUDE.md", "@AGENTS.md")]:
        p = root / name
        if not p.is_file() or token not in p.read_text():
            errors.append("Missing instruction entrypoint: " + name)
    workflows = cfg.get("workflows")
    if not isinstance(workflows, dict) or not workflows:
        return errors + ["No enrolled workflow contracts"]
    for name, spec in workflows.items():
        p = root / name
        if not name.startswith(".github/workflows/") or ".." in Path(name).parts:
            errors.append("Invalid workflow path")
            continue
        try:
            data = yaml.load(p.read_text(), Loader=yaml.BaseLoader)
            if not isinstance(data, dict):
                raise ValueError()
            jobs = data.get("jobs", {})
            if not isinstance(jobs, dict) or not jobs:
                raise ValueError()
        except (OSError, ValueError, yaml.YAMLError):
            errors.append("Missing or invalid workflow: " + name)
            continue
        for job in spec.get("required_jobs", []):
            if job not in jobs:
                errors.append(name + ": missing required job " + job)
        for job, value in jobs.items():
            references = [value["uses"]] if "uses" in value else []
            references += [step["uses"] for step in value.get("steps", []) if "uses" in step]
            for ref in references:
                if not (ref.startswith("./") or re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref) or re.fullmatch(r"docker://.+@sha256:[0-9a-f]{64}", ref)):
                    errors.append(name + ": unpinned action " + ref)
            if "uses" in value:
                continue
            try:
                timeout = int(value.get("timeout-minutes", "0"))
                if not 1 <= timeout <= spec.get("max_timeout_minutes", 60):
                    raise ValueError()
            except (ValueError, TypeError):
                errors.append(name + ": unbounded timeout " + job)
        mode = spec.get("mode")
        cancel = data.get("concurrency", {}).get("cancel-in-progress")
        if mode == "validation":
            group = data.get("concurrency", {}).get("group", "")
            expressions = [x.strip() for x in re.findall(r"\$\{\{(.*?)\}\}", group)]
            if cancel != "true" or "github.workflow" not in expressions or not any(token in expressions for token in ("github.event.pull_request.number", "github.ref", "github.event.pull_request.number || github.ref")):
                errors.append(name + ": missing workflow/PR-scoped cancellation")
            events = data.get("on", {})
            if isinstance(events, str): events = {events: ""}
            if isinstance(events, list): events = {event: "" for event in events}
            if not isinstance(events, dict) or "pull_request" not in events or events.get("pull_request") not in ("", None, {}):
                errors.append(name + ": validation requires an unfiltered pull_request trigger")
        elif mode == "deployment":
            if cancel not in (None, "false"):
                errors.append(name + ": deployment cancellation is unsafe")
        else:
            errors.append(name + ": unknown workflow mode")
        for job in spec.get("required_jobs", []):
            value = jobs.get(job, {})
            if value.get("continue-on-error", "false") != "false":
                errors.append(name + ": required job is nonblocking " + job)
            if any(step.get("continue-on-error", "false") != "false" for step in value.get("steps", [])):
                errors.append(name + ": required job contains nonblocking step " + job)
        for job, commands in spec.get("required_commands", {}).items():
            job_spec = jobs.get(job, {})
            if job_spec.get("needs") and job_spec.get("if") not in ("always()", "${{ always() }}"):
                errors.append(name + ": dependent required command job must always run " + job)
            if job_spec.get("continue-on-error", "false") != "false" or ("if" in job_spec and job_spec["if"] not in ("always()", "${{ always() }}")):
                errors.append(name + ": required command job must be unconditional and blocking " + job)
            actual = [step.get("run") for step in job_spec.get("steps", [])
                      if "if" not in step and step.get("continue-on-error", "false") == "false"]
            if any(command not in actual for command in commands):
                errors.append(name + ": missing acceptance command " + job)
        aggregate = spec.get("aggregate")
        if aggregate:
            gate = jobs.get(aggregate, {})
            needs = gate.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            required = set(spec.get("required_jobs", [])) - {aggregate}
            if set(needs) != required or gate.get("if", "") not in ("always()", "${{ always() }}"):
                errors.append(name + ": aggregate must always depend on every required job")
            if not any(hashlib.sha256(step.get("run", "").encode()).hexdigest() in AGGREGATE_COMMAND_HASHES
                       and step.get("env", {}).get("RESULTS") == "${{ toJSON(needs) }}"
                       and "if" not in step and step.get("continue-on-error", "false") == "false"
                       for step in gate.get("steps", [])):
                errors.append(name + ": aggregate must use a reviewed blocking result validator")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        errors = check(args.root)
    except (TypeError, AttributeError, KeyError, ValueError, OSError):
        errors = ["Malformed policy or workflow structure"]
    print(json.dumps({"policy_version": VERSION, "static_policy": "FAIL" if errors else "PASS",
                      "errors": errors, "runtime_acceptance": "not_evaluated"}))
    return bool(errors)

if __name__ == "__main__":
    sys.exit(main())
