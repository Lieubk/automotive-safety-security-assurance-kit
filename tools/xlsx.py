#!/usr/bin/env python3
"""Exchange with spreadsheets: requirements delivered as Excel registered as imported items,
a new version compared, items exported, and a sheet of test results turned into the
results file `record.py test-run` reads.

The reader and the writer use the standard library only (an .xlsx file is a zip of XML).

Usage:
    python tools/xlsx.py [--project DIR] sheets FILE
    python tools/xlsx.py [--project DIR] import FILE --sheet NAME --type T --source NAME --version V
                         --column source_id=COL --column text=COL [--column title=COL] [--column ATTR=COL ...]
                         [--header-row N] [--received DATE] [--dry-run]
    python tools/xlsx.py [--project DIR] compare FILE --sheet NAME --source NAME --column ... [--header-row N]
    python tools/xlsx.py [--project DIR] export --type T [--type T ...] --out FILE.xlsx
    python tools/xlsx.py [--project DIR] results FILE --sheet NAME --column test=COL --column verdict=COL
                         [--column reason=COL] [--header-row N] --out results.json

A column is named by its header text or by its letter (B). Verdicts are read as passed for
pass/passed/ok, failed for fail/failed/nok/ng, blocked for blocked, and not-run for anything
else that is not empty (not tested, n/a, open), with the cell text kept as the reason.
Exit code 0 = done, 1 = refused (the reason is printed), 2 = usage.
"""
import argparse
import html
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exchange  # noqa: E402
import record  # noqa: E402
from traceability import Project  # noqa: E402

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PASS = {"pass", "passed", "ok", "p"}
FAIL = {"fail", "failed", "nok", "ng", "f"}


def column_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_workbook(path):
    """{sheet name: [rows of cell texts]} of an .xlsx file."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = {}
    for sheet in wb.find("m:sheets", NS):
        target = rels[sheet.get(REL)].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        rows = []
        for row in ET.fromstring(z.read(target)).findall(".//m:sheetData/m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                v = c.find("m:v", NS)
                value = v.text if v is not None else ""
                if c.get("t") == "s" and value:
                    value = shared[int(value)]
                elif c.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
                cells[column_index(c.get("r"))] = (value or "").strip()
            rows.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
        sheets[sheet.get("name")] = rows
    return sheets


def table(path, sheet, header_row):
    sheets = read_workbook(path)
    if sheet not in sheets:
        return None, None, "no sheet %r; the file has: %s" % (sheet, ", ".join(sheets))
    rows = sheets[sheet]
    if header_row > len(rows):
        return None, None, "sheet %r has %d rows; --header-row %d is beyond them" % (sheet, len(rows), header_row)
    return rows[header_row - 1], rows[header_row:], None


def resolve(header, columns):
    """{name: column index} from NAME=COL, where COL is a header text or a column letter."""
    out, problems = {}, []
    for spec in columns or []:
        if "=" not in spec:
            problems.append("--column takes NAME=COL, got %r" % spec)
            continue
        name, col = spec.split("=", 1)
        if col in header:
            out[name] = header.index(col)
        elif re.fullmatch(r"[A-Z]{1,3}", col):
            out[name] = column_index(col)
        else:
            problems.append("column %r is neither a header of the sheet nor a column letter" % col)
    return out, problems


def records_of(args):
    header, rows, problem = table(args.file, args.sheet, args.header_row)
    if problem:
        return None, [problem]
    cols, problems = resolve(header, args.column)
    problems += ["--column %s=... is needed" % n for n in ("source_id", "text") if n not in cols]
    if problems:
        return None, problems
    records = []
    for row in rows:
        cell = {name: (row[i] if i < len(row) else "") for name, i in cols.items()}
        if not cell.get("source_id") and not cell.get("text"):
            continue                                       # empty row
        records.append({"source_id": cell.get("source_id"), "title": cell.get("title"), "text": cell.get("text"),
                        "attributes": {k: v for k, v in cell.items() if k not in ("source_id", "title", "text") and v}})
    return records, []


def cmd_sheets(project, args):
    for name, rows in read_workbook(args.file).items():
        widest = max(rows[:15], key=lambda r: len([v for v in r if v]), default=[])
        print("%-30s %4d rows  %s" % (name, len(rows), " | ".join(v[:20] for v in widest if v)[:150]))
    return 0


def cmd_import(project, args):
    records, problems = records_of(args)
    if problems:
        return record.stop(problems)
    problems, written = exchange.register(project, args.type, args.source, args.version, args.received, records, args.dry_run)
    if problems:
        return record.stop(problems)
    if args.dry_run:
        for rec in records[:2]:
            print("--- %s (%s)\n%s" % (rec.get("title") or "-", rec["source_id"], str(rec["text"])[:400]))
    print("%s %d %s items from %s, version %s: %s" % ("would write" if args.dry_run else "wrote", len(written), args.type,
                                                    args.source, args.version,
                                                    "%s to %s" % (written[0], written[-1]) if written else "-"))
    return 0


def cmd_compare(project, args):
    records, problems = records_of(args)
    if problems:
        return record.stop(problems)
    return exchange.print_comparison(project, args.source, records)


def cmd_results(project, args):
    header, rows, problem = table(args.file, args.sheet, args.header_row)
    if problem:
        return record.stop([problem])
    cols, problems = resolve(header, args.column)
    problems += ["--column %s=... is needed" % n for n in ("test", "verdict") if n not in cols]
    if problems:
        return record.stop(problems)
    known = set(project.items)
    results, skipped = [], []
    for row in rows:
        def get(name):
            i = cols.get(name)
            return row[i] if i is not None and i < len(row) else ""
        test, verdict = get("test"), get("verdict")
        if not test or not verdict:
            continue
        if test not in known:
            skipped.append(test)
            continue
        low = verdict.strip().lower()
        entry = {"test": test, "verdict": "passed" if low in PASS else "failed" if low in FAIL
                 else "blocked" if low == "blocked" else "not-run"}
        reason = get("reason")
        if entry["verdict"] == "not-run":
            entry["reason"] = reason or verdict
        elif reason:
            entry["reason"] = reason
        results.append(entry)
    if skipped:
        print("not test cases of the project, left out: %s" % ", ".join(sorted(set(skipped))[:12]))
    Path(args.out).write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("wrote %s: %d results (%s); record them with `record.py test-run --results %s ...`"
          % (args.out, len(results), ", ".join("%d %s" % (n, v) for v, n in sorted(counts.items())), args.out))
    return 0


def cmd_export(project, args):
    import document                                       # the workbook writer of the document generator
    rows, unknown = [], [t for t in args.type if t not in project.types]
    if unknown:
        return record.stop(["unknown type: %s" % ", ".join(unknown)])
    items = sorted((i for i in project.items.values() if i.type in args.type and project.live(i)), key=lambda i: i.id)
    for item in items:
        section = exchange.first_section(project, item.type)
        links = "; ".join("%s: %s" % (role, ", ".join(t for t, _ in item.targets(role))) for role in (item.front.get("links") or {}))
        rows.append([item.id, item.type, item.title, item.status, str(item.front.get("asil") or ""),
                     item.sections.get(section, "").strip(), links, item.hash])
    doc = document.Doc("Export of %s" % ", ".join(args.type))
    doc.add("heading", 1, "Items", None)
    doc.add("table", ["id", "type", "title", "status", "asil", "text", "links", "content hash"], rows)
    info = document.provenance(project, "export", {"title": doc.title}, items, None)
    info["left_out"] = []
    Path(args.out).write_bytes(document.to_xlsx(doc, info))
    print("wrote %s: %d items" % (args.out, len(items)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("sheets").add_argument("file")
    for name in ("import", "compare", "results"):
        p = sub.add_parser(name)
        p.add_argument("file")
        p.add_argument("--sheet", required=True)
        p.add_argument("--column", action="append", required=True, help="NAME=COL, COL a header text or a column letter")
        p.add_argument("--header-row", type=int, default=1)
        if name in ("import", "compare"):
            p.add_argument("--source", required=True)
        if name == "import":
            p.add_argument("--type", required=True)
            p.add_argument("--version", required=True)
            p.add_argument("--received")
            p.add_argument("--dry-run", action="store_true")
        if name == "results":
            p.add_argument("--out", required=True)
    export = sub.add_parser("export")
    export.add_argument("--type", action="append", required=True)
    export.add_argument("--out", required=True)
    args = ap.parse_args()
    project = Project(args.project)
    return {"sheets": cmd_sheets, "import": cmd_import, "compare": cmd_compare, "results": cmd_results,
            "export": cmd_export}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
