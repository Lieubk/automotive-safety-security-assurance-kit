"""Tests for the record tool (tools/record.py): what it writes and, above all, what it refuses.

They run the tool as a command against a copy of the worked example.

Run:  python -m unittest discover -s tools/tests -v
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "power-window"
CHECKLIST = ROOT / ".claude" / "docs" / "checklists" / "software-requirements.md"
REVIEWER = "T. Tester"


class RecordCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="recordtest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "p"
        shutil.copytree(str(EXAMPLE), str(self.project), ignore=shutil.ignore_patterns("build"))

    def record(self, *arguments):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "record.py"), "--project", str(self.project)]
                              + [str(a) for a in arguments], capture_output=True, text=True)
        return done.returncode, done.stdout

    def json_file(self, name, data):
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def all_checks(self, result="pass"):
        ids = re.findall(r"(?m)^\|\s*([A-Z]{2,5}-\d+)\s*\|", CHECKLIST.read_text(encoding="utf-8"))
        return self.json_file("checks.json", [{"check": i, "result": result, "note": "test"} for i in ids])

    def front(self, relative):
        text = (self.project / relative).read_text(encoding="utf-8")
        return yaml.safe_load(text.split("---")[1])

    def records(self, folder, prefix=""):
        return sorted(p.name for p in (self.project / folder).glob(prefix + "*.md"))


class Review(RecordCase):
    def review(self, *extra, checklist="software-requirements v2", verdict="approved", ids=("SWR-0001",)):
        return self.record("review", "--checklist", checklist, "--reviewer", REVIEWER, "--verdict", verdict, *extra, *ids)

    def test_approval_under_a_toolkit_checklist_needs_a_result_for_every_check(self):
        code, out = self.review()
        self.assertEqual(code, 1)
        self.assertIn("needs a result for every check", out)
        self.assertIn("no record written", out)

    def test_approval_with_all_checks_is_recorded(self):
        before = self.records("records/reviews")
        code, out = self.review("--checks", self.all_checks())
        self.assertEqual(code, 0, out)
        new = [name for name in self.records("records/reviews") if name not in before]
        record = self.front("records/reviews/" + new[0])
        self.assertEqual((record["verdict"], record["checklist_source"], record["reviewers"]), ("approved", "toolkit", [REVIEWER]))
        self.assertEqual(record["subject"][0]["item"], "SWR-0001")

    def test_the_title_of_the_checklist_is_accepted_as_citation(self):
        code, out = self.review("--checks", self.all_checks(), checklist="Software requirements review v2")
        self.assertEqual(code, 0, out)

    def test_unknown_checklist_is_refused(self):
        code, out = self.review("--checks", self.all_checks(), checklist="my own list v1")
        self.assertEqual(code, 1)
        self.assertIn("cites no checklist of this toolkit", out)

    def test_the_record_keeps_the_hash_of_the_checklist_applied(self):
        code, out = self.review("--checks", self.all_checks())
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertRegex(record["checklist_hash"], r"^[0-9a-f]{12}$")

    def test_wrong_version_is_refused(self):
        code, out = self.review("--checks", self.all_checks(), checklist="software-requirements v9")
        self.assertEqual(code, 1)
        self.assertIn("the citation says v9", out)

    def test_external_criteria_need_no_check_results(self):
        code, out = self.review("--external-criteria", checklist="customer review procedure, edition 3")
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertEqual(record["checklist_source"], "external")

    def test_a_check_that_was_not_assessed_blocks_approval(self):
        code, out = self.review("--checks", self.all_checks("not-assessed"))
        self.assertEqual(code, 1)
        self.assertIn("not assessed", out)

    def test_not_applicable_needs_its_reason(self):
        checks = json.loads(self.all_checks().read_text(encoding="utf-8"))
        checks[0] = {"check": checks[0]["check"], "result": "not-applicable"}
        code, out = self.review("--checks", self.json_file("c.json", checks))
        self.assertEqual(code, 1)
        self.assertIn("the note must say why", out)

    def test_open_finding_blocks_approval_and_allows_rework(self):
        findings = self.json_file("f.json", [{"id": "F1", "item": "SWR-0001", "text": "x", "severity": "major", "state": "open"}])
        code, out = self.review("--checks", self.all_checks(), "--findings", findings)
        self.assertEqual(code, 1)
        self.assertIn("while a finding is open", out)
        code, out = self.review("--findings", findings, verdict="rework")
        self.assertEqual(code, 0, out)

    def test_no_approval_above_a_draft(self):
        parent_id = self.front("spec/software/requirements/SWR-0001.md")["links"]["derived_from"][0]
        parent = next(self.project.glob("spec/**/%s.md" % parent_id))
        parent.write_text(parent.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1), encoding="utf-8")
        code, out = self.review("--checks", self.all_checks())
        self.assertEqual(code, 1)
        self.assertIn("cannot be approved while %s" % parent_id, out)

    def test_accountable_check_answered_with_a_finding_blocks_approval(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        accountable = re.search(r"(?m)^\|\s*([A-Z]{2,5}-\d+)\s*\|.*\|\s*accountable\s*\|\s*$", text).group(1)
        checks = json.loads(self.all_checks().read_text(encoding="utf-8"))
        for entry in checks:
            if entry["check"] == accountable:
                entry["result"] = "finding"
        closed = self.json_file("f.json", [{"id": "F1", "item": "SWR-0001", "text": "not agreed", "severity": "major",
                                            "state": "closed"}])
        code, out = self.review("--checks", self.json_file("c.json", checks), "--findings", closed)
        self.assertEqual(code, 1)
        self.assertIn("cannot be closed by decision", out)

    def change(self, relative, old, new):
        path = self.project / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_reconfirmation_of_unchanged_items_after_a_change_upstream(self):
        parent_id = self.front("spec/software/requirements/SWR-0001.md")["links"]["derived_from"][0]
        parent = next(self.project.glob("spec/**/%s.md" % parent_id)).relative_to(self.project).as_posix()
        self.change(parent, "title: ", "title: Changed - ")
        code, out = self.record("review", "--reconfirm", "--reviewer", REVIEWER, "--verdict", "approved", "SWR-0001")
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertEqual(record["checklist_source"], "reconfirmation")
        self.assertIn(parent_id, [r["item"] for r in record["references"]])

    def test_reconfirmation_is_refused_for_an_item_that_changed_itself(self):
        self.change("spec/software/requirements/SWR-0001.md", "title: ", "title: Changed - ")
        code, out = self.record("review", "--reconfirm", "--reviewer", REVIEWER, "--verdict", "approved", "SWR-0001")
        self.assertEqual(code, 1)
        self.assertIn("nothing to reconfirm", out)

    def test_reconfirmation_keeps_the_code_review_of_an_unchanged_unit(self):
        code, out = self.record("review", "--reconfirm", "--reviewer", REVIEWER, "--verdict", "approved", "UNT-0003")
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertEqual(sorted(s["file"] for s in record["sources"]), ["src/antipinch/AntiPinch.c", "src/antipinch/AntiPinch.h"])

    def test_reconfirmation_does_not_hide_code_that_changed_after_its_review(self):
        self.change("src/antipinch/AntiPinch.c", "\n", "\n/* changed after the review */\n")
        code, out = self.record("review", "--reconfirm", "--reviewer", REVIEWER, "--verdict", "approved", "UNT-0003")
        self.assertEqual(code, 0, out)
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "traceability.py"), "--project", str(self.project),
                               "check"], capture_output=True, text=True)
        suspect = [line for line in done.stdout.splitlines() if "SUSPECT" in line and "UNT-0003" in line]
        self.assertTrue(suspect, done.stdout)
        self.assertIn("AntiPinch.c changed after review", suspect[0])

    def test_reconfirmation_is_not_a_review_of_code(self):
        code, out = self.record("review", "--reconfirm", "--item-under-test", "abc123", "--reviewer", REVIEWER,
                                "--verdict", "approved", "UNT-0003")
        self.assertEqual(code, 1)
        self.assertIn("cannot be combined", out)

    def test_a_finding_on_an_item_that_is_not_a_subject_is_refused(self):
        findings = self.json_file("f.json", [{"id": "F1", "item": "SWR-0002", "text": "x", "severity": "minor",
                                              "state": "open"}])
        code, out = self.review("--findings", findings, verdict="rework")
        self.assertEqual(code, 1)
        self.assertIn("not a subject of this review", out)

    def test_a_whole_section_can_be_not_applicable_in_one_entry(self):
        text = CHECKLIST.read_text(encoding="utf-8")
        set_part = text.split("## The set")[1]
        ids = re.findall(r"(?m)^\|\s*([A-Z]{2,5}-\d+)\s*\|", set_part)
        checks = [c for c in json.loads(self.all_checks().read_text(encoding="utf-8")) if c["check"] not in ids]
        checks.append({"section": "The set", "result": "not-applicable", "note": "test of a single item"})
        code, out = self.review("--checks", self.json_file("c.json", checks))
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        given = {c["check"]: c for c in record["checks"]}
        self.assertTrue(all(given[i]["result"] == "not-applicable" for i in ids))
        checks[-1]["result"] = "pass"
        code, out = self.review("--checks", self.json_file("c2.json", checks))
        self.assertEqual(code, 1)
        self.assertIn("only not-applicable", out)

    def test_reconfirmation_names_the_reviews_it_rests_on(self):
        code, out = self.record("review", "--reconfirm", "--reviewer", REVIEWER, "--verdict", "approved", "SWR-0001")
        self.assertEqual(code, 0, out)
        record = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertTrue(record["rests_on"] and all(r.startswith("REV-") for r in record["rests_on"]))

    def test_the_help_shows_the_input_formats(self):
        code, out = self.record("--help")
        self.assertEqual(code, 0)
        self.assertIn("Checks FILE is JSON", out)

    def test_code_is_recorded_only_when_the_revision_is_named(self):
        self.review("--external-criteria", checklist="x", ids=("UNT-0003",))
        without = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.review("--external-criteria", "--item-under-test", "abc123", checklist="x", ids=("UNT-0003",))
        named = self.front("records/reviews/" + self.records("records/reviews")[-1])
        self.assertNotIn("sources", without)
        self.assertEqual(sorted(s["file"] for s in named["sources"]), ["src/antipinch/AntiPinch.c", "src/antipinch/AntiPinch.h"])


class Runs(RecordCase):
    def results(self, **extra):
        tests = [p.stem for p in (self.project / "verification/unit").glob("UT-*.md")]
        data = {"executed_at": "2026-06-01T10:00:00+00:00", "compiler": "test compiler",
                "results": [{"test": t, "verdict": "passed"} for t in sorted(tests)]}
        data.update(extra)
        return self.json_file("results.json", data)

    def run_record(self, *extra, **data):
        return self.record("test-run", "--level", "unit", "--results", self.results(**data), "--item-under-test", "abc123",
                           "--environment", "host", *extra)

    def test_run_stores_source_hashes(self):
        code, out = self.run_record()
        self.assertEqual(code, 0, out)
        record = self.front("verification/runs/" + self.records("verification/runs", "RUN-")[-1])
        self.assertIn("src/antipinch/AntiPinch.c", [s["file"] for s in record["sources"]])
        self.assertIn("tests/unit/test_AntiPinch.c", [s["file"] for s in record["sources"]])

    def test_approved_test_case_missing_from_the_results_stops_the_record(self):
        data = json.loads(self.results().read_text(encoding="utf-8"))
        data["results"].pop()
        code, out = self.record("test-run", "--level", "unit", "--results", self.json_file("r.json", data),
                                "--item-under-test", "abc123", "--environment", "host")
        self.assertEqual(code, 1)
        self.assertIn("has no result in the file", out)

    def test_deviation_is_kept_with_the_coverage_entry(self):
        coverage = [{"file": "src/antipinch/AntiPinch.c", "statement_percent": 100.0, "branch_percent": 96.0}]
        code, out = self.run_record("--deviation", "UNT-0003=defensive default branch, accepted by the software lead",
                                    coverage=coverage)
        self.assertEqual(code, 0, out)
        record = self.front("verification/runs/" + self.records("verification/runs", "RUN-")[-1])
        self.assertEqual(record["coverage"][0]["deviation"], "defensive default branch, accepted by the software lead")

    def test_deviation_for_a_unit_without_coverage_entry_is_refused(self):
        code, out = self.run_record("--deviation", "UNT-0001=reason", coverage=[])
        self.assertEqual(code, 1)
        self.assertIn("no entry for: UNT-0001", out)

    def test_analysis_deviation_that_matches_no_finding_stops_the_record(self):
        data = {"tool": "t", "executed_at": "2026-06-01T10:00:00+00:00",
                "files": ["src/antipinch/AntiPinch.c", "src/windowpos/HallCapture.c", "src/windowpos/WindowPos.c"],
                "findings": [], "deviations": [{"file": "src/antipinch/AntiPinch.c", "line": 1, "rule": "R1",
                                                "justification": "j", "accepted_by": "a"}]}
        code, out = self.record("analysis-run", "--results", self.json_file("a.json", data), "--item-under-test", "abc123")
        self.assertEqual(code, 1)
        self.assertIn("matches no finding", out)


class Integration(RecordCase):
    """Build records and runs on integrated software, against the integration strategy of the example
    (PLN-0004: step detection with CMP-0003 and CMP-0004, step application adding CMP-0002 and CMP-0005)."""

    DETECTION = ["SIT-0001", "SIT-0002", "SIT-0003"]
    DOUBLE = "tests/integration/doubles/Platform_double.c"

    def build(self, step="detection", **manifest):
        """Record a build; returns (exit code, output, the ID of the record written or None)."""
        data = {"executed_at": "2026-06-01T09:00:00+00:00", "tool": "gcc 13.2", "result": "succeeded",
                "files": ["src/windowpos/HallCapture.c", "src/windowpos/WindowPos.c", "src/antipinch/AntiPinch.c"],
                "doubles": [{"component": "CMP-0006", "file": self.DOUBLE}]}
        data.update(manifest)
        code, out = self.record("build", "--step", step, "--manifest", self.json_file("manifest.json", data),
                                "--item-under-test", "abc123")
        found = re.search(r"verification/builds/(BLD-\d+)\.md", out)
        return code, out, found.group(1) if found else None

    def run_on(self, build, tests, level="software-integration", commit="abc123"):
        data = {"executed_at": "2026-06-01T10:00:00+00:00", "results": [{"test": t, "verdict": "passed"} for t in tests]}
        extra = ["--build", build] if build else []
        return self.record("test-run", "--level", level, "--results", self.json_file("r.json", data),
                           "--item-under-test", commit, "--environment", "host", *extra)

    def test_build_groups_the_units_by_component_and_keeps_the_doubles(self):
        code, out, build = self.build()
        self.assertEqual(code, 0, out)
        record = self.front("verification/builds/%s.md" % build)
        self.assertEqual(record["contents"], [{"component": "CMP-0003", "units": ["UNT-0001", "UNT-0002"]},
                                              {"component": "CMP-0004", "units": ["UNT-0003"]}])
        self.assertEqual(record["doubles"], [{"component": "CMP-0006", "file": self.DOUBLE}])
        self.assertIn(self.DOUBLE, [s["file"] for s in record["sources"]])

    def test_build_of_a_step_the_plan_does_not_have_is_refused(self):
        code, out, _ = self.build(step="everything")
        self.assertEqual(code, 1)
        self.assertIn("has no step 'everything'", out)

    def test_built_file_that_belongs_to_no_unit_is_refused(self):
        code, out, _ = self.build(files=["src/windowpos/HallCapture.c", self.DOUBLE])
        self.assertEqual(code, 1)
        self.assertIn("belongs to no software unit", out)

    def test_component_integrated_as_received_needs_its_version(self):
        code, out, _ = self.build(step="application", delivered=[{"component": "CMP-0005"}])
        self.assertEqual(code, 1)
        self.assertIn("needs the version", out)

    def test_build_reports_what_the_step_should_contain_but_does_not(self):
        code, out, _ = self.build(step="application")
        self.assertEqual(code, 0, out)
        self.assertIn("not in this build, although the step integrates them: CMP-0002, CMP-0005", out)

    def test_integration_run_needs_a_build(self):
        code, out = self.run_on(None, self.DETECTION)
        self.assertEqual(code, 1)
        self.assertIn("needs --build", out)

    def test_integration_run_records_the_build_and_the_cases_of_its_step(self):
        _, _, build = self.build()
        code, out = self.run_on(build, self.DETECTION)
        self.assertEqual(code, 0, out)
        record = self.front("verification/runs/" + self.records("verification/runs", "RUN-")[-1])
        self.assertEqual(record["build"], build)

    def test_integration_run_needs_every_case_of_its_step(self):
        _, _, build = self.build()
        code, out = self.run_on(build, self.DETECTION[:2])
        self.assertEqual(code, 1)
        self.assertIn("approved test case SIT-0003 has no result", out)

    def test_case_of_a_later_step_cannot_run_on_an_earlier_build(self):
        _, _, build = self.build()
        code, out = self.run_on(build, self.DETECTION + ["SIT-0004"])
        self.assertEqual(code, 1)
        self.assertIn("SIT-0004 belongs to step 'application'", out)

    def test_run_on_a_build_of_another_commit_is_refused(self):
        _, _, build = self.build()
        code, out = self.run_on(build, self.DETECTION, commit="def456")
        self.assertEqual(code, 1)
        self.assertIn("was built from abc123", out)

    def test_junit_report_from_a_test_bench(self):
        _, _, build = self.build(step="application", executed_at="2026-06-01T09:30:00+00:00")
        cases = ['<testcase classname="Window" name="SQT-0001 opening"><failure message="late"/></testcase>',
                 '<testcase classname="Window" name="SQT-0002 reference"><skipped message="switch defect on bench"/>'
                 '</testcase>']
        cases += ['<testcase classname="Window" name="SQT-%04d"/>' % n for n in range(3, 10)]
        report = Path(self.tmp.name) / "bench.xml"
        report.write_text('<testsuites><testsuite name="bench" timestamp="2026-06-02T08:00:00">%s</testsuite>'
                          '</testsuites>' % "".join(cases), encoding="utf-8")
        code, out = self.record("test-run", "--level", "software-qualification", "--results", report,
                                "--item-under-test", "abc123", "--environment", "bench 3", "--build", build,
                                "--selection", "all")
        self.assertEqual(code, 0, out)
        record = self.front("verification/runs/" + self.records("verification/runs", "RUN-")[-1])
        self.assertEqual(record["executed_at"], "2026-06-02T08:00:00")
        verdicts = {r["test"]: r for r in record["results"]}
        self.assertEqual((verdicts["SQT-0001"]["verdict"], verdicts["SQT-0001"]["reason"]), ("failed", "late"))
        self.assertEqual((verdicts["SQT-0002"]["verdict"], verdicts["SQT-0002"]["reason"]),
                         ("not-run", "switch defect on bench"))
        self.assertEqual(verdicts["SQT-0009"]["verdict"], "passed")
        self.assertTrue(verdicts["SQT-0001"]["evidence"].startswith("verification/evidence/"))

    def test_qualification_on_a_build_of_an_earlier_step_is_refused(self):
        _, _, build = self.build()
        code, out = self.run_on(build, [], level="software-qualification")
        self.assertEqual(code, 1)
        self.assertIn("qualified on a build of the last step", out)


class QualityChecks(RecordCase):
    """Checks against the quality assurance plan of the example (PLN-0007)."""

    def check(self, *extra, result="conforms", findings=None, subject=("SWR-0001",), kind="work-product"):
        summary = Path(self.tmp.name) / "summary.txt"
        summary.write_text("Looked at the requirement and its review.", encoding="utf-8")
        arguments = ["quality-check", "--kind", kind, "--criteria", "software-requirements v2", "--checked-by",
                     "Q. Engineer", "--result", result, "--summary", summary, "--checked-at", "2026-06-01"]
        for s in subject:
            arguments += ["--subject", s]
        if findings is not None:
            arguments += ["--findings", self.json_file("findings.json", findings)]
        return self.record(*arguments, *extra)

    def test_a_check_needs_an_approved_quality_assurance_plan(self):
        plan = self.project / "plans" / "PLN-0007.md"
        plan.write_text(plan.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1), encoding="utf-8")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("no approved quality-assurance plan", out)

    def test_a_work_product_check_records_the_approving_review(self):
        code, out = self.check("--check", "work product sample")
        self.assertEqual(code, 0, out)
        record = self.front("records/quality/" + self.records("records/quality", "QAR-")[-1])
        self.assertEqual(record["facts"][0]["item"], "SWR-0001")
        self.assertTrue(record["facts"][0]["approved_by"].startswith("REV-"))

    def test_a_finding_needs_an_action_that_exists(self):
        code, out = self.check(result="conforms-with-findings",
                               findings=[{"id": "F1", "text": "Unclear.", "action": "CA-0099"}])
        self.assertEqual(code, 1)
        self.assertIn("write the action first", out)

    def test_the_result_has_to_agree_with_the_findings(self):
        code, out = self.check(result="does-not-conform")
        self.assertEqual(code, 1)
        self.assertIn("needs at least one finding", out)

    def test_a_process_check_records_the_evidence_per_practice(self):
        code, out = self.check(kind="process", subject=("SWE.1",))
        self.assertEqual(code, 0, out)
        record = self.front("records/quality/" + self.records("records/quality", "QAR-")[-1])
        self.assertEqual(record["facts"][0]["process"], "SWE.1")
        self.assertEqual(record["facts"][0]["practices"][0]["practice"], "SWE.1.BP1")

    def test_a_report_covers_the_checks_since_the_last_one(self):
        self.check()
        summary = Path(self.tmp.name) / "report.txt"
        summary.write_text("One check, conforming.", encoding="utf-8")
        code, out = self.record("quality-report", "--checked-by", "Q. Engineer", "--result", "conforms",
                                "--summary", summary, "--as-of", "2026-06-30")
        self.assertEqual(code, 0, out)
        names = self.records("records/quality", "QAR-")
        report = self.front("records/quality/" + names[-1])
        self.assertEqual(report["kind"], "summary")
        self.assertEqual(report["subject"], [names[-2][:-3]])


class SystemBuilds(RecordCase):
    """A system integration step added to the copy of the example: its software element and its hardware."""

    def setUp(self):
        super().setUp()
        front = {"id": "PLN-0098", "type": "plan", "title": "System integration strategy", "status": "approved",
                 "kind": "system-integration", "integration_steps": [{"name": "door", "components": ["SYE-0001", "SYE-0002"]}]}
        (self.project / "plans" / "PLN-0098.md").write_text(
            "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n## Scope\n\nx\n", encoding="utf-8")

    def build(self, elements):
        data = {"executed_at": "2026-06-20T09:00:00+00:00", "tool": "door bench 2", "result": "succeeded",
                "elements": elements, "doubles": [{"element": "SYE-0002", "description": "not used"}][:0]}
        return self.record("build", "--level", "system", "--step", "door", "--manifest",
                           self.json_file("system.json", data), "--item-under-test", "door module B2")

    def test_a_system_build_records_the_versions_and_the_software_build(self):
        code, out = self.build([{"element": "SYE-0001", "version": "r1.0-rc1", "build": "BLD-0002"},
                                {"element": "SYE-0002", "version": "B2 sample"}])
        self.assertEqual(code, 0, out)
        record = self.front("verification/builds/" + self.records("verification/builds", "BLD-")[-1])
        self.assertEqual(record["level"], "system")
        self.assertEqual(record["contents"][0], {"component": "SYE-0001", "delivered": "r1.0-rc1", "build": "BLD-0002"})

    def test_a_system_build_names_system_elements_with_their_versions(self):
        code, out = self.build([{"element": "CMP-0003", "version": "x"}, {"element": "SYE-0002"}])
        self.assertEqual(code, 1)
        self.assertIn("CMP-0003, which is not a system element", out)
        self.assertIn("SYE-0002 needs the version", out)

    def test_a_software_run_cannot_name_a_system_build(self):
        self.build([{"element": "SYE-0001", "version": "r1.0-rc1", "build": "BLD-0002"},
                    {"element": "SYE-0002", "version": "B2 sample"}])
        system = self.records("verification/builds", "BLD-")[-1][:-3]
        data = {"executed_at": "2026-06-20T10:00:00+00:00", "results": [{"test": "SIT-0001", "verdict": "passed"}]}
        code, out = self.record("test-run", "--level", "software-integration", "--results", self.json_file("r.json", data),
                                "--item-under-test", "door module B2", "--environment", "bench", "--build", system)
        self.assertEqual(code, 1)
        self.assertIn("a run of level software-integration needs a software build", out)


class SupplierReviews(RecordCase):
    def setUp(self):
        super().setUp()
        front = {"id": "SAG-0001", "type": "supplier-agreement", "title": "Platform team", "status": "approved",
                 "supplier": "window lifter platform team, order 17", "components": ["CMP-0002"],
                 "exchanges": [{"name": "release", "direction": "from-supplier", "content": "WindowCmd source"}],
                 "meetings": [{"name": "progress call", "kind": "progress", "cadence": 7}]}
        path = self.project / "plans" / "suppliers" / "SAG-0001.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n## Joint processes\n\nx\n",
                        encoding="utf-8")

    def review(self, held_at, items, agreement="SAG-0001"):
        minutes = Path(self.tmp.name) / "minutes.txt"
        minutes.write_text("Schedule on track; release 3.2.1 due.", encoding="utf-8")
        return self.record("supplier-review", "--agreement", agreement, "--kind", "progress", "--held-at", held_at,
                           "--participant", "Project lead", "--participant", "Platform lead", "--minutes", minutes,
                           "--open-items", self.json_file("items.json", items))

    def overview(self, as_of):
        sys.path.insert(0, str(ROOT / "tools"))
        from traceability import Project, suppliers, as_date
        return suppliers(Project(self.project), as_date(as_of))["agreements"][0]

    def test_an_open_item_stays_open_until_a_later_review_closes_it(self):
        code, out = self.review("2026-06-01", [{"id": "A1", "text": "date of 3.2.1", "owner": "Platform lead",
                                                "due": "2026-06-05", "state": "open"}])
        self.assertEqual(code, 0, out)
        first = self.records("records/suppliers", "SRV-")[-1][:-3]
        status = self.overview("2026-06-10")
        self.assertEqual([i["item"] for i in status["open_items"]], ["%s#A1" % first])
        self.assertEqual(status["open_items"][0]["overdue_days"], 5)
        self.assertEqual(status["meetings"][0]["overdue_days"], 2)
        self.review("2026-06-08", [{"id": "A1", "text": "3.2.1 on 2026-06-15", "owner": "Platform lead",
                                    "state": "closed", "closes": "%s#A1" % first}])
        self.assertEqual(self.overview("2026-06-10")["open_items"], [])

    def test_a_review_needs_a_supplier_agreement(self):
        code, out = self.review("2026-06-01", [], agreement="PLN-0001")
        self.assertEqual(code, 1)
        self.assertIn("no live supplier agreement", out)


class SelfAssessments(RecordCase):
    """Ratings of SUP.9 in the example, where every practice shows evidence present."""

    def ratings(self, **changes):
        practices = [{"practice": "SUP.9.BP%d" % n, "rating": "F"} for n in range(1, 10)]
        for entry in practices:
            entry.update(changes.get(entry["practice"].replace(".", "_"), {}))
        return self.json_file("ratings.json", {"practices": practices})

    def assess(self, ratings, *extra):
        summary = Path(self.tmp.name) / "summary.txt"
        summary.write_text("Strong tracking; trends from one problem only.", encoding="utf-8")
        return self.record("self-assessment", "--ratings", ratings, "--assessor", "A. Assessor", "--process", "SUP.9",
                           "--summary", summary, "--as-of", "2026-06-25", *extra)

    def test_ratings_that_agree_with_the_observations_are_recorded(self):
        code, out = self.assess(self.ratings())
        self.assertEqual(code, 0, out)
        record = self.front("records/assessments/" + self.records("records/assessments", "SAS-")[-1])
        self.assertEqual(len(record["ratings"]), 9)
        self.assertEqual(record["observations"][0], {"practice": "SUP.9.BP1", "state": "evidence present"})
        self.assertEqual(record["consistency"], [])

    def test_every_practice_needs_a_rating(self):
        path = self.json_file("ratings.json", {"practices": [{"practice": "SUP.9.BP1", "rating": "F"}]})
        code, out = self.assess(path, "--check-only")
        self.assertEqual(code, 1)
        self.assertIn("SUP.9.BP2 has no rating", out)

    def test_a_rating_below_the_observation_needs_its_reason(self):
        code, out = self.assess(self.ratings(SUP_9_BP4={"rating": "P"}))
        self.assertEqual(code, 1)
        self.assertIn("SUP.9.BP4 rated P while the toolkit observes 'evidence present': give the reason", out)
        code, out = self.assess(self.ratings(SUP_9_BP4={"rating": "P", "note": "the cause restates the symptom"},
                                             SUP_9_BP5={"note": "no urgent problem: nothing rested on the diagnosis"}))
        self.assertEqual(code, 0, out)
        record = self.front("records/assessments/" + self.records("records/assessments", "SAS-")[-1])
        kinds = sorted(f["kind"] for f in record["consistency"])
        self.assertEqual(kinds, ["observation", "recommendation", "recommendation", "rule"])

    def test_at_level_2_every_generic_practice_needs_a_rating(self):
        code, out = self.assess(self.ratings(), "--level", "2", "--check-only")
        self.assertEqual(code, 1)
        self.assertIn("SUP.9 GP 2.1.1 has no rating", out)
        generic = [{"process": "SUP.9", "practice": "GP 2.%d.%d" % pair, "rating": "P", "note": "rehearsal"}
                   for pair in [(1, n) for n in range(1, 8)] + [(2, n) for n in range(1, 5)]]
        practices = json.loads(Path(self.ratings()).read_text(encoding="utf-8"))["practices"]
        path = self.json_file("level2.json", {"practices": practices, "generic": generic})
        code, out = self.assess(path, "--level", "2")
        self.assertEqual(code, 0, out)
        record = self.front("records/assessments/" + self.records("records/assessments", "SAS-")[-1])
        self.assertEqual(len(record["generic_observations"]), 11)

    def test_a_rating_above_a_practice_it_depends_on_by_rule_needs_its_reason(self):
        # SUP.9.BP3 depends on SUP.9.BP1 by a rule of the catalog
        low = {"rating": "P", "note": "the strategy names no status model"}
        code, out = self.assess(self.ratings(SUP_9_BP1=low), "--check-only")
        self.assertEqual(code, 1)
        self.assertIn("SUP.9.BP3 rated F, above SUP.9.BP1, which it depends on (rule), rated P: give the reason", out)


class ProblemTrends(RecordCase):
    def add_problem(self):
        front = {"id": "PRB-0099", "type": "problem-report", "title": "Late stop", "status": "open", "severity": "major",
                 "reported_by": "Tester", "reported_at": "2026-06-01", "detected_by": "qualification-test",
                 "found_in": "abc123"}
        path = self.project / "records" / "problems" / "PRB-0099.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n## Description\n\nx\n", encoding="utf-8")

    def test_a_trend_report_needs_the_analysts_assessment(self):
        code, out = self.record("problem-trends", "--reported-by", "S. Lead", "--assessment",
                                str(Path(self.tmp.name) / "none.txt"))
        self.assertEqual(code, 1)
        self.assertIn("analyst's reading", out)

    def test_a_trend_report_carries_the_figures_and_the_assessment(self):
        self.add_problem()
        assessment = Path(self.tmp.name) / "assessment.txt"
        assessment.write_text("One problem, from qualification; no trend yet.", encoding="utf-8")
        code, out = self.record("problem-trends", "--reported-by", "S. Lead", "--assessment", assessment,
                                "--as-of", "2026-06-15")
        self.assertEqual(code, 0, out)
        folder = self.project / "records" / "problem-trends"
        record = self.front("records/problem-trends/" + sorted(p.name for p in folder.glob("PTR-*.md"))[-1])
        self.assertEqual(record["problems"], [{"item": "PRB-0099", "state": "open", "severity": "major",
                                               "origin": None, "detected_by": "qualification-test", "age_days": 14}])
        self.assertEqual(record["figures"]["unresolved_by_age"]["8 to 30 days"], 1)


class StatusReports(RecordCase):
    def test_a_report_needs_the_reporters_assessment(self):
        code, out = self.record("status-report", "--reported-by", "P. Lead", "--assessment", str(Path(self.tmp.name) / "none.txt"))
        self.assertEqual(code, 1)
        self.assertIn("reporter's reading", out)

    def test_a_report_carries_the_figures_and_the_assessment(self):
        package = self.project / "plans" / "work-packages" / "WP-0099.md"
        package.parent.mkdir(parents=True, exist_ok=True)
        package.write_text("---\nid: WP-0099\ntype: work-package\ntitle: Feature\nstatus: draft\nowner: Project lead\n"
                           "category: engineering\nplanned_finish: '2026-01-31'\nlinks:\n  delivers: [SWR-0001]\n---\n\n"
                           "## Description\n\nThe work.\n", encoding="utf-8")
        text = Path(self.tmp.name) / "assessment.txt"
        text.write_text("On track except the feature package, which is late by two weeks.", encoding="utf-8")
        code, out = self.record("status-report", "--reported-by", "P. Lead", "--assessment", text, "--as-of", "2026-02-15")
        self.assertEqual(code, 0, out)
        newest = self.records("records/status", "PSR-")[-1]
        record_text = (self.project / "records" / "status" / newest).read_text(encoding="utf-8")
        record = yaml.safe_load(record_text.split("---")[1])
        entry = next(p for p in record["work_packages"] if p["item"] == "WP-0099")
        self.assertTrue(entry["late"])
        self.assertIn("## Assessment", record_text)


class CybersecurityRecords(unittest.TestCase):
    """The case and the assessment, on the engine's TARA fixture."""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_traceability import CS_CONFIG, Fixture, cs_items
        self.fixture = Fixture(cs_items(), config=CS_CONFIG)
        self.addCleanup(self.fixture.tmp.cleanup)
        self.project = self.fixture.root
        self.text = self.project / "argument.md"
        self.text.write_text("The goal covers the only threat above risk 1; see the TARA.", encoding="utf-8")

    def record(self, *arguments):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "record.py"), "--project", str(self.project)]
                              + [str(a) for a in arguments], capture_output=True, text=True)
        return done.returncode, done.stdout

    def front(self, relative):
        return yaml.safe_load((self.project / relative).read_text(encoding="utf-8").split("---")[1])

    def test_the_case_lists_the_evidence_per_work_product(self):
        code, out = self.record("cybersecurity-case", "--prepared-by", "C. Lead", "--argument", self.text)
        self.assertEqual(code, 0, out)
        case = self.front("records/cybersecurity/CSE-0001.md")
        self.assertEqual(case["clauses"], ["6", "9", "15"])
        products = {w["work_product"]: w for w in case["work_products"]}
        self.assertEqual([i["item"] for i in products["WP-09-03"]["items"]], ["CSG-0001"])
        self.assertEqual([i["item"] for i in products["WP-06-01"]["items"]], ["PLN-0009"])
        self.assertEqual(products["WP-06-03"]["items"], [])                  # no assessment yet
        self.assertIn("## Argument", (self.project / "records/cybersecurity/CSE-0001.md").read_text(encoding="utf-8"))

    def test_the_assessment_is_independent_of_the_case(self):
        self.record("cybersecurity-case", "--prepared-by", "C. Lead", "--argument", self.text)
        base = ["cybersecurity-assessment", "--case", "CSE-0001", "--independence", "other department",
                "--report", self.text]
        code, out = self.record(*base, "--assessor", "C. Lead", "--judgement", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("an assessment is independent", out)
        code, out = self.record(*base, "--assessor", "I. Assessor", "--judgement", "conditionally-accepted")
        self.assertEqual(code, 1)
        self.assertIn("names its conditions", out)
        code, out = self.record(*base, "--assessor", "I. Assessor", "--judgement", "conditionally-accepted",
                                "--conditions", "authentication tested on the bench before SOP")
        self.assertEqual(code, 0, out)
        sys.path.insert(0, str(ROOT / "tools"))
        from traceability import Project
        findings = [f for f in Project(self.project).check() if f["item"] == "CSA-0001"]
        self.assertEqual(findings, [])


class Baselines(RecordCase):
    def test_baseline_lists_approved_engineering_items_only(self):
        code, out = self.record("baseline", "--tag", "design-1", "--purpose", "design freeze")
        self.assertEqual(code, 0, out)
        record = self.front("records/baselines/BL-0001.md")
        listed = {entry["item"] for entry in record["items"]}
        self.assertIn("SWR-0001", listed)
        self.assertFalse({i for i in listed if i.startswith(("REV-", "RUN-", "SAR-"))})
        self.assertTrue(all(entry["status"] == "approved" for entry in record["items"]))

    def test_baseline_is_refused_while_the_check_reports_errors(self):
        (self.project / "verification/unit/UT-0001.md").unlink()        # leaves broken references behind
        code, out = self.record("baseline", "--tag", "design-1", "--purpose", "design freeze")
        self.assertEqual(code, 1)
        self.assertIn("needs none", out)
        code, out = self.record("baseline", "--tag", "work-1", "--purpose", "working")
        self.assertEqual(code, 0, out)

    def test_unapproved_items_stay_out_only_with_the_users_reason(self):
        path = self.project / "verification/software-qualification/SQT-0009.md"
        path.write_text(path.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1),
                        encoding="utf-8")
        code, out = self.record("baseline", "--tag", "design-1", "--purpose", "design freeze")
        self.assertEqual(code, 1, out)
        self.assertIn("draft: SQT-0009", out)
        code, out = self.record("baseline", "--tag", "design-1", "--purpose", "design freeze",
                                "--leave-out-reason", "SQT-0009 follows with the next release")
        self.assertEqual(code, 0, out)
        record = self.front("records/baselines/BL-0001.md")
        self.assertEqual(record["left_out"], [{"item": "SQT-0009", "status": "draft"}])
        self.assertEqual(record["left_out_reason"], "SQT-0009 follows with the next release")

    def test_a_communication_record_counts_only_for_the_practices_it_names(self):
        self.record("baseline", "--tag", "design-1", "--purpose", "design freeze")
        code, out = self.record("communication", "--subject", "BL-0001", "--audience", "Customer", "--channel", "mail",
                                "--practice", "SWE.1.BP8")
        self.assertEqual(code, 0, out)
        sys.path.insert(0, str(ROOT / "tools"))
        from traceability import Project, practice_rows
        rows = {r["practice"]: r for r in practice_rows(Project(self.project))}
        self.assertEqual(rows["SWE.1.BP8"]["evidence"], 1)
        self.assertEqual(rows["SWE.3.BP7"]["evidence"], 0)

    def test_communication_date_must_be_a_date(self):
        self.record("baseline", "--tag", "design-1", "--purpose", "design freeze")
        code, out = self.record("communication", "--subject", "BL-0001", "--audience", "Customer", "--channel", "mail",
                                "--sent-at", "last week")
        self.assertEqual(code, 1)
        code, out = self.record("communication", "--subject", "BL-0001", "--audience", "Customer", "--channel", "mail",
                                "--sent-at", "2026-06-02")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
