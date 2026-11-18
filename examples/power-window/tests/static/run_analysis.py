#!/usr/bin/env python3
"""Run compiler-based static analysis over the unit sources of the example.

Uses the analyser that comes with the compiler found by the unit test runner:
`-fanalyzer` for gcc, `--analyze` for clang, `/analyze` for the Visual Studio
compiler. This checks for defects such as null dereference, uninitialised use
and buffer overrun. It is NOT a coding-guideline checker: conformance to a
guideline set such as MISRA C needs a dedicated analyser and is not shown by
this run.

Writes `build/static-analysis.log` (raw tool output) and
`build/static-analysis-results.json`, the input of
`python tools/record.py analysis-run`. Standard library only.

Usage (from the repository root):
    python examples/power-window/tests/static/run_analysis.py
"""
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "unit"))
from run_tests import BUILD, ROOT, SOURCES, find_compiler, include_directories, msvc, relative, run  # noqa: E402

MSVC_LINE = re.compile(r"^(?P<file>[^()\n]+)\((?P<line>\d+)(?:,\d+)?\)\s*:\s*(?P<severity>warning|error)\s+(?P<rule>C\d+)\s*:\s*(?P<message>.*)$")
GNU_LINE = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?:\d+:)?\s*(?P<severity>warning|error):\s*(?P<message>.*?)(?:\s+\[(?P<rule>[^\]]+)\])?$")


def analyse(compiler, source):
    includes = [relative(folder) for folder in include_directories()]
    if compiler["kind"] == "msvc":
        # autolog- keeps the analyser from dropping an XML file per source into the working directory
        arguments = ["/nologo", "/std:c11", "/W4", "/analyze", "/analyze:only", "/analyze:autolog-"]
        arguments += ['/I"%s"' % folder for folder in includes] + ['"%s"' % relative(source)]
        return msvc(compiler["vcvars"], arguments)
    flag = ["--analyze"] if "clang" in compiler["name"].lower() else ["-fanalyzer", "-fsyntax-only"]
    command = [compiler["path"], "-std=c99", "-Wall", "-Wextra"] + flag
    command += ["-I" + folder for folder in includes] + [relative(source)]
    return run(command, cwd=str(ROOT))


def main():
    compiler = find_compiler()
    if compiler is None:
        print("NOT ASSESSED: no C compiler found, static analysis did not run")
        return 2
    pattern = MSVC_LINE if compiler["kind"] == "msvc" else GNU_LINE
    mode = "/analyze" if compiler["kind"] == "msvc" else ("--analyze" if "clang" in compiler["name"].lower() else "-fanalyzer")
    sources = sorted(SOURCES.rglob("*.c"))
    BUILD.mkdir(exist_ok=True)
    log, findings, failed = [], [], []
    for source in sources:
        code, output = analyse(compiler, source)
        log.append("=== %s (exit %d)\n%s" % (relative(source), code, output))
        seen = set()
        for line in output.splitlines():
            match = pattern.match(line.strip())
            if not match:
                continue
            file = Path(match.group("file").strip())
            file = relative(file if file.is_absolute() else ROOT / file)
            key = (file, match.group("line"), match.group("rule"))
            if key in seen:
                continue
            seen.add(key)
            findings.append({"file": file, "line": int(match.group("line")), "rule": match.group("rule") or "",
                             "severity": match.group("severity"), "message": match.group("message").strip()})
        if code != 0 and not seen:
            failed.append(relative(source))        # the tool stopped without a finding it could attribute
    (BUILD / "static-analysis.log").write_text("\n".join(log), encoding="utf-8")
    if failed:
        print("NOT ASSESSED: the analyser failed on %s; see build/static-analysis.log" % ", ".join(failed))
        return 2
    results = {
        "tool": "%s, compiler static analysis (%s), no coding-guideline rule set" % (compiler["name"].split(" (")[0], mode),
        "executed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "files": [relative(s) for s in sources],
        "findings": findings,
        "evidence": "build/static-analysis.log",
    }
    (BUILD / "static-analysis-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("tool: %s" % results["tool"])
    print("%d files analysed, %d findings" % (len(sources), len(findings)))
    for finding in findings:
        print("  %(file)s:%(line)d %(severity)s %(rule)s %(message)s" % finding)
    print("results: build/static-analysis-results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
