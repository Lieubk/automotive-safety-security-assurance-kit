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
    status             items per type and state, and the latest verification runs

Options
    --project DIR      project root (default: current directory)
    --all              `check`: also list findings on items still in draft
    --json             `check`: findings as JSON

File layout and hash definition: schema/item-format.md. Rules: schema/items.yaml.
Requires PyYAML. Exit code of `check`: 0 = no errors, 1 = errors.
"""
import argparse
import fnmatch
import hashlib
import json
import re
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
VERDICTS = {"passed", "failed", "blocked", "not-run"}
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.S)
HEADING = re.compile(r"^##\s+(.+?)\s*$")
C_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
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


def content_hash(front, body):
    data = {k: v for k, v in front.items() if k != "status"}
    head = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    lines = [line.rstrip() for line in body.replace("\r\n", "\n").split("\n")]
    text = "\n".join(lines).strip("\n")
    return hashlib.sha256((head + "\n" + text).encode("utf-8")).hexdigest()[:12]


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# --------------------------------------------------------------------------- project

class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.schema = yaml.safe_load((ROOT / "schema" / "items.yaml").read_text(encoding="utf-8"))
        cfg = self.root / "project.yaml"
        self.config = (yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}) if cfg.exists() else {}
        processes = (self.config.get("scope") or {}).get("processes")
        self.scope = set(processes) if processes else None      # None = everything in scope
        self.types = self.schema["types"]
        self.rules = {r["id"]: r for r in self.schema["coverage"]}
        self.items, self.findings = {}, []
        self.incoming = defaultdict(lambda: defaultdict(list))   # target id -> role -> [source ids]
        self.load()

    # ---- loading

    def load(self):
        folders = (self.config.get("paths") or {}).get("items") or ["spec", "verification", "records"]
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

    # ---- helpers

    def add(self, level, rule, subject, message, supports=None):
        supports = [s for s in (supports or [])
                    if self.scope is None or str(s).split(".BP")[0] in self.scope]   # only what is in scope
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

    def of_type(self, *types):
        return [i for i in self.items.values() if i.type in types]

    def sources(self, target_id, role, types=None):
        found = [self.items[s] for s in self.incoming[target_id][role] if s in self.items]
        return [s for s in found if self.live(s) and (types is None or s.type in types)]

    def in_scope(self, supports):
        if self.scope is None:
            return True
        return bool({str(s).split(".BP")[0] for s in supports if ".BP" in str(s)} & self.scope)

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

    def gap(self, rule_id, item, message):
        self.add(self.level_for(item), rule_id, item.id, message, self.rules[rule_id]["supports"])

    def approving_review(self, item):
        """The final review record that approved this item at its current content, if any."""
        for rev in self.of_type("review-record"):
            if rev.status != "final" or rev.front.get("verdict") != "approved":
                continue
            for entry in as_list(rev.front.get("subject")):
                if isinstance(entry, dict) and entry.get("item") == item.id and str(entry.get("hash")) == item.hash:
                    return rev
        return None

    def latest_run(self, type_name, **match):
        runs = [r for r in self.of_type(type_name) if r.status == "final"
                and all(r.front.get(k) == v for k, v in match.items())]
        return max(runs, key=lambda r: str(r.front.get("executed_at", "")), default=None)

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

    def check_attributes(self, item):
        attrs = self.attributes(item.type)
        for name in item.front:
            if name not in attrs and name != "links":
                self.add("warning", "SCHEMA", item.id, "attribute '%s' is not defined for type %s" % (name, item.type))
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
            if "structure" in spec:
                self.check_structured(item, name, value, spec["structure"])
        if not item.imported:
            for section, stage in (self.types[item.type].get("sections") or {}).items():
                if self.due(item, stage) and not item.has_section(section):
                    self.add("error", "SCHEMA", item.id, "section '%s' is required (%s)" % (section, stage))
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
                if anchor:
                    names = {f.get("name") for f in as_list(target.front.get("functions")) if isinstance(f, dict)}
                    if anchor not in names:
                        self.add("error", "LINK", item.id, "%s target %s#%s: the unit designs no function of that name"
                                 % (role, target_id, anchor))
        if item.type == "software-interface":
            for name in ("provided_by", "used_by"):
                for ref in as_list(item.front.get(name)):
                    if getattr(self.items.get(str(ref)), "type", None) != "software-component":
                        self.add("error", "LINK", item.id, "%s names %s, which is not a software component" % (name, ref))
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
                           only=lambda i: i.front.get("assessment") in ("accepted", "accepted-with-deviation"))

    def cov_02(self, rule):
        self.need_link(rule, "system-requirement", "derived_from", self.internal_with_rationale,
                       "no derived_from link, and not marked origin internal with a Rationale")

    def cov_03(self, rule):
        self.need_link(rule, "system-requirement", "allocated_to", self.constraint_with_rationale,
                       "not allocated to any system element or interface")

    def cov_04(self, rule):
        self.need_incoming(rule, "system-element", "allocated_to", ["system-requirement"],
                           "no system requirement is allocated to it")

    def cov_05(self, rule):
        for req in self.of_type("system-requirement"):
            if not self.live(req):
                continue
            elements = [self.items[t] for t, _ in req.targets("allocated_to") if t in self.items]
            software = [e for e in elements if e.type == "system-element" and e.front.get("kind") == "software"]
            if not software:
                continue
            covered = self.sources(req.id, "derived_from", ["software-requirement"])
            if not covered and not any(self.sources(e.id, "derived_from", ["software-requirement"]) for e in software):
                self.gap(rule, req, "allocated to software, but no software requirement is derived from it")

    def cov_06(self, rule):
        self.need_link(rule, "software-requirement", "derived_from", self.internal_with_rationale,
                       "no derived_from link, and not marked origin internal with a Rationale")

    def cov_07(self, rule):
        self.need_link(rule, "software-requirement", "allocated_to", self.constraint_with_rationale,
                       "not allocated to any software component or interface")

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
            if not any(self.sources(cid, "allocated_to", ["software-requirement"]) for cid in family):
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
                self.gap(rule, unit, "no unit test verifies it")
            if unit.id not in analysed:
                self.gap(rule, unit, "the latest final static analysis run has no entry for it"
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
            run = self.latest_run("test-run", level=TEST_TYPES[test.type][1])
            if run is None:
                self.gap(rule, test, "no final test run of level %s exists" % TEST_TYPES[test.type][1])
                continue
            entry = next((e for e in as_list(run.front.get("results"))
                          if isinstance(e, dict) and e.get("test") == test.id), None)
            if entry is None:
                self.gap(rule, test, "no verdict in the latest final test run %s" % run.id)
            elif entry["verdict"] in ("not-run", "blocked") and not entry.get("reason"):
                self.gap(rule, test, "%s in %s without a reason" % (entry["verdict"], run.id))

    def cov_19(self, rule):
        for item in self.items.values():
            if self.types.get(item.type, {}).get("lifecycle") != "engineering" or item.status != "approved":
                continue
            review = self.approving_review(item)
            if review is None:
                older = [r.id for r in self.of_type("review-record")
                         if any(isinstance(e, dict) and e.get("item") == item.id for e in as_list(r.front.get("subject")))]
                self.gap(rule, item, "stale approval: content changed since review %s (current hash %s)"
                         % (", ".join(older), item.hash) if older else
                         "approved, but no final review record covers it (current hash %s)" % item.hash)
                continue
            opened = [f.get("id") for f in as_list(review.front.get("findings"))
                      if isinstance(f, dict) and f.get("state") == "open" and f.get("item") in (None, item.id)]
            if opened:
                self.gap(rule, item, "review %s still has open findings: %s" % (review.id, ", ".join(map(str, opened))))

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
        """Name-level comparison of designed functions and C definitions (not full signatures)."""
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
            for role, relation in (("derived_from", "derived from it"), ("implements", "implements it")):
                for target, _ in item.targets(role):
                    if target in self.items:
                        compare(item, self.items[target], relation)
            if item.type == "software-unit":
                for target, _ in item.targets("part_of"):
                    if target in self.items:
                        compare(item, self.items[target], "is part of it")
            if item.type in ("software-component", "software-interface", "system-element", "system-interface"):
                for req in self.sources(item.id, "allocated_to"):
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
            for role, link in self.schema["links"].items():
                pairs = [p for p in link["pairs"] if p["from"] == item.type]
                if not pairs or not self.in_scope([s for p in pairs for s in p["supports"]]):
                    continue
                for target_id, _ in item.targets(role):
                    target = self.items.get(target_id)
                    if target is None:
                        continue
                    supports = [s for p in pairs for s in p["supports"]]
                    if target_id not in seen:
                        self.add("warning", "CONSISTENCY", item.id, "review %s does not record %s (%s) as a reference: "
                                 "consistency with it is not evidenced" % (review.id, target_id, role), supports)
                    elif seen[target_id] != target.hash:
                        self.add("error", "SUSPECT", item.id, "suspect link: %s (%s) changed after review %s"
                                 % (target_id, role, review.id), supports)

    def check(self):
        self.check_structure()
        self.check_coverage()
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
            print("  %-13s <- %s  %s" % (role, source, project.items[source].title))
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
        for role in (project.items[i].front.get("links") or {}):
            for target, _ in project.items[i].targets(role):
                if target in project.items and target not in ids:
                    references[target] = project.items[target].hash
    print("subject:")
    for i in ids:
        print("  - {item: %s, hash: %s}" % (i, project.items[i].hash))
    print("references:" if references else "references: []")
    for target in sorted(references):
        print("  - {item: %s, hash: %s}" % (target, references[target]))
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
    args = ap.parse_args()
    project = Project(args.project)
    return {"check": cmd_check, "matrix": cmd_matrix, "show": cmd_show, "impact": cmd_impact,
            "hash": cmd_hash, "status": cmd_status}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
