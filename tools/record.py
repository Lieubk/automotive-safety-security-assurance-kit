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
             [--deviation UNIT=TEXT ...]
        final test-run record from a results file (JSON):
        {"executed_at": "<ISO time>", "compiler": "...",            (compiler optional)
         "results": [{"test": "UT-0001", "verdict": "passed", "evidence": "<path>"}],
         "coverage": [{"file": "src/a.c", "statement_percent": 100.0, "branch_percent": 97.5}]}
        `coverage` is optional: a list per source file (attributed to the owning
        unit; every key ending in `_percent` is kept), or a text saying why it
        was not measured. --deviation records, for one unit, the reason a person
        accepted a coverage figure below target: pass what that person states.
        The record also stores a hash of every unit source and test file, so a
        change of the code after the run can be seen.
        Every test named must be a test case of that level, and every approved
        test case of that level must appear; otherwise nothing is written.
        Evidence files are copied to verification/evidence/<record id>/.

    analysis-run --results FILE --item-under-test REF
        final static-analysis-run record from a results file (JSON):
        {"tool": "<name, version, rule set>", "executed_at": "<ISO time>",
         "files": ["src/a.c", ...],                       (every file that was analysed)
         "findings": [{"file": "src/a.c", "line": 12, "rule": "...", "severity": "...",
                       "message": "..."}],
         "deviations": [{"file", "line", "rule", "justification", "accepted_by"}],   (optional)
         "metrics": [{"file", "name", "value"}],                                    (optional)
         "evidence": "<path of the raw tool output>"}
        A finding matched by a deviation (same file, rule and line) is recorded
        as justified, not as open; a deviation that matches nothing stops the
        command.
        Findings are attributed to software units through `source_files`. A live
        unit none of whose C files was analysed stops the command.

    review --checklist "NAME vN" --reviewer NAME [--reviewer NAME ...] --verdict approved|rework
           [--findings FILE] [--checks FILE] [--item-under-test REF] [--external-criteria] ID [ID ...]
        final review record for the named items at their current content. The
        subject and the references (every upstream item the subject links to)
        are filled in with content hashes. With --item-under-test the review
        counts as a review of the code as well: for software units the hashes
        of their source files are stored, so the record says which code was
        reviewed. Without it the record covers the design only, and the trace
        check keeps asking for a review of the code. Findings FILE is JSON: a list of
        {"id", "item", "text", "severity": "major"|"minor", "state": "open"|"closed",
         "closes": "<REV-ID>#<finding id>"}    (closes is optional)
        Checks FILE is JSON: a list of
        {"check", "result": "pass"|"finding"|"not-applicable"|"not-assessed", "note"}.
        The checklist is cited as "<name> v<N>", <name> being a file under
        .claude/docs/checklists (without .md) or its title without the word
        "checklist"; the version must be the one in the file. Criteria from
        outside the toolkit are recorded with --external-criteria.
        Verdict approved is refused while a finding is open; while a check of
        the checklist has no result or is not assessed; while an item the
        subject links to is still in draft or in review; and while an open
        finding of an earlier review of the same content is not closed by an
        entry with `closes`.
        The reviewer names are the people accountable for the verdict: pass what
        the user states, never an invented name.

    baseline --tag TAG --purpose TEXT
        final baseline record: the approved plans and engineering items with
        content hash and status (for an internal purpose: all of them, whatever
        their state). Change requests, problem reports and records are not part
        of a baseline. Refused while the trace check reports errors, unless the
        purpose is one of `trace.internal_baselines` of project.yaml. The version
        control tag itself is set by whoever runs the command, after the record
        is committed.

    communication --subject ID [--subject ID ...] --audience WHO [--audience WHO ...]
                  --channel TEXT [--agreement TEXT] [--sent-at DATE]
        final communication record: what was made known to whom and how, and,
        with --agreement, what was agreed. Pass what the user states happened.

Options
    --project DIR      project root (default: current directory)

Requires PyYAML.
"""
import argparse
import datetime
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from traceability import TEST_TYPES, VERDICTS, Project, file_hash  # noqa: E402


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


def source_hashes(project, files):
    """[{file, hash}] for the given repository paths that exist, so a later change of the code can be seen."""
    out = []
    for name in sorted({Path(str(f)).as_posix() for f in files}):
        if (project.root / name).is_file():
            out.append({"file": name, "hash": file_hash(project.root / name)})
    return out


def unit_sources(project):
    return [f for u in project.of_type("software-unit") if project.live(u) for f in u.front.get("source_files") or []]


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
    coverage = data.get("coverage")
    if isinstance(coverage, list):
        owner = {Path(str(f)).as_posix(): u.id for u in project.of_type("software-unit")
                 for f in u.front.get("source_files") or []}
        unowned = [c.get("file") for c in coverage if Path(str(c.get("file"))).as_posix() not in owner]
        if unowned:
            return stop(["coverage reported for %s, which belongs to no software unit" % f for f in unowned])
        kept = []
        for c in coverage:
            entry = {"unit": owner[Path(str(c["file"])).as_posix()], "file": c["file"]}
            entry.update({k: v for k, v in c.items() if k.endswith("_percent") or k == "deviation"})
            kept.append(entry)
        coverage = kept
    deviations = dict(d.split("=", 1) for d in args.deviation or [] if "=" in d)
    if deviations:
        by_unit = {c["unit"]: c for c in coverage} if isinstance(coverage, list) else {}
        missing = sorted(set(deviations) - set(by_unit))
        if missing or len(deviations) != len(args.deviation):
            return stop(["--deviation needs UNIT=TEXT for a unit that has a coverage entry; no entry for: %s"
                         % (", ".join(missing) or "(malformed argument)")])
        for unit_id, text in deviations.items():
            by_unit[unit_id]["deviation"] = text
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
    if coverage:
        front["coverage"] = coverage       # a list per unit, or the reason it was not measured
    scripts = [str(cases[r["test"]].front.get("script") or "").partition("::")[0] for r in results]
    front["sources"] = source_hashes(project, unit_sources(project) + [s for s in scripts if s])
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
    justified = defaultdict(list)

    def key(entry):
        return Path(str(entry.get("file"))).as_posix(), str(entry.get("rule")), str(entry.get("line"))

    accepted = {key(d): d for d in data.get("deviations", [])}
    for d in data.get("deviations", []):
        if not d.get("justification") or not d.get("accepted_by"):
            problems.append("deviation for %s %s needs a justification and who accepted it" % (d.get("file"), d.get("rule")))
    matched = set()
    for finding in data.get("findings", []):
        file = Path(str(finding.get("file"))).as_posix()
        if file not in owner:
            problems.append("finding in %s, which belongs to no software unit" % file)
        elif key(finding) in accepted:
            matched.add(key(finding))
            justified[owner[file]].append(accepted[key(finding)])
        else:
            per_unit[owner[file]][str(finding.get("severity", "unclassified"))] += 1
    problems += ["deviation for %s rule %s line %s matches no finding of this run" % k
                 for k in sorted(set(accepted) - matched)]
    metrics = defaultdict(list)
    for metric in data.get("metrics", []):
        file = Path(str(metric.get("file"))).as_posix()
        if file in owner:
            metrics[owner[file]].append({k: v for k, v in metric.items() if k != "file"})
    results = []
    for unit in sorted(units, key=lambda u: u.id):
        if unit.front.get("origin") in ("generated", "third-party"):
            continue
        sources = [Path(str(p)).as_posix() for p in unit.front.get("source_files") or [] if str(p).endswith(".c")]
        missing = [s for s in sources if s not in analysed]
        if missing or not sources:
            problems.append("%s: not analysed: %s" % (unit.id, ", ".join(missing) or "no C source file listed"))
            continue
        row = {"unit": unit.id, "files": sources, "open_findings": dict(per_unit[unit.id]) or 0}
        if justified[unit.id]:
            row["deviations"] = justified[unit.id]
        if metrics[unit.id]:
            row["metrics"] = metrics[unit.id]
        row["evidence"] = data.get("evidence")
        results.append(row)
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
        "sources": source_hashes(project, unit_sources(project)),
    }
    path = write_item(project, "static-analysis-run", front)
    print("wrote %s: %d units, %d findings" % (path, len(results), len(data.get("findings", []))))
    return 0


CHECKLISTS = Path(__file__).resolve().parent.parent / ".claude" / "docs" / "checklists"
RESULTS = ("pass", "finding", "not-applicable", "not-assessed")


def plain(text):
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def find_checklist(citation):
    """(file name, version, check IDs) of the toolkit checklist that '<name> v<N>' cites, or None.

    <name> is the file name without extension or the title without the word "checklist";
    spaces and hyphens are interchangeable.
    """
    cited = re.match(r"^(.*?)\s+v(\d+)$", str(citation).strip(), re.I)
    if not cited:
        return None
    for path in sorted(CHECKLISTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.M)
        names = {plain(path.stem)}
        if title:
            names.add(plain(re.sub(r"(?i)\bchecklist\b", " ", title.group(1))))
        if plain(cited.group(1)) in names:
            version = re.search(r"^Version (\d+)", text, re.M)
            return path.name, version.group(1) if version else None, re.findall(r"(?m)^\|\s*([A-Z]{2,5}-\d+)\s*\|", text), cited.group(2)
    return None


def cmd_review(project, args):
    problems = ["no such item: %s" % i for i in args.ids if i not in project.items]
    findings = json.loads(Path(args.findings).read_text(encoding="utf-8")) if args.findings else []
    for finding in findings:
        if finding.get("state") not in ("open", "closed") or finding.get("severity") not in ("major", "minor"):
            problems.append("finding %s needs severity major|minor and state open|closed" % finding.get("id"))
    if args.verdict == "approved" and any(f.get("state") == "open" for f in findings):
        problems.append("verdict approved is not possible while a finding is open")
    checks = json.loads(Path(args.checks).read_text(encoding="utf-8")) if args.checks else []
    for entry in checks:
        if entry.get("result") not in RESULTS:
            problems.append("check %s needs result %s" % (entry.get("check"), "|".join(RESULTS)))
        elif entry["result"] == "not-applicable" and not entry.get("note"):
            problems.append("check %s is not-applicable: the note must say why" % entry.get("check"))
    listed = None if args.external_criteria else find_checklist(args.checklist)
    if listed is None and not args.external_criteria:
        problems.append("'%s' cites no checklist of this toolkit: expected '<name> v<N>' for a file under "
                        ".claude/docs/checklists. For criteria from outside the toolkit pass --external-criteria."
                        % args.checklist)
    elif listed:
        file_name, version, known, cited_version = listed
        if version != cited_version:
            problems.append("%s is at version %s, the citation says v%s" % (file_name, version, cited_version))
        given = [str(c.get("check")) for c in checks]
        problems += ["check %s is not in %s" % (c, file_name) for c in given if c not in known]
        if args.verdict == "approved":
            missing = [c for c in known if c not in given]
            if missing:
                problems.append("verdict approved needs a result for every check of %s (--checks); none for: %s"
                                % (file_name, ", ".join(missing)))
    if args.verdict == "approved" and not any("no such item" in p for p in problems):
        for item_id in args.ids:
            item = project.items[item_id]
            for role in (item.front.get("links") or {}):
                for target_id, _ in item.targets(role):
                    target = project.items.get(target_id)
                    if target is not None and target_id not in args.ids and project.live(target) \
                            and project.types[target.type]["lifecycle"] == "engineering" and target.status != "approved":
                        problems.append("%s cannot be approved while %s (%s) is in state %s"
                                        % (item_id, target_id, role, target.status))
    unassessed = [str(c.get("check")) for c in checks if c.get("result") == "not-assessed"]
    if args.verdict == "approved" and unassessed:
        problems.append("verdict approved is not possible while checks are not assessed: %s" % ", ".join(unassessed))
    if args.verdict == "approved" and not problems:
        closing = {str(f.get("closes")) for f in findings if f.get("closes") and f.get("state") == "closed"}
        for item_id in args.ids:
            for earlier in project.reviews_of(project.items[item_id]):
                for finding in earlier.front.get("findings") or []:
                    ref = "%s#%s" % (earlier.id, finding.get("id"))
                    if finding.get("state") == "open" and finding.get("item") in (None, item_id) and ref not in closing:
                        problems.append("%s: finding %s of an earlier review of the same content is open; close it "
                                        "with a finding entry that has \"closes\": \"%s\"" % (item_id, ref, ref))
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
        "checklist_source": "external" if args.external_criteria else "toolkit",
        "reviewers": args.reviewer,
        "verdict": args.verdict,
        "reviewed_at": datetime.date.today().isoformat(),
        "subject": [{"item": i, "hash": project.items[i].hash} for i in args.ids],
        "references": [{"item": i, "hash": h} for i, h in sorted(references.items())],
        "findings": findings,
    }
    if checks:
        front["checks"] = checks
    if args.item_under_test:
        front["item_under_test"] = args.item_under_test
    code = [f for i in args.ids if project.items[i].type == "software-unit"
            for f in project.items[i].front.get("source_files") or []]
    if code and args.item_under_test:      # naming the code revision is what makes it a review of the code
        front["sources"] = source_hashes(project, code)
    path = write_item(project, "review-record", front)
    print("wrote %s: %s, %d items, %d references, %d findings"
          % (path, args.verdict, len(args.ids), len(references), len(findings)))
    return 0


def cmd_baseline(project, args):
    internal = (project.config.get("trace") or {}).get("internal_baselines") or []
    errors = [f for f in project.check() if f["level"] == "error"]
    if errors and args.purpose not in internal:
        return stop(["the trace check reports %d errors; a baseline with purpose '%s' needs none"
                     % (len(errors), args.purpose)]
                    + ["  %s %s %s" % (f["rule"], f["item"], f["message"]) for f in errors[:10]])
    engineering = [i for i in project.items.values()
                   if project.types[i.type]["lifecycle"] == "engineering" and project.live(i)]
    # an internal baseline is a snapshot of everything; any other holds what is approved
    members = engineering if args.purpose in internal else [i for i in engineering if i.status == "approved"]
    left_out = len(engineering) - len(members)
    front = {
        "id": next_id(project, "baseline"),
        "type": "baseline",
        "status": "final",
        "tag": args.tag,
        "purpose": args.purpose,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "items": [{"item": i.id, "hash": i.hash, "status": i.status} for i in sorted(members, key=lambda i: i.id)],
    }
    path = write_item(project, "baseline", front)
    print("wrote %s: %d items, purpose %s, tag %s (set the tag after committing the record)"
          % (path, len(members), args.purpose, args.tag))
    if left_out:
        print("not in the baseline: %d items that are not approved (python tools/traceability.py list --status draft)" % left_out)
    return 0


def cmd_communication(project, args):
    problems = ["no such item: %s" % s for s in args.subject if s not in project.items]
    if args.sent_at:
        try:
            datetime.date.fromisoformat(args.sent_at)
        except ValueError:
            problems.append("--sent-at must be a date as YYYY-MM-DD, got %r" % args.sent_at)
    if problems:
        return stop(problems)
    front = {
        "id": next_id(project, "communication-record"),
        "type": "communication-record",
        "status": "final",
        "subject": args.subject if len(args.subject) > 1 else args.subject[0],
        "audience": args.audience,
        "channel": args.channel,
        "sent_at": args.sent_at or datetime.date.today().isoformat(),
    }
    if args.agreement:
        front["agreement"] = args.agreement
    path = write_item(project, "communication-record", front)
    print("wrote %s: %s to %s" % (path, ", ".join(args.subject), ", ".join(args.audience)))
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
    run.add_argument("--deviation", action="append", metavar="UNIT=TEXT")
    analysis = sub.add_parser("analysis-run")
    analysis.add_argument("--results", required=True)
    analysis.add_argument("--item-under-test", required=True)
    review = sub.add_parser("review")
    review.add_argument("--checklist", required=True)
    review.add_argument("--reviewer", required=True, action="append")
    review.add_argument("--verdict", required=True, choices=["approved", "rework"])
    review.add_argument("--findings")
    review.add_argument("--checks")
    review.add_argument("--item-under-test")
    review.add_argument("--external-criteria", action="store_true",
                        help="the review used criteria from outside the toolkit, named under --checklist")
    review.add_argument("ids", nargs="+")
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--tag", required=True)
    baseline.add_argument("--purpose", required=True)
    told = sub.add_parser("communication")
    told.add_argument("--subject", required=True, action="append")
    told.add_argument("--audience", required=True, action="append")
    told.add_argument("--channel", required=True)
    told.add_argument("--agreement")
    told.add_argument("--sent-at", help="date it was sent, when not today")
    args = ap.parse_args()
    project = Project(args.project)
    commands = {"next-id": cmd_next_id, "test-run": cmd_test_run, "analysis-run": cmd_analysis_run,
                "review": cmd_review, "baseline": cmd_baseline, "communication": cmd_communication}
    return commands[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
