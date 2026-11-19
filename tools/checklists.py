#!/usr/bin/env python3
"""Review checklists: those of the toolkit and those of a project.

The toolkit's checklists are under .claude/docs/checklists. A project may keep
checklists of its own under `checklists/` in its root, in the same format
(.claude/skills/review/references/project-checklists.md). A project checklist

- applies to types for which the toolkit has no checklist (no relation line),
- extends a toolkit checklist (`Extends: <name> v<N>`): a review that cites it
  applies the checks of both, or
- replaces one (`Replaces: <name> v<N>`): a review applies the project's alone.

A toolkit checklist that the project extends or replaces can no longer be cited
on its own in that project. The version a project checklist names must be the
toolkit checklist's present version, so that a new version of the toolkit's is
looked at before the next review relies on it.

Imported by record.py (citations, check templates, the `checklists` command)
and by traceability.py (the CHECKLIST findings of `check`).
"""

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLKIT = ROOT / ".claude" / "docs" / "checklists"
PROJECT_FOLDER = "checklists"
KINDS = ("script", "semantic", "accountable")
ROW = re.compile(r"^\|\s*([A-Z]{2,5}-\d+)\s*\|")


def plain(text):
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def file_hash(path):
    """Hash of a file, independent of line-ending style (the same as traceability.file_hash)."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]


def parse(path, source, root):
    """One checklist file as a dict; `problems` lists what is wrong with its format."""
    text = path.read_text(encoding="utf-8")
    head = re.split(r"(?m)^## ", text, maxsplit=1)[0]
    title = re.search(r"^#\s+(.+)$", text, re.M)
    version = re.search(r"^Version (\d+)", text, re.M)
    applies = re.search(r"Applies to:(.*?)(?=\bSupports:|\bExtends:|\bReplaces:|\n\s*\n|$)", head, re.S)
    relation = re.findall(r"\b(Extends|Replaces):\s*`?([A-Za-z0-9][A-Za-z0-9 _-]*?)\s+v(\d+)`?(?=[\s.,;]|$)", head)
    problems = []
    if not version:
        problems.append("no 'Version <n>' line")
    if not applies:
        problems.append("no 'Applies to:' sentence before the first section")
    if len(relation) > 1:
        problems.append("names more than one checklist under Extends or Replaces; one at most")
    checks, sections, kinds, heading, kind, header = {}, {}, {}, None, None, False
    for line in text.splitlines():
        if line.startswith("## "):
            heading = plain(line[3:])
            named = re.match(r"^## Kind (\S+)", line)          # a part that applies to one kind of plan only
            kind = named.group(1) if named else None
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if cells and cells[0] == "ID":
            header = True
            if cells[-1] != "Kind":
                problems.append("table header must end with the column 'Kind'")
            continue
        found = ROW.match(line)
        if not found:
            continue
        check = found.group(1)
        if check in checks:
            problems.append("check ID %s is used twice" % check)
        if cells[-1] not in KINDS:
            problems.append("check %s has kind '%s'; one of %s" % (check, cells[-1], ", ".join(KINDS)))
        checks[check] = cells[-1]
        if heading:
            sections.setdefault(heading, []).append(check)
            if kind:
                kinds.setdefault(kind, []).append(check)
    if not checks:
        problems.append("no checks found: rows '| <ID> | <check> | <how to check> | <kind> |' with IDs like ABC-01"
                        if not header else "no check rows under the table header")
    names = {plain(path.stem)}
    if title:
        names.add(plain(re.sub(r"(?i)\bchecklist\b", " ", title.group(1))))
    return {
        "file": path.name,
        "path": path.relative_to(root).as_posix() if root in path.parents else path.as_posix(),
        "source": source,
        "name": path.stem,
        "names": names,
        "title": title.group(1).strip() if title else path.stem,
        "version": version.group(1) if version else None,
        "applies": " ".join((applies.group(1) if applies else "").split()).rstrip("."),
        "applies_tokens": re.findall(r"`([^`]+)`", applies.group(1)) if applies else [],
        "relation": relation[0][0].lower() if len(relation) == 1 else None,
        "base_name": relation[0][1] if len(relation) == 1 else None,
        "base_version": relation[0][2] if len(relation) == 1 else None,
        "checks": checks,
        "sections": sections,
        "kinds": kinds,
        "hash": file_hash(path),
        "problems": problems,
    }


def citation(entry):
    return "%s v%s" % (entry["name"], entry["version"] or "?")


class Catalog:
    """The toolkit's checklists and the project's, with the relations between them."""

    def __init__(self, project_root=None):
        self.project_root = Path(project_root).resolve() if project_root else None
        self.toolkit = [parse(p, "toolkit", ROOT) for p in sorted(TOOLKIT.glob("*.md"))]
        folder = self.project_root / PROJECT_FOLDER if self.project_root else None
        self.project = [parse(p, "project", self.project_root) for p in sorted(folder.glob("*.md"))] \
            if folder and folder.is_dir() else []
        self.overridden = {}                             # toolkit file name -> project entry that extends or replaces it
        for entry in self.project:
            entry["base"] = None
            for other in self.toolkit:
                if entry["names"] & other["names"]:
                    entry["problems"].append("has the name of the toolkit checklist %s; give it a name of its own"
                                             % other["file"])
            for other in self.project:
                if other is not entry and entry["names"] & other["names"]:
                    entry["problems"].append("has the same name as %s" % other["path"])
            if not entry["relation"]:
                continue
            base = self.find_toolkit(entry["base_name"])
            word = entry["relation"].capitalize()
            if base is None:
                entry["problems"].append("%s: %s v%s is no checklist of the toolkit (.claude/docs/checklists)"
                                         % (word, entry["base_name"], entry["base_version"]))
                continue
            entry["base"] = base
            if base["version"] != entry["base_version"]:
                entry["problems"].append(
                    "%s %s v%s, but the toolkit's %s is at version %s: compare the two versions, decide whether the "
                    "project's checks still hold, then change the line to v%s and raise the version of this file "
                    "if a check of it changed" % (word.lower(), base["name"], entry["base_version"], base["file"],
                                                  base["version"], base["version"]))
            if entry["relation"] == "extends":
                clash = sorted(set(entry["checks"]) & set(base["checks"]))
                if clash:
                    entry["problems"].append("check IDs %s are also IDs of %s: use IDs of the project's own"
                                             % (", ".join(clash), base["file"]))
            earlier = self.overridden.get(base["file"])
            if earlier:
                entry["problems"].append("%s is already extended or replaced by %s; one project checklist per "
                                         "toolkit checklist" % (base["file"], earlier["path"]))
            else:
                self.overridden[base["file"]] = entry

    def find_toolkit(self, name):
        wanted = plain(name)
        return next((e for e in self.toolkit if wanted in e["names"]), None)

    def problems(self):
        """(path, message) for every problem of a project checklist."""
        return [(e["path"], m) for e in self.project for m in e["problems"]]

    def effective(self, entry):
        """What a review that cites `entry` applies: for an extension, the base's checks followed by its own."""
        result = dict(entry)
        base = entry.get("base")
        if entry.get("relation") == "extends" and base:
            result["checks"] = {**base["checks"], **entry["checks"]}
            result["sections"] = {k: list(v) for k, v in base["sections"].items()}
            for heading, ids in entry["sections"].items():
                result["sections"].setdefault(heading, []).extend(ids)
            result["kinds"] = {k: list(v) for k, v in base["kinds"].items()}
            for kind, ids in entry["kinds"].items():
                result["kinds"].setdefault(kind, []).extend(ids)
        return result

    def resolve(self, cited):
        """The checklist a citation '<name> v<N>' names, ready to apply, and the problems that forbid citing it.

        Returns (entry or None, problems). entry carries `cited` (the version in the citation), `checks`,
        `sections` and `kinds` as a review applies them, and `base` for a project checklist with a relation.
        """
        match = re.match(r"^(.*?)\s+v(\d+)$", str(cited or "").strip(), re.I)
        if not match:
            return None, []
        wanted = plain(match.group(1))
        found = [e for e in self.project + self.toolkit if wanted in e["names"]]
        if not found:
            return None, []
        entry = found[0]
        problems = []
        if len(found) > 1:
            problems.append("'%s' names more than one checklist: %s" % (cited, ", ".join(e["path"] for e in found)))
        if entry["source"] == "toolkit" and entry["file"] in self.overridden:
            own = self.overridden[entry["file"]]
            problems.append("this project %s %s with its own checklist %s: cite '%s'"
                            % ("extends" if own["relation"] == "extends" else "replaces", entry["file"], own["path"],
                               citation(own)))
        if entry["source"] == "project" and entry["problems"]:
            problems += ["%s: %s" % (entry["path"], m) for m in entry["problems"]]
        result = self.effective(entry)
        result["cited"] = match.group(2)
        return result, problems

    def for_type(self, type_name):
        """The checklists to cite for an item type (or for `imported`): a toolkit checklist the project neither
        extends nor replaces, a project checklist that extends or replaces one that names the type, or a project
        checklist that names it."""
        names = []
        for entry in self.toolkit:
            if type_name in entry["applies_tokens"]:
                names.append(self.overridden.get(entry["file"], entry))
        for entry in self.project:
            if type_name in entry["applies_tokens"] and entry not in names:
                names.append(entry)
        return names
