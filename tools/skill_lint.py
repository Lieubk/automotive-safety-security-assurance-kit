#!/usr/bin/env python3
"""Mechanical checks of the skills, agents, rules and checklists under .claude/.

What a script can verify about a skill: that it has the agreed shape, that every
identifier it mentions exists (base practices and coverage rules in the catalog
and the schema, item types and link roles in the schema, tool commands, other
skills, referenced files), and that the reviewing agent cannot write. What a
skill says, and whether it is right, is for a reader to judge.

The set of files is derived from what the folders contain, so a new skill cannot
stay outside the check by not being on a list.

Usage:
    python tools/skill_lint.py

Requires PyYAML. Exit code 0 = no errors, 1 = errors.
"""
import difflib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / ".claude"
FRONT = re.compile(r"\A---\n(.*?)\n---[ \t]*\n", re.S)
SECTIONS = ["Before you start", "Steps", "Writing", "Checks before you finish", "Hand-over", "Do not"]
KINDS = {"script", "semantic", "accountable"}
MODELS = {"opus", "sonnet", "haiku", "fable", "inherit"}      # aliases only: a published toolkit pins no version
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
BUILT_IN_AGENTS = {"general-purpose", "Explore", "Plan"}
MAX_LINES = 200
TRACE_COMMANDS = {"check", "matrix", "show", "impact", "hash", "status", "list", "audit", "practices", "diff",
                  "progress", "problems", "history", "quality", "generic"}
RECORD_COMMANDS = {"next-id", "test-run", "analysis-run", "review", "baseline", "communication", "status-report", "build",
                   "problem-trends", "quality-check", "quality-report", "self-assessment"}


def front_matter(path, errors):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = FRONT.match(text)
    if not match:
        errors.append("%s: no YAML front matter" % rel(path))
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        errors.append("%s: front matter is not valid YAML (%s)" % (rel(path), str(exc).split("\n")[0]))
        data = {}
    return data, text[match.end():]


def rel(path):
    return path.relative_to(ROOT).as_posix()


def vocabulary():
    """Identifiers that exist: base practices, coverage rules, item types, link roles."""
    practices = set()
    for f in (ROOT / "aspice").rglob("processes/*.yaml"):
        practices |= {bp["id"] for bp in yaml.safe_load(f.read_text(encoding="utf-8"))["base_practices"]}
    schema = yaml.safe_load((ROOT / "schema" / "items.yaml").read_text(encoding="utf-8"))
    return {
        "practices": practices,
        "rules": {r["id"] for r in schema["coverage"]},
        "types": set(schema["types"]),
        "roles": set(schema["links"]),
        # terms that resemble type names without being typos of them
        "other": set(schema["plan_kinds"]) | set(schema["structures"]) | set(schema["lifecycles"])
                 | {state for lc in schema["lifecycles"].values() for state in lc["states"]}
                 | {name for spec in schema["types"].values() for name in spec.get("attributes", {}) if name != "use"}
                 | {name for group in schema["attribute_sets"].values() for name in group}
                 | {str(value) for spec in schema["types"].values() for attr in spec.get("attributes", {}).values()
                    if isinstance(attr, dict) for value in attr.get("values", [])},
    }


def check_references(path, text, vocab, skills, errors, warnings):
    name = rel(path)
    for ref in sorted(set(re.findall(r"\b[A-Z]{3}\.\d+\.BP\d+\b", text))):
        if ref not in vocab["practices"]:
            errors.append("%s: base practice %s is not in the catalog" % (name, ref))
    for ref in sorted(set(re.findall(r"\bCOV-\d+\b", text))):
        if ref not in vocab["rules"]:
            errors.append("%s: coverage rule %s is not in the schema" % (name, ref))
    known = vocab["types"] | vocab["roles"]
    for token in sorted(set(re.findall(r"`([a-z][a-z_-]{5,})`", text))):
        if token in known or token in vocab["other"]:
            continue
        close = difflib.get_close_matches(token, known, n=1, cutoff=0.88)
        if close:
            warnings.append("%s: `%s` looks like the schema term `%s` but is not it" % (name, token, close[0]))
    for tool, command in re.findall(r"python tools[\\/](\w+)\.py(?:\s+--project\s+\S+)?\s+([a-z][a-z-]+)", text):
        if not (ROOT / "tools" / (tool + ".py")).is_file():
            errors.append("%s: tools/%s.py does not exist" % (name, tool))
        elif tool == "traceability" and command not in TRACE_COMMANDS:
            errors.append("%s: traceability.py has no command '%s'" % (name, command))
        elif tool == "record" and command not in RECORD_COMMANDS:
            errors.append("%s: record.py has no command '%s'" % (name, command))
    for skill in sorted(set(re.findall(r"(?<![\w/.])/([a-z][a-z-]{3,})\b(?![/.\w])", text))):
        if skill in CANDIDATE_SKILL_NAMES and skill not in skills:
            errors.append("%s: /%s is not a skill of this toolkit" % (name, skill))
    for target in sorted(set(re.findall(r"\.claude/docs/checklists/[\w-]+\.md", text.replace("\\", "/")))):
        if not (ROOT / target).is_file():
            errors.append("%s: %s does not exist" % (name, target))


# Words that follow a slash in prose and are meant as skill names; anything else after a
# slash (paths, "and/or") is ignored. Extended automatically with the skills that exist.
CANDIDATE_SKILL_NAMES = {
    "aspice-start", "import-inputs", "next-step", "sw-requirements", "sw-architecture", "sw-detailed-design",
    "sw-unit-implement", "sw-unit-verify", "review", "trace-check", "process-gate", "baseline", "change-request",
    "project-plan", "work-breakdown", "project-status",
}


def lint_skill(folder, vocab, skills, errors, warnings):
    path = folder / "SKILL.md"
    if not path.is_file():
        errors.append("%s: no SKILL.md" % rel(folder))
        return
    front, body = front_matter(path, errors)
    name = rel(path)
    if front.get("name") != folder.name:
        errors.append("%s: name '%s' does not equal the folder name" % (name, front.get("name")))
    if len(str(front.get("description") or "")) < 40:
        errors.append("%s: description is missing or too short to tell when to use the skill" % name)
    tools = str(front.get("allowed-tools") or "")
    if not tools:
        errors.append("%s: no allowed-tools" % name)
    forked = front.get("context") == "fork"
    if "context" in front and not forked:
        errors.append("%s: context '%s' is not a value Claude Code knows; only 'fork'" % (name, front.get("context")))
    for key in ("model", "effort"):
        if key in front and not forked:
            errors.append("%s: %s on a skill that runs in the conversation switches the session's %s for the turn, "
                          "and the conversation is read again without cache; leave it out, or run the skill with "
                          "context: fork" % (name, key, key))
    check_model(name, front, errors)
    if forked:
        if "AskUserQuestion" in tools:
            errors.append("%s: a forked skill cannot hold a conversation with the user; drop AskUserQuestion or the fork" % name)
        agent = front.get("agent")
        if agent and agent not in BUILT_IN_AGENTS and not (CLAUDE / "agents" / ("%s.md" % agent)).is_file():
            errors.append("%s: agent '%s' is neither built in nor defined in .claude/agents" % (name, agent))
    lines = body.count("\n") + 1
    if lines > MAX_LINES:
        errors.append("%s: %d lines; move detail to references/ (limit %d)" % (name, lines, MAX_LINES))
    headings = re.findall(r"^## (.+?)\s*$", body, re.M)
    wanted = [s for s in SECTIONS if s != "Writing" or re.search(r"\b(Write|Edit)\b", tools)]
    position = -1
    for section in wanted:
        if section not in headings:
            errors.append("%s: section '## %s' is missing" % (name, section))
        elif headings.index(section) < position:
            errors.append("%s: section '## %s' is out of order" % (name, section))
        else:
            position = headings.index(section)
    if not re.search(r"^\|\s*Base practice\s*\|", body, re.M) and re.search(r"\b[A-Z]{3}\.\d+\.BP\d+\b", body):
        warnings.append("%s: mentions base practices but has no 'Base practice' table" % name)
    for target in sorted(set(re.findall(r"references/([\w.-]+\.md)", body))):
        if not (folder / "references" / target).is_file():
            errors.append("%s: references/%s does not exist" % (name, target))
    for extra in sorted((folder / "references").glob("*.md")) if (folder / "references").is_dir() else []:
        if extra.name not in body:
            warnings.append("%s: references/%s is never mentioned in SKILL.md" % (name, extra.name))
    texts = [path] + sorted(folder.rglob("references/*.md"))
    for file in texts:
        check_references(file, file.read_text(encoding="utf-8"), vocab, skills, errors, warnings)


def check_model(name, front, errors):
    if "model" in front and str(front["model"]) not in MODELS:
        errors.append("%s: model '%s' is not one of %s" % (name, front["model"], ", ".join(sorted(MODELS))))
    if "effort" in front and str(front["effort"]) not in EFFORTS:
        errors.append("%s: effort '%s' is not one of %s" % (name, front["effort"], ", ".join(sorted(EFFORTS))))


def lint_agent(path, vocab, skills, errors, warnings):
    front, body = front_matter(path, errors)
    name = rel(path)
    if front.get("name") != path.stem:
        errors.append("%s: name '%s' does not equal the file name" % (name, front.get("name")))
    if len(str(front.get("description") or "")) < 40:
        errors.append("%s: description is missing or too short" % name)
    tools = str(front.get("tools") or "")
    if not tools:
        errors.append("%s: no tools listed" % name)
    for key in ("model", "effort"):
        if key not in front:
            errors.append("%s: no %s; every agent states the %s its work needs (skill-authoring.md, Model and effort)"
                          % (name, key, key))
    check_model(name, front, errors)
    if "review" in path.stem and re.search(r"\b(Write|Edit|NotebookEdit)\b", tools):
        errors.append("%s: a reviewing agent must not have write tools" % name)
    if "working-agreement" not in body:
        warnings.append("%s: does not refer to the working agreement" % name)
    check_references(path, body, vocab, skills, errors, warnings)


def lint_checklist(path, vocab, skills, errors, warnings):
    text = path.read_text(encoding="utf-8")
    name = rel(path)
    if not re.search(r"^Version \d+", text, re.M):
        errors.append("%s: no 'Version <n>' line" % name)
    rows = [line for line in text.splitlines() if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line)]
    checks = 0
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if cells and cells[0] == "ID":
            if cells[-1] != "Kind":
                errors.append("%s: table header must end with the column 'Kind'" % name)
            continue
        checks += 1
        kind = cells[-1] if cells else ""
        if kind not in KINDS:
            errors.append("%s: check %s has kind '%s'; one of %s" % (name, cells[0] if cells else "?", kind, sorted(KINDS)))
        elif kind == "script" and not re.search(r"`|COV-\d+|SCHEMA|FORMAT|LINK|SUSPECT|CONSISTENCY", row):
            errors.append("%s: check %s is marked script but names no rule or command" % (name, cells[0]))
    if not checks:
        errors.append("%s: no checks found" % name)
    check_references(path, text, vocab, skills, errors, warnings)


def main():
    vocab = vocabulary()
    errors, warnings = [], []
    skill_folders = sorted(p for p in (CLAUDE / "skills").iterdir() if p.is_dir()) if (CLAUDE / "skills").is_dir() else []
    skills = {p.name for p in skill_folders}
    CANDIDATE_SKILL_NAMES.update(skills)
    for folder in skill_folders:
        lint_skill(folder, vocab, skills, errors, warnings)
    agents = sorted((CLAUDE / "agents").glob("*.md")) if (CLAUDE / "agents").is_dir() else []
    for path in agents:
        lint_agent(path, vocab, skills, errors, warnings)
    checklists = sorted((CLAUDE / "docs" / "checklists").glob("*.md")) if (CLAUDE / "docs" / "checklists").is_dir() else []
    for path in checklists:
        lint_checklist(path, vocab, skills, errors, warnings)
    others = sorted((CLAUDE / "docs").glob("*.md")) + sorted((CLAUDE / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"]
    for path in others:
        if path.is_file():
            check_references(path, path.read_text(encoding="utf-8"), vocab, skills, errors, warnings)
    for line in warnings:
        print("warning: " + line)
    for line in errors:
        print("error: " + line)
    print("%d skills, %d agents, %d checklists | %d errors, %d warnings"
          % (len(skill_folders), len(agents), len(checklists), len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
