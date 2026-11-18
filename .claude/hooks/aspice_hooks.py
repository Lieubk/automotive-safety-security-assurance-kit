#!/usr/bin/env python3
"""Claude Code hooks of the toolkit: one script, one sub-command per event.

    session-start   context for a new session: scope, item counts, open findings
    pre-write       before Write or Edit: refuse changes to imported inputs, to
                    final records, and to items inside a baseline that no approved
                    change request names
    post-write      after Write or Edit: check the item that was just written and
                    hand structural findings and a stale approval back to the model
    pre-shell       before a shell command: inside an agent of this toolkit, refuse a
                    command its file does not allow; before `git commit`, run the
                    leak scan in a repository that holds confidential sources

The payload arrives as JSON on stdin (see the Claude Code hooks documentation).
A refusal is JSON on stdout with exit code 0; an advisory is JSON as well. Without
PyYAML the hooks cannot check anything: they say so instead of staying silent,
because a check that cannot report that it did not run is not a check.

Wired up in .claude/settings.json. Test: python -m unittest discover -s tools/tests
"""
import fnmatch
import io
import json
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
STRUCTURAL = ("FORMAT", "SCHEMA", "LINK")


def engine():
    """The trace engine module, or None when its dependency is missing."""
    try:
        import traceability
        return traceability
    except ImportError:
        return None


def not_assessed(event):
    return "NOT ASSESSED (%s hook): PyYAML is not installed, so the toolkit's checks did not run. " \
           "Install it with `python -m pip install pyyaml`." % event


def project_root(path):
    """Nearest folder at or above the file that holds a project.yaml, inside the repository."""
    for folder in [path] + list(path.parents):
        if (folder / "project.yaml").is_file():
            return folder
        if folder == ROOT:
            break
    return None


def item_at(project, path):
    path = path.resolve()
    return next((i for i in project.items.values() if i.path.resolve() == path), None)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


def content_after(payload, path):
    """The text the file would have after the tool call, or None when that cannot be told."""
    tool_input = payload.get("tool_input") or {}
    if payload.get("tool_name") == "Write":
        return tool_input.get("content")
    old, new = tool_input.get("old_string"), tool_input.get("new_string")
    if old is None or new is None:
        return None
    text = path.read_text(encoding="utf-8")
    return text.replace(old, new) if tool_input.get("replace_all") else text.replace(old, new, 1)


DISPOSITION = ("status", "superseded_by", "rejection_reason")     # how an item is disposed of, not what it says


def after(trace, payload, path):
    """(front matter, body) the file would have after the tool call, or (None, None)."""
    text = content_after(payload, path)
    match = trace.FRONT_MATTER.match(text.replace("\r\n", "\n")) if text is not None else None
    if not match:
        return None, None
    try:
        front = trace.yaml.safe_load(match.group(1)) or {}
    except trace.yaml.YAMLError:
        return None, None
    return (front, match.group(2)) if isinstance(front, dict) else (None, None)


def same_statement(trace, item, front, body, also=()):
    """True when only the disposition of the item changes, not what it says."""
    current = trace.FRONT_MATTER.match(item.path.read_text(encoding="utf-8").replace("\r\n", "\n"))
    if front is None or current is None:
        return False

    def statement(data):
        return {key: value for key, value in data.items() if key not in DISPOSITION and key not in also}

    return trace.content_hash(statement(front), body) == trace.content_hash(statement(item.front), current.group(2))


def pre_write(payload):
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        return 0
    path = Path(file_path)
    root = project_root(path.parent if path.parent.exists() else ROOT)
    if root is None or not path.is_file() or path.suffix != ".md":
        return 0                                      # not an existing item of a project
    trace = engine()
    if trace is None:
        return deny(not_assessed("pre-write") + " Edits to existing project items are refused until the checks can run.")
    project = trace.Project(root)
    item = item_at(project, path)
    if item is None:
        return 0
    front, body = after(trace, payload, path)
    retiring = (front or {}).get("status") in ("obsolete", "rejected") and item.status not in ("obsolete", "rejected")
    if front is not None and trace.content_hash(front, body) == item.hash and not retiring:
        return 0                                      # nothing that was reviewed changes
    if item.imported and project.reviews_of(item):
        # accepted through a review: from here on it changes only with its source
        new_version = isinstance((front or {}).get("imported"), dict) and \
            front["imported"].get("version") != (item.front.get("imported") or {}).get("version")
        # the links of an imported item are the project's own bookkeeping (for example which
        # requirements a delivered element fulfils), not part of what was delivered
        if not new_version and not same_statement(trace, item, front, body, also=("links",)):
            return deny("%s is an imported input that has been accepted, and is read-only. A problem with it is a "
                        "query to its source. A new version from the source is registered with /import-inputs, "
                        "which records the new `imported.version`." % item.id)
        # a new delivery may replace the content - but not inside a baseline without a change request (below)
    if project.types[item.type]["lifecycle"] == "record" and item.status == "final":
        return deny("%s is a final record and is never edited. Create a new record that supersedes it "
                    "(python tools/record.py ...)." % item.id)
    internal = (project.config.get("trace") or {}).get("internal_baselines") or []
    holding = [b.id for b in project.of_type("baseline") if b.status == "final" and b.front.get("purpose") not in internal
               and any(isinstance(e, dict) and e.get("item") == item.id and str(e.get("hash")) == item.hash
                       for e in trace.as_list(b.front.get("items")))]
    if holding and project.types[item.type]["lifecycle"] == "engineering" \
            and (retiring or not same_statement(trace, item, front, body)):
        permitted = [c.id for c in project.of_type("change-request")
                     if c.status in ("approved", "implemented") and (item.id, None) in c.targets("affects")]
        if not permitted:
            return deny("%s is part of baseline %s at its current content. Changing or retiring it needs an "
                        "approved change request that names it: run /change-request first."
                        % (item.id, ", ".join(holding)))
    return 0


def post_write(payload):
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        return 0
    path = Path(file_path)
    root = project_root(path.parent)
    if root is None or path.suffix != ".md":
        return 0
    trace = engine()
    if trace is None:
        print(json.dumps({"decision": "block", "reason": not_assessed("post-write")}))
        return 0
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return 0
    project = trace.Project(root)
    folders = (project.config.get("paths") or {}).get("items") or ["plans", "spec", "verification", "records"]
    if not any(relative.startswith(folder.rstrip("/") + "/") for folder in folders):
        return 0                                      # not in a folder that holds items
    item = item_at(project, path)
    key = item.id if item else relative
    lines = ["%s %s: %s" % (f["rule"], f["item"], f["message"]) for f in project.check()
             if f["item"] == key and f["level"] == "error" and f["rule"] in STRUCTURAL]
    notes = []
    if lines:
        notes.append("The item just written does not match the schema. Fix it now:\n  " + "\n  ".join(lines))
    if item is not None and item.status == "approved" and project.types[item.type]["lifecycle"] == "engineering" \
            and project.approving_review(item) is None:
        dependents = sum(len(v) for v in project.incoming[item.id].values())
        notes.append("%s has status approved, but no final review record covers its current content (hash %s). "
                     "An item is approved only through /review: set its status to draft first, then go on editing. "
                     "Tell the user that %d items link to it directly; python tools/traceability.py impact %s lists "
                     "everything that depends on it." % (item.id, item.hash, dependents, item.id))
    if notes:
        print(json.dumps({"decision": "block", "reason": "\n".join(notes)}))
    return 0


SHELL_OPERATORS = re.compile(r"[;&|`<>\n]|\$\(")


def agent_commands(agent_type):
    """The shell commands an agent of this toolkit may run, as patterns; None when it is not
    one of ours or allows the shell without restriction.

    Claude Code grants the whole Bash tool for an entry such as `Bash(python tools/x.py *)`
    in an agent's `tools`; the pattern is enforced here."""
    path = ROOT / ".claude" / "agents" / ("%s.md" % agent_type)
    if not agent_type or not re.match(r"^[\w-]+$", str(agent_type)) or not path.is_file():
        return None
    head = re.match(r"\A---\n(.*?)\n---", path.read_text(encoding="utf-8").replace("\r\n", "\n"), re.S)
    line = re.search(r"(?m)^tools:\s*(.+)$", head.group(1)) if head else None
    if not line:
        return None
    tools = [t.strip() for t in re.split(r",(?![^(]*\))", line.group(1))]
    if "Bash" in tools or "PowerShell" in tools:
        return None
    return [t[len("Bash("):-1] for t in tools if t.startswith("Bash(") and t.endswith(")")]


def pre_shell(payload):
    command = str((payload.get("tool_input") or {}).get("command") or "")
    allowed = agent_commands(payload.get("agent_type"))
    if allowed is not None:
        plain = command.strip()
        if SHELL_OPERATORS.search(plain) or not any(fnmatch.fnmatchcase(plain, p) for p in allowed):
            return deny("The agent %s may run only these commands, one at a time and without shell operators: "
                        "%s. Ask the caller for anything else." % (payload.get("agent_type"), "; ".join(allowed) or "none"))
    if not re.search(r"\bgit\b[^|;&]*\bcommit\b", command):
        return 0
    if not (ROOT / ".confidential").is_dir():
        return 0                                      # nothing confidential to protect in this repository
    try:
        import confidentiality_scan
    except ImportError:
        return deny("The leak scan could not be loaded, so nothing was checked before this commit.")
    captured, argv = io.StringIO(), sys.argv
    try:
        sys.argv = ["confidentiality_scan.py"]
        with redirect_stdout(captured):
            result = confidentiality_scan.main()
    finally:
        sys.argv = argv
    if result:
        lines = captured.getvalue().strip().splitlines()
        return deny("The leak scan found content that must not be committed:\n" + "\n".join(lines[:15])
                    + ("\n... %d more lines" % (len(lines) - 15) if len(lines) > 15 else ""))
    return 0


def session_start(payload):
    trace = engine()
    if trace is None:
        print(not_assessed("session-start"))
        return 0
    if not (ROOT / "project.yaml").is_file():
        print("Automotive SPICE toolkit: this repository has no project.yaml yet. /aspice-start sets up the scope "
              "(role, inputs received, processes the team is responsible for). A worked example is in "
              "examples/power-window: python tools/traceability.py --project examples/power-window check")
        return 0
    project = trace.Project(ROOT)
    findings = project.check()
    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]
    scope = ", ".join(sorted(project.scope)) if project.scope else "all processes (no scope set)"
    active = sum(1 for rule in project.rules if project.active(rule))
    print("Automotive SPICE toolkit. Scope: %s. %d items, %d of %d coverage rules active, %d errors, %d warnings."
          % (scope, len(project.items), active, len(project.rules), len(errors), len(warnings)))
    for finding in errors[:8]:
        print("  %s %s: %s" % (finding["rule"], finding["item"], finding["message"]))
    if len(errors) > 8:
        print("  ... %d more errors: python tools/traceability.py check" % (len(errors) - 8))
    print("Rules of work: .claude/docs/working-agreement.md. /next-step says what to do next.")
    return 0


EVENTS = {"session-start": session_start, "pre-write": pre_write, "post-write": post_write, "pre-shell": pre_shell}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in EVENTS:
        print("usage: aspice_hooks.py %s" % " | ".join(EVENTS), file=sys.stderr)
        return 1
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    return EVENTS[sys.argv[1]](payload)


if __name__ == "__main__":
    sys.exit(main())
