"""Fill a customer's Excel template with a document of tools/document.py.

A map file (YAML) says which workbook to fill and where:

    template: customer-test-report.xlsx      # the customer's workbook, relative to this map file
    cells:                                   # single cells: document information
      - {sheet: Cover, cell: C5, value: "{{project}}"}
      - {sheet: Cover, cell: C6, value: "commit {{commit}}, {{baseline}}"}
    tables:
      - sheet: Specification                 # a table of the document, chosen by its column names
        header_row: 11
        from: table
        columns: {"No": "#", "Test ID": "test case", "Description": "title",
                  "Expected result": "expected result", "Result": "verdict"}
        values: {"Result": {passed: Passed, failed: Failed, not run: Not Test}}
      - sheet: Requirements                  # one row per item of the document
        header_row: 3
        from: items
        types: [software-requirement]
        columns: {"ID": id, "Requirement": "section:Statement", "ASIL": asil, "Derived from": "link:derived_from"}

Placeholders in `cells`: {{title}}, {{project}}, {{kind}}, {{date}}, {{commit}}, {{baseline}},
{{draft}}. Template headers are matched ignoring case, spaces and punctuation. A column
source of `from: table` is a column name of the document's table; of `from: items` it is
`id`, `title`, `status`, `type`, `hash`, an attribute name, `section:<name>`, `link:<role>`
(targets) or `link-from:<role>` (items that link to it). `#` numbers the rows. `values`
translates the document's words into the template's, per template header, for example into
the entries of a drop-down list.

Rows are written from the row below the header. Before that, what the template holds below
the header is cleared: by default in every column that has a header (`clear: table`; formulas
stay), with `clear: mapped` only in the mapped columns, with `clear: false` nowhere - a
template is often an earlier report whose rows must not mix with the new ones. Rows beyond
the template's formatted rows take the style of the first data row. Everything else of the
workbook stays: other sheets, merged cells, data validations, conditional formatting, names.
A sheet "Document information" is added with the provenance, the DRAFT reasons and the items
with their content hashes. Needs the package openpyxl; charts of the template are not kept.
"""
import copy
import io
import re
from pathlib import Path

import yaml

FIELDS = ("title", "project", "kind", "date", "commit", "baseline", "draft")
ITEM_FIELDS = ("id", "title", "status", "type", "hash")


class MapLoader(yaml.SafeLoader):
    """YAML as people write headers: No, Yes, On and Off stay words; only true and false are booleans."""


MapLoader.yaml_implicit_resolvers = {key: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:bool"]
                                     for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()}
MapLoader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
                                list("tTfF"))


def norm(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def load_map(path):
    """The map and the problems found in it."""
    path = Path(path)
    if not path.is_file():
        return None, ["map %s does not exist" % path]
    try:
        spec = yaml.load(path.read_text(encoding="utf-8"), Loader=MapLoader) or {}
    except yaml.YAMLError as exc:
        return None, ["map %s is not valid YAML: %s" % (path, exc)]
    problems = []
    template = path.parent / str(spec.get("template") or "")
    if not spec.get("template") or not template.is_file():
        problems.append("map %s: `template` must name the customer's workbook next to it (%s not found)" % (path.name, template))
    spec["template_path"] = template
    for n, cell in enumerate(spec.get("cells") or [], 1):
        if not isinstance(cell, dict) or not all(cell.get(k) for k in ("sheet", "cell")) or "value" not in cell:
            problems.append("map %s: cells entry %d needs sheet, cell and value" % (path.name, n))
    for n, table in enumerate(spec.get("tables") or [], 1):
        if not isinstance(table, dict) or not table.get("sheet") or not isinstance(table.get("header_row"), int) \
                or table.get("from") not in ("table", "items") or not isinstance(table.get("columns"), dict) \
                or not table.get("columns"):
            problems.append("map %s: tables entry %d needs sheet, header_row (a number), from (table or items) "
                            "and columns (template header: source)" % (path.name, n))
        elif table["from"] == "items" and not table.get("types"):
            problems.append("map %s: tables entry %d takes its rows from items and needs `types`" % (path.name, n))
    if not spec.get("cells") and not spec.get("tables"):
        problems.append("map %s fills nothing: it has neither cells nor tables" % path.name)
    return spec, problems


def cell_text(text, plain):
    """A value for a cell: Markdown reduced to text, inline code without its backticks."""
    return re.sub(r"`([^`]*)`", r"\1", plain(text)).strip()


def table_rows(doc, sources, plain):
    """Rows of the document's tables that have every source column, in the order of `sources`."""
    wanted = [norm(s) for s in sources if s != "#"]
    rows, headers = [], []
    for node in doc.nodes:
        if node[0] != "table":
            continue
        names = [norm(h) for h in node[1]]
        headers.append(", ".join(map(str, node[1])))
        if all(w in names for w in wanted):
            index = [names.index(norm(s)) if s != "#" else None for s in sources]
            rows += [[cell_text(row[i], plain) if i is not None and i < len(row) else "" for i in index]
                     for row in node[2]]
    return rows, sorted(set(headers))


def item_value(project, item, source, plain, value_text):
    source = str(source)
    if source in ITEM_FIELDS:
        return {"id": item.id, "title": item.title, "status": item.status, "type": item.type, "hash": item.hash}[source]
    kind, _, name = source.partition(":")
    if kind == "section" and name:
        return cell_text(item.sections.get(name, ""), plain)
    if kind == "link" and name:
        return ", ".join(t for t, _ in item.targets(name))
    if kind == "link-from" and name:
        return ", ".join(sorted(project.incoming[item.id][name]))
    return value_text(item.front.get(source))


def fill(doc, info, project, map_path, plain, value_text):
    """The filled workbook as bytes, or None, with the problems that refuse it."""
    try:
        import openpyxl
        from openpyxl.cell.cell import MergedCell
    except ImportError:
        return None, ["an Excel template needs the package openpyxl (pip install openpyxl): NOT ASSESSED"]
    spec, problems = load_map(map_path)
    if problems:
        return None, problems
    template = spec["template_path"]
    workbook = openpyxl.load_workbook(str(template), keep_vba=template.suffix.lower() == ".xlsm")
    draft = "DRAFT - " + "; ".join(info["draft_reasons"]) if info["draft"] else ""
    fields = {"title": info["title"], "project": info["project"], "kind": info["kind"],
              "date": info["generated_at"][:10], "commit": info["commit"], "baseline": info["baseline"], "draft": draft}

    def sheet(name):
        if name not in workbook.sheetnames:
            problems.append("the template has no sheet %r; it has: %s" % (name, ", ".join(workbook.sheetnames)))
            return None
        return workbook[name]

    for entry in spec.get("cells") or []:
        ws = sheet(entry["sheet"])
        if ws is None:
            continue
        cell = ws[entry["cell"]]
        if isinstance(cell, MergedCell):
            problems.append("%s!%s lies inside a merged range that starts elsewhere; name its first cell"
                            % (entry["sheet"], entry["cell"]))
            continue
        cell.value = re.sub(r"\{\{(\w+)\}\}", lambda m: str(fields.get(m.group(1), m.group(0))), str(entry["value"]))
    filled = []
    for entry in spec.get("tables") or []:
        ws = sheet(entry["sheet"])
        if ws is None:
            continue
        header = {norm(c.value): c.column for c in ws[entry["header_row"]] if c.value not in (None, "")}
        columns = []
        for target, source in entry["columns"].items():
            if norm(target) in header:
                columns.append((header[norm(target)], source))
            else:
                problems.append("%s row %d has no header %r; it has: %s" % (entry["sheet"], entry["header_row"], target,
                                ", ".join(str(c.value) for c in ws[entry["header_row"]] if c.value not in (None, ""))))
        if len(columns) != len(entry["columns"]):
            continue
        if entry["from"] == "table":
            rows, headers = table_rows(doc, [s for _, s in columns], plain)
            if not headers or not any(all(s == "#" or norm(s) in [norm(h) for h in t.split(", ")] for _, s in columns)
                                      for t in headers):
                problems.append("no table of the document has the columns %s; its tables have: %s"
                                % (", ".join(str(s) for _, s in columns), " | ".join(headers) or "none"))
                continue
        else:
            items = [project.items[i["item"]] for i in info["items"]
                     if i["item"] in project.items and project.items[i["item"]].type in entry["types"]]
            rows = [[item_value(project, item, s, plain, value_text) if s != "#" else "" for _, s in columns]
                    for item in items]
        words = {}                                            # template header -> {document word: template word}
        for target, mapping in (entry.get("values") or {}).items():
            col = header.get(norm(target))
            if col is None or not isinstance(mapping, dict):
                problems.append("%s: values names %r, which is no header of row %d, or gives no mapping"
                                % (entry["sheet"], target, entry["header_row"]))
                continue
            words[col] = {norm(k): v for k, v in mapping.items()}
        for n, row in enumerate(rows, 1):
            for k, (col, source) in enumerate(columns):
                if source == "#":
                    row[k] = n
                elif col in words and norm(row[k]) in words[col]:
                    row[k] = words[col][norm(row[k])]
        first = entry["header_row"] + 1
        styles = {col: copy.copy(ws.cell(first, col)._style) for col, _ in columns}
        clear = entry.get("clear", "table")
        if clear not in ("table", "mapped", False):
            problems.append("%s: clear is table, mapped or false, not %r" % (entry["sheet"], clear))
            continue
        cleared = sorted(header.values()) if clear == "table" else [col for col, _ in columns] if clear else []
        for r in range(first, max(ws.max_row, first) + 1):
            for col in cleared:
                cell = ws.cell(r, col)
                if not isinstance(cell, MergedCell) and not str(cell.value or "").startswith("="):
                    cell.value = None
        for n, row in enumerate(rows):
            for (col, _), value in zip(columns, row):
                cell = ws.cell(first + n, col)
                if isinstance(cell, MergedCell):
                    problems.append("%s row %d column %d is merged; the template's table rows must not be"
                                    % (entry["sheet"], first + n, col))
                    break
                cell.value = value if value not in ("", None) else None
                if n and not cell.has_style:
                    cell._style = copy.copy(styles[col])
        filled.append("%s: %d rows" % (entry["sheet"], len(rows)))
    if problems:
        return None, problems
    name = "Document information"
    while name in workbook.sheetnames:
        name += " (generated)"
    ws = workbook.create_sheet(name)
    rows = [("Title", info["title"]), ("Project", info["project"]), ("Kind", info["kind"]),
            ("Generated", info["generated_at"]), ("Commit", info["commit"]),
            ("Uncommitted changes", "yes" if info["uncommitted_changes"] else "no"), ("Baseline", info["baseline"]),
            ("Draft", draft or "no"), ("Left out, not approved", ", ".join(info.get("left_out") or []) or "none"),
            ("Filled", "; ".join(filled) or "-"), ("Template", template.name), ()]
    for row in rows:
        ws.append(list(row))
    ws.append(["item", "title", "state", "content hash"])
    for i in info["items"]:
        ws.append([i["item"], i["title"], i["status"], i["hash"]])
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 24, 70
    out = io.BytesIO()
    workbook.save(out)
    return out.getvalue(), []
