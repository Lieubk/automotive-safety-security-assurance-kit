#!/usr/bin/env python3
"""Create evidence records from tool output and recorded decisions.

Records are evidence: a test result nobody ran and a review nobody held do not
exist. These commands therefore take their content from a tool's result file,
or from what a named person decided, and compute everything that can be
computed (IDs, content hashes, references) instead of asking for it.

Commands
    next-id TYPE
        print the next free ID for an item type, for example `next-id review-record`

    test-run --level LEVEL --results FILE --item-under-test REF --environment NAME
        final test-run record from a results file (JSON):
        {"executed_at": "<ISO time>", "compiler": "...",            (compiler optional)
         "results": [{"test": "UT-0001", "verdict": "passed", "evidence": "<path>"}]}
        Every test named must be a test case of that level, and every approved
        test case of that level must appear; otherwise nothing is written.
        Evidence files are copied to verification/evidence/<record id>/.

    analysis-run --results FILE --item-under-test REF
        final static-analysis-run record from a results file (JSON):
        {"tool": "<name, version, rule set>", "executed_at": "<ISO time>",
         "files": ["src/a.c", ...],                       (every file that was analysed)
         "findings": [{"file": "src/a.c", "line": 12, "rule": "...", "severity": "...",
                       "message": "..."}],
         "evidence": "<path of the raw tool output>"}
        Findings are attributed to software units through `source_files`. A live
        unit none of whose C files was analysed stops the command.

    review --checklist NAME --reviewer NAME [--reviewer NAME ...] --verdict approved|rework
           [--findings FILE] ID [ID ...]
        final review record for the named items at their current content. The
        subject and the references (every upstream item the subject links to)
        are filled in with content hashes. FILE is JSON: a list of
        {"id", "item", "text", "severity": "major"|"minor", "state": "open"|"closed"}.
        The reviewer names are the people accountable for the verdict: pass what
        the user states, never an invented name.

Options
    --project DIR      project root (default: current directory)

Requires PyYAML.
"""
import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from traceability import TEST_TYPES, VERDICTS, Project  # noqa: E402


def next_id(project, type_name):
    prefix = project.types[type_name]["prefix"]
    numbers = [int(i.rsplit("-", 1)[1]) for i in project.items if i.rsplit("-", 1)[0] == prefix]
    return "%s-%04d" % (prefix, max(numbers, default=0) + 1)


def write_item(project, type_name, front):
    folder = project.root / project.types[type_name]["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (front["id"] + ".md")
    text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=120) + "---\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path.relative_to(project.root).as_posix()


def keep_evidence(project, record_id, path):
    """Copy a tool output file next to the records, so the evidence outlives the build folder."""
    source = project.root / str(path)
    if not path or not source.is_file():
        return path
    folder = project.root / "verification" / "evidence" / record_id
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, folder / source.name)
    return (folder / source.name).relative_to(project.root).as_posix()


def stop(problems):
    print("\n".join(problems))
    print("no record written")
    return 1


def cmd_next_id(project, args):
    if args.type not in project.types:
        return stop(["unknown type: %s" % args.type])
    print(next_id(project, args.type))
    return 0


def cmd_test_run(project, args):
    levels = {level: type_name for type_name, (_, level) in TEST_TYPES.items()}
    if args.level not in levels:
        return stop(["unknown level %s; one of %s" % (args.level, sorted(levels))])
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
    problems += ["approved test case %s has no result in the file" % c.id
                 for c in cases.values() if c.status == "approved" and c.id not in reported]
    if problems:
        return stop(problems)
    record_id = next_id(project, "test-run")
    for row in results:
        if row.get("evidence"):
            row["evidence"] = keep_evidence(project, record_id, row["evidence"])
    front = {
        "id": record_id,
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
    print("wrote %s: %s" % (path, ", ".join("%d %s" % (n, v) for v, n in counts.items() if n)))
    return 0


def cmd_analysis_run(project, args):
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    analysed = {Path(f).as_posix() for f in data.get("files", [])}
    owner, units = {}, [u for u in project.of_type("software-unit") if project.live(u)]
    for unit in units:
        for path in unit.front.get("source_files") or []:
            owner[Path(str(path)).as_posix()] = unit.id
    problems = ["analysed file %s belongs to no software unit" % f for f in sorted(analysed) if f not in owner]
    per_unit = defaultdict(lambda: defaultdict(int))
    for finding in data.get("findings", []):
        file = Path(str(finding.get("file"))).as_posix()
        if file not in owner:
            problems.append("finding in %s, which belongs to no software unit" % file)
        else:
            per_unit[owner[file]][str(finding.get("severity", "unclassified"))] += 1
    results = []
    for unit in sorted(units, key=lambda u: u.id):
        if unit.front.get("origin") in ("generated", "third-party"):
            continue
        sources = [Path(str(p)).as_posix() for p in unit.front.get("source_files") or [] if str(p).endswith(".c")]
        missing = [s for s in sources if s not in analysed]
        if missing or not sources:
            problems.append("%s: not analysed: %s" % (unit.id, ", ".join(missing) or "no C source file listed"))
            continue
        results.append({"unit": unit.id, "files": sources, "open_findings": dict(per_unit[unit.id]) or 0,
                        "evidence": data.get("evidence")})
    if problems:
        return stop(problems)
    record_id = next_id(project, "static-analysis-run")
    evidence = keep_evidence(project, record_id, data.get("evidence"))
    for row in results:
        row["evidence"] = evidence
    front = {
        "id": record_id,
        "type": "static-analysis-run",
        "status": "final",
        "item_under_test": args.item_under_test,
        "tool": data.get("tool"),
        "executed_at": data.get("executed_at"),
        "results": results,
    }
    path = write_item(project, "static-analysis-run", front)
    print("wrote %s: %d units, %d findings" % (path, len(results), len(data.get("findings", []))))
    return 0


def cmd_review(project, args):
    problems = ["no such item: %s" % i for i in args.ids if i not in project.items]
    findings = json.loads(Path(args.findings).read_text(encoding="utf-8")) if args.findings else []
    for finding in findings:
        if finding.get("state") not in ("open", "closed") or finding.get("severity") not in ("major", "minor"):
            problems.append("finding %s needs severity major|minor and state open|closed" % finding.get("id"))
    if args.verdict == "approved" and any(f.get("state") == "open" for f in findings):
        problems.append("verdict approved is not possible while a finding is open")
    if problems:
        return stop(problems)
    references = {}
    for item_id in args.ids:
        item = project.items[item_id]
        for role in (item.front.get("links") or {}):
            for target, _ in item.targets(role):
                if target in project.items and target not in args.ids:
                    references[target] = project.items[target].hash
    front = {
        "id": next_id(project, "review-record"),
        "type": "review-record",
        "status": "final",
        "checklist": args.checklist,
        "reviewers": args.reviewer,
        "verdict": args.verdict,
        "subject": [{"item": i, "hash": project.items[i].hash} for i in args.ids],
        "references": [{"item": i, "hash": h} for i, h in sorted(references.items())],
        "findings": findings,
    }
    path = write_item(project, "review-record", front)
    print("wrote %s: %s, %d items, %d references, %d findings"
          % (path, args.verdict, len(args.ids), len(references), len(findings)))
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
    analysis = sub.add_parser("analysis-run")
    analysis.add_argument("--results", required=True)
    analysis.add_argument("--item-under-test", required=True)
    review = sub.add_parser("review")
    review.add_argument("--checklist", required=True)
    review.add_argument("--reviewer", required=True, action="append")
    review.add_argument("--verdict", required=True, choices=["approved", "rework"])
    review.add_argument("--findings")
    review.add_argument("ids", nargs="+")
    args = ap.parse_args()
    project = Project(args.project)
    commands = {"next-id": cmd_next_id, "test-run": cmd_test_run, "analysis-run": cmd_analysis_run, "review": cmd_review}
    return commands[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
