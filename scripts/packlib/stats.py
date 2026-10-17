# SPDX-License-Identifier: Apache-2.0
"""Estimate the token cost of each generated output from the files on disk, at about four characters per token.

"Always loaded" is the text a host keeps in every conversation once the output is installed: skill and agent
descriptions (skills marked disable-model-invocation are left out), or a whole pasted pack. "On demand" is the text
read only when a skill, agent or card is used. It reads files rather than build outputs, so it can also measure an
older checkout for a before-and-after comparison.
"""
import json
from pathlib import Path
import re

FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
TOML_DESCRIPTION = re.compile(r'^description = (".*")$', re.M)


def tokens(chars):
    return (chars + 3) // 4


def _field(front, key):
    match = re.search(rf"^{key}: (.*)$", front, re.M)
    if not match:
        return ""
    value = match.group(1).strip()
    return json.loads(value) if value.startswith('"') else value.strip("'")


def measure(path):
    """(always-loaded chars, on-demand chars, preamble chars or None) for one skill, agent or pack file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".toml":
        match = TOML_DESCRIPTION.search(text)
        return (len(json.loads(match.group(1))) if match else 0), len(text), None
    match = FRONT.match(text)
    if not match:
        return len(text), 0, None
    front, body = match.group(1), text[match.end():]
    hidden = _field(front, "disable-model-invocation") == "true"
    preamble = None
    if "/agents/" in path.as_posix() and not path.stem.endswith("-orchestrator") and "\n---\n\n# " in body:
        preamble = len(re.sub(r"<!--.*?-->", "", body.split("\n---\n\n# ", 1)[0], flags=re.S).strip())
    return (0 if hidden else len(_field(front, "description"))), len(body), preamble


def _row(name, paths):
    loaded = demand = largest = 0
    preambles = []
    for path in paths:
        always, body, preamble = measure(path)
        loaded += always
        demand += body
        largest = max(largest, body)
        if preamble is not None:
            preambles.append(preamble)
    average = sum(preambles) // len(preambles) if preambles else 0
    return {"output": name, "files": len(paths), "always": tokens(loaded), "demand": tokens(demand),
            "largest": tokens(largest), "preamble": average}


def _components(folder):
    return sorted(folder.glob("skills/*/SKILL.md")) + sorted(folder.glob("agents/*.md"))


def rows(root):
    root = Path(root)
    found = []
    plugins = sorted(path for path in (root / "plugins").glob("*") if (path / ".claude-plugin").is_dir())
    every = []
    for folder in plugins:
        parts = _components(folder)
        every += parts
        found.append(_row(f"plugin {folder.name}", parts))
    if plugins:
        found.append(_row("all family plugins together", every))
    market = root / ".claude-plugin" / "marketplace.json"
    if market.is_file():
        for entry in json.loads(market.read_text(encoding="utf-8")).get("plugins", []):
            if entry.get("source") in ("./", "."):
                paths = [root / skill[2:] / "SKILL.md" for skill in entry.get("skills", [])]
                paths += [root / agent[2:] for agent in entry.get("agents", [])]
                found.append(_row(f"bundle {entry['name']}", paths))
    if (root / "skills").is_dir():
        found.append(_row("skills/ (npx skills, Gemini)", sorted((root / "skills").glob("*/SKILL.md"))))
    codex = root / "adapters" / "codex"
    if codex.is_dir():
        found.append(_row("Codex plugin skills", sorted(codex.glob("skills/*/SKILL.md"))))
        found.append(_row("Codex agents", sorted(codex.glob("agents/*.toml"))))
    copilot = root / "adapters" / "copilot" / "agents"
    if copilot.is_dir():
        found.append(_row("Copilot agents", sorted(copilot.glob("*.agent.md"))))
    for pack in sorted((root / "dist" / "packs").glob("*.md")):
        found.append(_row(f"paste {pack.stem}", [pack]))
    return found


def table(found):
    lines = ["| Output | Files | Always loaded (tokens) | On demand (tokens) | Largest file (tokens) | Agent preamble (chars) |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in found:
        preamble = str(row["preamble"]) if row["preamble"] else "-"
        lines.append(f"| {row['output']} | {row['files']} | {row['always']:,} | {row['demand']:,} | {row['largest']:,} | {preamble} |")
    return "\n".join(lines)
