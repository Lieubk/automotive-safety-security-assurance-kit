#!/usr/bin/env python3
"""Build the integration steps of the power window example and run their tests.

For every step of the software integration plan (the plan of kind
software-integration under plans/; the approved one if there is one) the script

- collects what the step contains: the C files of the units of every developed
  component integrated up to the step, the files of every component taken over as
  received, and the doubles of the components the step names under `doubles`
  (both from tests/integration/integration.yaml);
- builds one test program from them and tests/integration/test_<step>.c;
- writes build/integration/<step>/manifest.json, the input of
  `tools/record.py build`;
- runs the program and writes build/integration/<step>/results.json, the input of
  `tools/record.py test-run --level software-integration --build <BLD-ID>`.

Steps and components are read from the items with the toolkit's trace engine
(tools/traceability.py, found in the project or a folder above it). The compiler
is chosen as for the unit tests (tests/unit/run_tests.py); warnings are errors.
Verdict lines are `SIT-0001 PASS` or `SIT-0001 FAIL <file>:<line>`; a test case
of the test file that prints no PASS line counts as failed.

Usage:  python tests/integration/run_tests.py [--step NAME]
Exit code 0 = every step built and every case passed, 1 = a build or a case
failed, 2 = nothing could be run. Needs PyYAML, like the toolkit.
"""
import datetime
import importlib.util
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


unit = load_module("unit_runner", ROOT / "tests" / "unit" / "run_tests.py")   # its compiler handling

VERDICT_LINE = re.compile(r"^((?:SIT|SQT)-\d{4}) (PASS|FAIL)\b")
TEST_FUNCTION = re.compile(r"\btest_(SIT|SQT)_(\d{4})_\w+\s*\(\s*void\s*\)\s*\{")


def trace_engine():
    """The Project class of the toolkit's trace engine, or None."""
    for folder in [ROOT] + list(ROOT.parents):
        if (folder / "tools" / "traceability.py").is_file():
            sys.path.insert(0, str(folder / "tools"))
            from traceability import Project
            return Project
    return None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load():
    """(project, plan, steps, configuration) or an error text."""
    project_class = trace_engine()
    if project_class is None:
        return "the toolkit's tools/traceability.py was not found above %s" % ROOT
    project = project_class(ROOT)
    plans = [p for p in project.of_type("plan") if p.front.get("kind") == "software-integration" and project.live(p)]
    plans.sort(key=lambda p: (p.status != "approved", p.id))
    if not plans:
        return "no plan of kind software-integration under plans/"
    config = yaml.safe_load((HERE / "integration.yaml").read_text(encoding="utf-8")) or {}
    return project, plans[0], project.integration_steps(plans[0]), config


def step_contents(project, config, steps, index):
    """What the build of a step consists of: (software files, delivered, doubles, problems)."""
    software, delivered, doubles, problems = [], [], [], []
    for component in project.integrated_up_to(steps, index):
        received = (config.get("delivered") or {}).get(component)
        if received:
            delivered.append({"component": component, "version": received["version"], "files": received["files"]})
            continue
        units = project.sources(component, "part_of", ["software-unit"])
        files = [str(f) for u in units for f in u.front.get("source_files") or [] if str(f).endswith(".c")]
        if not files:
            problems.append("%s has no unit with code and is not delivered as received" % component)
        software += files
    for entry in steps[index].get("doubles") or []:
        for component in project.leaves(entry):
            file = (config.get("doubles") or {}).get(component)
            if file:
                doubles.append({"component": component, "file": file})
            else:
                problems.append("no double is configured for %s" % component)
    return software, delivered, doubles, problems


def build(compiler, config, files, folder, name):
    """Compile one program from the given files. Returns (executable, exit code, compiler output)."""
    includes = [str(path) for path in config.get("include") or []]
    folder.mkdir(parents=True, exist_ok=True)
    if compiler["kind"] == "gnu":
        executable = folder / name
        command = [compiler["path"]] + unit.GNU_FLAGS + ["-I" + path for path in includes]
        command += files + ["-o", unit.relative(executable)]
        code, output = unit.run(command, cwd=str(ROOT))
    else:
        executable = folder / (name + ".exe")
        objects = folder / "obj"
        objects.mkdir(parents=True, exist_ok=True)
        arguments = unit.MSVC_FLAGS + ['/I"%s"' % path for path in includes]
        arguments += ['/Fo"%s/"' % unit.relative(objects), '/Fe"%s"' % unit.relative(executable)]
        arguments += ['"%s"' % path for path in files]
        code, output = unit.msvc(compiler["vcvars"], arguments)
    return executable, code, output


def run_program(executable, test_file, log_file, build_ok, build_output):
    """Run a built test program; the results per test case of the file, and the log written."""
    expected = ["%s-%s" % match for match in TEST_FUNCTION.findall(test_file.read_text(encoding="utf-8"))]
    log, verdicts = ["== build\n" + build_output], {}
    if not build_ok:
        log.append("== build failed, the test cases of this program count as failed\n")
    else:
        code, output = unit.run([str(executable)], cwd=str(ROOT), timeout=300)
        log.append("== run: exit code %d\n%s" % (code, output))
        for line in output.splitlines():
            match = VERDICT_LINE.match(line.strip())
            if match:
                verdicts[match.group(1)] = match.group(2)
    log_file.write_text("".join(log), encoding="utf-8", newline="\n")
    evidence = unit.relative(log_file)
    return [{"test": test, "verdict": "passed" if verdicts.get(test) == "PASS" and test in expected else "failed",
             "evidence": evidence} for test in sorted(set(expected) | set(verdicts))]


def main():
    wanted = sys.argv[sys.argv.index("--step") + 1] if "--step" in sys.argv[1:-1] else None
    loaded = load()
    if isinstance(loaded, str):
        print(loaded)
        return 2
    project, plan, steps, config = loaded
    compiler = unit.find_compiler()
    if compiler is None:
        print("no C compiler found: put cc, gcc or clang on PATH, or install Visual Studio with the C++ workload")
        return 2
    print("plan: %s (%s), compiler: %s" % (plan.id, plan.status, compiler["name"]))
    failed = False
    for index, step in enumerate(steps):
        name = str(step["name"])
        if wanted and name != wanted:
            continue
        folder = unit.BUILD / "integration" / name
        folder.mkdir(parents=True, exist_ok=True)
        software, delivered, doubles, problems = step_contents(project, config, steps, index)
        test_file = HERE / ("test_%s.c" % name)
        if problems or not test_file.is_file():
            print("step %-12s not built: %s" % (name, "; ".join(problems) or "no test program %s" % unit.relative(test_file)))
            failed = True
            continue
        files = software + [f for d in delivered for f in d["files"]] + [d["file"] for d in doubles]
        executable, code, output = build(compiler, config, files + [unit.relative(test_file)], folder, "test_" + name)
        built_at = now()
        (folder / "build.log").write_text(output, encoding="utf-8", newline="\n")
        manifest = {"executed_at": built_at, "tool": compiler["name"], "result": "succeeded" if code == 0 else "failed",
                    "files": software, "delivered": delivered, "doubles": doubles,
                    "evidence": unit.relative(folder / "build.log")}
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        results = run_program(executable, test_file, folder / "run.log", code == 0, output)
        report = {"compiler": compiler["name"], "executed_at": now(), "results": results}
        (folder / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        passed = sum(1 for r in results if r["verdict"] == "passed")
        print("step %-12s build %s, %d of %d passed  (%s)" % (name, manifest["result"], passed, len(results),
                                                             unit.relative(folder)))
        failed = failed or code != 0 or passed != len(results) or not results
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
