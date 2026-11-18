#!/usr/bin/env python3
"""Create evidence records from tool output, so that nobody types results by hand.

Commands
    next-id TYPE
        print the next free ID for an item type, for example `next-id review-record`

    test-run --level LEVEL --results FILE --item-under-test REF --environment NAME
        write a final test-run record from a results file. The file is JSON:
        {"executed_at": "<ISO time>", "compiler": "...",            (compiler optional)
         "results": [{"test": "UT-0001", "verdict": "passed", "evidence": "<path>"}]}
        Every test named must exist as a test case item of that level, and every
        approved test case of that level must appear, otherwise nothing is written.

Options
    --project DIR      project root (default: current directory)

Requires PyYAML.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from traceability import TEST_TYPES, VERDICTS, Project  # noqa: E402


def next_id(project, type_name):
    prefix = project.types[type_name]["prefix"]
    numbers = [int(i.rsplit("-", 1)[1]) for i in project.items if i.rsplit("-", 1)[0] == prefix]
    return "%s-%04d" % (prefix, max(numbers, default=0) + 1)


def write_item(project, type_name, front, body=""):
    folder = project.root / project.types[type_name]["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (front["id"] + ".md")
    text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=120) + "---\n" + body
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def cmd_next_id(project, args):
    if args.type not in project.types:
        print("unknown type: %s" % args.type)
        return 1
    print(next_id(project, args.type))
    return 0


def cmd_test_run(project, args):
    levels = {level: type_name for type_name, (_, level) in TEST_TYPES.items()}
    if args.level not in levels:
        print("unknown level %s; one of %s" % (args.level, sorted(levels)))
        return 1
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    cases = {i.id: i for i in project.of_type(levels[args.level])}
    problems, results = [], []
    for entry in data.get("results", []):
        test, verdict = entry.get("test"), entry.get("verdict")
        if test not in cases:
            problems.append("%s is not a %s item" % (test, levels[args.level]))
        elif verdict not in VERDICTS:
            problems.append("%s has verdict %r; one of %s" % (test, verdict, sorted(VERDICTS)))
        else:
            row = {"test": test, "verdict": verdict}
            row.update({k: entry[k] for k in ("evidence", "reason") if entry.get(k)})
            results.append(row)
    reported = {r["test"] for r in results}
    for case in cases.values():
        if case.status == "approved" and case.id not in reported:
            problems.append("approved test case %s has no result in the file" % case.id)
    if problems:
        print("\n".join(problems))
        print("no record written")
        return 1
    front = {
        "id": next_id(project, "test-run"),
        "type": "test-run",
        "status": "final",
        "level": args.level,
        "item_under_test": args.item_under_test,
        "environment": args.environment + (" (%s)" % data["compiler"] if data.get("compiler") else ""),
        "executed_at": data.get("executed_at"),
        "results": sorted(results, key=lambda r: r["test"]),
    }
    path = write_item(project, "test-run", front)
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in sorted(VERDICTS)}
    print("wrote %s: %s" % (path.relative_to(project.root).as_posix(),
                            ", ".join("%d %s" % (n, v) for v, n in counts.items() if n)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("next-id").add_argument("type")
    run = sub.add_parser("test-run")
    run.add_argument("--level", required=True)
    run.add_argument("--results", required=True)
    run.add_argument("--item-under-test", required=True)
    run.add_argument("--environment", required=True)
    args = ap.parse_args()
    project = Project(args.project)
    return {"next-id": cmd_next_id, "test-run": cmd_test_run}[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
