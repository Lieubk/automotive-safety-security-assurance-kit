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
             [--deviation UNIT=TEXT ...] [--build BLD-ID] [--selection TEXT] [--executed-at TIME]
        final test-run record from a results file (JSON):
        {"executed_at": "<ISO time>", "compiler": "...",            (compiler optional)
         "results": [{"test": "UT-0001", "verdict": "passed", "evidence": "<path>",
                      "reason": "<why not-run or blocked>"}],
         "coverage": [{"file": "src/a.c", "statement_percent": 100.0, "branch_percent": 97.5}]}
        or from a JUnit XML report (a file ending in .xml), as test benches write
        them: a <testcase> is matched to a test case by the ID in its name or
        class name; <failure> and <error> give failed, <skipped> not-run with its
        message as the reason; the report itself is kept as evidence.
        `coverage` is optional: a list per source file (attributed to the owning
        unit; every key ending in `_percent` is kept), or a text saying why it
        was not measured. --deviation records, for one unit, the reason a person
        accepted a coverage figure below target: pass what that person states.
        The record also stores a hash of every unit source and test file, so a
        change of the code after the run can be seen.
        Every test named must be a test case of that level, and every approved
        test case of that level must appear; otherwise nothing is written.
        --build names the build record of the integrated software that was
        tested; it must be final, have succeeded and be built from the item under
        test. A software-integration run needs it: then the approved test cases
        of the build's step must appear, cases of earlier steps may appear as
        regression, and cases of later steps may not. A software-qualification
        run needs a build of the last step once an approved software-integration
        plan exists. --selection says how the cases were chosen (all, the
        regression set, the impact of a change), in the strategy's terms.
        Evidence files are copied to verification/evidence/<record id>/.

    build --step NAME --manifest FILE --item-under-test REF
        final build record of one step of the approved software-integration plan,
        from the manifest (JSON) the project's build writes:
        {"executed_at": "<ISO time>", "tool": "<build tool and compiler, versions>",
         "result": "succeeded" | "failed",
         "files": ["src/a.c", ...],                     (project sources built)
         "delivered": [{"component": "CMP-0005", "version": "...", "files": [...]}],
                                                        (optional: integrated as received)
         "doubles": [{"component": "CMP-0006", "file": "tests/x/double.c"}],
                                                        (optional: stand-ins)
         "evidence": "<path of the build log>"}
        Every built file must belong to a live software unit (or match the
        generated or third-party patterns of project.yaml); the units are grouped
        by their component. The record stores a hash of every file built, so a
        change after the build can be seen. A failed build is recorded as well.

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
    review --reconfirm --reviewer NAME [--reviewer NAME ...] --verdict approved|rework
           [--findings FILE] ID [ID ...]
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
        A whole section of the checklist that does not concern the subjects is
        one entry {"section": "<heading>", "result": "not-applicable", "note"};
        it stands for every check of that section the file does not list.
        A finding names an item that is a subject of the review, or none for a
        finding on the set.
        The checklist is cited as "<name> v<N>", <name> being a file under
        .claude/docs/checklists (without .md) or its title without the word
        "checklist"; the version must be the one in the file. Criteria from
        outside the toolkit are recorded with --external-criteria.
        Verdict approved is refused while a finding is open; while a check of
        the checklist has no result or is not assessed; while an item the
        subject links to is still in draft or in review; while an accountable
        check is answered with a finding (what a person states is missing cannot
        be closed by decision); and while an open finding of an earlier review of
        the same content is not closed by an entry with `closes`.
        --reconfirm is for items that have NOT changed but build on something
        that has (the trace check reports SUSPECT): the reviewers compared them
        with the new versions and confirm them. It needs no checklist results,
        is refused for an item whose own content has no approving review, records
        the new versions as references, and carries the code review of a unit over
        as it was recorded: code that changed since then stays reported as changed.
        It cannot be combined with --item-under-test or --external-criteria: a
        review of code is a review against the code checklist.
        The reviewer names are the people accountable for the verdict: pass what
        the user states, never an invented name.

    quality-check --kind work-product|process [--check NAME] --subject ID [--subject ID ...]
                  --criteria TEXT --checked-by NAME --result conforms|conforms-with-findings|does-not-conform
                  --summary FILE [--findings FILE] [--checked-at DATE]
        final quality record of a check by quality assurance. The tool adds the
        facts at the time: per item its state, hash and approving review with its
        reviewers and checklist; per process the evidence per base practice of
        `practices`. The verdict and the summary are the checker's. Findings FILE
        is JSON: [{"id", "text", "action": "<CA-ID or PRB-ID>", "severity"}]; the
        action has to exist. Refused without an approved quality-assurance plan,
        for a --check the plan does not have, for result conforms with findings,
        and for any other result without one.

    quality-report --checked-by NAME --result R --summary FILE [--as-of DATE] [--period TEXT]
        final quality record of kind summary: the quality records since the last
        report as subject, the figures of `traceability.py quality` as facts - the
        findings of the checks with the state of their actions among them - and the
        reading of quality assurance from the file. It raises no findings of its own. It is communicated with
        `communication --subject <QAR-ID> --practice SUP.1.BP4` (COV-45).

    self-assessment --ratings FILE --assessor NAME [--assessor NAME ...] [--process ID ...]
                    --summary FILE [--as-of DATE] [--check-only]
        final self-assessment record: the ratings N, P, L, F that the named
        assessors gave per base practice (FILE is JSON {"practices": [{"practice",
        "rating", "note"}], "attributes": [{"process", "attribute", "rating",
        "note"}]}), the state of each practice in `practices` at the time, and
        the consistency flags: a rating outside the band of what the toolkit
        observes, and a rating above that of a practice it depends on in the
        catalog. A flag from an observation or from a rule of the catalog needs
        the reason in the note of the rating; a flag from a recommendation is
        recorded. Every base practice of the processes needs a rating. The
        processes are --process, else assessment_scope, else the scope.
        --check-only lists the gaps and flags and writes nothing. The toolkit
        rates nothing: the ratings are the assessors'.

    problem-trends --reported-by NAME --assessment FILE [--as-of DATE] [--period TEXT]
        final problem trend report: every problem report known on the date with
        its state, severity, origin, detection and age, and the counts by state,
        severity, origin, detection and age (the figures of `traceability.py
        problems`), with the analyst's assessment from the file, in their words.
        Refused without an assessment.

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
import fnmatch
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import traceability as trace  # noqa: E402
from traceability import TEST_TYPES, VERDICTS, Project, file_hash  # noqa: E402


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


TEST_ID = re.compile(r"\b([A-Z]+-\d{4,})\b")


def junit_results(project, path):
    """The results of a JUnit XML report (as most test benches write one) in the form of a results file.
    A test case is recognised by its ID in the name or class name of the <testcase>."""
    import xml.etree.ElementTree as ElementTree
    root = ElementTree.parse(str(path)).getroot()
    suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
    try:
        evidence = path.resolve().relative_to(project.root).as_posix()
    except ValueError:
        evidence = str(path.resolve())
    results, stamps = [], []
    for suite in suites:
        if suite.get("timestamp"):
            stamps.append(suite.get("timestamp"))
        for case in suite.iter("testcase"):
            names = " ".join(filter(None, (case.get("name"), case.get("classname"))))
            ids = TEST_ID.findall(names)
            row = {"test": ids[0] if ids else names, "verdict": "passed", "evidence": evidence}
            failed = case.find("failure") if case.find("failure") is not None else case.find("error")
            skipped = case.find("skipped")
            if failed is not None:
                row["verdict"] = "failed"
            elif skipped is not None:
                row["verdict"] = "not-run"
                reason = (skipped.get("message") or skipped.text or "").strip()
                if reason:
                    row["reason"] = reason
            results.append(row)
    return {"executed_at": min(stamps) if stamps else None, "results": results}


def cmd_test_run(project, args):
    levels = {level: type_name for type_name, (_, level) in TEST_TYPES.items()}
    if args.level not in levels:
        return stop(["unknown level %s; one of %s" % (args.level, sorted(levels))])
    source = Path(args.results)
    data = junit_results(project, source) if source.suffix.lower() == ".xml" \
        else json.loads(source.read_text(encoding="utf-8"))
    if args.executed_at:
        data["executed_at"] = args.executed_at
    if not data.get("executed_at"):
        return stop(["the results give no time of execution; pass the time the tests ran with --executed-at"])
    cases = {i.id: i for i in project.of_type(levels[args.level])}
    build, required, allowed = None, (lambda case: True), (lambda case: True)
    steps = [str(s.get("name")) for s in project.integration_steps()]
    if args.build:
        build = project.items.get(args.build)
        if build is None or build.type != "build-record" or build.status != "final":
            return stop(["%s is not a final build record" % args.build])
        if build.front.get("result") != "succeeded":
            return stop(["%s records a build that failed: nothing can have been tested on it" % build.id])
        if str(build.front.get("item_under_test")) != args.item_under_test:
            return stop(["%s was built from %s, not from %s" % (build.id, build.front.get("item_under_test"),
                                                                 args.item_under_test)])
        step = str(build.front.get("step"))
        if step not in steps:
            return stop(["%s carries out step '%s', which the approved software-integration plan does not have"
                         % (build.id, step)])
        if args.level == "software-integration":
            done = steps[:steps.index(step) + 1]
            required = lambda case: str(case.front.get("step")) == step               # noqa: E731
            allowed = lambda case: str(case.front.get("step")) in done                # noqa: E731
        elif args.level == "software-qualification" and step != steps[-1]:
            return stop(["%s is a build of step '%s'; the software is qualified on a build of the last step '%s'"
                         % (build.id, step, steps[-1])])
    elif args.level == "software-integration":
        return stop(["a software integration run needs --build: the build record of the integration step tested"])
    elif args.level == "software-qualification" and steps:
        return stop(["the project has an approved software-integration plan: name the build of its last step "
                     "that was tested with --build"])
    problems, results = [], []
    for entry in data.get("results", []):
        test, verdict = entry.get("test"), entry.get("verdict")
        if test not in cases:
            problems.append("%s is not a %s item" % (test, levels[args.level]))
        elif verdict not in VERDICTS:
            problems.append("%s has verdict %r; one of %s" % (test, verdict, sorted(VERDICTS)))
        elif not allowed(cases[test]):
            problems.append("%s belongs to step '%s', which comes after the step of %s: what it tests is not "
                            "in the build" % (test, cases[test].front.get("step"), build.id))
        else:
            row = {"test": test, "verdict": verdict}
            row.update({k: entry[k] for k in ("evidence", "reason") if entry.get(k)})
            results.append(row)
    reported = {r["test"] for r in results}
    problems += ["approved test case %s has no result in the file" % c.id
                 for c in cases.values() if c.status == "approved" and required(c) and c.id not in reported]
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
    if build is not None:
        front["build"] = build.id
    if args.selection:
        front["selection"] = args.selection
    if coverage:
        front["coverage"] = coverage       # a list per unit, or the reason it was not measured
    scripts = [str(cases[r["test"]].front.get("script") or "").partition("::")[0] for r in results]
    front["sources"] = source_hashes(project, unit_sources(project) + [s for s in scripts if s])
    path = write_item(project, "test-run", front)
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in sorted(VERDICTS)}
    print("wrote %s: %s" % (path, ", ".join("%d %s" % (n, v) for v, n in counts.items() if n)))
    return 0


def cmd_build(project, args):
    plan = project.integration_plan()
    if plan is None:
        return stop(["no approved software-integration plan: the steps a build carries out are defined there"])
    steps = [str(s.get("name")) for s in project.integration_steps(plan)]
    if args.step not in steps:
        return stop(["%s has no step '%s'; its steps: %s" % (plan.id, args.step, ", ".join(steps))])
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    problems = ["the manifest gives no %s" % key for key in ("executed_at", "tool") if not data.get(key)]
    if data.get("result") not in ("succeeded", "failed"):
        problems.append("the manifest gives result %r; one of succeeded, failed" % data.get("result"))
    paths = project.config.get("paths") or {}
    exempt = trace.as_list(paths.get("generated")) + trace.as_list(paths.get("third_party"))
    owner = {Path(str(f)).as_posix(): u for u in project.of_type("software-unit") if project.live(u)
             for f in u.front.get("source_files") or []}
    contents, built = {}, []
    for name in (Path(str(f)).as_posix() for f in data.get("files", [])):
        built.append(name)
        if name in owner:
            unit = owner[name]
            parents = unit.targets("part_of")
            if not parents:
                problems.append("%s belongs to %s, which is part of no component" % (name, unit.id))
                continue
            entry = contents.setdefault(parents[0][0], {"component": parents[0][0], "units": []})
            if unit.id not in entry["units"]:
                entry["units"].append(unit.id)
        elif not any(fnmatch.fnmatch(name, pattern) for pattern in exempt):
            problems.append("built file %s belongs to no software unit; code of a component integrated as received "
                            "is listed under 'delivered' with the component and its version" % name)
    for entry in data.get("delivered", []):
        comp = project.items.get(str(entry.get("component")))
        if comp is None or comp.type != "software-component":
            problems.append("delivered names %s, which is not a software component" % entry.get("component"))
        elif not entry.get("version"):
            problems.append("delivered %s needs the version that was integrated" % comp.id)
        elif comp.id in contents:
            problems.append("%s is listed as delivered and has units built from the project's sources" % comp.id)
        else:
            contents[comp.id] = {"component": comp.id, "delivered": str(entry["version"])}
            built += [Path(str(f)).as_posix() for f in entry.get("files", [])]
    doubles = []
    for entry in data.get("doubles", []):
        comp = project.items.get(str(entry.get("component")))
        if comp is None or comp.type != "software-component" or not entry.get("file"):
            problems.append("a double needs the software component it stands for and its file: %s" % entry)
        else:
            doubles.append({"component": comp.id, "file": Path(str(entry["file"])).as_posix()})
    problems += ["built file %s does not exist" % f for f in built + [d["file"] for d in doubles]
                 if not (project.root / f).is_file()]
    if problems:
        return stop(problems)
    record_id = next_id(project, "build-record")
    front = {
        "id": record_id,
        "type": "build-record",
        "status": "final",
        "step": args.step,
        "item_under_test": args.item_under_test,
        "tool": data["tool"],
        "executed_at": data["executed_at"],
        "result": data["result"],
        "contents": [dict(contents[c], units=sorted(contents[c]["units"])) if "units" in contents[c] else contents[c]
                     for c in sorted(contents)],
    }
    if doubles:
        front["doubles"] = sorted(doubles, key=lambda d: (d["component"], d["file"]))
    front["sources"] = source_hashes(project, built + [d["file"] for d in doubles])
    if data.get("evidence"):
        front["evidence"] = keep_evidence(project, record_id, data["evidence"])
    path = write_item(project, "build-record", front)
    expected = project.integrated_up_to(project.integration_steps(plan), steps.index(args.step))
    absent = [c for c in expected if c not in contents]
    print("wrote %s: step '%s', %s, %d components (%s)" % (path, args.step, data["result"], len(contents),
                                                             ", ".join(sorted(contents))))
    if absent:
        print("not in this build, although the step integrates them: %s" % ", ".join(absent))
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
    """The toolkit checklist that '<name> v<N>' cites, as {file, version, cited, checks: {ID: kind}}, or None.

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
            rows = re.findall(r"(?m)^\|\s*([A-Z]{2,5}-\d+)\s*\|.*\|\s*(script|semantic|accountable)\s*\|\s*$", text)
            sections, heading = {}, None
            for line in text.splitlines():
                if line.startswith("## "):
                    heading = plain(line[3:])
                found = re.match(r"^\|\s*([A-Z]{2,5}-\d+)\s*\|", line)
                if found and heading:
                    sections.setdefault(heading, []).append(found.group(1))
            return {"file": path.name, "version": version.group(1) if version else None, "cited": cited.group(2),
                    "checks": dict(rows), "sections": sections, "hash": file_hash(path)}
    return None


def cmd_review(project, args):
    problems = ["no such item: %s" % i for i in args.ids if i not in project.items]
    if problems:
        return stop(problems)
    items = [project.items[i] for i in args.ids]
    findings = json.loads(Path(args.findings).read_text(encoding="utf-8")) if args.findings else []
    for finding in findings:
        if finding.get("state") not in ("open", "closed") or finding.get("severity") not in ("major", "minor"):
            problems.append("finding %s needs severity major|minor and state open|closed" % finding.get("id"))
    checks = json.loads(Path(args.checks).read_text(encoding="utf-8")) if args.checks else []
    subjects = set(args.ids)
    for finding in findings:
        if finding.get("item") and finding["item"] not in subjects:
            problems.append("finding %s is on %s, which is not a subject of this review. A problem in another item is "
                            "recorded about that item: a problem report with `affects` for an item of the project, a "
                            "query for an imported one; or the item becomes a subject" % (finding.get("id"), finding["item"]))
    sectioned = [entry for entry in checks if "section" in entry and "check" not in entry]
    checks = [entry for entry in checks if entry not in sectioned]
    for entry in checks:
        if entry.get("result") not in RESULTS:
            problems.append("check %s needs result %s" % (entry.get("check"), "|".join(RESULTS)))
        elif entry["result"] == "not-applicable" and not entry.get("note"):
            problems.append("check %s is not-applicable: the note must say why" % entry.get("check"))
    approving = args.verdict == "approved"
    listed = None                                         # the toolkit checklist, when one is cited

    if args.reconfirm:
        # nothing in the subject changed: it is confirmed against the new versions of what it builds on
        source, citation = "reconfirmation", args.checklist or "reconfirmation after a change upstream"
        if args.item_under_test or args.external_criteria:
            problems.append("--reconfirm confirms unchanged items and cannot be combined with --item-under-test or "
                            "--external-criteria: a review of code is recorded against the code checklist")
        problems += ["%s: its current content has no approving review, so there is nothing to reconfirm; "
                     "it needs a review against its checklist" % item.id
                     for item in items if project.approving_review(item) is None]
        if sectioned or checks:
            problems.append("--reconfirm applies no checklist: leave out --checks")
    elif args.external_criteria:
        source, citation = "external", args.checklist
        if not citation:
            problems.append("--external-criteria needs --checklist to name the criteria that were used")
        if sectioned:
            problems.append("a section entry needs a checklist of the toolkit; list the checks one by one")
    else:
        source, citation = "toolkit", args.checklist
        listed = find_checklist(citation) if citation else None
        if not citation:
            problems.append("--checklist is needed: '<name> v<N>' of a file under .claude/docs/checklists")
        elif listed is None:
            problems.append("'%s' cites no checklist of this toolkit: expected '<name> v<N>' for a file under "
                            ".claude/docs/checklists. For criteria from outside the toolkit pass --external-criteria; "
                            "to confirm unchanged items after a change upstream pass --reconfirm." % citation)
        else:
            given_ids = {str(c.get("check")) for c in checks}
            for entry in sectioned:
                ids = listed["sections"].get(plain(str(entry["section"])))
                if ids is None:
                    problems.append("section '%s' is not a section of %s" % (entry["section"], listed["file"]))
                elif entry.get("result") != "not-applicable" or not entry.get("note"):
                    problems.append("section '%s': only not-applicable, with a note that says why, can be given for a "
                                    "whole section" % entry["section"])
                else:
                    checks += [{"check": i, "result": "not-applicable", "note": "section %s: %s" % (entry["section"], entry["note"])}
                               for i in ids if i not in given_ids]
            if listed["version"] != listed["cited"]:
                problems.append("%s is at version %s, the citation says v%s" % (listed["file"], listed["version"], listed["cited"]))
            given = {str(c.get("check")): c for c in checks}
            problems += ["check %s is not in %s" % (c, listed["file"]) for c in given if c not in listed["checks"]]
            if approving:
                missing = [c for c in listed["checks"] if c not in given]
                if missing:
                    problems.append("verdict approved needs a result for every check of %s (--checks); none for: %s"
                                    % (listed["file"], ", ".join(missing)))
                refused = [c for c, kind in listed["checks"].items()
                           if kind == "accountable" and given.get(c, {}).get("result") == "finding"]
                if refused:
                    problems.append("accountable checks answered with a finding: %s. What a person states is missing "
                                    "cannot be closed by decision; record the verdict rework, or record the check as "
                                    "pass once the fact exists" % ", ".join(refused))

    if approving:
        if any(f.get("state") == "open" for f in findings):
            problems.append("verdict approved is not possible while a finding is open")
        unassessed = [str(c.get("check")) for c in checks if c.get("result") == "not-assessed"]
        if unassessed:
            problems.append("verdict approved is not possible while checks are not assessed: %s" % ", ".join(unassessed))
        for item in items:
            for target_id, role in project.dependencies(item):
                target = project.items.get(target_id)
                if target is not None and target_id not in args.ids and project.live(target) \
                        and project.types[target.type]["lifecycle"] == "engineering" and target.status != "approved":
                    problems.append("%s cannot be approved while %s (%s) is in state %s"
                                    % (item.id, target_id, role, target.status))
        closing = {str(f.get("closes")) for f in findings if f.get("closes") and f.get("state") == "closed"}
        for item in items:
            for earlier in project.reviews_of(item):
                for finding in earlier.front.get("findings") or []:
                    ref = "%s#%s" % (earlier.id, finding.get("id"))
                    if finding.get("state") == "open" and finding.get("item") in (None, item.id) and ref not in closing:
                        problems.append("%s: finding %s of an earlier review of the same content is open; close it "
                                        "with a finding entry that has \"closes\": \"%s\"" % (item.id, ref, ref))
    if problems:
        return stop(problems)

    references = {}
    for item in items:
        for target, _ in project.dependencies(item):
            if target in project.items and target not in args.ids:
                references[target] = project.items[target].hash
    front = {
        "id": next_id(project, "review-record"),
        "type": "review-record",
        "status": "final",
        "checklist": citation,
        "checklist_source": source,
        "checklist_hash": listed["hash"] if listed else None,
        "reviewers": args.reviewer,
        "verdict": args.verdict,
        "reviewed_at": datetime.date.today().isoformat(),
        "subject": [{"item": i.id, "hash": i.hash} for i in items],
        "references": [{"item": i, "hash": h} for i, h in sorted(references.items())],
        "findings": findings,
    }
    if front["checklist_hash"] is None:
        del front["checklist_hash"]
    if checks:
        front["checks"] = checks
    if args.reconfirm:
        front["rests_on"] = sorted({project.approving_review(i).id for i in items})
    code = [f for i in items if i.type == "software-unit" for f in i.front.get("source_files") or []]
    if code and args.item_under_test:      # naming the code revision is what makes it a review of the code
        front["item_under_test"] = args.item_under_test
        front["sources"] = source_hashes(project, code)
    elif code and args.reconfirm:
        # The code review of each unit is carried over exactly as it was recorded - the hashes of
        # then, not of now - so code that changed since stays reported as changed after review.
        kept, revisions = {}, set()
        for item in items:
            earlier = project.approving_review(item)
            mine = {Path(str(f)).as_posix() for f in item.front.get("source_files") or []}
            for entry in (earlier.front.get("sources") or []) if earlier else []:
                if isinstance(entry, dict) and Path(str(entry.get("file"))).as_posix() in mine:
                    kept[Path(str(entry["file"])).as_posix()] = str(entry.get("hash"))
                    revisions.add(str(earlier.front.get("item_under_test")))
        if kept:
            front["sources"] = [{"file": name, "hash": value} for name, value in sorted(kept.items())]
            front["item_under_test"] = ", ".join(sorted(revisions))
    elif args.item_under_test:
        front["item_under_test"] = args.item_under_test
    path = write_item(project, "review-record", front)
    print("wrote %s: %s, %d items, %d references, %d findings"
          % (path, args.verdict, len(items), len(references), len(findings)))
    for earlier in front.get("rests_on") or []:
        basis = project.items[earlier].front
        print("rests on %s: %s - %s" % (earlier, basis.get("checklist_source") or "toolkit", basis.get("checklist")))
    return 0


def cmd_status_report(project, args):
    as_of = trace.as_date(args.as_of) if args.as_of else datetime.date.today()
    problems = [] if as_of else ["--as-of must be a date YYYY-MM-DD"]
    text = Path(args.assessment).read_text(encoding="utf-8").strip() if args.assessment and Path(args.assessment).is_file() else ""
    if not text:
        problems.append("--assessment names no file with text: the report carries the reporter's reading of the "
                        "figures, in their words")
    if problems:
        return stop(problems)
    data = trace.progress(project, as_of)
    findings = project.check()
    front = {
        "id": next_id(project, "project-status-report"),
        "type": "project-status-report",
        "status": "final",
        "title": "Project status as of %s" % as_of,
        "as_of": str(as_of),
        "period": args.period,
        "reported_by": args.reported_by,
        "work_packages": [{k: p[k] for k in ("item", "state", "planned_finish", "late", "estimate", "actual_effort",
                                             "delivered", "settled")} for p in data["work_packages"]],
        "milestones": [{k: m[k] for k in ("name", "date", "state")} for m in data["milestones"]],
        "corrective_actions": [{k: a[k] for k in ("item", "state", "due", "overdue")} for a in data["corrective_actions"]],
        "check": {"errors": sum(1 for f in findings if f["level"] == "error"),
                  "warnings": sum(1 for f in findings if f["level"] == "warning")},
    }
    if not args.period:
        del front["period"]
    path = write_item(project, "project-status-report", front, "\n## Assessment\n\n%s\n" % text)
    print("wrote %s: %d work packages, %d late; %d milestones; %d corrective actions open"
          % (path, len(data["work_packages"]), sum(1 for p in data["work_packages"] if p["late"]),
             len(data["milestones"]), len(data["corrective_actions"])))
    return 0


def read_text_file(path, what):
    """The text of a file a person wrote, or None."""
    return Path(path).read_text(encoding="utf-8").strip() if path and Path(path).is_file() else None


def quality_findings(project, path, problems):
    """Findings of a quality check from a JSON file; each must name an existing action."""
    if not path:
        return []
    findings = json.loads(Path(path).read_text(encoding="utf-8"))
    for finding in findings:
        action = project.items.get(str(finding.get("action")))
        if not finding.get("id") or not finding.get("text"):
            problems.append("a finding needs id and text: %s" % finding)
        if action is None or action.type not in ("corrective-action", "problem-report"):
            problems.append("finding %s: action %s is no corrective action or problem report; write the action first"
                            % (finding.get("id"), finding.get("action")))
    return findings


def consistent_result(result, findings, problems):
    if result == "conforms" and findings:
        problems.append("result conforms, but the file lists findings")
    if result != "conforms" and not findings:
        problems.append("result %s needs at least one finding" % result)


def cmd_quality_check(project, args):
    plan = project.quality_plan()
    problems = [] if plan else ["no approved quality-assurance plan: the checks are performed as it defines them"]
    names = [str(c.get("name")) for c in trace.as_list(plan.front.get("quality_checks")) if isinstance(c, dict)] if plan else []
    if plan and args.check and args.check not in names:
        problems.append("%s has no quality check '%s'; its checks: %s" % (plan.id, args.check, ", ".join(names)))
    checked_at = args.checked_at or datetime.date.today().isoformat()
    if trace.as_date(checked_at) is None:
        problems.append("--checked-at must be a date YYYY-MM-DD")
    summary = read_text_file(args.summary, "summary")
    if not summary:
        problems.append("--summary names no file with text: the record carries the checker's verdict in their words")
    facts = []
    if args.kind == "work-product":
        for ref in args.subject:
            item = project.items.get(ref)
            if item is None:
                problems.append("no such item: %s" % ref)
                continue
            review = project.approving_review(item)
            facts.append({"item": item.id, "type": item.type, "status": item.status, "hash": item.hash,
                          "approved_by": review.id if review else None,
                          "reviewers": trace.as_list(review.front.get("reviewers")) if review else [],
                          "checklist": review.front.get("checklist") if review else None})
    else:
        scope = project.scope or set()
        for ref in args.subject:
            if project.scope is not None and ref not in scope:
                problems.append("%s is not a process in the scope of this project" % ref)
                continue
            facts.append({"process": ref, "practices": [{k: row[k] for k in ("practice", "state", "errors", "warnings")}
                                                        for row in trace.practice_rows(Project(project.root), ref)]})
    findings = quality_findings(project, args.findings, problems)
    consistent_result(args.result, findings, problems)
    if problems:
        return stop(problems)
    front = {
        "id": next_id(project, "quality-record"),
        "type": "quality-record",
        "status": "final",
        "kind": args.kind,
        "check": args.check,
        "subject": args.subject,
        "criteria": args.criteria,
        "checked_by": args.checked_by,
        "checked_at": checked_at,
        "result": args.result,
        "findings": findings,
        "facts": facts,
    }
    if not args.check:
        del front["check"]
    path = write_item(project, "quality-record", front, "\n## Summary\n\n%s\n" % summary)
    print("wrote %s: %s check of %s, %s, %d findings" % (path, args.kind, ", ".join(args.subject), args.result, len(findings)))
    return 0


def cmd_quality_report(project, args):
    as_of = trace.as_date(args.as_of) if args.as_of else datetime.date.today()
    problems = [] if as_of else ["--as-of must be a date YYYY-MM-DD"]
    summary = read_text_file(args.summary, "summary")
    if not summary:
        problems.append("--summary names no file with text: the report carries the reading of quality assurance, "
                        "in the words of the person in that role")
    if project.quality_plan() is None:
        problems.append("no approved quality-assurance plan: reporting is done as it defines it")
    if problems:
        return stop(problems)
    data = trace.quality(project, as_of)
    front = {
        "id": next_id(project, "quality-record"),
        "type": "quality-record",
        "status": "final",
        "title": "Quality assurance report as of %s" % as_of,
        "kind": "summary",
        "subject": data["figures"]["not_summarised"],
        "criteria": "%s, %s" % (data["plan"], args.period or "since the last report"),
        "checked_by": args.checked_by,
        "checked_at": str(as_of),
        "result": args.result,
        "findings": [],
        "facts": {"checks": [{k: c[k] for k in ("name", "performed", "last", "last_result")} for c in data["checks"]],
                  "findings": [{k: f[k] for k in ("record", "finding", "action", "state", "overdue_days", "escalation_due")}
                               for f in data["findings"]],
                  "figures": {k: v for k, v in data["figures"].items() if k != "not_summarised"}},
    }
    path = write_item(project, "quality-record", front, "\n## Summary\n\n%s\n" % summary)
    print("wrote %s: report over %d quality records, %d findings open" % (path, len(front["subject"]),
                                                                          data["figures"]["findings_open"]))
    return 0


RATING_ORDER = {"N": 0, "P": 1, "L": 2, "F": 3}
RATING_BANDS = {                                   # the ratings that agree with what the trace engine observes
    "evidence present": ("L", "F"),
    "warnings open": ("P", "L", "F"),
    "evidence not settled": ("P", "L"),
    "findings open": ("N", "P", "L"),
    "no evidence yet": ("N", "P"),
    "no evidence structure": (),                   # the toolkit cannot tell: every rating says where the evidence is
}


def assessment_findings(project, processes, data):
    """Missing and wrong ratings, and the consistency flags with whether each one needs a note."""
    problems, flags, observations, ratings = [], [], [], {}
    for entry in data.get("practices", []):
        if entry.get("rating") not in RATING_ORDER:
            problems.append("%s: rating %r; one of N, P, L, F" % (entry.get("practice"), entry.get("rating")))
        else:
            ratings[str(entry.get("practice"))] = entry
    catalog = trace.ROOT / "aspice" / str((project.config.get("aspice") or {}).get("version") or "3.1") / "processes"
    relations = []
    for pid in processes:
        source = catalog / (pid + ".yaml")
        if not source.is_file():
            problems.append("%s is not a process of the catalog" % pid)
            continue
        relations += yaml.safe_load(source.read_text(encoding="utf-8")).get("depends_on") or []
        for row in trace.practice_rows(Project(project.root), pid):
            observations.append({"practice": row["practice"], "state": row["state"]})
            entry = ratings.get(row["practice"])
            if entry is None:
                problems.append("%s has no rating" % row["practice"])
                continue
            band = RATING_BANDS.get(row["state"], ())
            if entry["rating"] not in band:
                flags.append({"practice": row["practice"], "kind": "observation", "needs_note": True,
                              "text": "rated %s while the toolkit observes '%s'" % (entry["rating"], row["state"])})
    known = {o["practice"] for o in observations}
    problems += ["%s is not a base practice of %s" % (p, ", ".join(processes)) for p in ratings if p not in known]
    for relation in relations:
        source, target = ratings.get(str(relation.get("from"))), ratings.get(str(relation.get("to")))
        if source and target and RATING_ORDER[source["rating"]] > RATING_ORDER[target["rating"]]:
            flags.append({"practice": source["practice"], "kind": relation.get("kind"),
                          "needs_note": relation.get("kind") == "rule",
                          "text": "rated %s, above %s, which it depends on (%s), rated %s"
                                  % (source["rating"], target["practice"], relation.get("kind"), target["rating"])})
    for flag in flags:
        flag["note"] = (ratings.get(flag["practice"]) or {}).get("note")
        if flag["needs_note"] and not flag["note"]:
            problems.append("%s %s: give the reason in its note" % (flag["practice"], flag["text"]))
    return problems, flags, observations


def cmd_self_assessment(project, args):
    data = json.loads(Path(args.ratings).read_text(encoding="utf-8"))
    processes = args.process or list(trace.as_list((project.config.get("scope") or {}).get("assessment_scope"))) \
        or sorted(project.scope or [])
    problems, flags, observations = assessment_findings(project, processes, data)
    for entry in data.get("attributes", []):
        if entry.get("rating") not in RATING_ORDER or not entry.get("process") or not entry.get("attribute"):
            problems.append("attribute rating needs process, attribute and a rating N, P, L or F: %s" % entry)
    if args.check_only:
        for flag in flags:
            print("%s %s%s" % (flag["practice"], flag["text"], " - note: %s" % flag["note"] if flag["note"] else ""))
        print("\n".join(problems) if problems else "ratings complete; every flag that needs a note has one")
        return 1 if problems else 0
    summary = read_text_file(args.summary, "summary")
    if not summary:
        problems.append("--summary names no file with text: strengths, weaknesses and actions, in the assessors' words")
    if problems:
        return stop(problems)
    as_of = args.as_of or datetime.date.today().isoformat()
    front = {
        "id": next_id(project, "self-assessment"),
        "type": "self-assessment",
        "status": "final",
        "title": "Self-assessment of %s as of %s" % (", ".join(processes), as_of),
        "as_of": as_of,
        "assessors": args.assessor,
        "processes": processes,
        "target_level": (project.config.get("aspice") or {}).get("target_level"),
        "ratings": sorted(data.get("practices", []), key=lambda e: str(e.get("practice"))),
        "attribute_ratings": data.get("attributes", []),
        "observations": observations,
        "consistency": [{k: f[k] for k in ("practice", "kind", "text", "note")} for f in flags],
    }
    if not front["attribute_ratings"]:
        del front["attribute_ratings"]
    path = write_item(project, "self-assessment", front, "\n## Summary\n\n%s\n" % summary)
    print("wrote %s: %d practices rated, %d consistency flags" % (path, len(front["ratings"]), len(flags)))
    return 0


def cmd_problem_trends(project, args):
    as_of = trace.as_date(args.as_of) if args.as_of else datetime.date.today()
    problems = [] if as_of else ["--as-of must be a date YYYY-MM-DD"]
    text = Path(args.assessment).read_text(encoding="utf-8").strip() if args.assessment and Path(args.assessment).is_file() else ""
    if not text:
        problems.append("--assessment names no file with text: the report carries the analyst's reading of the "
                        "figures - trends, recurring causes and the actions decided - in their words")
    if problems:
        return stop(problems)
    data = trace.problems(project, as_of)
    front = {
        "id": next_id(project, "problem-trend-report"),
        "type": "problem-trend-report",
        "status": "final",
        "title": "Problem status and trends as of %s" % as_of,
        "as_of": str(as_of),
        "period": args.period,
        "reported_by": args.reported_by,
        "problems": [{k: e[k] for k in ("item", "state", "severity", "origin", "detected_by", "age_days")}
                     for e in data["problems"]],
        "figures": data["figures"],
    }
    if not args.period:
        del front["period"]
    path = write_item(project, "problem-trend-report", front, "\n## Assessment\n\n%s\n" % text)
    figures = data["figures"]
    print("wrote %s: %d problems, %d unresolved" % (path, figures["total"], figures["unresolved"]))
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
    if args.practice:
        front["practices"] = args.practice
    path = write_item(project, "communication-record", front)
    print("wrote %s: %s to %s" % (path, ", ".join(args.subject), ", ".join(args.audience)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("next-id").add_argument("type")
    run = sub.add_parser("test-run")
    run.add_argument("--level", required=True)
    run.add_argument("--results", required=True)
    run.add_argument("--item-under-test", required=True)
    run.add_argument("--environment", required=True)
    run.add_argument("--deviation", action="append", metavar="UNIT=TEXT")
    run.add_argument("--build", help="build record of the integrated software that was tested")
    run.add_argument("--selection", help="how the test cases were chosen, in the terms of the test strategy")
    run.add_argument("--executed-at", help="time the tests ran, when the results file does not give it")
    built = sub.add_parser("build")
    built.add_argument("--step", required=True)
    built.add_argument("--manifest", required=True)
    built.add_argument("--item-under-test", required=True)
    analysis = sub.add_parser("analysis-run")
    analysis.add_argument("--results", required=True)
    analysis.add_argument("--item-under-test", required=True)
    review = sub.add_parser("review")
    review.add_argument("--checklist")
    review.add_argument("--reviewer", required=True, action="append")
    review.add_argument("--verdict", required=True, choices=["approved", "rework"])
    review.add_argument("--findings")
    review.add_argument("--checks")
    review.add_argument("--item-under-test")
    review.add_argument("--external-criteria", action="store_true",
                        help="the review used criteria from outside the toolkit, named under --checklist")
    review.add_argument("--reconfirm", action="store_true",
                        help="the items are unchanged and are confirmed against new versions of what they build on")
    review.add_argument("ids", nargs="+")
    status = sub.add_parser("status-report")
    status.add_argument("--reported-by", required=True)
    status.add_argument("--assessment", required=True, help="text file with the reporter's assessment")
    status.add_argument("--as-of", help="date the figures are measured against (default: today)")
    status.add_argument("--period")
    qa_check = sub.add_parser("quality-check")
    qa_check.add_argument("--kind", required=True, choices=["work-product", "process"])
    qa_check.add_argument("--check", help="name of the quality check of the quality-assurance plan")
    qa_check.add_argument("--subject", required=True, action="append", help="item ID, or process ID for kind process")
    qa_check.add_argument("--criteria", required=True)
    qa_check.add_argument("--checked-by", required=True)
    qa_check.add_argument("--result", required=True, choices=["conforms", "conforms-with-findings", "does-not-conform"])
    qa_check.add_argument("--summary", required=True, help="text file with the checker's verdict in their words")
    qa_check.add_argument("--findings", help="JSON file: [{id, text, action, severity}]")
    qa_check.add_argument("--checked-at", help="date of the check (default: today)")
    qa_report = sub.add_parser("quality-report")
    qa_report.add_argument("--checked-by", required=True)
    qa_report.add_argument("--result", required=True, choices=["conforms", "conforms-with-findings", "does-not-conform"])
    qa_report.add_argument("--summary", required=True)
    qa_report.add_argument("--as-of")
    qa_report.add_argument("--period")
    sas = sub.add_parser("self-assessment")
    sas.add_argument("--ratings", required=True, help='JSON: {"practices": [{practice, rating, note}], "attributes": [...]}')
    sas.add_argument("--assessor", action="append", help="person who rated; repeat for several")
    sas.add_argument("--process", action="append", help="process assessed (default: assessment_scope, else the scope)")
    sas.add_argument("--summary", help="text file: strengths, weaknesses, actions")
    sas.add_argument("--as-of")
    sas.add_argument("--check-only", action="store_true", help="report missing ratings and flags, write nothing")
    trends = sub.add_parser("problem-trends")
    trends.add_argument("--reported-by", required=True)
    trends.add_argument("--assessment", required=True, help="text file with the analyst's reading")
    trends.add_argument("--as-of", help="date the ages are measured to (default: today)")
    trends.add_argument("--period")
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--tag", required=True)
    baseline.add_argument("--purpose", required=True)
    told = sub.add_parser("communication")
    told.add_argument("--subject", required=True, action="append")
    told.add_argument("--audience", required=True, action="append")
    told.add_argument("--channel", required=True)
    told.add_argument("--agreement")
    told.add_argument("--sent-at", help="date it was sent, when not today")
    told.add_argument("--practice", action="append", help="communicate practice the record serves, e.g. SWE.1.BP8")
    args = ap.parse_args()
    project = Project(args.project)
    commands = {"next-id": cmd_next_id, "test-run": cmd_test_run, "analysis-run": cmd_analysis_run,
                "review": cmd_review, "baseline": cmd_baseline, "communication": cmd_communication,
                "status-report": cmd_status_report, "build": cmd_build,
                "problem-trends": cmd_problem_trends, "quality-check": cmd_quality_check,
                "quality-report": cmd_quality_report, "self-assessment": cmd_self_assessment}
    return commands[args.command](project, args)


if __name__ == "__main__":
    sys.exit(main())
