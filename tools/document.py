#!/usr/bin/env python3
"""Generate documents from the items of a project: HTML, Excel (XLSX), or DOCX in a
neutral style or in the customer's Word template.

A document is a view over the items, never a second source. Its kinds are defined in
`schema/documents.yaml` (requirements specification, architecture description,
detailed design, TARA report). Every document states where it comes from: the commit,
whether the working tree had changes, the baseline if one was named, and the items it
shows with their states and content hashes. A document that shows items which are not
approved, or that was generated from uncommitted changes, is marked DRAFT.

Usage:
    python tools/document.py [--project DIR] list
    python tools/document.py [--project DIR] build KIND [--format html|docx|xlsx] [--out FILE]
                             [--template FILE.docx|.dotx] [--baseline BL-ID] [--include-drafts]
                             [--no-script]

XLSX needs no other package: one sheet with the document information and the revision
history (baselines and reviews of the items shown), then one sheet per chapter.
DOCX needs the package python-docx. A template is a .docx or .dotx file: its styles
(Title, Heading 1 to 4, List Bullet, List Number, Table Grid), cover page, headers and
footers are kept; the placeholders {{title}}, {{project}}, {{kind}}, {{date}},
{{commit}} and {{baseline}} are filled in, and the content goes where a paragraph
{{content}} stands, or after the template's own content.
Exit code 0 = written, 1 = refused (the reason is printed), 2 = usage.
"""
import argparse
import datetime
import html
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import traceability as trace  # noqa: E402
from traceability import Project, as_list  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFINITIONS = ROOT / "schema" / "documents.yaml"
SKIP_ATTRIBUTES = {"id", "type", "title", "status", "imported", "links"}
SETTLED = ("approved", "final")
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
ID_PATTERN = re.compile(r"\b[A-Z]{2,5}-\d{4}\b")


def definitions():
    return yaml.safe_load(DEFINITIONS.read_text(encoding="utf-8"))["documents"]


# --------------------------------------------------------------------------- markdown

def md_blocks(text):
    """Split the Markdown of an item section into blocks: heading, para, list, table, code."""
    out, lines, i = [], (text or "").replace("\r\n", "\n").split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence = re.match(r"^\s*```\s*([\w-]*)", line)
        if fence:
            body, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            out.append(("code", fence.group(1), "\n".join(body)))
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            out.append(("heading", len(heading.group(1)), heading.group(2).strip()))
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            if rows:
                out.append(("table", rows[0], rows[1:]))
            continue
        item = re.match(r"^\s*(?:([-*+])|(\d+)[.)])\s+(.*)$", line)
        if item:
            ordered, entries = bool(item.group(2)), []
            while i < len(lines):
                m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", lines[i])
                if m:
                    entries.append(m.group(1))
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and entries:
                    entries[-1] += " " + lines[i].strip()
                else:
                    break
                i += 1
            out.append(("list", ordered, entries))
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^\s*(```|#{1,6}\s|\||[-*+]\s|\d+[.)]\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if not para:                                  # a line no rule took: keep it as text
            para, i = [line.strip()], i + 1
        out.append(("para", " ".join(para)))
    return out


def inline_html(text, anchors=()):
    """Inline Markdown to HTML: code, bold, italic, links; item IDs in the document become links."""
    parts = re.split(r"(`[^`]+`)", str(text))
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append("<code>%s</code>" % html.escape(part[1:-1]))
            continue
        s = html.escape(part)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
        s = ID_PATTERN.sub(lambda m: '<a href="#%s">%s</a>' % (m.group(0), m.group(0))
                           if m.group(0) in anchors else m.group(0), s)
        out.append(s)
    return "".join(out)


def plain(text):
    """Inline Markdown reduced to its text, for DOCX runs."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", str(text))
    return s.replace("**", "")


# --------------------------------------------------------------------------- document model

class Doc:
    """A neutral list of nodes that both renderers read."""

    def __init__(self, title):
        self.title, self.nodes, self.anchors = title, [], set()

    def add(self, *node):
        self.nodes.append(node)


def value_text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(value_text(v) for v in value)
    if isinstance(value, dict):
        return "; ".join("%s: %s" % (k, value_text(v)) for k, v in value.items())
    return str(value)


def structured_table(records, structure=None):
    keys = list((structure or {}).get("mandatory", [])) + list((structure or {}).get("keys", []))
    for record in records:
        keys += [k for k in record if k not in keys]
    keys = [k for k in keys if any(k in r for r in records)]
    return keys, [[value_text(r.get(k)) for k in keys] for r in records]


def link_text(project, ids):
    out = []
    for target in ids:
        item = project.items.get(target)
        out.append("%s %s" % (target, item.title) if item else target)
    return ", ".join(out)


def render_item(doc, project, item, level):
    doc.add("heading", level, "%s %s" % (item.id, item.title), item.id)
    if unsettled(project, item):
        doc.add("note", "DRAFT: %s is in state %s and not approved." % (item.id, item.status))
    if item.imported:
        origin = item.front.get("imported") or {}
        doc.add("note", "Received from %s, version %s%s." % (
            origin.get("source", "?"), origin.get("version", "?"),
            (", identifier %s" % origin["source_id"]) if origin.get("source_id") else ""))
    rows, structured = [], []
    for name, spec in project.attributes(item.type).items():
        value = item.front.get(name)
        if name in SKIP_ATTRIBUTES or value in (None, "", []):
            continue
        structure = project.schema["structures"].get(spec.get("structure")) if isinstance(spec, dict) else None
        records = value if isinstance(value, list) else [value] if structure and isinstance(value, dict) else None
        if records and all(isinstance(r, dict) for r in records) and (structure or len(records) > 1
                                                                       or isinstance(value, list)):
            structured.append((name, records, structure))
        else:
            rows.append((name, value_text(value)))
    rows.insert(0, ("status", item.status))
    doc.add("kv", rows)
    for name, records, structure in structured:
        keys, body = structured_table(records, structure)
        doc.add("caption", name)
        doc.add("table", keys, body)
    for section, text in item.sections.items():
        if text.strip():
            doc.add("heading", level + 1, section, None)
            doc.add("markdown", text)
    links = [(role, [t for t, _ in item.targets(role)]) for role in (item.front.get("links") or {})]
    incoming = [(role, sorted(project.incoming[item.id][role])) for role in sorted(project.incoming[item.id])
                if project.incoming[item.id][role]]
    if links or incoming:
        doc.add("caption", "links")
        doc.add("kv", [(role, link_text(project, ids)) for role, ids in links if ids]
                + [("%s (from)" % role, link_text(project, ids)) for role, ids in incoming])


def unsettled(project, item):
    """An item a document may show only as a draft: engineering items not approved, records not final.
    Problems, changes, risks, actions, queries and weaknesses are shown in the state they are in."""
    lifecycle = project.types.get(item.type, {}).get("lifecycle")
    return lifecycle in ("engineering", "record") and item.status not in SETTLED


def selected(project, spec, include_drafts, allowed):
    where = spec.get("where") or {}
    found = []
    for item in project.of_type(*spec.get("types", [])):
        if not (project.live(item) or spec.get("all_states")) or (allowed is not None and item.id not in allowed):
            continue
        if any(item.front.get(k) not in v for k, v in where.items()):
            continue
        if "imported" in spec and item.imported != bool(spec["imported"]):
            continue
        if unsettled(project, item) and not include_drafts:
            continue
        found.append(item)
    found.sort(key=lambda i: i.id)
    if spec.get("latest") and found:
        found = [max(found, key=lambda i: (str(i.front.get("executed_at") or i.front.get("as_of") or ""),
                                           trace.record_number(i.id)))]
    return found


def column_value(project, item, column):
    if column == "id":
        return item.id
    if column == "title":
        return item.title
    if column in project.schema["links"]:
        return ", ".join(t for t, _ in item.targets(column))
    return value_text(item.front.get(column))


def figures_nodes(doc, data, keys=None):
    """The figures a command of the trace engine returns: scalars and mappings as a list, lists as tables."""
    rows = []
    for key, value in data.items():
        if keys and key not in keys:
            continue
        if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            head, body = structured_table(value)
            doc.add("caption", key.replace("_", " "))
            doc.add("table", head, body)
        elif isinstance(value, dict):
            rows += [("%s: %s" % (key.replace("_", " "), k.replace("_", " ")), value_text(v)) for k, v in value.items()]
        elif value not in (None, "", []):
            rows.append((key.replace("_", " "), value_text(value)))
    if rows:
        doc.add("kv", rows)


def baseline_nodes(doc, project, baseline):
    """The content of a baseline and what changed against the baseline before it."""
    records = sorted((b for b in project.of_type("baseline") if b.status == "final"), key=lambda b: trace.record_number(b.id))
    record = project.items.get(baseline) if baseline else (records[-1] if records else None)
    if record is None:
        doc.add("para", "No baseline exists in the project.")
        return []
    entries = {str(e.get("item")): e for e in as_list(record.front.get("items")) if isinstance(e, dict)}
    doc.add("kv", [("baseline", record.id), ("tag", value_text(record.front.get("tag"))),
                   ("purpose", value_text(record.front.get("purpose"))),
                   ("created", value_text(record.front.get("created_at"))), ("items", str(len(entries))),
                   ("left out", value_text(record.front.get("left_out_reason")) or
                    ("%d items" % len(as_list(record.front.get("left_out"))) if record.front.get("left_out") else "none"))])
    earlier = [b for b in records if trace.record_number(b.id) < trace.record_number(record.id)]
    if earlier:
        before = {str(e.get("item")): e for e in as_list(earlier[-1].front.get("items")) if isinstance(e, dict)}
        changes = [["added", i] for i in sorted(set(entries) - set(before))]
        changes += [["removed", i] for i in sorted(set(before) - set(entries))]
        changes += [["changed", i] for i in sorted(set(entries) & set(before))
                    if str(entries[i].get("hash")) != str(before[i].get("hash"))]
        doc.add("caption", "changes since %s (tag %s)" % (earlier[-1].id, earlier[-1].front.get("tag")))
        if changes:
            doc.add("table", ["change", "item", "title"], [[c, i, getattr(project.items.get(i), "title", "")] for c, i in changes])
        else:
            doc.add("para", "No item changed.")
    doc.add("caption", "content")
    doc.add("table", ["item", "title", "state", "content hash"],
            [[i, getattr(project.items.get(i), "title", ""), value_text(e.get("status")), value_text(e.get("hash"))]
             for i, e in sorted(entries.items())])
    return [record]


def build(project, kind, include_drafts=False, baseline=None, as_of=None):
    """The document and its provenance, or problems that prevent it."""
    spec = definitions().get(kind)
    if spec is None:
        return None, None, ["unknown document kind %r; `list` shows the kinds" % kind]
    problems, allowed = [], None
    if baseline:
        record = project.items.get(baseline)
        if record is None or record.type != "baseline":
            return None, None, ["%s is not a baseline" % baseline]
        allowed = {str(e.get("item")): str(e.get("hash")) for e in as_list(record.front.get("items")) if isinstance(e, dict)}
        changed = [i for i, h in allowed.items() if i in project.items and project.items[i].hash != h]
        if changed:
            problems.append("%d items differ from baseline %s (%s): check out tag %s and generate again"
                            % (len(changed), baseline, ", ".join(sorted(changed)[:8]), record.front.get("tag")))
    if problems:
        return None, None, problems
    doc, shown = Doc(spec["title"]), []
    for chapter in spec["chapters"]:
        doc.add("heading", 1, chapter["title"], None)
        if chapter.get("text"):
            doc.add("para", chapter["text"])
        if "items" in chapter:
            items = selected(project, chapter["items"], include_drafts, allowed)
            for item in items:
                render_item(doc, project, item, 2)
            shown += items
            if not items:
                doc.add("para", "Nothing of this kind in the project.")
        elif "table" in chapter:
            items = selected(project, chapter["table"], include_drafts, allowed)
            columns = chapter["table"]["columns"]
            if items:
                doc.add("table", columns, [[column_value(project, i, c) for c in columns] for i in items])
            else:
                doc.add("para", "Nothing of this kind in the project.")
            shown += items
        elif "matrix" in chapter:
            m = chapter["matrix"]
            items = selected(project, {"types": [m["of"]]}, include_drafts, allowed)
            rows = []
            for item in items:
                linked = sorted(project.incoming[item.id][m["role"]]) if m.get("incoming") \
                    else [t for t, _ in item.targets(m["role"])]
                rows.append(["%s %s" % (item.id, item.title), link_text(project, linked) or "-"])
            header = [m["of"], ("%s (from)" if m.get("incoming") else "%s") % m["role"]]
            doc.add("table", header, rows) if rows else doc.add("para", "Nothing of this kind in the project.")
        elif "tara" in chapter:
            data = trace.tara(project)
            rows = [[e["item"], e["title"], ", ".join(e["assets"]), ", ".join(e["damage_scenarios"]), e["impact"] or "-",
                     e["feasibility"] or "-", "%s%s" % (e["risk_value"], "" if e["matrix_value"] in (None, e["risk_value"])
                                                        else " (matrix %s)" % e["matrix_value"]),
                     "/".join(e["treatment"]) or "-", ", ".join(e["goals"] + e["claims"]) or "-"]
                    for e in data["threat_scenarios"]
                    if (include_drafts or e["state"] in SETTLED) and (allowed is None or e["item"] in allowed)]
            doc.add("table", ["threat scenario", "title", "assets", "damage", "impact", "feasibility", "risk",
                              "treatment", "answered by"], rows)
        elif "findings" in chapter:
            wanted = set(as_list(chapter["findings"].get("processes")))
            rows = [[f["level"], f["rule"], f["item"], f["message"]] for f in findings_of(project)
                    if f["level"] in ("error", "warning")
                    and (not wanted or {trace.process_of(s) for s in f["supports"]} & wanted)]
            doc.add("table", ["level", "rule", "item", "message"], rows) if rows \
                else doc.add("para", "The trace check reports no error and no warning here.")
        elif "figures" in chapter:
            source = chapter["figures"]["source"]
            data = trace.tara(project) if source == "tara" else getattr(trace, source)(project, as_of or datetime.date.today())
            figures_nodes(doc, data.get("figures", data) if chapter["figures"].get("summary") else data,
                          chapter["figures"].get("keys"))
        elif "trace" in chapter:
            wanted = set(as_list(chapter["trace"].get("processes")))
            for role, link in project.schema["links"].items():
                for pair in link["pairs"]:
                    if pair["to"] == "any" or not project.in_scope(pair["supports"]) or pair.get("evidence") == "none":
                        continue
                    if wanted and not {trace.process_of(s) for s in pair["supports"]} & wanted:
                        continue
                    targets = [t for t in project.of_type(*pair["to"]) if project.live(t)
                               and (allowed is None or t.id in allowed)]
                    if not targets:
                        continue
                    shown += targets
                    doc.add("caption", "%s: %s -> %s" % (role, pair["from"], ", ".join(pair["to"])))
                    doc.add("table", ["target", "title", "linked from"],
                            [[t.id, t.title, ", ".join(sorted(s.id for s in project.sources(t.id, role, [pair["from"]]))) or "-"]
                             for t in sorted(targets, key=lambda t: t.id)])
        elif "baseline" in chapter:
            shown += baseline_nodes(doc, project, baseline)
        elif "testcases" in chapter:
            spec_ = chapter["testcases"]
            cases = selected(project, {"types": spec_["types"]}, include_drafts, allowed)
            level = spec_.get("level") or trace.TEST_TYPES.get(spec_["types"][0], (None, None))[1]
            runs = [r for r in project.of_type("test-run") if r.status == "final" and r.front.get("level") == level]
            verdicts, rows = {}, []
            for run in sorted(runs, key=lambda r: (str(r.front.get("executed_at", "")), trace.record_number(r.id))):
                for entry in as_list(run.front.get("results")):
                    if isinstance(entry, dict):
                        verdicts[str(entry.get("test"))] = (run, entry)   # the latest run that has the case wins
            counts = {}
            for case in cases:
                run, entry = verdicts.get(case.id, (None, {}))
                verdict = entry.get("verdict") or "not run"
                counts[verdict] = counts.get(verdict, 0) + 1
                rows.append([case.id, case.title, ", ".join(t for t, _ in case.targets("verifies")),
                             value_text(case.front.get("step")) or "-", value_text(case.front.get("execution")),
                             case.sections.get("Preconditions", "").strip() or "-", case.sections.get("Steps", "").strip(),
                             case.sections.get("Expected result", "").strip(), verdict,
                             run.id if run else "-", value_text(run.front.get("executed_at"))[:10] if run else "-",
                             value_text(run.front.get("environment")) if run else "-",
                             value_text(entry.get("reason") or entry.get("evidence")) or "-"])
            doc.add("caption", "result summary")
            doc.add("kv", [(k, str(v)) for k, v in sorted(counts.items())] + [("total", str(len(cases)))])
            doc.add("table", ["test case", "title", "verifies", "step", "execution", "preconditions", "steps",
                              "expected result", "verdict", "run", "executed", "environment", "reason or evidence"], rows)
            shown += cases + [r for r, _ in verdicts.values()]
        elif "tara_sheet" in chapter:
            plan = project.cs_plan()
            method = plan.front.get("tara_method") if plan and isinstance(plan.front.get("tara_method"), dict) else {}
            categories = [str(c) for c in as_list(method.get("impact_categories"))]
            rows = []
            for threat in selected(project, {"types": ["threat-scenario"]}, include_drafts, allowed):
                assets = [project.items[t] for t, _ in threat.targets("threatens") if t in project.items]
                damages = [project.items[t] for t, _ in threat.targets("leads_to") if t in project.items]
                answers = project.sources(threat.id, "addresses", ["cybersecurity-goal", "cybersecurity-claim"])
                goals = [a for a in answers if a.type == "cybersecurity-goal"]
                requirements = [r for g in goals for r in project.sources(g.id, "derived_from")]
                elements = [e for r in requirements for e in project.sources(r.id, "fulfils")]
                tests = [c for r in requirements for c in project.sources(r.id, "verifies")]
                for n, path in enumerate([p for p in as_list(threat.front.get("attack_paths")) if isinstance(p, dict)] or [{}], 1):
                    impact = {c: max((str((d.front.get("impact") or {}).get(c, "")) for d in damages
                                      if str((d.front.get("impact") or {}).get(c, "")) in trace.IMPACT_LEVELS),
                                     key=trace.IMPACT_LEVELS.index, default="-") for c in categories}
                    rows.append([", ".join(a.id for a in assets), "; ".join(a.title for a in assets),
                                 ", ".join(sorted({p for a in assets for p in as_list(a.front.get("properties"))})),
                                 ", ".join(d.id for d in damages), "; ".join(d.title for d in damages)]
                                + [impact[c] for c in categories]
                                + [project.highest_impact(threat) or "-", threat.id, threat.title,
                                   value_text(threat.front.get("property")), "%d: %s" % (n, value_text(path.get("path"))),
                                   value_text(path.get("factors")) or "-", value_text(path.get("feasibility")) or "-",
                                   value_text(threat.front.get("feasibility")), value_text(threat.front.get("risk_value")),
                                   value_text(threat.front.get("treatment")), value_text(threat.front.get("decision")) or "-",
                                   ", ".join(a.id for a in answers) or "-", ", ".join(r.id for r in requirements) or "-",
                                   ", ".join(e.id for e in elements) or "-", ", ".join(c.id for c in tests) or "-",
                                   value_text(threat.front.get("residual_risk_value")) or "-"])
                shown += [threat] + assets + damages + answers
            doc.add("table", ["asset", "asset title", "properties", "damage", "damage title"]
                    + ["impact %s" % c for c in categories]
                    + ["highest impact", "threat", "threat title", "property lost", "attack path", "factors",
                       "path feasibility", "feasibility", "risk value", "treatment", "decision", "goal or claim",
                       "requirements", "allocated to", "verified by", "residual risk"], rows)
        elif "method" in chapter:
            plan = project.cs_plan()
            method = plan.front.get("tara_method") if plan else None
            if not isinstance(method, dict):
                doc.add("note", "No approved cybersecurity plan with a tara_method: the ratings are not assessed.")
                continue
            doc.add("kv", [("plan", "%s %s" % (plan.id, plan.title)),
                           ("impact categories", value_text(method.get("impact_categories"))),
                           ("impact levels", value_text(method.get("impact_meaning"))),
                           ("feasibility approach", value_text(method.get("feasibility_approach"))),
                           ("feasibility levels", value_text(method.get("feasibility_meaning"))),
                           ("retained without a decision up to", value_text(method.get("retain_up_to")))])
            matrix = method.get("risk_matrix") or {}
            doc.add("caption", "risk matrix")
            doc.add("table", ["impact \\ feasibility"] + trace.FEASIBILITY_LEVELS,
                    [[level] + [value_text(v) for v in as_list(matrix.get(level))] for level in reversed(trace.IMPACT_LEVELS)])
            shown.append(plan)
    shown = list({i.id: i for i in shown}.values())
    _FINDINGS.pop(id(project), None)
    doc.anchors = {i.id for i in shown}
    return doc, provenance(project, kind, spec, shown, baseline), []


_FINDINGS = {}


def findings_of(project):
    """The findings of the trace check, computed once per document."""
    if id(project) not in _FINDINGS:
        _FINDINGS[id(project)] = Project(project.root).check()
    return _FINDINGS[id(project)]


def git(project, *args):
    try:
        done = subprocess.run(["git", "-C", str(project.root)] + list(args), capture_output=True, text=True, timeout=30)
        return done.stdout.strip() if done.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def provenance(project, kind, spec, shown, baseline):
    commit = git(project, "rev-parse", "--short", "HEAD")
    dirty = git(project, "status", "--porcelain", "--", ".")
    record = project.items.get(baseline) if baseline else None
    unsettled_ids = [i.id for i in shown if unsettled(project, i)]
    history = []
    shown_ids = {i.id for i in shown}
    for record in project.of_type("baseline", "review-record"):
        if record.status != "final":
            continue
        if record.type == "baseline":
            covered = {str(e.get("item")) for e in as_list(record.front.get("items")) if isinstance(e, dict)}
            if covered & shown_ids:
                history.append({"date": value_text(record.front.get("created_at"))[:10], "record": record.id,
                                "what": "baseline %s, tag %s" % (value_text(record.front.get("purpose")), value_text(record.front.get("tag"))),
                                "by": "-"})
        else:
            covered = {str(e.get("item")) for e in as_list(record.front.get("subject")) if isinstance(e, dict)}
            if covered & shown_ids:
                history.append({"date": value_text(record.front.get("reviewed_at"))[:10] or "-", "record": record.id,
                                "what": "review %s of %d items shown here" % (value_text(record.front.get("verdict")), len(covered & shown_ids)),
                                "by": value_text(record.front.get("reviewers"))})
    history.sort(key=lambda h: (h["date"], trace.record_number(h["record"])))
    return {
        "kind": kind, "title": spec["title"],
        "project": str(((project.config.get("project") or {}).get("name")) or project.root.name),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "commit": commit or "not under version control",
        "uncommitted_changes": bool(dirty),
        "baseline": ("%s (tag %s)" % (baseline, record.front.get("tag"))) if record else "none",
        "items": [{"item": i.id, "title": i.title, "status": i.status, "hash": i.hash} for i in sorted(shown, key=lambda i: i.id)],
        "history": history,
        "draft": bool(unsettled_ids) or bool(dirty),
        "draft_reasons": (["items not approved: %s" % ", ".join(unsettled_ids)] if unsettled_ids else [])
                         + (["generated from uncommitted changes"] if dirty else []),
    }


# --------------------------------------------------------------------------- HTML

CSS = """
:root { --ink: #1d2430; --muted: #5b6575; --line: #d6dbe3; --soft: #f4f6f9; --accent: #2d5b8a; --warn: #a33a1f; }
body { font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; color: var(--ink); background: #fff;
       max-width: 60rem; margin: 2rem auto; padding: 0 1rem; }
h1 { font-size: 1.6rem; border-bottom: 2px solid var(--accent); padding-bottom: .3rem; margin-top: 2.5rem; }
h2 { font-size: 1.25rem; margin-top: 2rem; } h3 { font-size: 1.05rem; } h4 { font-size: .95rem; }
table { border-collapse: collapse; width: 100%; margin: .6rem 0 1rem; font-size: .9rem; }
th, td { border: 1px solid var(--line); padding: .3rem .5rem; text-align: left; vertical-align: top; }
th { background: var(--soft); } code, pre { font-family: Consolas, "Courier New", monospace; font-size: .88rem; }
pre { background: var(--soft); padding: .6rem; overflow-x: auto; } .caption { color: var(--muted); font-size: .85rem; margin: .8rem 0 .1rem; }
.note { border-left: 4px solid var(--warn); padding: .2rem .6rem; color: var(--warn); }
.banner { background: var(--warn); color: #fff; padding: .4rem .8rem; font-weight: 600; }
.meta td:first-child { width: 14rem; color: var(--muted); } nav ul { columns: 2; } a { color: var(--accent); }
@media print { nav { display: none; } h1 { page-break-before: always; } h1.title { page-break-before: avoid; } }
"""


def to_html(doc, info, script=True):
    a = doc.anchors
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           "<title>%s</title><style>%s</style></head><body>" % (html.escape(doc.title), CSS)]
    if info["draft"]:
        out.append('<div class="banner">DRAFT - %s</div>' % html.escape("; ".join(info["draft_reasons"])))
    out.append('<h1 class="title">%s</h1>' % html.escape(doc.title))
    out.append('<table class="meta">' + "".join("<tr><td>%s</td><td>%s</td></tr>" % (html.escape(k), html.escape(str(v))) for k, v in (
        ("Project", info["project"]), ("Generated", info["generated_at"]), ("Commit", info["commit"]),
        ("Uncommitted changes", "yes" if info["uncommitted_changes"] else "no"), ("Baseline", info["baseline"]),
        ("Items shown", len(info["items"])))) + "</table>")
    if info["history"]:
        out.append("<h2>Revision history</h2><table><tr><th>date</th><th>record</th><th>what</th><th>by</th></tr>%s</table>"
                   % "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(html.escape(h[k]) for k in ("date", "record", "what", "by"))
                             for h in info["history"]))
    toc = [(n[2], n[3]) for n in doc.nodes if n[0] == "heading" and n[1] == 1]
    out.append("<nav><ul>%s</ul></nav>" % "".join("<li>%s</li>" % html.escape(t) for t, _ in toc))
    for node in doc.nodes:
        kind = node[0]
        if kind == "heading":
            level, text, anchor = node[1], node[2], node[3]
            out.append("<h%d%s>%s</h%d>" % (min(level, 4), (' id="%s"' % anchor) if anchor else "",
                                             inline_html(text, ()), min(level, 4)))
        elif kind == "para":
            out.append("<p>%s</p>" % inline_html(node[1], a))
        elif kind == "note":
            out.append('<p class="note">%s</p>' % inline_html(node[1], a))
        elif kind == "caption":
            out.append('<p class="caption">%s</p>' % html.escape(node[1]))
        elif kind == "kv":
            out.append("<table>%s</table>" % "".join("<tr><th>%s</th><td>%s</td></tr>" % (html.escape(k), inline_html(v, a))
                                                     for k, v in node[1]))
        elif kind == "table":
            out.append("<table><tr>%s</tr>%s</table>" % ("".join("<th>%s</th>" % html.escape(str(h)) for h in node[1]),
                                                        "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline_html(c, a) for c in row)
                                                                for row in node[2])))
        elif kind == "markdown":
            for block in md_blocks(node[1]):
                out.append(block_html(block, a))
    out.append("<h1>Items in this document</h1><table><tr><th>item</th><th>title</th><th>state</th><th>content hash</th></tr>%s</table>"
               % "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td><code>%s</code></td></tr>" % (
                   inline_html(i["item"], a), html.escape(i["title"]), i["status"], i["hash"]) for i in info["items"]))
    out.append('<p class="caption">Generated by tools/document.py from the items of the project. The items are the source: '
               'change them, not this document.</p>')
    if script:
        out.append('<script src="%s"></script><script>if (window.mermaid) { mermaid.initialize({startOnLoad: true}); }</script>'
                   % MERMAID)
    out.append("</body></html>")
    return "\n".join(out)


def block_html(block, anchors):
    kind = block[0]
    if kind == "code":
        if block[1] == "mermaid":
            return '<pre class="mermaid">%s</pre>' % html.escape(block[2])
        return "<pre><code>%s</code></pre>" % html.escape(block[2])
    if kind == "heading":
        level = min(block[1] + 2, 4)
        return "<h%d>%s</h%d>" % (level, inline_html(block[2], anchors), level)
    if kind == "table":
        return "<table><tr>%s</tr>%s</table>" % ("".join("<th>%s</th>" % inline_html(h, anchors) for h in block[1]),
                                                "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline_html(c, anchors) for c in row)
                                                        for row in block[2]))
    if kind == "list":
        tag = "ol" if block[1] else "ul"
        return "<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline_html(e, anchors) for e in block[2]), tag)
    return "<p>%s</p>" % inline_html(block[1], anchors)


# --------------------------------------------------------------------------- XLSX

def _cell(ref, text, bold=False):
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(text))[:32000]
    return '<c r="%s" t="inlineStr"%s><is><t xml:space="preserve">%s</t></is></c>' % (
        ref, ' s="1"' if bold else ' s="2"', html.escape(text, quote=False))


def _column(n):
    name = ""
    while n:
        n, rest = divmod(n - 1, 26)
        name = chr(65 + rest) + name
    return name


def to_xlsx(doc, info):
    """A workbook without other packages: a sheet with the document information and the revision history,
    then one sheet per chapter with its tables and texts as rows."""
    sheets, current = [("Document", [])], None
    rows = sheets[0][1]
    rows += [[("Title", True), (doc.title, False)]] + [[(k, True), (str(v), False)] for k, v in (
        ("Project", info["project"]), ("Generated", info["generated_at"]), ("Commit", info["commit"]),
        ("Uncommitted changes", "yes" if info["uncommitted_changes"] else "no"), ("Baseline", info["baseline"]),
        ("Items shown", len(info["items"])), ("Draft", "; ".join(info["draft_reasons"]) or "no"))]
    rows.append([])
    rows.append([("Revision history", True)])
    rows.append([(h, True) for h in ("date", "record", "what", "by")])
    rows += [[(h["date"], False), (h["record"], False), (h["what"], False), (h["by"], False)] for h in info["history"]]
    for node in doc.nodes:
        kind = node[0]
        if kind == "heading" and node[1] == 1:
            name = re.sub(r"[\[\]:*?/\\]", " ", node[2])[:28].strip() or "Chapter"
            while name in {s[0] for s in sheets}:
                name = name[:25] + " %d" % len(sheets)
            current = []
            sheets.append((name, current))
            current.append([(node[2], True)])
            continue
        target = current if current is not None else rows
        if kind == "heading":
            target.append([])
            target.append([(node[2], True)])
        elif kind in ("para", "note"):
            target.append([(plain(node[1]), kind == "note")])
        elif kind == "caption":
            target.append([(node[1], True)])
        elif kind == "kv":
            target += [[(k, True), (plain(v), False)] for k, v in node[1]]
        elif kind == "table":
            target.append([(str(h), True) for h in node[1]])
            target += [[(plain(c), False) for c in row] for row in node[2]]
        elif kind == "markdown":
            for block in md_blocks(node[1]):
                if block[0] == "table":
                    target.append([(plain(h), True) for h in block[1]])
                    target += [[(plain(c), False) for c in row] for row in block[2]]
                elif block[0] == "list":
                    target += [[("- " + plain(e), False)] for e in block[2]]
                elif block[0] == "code":
                    target.append([(block[2], False)])
                elif block[0] == "heading":
                    target.append([(plain(block[2]), True)])
                else:
                    target.append([(plain(block[1]), False)])
    sheets.append(("Items", [[(h, True) for h in ("item", "title", "state", "content hash")]]
                   + [[(i["item"], False), (i["title"], False), (i["status"], False), (i["hash"], False)] for i in info["items"]]))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        names = [s[0] for s in sheets]
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + "".join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1)
                             for i in range(len(sheets))) + "</Types>")
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (html.escape(n), i + 1, i + 1) for i, n in enumerate(names))
                   + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1)
                             for i in range(len(sheets)))
                   + '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' % (len(sheets) + 1))
        z.writestr("xl/styles.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<fonts count="2"><font><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="10"/><name val="Calibri"/></font></fonts>'
                   '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
                   '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
                   '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                   '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
                   '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"><alignment vertical="top" wrapText="1"/></xf>'
                   '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs>'
                   '</styleSheet>')
        for i, (name, sheet_rows) in enumerate(sheets):
            width = max([len(r) for r in sheet_rows] + [1])
            cols = "".join('<col min="%d" max="%d" width="%d" customWidth="1"/>' % (c, c, 18 if c > 1 else 14) for c in range(1, width + 1))
            data = "".join('<row r="%d">%s</row>' % (n + 1, "".join(_cell("%s%d" % (_column(c + 1), n + 1), text, bold)
                                                                    for c, (text, bold) in enumerate(r)))
                           for n, r in enumerate(sheet_rows))
            z.writestr("xl/worksheets/sheet%d.xml" % (i + 1),
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                       '<sheetViews><sheetView workbookViewId="0"/></sheetViews><cols>%s</cols><sheetData>%s</sheetData></worksheet>' % (cols, data))
    return out.getvalue()


# --------------------------------------------------------------------------- DOCX

def open_template(path):
    """A python-docx Document from a .docx or .dotx file (a template's content type is changed in memory)."""
    import docx
    if path is None:
        return docx.Document()
    data = Path(path).read_bytes()
    if str(path).lower().endswith((".dotx", ".dotm")):
        source, target = zipfile.ZipFile(io.BytesIO(data)), io.BytesIO()
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
            for entry in source.infolist():
                content = source.read(entry.filename)
                if entry.filename == "[Content_Types].xml":
                    content = content.replace(b"wordprocessingml.template.main+xml", b"wordprocessingml.document.main+xml")
                out.writestr(entry, content)
        data = target.getvalue()
    return docx.Document(io.BytesIO(data))


def fill_placeholders(document, values):
    def paragraphs():
        yield from document.paragraphs
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    yield from cell.paragraphs
        for section in document.sections:
            for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
                yield from part.paragraphs
    for paragraph in paragraphs():
        text = paragraph.text
        if "{{" not in text:
            continue
        new = text
        for key, value in values.items():
            new = new.replace("{{%s}}" % key, value)
        if new != text and paragraph.runs:
            paragraph.runs[0].text = new
            for run in paragraph.runs[1:]:
                run.text = ""


def to_docx(doc, info, template=None):
    from docx.shared import Pt
    document = open_template(template)
    styles = {s.name for s in document.styles}

    def style(name):
        return name if name in styles else None

    fill_placeholders(document, {"title": doc.title, "project": info["project"], "kind": info["kind"],
                                 "date": info["generated_at"][:10], "commit": info["commit"], "baseline": info["baseline"]})
    body = document.element.body
    marker = next((p for p in document.paragraphs if p.text.strip() == "{{content}}"), None)
    start = len(body)

    def para(text, style_name=None, bold=False, mono=False):
        p = document.add_paragraph(style=style(style_name) if style_name else None)
        for i, part in enumerate(re.split(r"(`[^`]+`)", plain(text))):
            if not part:
                continue
            code = part.startswith("`") and part.endswith("`") and len(part) > 1
            run = p.add_run(part[1:-1] if code else part)
            run.bold = bold
            if code or mono:
                run.font.name = "Consolas"
                run.font.size = Pt(9)
        return p

    def table(header, rows):
        t = document.add_table(rows=1, cols=len(header))
        if style("Table Grid"):
            t.style = "Table Grid"
        for cell, text in zip(t.rows[0].cells, header):
            cell.text = ""
            cell.paragraphs[0].add_run(plain(text)).bold = True
        for row in rows:
            cells = t.add_row().cells
            for cell, text in zip(cells, row):
                cell.text = plain(text)

    if template is None:
        document.add_paragraph(doc.title, style=style("Title"))
    if info["draft"]:
        para("DRAFT - " + "; ".join(info["draft_reasons"]), bold=True)
    table(["Document information", ""], [["Project", info["project"]], ["Generated", info["generated_at"]],
                                         ["Commit", info["commit"]],
                                         ["Uncommitted changes", "yes" if info["uncommitted_changes"] else "no"],
                                         ["Baseline", info["baseline"]], ["Items shown", str(len(info["items"]))]])
    if info["history"]:
        para("Revision history", bold=True)
        table(["date", "record", "what", "by"], [[h["date"], h["record"], h["what"], h["by"]] for h in info["history"]])
    for node in doc.nodes:
        kind = node[0]
        if kind == "heading":
            document.add_heading(plain(node[2]), level=min(node[1], 4)) if style("Heading %d" % min(node[1], 4)) \
                else para(node[2], bold=True)
        elif kind in ("para", "note"):
            para(node[1], bold=(kind == "note"))
        elif kind == "caption":
            para(node[1], bold=True)
        elif kind == "kv":
            table(["", ""], [[k, v] for k, v in node[1]])
        elif kind == "table":
            table([str(h) for h in node[1]], node[2])
        elif kind == "markdown":
            for block in md_blocks(node[1]):
                if block[0] == "code":
                    if block[1] == "mermaid":
                        para("Diagram (Mermaid source; the HTML version draws it):", bold=True)
                    for line in block[2].split("\n"):
                        para(line, mono=True)
                elif block[0] == "heading":
                    level = min(block[1] + 2, 4)
                    document.add_heading(plain(block[2]), level=level) if style("Heading %d" % level) \
                        else para(block[2], bold=True)
                elif block[0] == "table":
                    table(block[1], block[2])
                elif block[0] == "list":
                    for entry in block[2]:
                        para(entry, "List Number" if block[1] else "List Bullet")
                else:
                    para(block[1])
    document.add_heading("Items in this document", level=1) if style("Heading 1") else para("Items in this document", bold=True)
    table(["item", "title", "state", "content hash"], [[i["item"], i["title"], i["status"], i["hash"]] for i in info["items"]])
    para("Generated by tools/document.py from the items of the project. The items are the source: change them, "
         "not this document.")
    if marker is not None:                            # move the content to where the template asks for it
        new = [e for e in list(body)[start:] if not e.tag.endswith("}sectPr")]
        anchor = marker._element
        for element in new:
            anchor.addprevious(element)
        anchor.getparent().remove(anchor)
    out = io.BytesIO()
    document.save(out)
    return out.getvalue()


# --------------------------------------------------------------------------- commands

def cmd_list(project, args):
    for kind, spec in definitions().items():
        types = sorted({t for c in spec["chapters"] for key in ("items", "table") if key in c for t in c[key]["types"]})
        types += sorted({c["matrix"]["of"] for c in spec["chapters"] if "matrix" in c} - set(types))
        counts = ", ".join("%s %d" % (t, len([i for i in project.of_type(t) if project.live(i)])) for t in types)
        print("%-38s %s  [%s]" % (kind, spec["title"], counts))
    return 0


def cmd_build(project, args):
    fmt = args.format or (Path(args.out).suffix.lstrip(".").lower() if args.out else "html")
    if fmt not in ("html", "docx", "xlsx"):
        print("--format must be html, docx or xlsx")
        return 2
    template = args.template or ((project.config.get("documents") or {}).get("template") or None)
    if template:
        template = Path(template) if Path(template).is_absolute() else (project.root / template)
        if fmt != "docx":
            print("a Word template applies to --format docx only")
            return 2
        if not template.is_file():
            print("template %s does not exist\nno document written" % template)
            return 1
    as_of = None
    if args.as_of:
        as_of = trace.as_date(args.as_of)
        if as_of is None:
            print("--as-of must be a date YYYY-MM-DD")
            return 2
    doc, info, problems = build(project, args.kind, args.include_drafts, args.baseline, as_of)
    if problems:
        print("\n".join(problems) + "\nno document written")
        return 1
    if fmt == "docx":
        try:
            import docx  # noqa: F401
        except ImportError:
            print("DOCX needs the package python-docx (pip install python-docx): NOT ASSESSED\nno document written")
            return 1
        data = to_docx(doc, info, template)
    elif fmt == "xlsx":
        data = to_xlsx(doc, info)
    else:
        data = to_html(doc, info, script=not args.no_script).encode("utf-8")
    out = Path(args.out) if args.out else project.root / "build" / "documents" / ("%s.%s" % (args.kind, fmt))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print("wrote %s: %s, %d items, commit %s%s%s" % (
        out.as_posix(), info["title"], len(info["items"]), info["commit"],
        ", template %s" % template.name if template else "",
        " - DRAFT (%s)" % "; ".join(info["draft_reasons"]) if info["draft"] else ""))
    if args.json:
        print(json.dumps({k: v for k, v in info.items() if k != "items"}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    b = sub.add_parser("build")
    b.add_argument("kind")
    b.add_argument("--format", choices=["html", "docx", "xlsx"])
    b.add_argument("--out")
    b.add_argument("--template", help="a .docx or .dotx file of the customer; default: documents.template of project.yaml")
    b.add_argument("--baseline", help="show only the items of this baseline; refused when they changed since")
    b.add_argument("--include-drafts", action="store_true", help="show items that are not approved, marked DRAFT")
    b.add_argument("--no-script", action="store_true", help="HTML without the script that draws Mermaid diagrams")
    b.add_argument("--json", action="store_true", help="also print the provenance")
    b.add_argument("--as-of", help="the date figures of status, problems, risks and quality are measured to (default: today)")
    args = ap.parse_args()
    project = Project(args.project)
    return {"list": cmd_list, "build": cmd_build}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
