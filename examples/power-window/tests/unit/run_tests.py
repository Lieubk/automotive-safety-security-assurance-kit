#!/usr/bin/env python3
"""Build and run the unit tests of the power window example.

For every tests/unit/test_<Unit>.c the script builds one executable from the
test file and the unit source src/**/<Unit>.c, runs it and collects the verdict
lines it prints (`UT-0001 PASS` or `UT-0001 FAIL <file>:<line>`).

Compiler: `cc`, `gcc` or `clang` from PATH with
`-std=c99 -pedantic -Wall -Wextra -Werror`; otherwise, on Windows, the Visual
Studio compiler found through vswhere, with `/std:c11 /W4 /WX`. Warnings are
errors in both cases.

Output, all under build/ in the example root:
    <test>.exe / <test>         the test executable
    <test>.log                  compiler output and test output
    unit-test-results.json      {"compiler", "executed_at", "results": [{"test", "verdict", "evidence"}]}

A test case that appears in a test file but prints no PASS line counts as
failed, so a build error or a crash cannot hide a test case.

Usage:  python tests/unit/run_tests.py
Exit code 0 = every test case passed, 1 = at least one failed, 2 = nothing could be run.
Standard library only.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

UNIT_TESTS = Path(__file__).resolve().parent
ROOT = UNIT_TESTS.parent.parent
SOURCES = ROOT / "src"
HOST = UNIT_TESTS / "host"
BUILD = ROOT / "build"

TEST_FUNCTION = re.compile(r"\btest_UT_(\d{4})_\w+\s*\(\s*void\s*\)\s*\{")
VERDICT_LINE = re.compile(r"^(UT-\d{4}) (PASS|FAIL)\b")
GNU_FLAGS = ["-std=c99", "-pedantic", "-Wall", "-Wextra", "-Werror"]
MSVC_FLAGS = ["/nologo", "/std:c11", "/W4", "/WX"]


def run(command, **options):
    """Run a command and return (exit code, combined output)."""
    try:
        done = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, errors="replace", **options)
    except (OSError, subprocess.TimeoutExpired) as problem:
        return 1, "%s: %s\n" % (type(problem).__name__, problem)
    return done.returncode, done.stdout


def find_vcvars():
    """Path of vcvars64.bat of the latest Visual Studio installation, or None."""
    program_files = os.environ.get("ProgramFiles(x86)") or r"C:\Program Files (x86)"
    vswhere = Path(program_files) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    if not vswhere.is_file():
        return None
    code, output = run([str(vswhere), "-latest", "-property", "installationPath"])
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if code != 0 or not lines:
        return None
    vcvars = Path(lines[0]) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    return vcvars if vcvars.is_file() else None


def msvc(vcvars, arguments):
    """Run cl inside the Visual Studio build environment.

    The output of vcvars64.bat itself is discarded, so that the log holds
    compiler output only; if the environment cannot be set up, cl is not found
    and the build fails with that message.
    """
    command = 'call "%s" >nul 2>nul && cl %s' % (vcvars, " ".join(arguments))
    environment = dict(os.environ, VSCMD_START_DIR=str(ROOT))   # keeps vcvars from changing directory
    return run(command, shell=True, cwd=str(ROOT), env=environment)


def find_compiler():
    """Describe the compiler to use: {"kind", "name", ...}, or None when there is none."""
    for name in ("cc", "gcc", "clang"):
        path = shutil.which(name)
        if path:
            code, output = run([path, "--version"])
            version = output.splitlines()[0].strip() if code == 0 and output.strip() else name
            return {"kind": "gnu", "path": path, "name": "%s (%s)" % (version, " ".join(GNU_FLAGS))}
    if os.name == "nt":
        vcvars = find_vcvars()
        if vcvars:
            _, banner = msvc(vcvars, [])            # cl without arguments prints its version banner
            match = re.search(r"Version\s+([\d.]+)\s+for\s+(\S+)", banner)
            version = "Microsoft C/C++ %s %s" % match.groups() if match else "Microsoft C/C++"
            return {"kind": "msvc", "vcvars": vcvars, "name": "%s (cl %s)" % (version, " ".join(MSVC_FLAGS[1:]))}
    return None


def include_directories():
    """The host stand-in headers, the test support header and every source folder with a header."""
    folders = sorted({header.parent for header in SOURCES.rglob("*.h")})
    return [HOST, UNIT_TESTS] + folders


def relative(path):
    """Path relative to the example root with forward slashes, as passed to the compiler.

    The compiler runs in the example root. Relative paths keep the location of
    the working copy out of the logs and out of the FAIL lines (`__FILE__`).
    """
    return Path(path).relative_to(ROOT).as_posix()


def build(compiler, test_file, unit_file, name):
    """Compile one test executable. Returns (executable path, exit code, compiler output)."""
    includes = [relative(folder) for folder in include_directories()]
    sources = [relative(test_file), relative(unit_file)]
    if compiler["kind"] == "gnu":
        executable = BUILD / name
        command = [compiler["path"]] + GNU_FLAGS + ["-I" + folder for folder in includes]
        command += sources + ["-o", relative(executable)]
        code, output = run(command, cwd=str(ROOT))
    else:
        executable = BUILD / (name + ".exe")
        objects = BUILD / "obj" / name
        objects.mkdir(parents=True, exist_ok=True)
        arguments = MSVC_FLAGS + ['/I"%s"' % folder for folder in includes]
        arguments += ['/Fo"%s/"' % relative(objects), '/Fe"%s"' % relative(executable)]
        arguments += ['"%s"' % source for source in sources]
        code, output = msvc(compiler["vcvars"], arguments)
    return executable, code, output


def main():
    test_files = sorted(UNIT_TESTS.glob("test_*.c"))
    if not test_files:
        print("no test files in %s" % UNIT_TESTS)
        return 2
    compiler = find_compiler()
    if compiler is None:
        print("no C compiler found: put cc, gcc or clang on PATH, or install Visual Studio with the C++ workload")
        return 2
    print("compiler: %s" % compiler["name"])
    BUILD.mkdir(exist_ok=True)

    results = []
    for test_file in test_files:
        name = test_file.stem
        unit = name[len("test_"):]
        expected = ["UT-" + number for number in TEST_FUNCTION.findall(test_file.read_text(encoding="utf-8"))]
        log_file = BUILD / (name + ".log")
        evidence = log_file.relative_to(ROOT).as_posix()
        log = []

        unit_files = sorted(SOURCES.rglob(unit + ".c"))
        if len(unit_files) != 1:
            log.append("expected exactly one %s.c under %s, found %d\n" % (unit, SOURCES, len(unit_files)))
            code = 1
        else:
            executable, code, output = build(compiler, test_file, unit_files[0], name)
            log.append("== build: %s + %s\n%s" % (test_file.relative_to(ROOT).as_posix(),
                                                  unit_files[0].relative_to(ROOT).as_posix(), output))
        verdicts = {}
        if code != 0:
            log.append("== build failed, the test cases of this file count as failed\n")
        else:
            code, output = run([str(executable)], cwd=str(ROOT), timeout=120)
            log.append("== run: exit code %d\n%s" % (code, output))
            for line in output.splitlines():
                match = VERDICT_LINE.match(line.strip())
                if match:
                    verdicts[match.group(1)] = match.group(2)
        with open(str(log_file), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("".join(log))

        for test in sorted(set(expected) | set(verdicts)):
            passed = verdicts.get(test) == "PASS" and test in expected
            results.append({"test": test, "verdict": "passed" if passed else "failed", "evidence": evidence})
        passed_here = sum(1 for test in set(expected) | set(verdicts)
                          if verdicts.get(test) == "PASS" and test in expected)
        print("%-22s %d of %d passed  (%s)" % (name, passed_here, len(set(expected) | set(verdicts)), evidence))

    results.sort(key=lambda entry: entry["test"])
    report = {
        "compiler": compiler["name"],
        "executed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "results": results,
    }
    report_file = BUILD / "unit-test-results.json"
    with open(str(report_file), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")

    failed = [entry["test"] for entry in results if entry["verdict"] != "passed"]
    print("%d test cases executed: %d passed, %d failed" % (len(results), len(results) - len(failed), len(failed)))
    if failed:
        print("failed: %s" % ", ".join(failed))
    print("results: %s" % report_file.relative_to(ROOT).as_posix())
    return 1 if failed or not results else 0


if __name__ == "__main__":
    sys.exit(main())
