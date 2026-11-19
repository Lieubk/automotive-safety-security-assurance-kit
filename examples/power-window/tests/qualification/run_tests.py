#!/usr/bin/env python3
"""Build the complete software of the power window example and run its qualification tests.

The software under test is what the last step of the software integration plan
contains - the same files the integration runner builds for that step, with the
same doubles - built together with tests/qualification/test_qualification.c into
one program. The result file build/qualification/results.json is the input of
`tools/record.py test-run --level software-qualification --build <BLD-ID>`, where
BLD-ID is the build record of the last step made from the same commit
(`python tools/traceability.py status` names it).

Verdict lines are `SQT-0001 PASS` or `SQT-0001 FAIL <file>:<line>`; a test case of
the test file that prints no PASS line counts as failed.

Usage:  python tests/qualification/run_tests.py
Exit code 0 = every case passed, 1 = the build or a case failed, 2 = nothing could be run.
"""
import datetime
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
spec = importlib.util.spec_from_file_location("integration_runner", str(ROOT / "tests" / "integration" / "run_tests.py"))
integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integration)
unit = integration.unit


def main():
    loaded = integration.load()
    if isinstance(loaded, str):
        print(loaded)
        return 2
    project, plan, steps, config = loaded
    if not steps:
        print("%s has no integration steps" % plan.id)
        return 2
    compiler = unit.find_compiler()
    if compiler is None:
        print("no C compiler found: put cc, gcc or clang on PATH, or install Visual Studio with the C++ workload")
        return 2
    last = len(steps) - 1
    software, delivered, doubles, problems = integration.step_contents(project, config, steps, last)
    if problems:
        print("software of step '%s' not complete: %s" % (steps[last]["name"], "; ".join(problems)))
        return 2
    folder = unit.BUILD / "qualification"
    test_file = HERE / "test_qualification.c"
    files = software + [f for d in delivered for f in d["files"]] + [d["file"] for d in doubles]
    executable, code, output = integration.build(compiler, config, files + [unit.relative(test_file)],
                                                 folder, "test_qualification")
    results = integration.run_program(executable, test_file, folder / "run.log", code == 0, output)
    report = {"compiler": compiler["name"],
              "executed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "results": results}
    (folder / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    passed = sum(1 for r in results if r["verdict"] == "passed")
    print("software of step '%s' (%s): build %s, %d of %d passed  (%s)"
          % (steps[last]["name"], plan.id, "succeeded" if code == 0 else "failed", passed, len(results),
             unit.relative(folder)))
    failed = [r["test"] for r in results if r["verdict"] != "passed"]
    if failed:
        print("failed: %s" % ", ".join(failed))
    return 1 if code != 0 or failed or not results else 0


if __name__ == "__main__":
    sys.exit(main())
