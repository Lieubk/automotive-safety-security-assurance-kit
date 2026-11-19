"""Registration of delivered requirements as imported items, shared by the exchange tools
(tools/xlsx.py, tools/alm.py). A record is a mapping with `source_id`, `title`, `text` and
optional `attributes` (item attribute -> value). tools/reqif.py keeps its own copy of this
logic for ReqIF.
"""
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record  # noqa: E402


def first_section(project, type_name):
    """The section the delivered text goes into: the first section the type defines."""
    sections = list((project.types[type_name].get("sections") or {}).keys())
    return sections[0] if sections else "Statement"


def imported_of(project, source):
    return [i for i in project.items.values() if i.imported and (i.front.get("imported") or {}).get("source") == source]


def normalised(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def check_records(records):
    problems, seen = [], set()
    for rec in records:
        sid = str(rec.get("source_id") or "").strip()
        if not sid:
            problems.append("a record has no identifier: %s" % (rec.get("title") or rec.get("text") or "")[:60])
        elif sid in seen:
            problems.append("identifier %s occurs twice" % sid)
        seen.add(sid)
        if not normalised(rec.get("text")):
            problems.append("%s has no text" % sid)
    return problems


def register(project, type_name, source, version, received, records, dry_run=False):
    """Write one imported item per record. Returns (problems, written IDs)."""
    if type_name not in project.types:
        return ["unknown type: %s" % type_name], []
    if imported_of(project, source):
        return ["%s already has imported items: compare the new version first, then take the changes over with "
                "/import-inputs" % source], []
    problems = check_records(records)
    attributes = project.attributes(type_name)
    unknown = sorted({a for r in records for a in (r.get("attributes") or {}) if a not in attributes})
    if unknown:
        problems.append("type %s has no attribute %s" % (type_name, ", ".join(unknown)))
    if problems:
        return problems, []
    section = first_section(project, type_name)
    number = int(record.next_id(project, type_name).rsplit("-", 1)[1])
    prefix = project.types[type_name]["prefix"]
    received = received or datetime.date.today().isoformat()
    written = []
    for rec in records:
        text = str(rec["text"]).strip()
        front = {"id": "%s-%04d" % (prefix, number), "type": type_name,
                 "title": (rec.get("title") or text.split("\n")[0])[:120], "status": "draft",
                 "imported": {"source": source, "version": str(version), "received": received,
                              "source_id": str(rec["source_id"])}}
        if "source_document" in attributes:
            front["source_document"] = "%s, version %s" % (source, version)
        if "source_id" in attributes:
            front["source_id"] = str(rec["source_id"])
        for name, value in (rec.get("attributes") or {}).items():
            if value not in (None, ""):
                front[name] = value
        written.append(front["id"])
        if not dry_run:
            record.write_item(project, type_name, front, "\n## %s\n\n%s\n" % (section, text))
        number += 1
    return [], written


def compare(project, source, records):
    """What a new delivery changes against the imported items of the source: (new, changed, removed, unchanged)."""
    items = {str((i.front.get("imported") or {}).get("source_id")): i for i in imported_of(project, source)}
    delivered = {str(r["source_id"]): r for r in records}
    new = sorted(set(delivered) - set(items))
    removed = sorted(set(items) - set(delivered))
    changed, unchanged = [], []
    for sid in sorted(set(items) & set(delivered)):
        item = items[sid]
        text = item.sections.get(first_section(project, item.type), "")
        (changed if normalised(text) != normalised(delivered[sid]["text"]) else unchanged).append((sid, item.id))
    return new, changed, removed, unchanged


def print_comparison(project, source, records):
    new, changed, removed, unchanged = compare(project, source, records)
    delivered = {str(r["source_id"]): r for r in records}
    for sid, item_id in changed:
        print("changed  %s  %s" % (sid, item_id))
    for sid in new:
        print("new      %s  %s" % (sid, normalised(delivered[sid]["text"])[:90]))
    for sid in removed:
        print("removed  %s" % sid)
    print("%d new, %d changed, %d removed, %d unchanged" % (len(new), len(changed), len(removed), len(unchanged)))
    return 0
