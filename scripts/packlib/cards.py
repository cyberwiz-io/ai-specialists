# SPDX-License-Identifier: Apache-2.0
"""Parse role cards and enforce the card rules in docs/CARD-GUIDE.md."""
import re

from .config import CARD_MAX

LABELS = ("Use for", "Inputs", "Method", "Deliver", "Acceptance", "Safeguards", "Handoff")
REQUIRED = tuple(label for label in LABELS if label != "Safeguards")
HEADER = re.compile(r"ID: ([a-z0-9-]+/[a-z0-9-]+)\. Version: ([0-9]+\.[0-9]+)\.")
LABEL = re.compile(r"\*\*([A-Za-z ]+):\*\*")
ID_REFERENCE = re.compile(r"`([a-z0-9-]+/[a-z0-9-]+)`")

# These words may only appear in a paragraph that also rules them out.
TRIGGERS = re.compile(
    r"\b(publish\w*|deploy\w*|credentials?|passwords?|tokens?|api keys?|connect\w*|install\w*|"
    r"upload\w*|log in|execute[sd]?|executing|exploit|exploits|payloads?|malware|"
    r"evade[sd]?|evading|evasion|certified|certification|certify|guarantee\w*|compliant)\b", re.I)
NEGATION = re.compile(r"\b(not|never|no|without|cannot|unless|outside|nothing)\b|n't\b", re.I)
# Named laws, standards and frameworks would imply a crosswalk the pack does not have.
STANDARDS = re.compile(
    r"\b(ISO[ -]?\d+|NIST|OWASP|MITRE|ATT&CK|SOC ?2|HIPAA|GDPR|CCPA|PCI[ -]?DSS|SOX|FERPA|COPPA|"
    r"CIS Controls|GAAP|IFRS|WCAG|FCRA|EEOC|FLSA|Title VII)\b")
SAFEGUARD_TERMS = ("source", "uncertain", "authoriz", "escalat")


def parse(text):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    result = {"name": "", "id": "", "version": "", "paragraphs": {}, "order": [], "raw": paragraphs}
    if paragraphs and paragraphs[0].startswith("# "):
        result["name"] = paragraphs[0][2:].strip()
    if len(paragraphs) > 1:
        match = HEADER.fullmatch(paragraphs[1])
        if match:
            result["id"], result["version"] = match.groups()
    for paragraph in paragraphs[2:]:
        match = LABEL.match(paragraph)
        if match:
            result["order"].append(match.group(1))
            result["paragraphs"][match.group(1)] = paragraph[match.end():].strip()
    return result


def use_for(text):
    """First sentence of the Use for paragraph, for registries and indexes."""
    body = parse(text)["paragraphs"].get("Use for", "")
    cut = body.find(". ")
    sentence = (body if cut < 0 else body[:cut + 1]).rstrip()
    sentence = sentence if sentence.endswith(".") else sentence + "."
    return sentence[:1].upper() + sentence[1:]


LIST_CUT = re.compile(r": |; ")
CLAUSE_CUT = re.compile(r", such as | such as |, including |, so | so | before |, from | from |, meaning |, and |, or | \(")
BRIEF_SAFE, BRIEF_MAX = 80, 100


def brief(text):
    """The Use for sentence cut at a clause that still reads whole, for descriptions loaded into every conversation."""
    sentence = use_for(text).rstrip(".")
    if len(sentence) <= BRIEF_SAFE:
        return sentence + "."
    for limit, pattern in ((BRIEF_MAX, LIST_CUT), (BRIEF_SAFE, CLAUSE_CUT), (BRIEF_MAX, re.compile(", "))):
        cuts = [m.start() for m in pattern.finditer(sentence) if 30 <= m.start() <= limit]
        if cuts:
            return sentence[:cuts[-1]] + "."
    return sentence + "."


def check(role, text, version, known_ids):
    """Return a list of failure strings for one card."""
    name, failures = role["path"], []
    card = parse(text)
    if len(text.encode("utf-8")) > CARD_MAX:
        failures.append(f"{name}: card exceeds {CARD_MAX} bytes")
    if card["name"] != role["name"]:
        failures.append(f"{name}: title must be '# {role['name']}'")
    if card["id"] != role["id"]:
        failures.append(f"{name}: header must read 'ID: {role['id']}. Version: {version}.'")
    elif card["version"] != version:
        failures.append(f"{name}: expected one Version {version}")
    wanted = [label for label in REQUIRED]
    if role["sensitive"] or "Safeguards" in card["order"]:
        wanted.insert(wanted.index("Handoff"), "Safeguards")
    for label in wanted:
        if label not in card["order"]:
            failures.append(f"{name}: missing {label}")
    present = [label for label in card["order"] if label in wanted]
    if all(label in card["order"] for label in wanted) and present != wanted:
        failures.append(f"{name}: labels must appear in the order {', '.join(wanted)}")
    for paragraph in card["raw"][2:]:
        if len(LABEL.findall(paragraph)) > 1:
            failures.append(f"{name}: a paragraph holds more than one label ('{paragraph[:24]}...'); put each on its own paragraph")
    if "Coordinator boundaries apply" not in card["paragraphs"].get("Handoff", ""):
        failures.append(f"{name}: Handoff must state that all Coordinator boundaries apply")
    if "Safeguards" in card["paragraphs"]:
        body = card["paragraphs"]["Safeguards"].lower()
        for term in SAFEGUARD_TERMS:
            if term not in body:
                failures.append(f"{name}: Safeguards must address '{term}'")
        if not re.search(r"\bnot\b[^.]*\badvice\b", body):
            failures.append(f"{name}: Safeguards must say the output is not advice")
    for paragraph in card["raw"][2:]:
        for match in TRIGGERS.finditer(paragraph):
            if not NEGATION.search(paragraph):
                failures.append(f"{name}: '{match.group(0)}' appears without ruling it out")
                break
    for match in STANDARDS.finditer(text):
        failures.append(f"{name}: names a standard or regulation ('{match.group(0)}')")
        break
    for reference in sorted(set(ID_REFERENCE.findall(text))):
        if reference not in known_ids:
            failures.append(f"{name}: handoff references unknown role {reference}")
    return failures
