#!/usr/bin/env python3
"""Check the item schema for internal consistency and against the process catalog.

Verifies that `schema/items.yaml` parses without values a YAML 1.1 parser turns
into booleans by accident, that every lifecycle, attribute set, structure and
item type it refers to is defined, and that every base practice and work
product named under `supports` exists in the catalog - the process catalog
under aspice/, or for references "21434:..." the catalog of ISO/SAE 21434. Also
lists the base practices of the engineering processes and the subclauses of the
project-level clauses of ISO/SAE 21434 that no schema element supports, so gaps
in evidence structure stay visible.

Usage:
    python tools/schema_check.py [--version 3.1]

Requires PyYAML. Exit code 0 = consistent, 1 = errors.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STAGES = {"always", "before-review", "before-approval", "optional"}
PSEUDO_SUBJECTS = {"source-file", "test-case", "any-engineering-item", "project"}
WP_ID = re.compile(r"^\d{2}-\d{2}$")


def stray_booleans(node, path=""):
    """Paths where a boolean appears outside a `values` list (yes/no/on/off traps)."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, bool):
                found.append(path + "/<boolean key>")
            found += stray_booleans(value, path + "/" + str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found += stray_booleans(value, "%s[%d]" % (path, i))
    elif isinstance(node, bool) and "/values[" not in path and "/when/" not in path \
            and not path.endswith("/may_be_empty"):
        found.append(path)
    return found


def attribute_names(schema, type_name):
    """All attribute names of a type, including those of the attribute sets it uses."""
    names = set()
    for name, spec in schema["types"][type_name]["attributes"].items():
        if name == "use":
            for used_set in spec:
                names |= set(schema["attribute_sets"].get(used_set, {}))
        else:
            names.add(name)
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", default="3.1")
    args = ap.parse_args()

    schema = yaml.safe_load((ROOT / "schema" / "items.yaml").read_text(encoding="utf-8"))
    practices, products = {}, set()
    for f in (ROOT / "aspice" / args.version / "processes").glob("*.yaml"):
        proc = yaml.safe_load(f.read_text(encoding="utf-8"))
        for bp in proc["base_practices"]:
            practices[bp["id"]] = bp["name"]
        products |= {wp["id"] for wp in proc["output_work_products"]}

    cybersecurity, cs_levels = {}, {}
    cs_file = ROOT / "iso-sae-21434" / "2021" / "catalog.yaml"
    if cs_file.exists():
        catalog = yaml.safe_load(cs_file.read_text(encoding="utf-8"))
        for clause in catalog["clauses"]:
            for sub in clause["subclauses"]:
                cybersecurity["21434:" + str(sub["id"])] = sub["name"]
                cs_levels["21434:" + str(sub["id"])] = clause["level"]
        cybersecurity.update({"21434:" + wp["id"]: wp["name"] for wp in catalog["work_products"]})

    fs_file = ROOT / "iso-26262" / "2018" / "catalog.yaml"
    if fs_file.exists():
        catalog = yaml.safe_load(fs_file.read_text(encoding="utf-8"))
        for part in catalog["parts"]:
            for clause in part["clauses"]:
                key = "26262-%s:%s" % (part["id"], clause["id"])
                cybersecurity[key] = clause["name"]
                cs_levels[key] = "project" if part["level"] in ("concept", "system", "software", "analyses")                     or (part["id"] == "2" and clause["id"] == "6") else part["level"]
                for wp in clause["work_products"]:
                    cybersecurity["26262-%s:%s" % (part["id"], wp["id"])] = wp["name"]

    errors, used = [], set()

    def supports(where, refs):
        for ref in map(str, refs or []):
            used.add(ref)
            known = cybersecurity if ref.startswith(("21434:", "26262-")) else products if WP_ID.match(ref) else practices
            if ref not in known:
                errors.append("%s: '%s' is not in the catalog" % (where, ref))

    def attributes(where, attrs):
        for name, spec in attrs.items():
            if name == "use":
                for used_set in spec:
                    if used_set not in schema["attribute_sets"]:
                        errors.append("%s: unknown attribute set '%s'" % (where, used_set))
                continue
            if spec.get("required") not in STAGES:
                errors.append("%s.%s: required must be one of %s" % (where, name, sorted(STAGES)))
            if "structure" in spec and spec["structure"] not in schema["structures"]:
                errors.append("%s.%s: unknown structure '%s'" % (where, name, spec["structure"]))

    errors += ["boolean where a word was meant: " + p for p in stray_booleans(schema)]

    for name, lifecycle in schema["lifecycles"].items():
        staged = [s for states in lifecycle.get("stages", {}).values() for s in states]
        for t in lifecycle["transitions"]:
            sources = t["from"] if isinstance(t["from"], list) else [t["from"]]
            staged += sources + [t["to"]]
        for state in staged:
            if state not in lifecycle["states"]:
                errors.append("lifecycle %s: unknown state '%s'" % (name, state))
        if set(lifecycle.get("stages", {})) != {"before-review", "before-approval"}:
            errors.append("lifecycle %s: stages must define before-review and before-approval" % name)

    for name, attrs in schema["attribute_sets"].items():
        attributes("attribute set " + name, attrs)

    for name, structure in schema["structures"].items():
        overlap = set(structure["mandatory"]) & set(structure["keys"])
        if overlap:
            errors.append("structure %s: keys listed twice: %s" % (name, sorted(overlap)))

    types, prefixes = schema["types"], {}
    for name, spec in types.items():
        where = "type " + name
        if spec["lifecycle"] not in schema["lifecycles"]:
            errors.append("%s: unknown lifecycle '%s'" % (where, spec["lifecycle"]))
        if spec["prefix"] in prefixes:
            errors.append("%s: prefix %s already used by %s" % (where, spec["prefix"], prefixes[spec["prefix"]]))
        prefixes[spec["prefix"]] = name
        attributes(where, spec["attributes"])
        for section, stage in (spec.get("sections") or {}).items():
            if stage not in STAGES:
                errors.append("%s: section '%s' has stage '%s'" % (where, section, stage))
        supports(where, spec.get("supports"))

    for i, cond in enumerate(schema.get("conditions") or [], 1):
        where = "condition %d" % i
        wanted = list(cond["when"]) + list(cond.get("attributes") or [])
        if cond["types"] == "any":      # every type that carries the attributes named
            targets = [t for t in types if all(a in attribute_names(schema, t) for a in wanted)]
            if not targets:
                errors.append("%s: no type carries %s" % (where, wanted))
        else:
            targets = cond["types"]
        if cond.get("stage") not in STAGES:
            errors.append("%s: stage must be one of %s" % (where, sorted(STAGES)))
        if "structure" in cond and cond["structure"] not in schema["structures"]:
            errors.append("%s: unknown structure '%s'" % (where, cond["structure"]))
        for target in targets:
            if target not in types:
                errors.append("%s: unknown type '%s'" % (where, target))
                continue
            known = attribute_names(schema, target)
            for attr in wanted:
                if attr not in known:
                    errors.append("%s: type %s has no attribute '%s'" % (where, target, attr))
            for section in cond.get("sections") or []:
                if section not in (types[target].get("sections") or {}):
                    errors.append("%s: type %s has no section '%s'" % (where, target, section))

    plan_values = schema["types"]["plan"]["attributes"]["kind"]["values"]
    if sorted(plan_values) != sorted(schema["plan_kinds"]):
        errors.append("plan_kinds and the allowed values of plan.kind differ")
    for kind, refs in schema["plan_kinds"].items():
        supports("plan kind " + kind, refs)

    pairs = 0
    for role, link in schema["links"].items():
        for pair in link["pairs"]:
            pairs += 1
            targets = pair["to"] if isinstance(pair["to"], list) else []
            if not targets and pair["to"] != "any":
                errors.append("link %s: 'to' must be a list of types or 'any'" % role)
            for end in [pair["from"]] + targets:
                if end not in types:
                    errors.append("link %s: unknown type '%s'" % (role, end))
            supports("link " + role, pair.get("supports"))

    rule_ids = set()
    for rule in schema["coverage"]:
        if rule["id"] in rule_ids:
            errors.append("coverage: duplicate id %s" % rule["id"])
        rule_ids.add(rule["id"])
        if rule["subject"] not in types and rule["subject"] not in PSEUDO_SUBJECTS:
            errors.append("%s: unknown subject '%s'" % (rule["id"], rule["subject"]))
        supports(rule["id"], rule.get("supports"))

    documents_file = ROOT / "schema" / "documents.yaml"
    documents = yaml.safe_load(documents_file.read_text(encoding="utf-8"))["documents"] if documents_file.exists() else {}
    for name, spec in documents.items():
        where = "document " + name
        supports(where, spec.get("supports"))
        for chapter in spec["chapters"]:
            for key in ("items", "table"):
                for type_name in (chapter.get(key) or {}).get("types", []):
                    if type_name not in types:
                        errors.append("%s: unknown type '%s'" % (where, type_name))
            matrix = chapter.get("matrix")
            if matrix and (matrix.get("of") not in types or matrix.get("role") not in schema["links"]):
                errors.append("%s: matrix of '%s' by '%s' names an unknown type or link role" % (where, matrix.get("of"), matrix.get("role")))
            for column in (chapter.get("table") or {}).get("columns", []):
                known = {"id", "title", "type", "status"} | set(schema["links"]) | {
                    a for t in chapter["table"]["types"] if t in types for a in attribute_names(schema, t)}
                if column not in known:
                    errors.append("%s: column '%s' is no attribute or link role of %s" % (where, column, chapter["table"]["types"]))

    print("schema v%s | %d types | %d link roles, %d pairs | %d coverage rules | %d structures | %d documents"
          % (schema["schema_version"], len(types), len(schema["links"]), pairs, len(rule_ids), len(schema["structures"]),
             len(documents)))
    unsupported = [bp for bp in sorted(practices, key=lambda b: (b.split(".BP")[0], int(b.split(".BP")[1])))
                   if bp.split(".")[0] in ("SYS", "SWE") and bp not in used]
    if unsupported:
        print("engineering base practices no schema element supports (%d):" % len(unsupported))
        for bp in unsupported:
            print("  %s %s" % (bp, practices[bp]))
    uncovered = [ref for ref in cybersecurity if cs_levels.get(ref) in ("project", "method") and ref not in used]
    if uncovered:
        print("subclauses of ISO/SAE 21434 and clauses of ISO 26262 at project level that no schema element supports (%d):"
              % len(uncovered))
        for ref in uncovered:
            print("  %s %s" % (ref, cybersecurity[ref]))
    for e in errors:
        print("error: " + e)
    print("%d errors" % len(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
