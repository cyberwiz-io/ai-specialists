#!/usr/bin/env python3
"""Pinned portable static policy checks. Not a tamper-proof external verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION = "1.0.0"

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
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
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
            if cancel != "true" or "github.workflow" not in data.get("concurrency", {}).get("group", ""):
                errors.append(name + ": missing workflow-scoped cancellation")
        elif mode == "deployment":
            if cancel not in (None, "false"):
                errors.append(name + ": deployment cancellation is unsafe")
        else:
            errors.append(name + ": unknown workflow mode")
        for job, commands in spec.get("required_commands", {}).items():
            job_spec = jobs.get(job, {})
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
            if set(needs) != required or "always()" not in gate.get("if", ""):
                errors.append(name + ": aggregate must always depend on every required job")
            if not any("toJSON(needs)" in str(step.get("env", {})) for step in gate.get("steps", [])):
                errors.append(name + ": aggregate must inspect dependency results")
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
