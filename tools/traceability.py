#!/usr/bin/env python3
"""Trace engine: load item files, check them against the schema, report traceability.

Everything here is deterministic. The engine reports observations (a link is
missing, an approval is stale, a file has no owner); whether a project may move
on is decided by people and by the gate checks that read these observations.

Commands
    check              validate every item and evaluate the coverage rules in scope
    matrix             traceability tables for the link pairs in scope
    show ID            one item with what it links to and what links to it
    impact ID          everything that depends on an item, directly or indirectly
    hash [ID ...]      content hashes; with --upstream a ready-to-paste block of
                       subject and references entries for a review record
    status             items per type and state, the latest verification runs and
                       the latest build of each integration step
    list               IDs with state and title; --type, --status and --imported narrow it
    audit ID           compare a baseline record with the items as they are now
    progress           work packages, milestones and corrective actions against the
                       plan as of a date (--as-of; default today); --json
    problems           problem reports with state, severity, origin, detection and age
                       as of a date (--as-of; default today), and the figures; --json
    history ID         the states an item had in the commits that changed it, from git
    risks              the risks by exposure, with treatment actions overdue and indicators
                       at their threshold (--as-of; default today); --json
    suppliers          per supplier agreement: meetings held against the agreed rhythm,
                       exchanges recorded, open items and corrective actions
                       (--as-of; default today); --json
    quality            the checks of the quality assurance plan and their records, the
                       findings with the state of their actions, lateness and the
                       escalations due as of a date (--as-of; default today); --json
    diff ID            what changed in an item since a review saw it, as subject or as
                       reference (--since REV-ID; default: the newest), from git
    generic [PROC]     per generic practice of level 2 and process in scope: what the
                       repository holds for it (work packages, status reports,
                       actions, communication, baselines, reviews); --json
    practices [PROC]   per base practice of the processes in scope (or of one
                       process): the evidence the project holds and the findings
                       still open. The deterministic input of a process gate

Options
    --project DIR      project root (default: current directory)
    --all              `check`: also list findings on items still in draft
    --json             `check`: findings as JSON

File layout and hash definition: schema/item-format.md. Rules: schema/items.yaml.
Requires PyYAML. Exit code of `check`: 0 = no errors, 1 = errors.
"""
import argparse
import datetime
import difflib
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ASIL_ORDER = {"QM": 0, "A": 1, "B": 2, "C": 3, "D": 4}
TEST_TYPES = {  # type -> (process that owns it, level name used by test runs)
    "unit-test": ("SWE.4", "unit"),
    "software-integration-test": ("SWE.5", "software-integration"),
    "software-qualification-test": ("SWE.6", "software-qualification"),
    "system-integration-test": ("SYS.4", "system-integration"),
    "system-qualification-test": ("SYS.5", "system-qualification"),
}
RUN_LEVELS = {level: process for process, level in TEST_TYPES.values()}   # level of a test run -> its process
INTEGRATION_LEVELS = {  # integration at software level (SWE.5, SWE.6) and at system level (SYS.4, SYS.5)
    "software": {"kind": "software-integration", "element": "software-component", "test": "software-integration-test",
                 "integration": "software-integration", "qualification": "software-qualification",
                 "practices": ("SWE.5.BP6", "SWE.6.BP4"), "name": "software"},
    "system": {"kind": "system-integration", "element": "system-element", "test": "system-integration-test",
               "integration": "system-integration", "qualification": "system-qualification",
               "practices": ("SYS.4.BP6", "SYS.5.BP4"), "name": "system"},
}
LEVEL_OF_TEST = {spec["test"]: level for level, spec in INTEGRATION_LEVELS.items()}
CS_PREFIX = "21434:"                       # references to ISO/SAE 21434 in `supports`
SUPPLIER_REVIEW_KINDS = {"ACQ.4.BP3": "technical", "ACQ.4.BP4": "progress"}   # which reviews evidence which practice
STANDARD_PREFIXES = (CS_PREFIX, "26262-")  # types that only these standards use are evidence of each they name
FS_PREFIX = "26262:"                       # scope key of a part of ISO 26262; references read "26262-<part>:<clause>"
ASIL_RANK = {"QM": 0, "A": 1, "B": 2, "C": 3, "D": 4}
INDEPENDENCE = {"I0": 0, "I1": 1, "I2": 2, "I3": 3}
FS_DECISIONS = ("performed", "tailored", "not-applicable", "by-customer", "by-supplier", "by-organization")
METHOD_TABLE_PARTS = ("4", "5", "6", "8")
_FS_CATALOG = None


def fs_catalog():
    """The catalog of ISO 26262: parts, clauses, requirement numbers, work products, table titles."""
    global _FS_CATALOG
    if _FS_CATALOG is None:
        path = ROOT / "iso-26262" / "2018" / "catalog.yaml"
        _FS_CATALOG = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {"parts": []}
    return _FS_CATALOG


IMPACT_LEVELS = ["negligible", "moderate", "major", "severe"]         # lowest first
FEASIBILITY_LEVELS = ["very-low", "low", "medium", "high"]            # lowest first; the columns of risk_matrix
CS_PROPERTIES = {"confidentiality", "integrity", "availability", "authenticity", "authorization", "non-repudiation"}
CS_TREATMENTS = ("avoid", "reduce", "share", "retain")
CS_DECISIONS = ("performed", "tailored", "not-applicable", "by-customer", "by-supplier")
_CS_CATALOG = None


def cs_catalog():
    """The catalog of ISO/SAE 21434: clauses, subclauses, requirement and work product identifiers."""
    global _CS_CATALOG
    if _CS_CATALOG is None:
        path = ROOT / "iso-sae-21434" / "2021" / "catalog.yaml"
        _CS_CATALOG = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() \
            else {"clauses": [], "work_products": []}
    return _CS_CATALOG


VERDICTS = {"passed", "failed", "blocked", "not-run"}
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.S)
HEADING = re.compile(r"^##\s+(.+?)\s*$")
C_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
C_SIGNATURE = re.compile(r"(?m)^[ \t]*((?:[A-Za-z_]\w*[ \t\*]+)+)([A-Za-z_]\w*)\s*\(([^;{}()]*)\)\s*[;{]")
C_DEFINITION = re.compile(
    r"^(?!\s*(?:static|typedef|return|if|else|for|while|switch|do)\b)"
    r"[A-Za-z_][\w \t\*]*?\b([A-Za-z_]\w*)\s*\([^;{}()]*\)\s*\{", re.M)


# --------------------------------------------------------------------------- items

class Item:
    def __init__(self, path, front, body):
        self.path = path
        self.front = front
        self.id = str(front.get("id", ""))
        self.type = str(front.get("type", ""))
        self.status = str(front.get("status", ""))
        self.title = str(front.get("title", ""))
        self.sections = split_sections(body)
        self.hash = content_hash(front, body)

    @property
    def imported(self):
        return bool(self.front.get("imported"))

    def targets(self, role):
        """Link targets of one role as (item id, anchor or None)."""
        values = (self.front.get("links") or {}).get(role) or []
        if isinstance(values, str):
            values = [values]
        return [tuple((str(v).split("#", 1) + [None])[:2]) for v in values]

    def has_section(self, name):
        return bool(self.sections.get(name, "").strip())


def split_sections(body):
    sections, current, fenced = {}, None, False
    for line in body.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        match = None if fenced else HEADING.match(line)
        if match:
            current = match.group(1)
            sections[current] = ""
        elif current is not None:
            sections[current] += line + "\n"
    return sections


HASH_EXCLUDED = ("status", "source_files", "progress")   # state, the pointer from a unit design to its code, tracking
HASH_EXCLUDED_LINKS = ("delivers",)       # which items a work package has produced so far: tracking, not plan
# What a component is to an interface that names it. The names differ from every link role
# on purpose: `uses` is a link of software units.
INTERFACE_ROLES = {"provided_by": "provider of", "used_by": "user of"}
UNRESOLVED = ("open", "analysed", "in-resolution")          # states of a problem report that is not yet resolved


def content_hash(front, body):
    data = {k: v for k, v in front.items() if k not in HASH_EXCLUDED}
    if isinstance(data.get("links"), dict) and any(r in data["links"] for r in HASH_EXCLUDED_LINKS):
        data["links"] = {r: t for r, t in data["links"].items() if r not in HASH_EXCLUDED_LINKS}
        if not data["links"]:
            del data["links"]
    head = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    lines = [line.rstrip() for line in body.replace("\r\n", "\n").split("\n")]
    text = "\n".join(lines).strip("\n")
    return hashlib.sha256((head + "\n" + text).encode("utf-8")).hexdigest()[:12]


def file_hash(path):
    """Hash of a source file, independent of line-ending style."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]


def record_number(item_id):
    """The running number of an ID, for ordering records by age."""
    tail = str(item_id).rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else 0


def c_type(text):
    """A C type written one way: single spaces, none around '*'."""
    return re.sub(r"\s*\*\s*", "*", " ".join(str(text).split()))


def c_signatures(code):
    """{function: (return type, [parameter types])} for the declarations and definitions in comment-free C text."""
    found = {}
    for match in C_SIGNATURE.finditer(code):
        returns = c_type(re.sub(r"\b(static|extern|inline)\b", " ", match.group(1)))
        name, parameters = match.group(2), match.group(3).strip()
        if not returns or name in ("if", "for", "while", "switch", "return", "sizeof"):
            continue
        types = []
        if parameters and parameters != "void":
            for parameter in parameters.split(","):
                named = re.match(r"^(.*[\s\*])([A-Za-z_]\w*)\s*((?:\[[^\]]*\])*)$", parameter.strip())
                types.append(c_type(named.group(1) + ("*" if named.group(3) else "")) if named else c_type(parameter))
        found.setdefault(name, (returns, types))
    return found


DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SETTLED = {"engineering": ("approved",), "record": ("final",), "query": ("closed",), "change-request": ("closed",),
           "problem-report": ("closed",), "action": ("closed",)}


def as_date(value):
    """A date from an attribute value (YAML may already have read it as one), or None."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and DATE.match(value.strip()):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def latest(records):
    """The record executed last; the higher number decides between equal times."""
    return max(records, key=lambda r: (str(r.front.get("executed_at", "")), record_number(r.id)), default=None)


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def process_of(ref):
    """The process a reference of `supports` belongs to: SWE.1 for SWE.1.BP3, the clause 21434:9 for a
    subclause 21434:9.4 or a work product 21434:WP-09-03; None for a work product of the process catalog."""
    ref = str(ref)
    if ".BP" in ref:
        return ref.split(".BP")[0]
    if ref.startswith("26262-"):
        part = ref[len("26262-"):].split(":")[0]
        return FS_PREFIX + part if part.isdigit() else None
    if ref.startswith(CS_PREFIX):
        rest = ref[len(CS_PREFIX):]
        number = rest[3:5] if rest.startswith("WP-") else rest.split(".")[0]
        return CS_PREFIX + str(int(number)) if number.isdigit() else None
    return None


# --------------------------------------------------------------------------- project

class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.schema = yaml.safe_load((ROOT / "schema" / "items.yaml").read_text(encoding="utf-8"))
        cfg = self.root / "project.yaml"
        self.config = (yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}) if cfg.exists() else {}
        processes = (self.config.get("scope") or {}).get("processes")
        self.scope = set(processes) if processes else None      # None = every process of the catalog in scope
        # clauses of ISO/SAE 21434 count only where the project declares them
        self.cs_scope = {CS_PREFIX + str(c) for c in as_list((self.config.get("scope") or {}).get("cybersecurity"))}
        # parts of ISO 26262 likewise
        self.fs_scope = {FS_PREFIX + str(p) for p in as_list((self.config.get("scope") or {}).get("safety"))}
        self.types = self.schema["types"]
        self.rules = {r["id"]: r for r in self.schema["coverage"]}
        self.items, self.findings = {}, []
        self.incoming = defaultdict(lambda: defaultdict(list))   # target id -> role -> [source ids]
        self.load()

    # ---- loading

    def load(self):
        folders = (self.config.get("paths") or {}).get("items") or ["plans", "spec", "verification", "records"]
        for folder in folders:
            for path in sorted((self.root / folder).rglob("*.md")):
                rel = path.relative_to(self.root).as_posix()
                text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
                match = FRONT_MATTER.match(text)
                if not match:
                    self.add("error", "FORMAT", rel, "no YAML front matter between two '---' lines")
                    continue
                try:
                    front = yaml.safe_load(match.group(1)) or {}
                except yaml.YAMLError as exc:
                    self.add("error", "FORMAT", rel, "front matter is not valid YAML: %s" % str(exc).split("\n")[0])
                    continue
                if not isinstance(front, dict) or not front.get("id"):
                    self.add("error", "FORMAT", rel, "front matter has no id")
                    continue
                item = Item(path, front, match.group(2))
                if item.id in self.items:
                    self.add("error", "FORMAT", item.id, "id used twice: %s and %s"
                             % (self.items[item.id].path.relative_to(self.root).as_posix(), rel))
                    continue
                self.items[item.id] = item
        for item in self.items.values():
            for role in (item.front.get("links") or {}):
                for target, _ in item.targets(role):
                    self.incoming[target][role].append(item.id)
            if item.type == "software-interface":
                # the component that provides an interface and the components that use it all
                # build on it: a change of the interface reaches them
                for name in ("provided_by", "used_by"):
                    for component in as_list(item.front.get(name)):
                        self.incoming[item.id][name].append(str(component))

    # ---- helpers

    def add(self, level, rule, subject, message, supports=None):
        supports = [s for s in (supports or []) if process_of(s) and self.covers(process_of(s))]   # only what is in scope
        self.findings.append({"level": level, "rule": rule, "item": subject, "message": message,
                              "supports": supports})

    def attributes(self, type_name):
        out = {}
        for name, spec in self.types[type_name]["attributes"].items():
            if name == "use":
                for used in spec:
                    out.update(self.schema["attribute_sets"][used])
            else:
                out[name] = spec
        return out

    def lifecycle(self, item):
        return self.schema["lifecycles"][self.types[item.type]["lifecycle"]]

    def due(self, item, stage):
        """Is something marked with this stage required for the item in its current state?"""
        if stage == "always":
            return True
        if stage == "optional":
            return False
        return item.status in self.lifecycle(item).get("stages", {}).get(stage, [])

    def live(self, item):
        return item.status not in ("rejected", "obsolete")

    def unsettled(self, item):
        """An engineering item that is in use but not approved: what builds on it cannot be settled either."""
        return self.live(item) and item.status != "approved" \
            and self.types.get(item.type, {}).get("lifecycle") == "engineering"

    def of_type(self, *types):
        return [i for i in self.items.values() if i.type in types]

    def sources(self, target_id, role, types=None):
        found = [self.items[s] for s in self.incoming[target_id][role] if s in self.items]
        return [s for s in found if self.live(s) and (types is None or s.type in types)]

    def dependencies(self, item):
        """(target id, role) of everything the item builds on: its links and, for a component,
        the interfaces it provides or uses (which are stated on the interface)."""
        found = [(target, role) for role in (item.front.get("links") or {}) if self.evidence(item.type, role)
                 for target, _ in item.targets(role)]
        if item.type == "software-component":
            for interface in self.of_type("software-interface"):
                for name, role in INTERFACE_ROLES.items():
                    if item.id in map(str, as_list(interface.front.get(name))):
                        found.append((interface.id, role))
        return list(dict.fromkeys(found))                 # several links to parts of one target count once

    def evidence(self, type_name, role):
        """False for links that plan or track work: they need no review against their targets."""
        pairs = [p for p in (self.schema["links"].get(role) or {}).get("pairs", []) if p["from"] == type_name]
        return not any(p.get("evidence") == "none" for p in pairs)

    def supports_of(self, item, role):
        """The base practices a dependency of this kind is evidence for."""
        if role in self.schema["links"]:
            return [s for p in self.schema["links"][role]["pairs"] if p["from"] == item.type for s in p["supports"]]
        return ["SWE.2.BP3", "SWE.2.BP8"]                 # provider of / user of an interface

    def allocation_targets(self, requirement):
        """Architectural elements a requirement is allocated to (the elements that fulfil it)."""
        imported = [self.items[t] for t, _ in requirement.targets("allocated_to") if t in self.items]
        return self.sources(requirement.id, "fulfils") + [e for e in imported if e not in self.sources(requirement.id, "fulfils")]

    def allocated_requirements(self, element_id, types=None):
        """Requirements allocated to an architectural element (the requirements it fulfils)."""
        element = self.items.get(element_id)
        found = [self.items[t] for t, _ in element.targets("fulfils") if t in self.items] if element else []
        found += [self.items[s] for s in self.incoming[element_id]["allocated_to"] if s in self.items
                  and self.items[s] not in found] if element else []
        return [r for r in found if self.live(r) and (types is None or r.type in types)]

    def covers(self, process):
        """Whether a process (SWE.1) or a clause of ISO/SAE 21434 (21434:9) is in the project's scope."""
        if str(process).startswith(CS_PREFIX):
            return process in self.cs_scope
        if str(process).startswith(FS_PREFIX):
            return process in self.fs_scope
        return self.scope is None or process in self.scope

    def in_scope(self, supports):
        return any(self.covers(p) for p in {process_of(s) for s in supports} if p)

    def active(self, rule_id):
        return self.in_scope(self.rules[rule_id]["supports"])

    def level_for(self, item):
        """How serious a coverage gap is, by how far the item has progressed."""
        stages = self.lifecycle(item).get("stages", {})
        if item.status in stages.get("before-approval", []):
            return "error"
        if item.status in stages.get("before-review", []):
            return "warning"
        return "info"

    def own_supports(self, rule_id, item, fallback="rule"):
        """The practices of a rule that belong to the process owning the item, so that a
        finding on a requirement is not counted against the unit verification process.
        When none of them does: all practices of the rule, or - for a rule about the item
        itself (fallback "subject") - the practices the item is evidence for."""
        supports = self.rules[rule_id]["supports"]
        if item.type == "plan":
            refs = self.schema["plan_kinds"].get(item.front.get("kind"), [])
        else:
            refs = self.types.get(item.type, {}).get("supports") or []
        processes = {process_of(r) for r in refs} - {None}
        own = [s for s in supports if process_of(s) in processes]
        if not own and fallback == "subject":
            own = [str(r) for r in refs if process_of(r)]
        return own or supports

    def gap(self, rule_id, item, message, fallback="rule"):
        self.add(self.level_for(item), rule_id, item.id, message, self.own_supports(rule_id, item, fallback))

    def reviews_of(self, item, verdict=None):
        """Final review records whose subject names this item at its current content, oldest first."""
        found = []
        for rev in self.of_type("review-record"):
            if rev.status != "final" or (verdict and rev.front.get("verdict") != verdict):
                continue
            if any(isinstance(e, dict) and e.get("item") == item.id and str(e.get("hash")) == item.hash
                   for e in as_list(rev.front.get("subject"))):
                found.append(rev)
        return sorted(found, key=lambda r: record_number(r.id))

    def unit_gap(self, rule_id, unit, message):
        """A verification gap of a unit: an error once the unit has code, pending before."""
        if as_list(unit.front.get("source_files")):
            self.gap(rule_id, unit, message)
        else:
            self.add("warning" if unit.status == "approved" else "info", rule_id, unit.id,
                     message + " (pending: the unit has no code yet)", self.own_supports(rule_id, unit))

    def approving_review(self, item):
        """The newest final review record that approved this item at its current content, if any."""
        reviews = self.reviews_of(item, "approved")
        return reviews[-1] if reviews else None

    def latest_run(self, type_name, **match):
        return latest([r for r in self.of_type(type_name) if r.status == "final"
                       and all(r.front.get(k) == v for k, v in match.items())])

    # ---- integration steps (SWE.5 and SYS.4)

    def integration_plan(self, level="software"):
        """The approved integration plan of the level, or None."""
        kind = INTEGRATION_LEVELS[level]["kind"]
        return next((p for p in sorted(self.of_type("plan"), key=lambda p: record_number(p.id))
                     if p.status == "approved" and p.front.get("kind") == kind), None)

    def integration_steps(self, plan=None, level="software"):
        plan = plan or self.integration_plan(level)
        return [s for s in as_list(plan.front.get("integration_steps")) if isinstance(s, dict) and s.get("name")] \
            if plan else []

    def leaves(self, entry):
        """What a step entry stands for: a system element, a software component, or the components inside a composition."""
        item = self.items.get(str(entry))
        if item is None:
            return []
        if item.type == "system-element":
            return [item.id]
        if item.type != "software-component":
            return []
        if item.front.get("kind") != "composition":
            return [item.id]
        return [c for c in self.descendants(item.id) if self.items[c].front.get("kind") != "composition"]

    def integrated_up_to(self, steps, index):
        out = []
        for step in steps[:index + 1]:
            for entry in as_list(step.get("components")):
                out += [c for c in self.leaves(entry) if c not in out]
        return out

    def builds_of(self, step_name, succeeded=False, level="software"):
        return [b for b in self.of_type("build-record") if b.status == "final" and b.front.get("step") == step_name
                and (b.front.get("level") or "software") == level
                and (not succeeded or b.front.get("result") == "succeeded")]

    def problem_plan(self):
        """The approved plan of kind problem-resolution, or None."""
        return next((p for p in sorted(self.of_type("plan"), key=lambda p: record_number(p.id))
                     if p.status == "approved" and p.front.get("kind") == "problem-resolution"), None)

    def risk_plan(self):
        """The approved plan of kind risk-management, or else the one in work, so that risks are rated against the
        scale while the plan is written; outputs name its state."""
        return self.plan_in_work("risk-management")

    def quality_plan(self):
        """The approved plan of kind quality-assurance, or None."""
        return next((p for p in sorted(self.of_type("plan"), key=lambda p: record_number(p.id))
                     if p.status == "approved" and p.front.get("kind") == "quality-assurance"), None)

    def problem_gap(self, rule_id, problem, message):
        """Urgency and alerts matter from the first day: a warning while the problem is open, an error after."""
        self.add("warning" if problem.status == "open" else "error", rule_id, problem.id, message,
                 self.own_supports(rule_id, problem))

    def build_step(self, run, level=None):
        """The integration step of the build a test run names (of the given level, if one is given), or None."""
        build = self.items.get(str(run.front.get("build") or ""))
        if build is None or build.type != "build-record":
            return None
        if level and (build.front.get("level") or "software") != level:
            return None
        return build.front.get("step")

    # ---- structural checks

    def check_structure(self):
        prefixes = {spec["prefix"]: name for name, spec in self.types.items()}
        for item in self.items.values():
            rel = item.path.relative_to(self.root).as_posix()
            if item.type not in self.types:
                self.add("error", "SCHEMA", item.id, "unknown type '%s'" % item.type)
                continue
            spec = self.types[item.type]
            if item.path.stem != item.id:
                self.add("error", "FORMAT", item.id, "file name %s does not match the id" % item.path.name)
            if prefixes.get(item.id.rsplit("-", 1)[0]) != item.type:
                self.add("error", "FORMAT", item.id, "id prefix does not belong to type %s (expected %s-NNNN)"
                         % (item.type, spec["prefix"]))
            if not rel.startswith(spec["folder"].rstrip("/") + "/"):
                self.add("error", "FORMAT", item.id, "file is in %s, expected under %s/" % (rel, spec["folder"]))
            if item.status not in self.lifecycle(item)["states"]:
                self.add("error", "SCHEMA", item.id, "status '%s' is not a state of its lifecycle %s"
                         % (item.status, self.lifecycle(item)["states"]))
                continue
            self.check_attributes(item)
            self.check_links(item)
        self.check_records()
        self.check_cybersecurity_values()

    def check_attributes(self, item):
        attrs = self.attributes(item.type)
        for name in item.front:
            if name not in attrs and name != "links":
                self.add("warning", "SCHEMA", item.id, "attribute '%s' is not defined for type %s" % (name, item.type))
        origin = item.front.get("imported")
        if origin is not None and not (isinstance(origin, dict) and origin.get("source") and origin.get("version")):
            self.add("error", "SCHEMA", item.id, "imported must be a mapping that names at least source and version")
        for name, spec in attrs.items():
            value = item.front.get(name)
            missing = value is None or value == "" or (value == [] and not spec.get("may_be_empty"))
            stage = spec.get("required", "optional")
            if missing:
                if self.due(item, stage) and not (item.imported and stage != "always"):
                    self.add("error", "SCHEMA", item.id, "attribute '%s' is required (%s)" % (name, stage))
                continue
            if "values" in spec and value not in spec["values"]:
                self.add("error", "SCHEMA", item.id, "attribute '%s' is %r, allowed: %s" % (name, value, spec["values"]))
            if spec.get("format") == "date" and as_date(value) is None:
                self.add("error", "SCHEMA", item.id, "attribute '%s' is %r: expected a date YYYY-MM-DD" % (name, value))
            if "structure" in spec:
                self.check_structured(item, name, value, spec["structure"])
        if not item.imported:
            for section, stage in (self.types[item.type].get("sections") or {}).items():
                if self.due(item, stage) and not item.has_section(section):
                    self.add("error", "SCHEMA", item.id, "section '%s' is required (%s)" % (section, stage))
            upcoming = next((s for s in ("before-review", "before-approval") if not self.due(item, s)), None)
            if upcoming and self.live(item):
                missing = [n for n, spec in attrs.items() if spec.get("required") == upcoming
                           and item.front.get(n) in (None, "", [])]
                missing += ["section " + s for s, stage in (self.types[item.type].get("sections") or {}).items()
                            if stage == upcoming and not item.has_section(s)]
                if missing:
                    self.add("info", "SCHEMA", item.id, "still to come %s: %s"
                             % (upcoming.replace("before-", "before "), ", ".join(missing)))
        for cond in self.schema.get("conditions") or []:
            if cond["types"] != "any" and item.type not in cond["types"]:
                continue
            if any(name not in attrs for name in cond["when"]):
                continue
            if not all(item.front.get(name) in allowed for name, allowed in cond["when"].items()):
                continue
            if not self.due(item, cond["stage"]) or (item.imported and cond["stage"] != "always"):
                continue
            reason = ", ".join("%s is %s" % (k, item.front.get(k)) for k in cond["when"])
            for name in cond.get("attributes") or []:
                value = item.front.get(name)
                if value is None or value == "" or value == []:
                    self.add("error", "SCHEMA", item.id, "attribute '%s' is required because %s" % (name, reason))
                elif "structure" in cond:
                    self.check_structured(item, name, value, cond["structure"])
            for section in cond.get("sections") or []:
                if not item.has_section(section):
                    self.add("error", "SCHEMA", item.id, "section '%s' is required because %s" % (section, reason))

    def check_structured(self, item, name, value, structure_name):
        structure = self.schema["structures"][structure_name]
        known = set(structure["mandatory"]) | set(structure["keys"])
        if structure.get("shape") == "mapping":
            records = [value]
            if isinstance(value, dict) and not value:
                self.add("error", "SCHEMA", item.id, "'%s' is empty: give objectives or not_relevant with a reason" % name)
        else:
            records = value if isinstance(value, list) else [value]
        for n, record in enumerate(records, 1):
            if not isinstance(record, dict):
                self.add("error", "SCHEMA", item.id, "'%s' entry %d is not a mapping (structure %s)" % (name, n, structure_name))
                continue
            label = record.get("name", n)
            for key in structure["mandatory"]:
                if record.get(key) in (None, "", []):
                    self.add("error", "SCHEMA", item.id, "'%s' entry %s lacks '%s'" % (name, label, key))
            for key in record:
                if key not in known:
                    self.add("warning", "SCHEMA", item.id, "'%s' entry %s has unknown key '%s'" % (name, label, key))
            for key in structure.get("dates") or []:
                if record.get(key) not in (None, "") and as_date(record[key]) is None:
                    self.add("error", "SCHEMA", item.id, "'%s' entry %s: %s is %r, expected a date YYYY-MM-DD"
                             % (name, label, key, record[key]))

    def check_links(self, item):
        allowed = defaultdict(set)      # role -> target types this item type may link to
        for role, link in self.schema["links"].items():
            for pair in link["pairs"]:
                if pair["from"] == item.type:
                    allowed[role] |= {"any"} if pair["to"] == "any" else set(pair["to"])
        for role in (item.front.get("links") or {}):
            if role not in self.schema["links"]:
                self.add("error", "LINK", item.id, "unknown link role '%s'" % role)
                continue
            if role not in allowed:
                self.add("error", "LINK", item.id, "type %s may not carry '%s' links" % (item.type, role))
                continue
            for target_id, anchor in item.targets(role):
                target = self.items.get(target_id)
                if target is None:
                    self.add("error", "LINK", item.id, "%s target %s does not exist" % (role, target_id))
                    continue
                if "any" not in allowed[role] and target.type not in allowed[role]:
                    self.add("error", "LINK", item.id, "%s target %s is a %s; allowed: %s"
                             % (role, target_id, target.type, sorted(allowed[role])))
                if self.live(item) and not self.live(target) and role != "shows":      # views: see COV-24
                    self.add("error", "LINK", item.id, "%s target %s is %s" % (role, target_id, target.status))
                if anchor:
                    names = {f.get("name") for f in as_list(target.front.get("functions")) if isinstance(f, dict)}
                    if anchor not in names:
                        self.add("error", "LINK", item.id, "%s target %s#%s: the unit designs no function of that name"
                                 % (role, target_id, anchor))
        for target_id, _ in item.targets("allocated_to"):
            target = self.items.get(target_id)
            if target is not None and not target.imported:
                self.add("error", "LINK", item.id, "allocated_to %s, an element of the project: the allocation is stated "
                         "on the element (fulfils); allocated_to is for elements received from outside the scope" % target_id)
        if item.type == "software-interface":
            for name in ("provided_by", "used_by"):
                for ref in as_list(item.front.get(name)):
                    if getattr(self.items.get(str(ref)), "type", None) != "software-component":
                        self.add("error", "LINK", item.id, "%s names %s, which is not a software component" % (name, ref))
        if item.type in TEST_TYPES and item.front.get("script"):
            script, _, function = str(item.front["script"]).partition("::")
            file = self.root / script
            if not file.is_file():
                self.add("error", "LINK", item.id, "script names %s, which does not exist" % script)
            elif function and not re.search(r"\b%s\b" % re.escape(function),
                                            file.read_text(encoding="utf-8", errors="replace")):
                self.add("error", "LINK", item.id, "script names function %s, which is not in %s" % (function, script))
        ref = item.front.get("superseded_by")
        if ref and re.fullmatch(r"[A-Z]+-\d+", str(ref)) and str(ref) not in self.items:
            self.add("error", "LINK", item.id, "superseded_by names %s, which does not exist" % ref)

    def check_records(self):
        for rev in self.of_type("review-record"):
            for name in ("subject", "references"):
                for entry in as_list(rev.front.get(name)):
                    if not isinstance(entry, dict) or "item" not in entry or "hash" not in entry:
                        self.add("error", "SCHEMA", rev.id, "%s entries must be {item, hash}" % name)
                    elif entry["item"] not in self.items:
                        self.add("error", "LINK", rev.id, "%s names %s, which does not exist" % (name, entry["item"]))
            for finding in as_list(rev.front.get("findings")):
                if isinstance(finding, dict) and finding.get("state") not in ("open", "closed"):
                    self.add("error", "SCHEMA", rev.id, "finding %s has state %r; allowed: open, closed"
                             % (finding.get("id"), finding.get("state")))
        for run in self.of_type("test-run"):
            for entry in as_list(run.front.get("results")):
                if not isinstance(entry, dict) or entry.get("verdict") not in VERDICTS:
                    self.add("error", "SCHEMA", run.id, "results entries must be {test, verdict}; verdict one of %s" % sorted(VERDICTS))
                elif getattr(self.items.get(str(entry.get("test"))), "type", None) not in TEST_TYPES:
                    self.add("error", "LINK", run.id, "result names %s, which is not a test case" % entry.get("test"))
            if run.front.get("build") and getattr(self.items.get(str(run.front["build"])), "type", None) != "build-record":
                self.add("error", "LINK", run.id, "build names %s, which is not a build record" % run.front["build"])
        for agreement in self.of_type("supplier-agreement"):
            for ref in as_list(agreement.front.get("components")):
                if getattr(self.items.get(str(ref)), "type", None) not in ("software-component", "system-element"):
                    self.add("error", "LINK", agreement.id, "components names %s, which is no software component or "
                             "system element" % ref)
        earlier = {}
        for review in sorted(self.of_type("supplier-review"), key=lambda r: (str(r.front.get("held_at")), record_number(r.id))):
            if getattr(self.items.get(str(review.front.get("agreement"))), "type", None) != "supplier-agreement":
                self.add("error", "LINK", review.id, "agreement names %s, which is no supplier agreement"
                         % review.front.get("agreement"))
            for item in as_list(review.front.get("open_items")):
                ref = item.get("closes") if isinstance(item, dict) else None
                if ref and earlier.get(str(ref)) != review.front.get("agreement"):
                    self.add("error", "LINK", review.id, "open item %s closes %s, which is no open item of an earlier "
                             "review of the same agreement" % (item.get("id"), ref))
            for item in as_list(review.front.get("open_items")):
                if isinstance(item, dict) and item.get("state") == "open":
                    earlier["%s#%s" % (review.id, item.get("id"))] = review.front.get("agreement")
        for record in self.of_type("quality-record"):
            if record.front.get("kind") in ("work-product", "summary"):
                for ref in as_list(record.front.get("subject")):
                    if str(ref) not in self.items:
                        self.add("error", "LINK", record.id, "subject names %s, which does not exist" % ref)
        for build in self.of_type("build-record"):
            element = INTEGRATION_LEVELS.get(build.front.get("level") or "software", INTEGRATION_LEVELS["software"])["element"]
            for entry in as_list(build.front.get("contents")):
                if not isinstance(entry, dict) or getattr(self.items.get(str(entry.get("component"))), "type", None) \
                        != element:
                    self.add("error", "LINK", build.id, "contents entries must name a %s under 'component'"
                             % element.replace("-", " "))
                    continue
                for unit_id in as_list(entry.get("units")):
                    if getattr(self.items.get(str(unit_id)), "type", None) != "software-unit":
                        self.add("error", "LINK", build.id, "contents name %s, which is not a software unit" % unit_id)
        for run in self.of_type("static-analysis-run"):
            for entry in as_list(run.front.get("results")):
                if not isinstance(entry, dict) or getattr(self.items.get(str(entry.get("unit"))), "type", None) != "software-unit":
                    self.add("error", "LINK", run.id, "results entries must name a software unit under 'unit'")
        for base in self.of_type("baseline"):
            for entry in as_list(base.front.get("items")):
                if not isinstance(entry, dict) or entry.get("item") not in self.items:
                    self.add("error", "LINK", base.id, "baseline lists %s, which does not exist"
                             % (entry.get("item") if isinstance(entry, dict) else entry))

    # ---- coverage rules

    def check_coverage(self):
        for rule_id in sorted(self.rules):
            if self.active(rule_id):
                getattr(self, "cov_" + rule_id[-2:])(rule_id)
        self.check_consistency_evidence()

    def need_link(self, rule_id, type_name, role, waiver=None, text=None):
        for item in self.of_type(type_name):
            if self.live(item) and not item.targets(role) and not (waiver and waiver(item)):
                self.gap(rule_id, item, text or "no %s link" % role)

    def need_incoming(self, rule_id, type_name, role, source_types, text, only=None, waiver=None):
        for item in self.of_type(type_name):
            if not self.live(item) or (only and not only(item)) or (waiver and waiver(item)):
                continue
            if not self.sources(item.id, role, source_types):
                self.gap(rule_id, item, text)

    @staticmethod
    def internal_with_rationale(item):
        return item.front.get("origin") == "internal" and item.has_section("Rationale")

    @staticmethod
    def constraint_with_rationale(item):
        return item.front.get("kind") == "constraint" and item.has_section("Rationale")

    def cov_01(self, rule):
        self.need_incoming(rule, "stakeholder-requirement", "derived_from", ["system-requirement"],
                           "accepted, but no system requirement is derived from it",
                           only=lambda i: i.front.get("assessment") in ("accepted", "accepted-with-deviation")
                           or (i.imported and not i.front.get("assessment")))

    def cov_02(self, rule):
        self.need_link(rule, "system-requirement", "derived_from", self.internal_with_rationale,
                       "no derived_from link, and not marked origin internal with a Rationale")

    def need_allocation(self, rule, type_name, text):
        for req in self.of_type(type_name):
            if self.live(req) and not self.allocation_targets(req) and not self.constraint_with_rationale(req):
                self.gap(rule, req, text)

    def cov_03(self, rule):
        self.need_allocation(rule, "system-requirement", "not allocated to any system element or interface")

    def cov_04(self, rule):
        for element in self.of_type("system-element"):
            if self.live(element) and not self.allocated_requirements(element.id, ["system-requirement"]):
                self.gap(rule, element, "no system requirement is allocated to it")

    def cov_05(self, rule):
        live = [r for r in self.of_type("system-requirement") if self.live(r)]
        if live and not any(self.allocation_targets(r) for r in live):
            self.add("warning", rule, "project", "no system requirement is allocated to an element: COV-05 cannot tell "
                     "which of the %d need software requirements; register the allocation the delivery states, or ask "
                     "the source for it" % len(live), self.rules[rule]["supports"])
        for req in self.of_type("system-requirement"):
            if not self.live(req):
                continue
            elements = self.allocation_targets(req)
            software = [e for e in elements if e.type == "system-element" and e.front.get("kind") == "software"]
            if not software:
                continue
            covered = self.sources(req.id, "derived_from", ["software-requirement"])
            by_element = (self.config.get("trace") or {}).get("derive_via_elements") and any(
                self.sources(e.id, "derived_from", ["software-requirement"]) for e in software)
            if not covered and not by_element:
                self.gap(rule, req, "allocated to software, but no software requirement is derived from it")

    def cov_06(self, rule):
        self.need_link(rule, "software-requirement", "derived_from", self.internal_with_rationale,
                       "no derived_from link, and not marked origin internal with a Rationale")

    def cov_07(self, rule):
        self.need_allocation(rule, "software-requirement", "not allocated to any software component or interface")

    def descendants(self, component_id):
        out, queue = [], [component_id]
        while queue:
            for child in self.sources(queue.pop(), "part_of", ["software-component"]):
                if child.id not in out:
                    out.append(child.id)
                    queue.append(child.id)
        return out

    def cov_08(self, rule):
        for comp in self.of_type("software-component"):
            if not self.live(comp):
                continue
            if comp.front.get("origin") in ("supplied", "generated") and comp.has_section("Purpose"):
                continue
            family = [comp.id] + self.descendants(comp.id)
            if not any(self.allocated_requirements(cid, ["software-requirement"]) for cid in family):
                self.gap(rule, comp, "no software requirement is allocated to it or to a component inside it")

    def cov_09(self, rule):
        for comp in self.of_type("software-component"):
            if not self.live(comp) or comp.front.get("origin") != "developed" or comp.front.get("kind") == "composition":
                continue
            designs = self.sources(comp.id, "refines", ["component-design"])
            if len(designs) != 1:
                self.gap(rule, comp, "%d component designs refine it, expected exactly 1" % len(designs))
            if not self.sources(comp.id, "part_of", ["software-unit"]):
                self.gap(rule, comp, "no software unit is part of it")

    def cov_10(self, rule):
        for unit in self.of_type("software-unit"):
            if not self.live(unit):
                continue
            parents = unit.targets("part_of")
            if len(parents) != 1:
                self.gap(rule, unit, "%d part_of links, expected exactly 1" % len(parents))
            for path in as_list(unit.front.get("source_files")):
                if not (self.root / str(path)).is_file():
                    self.gap(rule, unit, "source file %s does not exist" % path)
            if not as_list(unit.front.get("source_files")) and unit.front.get("origin") not in ("generated", "third-party"):
                self.add("warning" if unit.status == "approved" else "info", rule, unit.id,
                         "no source files listed: the unit is designed but not implemented", self.own_supports(rule, unit))

    def cov_11(self, rule):
        paths = self.config.get("paths") or {}
        exempt = as_list(paths.get("generated")) + as_list(paths.get("third_party"))
        owners = defaultdict(list)
        for unit in self.of_type("software-unit"):
            if self.live(unit):
                for path in as_list(unit.front.get("source_files")):
                    owners[Path(str(path)).as_posix()].append(unit.id)
        for source_root in as_list(paths.get("source_roots")):
            for path in sorted((self.root / source_root).rglob("*")):
                rel = path.relative_to(self.root).as_posix()
                if not path.is_file() or any(fnmatch.fnmatch(rel, pattern) for pattern in exempt):
                    continue
                if len(owners[rel]) != 1:
                    self.add("error", rule, rel, "belongs to %d software units (%s), expected exactly 1"
                             % (len(owners[rel]), ", ".join(owners[rel]) or "none"), self.rules[rule]["supports"])

    def cov_12(self, rule):
        run = self.latest_run("static-analysis-run")
        analysed = {e.get("unit") for e in as_list(run.front.get("results")) if isinstance(e, dict)} if run else set()
        for unit in self.of_type("software-unit"):
            if not self.live(unit) or unit.front.get("origin") in ("generated", "third-party"):
                continue
            if not self.sources(unit.id, "verifies", ["unit-test"]):
                self.unit_gap(rule, unit, "no unit test verifies it")
            if unit.id not in analysed:
                self.unit_gap(rule, unit, "the latest final static analysis run has no entry for it"
                              if run else "no final static analysis run exists")

    def cov_13(self, rule):
        self.need_incoming(rule, "software-interface", "verifies", ["software-integration-test"],
                           "no software integration test verifies it")

    def verified_or_reviewed(self, rule, type_name, test_type, text):
        for req in self.of_type(type_name):
            if not self.live(req):
                continue
            if req.front.get("verification_method") == "test":
                if not self.sources(req.id, "verifies", [test_type]):
                    self.gap(rule, req, text)
            elif req.front.get("verification_method") and not self.approving_review(req):
                self.gap(rule, req, "verified by %s, but no final review record covers its current content"
                         % req.front.get("verification_method"))

    def cov_14(self, rule):
        self.verified_or_reviewed(rule, "software-requirement", "software-qualification-test",
                                  "no software qualification test verifies it")

    def cov_15(self, rule):
        self.need_incoming(rule, "system-interface", "verifies", ["system-integration-test"],
                           "no system integration test verifies it")

    def cov_16(self, rule):
        self.verified_or_reviewed(rule, "system-requirement", "system-qualification-test",
                                  "no system qualification test verifies it")

    def tests_in_scope(self):
        return [t for t in self.of_type(*TEST_TYPES)
                if self.live(t) and (self.scope is None or TEST_TYPES[t.type][0] in self.scope)]

    def cov_17(self, rule):
        for test in self.tests_in_scope():
            targets = [self.items[t] for t, _ in test.targets("verifies") if t in self.items]
            if not [t for t in targets if self.live(t)]:
                self.gap(rule, test, "verifies nothing that is still valid")

    def cov_18(self, rule):
        for test in self.tests_in_scope():
            level, step = TEST_TYPES[test.type][1], test.front.get("step")
            if test.type in LEVEL_OF_TEST and step:
                run = latest([r for r in self.of_type("test-run") if r.status == "final" and r.front.get("level") == level
                              and self.build_step(r, LEVEL_OF_TEST[test.type]) == step])
                if run is None:
                    self.gap(rule, test, "no final test run of level %s on a build of step '%s' exists" % (level, step))
                    continue
            else:
                run = self.latest_run("test-run", level=level)
            if run is None:
                self.gap(rule, test, "no final test run of level %s exists" % level)
                continue
            entry = next((e for e in as_list(run.front.get("results"))
                          if isinstance(e, dict) and e.get("test") == test.id), None)
            if entry is None:
                self.gap(rule, test, "no verdict in the latest final test run %s" % run.id)
            elif entry["verdict"] in ("not-run", "blocked") and not entry.get("reason"):
                self.gap(rule, test, "%s in %s without a reason" % (entry["verdict"], run.id))
            elif entry["verdict"] == "failed":
                self.failed_case(rule, test, run, entry)

    def failed_case(self, rule, test, run, entry):
        """A failed verdict in the latest run stays visible until a run passes it: as an error while no
        problem report names the case, an item it verifies or the run; as a warning while that report is
        unresolved; as information once it is resolved."""
        names = {test.id, run.id} | {t for t, _ in test.targets("verifies")}
        reports = [p for p in self.of_type("problem-report") if p.status != "rejected"
                   and ({t for t, _ in p.targets("affects")} & names or run.id in str(p.front.get("found_in") or ""))]
        why = (" (%s)" % " ".join(str(entry.get("reason")).split())[:120]) if entry.get("reason") else ""
        supports = self.own_supports(rule, test)
        if not reports:
            self.add("error", rule, test.id, "failed in %s%s; no problem report names the case, what it verifies or the run"
                     % (run.id, why), supports)
            return
        open_ = [p for p in reports if p.status in UNRESOLVED]
        self.add("warning" if open_ else "info", rule, test.id, "failed in %s%s; %s" % (run.id, why, ", ".join(
            "%s %s" % (p.id, p.status) for p in (open_ or reports))), supports)

    def cov_19(self, rule):
        for item in self.items.values():
            if self.types.get(item.type, {}).get("lifecycle") != "engineering":
                continue
            if item.status in ("draft", "in-review"):
                # not approved yet: say what the last review of this content left open
                reviews = self.reviews_of(item)
                opened = [str(f.get("id")) for f in as_list(reviews[-1].front.get("findings")) if isinstance(f, dict)
                          and f.get("state") == "open" and f.get("item") in (None, item.id)] if reviews else []
                if opened:
                    self.gap(rule, item, fallback="subject", message="review %s left findings open: %s" % (reviews[-1].id, ", ".join(opened)))
                continue
            if item.status != "approved":
                continue
            review = self.approving_review(item)
            if review is None:
                older = [r.id for r in self.of_type("review-record")
                         if any(isinstance(e, dict) and e.get("item") == item.id for e in as_list(r.front.get("subject")))]
                self.gap(rule, item, fallback="subject", message="stale approval: content changed since review %s (current hash %s)"
                         % (", ".join(older), item.hash) if older else
                         "approved, but no final review record covers it (current hash %s)" % item.hash)
                continue
            opened = [str(f.get("id")) for f in as_list(review.front.get("findings"))
                      if isinstance(f, dict) and f.get("state") == "open" and f.get("item") in (None, item.id)]
            if opened:
                self.gap(rule, item, fallback="subject", message="review %s still has open findings: %s" % (review.id, ", ".join(opened)))
            closed = {str(f.get("closes")) for rev in self.reviews_of(item) for f in as_list(rev.front.get("findings"))
                      if isinstance(f, dict) and f.get("closes") and f.get("state") == "closed"}
            left = ["%s#%s" % (rev.id, f.get("id")) for rev in self.reviews_of(item) if rev.id != review.id
                    for f in as_list(rev.front.get("findings"))
                    if isinstance(f, dict) and f.get("state") == "open" and f.get("item") in (None, item.id)]
            left = [ref for ref in left if ref not in closed]
            if left:
                self.gap(rule, item, fallback="subject", message="approved by %s although findings of an earlier review of the same content are "
                         "open and not closed by a later finding entry: %s" % (review.id, ", ".join(left)))

    def cov_20(self, rule):
        for request in self.of_type("change-request"):
            if request.status not in ("submitted", "rejected") and not request.targets("affects"):
                self.add("error", rule, request.id, "state %s, but no affects link" % request.status,
                         self.rules[rule]["supports"])

    def cov_21(self, rule):
        for interface in self.of_type("software-interface"):
            provider = self.items.get(str(interface.front.get("provided_by")))
            if not self.live(interface) or provider is None or provider.front.get("origin") != "developed":
                continue
            units = [u for u in self.sources(interface.id, "realizes", ["software-unit"])
                     if (provider.id, None) in u.targets("part_of")]
            if not units:
                self.gap(rule, interface, "no software unit of its provider %s realizes it" % provider.id)

    def cov_22(self, rule):
        """Designed functions against the C code: existence both ways, and the signature
        wherever the design gives the types (argument `type`, `return_type` or one `type`
        shared by all `returns` entries)."""
        for unit in self.of_type("software-unit"):
            if not self.live(unit) or unit.front.get("origin") in ("generated", "third-party"):
                continue
            code = ""
            for path in as_list(unit.front.get("source_files")):
                file = self.root / str(path)
                if file.is_file() and file.suffix == ".c":
                    code += C_COMMENT.sub(" ", file.read_text(encoding="utf-8", errors="replace")) + "\n"
            if not code:
                continue
            designed = [f for f in as_list(unit.front.get("functions")) if isinstance(f, dict)]
            for function in designed:
                if function.get("category") in ("public", "scheduled", "callback") and not re.search(
                        r"\b%s\s*\([^;{}]*\)\s*\{" % re.escape(str(function.get("name"))), code):
                    self.gap(rule, unit, "designed function %s is not defined in its source files" % function.get("name"))
            names = {f.get("name") for f in designed}
            for name in sorted(set(C_DEFINITION.findall(code)) - names):
                self.gap(rule, unit, "function %s is defined in the code but not in the design" % name)
            everything = code
            for path in as_list(unit.front.get("source_files")):
                file = self.root / str(path)
                if file.is_file() and file.suffix == ".h":
                    everything += C_COMMENT.sub(" ", file.read_text(encoding="utf-8", errors="replace")) + "\n"
            coded = c_signatures(everything)
            for function in designed:
                if function.get("name") not in coded:
                    continue
                code_returns, code_types = coded[function["name"]]
                arguments = [a for a in as_list(function.get("arguments")) if isinstance(a, dict)]
                if all(a.get("type") for a in arguments):
                    wanted = [c_type(a["type"]) for a in arguments]
                    if wanted != code_types:
                        self.gap(rule, unit, "parameters of %s differ: design (%s), code (%s)"
                                 % (function["name"], ", ".join(wanted) or "void", ", ".join(code_types) or "void"))
                stated = {str(r.get("type")) for r in as_list(function.get("returns")) if isinstance(r, dict) and r.get("type")}
                wanted = function.get("return_type") or (stated.pop() if len(stated) == 1 else None)
                if wanted and "(" not in code_returns and c_type(wanted) != code_returns:
                    self.gap(rule, unit, "return type of %s differs: design %s, code %s"
                             % (function["name"], c_type(wanted), code_returns))

    def cov_23(self, rule):
        decided = {t for d in self.of_type("design-decision") if d.status == "approved" for t, _ in d.targets("concerns")}

        def rank(item):
            return ASIL_ORDER.get(str(item.front.get("asil")))

        def compare(item, other, relation):
            if rank(item) is None or rank(other) is None or rank(item) >= rank(other) or item.id in decided:
                return
            self.gap(rule, item, "ASIL %s is lower than ASIL %s of %s (%s); needs an approved design decision"
                     % (item.front.get("asil"), other.front.get("asil"), other.id, relation))

        for item in self.items.values():
            if not self.live(item) or item.imported:
                continue
            for role, relation in (("derived_from", "derived from it"), ("implements", "implements it"),
                                   ("verifies", "verifies it")):
                for target, _ in item.targets(role):
                    if target in self.items:
                        compare(item, self.items[target], relation)
            if item.type == "software-unit":
                for target, _ in item.targets("part_of"):
                    if target in self.items:
                        compare(item, self.items[target], "is part of it")
            if item.type in ("software-component", "software-interface", "system-element", "system-interface"):
                for req in self.allocated_requirements(item.id):
                    compare(item, req, "is allocated to this item")

    def cov_24(self, rule):
        for view in self.of_type("architecture-view"):
            if not self.live(view):
                continue
            shown = [self.items[t] for t, _ in view.targets("shows") if t in self.items]
            if not shown:
                self.gap(rule, view, "shows nothing")
            for target in shown:
                if not self.live(target):
                    self.gap(rule, view, "shows %s, which is %s" % (target.id, target.status))

    def cov_25(self, rule):
        waived = (self.config.get("trace") or {}).get("views_not_applicable") or {}
        kinds = {v.front.get("kind") for v in self.of_type("architecture-view")
                 if v.status == "approved" and v.front.get("level") == "software"}
        wanted = [("structure",), ("execution-model",), ("resource-summary",), ("state-machine", "sequence")]
        for group in wanted:
            if not (set(group) & kinds) and not all(k in waived for k in group):
                self.add("error", rule, "project", "no approved software-level architecture view of kind %s"
                         % " or ".join(group), self.rules[rule]["supports"])

    def cov_31(self, rule):
        supports = self.rules[rule]["supports"]
        packages = [p for p in self.of_type("work-package") if self.live(p)]
        for package in packages:
            if len(package.targets("part_of")) > 1:
                self.add("error", rule, package.id, "part of more than one work package", supports)
        for role in ("part_of", "depends_on"):
            graph = {p.id: [t for t, _ in p.targets(role) if t in self.items] for p in packages}
            for start in graph:
                seen, stack = set(), list(graph[start])
                while stack:
                    current = stack.pop()
                    if current == start:
                        self.add("error", rule, start, "its %s links lead back to it" % role, supports)
                        break
                    if current not in seen:
                        seen.add(current)
                        stack.extend(graph.get(current, []))

    def cov_32(self, rule):
        delivered = {t for p in self.of_type("work-package") if self.live(p) for t, _ in p.targets("delivers")}
        for item in self.items.values():
            if self.types.get(item.type, {}).get("lifecycle") != "engineering" or item.type == "work-package" \
                    or item.imported or not self.live(item):
                continue
            refs = self.schema["plan_kinds"].get(item.front.get("kind"), []) if item.type == "plan" \
                else self.types[item.type].get("supports") or []
            if self.in_scope(refs) and item.id not in delivered:
                self.gap(rule, item, "no work package delivers it")

    def cov_33(self, rule):
        have = {p.front.get("category") for p in self.of_type("work-package") if self.live(p)}
        missing = [c for c in ("engineering", "management", "support") if c not in have]
        if missing:
            self.add("error", rule, "project", "no work package of category %s" % ", ".join(missing),
                     self.rules[rule]["supports"])

    def cov_34(self, rule):
        for package in self.of_type("work-package"):
            if not self.live(package):
                continue
            start, finish = as_date(package.front.get("planned_start")), as_date(package.front.get("planned_finish"))
            if start and finish and finish < start:
                self.gap(rule, package, "planned finish %s is before planned start %s" % (finish, start))
            for parent_id, _ in package.targets("part_of"):
                parent = self.items.get(parent_id)
                end = as_date(parent.front.get("planned_finish")) if parent else None
                if finish and end and finish > end:
                    self.gap(rule, package, "planned to finish %s, after %s, which it is part of (%s)" % (finish, parent_id, end))
            for before_id, _ in package.targets("depends_on"):
                before = self.items.get(before_id)
                end = as_date(before.front.get("planned_finish")) if before else None
                if start and end and end > start:
                    self.gap(rule, package, "planned to start %s, before %s it depends on finishes (%s)" % (start, before_id, end))
            for activity in as_list(package.front.get("activities")):
                end = as_date(activity.get("planned_finish")) if isinstance(activity, dict) else None
                if end and finish and end > finish:
                    self.gap(rule, package, "activity '%s' finishes %s, after the work package (%s)"
                             % (activity.get("name"), end, finish))

    def cov_35(self, rule):
        self.check_integration_plan(rule, "software")

    def cov_36(self, rule):
        self.check_integration_builds(rule, "software")

    def cov_37(self, rule):
        self.check_integration_tests(rule, "software")

    def cov_38(self, rule):
        self.check_integration_runs(rule, "software")

    def cov_46(self, rule):
        self.check_integration_plan(rule, "system")

    def cov_47(self, rule):
        self.check_integration_builds(rule, "system")

    def cov_48(self, rule):
        self.check_integration_tests(rule, "system")

    def cov_49(self, rule):
        self.check_integration_runs(rule, "system")

    def integrated_elements(self, level):
        """The elements a strategy of the level has to account for: no compositions, no external systems."""
        spec = INTEGRATION_LEVELS[level]
        skip = ("composition",) if level == "software" else ("external",)
        return [e for e in self.of_type(spec["element"]) if self.live(e) and e.front.get("kind") not in skip]

    def check_integration_plan(self, rule, level):
        spec = INTEGRATION_LEVELS[level]
        supports, plan = self.rules[rule]["supports"], self.integration_plan(level)
        if plan is None:
            return                                        # COV-27 reports the missing plan
        steps = self.integration_steps(plan)
        names = [str(s.get("name")) for s in steps]
        for name in sorted({n for n in names if names.count(n) > 1}):
            self.add("error", rule, plan.id, "step name '%s' is used twice" % name, supports)
        added = defaultdict(list)
        for n, step in enumerate(steps):
            for key in ("components", "doubles"):
                for entry in as_list(step.get(key)):
                    item = self.items.get(str(entry))
                    if item is None or item.type != spec["element"] or not self.live(item):
                        self.add("error", rule, plan.id, "step '%s' names %s under %s, which is not a live %s"
                                 % (step.get("name"), entry, key, spec["element"].replace("-", " ")), supports)
            for entry in as_list(step.get("components")):
                for leaf in self.leaves(entry):
                    added[leaf].append((n, str(step.get("name"))))
            for entry in as_list(step.get("doubles")):
                for leaf in self.leaves(entry):
                    earlier = [name for m, name in added[leaf] if m <= n]
                    if earlier:
                        self.add("error", rule, plan.id, "step '%s' names %s as a double, but step '%s' integrates it"
                                 % (step.get("name"), leaf, earlier[0]), supports)
        last_doubles = {leaf for entry in as_list(steps[-1].get("doubles")) for leaf in self.leaves(entry)} \
            if steps else set()
        for element in self.integrated_elements(level):
            if len(added[element.id]) > 1:
                self.add("error", rule, element.id, "integrated in more than one step of %s: %s"
                         % (plan.id, ", ".join(name for _, name in added[element.id])), supports)
            elif not added[element.id] and element.id not in last_doubles:
                self.add("error", rule, element.id, "integrated in no step of %s, and not named as a double of its last "
                         "step" % plan.id, supports)

    def check_integration_builds(self, rule, level):
        supports, plan = self.rules[rule]["supports"], self.integration_plan(level)
        steps = self.integration_steps(plan)
        for n, step in enumerate(steps):
            name, expected = str(step.get("name")), self.integrated_up_to(steps, n)
            if level == "software":
                coded = {cid: [u.id for u in self.sources(cid, "part_of", ["software-unit"])
                               if as_list(u.front.get("source_files"))] for cid in expected}
                developed = [c for c in expected if self.items[c].front.get("origin") == "developed"]
                pending = bool(developed) and not any(coded[c] for c in developed)
            else:
                coded, developed, pending = {}, [], False
            build = latest(self.builds_of(name, level=level))
            if build is None:
                if pending:
                    self.add("warning", rule, plan.id, "step '%s' has no final build record (pending: no unit of the "
                             "step has code yet)" % name, supports)
                else:
                    self.add("error", rule, plan.id, "step '%s' has no final build record" % name, supports)
                continue
            if build.front.get("result") != "succeeded":
                self.add("error", rule, plan.id, "the latest build %s of step '%s' failed" % (build.id, name), supports)
                continue
            contents = {str(e.get("component")): e for e in as_list(build.front.get("contents")) if isinstance(e, dict)}
            for cid in expected:
                if cid in developed and not coded[cid]:
                    continue                              # no code yet: COV-10 says so for its units
                if cid not in contents:
                    self.add("error", rule, plan.id, "the latest build %s of step '%s' does not contain %s"
                             % (build.id, name, cid), supports)
                    continue
                missing = [u for u in coded.get(cid, []) if u not in map(str, as_list(contents[cid].get("units")))]
                if cid in developed and missing:
                    self.add("error", rule, plan.id, "the latest build %s of step '%s' does not contain %s of %s"
                             % (build.id, name, ", ".join(missing), cid), supports)
            if level == "system":
                self.check_software_in_system_build(rule, plan, name, build, contents, supports)
                continue
            for entry in as_list(build.front.get("sources")):
                if not isinstance(entry, dict):
                    continue
                file = self.root / str(entry.get("file"))
                if not file.is_file():
                    self.add("error", rule, plan.id, "%s, built by %s for step '%s', no longer exists: the build does "
                             "not describe the current software" % (entry.get("file"), build.id, name), supports)
                elif file_hash(file) != str(entry.get("hash")):
                    self.add("error", rule, plan.id, "%s changed after build %s of step '%s': the integrated software "
                             "is older than the code" % (entry.get("file"), build.id, name), supports)
            built = {Path(str(e.get("file"))).as_posix() for e in as_list(build.front.get("sources")) if isinstance(e, dict)}
            for cid in developed:
                for unit_id in coded[cid]:
                    for path in as_list(self.items[unit_id].front.get("source_files")):
                        if Path(str(path)).as_posix() not in built and str(path).endswith(".c"):
                            self.add("error", rule, plan.id, "build %s of step '%s' did not build %s of %s"
                                     % (build.id, name, path, unit_id), supports)

    def check_software_in_system_build(self, rule, plan, name, build, contents, supports):
        """A system build that integrates software names the software build; it has to be the latest one."""
        software_steps = self.integration_steps(level="software")
        for cid, entry in sorted(contents.items()):
            ref = entry.get("build")
            if not ref:
                continue
            software = self.items.get(str(ref))
            if software is None or software.type != "build-record" or software.status != "final" \
                    or (software.front.get("level") or "software") != "software":
                self.add("error", rule, plan.id, "build %s of step '%s' names %s for %s, which is not a final software "
                         "build record" % (build.id, name, ref, cid), supports)
                continue
            if software.front.get("result") != "succeeded":
                self.add("error", rule, plan.id, "build %s of step '%s' integrates %s, a software build that failed"
                         % (build.id, name, ref), supports)
            if software_steps and software.front.get("step") == software_steps[-1].get("name"):
                newest = latest(self.builds_of(software.front.get("step"), succeeded=True))
                if newest is not None and newest.id != software.id:
                    self.add("error", rule, plan.id, "build %s of step '%s' integrates software build %s; the latest "
                             "software build is %s: the system build is older than the software"
                             % (build.id, name, ref, newest.id), supports)

    def check_integration_tests(self, rule, level):
        spec = INTEGRATION_LEVELS[level]
        plan = self.integration_plan(level)
        names = [str(s.get("name")) for s in self.integration_steps(plan)]
        tests = [t for t in self.of_type(spec["test"]) if self.live(t)]
        for test in tests:
            step = test.front.get("step")
            if step in (None, ""):
                continue                                  # SCHEMA reports it once it is due
            if plan is None:
                self.gap(rule, test, "names step '%s', but no approved %s plan exists" % (step, spec["kind"]))
            elif str(step) not in names:
                self.gap(rule, test, "names step '%s', which %s does not have (steps: %s)"
                         % (step, plan.id, ", ".join(names)))
        for name in names:
            if not any(str(t.front.get("step")) == name for t in tests):
                self.add("error", rule, plan.id, "no %s integration test belongs to step '%s'" % (spec["name"], name),
                         self.rules[rule]["supports"])

    def check_integration_runs(self, rule, level):
        spec = INTEGRATION_LEVELS[level]
        plan = self.integration_plan(level)
        steps = self.integration_steps(plan)
        runs = [r for r in self.of_type("test-run") if r.status == "final"]

        def judge(run, step_name, practice):
            build = self.items.get(str(run.front.get("build") or ""))
            if build is None or build.type != "build-record" or build.status != "final" \
                    or (build.front.get("level") or "software") != level:
                self.add("error", rule, run.id, "names %s: which integrated %s was tested is not recorded by a final "
                         "%s build record" % (run.front.get("build") or "no build", spec["name"], spec["name"]), [practice])
                return
            problems = []
            if build.front.get("result") != "succeeded":
                problems.append("tested %s, a build that failed" % build.id)
            if step_name and build.front.get("step") != step_name:
                problems.append("tested %s of step '%s', expected a build of step '%s'"
                                % (build.id, build.front.get("step"), step_name))
            if str(build.front.get("item_under_test")) != str(run.front.get("item_under_test")):
                problems.append("tested %s, built from %s, but names %s as item under test"
                                % (build.id, build.front.get("item_under_test"), run.front.get("item_under_test")))
            newest = latest(self.builds_of(build.front.get("step"), succeeded=True, level=level))
            if not problems and newest is not None and newest.id != build.id:
                problems.append("tested %s; the latest build of step '%s' is %s: the run does not describe it"
                                % (build.id, build.front.get("step"), newest.id))
            for text in problems:
                self.add("error", rule, run.id, text, [practice])

        integration = [r for r in runs if r.front.get("level") == spec["integration"]]
        for step in steps:
            run = latest([r for r in integration if self.build_step(r, level) == step.get("name")])
            if run is not None:
                judge(run, step.get("name"), spec["practices"][0])
        newest = latest(integration)
        if newest is not None and self.build_step(newest, level) is None:
            judge(newest, None, spec["practices"][0])
        qualification = self.latest_run("test-run", level=spec["qualification"])
        if qualification is not None and steps:
            judge(qualification, steps[-1].get("name"), spec["practices"][1])

    def cov_39(self, rule):
        plan = self.problem_plan()
        if plan is None:
            return                                        # COV-27 reports the missing plan
        urgent = [str(s) for s in as_list(plan.front.get("urgent_severities"))]
        allowed = self.types["problem-report"]["attributes"]["severity"]["values"]
        for severity in urgent:
            if severity not in allowed:
                self.add("error", rule, plan.id, "urgent_severities names %s, which is not a severity (%s)"
                         % (severity, ", ".join(allowed)), self.rules[rule]["supports"])
        for problem in self.of_type("problem-report"):
            if self.live(problem) and str(problem.front.get("severity")) in urgent \
                    and not isinstance(problem.front.get("urgent_action"), dict):
                self.problem_gap(rule, problem, "severity %s is urgent by %s, but no urgent_action records what was "
                                 "authorised, by whom and when" % (problem.front.get("severity"), plan.id))

    def cov_40(self, rule):
        plan = self.problem_plan()
        if plan is None:
            return
        alert_rules = [r for r in as_list(plan.front.get("alerts")) if isinstance(r, dict)]
        told = defaultdict(set)
        for record in self.of_type("communication-record"):
            if record.status == "final":
                for subject in as_list(record.front.get("subject")):
                    told[str(subject)] |= {str(a).strip().lower() for a in as_list(record.front.get("audience"))}
        for problem in self.of_type("problem-report"):
            if not self.live(problem):
                continue
            for alert in alert_rules:
                if str(alert.get("severity")) != str(problem.front.get("severity")):
                    continue
                missing = [str(a) for a in as_list(alert.get("audience")) if str(a).strip().lower() not in told[problem.id]]
                if missing:
                    self.problem_gap(rule, problem, "severity %s: no final communication record alerts %s, as %s asks"
                                     % (problem.front.get("severity"), ", ".join(missing), plan.id))

    def cov_41(self, rule):
        internal = as_list((self.config.get("trace") or {}).get("internal_baselines"))
        baselined = {str(e.get("item")) for b in self.of_type("baseline")
                     if b.status == "final" and b.front.get("purpose") not in internal
                     for e in as_list(b.front.get("items")) if isinstance(e, dict)}
        for problem in self.of_type("problem-report"):
            if problem.status not in ("in-resolution", "resolved", "closed"):
                continue
            hit = [target for target, _ in problem.targets("affects") if target in baselined]
            if hit and not self.sources(problem.id, "resolves", ["change-request"]):
                self.gap(rule, problem, "affects %s, which a baseline lists, but no change request resolves it"
                         % ", ".join(hit))

    def cov_42(self, rule):
        for problem in self.of_type("problem-report"):
            if problem.status != "closed":
                continue
            closure = problem.front.get("closure")
            if isinstance(closure, dict):
                for ref in as_list(closure.get("evidence")):
                    record = self.items.get(str(ref))
                    if record is None or record.type not in ("test-run", "review-record") or record.status != "final":
                        self.gap(rule, problem, "closure evidence %s is not a final test run or review record" % ref)
            for change in self.sources(problem.id, "resolves", ["change-request"]):
                if change.status != "closed":
                    self.gap(rule, problem, "closed, but %s, which resolves it, is %s" % (change.id, change.status))

    def cov_43(self, rule):
        plan = self.quality_plan()
        checks = [c for c in as_list(plan.front.get("quality_checks")) if isinstance(c, dict)] if plan else []
        records = [r for r in self.of_type("quality-record") if r.status == "final"]
        for base in self.of_type("baseline"):
            if base.status != "final":
                continue
            created = as_date(str(base.front.get("created_at") or "")[:10])
            for check in checks:
                if base.front.get("purpose") not in map(str, as_list(check.get("before"))):
                    continue
                done = [r for r in records if r.front.get("check") == check.get("name")
                        and as_date(r.front.get("checked_at")) and (created is None or as_date(r.front.get("checked_at")) <= created)
                        and written_before(r.front.get("recorded_at"), base.front.get("created_at"))]
                if not done:
                    self.add("error", rule, base.id, "no final quality record of check '%s' was made before this %s "
                             "baseline, as %s asks" % (check.get("name"), base.front.get("purpose"), plan.id),
                             self.rules[rule]["supports"])

    def cov_44(self, rule):
        for record in self.of_type("quality-record"):
            if record.status != "final":
                continue
            for finding in as_list(record.front.get("findings")):
                action = self.items.get(str(finding.get("action"))) if isinstance(finding, dict) else None
                if action is None or action.type not in ("corrective-action", "problem-report"):
                    self.add("error", rule, record.id, "finding %s names %s as its action, which is no corrective action "
                             "or problem report" % (finding.get("id") if isinstance(finding, dict) else finding,
                                                   finding.get("action") if isinstance(finding, dict) else None),
                             self.rules[rule]["supports"])

    def cov_45(self, rule):
        told = {str(s) for c in self.of_type("communication-record") if c.status == "final"
                for s in as_list(c.front.get("subject"))}
        for record in self.of_type("quality-record"):
            if record.status == "final" and record.front.get("kind") == "summary" and record.id not in told:
                self.add("error", rule, record.id, "no final communication record names this quality report",
                         self.rules[rule]["supports"])

    def risk_numbers(self, risk):
        try:
            return int(risk.front.get("probability")), int(risk.front.get("impact"))
        except (TypeError, ValueError):
            return None, None

    def cov_50(self, rule):
        plan = self.risk_plan()
        if plan is None:
            return
        scale = plan.front.get("risk_scale") if isinstance(plan.front.get("risk_scale"), dict) else {}
        categories = [str(c) for c in as_list(plan.front.get("risk_categories"))]
        for risk in self.of_type("risk"):
            if risk.status in ("identified", "rejected"):
                continue
            probability, impact = self.risk_numbers(risk)
            if probability is None or not 1 <= probability <= int(scale.get("probability_levels") or 0):
                self.gap(rule, risk, "probability %r is outside 1 to %s of %s"
                         % (risk.front.get("probability"), scale.get("probability_levels"), plan.id))
            if impact is None or not 1 <= impact <= int(scale.get("impact_levels") or 0):
                self.gap(rule, risk, "impact %r is outside 1 to %s of %s" % (risk.front.get("impact"),
                                                                           scale.get("impact_levels"), plan.id))
            if str(risk.front.get("category")) not in categories:
                self.gap(rule, risk, "category %s is not one of %s: %s" % (risk.front.get("category"), plan.id,
                                                                          ", ".join(categories)))

    def cov_51(self, rule):
        plan = self.risk_plan()
        scale = plan.front.get("risk_scale") if plan and isinstance(plan.front.get("risk_scale"), dict) else {}
        if not scale.get("acceptable_up_to"):
            return
        for risk in self.of_type("risk"):
            if risk.status in ("identified", "rejected", "closed", "in-treatment"):
                continue
            probability, impact = self.risk_numbers(risk)
            if probability is None or impact is None or probability * impact <= int(scale["acceptable_up_to"]):
                continue
            if risk.status == "accepted" and risk.front.get("decision"):
                continue
            self.gap(rule, risk, "exposure %d is above %s of %s: the risk needs treatment, or a decision that names "
                     "who accepted it" % (probability * impact, scale["acceptable_up_to"], plan.id))

    def cov_52(self, rule):
        for risk in self.of_type("risk"):
            if risk.status == "in-treatment" and not [i for i in as_list(risk.front.get("indicators"))
                                                      if isinstance(i, dict) and i.get("threshold") not in (None, "")]:
                self.gap(rule, risk, "in treatment, but no indicator with a threshold shows whether the treatment works")

    def cov_26(self, rule):
        internal = as_list((self.config.get("trace") or {}).get("internal_baselines"))
        told = set()
        for record in self.of_type("communication-record"):
            if record.status == "final":
                told |= {str(s) for s in as_list(record.front.get("subject"))}
        for base in self.of_type("baseline"):
            if base.status == "final" and base.front.get("purpose") not in internal and base.id not in told:
                self.add("error", rule, base.id, "no final communication record names this baseline",
                         self.rules[rule]["supports"])

    def cov_27(self, rule):
        have = {p.front.get("kind") for p in self.of_type("plan") if p.status == "approved"}
        for kind, practices in self.schema["plan_kinds"].items():
            needed = [bp for bp in practices if self.covers(process_of(bp))]
            if needed and kind not in have:
                self.add("error", rule, "project", "no approved plan of kind %s" % kind, needed)

    def cov_28(self, rule):
        plans = [p for p in self.of_type("plan") if p.status == "approved" and p.front.get("kind") == "unit-verification"]
        targets = (plans[0].front.get("coverage_targets") or {}) if plans else {}
        if plans and not targets:
            self.add("warning", rule, plans[0].id, "the plan sets no coverage_targets: structural coverage is not assessed",
                     self.rules[rule]["supports"])
        run = self.latest_run("test-run", level="unit")
        measured = (run.front.get("coverage") if run else None) or []
        by_unit = {c.get("unit"): c for c in measured if isinstance(c, dict)} if isinstance(measured, list) else {}
        for unit in self.of_type("software-unit"):
            target = targets.get(str(unit.front.get("asil")))
            if not self.live(unit) or not target or unit.front.get("origin") in ("generated", "third-party"):
                continue
            entry = by_unit.get(unit.id)
            if entry is None:
                why = measured if isinstance(measured, str) else "no entry for the unit"
                self.unit_gap(rule, unit, "structural coverage not measured in %s (%s)" % (run.id, why)
                              if run else "no final unit test run exists, so structural coverage is not measured")
                continue
            for metric, wanted in sorted(target.items()):
                got = entry.get(metric)
                if (got is None or got < wanted) and not entry.get("deviation"):
                    self.gap(rule, unit, "%s is %s in %s, target for ASIL %s is %s"
                             % (metric, "not reported" if got is None else got, run.id, unit.front.get("asil"), wanted))

    def cov_29(self, rule):
        for unit in self.of_type("software-unit"):
            if not self.live(unit) or unit.front.get("origin") in ("generated", "third-party"):
                continue
            named = {anchor for test in self.sources(unit.id, "verifies", ["unit-test"])
                     for target, anchor in test.targets("verifies") if target == unit.id and anchor}
            for function in as_list(unit.front.get("functions")):
                if isinstance(function, dict) and function.get("category") in ("public", "scheduled", "callback") \
                        and function.get("name") not in named:
                    self.unit_gap(rule, unit, "no unit test verifies %s#%s" % (unit.id, function.get("name")))

    def cov_30(self, rule):
        supports = self.rules[rule]["supports"]
        recorded = {}
        for run in (self.latest_run("test-run", level="unit"), self.latest_run("static-analysis-run")):
            if run is None:
                continue
            sources = run.front.get("sources")
            if not sources:
                self.add("warning", rule, run.id, "records no source hashes: whether the code changed after this run "
                         "cannot be told", supports)
                continue
            recorded[run.id] = {Path(str(s.get("file"))).as_posix(): str(s.get("hash"))
                                for s in as_list(sources) if isinstance(s, dict)}

        def compare(item, path):
            file = self.root / str(path)
            if not file.is_file():
                return                                    # a missing file is reported by its own rule
            name, now = Path(str(path)).as_posix(), file_hash(file)
            for run_id, hashes in sorted(recorded.items()):
                if name in hashes and hashes[name] != now:
                    self.gap(rule, item, "%s changed after %s: that run does not describe the current code" % (name, run_id))
                elif name not in hashes and item.type == "software-unit":
                    self.gap(rule, item, "%s is not among the sources %s recorded" % (name, run_id))

        for unit in self.of_type("software-unit"):
            if self.live(unit) and unit.front.get("origin") not in ("generated", "third-party"):
                for path in as_list(unit.front.get("source_files")):
                    compare(unit, path)
        for test in self.of_type("unit-test"):
            if self.live(test) and test.front.get("script"):
                compare(test, str(test.front["script"]).partition("::")[0])

    def check_consistency_evidence(self):
        """Suspect links and missing consistency evidence, from the references of approving reviews."""
        for item in self.items.values():
            if self.types.get(item.type, {}).get("lifecycle") != "engineering" or item.status != "approved" or item.imported:
                continue
            review = self.approving_review(item)
            if review is None:
                continue                                  # already reported by COV-19
            # items reviewed together in the same record were compared with each other as well
            seen = {e.get("item"): str(e.get("hash"))
                    for name in ("references", "subject")
                    for e in as_list(review.front.get(name)) if isinstance(e, dict)}
            files = as_list(item.front.get("source_files")) if item.type == "software-unit" else []
            if files and self.in_scope(["SWE.3.BP6"]):
                covered = {Path(str(s.get("file"))).as_posix(): str(s.get("hash"))
                           for s in as_list(review.front.get("sources")) if isinstance(s, dict)}
                for path in files:
                    name, file = Path(str(path)).as_posix(), self.root / str(path)
                    if not file.is_file():
                        continue
                    if name not in covered:
                        self.add("warning", "CONSISTENCY", item.id, "review %s does not record %s: a review of the "
                                 "code against the design is not evidenced" % (review.id, name), ["SWE.3.BP6"])
                    elif covered[name] != file_hash(file):
                        self.add("error", "SUSPECT", item.id, "%s changed after review %s: the code is no longer the "
                                 "code that was reviewed" % (name, review.id), ["SWE.3.BP6"])
            for target_id, role in self.dependencies(item):
                target, supports = self.items.get(target_id), self.supports_of(item, role)
                if target is None or not self.in_scope(supports):
                    continue
                if target_id not in seen:
                    self.add("warning", "CONSISTENCY", item.id, "review %s does not record %s (%s) as a reference: "
                             "consistency with it is not evidenced" % (review.id, target_id, role), supports)
                elif seen[target_id] != target.hash:
                    if self.unsettled(target):
                        continue                          # reported as UPSTREAM until the target is approved again
                    self.add("error", "SUSPECT", item.id, "suspect link: %s (%s) changed after review %s"
                             % (target_id, role, review.id), supports)

    def check_upstream(self):
        """An approved item cannot be more settled than what it builds on; open queries stay visible."""
        for item in self.items.values():
            if self.types.get(item.type, {}).get("lifecycle") != "engineering" or item.status != "approved" or item.imported:
                continue
            for target_id, role in self.dependencies(item):
                target, supports = self.items.get(target_id), self.supports_of(item, role)
                if target is None or not self.in_scope(supports):
                    continue
                if self.unsettled(target):
                    self.add("error", "UPSTREAM", item.id, "approved, but %s (%s) is in state %s"
                             % (target_id, role, target.status), supports)
        for query in self.of_type("query"):
            if query.status != "open":
                continue
            sent = "" if query.front.get("asked_at") else " (not put to its source yet)"
            for target_id, _ in query.targets("about"):
                target = self.items.get(target_id)
                if target is not None and target.status == "approved":
                    self.add("warning", "QUERY", target_id, "open query %s%s is about this approved item" % (query.id, sent))
        for problem in self.of_type("problem-report"):
            if problem.status not in UNRESOLVED:
                continue
            for target_id, _ in problem.targets("affects"):
                target = self.items.get(target_id)
                if target is not None and target.status == "approved":
                    self.add("warning", "PROBLEM", target_id, "problem report %s (%s, %s) concerns this approved item"
                             % (problem.id, problem.front.get("severity"), problem.status))


    def cov_74(self, rule):
        internal = as_list((self.config.get("trace") or {}).get("internal_baselines"))
        told = {}
        for record in self.of_type("communication-record"):
            if record.status == "final":
                for subject in as_list(record.front.get("subject")):
                    told.setdefault(str(subject), []).append(record)
        for release in self.of_type("release"):
            if release.status != "final":
                continue
            base = self.items.get(str(release.front.get("baseline")))
            if base is None or base.type != "baseline" or base.status != "final":
                self.add("error", rule, release.id, "names baseline %s, which is not a final baseline" % release.front.get("baseline"),
                         self.rules[rule]["supports"])
            elif base.front.get("purpose") in internal:
                self.add("error", rule, release.id, "is built from %s, an internal baseline" % base.id, self.rules[rule]["supports"])
            notices = told.get(release.id, [])
            if not notices:
                self.add("error", rule, release.id, "no final communication record names the release as delivered",
                         self.rules[rule]["supports"])
            elif not any(n.front.get("agreement") for n in notices):
                self.add("warning", rule, release.id, "delivered (%s), but no record states the receipt under agreement"
                         % ", ".join(n.id for n in notices), self.rules[rule]["supports"])

    def cov_75(self, rule):
        plan = self.plan_in_work("safety")
        entry = self.safety_entries(plan, "safety_activities", "clause").get("8:12") if plan else None
        waived = bool(entry and entry.get("decision") in ("not-applicable", "by-customer") and entry.get("rationale"))
        limited = {str(i) for i in as_list(entry.get("items"))} if entry else set()
        for component in self.of_type("software-component"):
            if not self.live(component) or component.front.get("origin") not in ("supplied", "reused") \
                    or ASIL_RANK.get(str(component.front.get("asil")), 0) == 0:
                continue
            if waived and (not limited or component.id in limited):
                continue                                  # waived by the safety plan, with its reason
            good = [q for q in self.sources(component.id, "qualifies", ["component-qualification"])
                    if q.status == "approved" and q.front.get("result") in ("qualified", "qualified-with-restrictions")]
            good += [a for a in self.sources(component.id, "qualifies", ["proven-in-use-argument"])
                     if a.status == "approved" and a.front.get("result") in ("obtained", "provisional")]
            if not good:
                self.gap(rule, component, "origin %s, ASIL %s, but no approved qualification qualifies it"
                         % (component.front.get("origin"), component.front.get("asil")))

    def cov_77(self, rule):
        plan = self.plan_in_work("safety")
        entry = self.safety_entries(plan, "safety_activities", "clause").get("8:14") if plan else None
        clauses = {"%s:%s" % (p["id"], c["id"]) for p in fs_catalog()["parts"] for c in p["clauses"]}
        for argument in self.of_type("proven-in-use-argument"):
            if not self.live(argument):
                continue
            if not argument.targets("qualifies"):
                self.gap(rule, argument, "qualifies no element: name the component or system element it argues for")
            bad = [str(c) for c in as_list(argument.front.get("credit")) if str(c).replace("26262-", "", 1) not in clauses]
            if bad:
                self.gap(rule, argument, "credit names %s, which are not clauses of ISO 26262 (<part>:<clause>)" % ", ".join(bad))
            if not entry or entry.get("decision") not in ("performed", "tailored"):
                self.gap(rule, argument, "the safety plan does not plan the proven in use credit: clause 8:14 is %s"
                         % (entry.get("decision") if entry else "not decided"))

    def cov_76(self, rule):
        selected = {str(e.front.get("supplier")).strip().lower() for e in self.of_type("supplier-evaluation")
                    if e.status == "approved" and e.front.get("result") in ("selected", "selected-with-conditions")}
        for agreement in self.of_type("supplier-agreement"):
            name = str(agreement.front.get("supplier") or "").strip().lower()
            if self.live(agreement) and not any(s and (s in name or name in s) for s in selected):
                self.gap(rule, agreement, "no approved supplier evaluation selected %s" % agreement.front.get("supplier"))

    # ---- ISO 26262

    def safety_plan(self):
        """The approved plan of kind safety, or None."""
        return next((p for p in sorted(self.of_type("plan"), key=lambda p: record_number(p.id))
                     if p.status == "approved" and p.front.get("kind") == "safety"), None)

    def plan_in_work(self, kind):
        """The approved plan of a kind, or else the newest live one, so that a plan is checked while it is written
        and reviewed; findings on it then carry the level of its state."""
        plans = sorted((p for p in self.of_type("plan") if self.live(p) and p.front.get("kind") == kind),
                       key=lambda p: record_number(p.id))
        return next((p for p in plans if p.status == "approved"), plans[-1] if plans else None)

    def fs_related(self, item, seen=None):
        """Whether an item is evidence of functional safety: of a type only ISO 26262 uses, of an ASIL above QM,
        derived from a safety goal, or a test case, review or run of such an item."""
        seen = seen if seen is not None else set()
        if item.id in seen:
            return False
        seen.add(item.id)
        refs = [str(r) for r in self.types.get(item.type, {}).get("supports") or []]
        if (refs and all(r.startswith(STANDARD_PREFIXES) for r in refs) and any(r.startswith("26262-") for r in refs)
                or ASIL_RANK.get(str(item.front.get("asil")), 0) > 0):
            return True
        if item.type == "plan":
            return any(str(r).startswith("26262-") for r in self.schema["plan_kinds"].get(item.front.get("kind"), []))
        related = [t for t, _ in item.targets("verifies")]
        if item.type == "review-record":
            related = [str(e.get("item")) for e in as_list(item.front.get("subject")) if isinstance(e, dict)]
        elif item.type == "test-run":
            related = [str(e.get("test")) for e in as_list(item.front.get("results")) if isinstance(e, dict)]
        return any(self.fs_related(self.items[t], seen) for t in related if t in self.items)

    def safety_parts(self):
        return [p for p in fs_catalog()["parts"] if FS_PREFIX + str(p["id"]) in self.fs_scope]

    def safety_entries(self, plan, attribute, key):
        entries = {}
        for entry in as_list(plan.front.get(attribute) if plan else None):
            if isinstance(entry, dict):
                entries[str(entry.get(key))] = entry
        return entries

    def plan_gap(self, rule, plan, message):
        self.add("error" if plan.status == "approved" else self.level_for(plan), rule, plan.id, message,
                 self.rules[rule]["supports"])

    def cov_63(self, rule):
        plan = self.plan_in_work("safety")
        if plan is None:
            return                                        # COV-27 reports the missing plan
        supports, entries = self.rules[rule]["supports"], self.safety_entries(plan, "safety_activities", "clause")
        known = set()
        for part in fs_catalog()["parts"]:
            known |= {"%s:%s" % (part["id"], c["id"]) for c in part["clauses"]}
        for part in self.safety_parts():
            for clause in part["clauses"]:
                key = "%s:%s" % (part["id"], clause["id"])
                entry = entries.get(key)
                if entry is None:
                    self.plan_gap(rule, plan, "safety_activities has no entry for clause %s %s" % (key, clause["name"]))
                elif entry.get("decision") not in FS_DECISIONS:
                    self.plan_gap(rule, plan, "clause %s: decision %r, allowed: %s"
                                  % (key, entry.get("decision"), ", ".join(FS_DECISIONS)))
                elif entry.get("decision") in ("tailored", "not-applicable") and not entry.get("rationale"):
                    self.plan_gap(rule, plan, "clause %s is %s without a rationale" % (key, entry["decision"]))
        for name in sorted(set(entries) - known):
            self.add("warning", rule, plan.id, "safety_activities names %s, which is not a clause of ISO 26262 "
                     "(write \"<part>:<clause>\", for example \"6:7\")" % name, supports)

    def cov_64(self, rule):
        plan = self.plan_in_work("safety")
        if plan is None:
            return
        supports, entries = self.rules[rule]["supports"], self.safety_entries(plan, "method_selection", "table")
        for part in self.safety_parts():
            if str(part["id"]) not in METHOD_TABLE_PARTS:
                continue
            for table in part.get("tables") or []:
                key = "%s:%s" % (part["id"], table["id"])
                entry = entries.get(key)
                if entry is None:
                    self.plan_gap(rule, plan, "method_selection has no entry for table %s (%s)" % (key, table["name"]))
                elif entry.get("decision") == "pending":
                    due = as_date(entry.get("due"))
                    if due is None or not entry.get("responsible"):
                        self.plan_gap(rule, plan, "table %s is pending without a due date and a responsible person" % key)
                    elif due < datetime.date.today():
                        self.plan_gap(rule, plan, "table %s is still pending; it was due on %s (%s)"
                                      % (key, due, entry.get("responsible")))
                    else:
                        self.add("warning", rule, plan.id, "table %s is pending until %s (%s)"
                                 % (key, due, entry.get("responsible")), self.rules[rule]["supports"])
                elif entry.get("decision") not in ("applied", "not-applicable"):
                    self.plan_gap(rule, plan, "table %s: decision %r, allowed: applied, not-applicable, pending" % (key, entry.get("decision")))
                elif entry["decision"] == "applied" and not (entry.get("methods") or entry.get("applied_in")):
                    self.plan_gap(rule, plan, "table %s is applied, but names neither methods nor where they are applied" % key)
                elif entry["decision"] == "not-applicable" and not entry.get("rationale"):
                    self.plan_gap(rule, plan, "table %s is not-applicable without a rationale" % key)

    def cov_65(self, rule):
        events = [e for e in self.of_type("hazardous-event") if self.live(e) and not e.imported]
        if not events:
            return
        plan = self.safety_plan()
        table = plan.front.get("asil_determination") if plan else None
        if not isinstance(table, dict):
            self.add("warning", rule, plan.id if plan else "project", "no approved safety plan with an asil_determination: "
                     "the ASILs of hazardous events are not assessed", self.rules[rule]["supports"])
            return
        for event in events:
            if not self.due(event, "before-review"):
                continue
            key = "%s%s%s" % (event.front.get("severity"), event.front.get("exposure"), event.front.get("controllability"))
            expected = table.get(key)
            if expected is None:
                self.gap(rule, event, "the asil_determination of %s has no entry for %s" % (plan.id, key))
            elif str(expected) != str(event.front.get("asil")):
                self.gap(rule, event, "ASIL %s, but the asil_determination of %s gives %s for %s"
                         % (event.front.get("asil"), plan.id, expected, key))

    def cov_66(self, rule):
        for event in self.of_type("hazardous-event"):
            rank = ASIL_RANK.get(str(event.front.get("asil")))
            if not self.live(event) or event.imported or not rank:
                continue
            goals = self.sources(event.id, "addresses", ["safety-goal"])
            if not goals:
                self.gap(rule, event, "ASIL %s, but no safety goal addresses it" % event.front.get("asil"))
            for goal in goals:
                if ASIL_RANK.get(str(goal.front.get("asil")), -1) < rank:
                    self.gap(rule, goal, "ASIL %s is lower than ASIL %s of %s, which it addresses"
                             % (goal.front.get("asil"), event.front.get("asil"), event.id))

    def cov_67(self, rule):
        for goal in self.of_type("safety-goal"):
            if self.live(goal) and not self.sources(goal.id, "derived_from", ["system-requirement", "software-requirement"]):
                self.gap(rule, goal, "no system or software requirement is derived from it")

    def cov_68(self, rule):
        for analysis in self.of_type("safety-analysis"):
            if not self.live(analysis) or analysis.imported or not self.due(analysis, "before-review"):
                continue
            for finding in as_list(analysis.front.get("findings")):
                if not isinstance(finding, dict):
                    continue
                label, state = finding.get("id"), finding.get("state")
                if state not in ("open", "closed"):
                    self.gap(rule, analysis, "finding %s: state %r, allowed: open, closed" % (label, state))
                elif state == "closed":
                    carrier = finding.get("carried_by")
                    if carrier and str(carrier).split("#")[0] not in self.items:
                        self.gap(rule, analysis, "finding %s: carried_by %s does not exist" % (label, carrier))
                    elif not carrier and not finding.get("rationale"):
                        self.gap(rule, analysis, "finding %s is closed without carried_by or a rationale" % label)
                elif analysis.status == "approved":
                    self.gap(rule, analysis, "approved with finding %s open" % label)

    def cov_69(self, rule):
        supports = self.rules[rule]["supports"]

        def analysed(element, level, method=None):
            for analysis in self.sources(element.id, "analyses", ["safety-analysis"]):
                if analysis.front.get("level") == level and (method is None or analysis.front.get("method") == method):
                    return True
            return False

        if self.covers(FS_PREFIX + "6"):
            for component in self.of_type("software-component"):
                if self.live(component) and component.front.get("kind") != "composition" \
                        and ASIL_RANK.get(str(component.front.get("asil")), 0) > 0 and not analysed(component, "software"):
                    self.add("error" if component.status == "approved" else "warning", rule, component.id,
                             "ASIL %s, but no software-level safety analysis analyses it" % component.front.get("asil"), supports)
            asils = {str(c.front.get("asil")) for c in self.of_type("software-component")
                     if self.live(c) and c.front.get("kind") != "composition" and c.front.get("asil") in ASIL_RANK}
            dfa = [a for a in self.of_type("safety-analysis") if self.live(a) and a.front.get("method") == "dfa"
                   and a.front.get("level") == "software"]
            if len(asils) > 1 and not dfa:
                self.add("error", rule, "project", "software components of ASIL %s coexist, but no software-level dependent "
                         "failures analysis exists" % ", ".join(sorted(asils, key=lambda a: ASIL_RANK[a])), supports)
        if self.covers(FS_PREFIX + "4"):
            for element in self.of_type("system-element"):
                if self.live(element) and element.front.get("kind") != "external" \
                        and ASIL_RANK.get(str(element.front.get("asil")), 0) > 0 and not analysed(element, "system"):
                    self.add("error" if element.status == "approved" else "warning", rule, element.id,
                             "ASIL %s, but no system-level safety analysis analyses it" % element.front.get("asil"), supports)

    def cov_70(self, rule):
        for decision in self.of_type("design-decision"):
            split = decision.front.get("decomposition")
            if not self.live(decision) or not isinstance(split, dict):
                continue
            original = self.items.get(str(split.get("requirement")))
            parts = [self.items.get(str(r)) for r in as_list(split.get("into"))]
            dfa = self.items.get(str(split.get("independence")))
            if original is None:
                self.gap(rule, decision, "decomposition names requirement %s, which does not exist" % split.get("requirement"))
            if not parts or None in parts:
                self.gap(rule, decision, "decomposition names requirements under into that do not exist: %s" % split.get("into"))
            if dfa is None or dfa.type != "safety-analysis" or dfa.front.get("method") != "dfa" or not self.live(dfa):
                self.gap(rule, decision, "decomposition names %s under independence, which is not a live dependent failures "
                         "analysis" % split.get("independence"))
            if original is not None:
                top = ASIL_RANK.get(str(original.front.get("asil")), 0)
                for part in [p for p in parts if p is not None]:
                    if ASIL_RANK.get(str(part.front.get("asil")), 0) > top:
                        self.gap(rule, decision, "%s has an ASIL above the decomposed requirement %s" % (part.id, original.id))

    def cov_71(self, rule):
        plan = self.safety_plan()
        table = plan.front.get("tcl_determination") if plan and isinstance(plan.front.get("tcl_determination"), dict) else None
        if not table and any(self.live(t) for t in self.of_type("tool-evaluation")):
            self.add("warning", rule, plan.id if plan else "project", "no approved safety plan with a tcl_determination: "
                     "the confidence levels of the tools are not assessed", self.rules[rule]["supports"])
        for tool in self.of_type("tool-evaluation"):
            if not self.live(tool) or not self.due(tool, "before-review"):
                continue
            if table:
                key = "%s-%s" % (tool.front.get("impact"), tool.front.get("detection"))
                expected = table.get(key)
                if expected is not None and str(expected) != str(tool.front.get("confidence")):
                    self.gap(rule, tool, "%s, but the tcl_determination of %s gives %s for %s"
                             % (tool.front.get("confidence"), plan.id, expected, key))

    def cov_72(self, rule):
        evaluated = [str(t.front.get("tool") or "").lower() for t in self.of_type("tool-evaluation") if self.live(t)]
        named = {}
        for record in self.of_type("build-record", "static-analysis-run"):
            if record.status == "final" and record.front.get("tool"):
                named.setdefault(str(record.front.get("tool")), record.id)
        for tool, record in sorted(named.items()):
            low = tool.lower()
            if not any(e and (e in low or e.split()[0] == low.split()[0]) for e in evaluated):
                self.add("error", rule, record, "tool '%s' is used, but no tool evaluation covers it" % tool,
                         self.rules[rule]["supports"])

    def cov_73(self, rule):
        plan = self.safety_plan()
        if plan is None:
            return
        records = [r for r in self.of_type("confirmation-measure") if r.status == "final"]
        for entry in as_list(plan.front.get("confirmation_measures")):
            if not isinstance(entry, dict):
                continue
            wanted = INDEPENDENCE.get(str(entry.get("independence")), 0)
            done = [r for r in records if r.front.get("kind") == entry.get("measure")
                    and str(r.front.get("subject")) == str(entry.get("subject"))]
            good = [r for r in done if INDEPENDENCE.get(str(r.front.get("independence")), -1) >= wanted
                    and r.front.get("result") not in ("failed", "rejected")]
            if not good:
                why = ("records %s do not reach independence %s or did not pass" % (", ".join(r.id for r in done), entry.get("independence"))
                       if done else "no final confirmation-measure record")
                self.add("error", rule, plan.id, "%s of %s: %s" % (entry.get("measure"), entry.get("subject"), why),
                         self.rules[rule]["supports"])

    # ---- ISO/SAE 21434

    def cs_plan(self):
        """The approved plan of kind cybersecurity, or None."""
        return next((p for p in sorted(self.of_type("plan"), key=lambda p: record_number(p.id))
                     if p.status == "approved" and p.front.get("kind") == "cybersecurity"), None)

    def tara_method(self, rule):
        """The tara_method of the approved cybersecurity plan; reports once per rule when there is none."""
        plan = self.cs_plan()
        method = plan.front.get("tara_method") if plan else None
        if isinstance(method, dict):
            return plan, method
        if any(self.live(t) and not t.imported for t in self.of_type("damage-scenario", "threat-scenario")):
            self.add("warning", rule, plan.id if plan else "project",
                     "no approved cybersecurity plan with a tara_method: ratings and risk values are not assessed",
                     self.rules[rule]["supports"])
        return plan, None

    def tara_items(self, *types):
        return [i for i in self.of_type(*types) if self.live(i) and not i.imported]

    def highest_impact(self, threat):
        """The highest impact rating of the damage scenarios a threat scenario leads to, or None."""
        levels = [str(level) for target, _ in threat.targets("leads_to") if target in self.items
                  for level in (self.items[target].front.get("impact") or {}).values()
                  if isinstance(self.items[target].front.get("impact"), dict) and str(level) in IMPACT_LEVELS]
        return max(levels, key=IMPACT_LEVELS.index) if levels else None

    def matrix_value(self, method, impact, feasibility):
        row = (method.get("risk_matrix") or {}).get(impact) if isinstance(method.get("risk_matrix"), dict) else None
        if not isinstance(row, list) or len(row) != len(FEASIBILITY_LEVELS) or feasibility not in FEASIBILITY_LEVELS:
            return None
        return row[FEASIBILITY_LEVELS.index(feasibility)]

    def cs_related(self, item, seen=None):
        """Whether an item is cybersecurity evidence: of a type only ISO/SAE 21434 uses, security-relevant,
        derived from a cybersecurity goal, or a test case, review or run of such an item."""
        seen = seen if seen is not None else set()
        if item.id in seen:
            return False
        seen.add(item.id)
        refs = [str(r) for r in self.types.get(item.type, {}).get("supports") or []]
        if (refs and all(r.startswith(STANDARD_PREFIXES) for r in refs) and any(r.startswith(CS_PREFIX) for r in refs)
                or item.front.get("security_relevant") is True):
            return True
        if any(getattr(self.items.get(t), "type", None) == "cybersecurity-goal" for t, _ in item.targets("derived_from")):
            return True
        related = [t for t, _ in item.targets("verifies")]
        if item.type == "review-record":
            related = [str(e.get("item")) for e in as_list(item.front.get("subject")) if isinstance(e, dict)]
        elif item.type == "test-run":
            related = [str(e.get("test")) for e in as_list(item.front.get("results")) if isinstance(e, dict)]
        return any(self.cs_related(self.items[t], seen) for t in related if t in self.items)

    def cov_53(self, rule):
        plan = self.plan_in_work("cybersecurity")
        if plan is None:
            return                                        # COV-27 reports the missing plan
        supports = self.rules[rule]["supports"]
        entries = {}
        for entry in as_list(plan.front.get("cybersecurity_activities")):
            if isinstance(entry, dict):
                entries[str(entry.get("subclause"))] = entry
        known = set()
        for clause in cs_catalog()["clauses"]:
            known |= {str(s["id"]) for s in clause["subclauses"]}
            if CS_PREFIX + str(clause["id"]) not in self.cs_scope:
                continue
            for sub in clause["subclauses"]:
                entry = entries.get(str(sub["id"]))
                if entry is None:
                    self.add("error", rule, plan.id, "cybersecurity_activities has no entry for subclause %s %s"
                             % (sub["id"], sub["name"]), supports)
                elif entry.get("decision") not in CS_DECISIONS:
                    self.add("error", rule, plan.id, "subclause %s: decision %r, allowed: %s"
                             % (sub["id"], entry.get("decision"), ", ".join(CS_DECISIONS)), supports)
                elif entry.get("decision") in ("tailored", "not-applicable") and not entry.get("rationale"):
                    self.add("error", rule, plan.id, "subclause %s is %s without a rationale"
                             % (sub["id"], entry.get("decision")), supports)
        for name in sorted(set(entries) - known):
            self.add("warning", rule, plan.id, "cybersecurity_activities names %s, which is not a subclause of "
                     "ISO/SAE 21434 (write it in quotes, for example \"9.4\")" % name, supports)

    def cov_54(self, rule):
        for asset in self.tara_items("asset"):
            if not self.sources(asset.id, "threatens", ["threat-scenario"]):
                self.gap(rule, asset, "no threat scenario threatens it")
        for damage in self.tara_items("damage-scenario"):
            if not self.sources(damage.id, "leads_to", ["threat-scenario"]):
                self.gap(rule, damage, "no threat scenario leads to it")

    def cov_55(self, rule):
        plan, method = self.tara_method(rule)
        if method is None:
            return
        categories = [str(c) for c in as_list(method.get("impact_categories"))]
        for damage in self.tara_items("damage-scenario"):
            impact = damage.front.get("impact")
            if not self.due(damage, "before-review") and not impact:
                continue
            if not isinstance(impact, dict):
                self.gap(rule, damage, "impact is not rated per category of %s (%s)" % (plan.id, ", ".join(categories)))
                continue
            for category in categories:
                if impact.get(category) is None:
                    self.gap(rule, damage, "no impact rating for category %s of %s" % (category, plan.id))
                elif str(impact.get(category)) not in IMPACT_LEVELS:
                    self.gap(rule, damage, "impact %s is %r; allowed: %s"
                             % (category, impact.get(category), ", ".join(reversed(IMPACT_LEVELS))))
            for category in sorted(set(map(str, impact)) - set(categories)):
                self.gap(rule, damage, "rated in category %s, which %s does not name" % (category, plan.id))

    def cov_56(self, rule):
        for threat in self.tara_items("threat-scenario"):
            assets = [self.items[t] for t, _ in threat.targets("threatens") if t in self.items]
            if not assets:
                self.gap(rule, threat, "threatens no asset")
            if not threat.targets("leads_to"):
                self.gap(rule, threat, "leads to no damage scenario")
            prop = threat.front.get("property")
            if assets and prop and not any(prop in as_list(a.front.get("properties")) for a in assets):
                self.gap(rule, threat, "property %s is not a property of %s" % (prop, ", ".join(a.id for a in assets)))
            if not self.due(threat, "before-review"):
                continue
            paths = [p for p in as_list(threat.front.get("attack_paths")) if isinstance(p, dict)]
            if not paths:
                self.gap(rule, threat, "no attack path")
                continue
            for n, path in enumerate(paths, 1):
                if path.get("feasibility") not in FEASIBILITY_LEVELS:
                    self.gap(rule, threat, "attack path %d: feasibility %r; allowed: %s"
                             % (n, path.get("feasibility"), ", ".join(reversed(FEASIBILITY_LEVELS))))
            rated = [p["feasibility"] for p in paths if p.get("feasibility") in FEASIBILITY_LEVELS]
            stated = threat.front.get("feasibility")
            if rated and stated in FEASIBILITY_LEVELS and stated != max(rated, key=FEASIBILITY_LEVELS.index):
                self.gap(rule, threat, "feasibility %s, but the highest of its attack paths is %s"
                         % (stated, max(rated, key=FEASIBILITY_LEVELS.index)))

    def cov_57(self, rule):
        plan, method = self.tara_method(rule)
        if method is None:
            return
        for impact in IMPACT_LEVELS:
            row = (method.get("risk_matrix") or {}).get(impact) if isinstance(method.get("risk_matrix"), dict) else None
            if not isinstance(row, list) or len(row) != len(FEASIBILITY_LEVELS) \
                    or any(v not in (1, 2, 3, 4, 5) for v in row):
                self.add("error", rule, plan.id, "risk_matrix needs for impact %s four risk values 1 to 5, for "
                         "feasibility %s" % (impact, ", ".join(FEASIBILITY_LEVELS)), self.rules[rule]["supports"])
        for threat in self.tara_items("threat-scenario"):
            if not self.due(threat, "before-review"):
                continue
            impact, feasibility = self.highest_impact(threat), threat.front.get("feasibility")
            if impact is None:
                self.gap(rule, threat, "no damage scenario it leads to is rated: the risk value cannot be checked")
                continue
            expected = self.matrix_value(method, impact, feasibility)
            if expected is not None and threat.front.get("risk_value") != expected:
                self.gap(rule, threat, "risk value %s, but the risk matrix of %s gives %s for impact %s and feasibility %s"
                         % (threat.front.get("risk_value"), plan.id, expected, impact, feasibility))

    def cov_58(self, rule):
        plan = self.cs_plan()
        method = plan.front.get("tara_method") if plan and isinstance(plan.front.get("tara_method"), dict) else {}
        limit = method.get("retain_up_to")
        for threat in self.tara_items("threat-scenario"):
            treatment = [str(t) for t in as_list(threat.front.get("treatment"))]
            if not treatment or not self.due(threat, "before-review"):
                continue
            goals = self.sources(threat.id, "addresses", ["cybersecurity-goal"])
            claims = self.sources(threat.id, "addresses", ["cybersecurity-claim"])
            if "reduce" in treatment and not goals:
                self.gap(rule, threat, "treatment reduce, but no cybersecurity goal addresses it")
            kept = [t for t in treatment if t in ("share", "retain")]
            if kept and not claims:
                self.gap(rule, threat, "treatment %s, but no cybersecurity claim addresses it" % " and ".join(kept))
            value = threat.front.get("risk_value")
            if "retain" in treatment and isinstance(limit, int) and isinstance(value, int) and value > limit \
                    and not threat.front.get("decision"):
                self.gap(rule, threat, "retains risk value %s, above %s (retain_up_to of %s), without a decision "
                         "naming who accepted it" % (value, limit, plan.id))

    def cov_59(self, rule):
        for goal in self.of_type("cybersecurity-goal"):
            if self.live(goal) and not self.sources(goal.id, "derived_from", ["system-requirement", "software-requirement"]):
                self.gap(rule, goal, "no system or software requirement is derived from it")

    def cov_60(self, rule):
        for item in self.items.values():
            if not self.live(item) or item.imported or "security_relevant" not in self.attributes(item.type):
                continue
            reasons = []
            for target_id, _ in item.targets("derived_from"):
                target = self.items.get(target_id)
                if target is None:
                    continue
                if target.type == "cybersecurity-goal":
                    reasons.append("derived from the cybersecurity goal %s" % target_id)
                elif target.front.get("security_relevant") is True:
                    reasons.append("derived from %s, which is security-relevant" % target_id)
            if item.type in ("software-component", "software-interface", "system-element", "system-interface"):
                reasons += ["fulfils %s, which is security-relevant" % r.id for r in self.allocated_requirements(item.id)
                            if r.front.get("security_relevant") is True]
            if reasons and item.front.get("security_relevant") is not True:
                self.gap(rule, item, "security_relevant is %s, but it is %s"
                         % (item.front.get("security_relevant"), "; ".join(reasons)))

    def cov_61(self, rule):
        for weakness in self.of_type("weakness"):
            if not self.live(weakness) or not self.due(weakness, "before-review") \
                    or weakness.front.get("vulnerability") is not True:
                continue
            treatment = [str(t) for t in as_list(weakness.front.get("treatment"))]
            if "reduce" in treatment and self.due(weakness, "before-approval") \
                    and not self.sources(weakness.id, "resolves", ["change-request"]) \
                    and not self.sources(weakness.id, "affects", ["problem-report"]) \
                    and not weakness.front.get("corrected_by"):
                self.gap(rule, weakness, "treatment reduce, but no change request resolves it, no problem report "
                         "carries the correction, and corrected_by names no release of another party")
            impact, feasibility = weakness.front.get("impact"), weakness.front.get("feasibility")
            if impact and feasibility:
                plan = self.cs_plan()
                method = plan.front.get("tara_method") if plan and isinstance(plan.front.get("tara_method"), dict) else None
                expected = self.matrix_value(method, str(impact), str(feasibility)) if method else None
                if expected is not None and weakness.front.get("risk_value") != expected:
                    self.gap(rule, weakness, "risk value %s, but the risk matrix of %s gives %s for impact %s and "
                             "feasibility %s" % (weakness.front.get("risk_value"), plan.id, expected, impact, feasibility))
            kept = [t for t in treatment if t in ("share", "retain")]
            if kept and not self.sources(weakness.id, "addresses", ["cybersecurity-claim"]):
                self.gap(rule, weakness, "treatment %s, but no cybersecurity claim addresses it" % " and ".join(kept))

    def cov_78(self, rule):
        for event in self.of_type("cybersecurity-event"):
            if self.live(event) and event.front.get("relevant") is True and event.status == "closed" \
                    and not self.sources(event.id, "derived_from", ["weakness"]):
                self.gap(rule, event, "triaged relevant, but no weakness is derived from it")

    def cov_62(self, rule):
        for goal in self.of_type("cybersecurity-goal"):
            if self.live(goal) and not self.sources(goal.id, "verifies", ["system-qualification-test"]):
                self.gap(rule, goal, "no system qualification test validates it")

    def check_cybersecurity_values(self):
        """Values of list attributes the schema cannot state as `values`, and references inside records."""
        for asset in self.of_type("asset"):
            wrong = [p for p in as_list(asset.front.get("properties")) if p not in CS_PROPERTIES]
            if wrong:
                self.add("error", "SCHEMA", asset.id, "properties %s; allowed: %s" % (wrong, ", ".join(sorted(CS_PROPERTIES))))
        for item in self.of_type("threat-scenario", "weakness"):
            wrong = [t for t in as_list(item.front.get("treatment")) if t not in CS_TREATMENTS]
            if wrong:
                self.add("error", "SCHEMA", item.id, "treatment %s; allowed: %s" % (wrong, ", ".join(CS_TREATMENTS)))
        for record in self.of_type("cybersecurity-assessment"):
            case = self.items.get(str(record.front.get("case")))
            if case is None or case.type != "cybersecurity-case":
                self.add("error", "LINK", record.id, "case names %s, which is not a cybersecurity case"
                         % record.front.get("case"))

    def check_inputs(self):
        """The record of what was received names what, which version and when."""
        for n, entry in enumerate(as_list(self.config.get("inputs")), 1):
            if not isinstance(entry, dict):
                continue
            missing = [k for k in ("source", "version", "received") if not str(entry.get(k) or "").strip()]
            if missing:
                self.add("warning", "SCHEMA", "project.yaml", "inputs entry %d (%s) has no %s: what was received is "
                         "recorded with its version and date" % (n, entry.get("source") or "-", ", ".join(missing)))

    def check(self):
        self.check_inputs()
        self.check_structure()
        self.check_coverage()
        self.check_upstream()
        return self.findings


# --------------------------------------------------------------------------- commands

def cmd_check(project, args):
    findings = project.check()
    order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda f: (order[f["level"]], f["rule"], f["item"]))
    counts = {level: sum(1 for f in findings if f["level"] == level) for level in order}
    shown = [f for f in findings if args.all or f["level"] != "info"]
    if args.json:
        print(json.dumps({"items": len(project.items), "counts": counts, "findings": shown}, indent=2))
    else:
        for f in shown:
            tail = "  [%s]" % ", ".join(f["supports"]) if f["supports"] else ""
            print("%-7s %-11s %-10s %s%s" % (f["level"], f["rule"], f["item"], f["message"], tail))
        scope = ", ".join(sorted(project.scope)) if project.scope else "all processes"
        if project.cs_scope:
            scope += "; ISO/SAE 21434 clauses %s" % ", ".join(sorted((c[len(CS_PREFIX):] for c in project.cs_scope), key=int))
        if project.fs_scope:
            scope += "; ISO 26262 parts %s" % ", ".join(sorted((c[len(FS_PREFIX):] for c in project.fs_scope), key=int))
        active = [r for r in sorted(project.rules) if project.active(r)]
        print("%d items | scope: %s | %d of %d coverage rules active | %d errors, %d warnings, %d on drafts%s"
              % (len(project.items), scope, len(active), len(project.rules), counts["error"], counts["warning"],
                 counts["info"], "" if args.all or not counts["info"] else " (use --all to list)"))
    return 1 if counts["error"] else 0


def cmd_matrix(project, args):
    for role, link in project.schema["links"].items():
        for pair in link["pairs"]:
            if pair["to"] == "any" or not project.in_scope(pair["supports"]):
                continue
            targets = [t for t in project.of_type(*pair["to"]) if project.live(t)]
            if not targets:
                continue
            print("\n### %s: %s -> %s  (%s)\n" % (role, pair["from"], ", ".join(pair["to"]), ", ".join(pair["supports"])))
            print("| Target | Title | Linked from |\n|---|---|---|")
            for target in sorted(targets, key=lambda t: t.id):
                sources = sorted(s.id for s in project.sources(target.id, role, [pair["from"]]))
                print("| %s | %s | %s |" % (target.id, target.title, ", ".join(sources) or "-"))
    return 0


def cmd_show(project, args):
    item = project.items.get(args.id)
    if item is None:
        print("no such item: %s" % args.id)
        return 1
    print("%s  %s  [%s]  %s  hash %s" % (item.id, item.type, item.status, item.title, item.hash))
    for role in (item.front.get("links") or {}):
        for target, anchor in item.targets(role):
            other = project.items.get(target)
            print("  %-13s -> %s%s  %s" % (role, target, "#" + anchor if anchor else "", other.title if other else "(missing)"))
    for role, sources in sorted(project.incoming[item.id].items()):
        for source in sorted(sources):
            other = project.items.get(source)
            print("  %-13s <- %s  %s" % (role, source, other.title if other else "(missing)"))
    for target, role in project.dependencies(item):
        if role in INTERFACE_ROLES.values():              # stated on the interface, not a link of the component
            print("  %-13s -> %s  %s" % (role, target, project.items[target].title))
    return 0


def cmd_impact(project, args):
    if args.id not in project.items:
        print("no such item: %s" % args.id)
        return 1
    seen, queue = {}, [(args.id, 0)]
    while queue:
        current, depth = queue.pop(0)
        for role, sources in project.incoming[current].items():
            for source in sources:
                if source not in seen and source != args.id:
                    seen[source] = (depth + 1, role, current)
                    queue.append((source, depth + 1))
    for source, (depth, role, via) in sorted(seen.items(), key=lambda kv: (kv[1][0], kv[0])):
        item = project.items[source]
        print("%d  %-10s %-28s %s  (%s %s)" % (depth, source, item.type, item.title, role, via))
    print("%d items depend on %s" % (len(seen), args.id))
    return 0


def cmd_hash(project, args):
    ids = args.ids or sorted(project.items)
    missing = [i for i in ids if i not in project.items]
    if missing:
        print("no such item: %s" % ", ".join(missing))
        return 1
    if not args.upstream:
        for i in ids:
            print("%s  %s" % (i, project.items[i].hash))
        return 0
    references = {}
    for i in ids:
        for target, _ in project.dependencies(project.items[i]):
            if target in project.items and target not in ids:
                references[target] = project.items[target].hash
    print("subject:")
    for i in ids:
        print("  - {item: %s, hash: %s}" % (i, project.items[i].hash))
    print("references:" if references else "references: []")
    for target in sorted(references):
        print("  - {item: %s, hash: %s}" % (target, references[target]))
    return 0


def progress(project, as_of):
    """Work packages, milestones and corrective actions as of a date: what the plan says against what the items show."""
    states = {}

    def state_of(package):
        if package.id in states:
            return states[package.id]
        states[package.id] = None                        # a cycle (COV-31) ends here
        delivered = [project.items[t] for t, _ in package.targets("delivers")
                     if t in project.items and project.live(project.items[t])]
        unsettled = [d.id for d in delivered if d.status not in SETTLED.get(project.types[d.type]["lifecycle"], ())]
        children = [c for c in project.sources(package.id, "part_of", ["work-package"])]
        child_states = [state_of(c) for c in children]
        track = package.front.get("progress") if isinstance(package.front.get("progress"), dict) else {}
        stated = as_date(track.get("completed_on"))
        open_children = [c.id for c, s in zip(children, child_states) if s and s["state"] != "done"]
        if stated and not unsettled and not open_children:
            state = "done"
        elif stated:
            state = "done as stated, contradicted"
        elif delivered or as_date(track.get("actual_start")) or any(s and s["state"] != "not started" for s in child_states):
            state = "in progress"
        else:
            state = "not started"
        start, finish = as_date(package.front.get("planned_start")), as_date(package.front.get("planned_finish"))
        result = {"item": package.id, "title": package.title, "owner": package.front.get("owner"), "state": state,
                  "planned_start": str(start) if start else None, "planned_finish": str(finish) if finish else None,
                  "estimate": package.front.get("estimate"), "actual_effort": track.get("actual_effort"),
                  "delivered": len(delivered), "settled": len(delivered) - len(unsettled), "unsettled": unsettled,
                  "open_parts": open_children,
                  "late": bool(finish and finish < as_of and state != "done"),
                  "late_to_start": bool(start and start < as_of and state == "not started"),
                  "parent": next((t for t, _ in package.targets("part_of")), None)}
        states[package.id] = result
        return result

    packages = [state_of(p) for p in sorted(project.of_type("work-package"), key=lambda p: record_number(p.id))
                if project.live(p)]
    baselines = [b for b in project.of_type("baseline") if b.status == "final"]
    milestones = []
    for plan in project.of_type("plan"):
        if plan.front.get("kind") != "project" or not project.live(plan):
            continue
        for stone in as_list(plan.front.get("milestones")):
            if not isinstance(stone, dict):
                continue
            date, purpose = as_date(stone.get("date")), stone.get("baseline_purpose")
            reached = sorted(str(b.front.get("created_at", ""))[:10] for b in baselines if purpose and b.front.get("purpose") == purpose)
            if reached:
                state = "reached %s%s" % (reached[0], " (late)" if date and as_date(reached[0]) and as_date(reached[0]) > date else "")
            elif not purpose:
                state = "not assessed: no baseline purpose named"
            elif date and date < as_of:
                state = "missed"
            else:
                state = "due in %d days" % (date - as_of).days if date else "no date"
            milestones.append({"plan": plan.id, "name": stone.get("name"), "date": str(date) if date else None,
                               "baseline_purpose": purpose, "state": state})
    actions = []
    for action in project.of_type("corrective-action"):
        if action.status in ("closed", "cancelled"):
            continue
        due = as_date(action.front.get("due"))
        actions.append({"item": action.id, "title": action.title, "owner": action.front.get("owner"), "state": action.status,
                        "due": str(due) if due else None, "overdue": bool(due and due < as_of and action.status == "open")})
    return {"as_of": str(as_of), "work_packages": packages, "milestones": milestones, "corrective_actions": actions}


def cmd_progress(project, args):
    as_of = as_date(args.as_of) if args.as_of else datetime.date.today()
    if as_of is None:
        print("--as-of must be a date YYYY-MM-DD")
        return 1
    data = progress(project, as_of)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("Progress as of %s" % data["as_of"])
    depth = {}
    for p in data["work_packages"]:
        depth[p["item"]] = depth.get(p["parent"], -1) + 1 if p["parent"] in depth else 0
        flags = [f for f, on in (("LATE", p["late"]), ("LATE TO START", p["late_to_start"])) if on]
        print("%s%-8s %-28s finish %-10s estimate %-5s actual %-5s delivered %d/%d settled  %s%s"
              % ("  " * depth[p["item"]], p["item"], p["state"], p["planned_finish"] or "-", p["estimate"] or "-",
                 p["actual_effort"] if p["actual_effort"] is not None else "-", p["settled"], p["delivered"],
                 p["owner"] or "-", ("  " + ", ".join(flags)) if flags else ""))
        if p["state"] == "done as stated, contradicted":
            print("%s         not settled: %s" % ("  " * depth[p["item"]], ", ".join(p["unsettled"] + p["open_parts"])))
    if data["milestones"]:
        print("Milestones")
        for m in data["milestones"]:
            print("  %-24s %-10s %s" % (m["name"], m["date"] or "-", m["state"]))
    if data["corrective_actions"]:
        print("Corrective actions")
        for a in data["corrective_actions"]:
            print("  %-8s %-6s due %-10s %s%s" % (a["item"], a["state"], a["due"] or "-", a["owner"] or "-",
                                                  "  OVERDUE" if a["overdue"] else ""))
    packages = data["work_packages"]
    count = lambda key, value: sum(1 for p in packages if p[key] == value)   # noqa: E731
    print("%d work packages: %d done, %d in progress (%d late), %d not started (%d late to start); "
          "%d milestones missed; %d corrective actions open (%d overdue)"
          % (len(packages), count("state", "done"), count("state", "in progress"),
             sum(1 for p in packages if p["state"] != "done" and p["late"]), count("state", "not started"),
             count("late_to_start", True), sum(1 for m in data["milestones"] if m["state"] == "missed"),
             len(data["corrective_actions"]), sum(1 for a in data["corrective_actions"] if a["overdue"])))
    return 0


def problems(project, as_of):
    """Problem reports known on a date, with their present state and their age on that date."""
    entries = []
    for problem in sorted(project.of_type("problem-report"), key=lambda p: record_number(p.id)):
        reported = as_date(problem.front.get("reported_at"))
        if reported and reported > as_of:
            continue                                      # not known yet on that date
        closure = problem.front.get("closure") if isinstance(problem.front.get("closure"), dict) else {}
        closed = as_date(closure.get("accepted_at")) if problem.status == "closed" else None
        end = closed if closed and closed <= as_of else as_of
        entries.append({
            "item": problem.id, "title": problem.title, "state": problem.status,
            "severity": problem.front.get("severity"), "origin": problem.front.get("origin"),
            "detected_by": problem.front.get("detected_by"),
            "reported_at": str(reported) if reported else None, "closed_at": str(closed) if closed else None,
            "age_days": (end - reported).days if reported else None,
            "affects": [t for t, _ in problem.targets("affects")],
            "change_requests": [{"item": c.id, "state": c.status}
                                for c in project.sources(problem.id, "resolves", ["change-request"])],
        })
    counted = [e for e in entries if e["state"] != "rejected"]
    unresolved = [e for e in counted if e["state"] in UNRESOLVED]

    def by(key):
        out = defaultdict(int)
        for entry in counted:
            out[str(entry[key])] += 1
        return dict(sorted(out.items()))

    figures = {"total": len(counted), "rejected": len(entries) - len(counted), "unresolved": len(unresolved),
               "by_state": by("state"), "by_severity": by("severity"), "by_origin": by("origin"),
               "by_detection": by("detected_by"),
               "unresolved_by_age": {"up to 7 days": sum(1 for e in unresolved if (e["age_days"] or 0) <= 7),
                                     "8 to 30 days": sum(1 for e in unresolved if 7 < (e["age_days"] or 0) <= 30),
                                     "over 30 days": sum(1 for e in unresolved if (e["age_days"] or 0) > 30)}}
    return {"as_of": str(as_of), "problems": entries, "figures": figures}


def quality(project, as_of):
    """What quality assurance planned and did, and the state of its non-conformances, on a date."""
    plan = project.quality_plan()
    records = sorted([r for r in project.of_type("quality-record") if r.status == "final"
                      and (as_date(r.front.get("checked_at")) or as_of) <= as_of],
                     key=lambda r: (str(r.front.get("checked_at")), record_number(r.id)))
    checks = []
    for check in (as_list(plan.front.get("quality_checks")) if plan else []):
        if not isinstance(check, dict):
            continue
        done = [r for r in records if r.front.get("check") == check.get("name")]
        checks.append({"name": check.get("name"), "kind": check.get("kind"), "scope": as_list(check.get("scope")),
                       "before": as_list(check.get("before")), "when": check.get("when"), "performed": len(done),
                       "last": done[-1].id if done else None,
                       "last_at": str(done[-1].front.get("checked_at")) if done else None,
                       "last_result": done[-1].front.get("result") if done else None})
    told = defaultdict(list)
    for record in project.of_type("communication-record"):
        if record.status == "final":
            for subject in as_list(record.front.get("subject")):
                told[str(subject)].append(record)
    rules = [e for e in (as_list(plan.front.get("escalation")) if plan else []) if isinstance(e, dict)]
    findings = []
    for record in records:
        if record.front.get("kind") == "summary":
            continue                                      # a report restates; the checks raise the findings
        for finding in as_list(record.front.get("findings")):
            if not isinstance(finding, dict):
                continue
            action = project.items.get(str(finding.get("action")))
            state = action.status if action else "missing"
            done = state in ("closed", "cancelled", "rejected", "done", "resolved")
            due = as_date(action.front.get("due")) if action is not None and action.type == "corrective-action" else None
            overdue = (as_of - due).days if due and not done and due < as_of else 0
            escalations = [c for c in told.get(str(finding.get("action")), [])
                           if not c.front.get("practices") or "SUP.1.BP6" in map(str, as_list(c.front.get("practices")))]
            reached = {str(a).strip().lower() for c in escalations for a in as_list(c.front.get("audience"))}
            needed = sorted({str(to) for rule in rules if overdue > int(rule.get("after_days") or 0)
                             for to in as_list(rule.get("to"))})
            findings.append({"record": record.id, "finding": finding.get("id"), "text": finding.get("text"),
                             "action": finding.get("action"), "state": state, "due": str(due) if due else None,
                             "overdue_days": overdue,
                             "escalation_due": [n for n in needed if n.strip().lower() not in reached],
                             "escalated_to": sorted({str(a) for c in escalations for a in as_list(c.front.get("audience"))}),
                             "responses": [c.front.get("agreement") for c in escalations if c.front.get("agreement")]})
    summaries = [{"record": r.id, "checked_at": str(r.front.get("checked_at")), "result": r.front.get("result"),
                  "communicated": bool(told.get(r.id))} for r in records if r.front.get("kind") == "summary"]
    summarised = {str(s) for r in records if r.front.get("kind") == "summary" for s in as_list(r.front.get("subject"))}
    open_findings = [f for f in findings if f["state"] not in ("closed", "cancelled", "rejected")]
    figures = {"checks_planned": len(checks), "checks_never_performed": sum(1 for c in checks if not c["performed"]),
               "records": sum(1 for r in records if r.front.get("kind") != "summary"),
               "conforming": sum(1 for r in records if r.front.get("kind") != "summary"
                                 and r.front.get("result") == "conforms"),
               "findings": len(findings), "findings_open": len(open_findings),
               "findings_overdue": sum(1 for f in open_findings if f["overdue_days"]),
               "escalations_due": sum(1 for f in findings if f["escalation_due"]),
               "not_summarised": [r.id for r in records if r.front.get("kind") != "summary" and r.id not in summarised]}
    return {"as_of": str(as_of), "plan": plan.id if plan else None, "checks": checks, "findings": findings,
            "summaries": summaries, "figures": figures}


def suppliers(project, as_of):
    """Per supplier agreement: meetings held against the agreed rhythm, exchanges recorded, open items."""
    out = []
    reviews = sorted([r for r in project.of_type("supplier-review") if r.status == "final"],
                     key=lambda r: (str(r.front.get("held_at")), record_number(r.id)))
    for agreement in sorted(project.of_type("supplier-agreement"), key=lambda a: record_number(a.id)):
        if not project.live(agreement):
            continue
        mine = [r for r in reviews if r.front.get("agreement") == agreement.id]
        meetings = []
        for meeting in as_list(agreement.front.get("meetings")):
            if not isinstance(meeting, dict):
                continue
            held = [r for r in mine if r.front.get("kind") == meeting.get("kind")]
            last = as_date(held[-1].front.get("held_at")) if held else None
            cadence = meeting.get("cadence")
            due = (last + datetime.timedelta(days=int(cadence))) if last and isinstance(cadence, int) else None
            meetings.append({"name": meeting.get("name"), "kind": meeting.get("kind"), "cadence": cadence,
                             "held": len(held), "last": str(last) if last else None,
                             "overdue_days": (as_of - due).days if due and due < as_of else 0})
        closed = {str(i.get("closes")) for r in mine for i in as_list(r.front.get("open_items"))
                  if isinstance(i, dict) and i.get("closes")}
        items = []
        for review in mine:
            for item in as_list(review.front.get("open_items")):
                if not isinstance(item, dict) or item.get("state") != "open":
                    continue
                key = "%s#%s" % (review.id, item.get("id"))
                if key in closed:
                    continue
                due = as_date(item.get("due"))
                items.append({"item": key, "text": item.get("text"), "owner": item.get("owner"),
                              "due": str(due) if due else None,
                              "overdue_days": (as_of - due).days if due and due < as_of else 0})
        exchanged = [c for c in project.of_type("communication-record") if c.status == "final"
                     and agreement.id in map(str, as_list(c.front.get("subject")))]
        actions = [a for a in project.of_type("corrective-action") if agreement.id in {t for t, _ in a.targets("addresses")}]
        out.append({"agreement": agreement.id, "supplier": agreement.front.get("supplier"), "status": agreement.status,
                    "components": as_list(agreement.front.get("components")), "meetings": meetings,
                    "exchanges_agreed": len(as_list(agreement.front.get("exchanges"))),
                    "exchanges_recorded": [c.id for c in exchanged], "open_items": items,
                    "corrective_actions": [{"item": a.id, "state": a.status} for a in actions]})
    return {"as_of": str(as_of), "agreements": out}


def cmd_suppliers(project, args):
    as_of = as_date(args.as_of) if args.as_of else datetime.date.today()
    if as_of is None:
        print("--as-of must be a date YYYY-MM-DD")
        return 2
    data = suppliers(project, as_of)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("Suppliers as of %s" % as_of)
    for a in data["agreements"]:
        print("%s %s (%s), components %s" % (a["agreement"], a["supplier"], a["status"], ", ".join(map(str, a["components"])) or "-"))
        for m in a["meetings"]:
            print("  meeting %-24s %-9s every %s, held %d times, last %s%s" % (
                m["name"], m["kind"], m["cadence"], m["held"], m["last"] or "-",
                ", overdue %d days" % m["overdue_days"] if m["overdue_days"] else ""))
        print("  exchanges: %d agreed, %d communication records" % (a["exchanges_agreed"], len(a["exchanges_recorded"])))
        for i in a["open_items"]:
            print("  open item %s (%s, due %s)%s: %s" % (i["item"], i["owner"], i["due"] or "-",
                  ", overdue %d days" % i["overdue_days"] if i["overdue_days"] else "", i["text"]))
        for c in a["corrective_actions"]:
            print("  corrective action %s %s" % (c["item"], c["state"]))
    print("%d supplier agreements" % len(data["agreements"]))
    return 0


def risks(project, as_of):
    """The risks with their exposure, treatment and indicators, as of a date."""
    plan = project.risk_plan()
    scale = plan.front.get("risk_scale") if plan and isinstance(plan.front.get("risk_scale"), dict) else {}
    limit = scale.get("acceptable_up_to")
    entries = []
    for risk in project.of_type("risk"):
        probability, impact = project.risk_numbers(risk)
        exposure = probability * impact if probability and impact else None
        actions = [a for a in as_list(risk.front.get("treatment")) if isinstance(a, dict)]
        overdue = [a.get("action") for a in actions if a.get("state") != "done" and as_date(a.get("due"))
                   and as_date(a.get("due")) < as_of]
        alarms = [i.get("name") for i in as_list(risk.front.get("indicators")) if isinstance(i, dict)
                  and i.get("value") is not None and i.get("threshold") is not None
                  and _number(i.get("value")) is not None and _number(i.get("threshold")) is not None
                  and _number(i.get("value")) >= _number(i.get("threshold"))]
        corrective = [{"item": a.id, "state": a.status} for a in project.of_type("corrective-action")
                      if risk.id in {t for t, _ in a.targets("addresses")}]
        entries.append({"item": risk.id, "title": risk.title, "state": risk.status, "category": risk.front.get("category"),
                        "owner": risk.front.get("owner"), "probability": probability, "impact": impact,
                        "exposure": exposure, "above_threshold": bool(limit and exposure and exposure > int(limit)),
                        "actions_open": sum(1 for a in actions if a.get("state") != "done"), "actions_overdue": overdue,
                        "indicators_at_threshold": alarms, "corrective_actions": corrective})
    entries.sort(key=lambda e: (-(e["exposure"] or 0), e["item"]))
    live = [e for e in entries if e["state"] not in ("closed", "rejected")]
    figures = {"live": len(live), "above_threshold": sum(1 for e in live if e["above_threshold"]),
               "in_treatment": sum(1 for e in live if e["state"] == "in-treatment"),
               "actions_overdue": sum(len(e["actions_overdue"]) for e in live),
               "indicators_at_threshold": sum(len(e["indicators_at_threshold"]) for e in live)}
    return {"as_of": str(as_of), "plan": plan.id if plan else None, "plan_status": plan.status if plan else None,
            "acceptable_up_to": limit, "risks": entries, "figures": figures}


def stamp(value):
    """A point in time from a datetime value or an ISO string, or None."""
    if isinstance(value, datetime.datetime):
        return value if value.tzinfo else value.replace(tzinfo=datetime.timezone.utc)
    try:
        moment = datetime.datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)


def written_before(first, second):
    """False only when both times are known and the first is later; a date alone cannot tell the order."""
    a, b = stamp(first), stamp(second)
    return not (a and b and len(str(first)) > 10 and len(str(second)) > 10 and a > b)


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cmd_risks(project, args):
    as_of = as_date(args.as_of) if args.as_of else datetime.date.today()
    if as_of is None:
        print("--as-of must be a date YYYY-MM-DD")
        return 2
    data = risks(project, as_of)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("Risks as of %s (plan %s, acceptable up to %s)" % (
        as_of, ("%s, %s" % (data["plan"], data["plan_status"]) if data["plan_status"] != "approved" else data["plan"])
        if data["plan"] else "none", data["acceptable_up_to"]))
    for e in data["risks"]:
        notes = []
        if e["actions_overdue"]:
            notes.append("overdue: %s" % "; ".join(map(str, e["actions_overdue"])))
        if e["indicators_at_threshold"]:
            notes.append("at threshold: %s" % ", ".join(map(str, e["indicators_at_threshold"])))
        print("%-9s %-12s %-10s exposure %-4s %s%s  %s" % (e["item"], e["state"], e["category"], e["exposure"],
              "above threshold " if e["above_threshold"] else "", " | ".join(notes), e["title"]))
    f = data["figures"]
    print("%d live risks, %d above the threshold, %d in treatment, %d treatment actions overdue, %d indicators at "
          "their threshold" % (f["live"], f["above_threshold"], f["in_treatment"], f["actions_overdue"],
                               f["indicators_at_threshold"]))
    return 0


def tara(project):
    """The threat scenarios with what their risk value rests on, highest risk first."""
    plan = project.cs_plan()
    method = plan.front.get("tara_method") if plan and isinstance(plan.front.get("tara_method"), dict) else None
    entries = []
    for threat in project.of_type("threat-scenario"):
        if not project.live(threat):
            continue
        impact, feasibility = project.highest_impact(threat), threat.front.get("feasibility")
        entries.append({
            "item": threat.id, "title": threat.title, "state": threat.status, "property": threat.front.get("property"),
            "assets": [t for t, _ in threat.targets("threatens")],
            "damage_scenarios": [t for t, _ in threat.targets("leads_to")],
            "impact": impact, "feasibility": feasibility,
            "attack_paths": len([p for p in as_list(threat.front.get("attack_paths")) if isinstance(p, dict)]),
            "risk_value": threat.front.get("risk_value"),
            "matrix_value": project.matrix_value(method, impact, feasibility) if method and impact else None,
            "treatment": [str(t) for t in as_list(threat.front.get("treatment"))],
            "goals": [g.id for g in project.sources(threat.id, "addresses", ["cybersecurity-goal"])],
            "claims": [c.id for c in project.sources(threat.id, "addresses", ["cybersecurity-claim"])],
            "imported": threat.imported})
    entries.sort(key=lambda e: (-(e["risk_value"] if isinstance(e["risk_value"], int) else 0), e["item"]))
    by_value = {str(v): sum(1 for e in entries if e["risk_value"] == v) for v in (5, 4, 3, 2, 1)}
    figures = {"threat_scenarios": len(entries), "by_risk_value": by_value,
               "untreated": sum(1 for e in entries if not e["treatment"]),
               "reduce_without_goal": sum(1 for e in entries if "reduce" in e["treatment"] and not e["goals"]),
               "kept_without_claim": sum(1 for e in entries if {"share", "retain"} & set(e["treatment"]) and not e["claims"]),
               "risk_value_differs": sum(1 for e in entries if e["matrix_value"] is not None
                                         and e["matrix_value"] != e["risk_value"]),
               "assets": len([a for a in project.of_type("asset") if project.live(a)]),
               "damage_scenarios": len([d for d in project.of_type("damage-scenario") if project.live(d)]),
               "goals": len([g for g in project.of_type("cybersecurity-goal") if project.live(g)]),
               "claims": len([c for c in project.of_type("cybersecurity-claim") if project.live(c)])}
    return {"plan": plan.id if plan else None, "feasibility_approach": (method or {}).get("feasibility_approach"),
            "threat_scenarios": entries, "figures": figures}


NOT_OURS = ("by-customer", "by-supplier", "by-organization", "not-applicable")


def clause_state(decision, structure, evidence, findings):
    """The observation for a clause, in the order the process gate reads it (references/standards.md there)."""
    if decision is None:
        return "not decided"
    if decision in NOT_OURS:
        return "not ours"
    if not structure:
        return "no evidence structure"
    if any(f["level"] == "error" for f in findings):
        return "findings open"
    if not evidence:
        return "no evidence yet"
    if any(e["status"] not in ("approved", "final") for e in evidence):
        return "evidence not settled"
    if findings:
        return "warnings open"
    return "evidence present"


def safety_rows(project, only=None):
    """Per clause of ISO 26262 under scope.safety (or of the part asked for): the decision of the safety plan,
    the items whose types give evidence for it, and the open findings of the rules behind it."""
    findings = project.check()
    plan = project.plan_in_work("safety")
    decisions = project.safety_entries(plan, "safety_activities", "clause")
    rows = []
    for part in fs_catalog()["parts"]:
        key = FS_PREFIX + str(part["id"])
        if (only and str(part["id"]) != str(only)) or (not only and key not in project.fs_scope):
            continue
        for clause in part["clauses"]:
            ref = "26262-%s:%s" % (part["id"], clause["id"])
            types = sorted(t for t, spec in project.types.items()
                           if any(str(s) == ref or str(s).startswith(ref + ".") for s in spec.get("supports") or []))
            kinds = sorted(k for k, refs in project.schema["plan_kinds"].items() if any(str(r) == ref or str(r).startswith(ref + ".") for r in refs))
            items = [i for i in project.items.values() if project.live(i) and (
                (i.type in types and i.type != "plan") or (i.type == "plan" and i.front.get("kind") in kinds))
                and project.fs_related(i)]
            own = {i.id for i in items if i.type not in ("review-record", "test-run")}
            items = [i for i in items if covers_own(i, own)]
            entry = decisions.get("%s:%s" % (part["id"], clause["id"])) or {}
            open_findings = [f for f in findings if f["level"] != "info"
                             and any(str(s) == ref or str(s).startswith(ref + ".") for s in f["supports"])]
            rows.append({"clause": "%s:%s" % (part["id"], clause["id"]), "name": clause["name"],
                         "in_scope": key in project.fs_scope, "decision": entry.get("decision"),
                         "plan": "%s (%s)" % (plan.id, plan.status) if plan else None,
                         "responsible": entry.get("responsible"),
                         "items": len(items), "approved_or_final": sum(1 for i in items if i.status in ("approved", "final")),
                         "types": sorted({i.type for i in items}) or types + ["plan of kind %s" % k for k in kinds],
                         "evidence": [{"item": i.id, "status": i.status, "hash": i.hash} for i in sorted(items, key=lambda i: i.id)],
                         "findings": [{"rule": f["rule"], "item": f["item"], "level": f["level"], "message": f["message"]}
                                      for f in open_findings]})
            rows[-1]["state"] = clause_state(rows[-1]["decision"], bool(types or kinds), rows[-1]["evidence"], open_findings)
    return rows


def cmd_safety(project, args):
    rows = safety_rows(project, args.part)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("no part of ISO 26262 is under scope.safety in project.yaml" if not args.part
              else "%s is not a part of ISO 26262 with clauses (2 to 9, 12)" % args.part)
        return 0
    for row in rows:
        decision = ("%s, %s" % (row["decision"], row["responsible"]) if row["decision"] else "no entry in the safety plan") \
            + ("; plan %s" % row["plan"] if row["plan"] and not row["plan"].endswith("(approved)") else "")
        evidence = "%d items (%d approved or final; %s)" % (row["items"], row["approved_or_final"], ", ".join(row["types"])) \
            if row["items"] else "no evidence (%s)" % (", ".join(row["types"]) or "no item type of the toolkit")
        print("26262-%-6s %s  [%s]\n    %s: %s" % (row["clause"], row["name"], decision, row["state"], evidence))
        for f in row["findings"]:
            print("    %-7s %-7s %-10s %s" % (f["level"], f["rule"], f["item"], f["message"]))
    events = [e for e in project.of_type("hazardous-event") if project.live(e)]
    if events:
        print("\nHazardous events by ASIL:")
        for event in sorted(events, key=lambda e: (-ASIL_RANK.get(str(e.front.get("asil")), 0), e.id)):
            goals = [g.id for g in project.sources(event.id, "addresses", ["safety-goal"])]
            print("  %-9s ASIL %-3s %s%s%s  goals: %s  %s" % (event.id, event.front.get("asil"), event.front.get("severity"),
                  event.front.get("exposure"), event.front.get("controllability"), ", ".join(goals) or "-", event.title))
    return 0


def cmd_tara(project, args):
    data = tara(project)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("TARA (plan %s, feasibility approach %s)" % (data["plan"] or "none approved", data["feasibility_approach"] or "-"))
    for e in data["threat_scenarios"]:
        value = "%s" % e["risk_value"]
        if e["matrix_value"] is not None and e["matrix_value"] != e["risk_value"]:
            value += " (matrix %s)" % e["matrix_value"]
        handled = ", ".join(e["goals"] + e["claims"]) or "-"
        print("%-9s %-10s risk %-12s impact %-10s feasibility %-8s %-14s by %-20s %s" % (
            e["item"], e["state"], value, e["impact"] or "-", e["feasibility"] or "-",
            "/".join(e["treatment"]) or "untreated", handled, e["title"]))
    f = data["figures"]
    print("%d threat scenarios (risk 5..1: %s), %d assets, %d damage scenarios, %d goals, %d claims | %d untreated, "
          "%d reduce without a goal, %d retained or shared without a claim, %d risk values differ from the matrix"
          % (f["threat_scenarios"], " ".join(str(f["by_risk_value"][k]) for k in ("5", "4", "3", "2", "1")),
             f["assets"], f["damage_scenarios"], f["goals"], f["claims"], f["untreated"], f["reduce_without_goal"],
             f["kept_without_claim"], f["risk_value_differs"]))
    return 0


def covers_own(record, own):
    """A review or a test run counts for a clause only when it covers items of the clause itself."""
    if record.type == "review-record":
        return bool({str(e.get("item")) for e in as_list(record.front.get("subject")) if isinstance(e, dict)} & own)
    if record.type == "test-run":
        return bool({str(e.get("test")) for e in as_list(record.front.get("results")) if isinstance(e, dict)} & own)
    return True


def clause_rows(project, only=None):
    """Per subclause of ISO/SAE 21434 in scope (or the clause asked for): the decision of the cybersecurity plan,
    the items that provide each work product, and the open findings of the rules behind the subclause."""
    findings = project.check()
    plan = project.plan_in_work("cybersecurity")
    decisions = {str(e.get("subclause")): e for e in as_list(plan.front.get("cybersecurity_activities") if plan else [])
                 if isinstance(e, dict)}
    plans = defaultdict(list)
    for p in project.of_type("plan"):
        for ref in project.schema["plan_kinds"].get(p.front.get("kind"), []):
            plans[str(ref)].append(p)
    rows = []
    for clause in cs_catalog()["clauses"]:
        key = CS_PREFIX + str(clause["id"])
        if (only and str(clause["id"]) != str(only)) or (not only and key not in project.cs_scope):
            continue
        for sub in clause["subclauses"]:
            ref = CS_PREFIX + str(sub["id"])
            found = []
            for wp in sub["work_products"]:
                wref = CS_PREFIX + wp
                types = [t for t, spec in project.types.items() if wref in map(str, spec.get("supports") or [])]
                items = [i for i in project.items.values() if i.type in types and project.live(i)
                         and i.type != "plan" and project.cs_related(i)] + plans.get(wref, [])
                for role, link in project.schema["links"].items():       # evidence carried by a link, e.g. the concept
                    for pair in link["pairs"]:
                        if wref in map(str, pair.get("supports") or []):
                            types.append(pair["from"])
                            items += [i for i in project.of_type(pair["from"]) if project.live(i) and i not in items
                                      and any(pair["to"] == "any" or getattr(project.items.get(t), "type", None) in pair["to"]
                                              for t, _ in i.targets(role))]
                found.append((wp, sorted(set(types)), items))
            own = {i.id for _, _, items in found for i in items if i.type not in ("review-record", "test-run")}
            products = []
            for wp, types, items in found:
                items = [i for i in items if covers_own(i, own)]       # a review of other items is not evidence here
                products.append({"work_product": wp, "name": next((w["name"] for w in cs_catalog()["work_products"]
                                                                   if w["id"] == wp), ""),
                                 "items": len(items), "approved_or_final": sum(1 for i in items if i.status in ("approved", "final")),
                                 "types": sorted({i.type for i in items}) or types,
                                 "evidence": [{"item": i.id, "status": i.status, "hash": i.hash}
                                              for i in sorted(items, key=lambda i: i.id)]})
            open_findings = [f for f in findings if ref in map(str, f["supports"]) and f["level"] != "info"]
            entry = decisions.get(str(sub["id"])) or {}
            evidence = [e for wp in products for e in wp["evidence"]]
            structure = any(wp["types"] for wp in products) or any(ref in map(str, r["supports"]) for r in project.schema["coverage"])
            rows.append({"subclause": str(sub["id"]), "name": sub["name"], "in_scope": key in project.cs_scope,
                         "decision": entry.get("decision"), "responsible": entry.get("responsible"),
                         "state": clause_state(entry.get("decision"), structure, evidence, open_findings),
                         "work_products": products,
                         "findings": [{"rule": f["rule"], "item": f["item"], "level": f["level"], "message": f["message"]}
                                      for f in open_findings]})
    return rows


def cmd_clauses(project, args):
    rows = clause_rows(project, args.clause)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("no clause of ISO/SAE 21434 is under scope.cybersecurity in project.yaml" if not args.clause
              else "%s is not a clause of ISO/SAE 21434 (5 to 15)" % args.clause)
        return 0
    for row in rows:
        decision = "%s, %s" % (row["decision"], row["responsible"]) if row["decision"] else "no entry in the cybersecurity plan"
        print("21434:%-7s %s  [%s]  %s" % (row["subclause"], row["name"], decision, row["state"]))
        for wp in row["work_products"]:
            print("    %s %s: %s" % (wp["work_product"], wp["name"], "%d items (%d approved or final; %s)"
                                    % (wp["items"], wp["approved_or_final"], ", ".join(wp["types"]))
                                    if wp["items"] else "none" + (" (types: %s)" % ", ".join(wp["types"]) if wp["types"]
                                                                  else " (no item type of the toolkit)")))
        for f in row["findings"]:
            print("    %-7s %-7s %-10s %s" % (f["level"], f["rule"], f["item"], f["message"]))
    return 0


def cmd_quality(project, args):
    as_of = as_date(args.as_of) if args.as_of else datetime.date.today()
    if as_of is None:
        print("--as-of must be a date YYYY-MM-DD")
        return 2
    data = quality(project, as_of)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("Quality assurance as of %s (plan %s)" % (as_of, data["plan"] or "none approved"))
    for c in data["checks"]:
        print("check %-28s %-12s performed %d times, last %s %s %s" % (c["name"], c["kind"], c["performed"],
              c["last"] or "-", c["last_at"] or "", c["last_result"] or ""))
    for f in data["findings"]:
        line = "finding %s#%s  action %s %s" % (f["record"], f["finding"], f["action"], f["state"])
        if f["overdue_days"]:
            line += ", overdue %d days" % f["overdue_days"]
        if f["escalation_due"]:
            line += ", escalation due to %s" % ", ".join(f["escalation_due"])
        if f["escalated_to"]:
            line += ", escalated to %s" % ", ".join(f["escalated_to"])
        print(line)
    for s in data["summaries"]:
        print("report %s %s %s, %s" % (s["record"], s["checked_at"], s["result"],
                                       "communicated" if s["communicated"] else "not communicated"))
    fig = data["figures"]
    print("%d checks planned (%d never performed); %d quality records, %d conforming; %d findings, %d open, %d overdue, "
          "%d escalations due; not yet in a report: %s"
          % (fig["checks_planned"], fig["checks_never_performed"], fig["records"], fig["conforming"], fig["findings"],
             fig["findings_open"], fig["findings_overdue"], fig["escalations_due"], ", ".join(fig["not_summarised"]) or "-"))
    return 0


def cmd_problems(project, args):
    as_of = as_date(args.as_of) if args.as_of else datetime.date.today()
    if as_of is None:
        print("--as-of must be a date YYYY-MM-DD")
        return 2
    data = problems(project, as_of)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print("Problems as of %s (states as they are now; ages to that date)" % as_of)
    for e in data["problems"]:
        changes = ", ".join("%s %s" % (c["item"], c["state"]) for c in e["change_requests"]) or "-"
        print("%-9s %-13s %-8s %-18s %-19s age %4s days  affects %s  changes %s  %s"
              % (e["item"], e["state"], e["severity"], e["origin"] or "-", e["detected_by"], e["age_days"],
                 ", ".join(e["affects"]) or "-", changes, e["title"]))
    f = data["figures"]
    print("%d problems, %d unresolved, %d rejected | by severity: %s | by origin: %s | by detection: %s | "
          "unresolved by age: %s"
          % (f["total"], f["unresolved"], f["rejected"],
             ", ".join("%s %d" % kv for kv in f["by_severity"].items()) or "-",
             ", ".join("%s %d" % kv for kv in f["by_origin"].items()) or "-",
             ", ".join("%s %d" % kv for kv in f["by_detection"].items()) or "-",
             ", ".join("%s %d" % kv for kv in f["unresolved_by_age"].items())))
    return 0


def cmd_history(project, args):
    """The states an item had in the commits that changed its file, oldest first."""
    item = project.items.get(args.id)
    if item is None:
        print("no such item: %s" % args.id)
        return 1
    rel = item.path.relative_to(project.root).as_posix()
    done = subprocess.run(["git", "log", "--follow", "--format=%h %ad", "--date=short", "--", rel],
                          cwd=str(project.root), capture_output=True, text=True)
    if done.returncode != 0:
        print("NOT ASSESSED: the history is read from git, and git gave: %s" % done.stderr.strip())
        return 2
    commits = [line.split(" ", 1) for line in reversed(done.stdout.strip().splitlines()) if line.strip()]
    last = None
    for commit, date in commits:
        shown = subprocess.run(["git", "show", "%s:./%s" % (commit, rel)], cwd=str(project.root),
                               capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        match = FRONT_MATTER.match(shown.replace("\r\n", "\n"))
        try:
            status = str((yaml.safe_load(match.group(1)) or {}).get("status")) if match else "?"
        except yaml.YAMLError:
            status = "?"
        if status != last:
            print("%s  %s  %s" % (date, commit, status))
            last = status
    if not commits:
        print("%s is in no commit yet: its history starts with the next commit" % item.id)
    elif item.status != last:
        print("%-10s  %-7s  %s" % ("now", "working", item.status))
    return 0


def reviewed_text(item, reviewed_hash):
    """(text, commit) of the item file as it was when it had the given content hash, from git; or (None, reason)."""
    folder, name = item.path.parent, item.path.name

    def git(*arguments):
        done = subprocess.run(["git", "-C", str(folder)] + list(arguments), capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        return done.stdout if done.returncode == 0 else None

    commits = git("log", "--format=%H", "--", name)
    if commits is None:
        return None, "the project is not under git, or git is not available"
    for commit in commits.split():
        text = git("show", "%s:./%s" % (commit, name))
        match = FRONT_MATTER.match((text or "").replace("\r\n", "\n"))
        if not match:
            continue
        try:
            front = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            continue
        if isinstance(front, dict) and content_hash(front, match.group(2)) == reviewed_hash:
            return text.replace("\r\n", "\n"), commit[:12]
    return None, "no commit holds %s at hash %s" % (name, reviewed_hash)


def cmd_diff(project, args):
    item = project.items.get(args.id)
    if item is None:
        print("no such item: %s" % args.id)
        return 1
    def seen_in(record):
        return next((str(e.get("hash")) for name in ("subject", "references") for e in as_list(record.front.get(name))
                     if isinstance(e, dict) and e.get("item") == item.id), None)

    reviews = [r for r in project.of_type("review-record") if r.status == "final" and seen_in(r)]
    if args.since:
        reviews = [r for r in reviews if r.id == args.since]
        if not reviews:
            print("%s is not a final review record that lists %s as subject or reference" % (args.since, item.id))
            return 1
    if not reviews:
        print("no final review record has %s as subject: there is nothing to compare with" % item.id)
        return 1
    review = max(reviews, key=lambda r: record_number(r.id))
    reviewed = seen_in(review)
    if reviewed == item.hash:
        print("%s is unchanged since %s (hash %s)" % (item.id, review.id, item.hash))
        return 0
    text, where = reviewed_text(item, reviewed)
    if text is None:
        print("NOT ASSESSED: the text %s saw of %s (hash %s) cannot be found: %s. Without it, the whole item is "
              "reviewed again. Commit items and records after every recorded review." % (review.id, item.id, reviewed, where))
        return 2
    now = item.path.read_text(encoding="utf-8").replace("\r\n", "\n")
    print("%s: changed since %s (hash %s, commit %s -> hash %s, working tree)" % (item.id, review.id, reviewed, where, item.hash))
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), now.splitlines(True),
                                               "%s as %s saw it" % (item.id, review.id), "%s now" % item.id, n=2))
    return 0


def cmd_status(project, args):
    table = defaultdict(lambda: defaultdict(int))
    for item in project.items.values():
        table[item.type][item.status] += 1
    for type_name in project.types:
        if type_name in table:
            print("%-28s %s" % (type_name, ", ".join("%d %s" % (n, s) for s, n in sorted(table[type_name].items()))))
    for type_name, (process, level) in TEST_TYPES.items():
        run = project.latest_run("test-run", level=level)
        if run:
            verdicts = defaultdict(int)
            for entry in as_list(run.front.get("results")):
                verdicts[entry.get("verdict")] += 1
            print("latest %s test run %s on %s: %s" % (level, run.id, run.front.get("item_under_test"),
                                                     ", ".join("%d %s" % (n, v) for v, n in sorted(verdicts.items()))))
    for step in project.integration_steps():
        build = latest(project.builds_of(step.get("name")))
        if build:
            print("latest build of step '%s' %s on %s: %s" % (step.get("name"), build.id,
                                                            build.front.get("item_under_test"), build.front.get("result")))
    return 0


def cmd_audit(project, args):
    base = project.items.get(args.id)
    if base is None or base.type != "baseline":
        print("no such baseline: %s" % args.id)
        return 1
    stored = {e.get("item"): e for e in as_list(base.front.get("items")) if isinstance(e, dict)}
    differences = []
    for item_id, entry in sorted(stored.items()):
        now = project.items.get(item_id)
        if now is None:
            differences.append("%s  missing: listed in the baseline, not in the project" % item_id)
        elif now.hash != str(entry.get("hash")):
            differences.append("%s  content changed: baseline %s, now %s" % (item_id, entry.get("hash"), now.hash))
        elif now.status != entry.get("status"):
            differences.append("%s  status changed: baseline %s, now %s" % (item_id, entry.get("status"), now.status))
    for item in sorted(project.items.values(), key=lambda i: i.id):
        if project.types[item.type]["lifecycle"] == "engineering" and item.status == "approved" and item.id not in stored:
            differences.append("%s  not listed: approved in the project, absent from the baseline" % item.id)
    for line in differences:
        print(line)
    print("%s (%s, tag %s): %d items listed, %d differences from the project as it is now"
          % (base.id, base.front.get("purpose"), base.front.get("tag"), len(stored), len(differences)))
    print("run this at the tagged commit to verify the baseline itself; run it later to see what moved on since")
    return 1 if differences else 0


def cmd_list(project, args):
    for item in sorted(project.items.values(), key=lambda i: (i.type, record_number(i.id))):
        if (args.type and item.type != args.type) or (args.status and item.status != args.status) \
                or (args.imported and not item.imported):
            continue
        print("%-10s %-11s %-28s %s" % (item.id, item.status, item.type, item.title))
    return 0


def practice_rows(project, process_id=None):
    """One row per base practice: evidence held and findings open. Observations only, no verdict."""
    version = str((project.config.get("aspice") or {}).get("version") or project.schema.get("aspice_version"))
    folder = ROOT / "aspice" / version / "processes"
    wanted = [process_id] if process_id else sorted(project.scope or [f.stem for f in folder.glob("*.yaml")])
    findings = project.check()
    schema = project.schema
    rows = []
    for pid in wanted:
        source = folder / (pid + ".yaml")
        if not source.is_file():
            rows.append({"practice": pid, "name": "process is not in the catalog", "state": "not assessed",
                         "evidence": 0, "settled": 0, "errors": 0, "warnings": 0, "by": []})
            continue
        for bp in yaml.safe_load(source.read_text(encoding="utf-8"))["base_practices"]:
            ref = bp["id"]
            refs = set(bp["maps_to"]) if "maps_to" in bp else {ref}     # 4.0: the 3.1 practices that carry it
            types = [name for name, spec in schema["types"].items() if refs & set(map(str, spec.get("supports") or []))]
            kinds = [kind for kind, kind_refs in schema["plan_kinds"].items() if refs & set(map(str, kind_refs))]
            if kinds and "plan" not in types:            # a strategy practice is evidenced by its plan
                types.append("plan")
            review_kinds = {SUPPLIER_REVIEW_KINDS[r] for r in refs if r in SUPPLIER_REVIEW_KINDS}
            roles = sorted({role for role, link in schema["links"].items()
                            for pair in link["pairs"] if refs & set(map(str, pair["supports"]))})
            rules = sorted(r["id"] for r in schema["coverage"] if refs & set(map(str, r["supports"])))
            held = [i for i in project.items.values() if i.type in types and project.live(i)
                    and (i.type != "plan" or i.front.get("kind") in kinds or not kinds)
                    and (i.type != "test-run" or RUN_LEVELS.get(i.front.get("level")) == pid)
                    and (i.type != "supplier-review" or not review_kinds or i.front.get("kind") in review_kinds)
                    and (i.type != "communication-record" or not i.front.get("practices")
                         or (refs | {ref}) & set(map(str, as_list(i.front.get("practices")))))]
            if not types:                                 # evidenced by links or rules only: count what carries them
                carriers = {i.id: i for role, link in schema["links"].items() for pair in link["pairs"]
                            if refs & set(map(str, pair["supports"])) for i in project.of_type(pair["from"])
                            if project.live(i) and i.targets(role)}
                subjects = {r["subject"] for r in schema["coverage"] if refs & set(map(str, r["supports"]))}
                carriers.update({i.id: i for i in project.items.values()
                                 if not roles and i.type in subjects and project.live(i)})
                held = list(carriers.values())
            settled = [i for i in held
                       if i.status in project.lifecycle(i).get("stages", {}).get("before-approval", [])]
            mine = [f for f in findings if refs & set(map(str, f["supports"]))]
            errors = sum(1 for f in mine if f["level"] == "error")
            warnings = sum(1 for f in mine if f["level"] == "warning")
            if not (types or roles or rules):
                state = "no evidence structure"          # the schema has nothing for this practice yet
            elif errors:
                state = "findings open"
            elif not held:
                state = "no evidence yet"
            elif held and len(settled) < len(held):
                state = "evidence not settled"           # items exist but are not all approved or final
            elif warnings:
                state = "warnings open"
            else:
                state = "evidence present"
            rows.append({"practice": ref, "name": bp["name"], "state": state, "evidence": len(held),
                         "settled": len(settled), "errors": errors, "warnings": warnings,
                         "by": types + ["link " + r for r in roles] + rules
                         + (["as 3.1 %s" % ", ".join(sorted(refs))] if "maps_to" in bp and refs else [])})
    return rows


STATE_RANK = {"findings open": 0, "no evidence yet": 1, "evidence not settled": 2, "warnings open": 3,
              "evidence present": 4, "no evidence structure": 5}


def generic_rows(project, process_id):
    """Per generic practice of level 2, what the repository holds for one process. Observations only.
    For a model whose generic practices map onto those of 3.1 (`maps_to` in its capability levels), the
    observations of the mapped practices are combined: the worst state, all evidence, all notes."""
    version = str((project.config.get("aspice") or {}).get("version") or project.schema.get("aspice_version"))
    catalog = yaml.safe_load((ROOT / "aspice" / version / "capability-levels.yaml").read_text(encoding="utf-8"))
    practices = [g for pa in catalog["process_attributes"] if pa["id"] in ("PA 2.1", "PA 2.2")
                 for g in pa.get("generic_practices", [])]
    rows = generic_rows_31(project, process_id, version)
    if not any("maps_to" in g for g in practices):
        return rows
    by_id = {r["practice"]: r for r in rows}
    out = []
    for gp in practices:
        mapped = [by_id[g] for g in gp.get("maps_to") or [] if g in by_id]
        if not mapped:
            out.append({"practice": gp["id"], "name": gp["name"], "state": "no evidence structure", "evidence": [], "note": ""})
            continue
        out.append({"practice": gp["id"], "name": gp["name"],
                    "state": min((r["state"] for r in mapped), key=lambda s: STATE_RANK.get(s, 9)),
                    "evidence": sorted({e for r in mapped for e in r["evidence"]}),
                    "note": "; ".join("%s (3.1): %s" % (r["practice"], r["note"]) for r in mapped if r["note"])})
    return out


def generic_rows_31(project, process_id, version):
    catalog = yaml.safe_load((ROOT / "aspice" / "3.1" / "capability-levels.yaml").read_text(encoding="utf-8"))
    names = {g["id"]: g["name"] for pa in catalog["process_attributes"] if pa["id"] in ("PA 2.1", "PA 2.2")
             for g in pa.get("generic_practices", [])}
    schema = project.schema
    findings = project.check()
    bps = [r for bp in yaml.safe_load((ROOT / "aspice" / version / "processes" / (process_id + ".yaml"))
                                      .read_text(encoding="utf-8"))["base_practices"]
           for r in (bp["maps_to"] if "maps_to" in bp else [bp["id"]])]
    kinds = [kind for kind, refs in schema["plan_kinds"].items() if set(refs) & set(bps)]
    types = [name for name, spec in schema["types"].items() if set(map(str, spec.get("supports") or [])) & set(bps)
             and name not in ("communication-record", "review-record", "plan")]
    live = [i for i in project.items.values() if project.live(i) and not i.imported]
    plans = [i for i in live if i.type == "plan" and i.front.get("kind") in kinds]
    products = [i for i in live if i.type in types and schema["types"][i.type]["lifecycle"] == "engineering"] + plans
    product_ids = {i.id for i in products}
    packages = [i for i in live if i.type == "work-package" and i.front.get("process") == process_id]
    settled = lambda items: all(i.status in SETTLED.get(project.types[i.type]["lifecycle"], ()) for i in items)  # noqa: E731
    rows = []

    def row(gp, state, evidence, note):
        rows.append({"practice": gp, "name": names.get(gp, ""), "state": state, "evidence": sorted(evidence),
                     "note": note})

    def held(items, note, empty="no evidence yet"):
        if not items:
            return empty, [], note
        return ("evidence present" if settled(items) else "evidence not settled"), [i.id for i in items], note

    state, ids, note = held([w for w in packages if w.front.get("estimate") and w.front.get("planned_finish")],
                            "work packages with `process: %s`, their estimates and dates; quality objectives are in the "
                            "strategy of the process" % process_id)
    row("GP 2.1.1", state, ids, note)
    with_activities = [w for w in packages if as_list(w.front.get("activities"))]
    if packages and len(with_activities) < len(packages):
        row("GP 2.1.2", "evidence not settled", [w.id for w in with_activities],
            "%d of %d work packages of the process have activities" % (len(with_activities), len(packages)))
    else:
        row("GP 2.1.2", *held(with_activities, "activities with owner, estimate and date in the work packages"))
    reports = [r for r in project.of_type("project-status-report") if r.status == "final"
               and {str(e.get("item")) for e in as_list(r.front.get("work_packages")) if isinstance(e, dict)}
               & {w.id for w in packages}]
    tracked = [w for w in packages if isinstance(w.front.get("progress"), dict)]
    if reports and tracked:
        row("GP 2.1.3", "evidence present", [r.id for r in reports] + [w.id for w in tracked],
            "status reports that list the work packages, and their progress as stated by the owners")
    else:
        row("GP 2.1.3", "evidence not settled" if (reports or tracked) else "no evidence yet",
            [r.id for r in reports] + [w.id for w in tracked], "status reports and stated progress of the work packages")
    targets = {w.id for w in packages} | product_ids
    actions = [a for a in project.of_type("corrective-action") if {x for x, _ in a.targets("addresses")} & targets]
    row("GP 2.1.4", *held(actions, "corrective actions that address the work packages or items of the process; "
                                   "whether one was needed is for a person to judge", empty="a person has to judge"))
    with_roles = [pl for pl in plans if pl.has_section("Responsibilities")]
    owners = [w for w in packages if w.front.get("owner")]
    row("GP 2.1.5", *held(with_roles + owners, "`Responsibilities` of the strategy, owners of the work packages; "
                                               "that the people know their roles is for a person to judge"))
    toolchain = any(v for v in ((project.config.get("toolchain") or {}).values()))
    resourced = [pl for pl in plans if pl.has_section("Environment and tools")] + \
        [w for w in packages if any(isinstance(a, dict) and a.get("skill") for a in as_list(w.front.get("activities")))]
    if resourced and toolchain:
        row("GP 2.1.6", *held(resourced, "`Environment and tools` of the strategy, `toolchain` of project.yaml, skills "
                                         "named in activities; training and availability are not in the repository"))
    else:
        row("GP 2.1.6", "evidence not settled" if (resourced or toolchain) else "no evidence yet", [i.id for i in resourced],
            "`toolchain` of project.yaml is %s" % ("set" if toolchain else "empty"))
    baselines = [b for b in project.of_type("baseline") if b.status == "final"]
    listed = {str(e.get("item")): b.id for b in baselines for e in as_list(b.front.get("items")) if isinstance(e, dict)}
    told = [c for c in project.of_type("communication-record") if c.status == "final" and (
        set(map(str, as_list(c.front.get("practices")))) & set(bps)
        or {str(s) for s in as_list(c.front.get("subject"))} & (product_ids | {listed.get(i) for i in product_ids}))]
    asked = [q for q in project.of_type("query") if {x for x, _ in q.targets("about")} & product_ids]
    row("GP 2.1.7", *held(told + asked, "communication records and queries about the items of the process"))
    checklists = []
    for path in sorted((ROOT / ".claude" / "docs" / "checklists").glob("*.md")):
        head = path.read_text(encoding="utf-8").split("\n\n## ")[0]
        if any("`%s`" % name in head for name in types + (["plan"] if kinds else [])):
            checklists.append(path.stem)
    row("GP 2.2.1", "evidence present" if types or kinds else "no evidence structure", checklists,
        "the item types of the schema and the review checklists %s; the project's own criteria, where it has any, are "
        "for a person" % (", ".join(checklists) or "-"))
    cm = [pl for pl in live if pl.type == "plan" and pl.front.get("kind") == "configuration-management"]
    row("GP 2.2.2", *held(cm, "the configuration management plan; identification, versions and links come from the "
                              "item format and the schema"))
    internal = as_list((project.config.get("trace") or {}).get("internal_baselines"))
    frozen = {str(e.get("item")) for b in baselines if b.front.get("purpose") not in internal
              for e in as_list(b.front.get("items")) if isinstance(e, dict)}
    engineering = [i for i in products if project.types[i.type]["lifecycle"] == "engineering"]
    inside = [i for i in engineering if i.id in frozen]
    if engineering and len(inside) == len(engineering):
        row("GP 2.2.3", "evidence present", [b.id for b in baselines], "every item of the process is in a baseline")
    else:
        row("GP 2.2.3", "evidence not settled" if inside or engineering else "no evidence yet", [i.id for i in inside],
            "%d of %d items of the process are in a baseline that is not internal; all are under version control"
            % (len(inside), len(engineering)))
    reviewed = [i for i in engineering if project.approving_review(i)]
    open_review = [f for f in findings if f["rule"] in ("COV-19", "SUSPECT", "CONSISTENCY") and f["level"] == "error"
                   and f["item"] in product_ids]
    checked = [q for q in project.of_type("quality-record") if q.status == "final" and q.front.get("kind") == "work-product"
               and {str(s) for s in as_list(q.front.get("subject"))} & product_ids]
    if open_review:
        row("GP 2.2.4", "findings open", [f["item"] for f in open_review], "items whose approval is stale or suspect")
    elif engineering and len(reviewed) == len(engineering):
        row("GP 2.2.4", "evidence present", list({project.approving_review(i).id for i in reviewed}) + [q.id for q in checked],
            "every item of the process has an approving review of its present content%s; whether the reviews were held "
            "as planned is for a person" % ("; quality records check a sample" if checked else ""))
    else:
        row("GP 2.2.4", "evidence not settled" if engineering else "no evidence yet", [i.id for i in reviewed],
            "%d of %d items of the process have an approving review" % (len(reviewed), len(engineering)))
    return rows


def model_caveat(project):
    """The line a reader of practices and generic needs when the catalog is not the released 3.1 model."""
    version = str((project.config.get("aspice") or {}).get("version") or project.schema.get("aspice_version"))
    levels = ROOT / "aspice" / version / "capability-levels.yaml"
    source = (yaml.safe_load(levels.read_text(encoding="utf-8")) or {}).get("source") if levels.is_file() else None
    if version == "3.1":
        return None
    return ("Automotive SPICE %s%s: practices are evidenced through the 3.1 practices each maps to (`as 3.1`); "
            "rules, checklists and notes are those of 3.1" % (version, " from the %s, not for assessments" % source
                                                             if source and "draft" in str(source) else ""))


def cmd_generic(project, args):
    wanted = [args.process] if args.process else sorted(project.scope or [])
    out = []
    version = str((project.config.get("aspice") or {}).get("version") or project.schema.get("aspice_version"))
    for pid in wanted:
        if not (ROOT / "aspice" / version / "processes" / (pid + ".yaml")).is_file():
            print("%s is not a process of the catalog" % pid)
            return 1
        out += [dict(r, process=pid) for r in generic_rows(Project(project.root), pid)]
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    caveat = model_caveat(project)
    if caveat:
        print(caveat)
    for r in out:
        print("%-7s %-9s %-22s %3d  %s" % (r["process"], r["practice"], r["state"], len(r["evidence"]), r["note"]))
    print("observations of what the repository holds per generic practice of level 2, not ratings; much of level 2 "
          "lies with people and outside the files")
    return 0


def cmd_practices(project, args):
    if args.process and project.scope is not None and args.process not in project.scope:
        print("%s is not in the scope of this project (%s)" % (args.process, ", ".join(sorted(project.scope))))
        return 1
    rows = practice_rows(project, args.process)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    caveat = model_caveat(project)
    if caveat:
        print(caveat)
    print("%-11s %-22s %8s %8s %6s %8s  %s" % ("practice", "state", "evidence", "settled", "errors", "warnings", "name"))
    for row in rows:
        print("%-11s %-22s %8d %8d %6d %8d  %s" % (row["practice"], row["state"], row["evidence"], row["settled"],
                                                 row["errors"], row["warnings"], row["name"]))
    print("states are observations, not ratings: 'evidence present' means items exist, are approved or final, "
          "and no rule in the schema objects; whether the practice is performed well is for a person to judge")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".", help="project root (default: current directory)")
    sub = ap.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--all", action="store_true")
    check.add_argument("--json", action="store_true")
    sub.add_parser("matrix")
    sub.add_parser("show").add_argument("id")
    sub.add_parser("impact").add_argument("id")
    hashes = sub.add_parser("hash")
    hashes.add_argument("ids", nargs="*")
    hashes.add_argument("--upstream", action="store_true")
    sub.add_parser("status")
    sub.add_parser("audit").add_argument("id")
    progress_parser = sub.add_parser("progress")
    progress_parser.add_argument("--as-of", help="the date to measure against (default: today)")
    progress_parser.add_argument("--json", action="store_true")
    diff = sub.add_parser("diff")
    diff.add_argument("id")
    diff.add_argument("--since", help="the review record to compare with (default: the newest that has the item as subject)")
    listing = sub.add_parser("list")
    listing.add_argument("--type")
    listing.add_argument("--status")
    listing.add_argument("--imported", action="store_true", help="only inputs received from outside the scope")
    problems_parser = sub.add_parser("problems")
    problems_parser.add_argument("--as-of", help="the date ages are measured to (default: today)")
    problems_parser.add_argument("--json", action="store_true")
    sub.add_parser("history").add_argument("id")
    risks_parser = sub.add_parser("risks")
    risks_parser.add_argument("--as-of", help="the date lateness is measured to (default: today)")
    risks_parser.add_argument("--json", action="store_true")
    suppliers_parser = sub.add_parser("suppliers")
    suppliers_parser.add_argument("--as-of", help="the date lateness is measured to (default: today)")
    suppliers_parser.add_argument("--json", action="store_true")
    quality_parser = sub.add_parser("quality")
    quality_parser.add_argument("--as-of", help="the date lateness is measured to (default: today)")
    quality_parser.add_argument("--json", action="store_true")
    generic = sub.add_parser("generic")
    generic.add_argument("process", nargs="?")
    generic.add_argument("--json", action="store_true")
    practices = sub.add_parser("practices")
    practices.add_argument("process", nargs="?")
    practices.add_argument("--json", action="store_true")
    safety = sub.add_parser("safety")
    safety.add_argument("part", nargs="?", help="a part of ISO 26262; default: the parts in scope")
    safety.add_argument("--json", action="store_true")
    tara_parser = sub.add_parser("tara")
    tara_parser.add_argument("--json", action="store_true")
    clauses = sub.add_parser("clauses")
    clauses.add_argument("clause", nargs="?", help="a clause number of ISO/SAE 21434; default: the clauses in scope")
    clauses.add_argument("--json", action="store_true")
    args = ap.parse_args()
    project = Project(args.project)
    return {"check": cmd_check, "matrix": cmd_matrix, "show": cmd_show, "impact": cmd_impact,
            "hash": cmd_hash, "status": cmd_status, "list": cmd_list, "audit": cmd_audit, "practices": cmd_practices,
            "diff": cmd_diff, "progress": cmd_progress,
            "problems": cmd_problems, "history": cmd_history, "quality": cmd_quality, "generic": cmd_generic,
            "suppliers": cmd_suppliers, "risks": cmd_risks, "tara": cmd_tara, "clauses": cmd_clauses,
            "safety": cmd_safety}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
