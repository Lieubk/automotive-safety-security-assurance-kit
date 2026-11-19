#!/usr/bin/env python3
"""Validate the Automotive SPICE process catalog and build its index.

The catalog is one YAML file per process under `aspice/<version>/processes/`.
It carries identifiers and structure (process, outcomes, base practices, output
work products, rating dependencies) plus this project's own paraphrased
descriptions. It does not carry the model's normative text.

Usage:
    python tools/catalog.py validate [--version 3.1]
    python tools/catalog.py index    [--version 3.1]    # rewrites index.yaml

For a version other than 3.1 (4.0, built from its draft), `maps_to` of each base practice
must name base practices of the 3.1 catalog: the toolkit's evidence structures carry them.

Requires PyYAML. Exit code 0 = valid, 1 = errors.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCOPES = {"vda", "extended", "other"}
KINDS = {"rule", "recommendation"}
WP_ID = re.compile(r"^\d{2}-\d{2}$")
RULE_ID = re.compile(r"^[A-Z0-9]+(\.[A-Z0-9]+)*\.(RL|RC)\.\d+$")
# "other-processes" is the one non-specific endpoint the rating-consistency material uses.
PRACTICE_REF = re.compile(r"^(?:([A-Z]{3}\.\d+)\.BP\d+|GP \d\.\d\.\d+|PA \d\.\d|[A-Z]{3}\.\d+|other-processes)$")


def load(version):
    folder = ROOT / "aspice" / version / "processes"
    procs = {}
    for f in sorted(folder.glob("*.yaml")):
        procs[f.stem] = yaml.safe_load(f.read_text(encoding="utf-8"))
    return folder, procs


def check_process(pid, p, all_bps, errors, warnings):
    def err(msg):
        errors.append("%s: %s" % (pid, msg))

    if not isinstance(p, dict):
        return err("file is not a mapping")
    for key in ("id", "name", "group", "scope", "purpose", "outcomes", "base_practices", "output_work_products"):
        if not p.get(key):
            err("missing or empty '%s'" % key)
    if errors and errors[-1].startswith(pid + ": missing"):
        return
    if p["id"] != pid:
        err("id '%s' does not match file name" % p["id"])
    if not pid.startswith(str(p["group"]) + "."):
        err("group '%s' does not match id" % p["group"])
    if p["scope"] not in SCOPES:
        err("scope '%s' not in %s" % (p["scope"], sorted(SCOPES)))
    if len(str(p["name"]).split()) > 12:
        err("name is longer than an identifier should be")

    numbers = [o.get("n") for o in p["outcomes"]]
    if numbers != list(range(1, len(numbers) + 1)):
        err("outcome numbers are not 1..N in order: %s" % numbers)
    if any(not o.get("text") for o in p["outcomes"]):
        err("an outcome has no text")
    valid = set(numbers)

    covered = set()
    for i, bp in enumerate(p["base_practices"], 1):
        bid = bp.get("id", "?")
        if bid != "%s.BP%d" % (pid, i):
            err("base practice %d has id '%s', expected %s.BP%d" % (i, bid, pid, i))
        for key in ("name", "intent", "outcomes", "evidence"):
            if not bp.get(key):
                err("%s: missing or empty '%s'" % (bid, key))
        bad = set(bp.get("outcomes") or []) - valid
        if bad:
            err("%s: unknown outcomes %s" % (bid, sorted(bad)))
        covered |= set(bp.get("outcomes") or [])
        for rid in bp.get("rule_ids") or []:
            if not RULE_ID.match(str(rid)):
                err("%s: malformed rule id '%s'" % (bid, rid))
        if len(str(bp.get("intent", "")).split()) > 45:
            warnings.append("%s: intent is longer than 45 words" % bid)
    if valid - covered:
        warnings.append("%s: outcomes without a base practice: %s" % (pid, sorted(valid - covered)))

    seen = set()
    for wp in p["output_work_products"]:
        wid = str(wp.get("id", "?"))
        if not WP_ID.match(wid):
            err("work product id '%s' is not NN-NN" % wid)
        if wid in seen:
            err("work product %s listed twice" % wid)
        seen.add(wid)
        if not wp.get("name"):
            err("work product %s has no name" % wid)
        if not wp.get("outcomes") and not p.get("outcomes_unmapped"):
            warnings.append("%s: work product %s has no outcome mapping" % (pid, wid))
        bad = set(wp.get("outcomes") or []) - valid
        if bad:
            err("work product %s: unknown outcomes %s" % (wid, sorted(bad)))

    for dep in p.get("depends_on") or []:
        if dep.get("kind") not in KINDS:
            err("dependency %s -> %s: kind must be one of %s" % (dep.get("from"), dep.get("to"), sorted(KINDS)))
        for end in ("from", "to"):
            ref = str(dep.get(end, ""))
            m = PRACTICE_REF.match(ref)
            if not m:
                err("dependency endpoint '%s' is not a practice, attribute or process id" % ref)
            elif m.group(1) and m.group(1) in all_bps and ref not in all_bps[m.group(1)]:
                err("dependency endpoint '%s' does not exist" % ref)
            elif m.group(1) and m.group(1) not in all_bps:
                warnings.append("%s: dependency endpoint %s is outside the catalog" % (pid, ref))


def build_index(version, procs):
    return {
        "version": version,
        "processes": [
            {
                "id": pid,
                "name": p["name"],
                "group": p["group"],
                "scope": p["scope"],
                "base_practices": len(p["base_practices"]),
                "file": "processes/%s.yaml" % pid,
            }
            for pid, p in sorted(procs.items(), key=lambda kv: (kv[1]["group"], int(kv[0].split(".")[1])))
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["validate", "index"])
    ap.add_argument("--version", default="3.1")
    args = ap.parse_args()

    folder, procs = load(args.version)
    if not procs:
        print("no process files under %s" % folder)
        return 1
    all_bps = {pid: {bp.get("id") for bp in (p or {}).get("base_practices") or []} for pid, p in procs.items()}
    errors, warnings = [], []
    for pid, p in procs.items():
        check_process(pid, p, all_bps, errors, warnings)
    if args.version != "3.1":                   # a later model is evidenced through the 3.1 practices it maps to
        _, base = load("3.1")
        known = {bp.get("id") for q in base.values() for bp in (q or {}).get("base_practices") or []}
        for pid, p in procs.items():
            for bp in (p or {}).get("base_practices") or []:
                bad = [m for m in bp.get("maps_to") or [] if m not in known]
                if bad:
                    errors.append("%s: %s maps to %s, not a base practice of 3.1" % (pid, bp.get("id"), ", ".join(bad)))

    index_path = folder.parent / "index.yaml"
    if not errors:
        wanted = yaml.safe_dump(build_index(args.version, procs), sort_keys=False, allow_unicode=True)
        if args.command == "index":
            index_path.write_text(wanted, encoding="utf-8", newline="\n")
            print("wrote %s" % index_path.relative_to(ROOT))
        elif not index_path.exists() or index_path.read_text(encoding="utf-8") != wanted:
            errors.append("index.yaml is missing or stale: run 'python tools/catalog.py index'")

    for w in warnings:
        print("warning: " + w)
    for e in errors:
        print("error: " + e)
    print("%d processes | %d errors | %d warnings" % (len(procs), len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
