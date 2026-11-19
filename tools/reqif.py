#!/usr/bin/env python3
"""Exchange requirements with ALM tools through ReqIF (Requirements Interchange Format).

Commands
    import FILE --type TYPE --source NAME --version V [--received DATE]
           [--id-attribute NAME] [--title-attribute NAME] [--text-attribute NAME] [--dry-run]
        one imported item per SPEC-OBJECT of the file, in state draft, unchanged:
        the text becomes the first section of the type (`Statement` for
        requirements), `imported` names source, version, date received and the
        identifier in the source. Refused when the source already has imported
        items: a new version is compared first (`compare`), and `/import-inputs`
        takes the changes over with the user.
    compare FILE --source NAME [--id-attribute ...] [--text-attribute ...]
        what a new version changes against the imported items of the source: new,
        changed and removed objects by their identifier in the source. Writes nothing.
    export --type TYPE [--type TYPE ...] --out FILE [--title TEXT]
        the items of the types as SPEC-OBJECTS (identifier, title, text, status,
        ASIL where the type has one) and their links between exported items as
        SPEC-RELATIONS, for delivery to an ALM tool.

The attribute names default to the ReqIF implementation guide's ReqIF.ForeignID,
ReqIF.Name and ReqIF.Text; a tool that uses others is named with the options.
Values are read by the long name of their attribute definition; XHTML is reduced to
plain text with paragraph breaks.

Options
    --project DIR      project root (default: current directory)

Requires PyYAML. The XML parser is the standard library's; files from outside are
data and are only read.
"""
import argparse
import datetime
import re
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record  # noqa: E402
from traceability import Project, as_list  # noqa: E402

REQIF_NS = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
XHTML_NS = "http://www.w3.org/1999/xhtml"
BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def children(element, name):
    return [c for c in element.iter() if local(c.tag) == name]


def xhtml_text(element):
    """Plain text of an XHTML value: paragraphs and line breaks kept, other markup dropped."""
    parts = []

    def walk(node):
        if local(node.tag) in BLOCKS and parts and not parts[-1].endswith("\n"):
            parts.append("\n")
        if node.text:
            parts.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                parts.append(child.tail)
        if local(node.tag) in BLOCKS:
            parts.append("\n")

    walk(element)
    lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(parts).split("\n")]
    return "\n\n".join(line for line in lines if line)


def read_objects(path):
    """[{identifier, values: {long name: text}}] of the SPEC-OBJECTS of a ReqIF file."""
    root = ElementTree.parse(str(path)).getroot()
    names, enums = {}, {}
    for definition in root.iter():
        tag = local(definition.tag)
        if tag.startswith("ATTRIBUTE-DEFINITION-") and definition.get("IDENTIFIER"):
            names[definition.get("IDENTIFIER")] = definition.get("LONG-NAME") or definition.get("IDENTIFIER")
        if tag == "ENUM-VALUE" and definition.get("IDENTIFIER"):
            enums[definition.get("IDENTIFIER")] = definition.get("LONG-NAME") or definition.get("IDENTIFIER")
    objects = []
    for spec in children(root, "SPEC-OBJECT"):
        values = {}
        for value in spec.iter():
            tag = local(value.tag)
            if not tag.startswith("ATTRIBUTE-VALUE-"):
                continue
            ref = next((r.text for r in value.iter() if local(r.tag).startswith("ATTRIBUTE-DEFINITION-")
                        and local(r.tag).endswith("-REF")), None)
            name = names.get((ref or "").strip(), (ref or "").strip())
            if tag == "ATTRIBUTE-VALUE-XHTML":
                content = next((c for c in value if local(c.tag) == "THE-VALUE"), None)
                values[name] = xhtml_text(content) if content is not None else ""
            elif tag == "ATTRIBUTE-VALUE-ENUMERATION":
                values[name] = ", ".join(enums.get((r.text or "").strip(), (r.text or "").strip())
                                         for r in value.iter() if local(r.tag) == "ENUM-VALUE-REF")
            else:
                values[name] = value.get("THE-VALUE", "")
        objects.append({"identifier": spec.get("IDENTIFIER"), "values": values})
    return objects


def source_id(obj, args):
    return obj["values"].get(args.id_attribute) or obj["identifier"]


def text_of(obj, args):
    return obj["values"].get(args.text_attribute, "").strip()


def first_section(project, type_name):
    sections = list((project.types[type_name].get("sections") or {}).keys())
    return sections[0] if sections else "Statement"


def imported_of(project, source):
    return {str((i.front.get("imported") or {}).get("source_id")): i for i in project.items.values()
            if isinstance(i.front.get("imported"), dict) and i.front["imported"].get("source") == source}


def cmd_import(project, args):
    if args.type not in project.types:
        return record.stop(["unknown type: %s" % args.type])
    if imported_of(project, args.source):
        return record.stop(["%s already has imported items: compare the new version first "
                            "(`python tools/reqif.py compare`), then take the changes over with /import-inputs" % args.source])
    objects = read_objects(args.file)
    problems = []
    seen = set()
    for obj in objects:
        sid = source_id(obj, args)
        if sid in seen:
            problems.append("identifier %s occurs twice in the file" % sid)
        seen.add(sid)
        if not text_of(obj, args):
            problems.append("%s has no value for %s" % (sid, args.text_attribute))
    if problems:
        return record.stop(problems)
    section = first_section(project, args.type)
    attributes = project.attributes(args.type)
    mapped = [tuple(m.split("=", 1)) for m in args.attribute or [] if "=" in m]
    unknown = [n for n, _ in mapped if n not in attributes]
    if unknown or len(mapped) != len(args.attribute or []):
        return record.stop(["--attribute takes <item attribute>=<ReqIF attribute>; %s has no attribute %s"
                            % (args.type, ", ".join(unknown) or "-")])
    received = args.received or datetime.date.today().isoformat()
    number = int(record.next_id(project, args.type).rsplit("-", 1)[1])
    prefix = project.types[args.type]["prefix"]
    written = []
    for obj in objects:
        text = text_of(obj, args)
        title = obj["values"].get(args.title_attribute) or text.split("\n")[0][:70]
        front = {"id": "%s-%04d" % (prefix, number), "type": args.type, "title": title, "status": "draft",
                 "imported": {"source": args.source, "version": args.version, "received": received,
                              "source_id": source_id(obj, args)}}
        if "source_document" in attributes:
            front["source_document"] = "%s, version %s" % (args.source, args.version)
        if "source_id" in attributes:
            front["source_id"] = source_id(obj, args)
        for name, reqif_name in mapped:
            value = obj["values"].get(reqif_name)
            if value not in (None, ""):
                front[name] = value
        body = "\n## %s\n\n%s\n" % (section, text)
        written.append(front["id"])
        if not args.dry_run:
            record.write_item(project, args.type, front, body)
        number += 1
    if args.dry_run:
        for obj in objects[:2]:
            print("--- %s (%s)\n%s" % (obj["values"].get(args.title_attribute) or "-", source_id(obj, args),
                                     text_of(obj, args)[:400]))
    print("%s %d %s items from %s, version %s: %s" % ("would write" if args.dry_run else "wrote", len(written),
                                                    args.type, args.source, args.version,
                                                    "%s to %s" % (written[0], written[-1]) if written else "-"))
    return 0


def normalised(text):
    return re.sub(r"\s+", " ", text or "").strip()


def cmd_compare(project, args):
    known = imported_of(project, args.source)
    if not known:
        print("%s has no imported items; nothing to compare with" % args.source)
        return 1
    objects = {source_id(o, args): o for o in read_objects(args.file)}
    new = sorted(set(objects) - set(known))
    removed = sorted(set(known) - set(objects))
    changed = []
    for sid in sorted(set(objects) & set(known)):
        item = known[sid]
        section = first_section(project, item.type)
        if normalised(item.sections.get(section, "")) != normalised(text_of(objects[sid], args)):
            changed.append((sid, item.id))
    for sid in new:
        print("new      %s  %s" % (sid, text_of(objects[sid], args).split("\n")[0][:90]))
    for sid, item_id in changed:
        print("changed  %s  %s" % (sid, item_id))
    for sid in removed:
        print("removed  %s  %s" % (sid, known[sid].id))
    print("%d new, %d changed, %d removed, %d unchanged against the imported items of %s"
          % (len(new), len(changed), len(removed), len(objects) - len(new) - len(changed), args.source))
    return 0


def cmd_export(project, args):
    items = sorted([i for i in project.items.values() if i.type in args.type and project.live(i)], key=lambda i: i.id)
    exported = {i.id for i in items}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    ElementTree.register_namespace("", REQIF_NS)
    ElementTree.register_namespace("xhtml", XHTML_NS)
    q = lambda name: "{%s}%s" % (REQIF_NS, name)                                   # noqa: E731
    root = ElementTree.Element(q("REQ-IF"))
    header = ElementTree.SubElement(ElementTree.SubElement(root, q("THE-HEADER")), q("REQ-IF-HEADER"),
                                    {"IDENTIFIER": "header"})
    for name, value in (("CREATION-TIME", now), ("REQ-IF-TOOL-ID", "aspice toolkit reqif.py"),
                        ("REQ-IF-VERSION", "1.0"), ("SOURCE-TOOL-ID", "aspice toolkit"),
                        ("TITLE", args.title or "Export of %s" % ", ".join(args.type))):
        ElementTree.SubElement(header, q(name)).text = value
    content = ElementTree.SubElement(ElementTree.SubElement(root, q("CORE-CONTENT")), q("REQ-IF-CONTENT"))
    datatypes = ElementTree.SubElement(content, q("DATATYPES"))
    ElementTree.SubElement(datatypes, q("DATATYPE-DEFINITION-STRING"),
                           {"IDENTIFIER": "dt-string", "LONG-NAME": "String", "MAX-LENGTH": "4000", "LAST-CHANGE": now})
    ElementTree.SubElement(datatypes, q("DATATYPE-DEFINITION-XHTML"),
                           {"IDENTIFIER": "dt-xhtml", "LONG-NAME": "XHTML", "LAST-CHANGE": now})
    spec_types = ElementTree.SubElement(content, q("SPEC-TYPES"))
    object_type = ElementTree.SubElement(spec_types, q("SPEC-OBJECT-TYPE"),
                                         {"IDENTIFIER": "type-item", "LONG-NAME": "Item", "LAST-CHANGE": now})
    definitions = ElementTree.SubElement(object_type, q("SPEC-ATTRIBUTES"))
    fields = [("ReqIF.ForeignID", "string"), ("ReqIF.Name", "string"), ("ReqIF.Text", "xhtml"),
              ("Type", "string"), ("Status", "string"), ("ASIL", "string")]
    for name, kind in fields:
        definition = ElementTree.SubElement(definitions, q("ATTRIBUTE-DEFINITION-%s" % kind.upper()),
                                            {"IDENTIFIER": "attr-" + name, "LONG-NAME": name, "LAST-CHANGE": now})
        ElementTree.SubElement(ElementTree.SubElement(definition, q("TYPE")),
                               q("DATATYPE-DEFINITION-%s-REF" % kind.upper())).text = "dt-" + kind
    roles = sorted({role for i in items for role in (i.front.get("links") or {})
                    for target, _ in i.targets(role) if target in exported})
    for role in roles:
        ElementTree.SubElement(spec_types, q("SPEC-RELATION-TYPE"),
                               {"IDENTIFIER": "rel-" + role, "LONG-NAME": role, "LAST-CHANGE": now})
    ElementTree.SubElement(spec_types, q("SPECIFICATION-TYPE"),
                           {"IDENTIFIER": "type-spec", "LONG-NAME": "Specification", "LAST-CHANGE": now})
    objects = ElementTree.SubElement(content, q("SPEC-OBJECTS"))
    for item in items:
        spec = ElementTree.SubElement(objects, q("SPEC-OBJECT"),
                                      {"IDENTIFIER": item.id, "LONG-NAME": item.title, "LAST-CHANGE": now})
        ElementTree.SubElement(ElementTree.SubElement(spec, q("TYPE")), q("SPEC-OBJECT-TYPE-REF")).text = "type-item"
        values = ElementTree.SubElement(spec, q("VALUES"))
        section = first_section(project, item.type)
        for name, kind in fields:
            text = {"ReqIF.ForeignID": item.id, "ReqIF.Name": item.title, "ReqIF.Text": item.sections.get(section, ""),
                    "Type": item.type, "Status": item.status, "ASIL": str(item.front.get("asil") or "")}[name]
            if kind == "xhtml":
                value = ElementTree.SubElement(values, q("ATTRIBUTE-VALUE-XHTML"))
                ElementTree.SubElement(ElementTree.SubElement(value, q("DEFINITION")),
                                       q("ATTRIBUTE-DEFINITION-XHTML-REF")).text = "attr-" + name
                div = ElementTree.SubElement(ElementTree.SubElement(value, q("THE-VALUE")), "{%s}div" % XHTML_NS)
                for paragraph in [p for p in text.strip().split("\n\n") if p.strip()]:
                    ElementTree.SubElement(div, "{%s}p" % XHTML_NS).text = normalised(paragraph)
            else:
                value = ElementTree.SubElement(values, q("ATTRIBUTE-VALUE-STRING"), {"THE-VALUE": text})
                ElementTree.SubElement(ElementTree.SubElement(value, q("DEFINITION")),
                                       q("ATTRIBUTE-DEFINITION-STRING-REF")).text = "attr-" + name
    relations = ElementTree.SubElement(content, q("SPEC-RELATIONS"))
    count = 0
    for item in items:
        for role in sorted(item.front.get("links") or {}):
            for target, _ in item.targets(role):
                if target not in exported:
                    continue
                count += 1
                relation = ElementTree.SubElement(relations, q("SPEC-RELATION"),
                                                  {"IDENTIFIER": "%s-%s-%s" % (item.id, role, target), "LAST-CHANGE": now})
                ElementTree.SubElement(ElementTree.SubElement(relation, q("TYPE")), q("SPEC-RELATION-TYPE-REF")).text = "rel-" + role
                ElementTree.SubElement(ElementTree.SubElement(relation, q("SOURCE")), q("SPEC-OBJECT-REF")).text = item.id
                ElementTree.SubElement(ElementTree.SubElement(relation, q("TARGET")), q("SPEC-OBJECT-REF")).text = target
    specifications = ElementTree.SubElement(content, q("SPECIFICATIONS"))
    specification = ElementTree.SubElement(specifications, q("SPECIFICATION"),
                                           {"IDENTIFIER": "spec", "LONG-NAME": args.title or "Export", "LAST-CHANGE": now})
    ElementTree.SubElement(ElementTree.SubElement(specification, q("TYPE")), q("SPECIFICATION-TYPE-REF")).text = "type-spec"
    hierarchy = ElementTree.SubElement(specification, q("CHILDREN"))
    for item in items:
        node = ElementTree.SubElement(hierarchy, q("SPEC-HIERARCHY"), {"IDENTIFIER": "h-" + item.id, "LAST-CHANGE": now})
        ElementTree.SubElement(ElementTree.SubElement(node, q("OBJECT")), q("SPEC-OBJECT-REF")).text = item.id
    ElementTree.indent(root)
    Path(args.out).write_bytes(ElementTree.tostring(root, encoding="utf-8", xml_declaration=True))
    print("wrote %s: %d items, %d relations" % (args.out, len(items), count))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("import", "compare"):
        p = sub.add_parser(name)
        p.add_argument("file")
        p.add_argument("--source", required=True)
        p.add_argument("--id-attribute", default="ReqIF.ForeignID")
        p.add_argument("--text-attribute", default="ReqIF.Text")
        if name == "import":
            p.add_argument("--type", required=True)
            p.add_argument("--version", required=True)
            p.add_argument("--received")
            p.add_argument("--title-attribute", default="ReqIF.Name")
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--attribute", action="append",
                           help="<item attribute>=<ReqIF attribute>: take a value over, for example asil=ASIL")
    export = sub.add_parser("export")
    export.add_argument("--type", required=True, action="append")
    export.add_argument("--out", required=True)
    export.add_argument("--title")
    args = ap.parse_args()
    project = Project(args.project)
    return {"import": cmd_import, "compare": cmd_compare, "export": cmd_export}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
