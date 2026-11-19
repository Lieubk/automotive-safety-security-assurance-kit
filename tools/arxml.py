#!/usr/bin/env python3
"""Read the software architecture from an AUTOSAR Classic model (ARXML).

Commands
    import FILE [--dry-run]
        a `software-component` item per SW component type and a `software-interface`
        item per port interface of the file, in state draft: kind from the AUTOSAR
        type, `provided_by` and `used_by` from the P- and R-ports, `elements` from the
        data elements and `operations` from the operations with their arguments,
        `part_of` from the compositions, and `model` naming the file. What the
        model does not say - purpose, responsibility, layer, origin, ASIL, the
        requirements a component fulfils - is left for the architect.
        Refused when items with the same names already exist: use `compare`.
    compare FILE
        what the items say against the model: components and interfaces the model
        has and the items lack or the other way round, and providers, users, data
        elements and operations that differ. Writes nothing.

Items are matched to the model by their short name, which is the start of the title
("<ShortName> - <description>"), as `/sw-architecture` names components.

Options
    --project DIR      project root (default: current directory)

Requires PyYAML. The model is data and is only read.
"""
import argparse
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record  # noqa: E402
from traceability import Project, as_list  # noqa: E402

COMPONENT_KINDS = {
    "APPLICATION-SW-COMPONENT-TYPE": "application", "SENSOR-ACTUATOR-SW-COMPONENT-TYPE": "sensor-actuator",
    "COMPOSITION-SW-COMPONENT-TYPE": "composition", "SERVICE-SW-COMPONENT-TYPE": "service",
    "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE": "complex-driver", "ECU-ABSTRACTION-SW-COMPONENT-TYPE": "ecu-abstraction",
    "PARAMETER-SW-COMPONENT-TYPE": "parameter", "NV-BLOCK-SW-COMPONENT-TYPE": "other", "SERVICE-PROXY-SW-COMPONENT-TYPE": "other",
}
INTERFACE_KINDS = {
    "SENDER-RECEIVER-INTERFACE": "sender-receiver", "CLIENT-SERVER-INTERFACE": "client-server",
    "MODE-SWITCH-INTERFACE": "mode-switch", "PARAMETER-INTERFACE": "parameter", "NV-DATA-INTERFACE": "non-volatile-data",
    "TRIGGER-INTERFACE": "trigger",
}
DIRECTIONS = {"IN": "in", "OUT": "out", "INOUT": "inout"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def child(element, name):
    return next((c for c in element if local(c.tag) == name), None)


def short_name(element):
    node = child(element, "SHORT-NAME")
    return node.text.strip() if node is not None and node.text else None


def ref_name(text):
    return (text or "").strip().rsplit("/", 1)[-1]


def read_model(path):
    """Components with ports and parts, interfaces with elements and operations, keyed by short name."""
    root = ElementTree.parse(str(path)).getroot()
    components, interfaces = {}, {}
    for element in root.iter():
        tag = local(element.tag)
        if tag in COMPONENT_KINDS and short_name(element):
            provides, uses, parts = [], [], []
            for port in element.iter():
                ptag = local(port.tag)
                if ptag == "P-PORT-PROTOTYPE":
                    provides += [ref_name(r.text) for r in port.iter() if local(r.tag) == "PROVIDED-INTERFACE-TREF"]
                elif ptag == "R-PORT-PROTOTYPE":
                    uses += [ref_name(r.text) for r in port.iter() if local(r.tag) == "REQUIRED-INTERFACE-TREF"]
                elif ptag == "SW-COMPONENT-PROTOTYPE":
                    parts += [ref_name(r.text) for r in port.iter() if local(r.tag) == "TYPE-TREF"]
            components[short_name(element)] = {"kind": COMPONENT_KINDS[tag], "provides": sorted(set(provides)),
                                                "uses": sorted(set(uses)), "parts": sorted(set(parts))}
        elif tag in INTERFACE_KINDS and short_name(element):
            elements, operations = [], []
            for data in element.iter():
                dtag = local(data.tag)
                if dtag in ("VARIABLE-DATA-PROTOTYPE", "PARAMETER-DATA-PROTOTYPE") and short_name(data):
                    type_ref = next((r.text for r in data if local(r.tag) == "TYPE-TREF"), None)
                    elements.append({"name": short_name(data), "direction": "out", "type": ref_name(type_ref) or "?"})
                elif dtag == "CLIENT-SERVER-OPERATION" and short_name(data):
                    arguments = []
                    for argument in data.iter():
                        if local(argument.tag) == "ARGUMENT-DATA-PROTOTYPE" and short_name(argument):
                            direction = child(argument, "DIRECTION")
                            type_ref = next((r.text for r in argument if local(r.tag) == "TYPE-TREF"), None)
                            arguments.append({"name": short_name(argument),
                                              "direction": DIRECTIONS.get((direction.text or "").strip() if direction is not None else "", "in"),
                                              "type": ref_name(type_ref) or "?"})
                    operation = {"name": short_name(data)}
                    if arguments:
                        operation["arguments"] = arguments
                    operations.append(operation)
            interfaces[short_name(element)] = {"kind": INTERFACE_KINDS[tag], "elements": elements, "operations": operations}
    return components, interfaces


def items_by_name(project, type_name):
    return {item.title.split(" - ")[0].strip(): item for item in project.of_type(type_name) if project.live(item)}


def cmd_import(project, args):
    components, interfaces = read_model(args.file)
    existing = set(items_by_name(project, "software-component")) & set(components)
    existing |= set(items_by_name(project, "software-interface")) & set(interfaces)
    if existing:
        return record.stop(["items with these names exist already: %s; compare instead (`python tools/arxml.py compare`)"
                            % ", ".join(sorted(existing))])
    try:
        model = Path(args.file).resolve().relative_to(project.root).as_posix()
    except ValueError:
        model = str(Path(args.file))
    ids, number = {}, int(record.next_id(project, "software-component").rsplit("-", 1)[1])
    for name in sorted(components):
        ids[name] = "CMP-%04d" % number
        number += 1
    number = int(record.next_id(project, "software-interface").rsplit("-", 1)[1])
    for name in sorted(interfaces):
        ids[name] = "IFC-%04d" % number
        number += 1
    parent = {part: name for name, spec in components.items() for part in spec["parts"]}
    for name, spec in sorted(components.items()):
        front = {"id": ids[name], "type": "software-component", "title": "%s - from the AUTOSAR model" % name,
                 "status": "draft", "kind": spec["kind"], "model": model}
        if parent.get(name) in ids:
            front["links"] = {"part_of": [ids[parent[name]]]}
        if not args.dry_run:
            record.write_item(project, "software-component", front,
                              "\n## Purpose\n\n(to be written: why the component exists)\n")
    for name, spec in sorted(interfaces.items()):
        providers = [ids[c] for c, cs in sorted(components.items()) if name in cs["provides"] and cs["kind"] != "composition"]
        users = [ids[c] for c, cs in sorted(components.items()) if name in cs["uses"] and cs["kind"] != "composition"]
        front = {"id": ids[name], "type": "software-interface", "title": "%s - from the AUTOSAR model" % name,
                 "status": "draft", "kind": spec["kind"]}
        if providers:
            front["provided_by"] = providers[0]
        if users:
            front["used_by"] = users
        if spec["elements"]:
            front["elements"] = spec["elements"]
        if spec["operations"]:
            front["operations"] = spec["operations"]
        if not args.dry_run:
            record.write_item(project, "software-interface", front,
                              "\n## Description\n\n(to be written: what the interface is for, its error behaviour)%s\n"
                              % ("\n\nProvided by more than one component in the model: %s." % ", ".join(providers)
                                 if len(providers) > 1 else ""))
    print("%s %d components and %d interfaces from %s" % ("would write" if args.dry_run else "wrote",
                                                        len(components), len(interfaces), args.file))
    return 0


def cmd_compare(project, args):
    components, interfaces = read_model(args.file)
    have_c, have_i = items_by_name(project, "software-component"), items_by_name(project, "software-interface")
    name_of = {item.id: name for name, item in have_c.items()}
    lines = []
    lines += ["component %s is in the model, no item names it" % n for n in sorted(set(components) - set(have_c))]
    lines += ["component %s (%s) is not in the model" % (n, have_c[n].id) for n in sorted(set(have_c) - set(components))]
    lines += ["interface %s is in the model, no item names it" % n for n in sorted(set(interfaces) - set(have_i))]
    lines += ["interface %s (%s) is not in the model" % (n, have_i[n].id) for n in sorted(set(have_i) - set(interfaces))]
    for name in sorted(set(interfaces) & set(have_i)):
        item, spec = have_i[name], interfaces[name]
        model_providers = {c for c, cs in components.items() if name in cs["provides"] and cs["kind"] != "composition"}
        model_users = {c for c, cs in components.items() if name in cs["uses"] and cs["kind"] != "composition"}
        item_providers = {name_of.get(str(r), str(r)) for r in as_list(item.front.get("provided_by"))}
        item_users = {name_of.get(str(r), str(r)) for r in as_list(item.front.get("used_by"))}
        if model_providers != item_providers:
            lines.append("interface %s (%s): provided by %s in the model, %s in the item"
                         % (name, item.id, ", ".join(sorted(model_providers)) or "-", ", ".join(sorted(item_providers)) or "-"))
        if model_users != item_users:
            lines.append("interface %s (%s): used by %s in the model, %s in the item"
                         % (name, item.id, ", ".join(sorted(model_users)) or "-", ", ".join(sorted(item_users)) or "-"))
        for key in ("elements", "operations"):
            model_names = {e["name"] for e in spec[key]}
            item_names = {str(e.get("name")) for e in as_list(item.front.get(key)) if isinstance(e, dict)}
            if model_names != item_names:
                lines.append("interface %s (%s): %s %s in the model, %s in the item"
                             % (name, item.id, key, ", ".join(sorted(model_names)) or "-", ", ".join(sorted(item_names)) or "-"))
    for line in lines:
        print(line)
    print("%d differences between the items and %s" % (len(lines), args.file))
    return 1 if lines else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import")
    imp.add_argument("file")
    imp.add_argument("--dry-run", action="store_true")
    sub.add_parser("compare").add_argument("file")
    args = ap.parse_args()
    project = Project(args.project)
    return {"import": cmd_import, "compare": cmd_compare}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
