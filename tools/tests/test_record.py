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
    def review(self, *extra, checklist="software-requirements v1", verdict="approved", ids=("SWR-0001",)):
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
        code, out = self.review("--checks", self.all_checks(), checklist="Software requirements review v1")
        self.assertEqual(code, 0, out)

    def test_unknown_checklist_is_refused(self):
        code, out = self.review("--checks", self.all_checks(), checklist="my own list v1")
        self.assertEqual(code, 1)
        self.assertIn("cites no checklist of this toolkit", out)

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
