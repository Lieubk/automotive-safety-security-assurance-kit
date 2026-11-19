"""Regression tests for the trace engine.

Each test builds a small, fully valid project in a temporary directory, breaks
exactly one thing, and expects the engine to report exactly that.

Run:  python -m unittest discover -s tools/tests -v
"""
import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traceability import Project, as_date, content_hash, file_hash, progress  # noqa: E402

SCOPE = ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SUP.8"]
CODE = "#include \"unit.h\"\n\n/* one step */\nvoid Unit_Step(void)\n{\n}\n"
TEST_CODE = "#include \"unit.h\"\n\nstatic void test_UT_0001(void)\n{\n    Unit_Step();\n}\n"
RECORDED = ["src/unit.c", "src/unit.h", "tests/test_unit.c"]     # files whose hashes the fixture's runs record


def base_items():
    """A minimal thread from an imported system requirement down to a passed unit test."""
    crit = {"asil": "B", "security_relevant": False}
    req = {"kind": "functional", "priority": "must", "release": "R1", "verification_method": "test", "origin": "derived"}
    test_sections = {"Steps": "Call the step.", "Expected result": "Nothing happens."}
    return {
        "SYE-0001": ({"type": "system-element", "title": "ECU software", "status": "approved", "kind": "software",
                      "imported": {"source": "Customer architecture", "version": "1"},
                      "links": {"fulfils": ["SYR-0001"]}}, {}),
        "SYR-0001": ({"type": "system-requirement", "title": "Reverse on obstacle", "status": "approved", "asil": "B",
                      "imported": {"source": "Customer specification", "version": "1"},
                      "links": {}}, {"Statement": "The system shall reverse."}),
        "SWR-0001": ({"type": "software-requirement", "title": "Detect obstacle", "status": "approved", **crit, **req,
                      "links": {"derived_from": ["SYR-0001"]}},
                     {"Statement": "The software shall detect.", "Verification criteria": "Detected within 10 ms."}),
        "CMP-0001": ({"type": "software-component", "title": "Window control", "status": "approved", **crit,
                      "kind": "composition", "layer": "application", "origin": "developed",
                      "resource_budget": {"not_relevant": "sum of its parts"}},
                     {"Purpose": "Groups the feature.", "Responsibility": "Contains the parts.", "Dynamic behavior": "See parts."}),
        "CMP-0002": ({"type": "software-component", "title": "Detection", "status": "approved", **crit,
                      "kind": "application", "layer": "application", "origin": "developed",
                      "resource_budget": {"rom_bytes": 2048, "ram_bytes": 64},
                      "links": {"part_of": ["CMP-0001"], "fulfils": ["SWR-0001"]}},
                     {"Purpose": "Protects.", "Responsibility": "Detects.", "Dynamic behavior": "Runs every 5 ms."}),
        "IFC-0001": ({"type": "software-interface", "title": "Obstacle state", "status": "approved", **crit,
                      "kind": "sender-receiver", "provided_by": "CMP-0002", "used_by": ["CMP-0001"],
                      "elements": [{"name": "obstacle", "direction": "out", "type": "boolean"}]},
                     {"Description": "Reports an obstacle."}),
        "VIEW-0001": ({"type": "architecture-view", "title": "Structure", "status": "approved", "level": "software",
                       "kind": "structure", "links": {"shows": ["CMP-0001", "CMP-0002"]}},
                      {"Description": "Parts.", "Diagram": "```mermaid\ngraph TD; A-->B\n```"}),
        "VIEW-0002": ({"type": "architecture-view", "title": "States", "status": "approved", "level": "software",
                       "kind": "state-machine", "links": {"shows": ["CMP-0002"]}},
                      {"Description": "States.", "Diagram": "```mermaid\nstateDiagram-v2\n  [*] --> Idle\n```"}),
        "VIEW-0003": ({"type": "architecture-view", "title": "Tasks", "status": "approved", "level": "software",
                       "kind": "execution-model", "links": {"shows": ["CMP-0002"]},
                       "table": [{"name": "Task_5ms", "activation": "periodic", "priority": 10, "entries": ["Unit_Step"]}]},
                      {"Description": "Tasks."}),
        "VIEW-0004": ({"type": "architecture-view", "title": "Resources", "status": "approved", "level": "software",
                       "kind": "resource-summary", "links": {"shows": ["CMP-0002"]},
                       "table": [{"resource": "ROM", "capacity": "64 KiB", "objective": "48 KiB"}]},
                      {"Description": "Totals."}),
        "CDS-0001": ({"type": "component-design", "title": "Detection design", "status": "approved",
                      "links": {"refines": ["CMP-0002"]}},
                     {"Design concept": "One unit.", "Static structure": "UNT-0001.", "Dynamic behavior": "Not applicable: one unit.",
                      "Design evaluation": "Simple, testable."}),
        "UNT-0001": ({"type": "software-unit", "title": "Detection unit", "status": "approved", **crit,
                      "origin": "handwritten", "source_files": ["src/unit.c", "src/unit.h"],
                      "functions": [{"name": "Unit_Step", "category": "scheduled", "period_ms": 5}],
                      "links": {"part_of": ["CMP-0002"], "realizes": ["IFC-0001"], "implements": ["SWR-0001"]}},
                     {"Purpose": "Detects.", "Behavior": "Compares.", "Error handling": "None needed.",
                      "Dynamic behavior": "Not applicable: stateless."}),
        "UT-0001": ({"type": "unit-test", "title": "Step runs", "status": "approved", "asil": "B",
                     "execution": "automated", "script": "tests/test_unit.c::test_UT_0001", "environment": "host",
                     "regression": True, "links": {"verifies": ["UNT-0001#Unit_Step"]}}, test_sections),
        "PLN-0001": ({"type": "plan", "title": "Unit verification strategy", "status": "approved", "kind": "unit-verification",
                      "coverage_targets": {"B": {"statement_percent": 100, "branch_percent": 100}}},
                     {"Scope": "All units.", "Approach": "Tests and analysis.", "Criteria": "All pass.",
                      "Environment and tools": "Host.", "Responsibilities": "Developer."}),
        "PLN-0002": ({"type": "plan", "title": "Configuration management plan", "status": "approved",
                      "kind": "configuration-management"},
                     {"Scope": "All items.", "Approach": "Git.", "Criteria": "Tags.",
                      "Environment and tools": "Git.", "Responsibilities": "Configuration manager."}),
        "RUN-0001": ({"type": "test-run", "status": "final", "level": "unit", "item_under_test": "abc123",
                      "environment": "host", "executed_at": "2026-01-02T10:00:00",
                      "results": [{"test": "UT-0001", "verdict": "passed", "evidence": "build/out.txt"}],
                      "coverage": [{"unit": "UNT-0001", "file": "src/unit.c", "statement_percent": 100.0,
                                    "branch_percent": 100.0}], "sources": "auto"}, {}),
        "SAR-0001": ({"type": "static-analysis-run", "status": "final", "item_under_test": "abc123",
                      "tool": "analyser 1.0", "executed_at": "2026-01-02T10:00:00",
                      "results": [{"unit": "UNT-0001", "open_findings": 0}], "sources": "auto"}, {}),
    }


class Fixture:
    def __init__(self, items=None, scope=SCOPE, config=None, review=True, files=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.schema = yaml.safe_load((Path(__file__).resolve().parents[2] / "schema" / "items.yaml").read_text(encoding="utf-8"))
        cfg = {"scope": {"processes": scope}, "paths": {"items": ["plans", "spec", "verification", "records"], "source_roots": ["src"]}}
        cfg.update(config or {})
        (self.root / "project.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
        for name, text in {"src/unit.c": CODE, "src/unit.h": "void Unit_Step(void);\n", "tests/test_unit.c": TEST_CODE,
                           **(files or {})}.items():
            if text is None:                    # a test that wants the file to be absent
                continue
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.items = base_items() if items is None else items
        for item_id, (front, sections) in self.items.items():
            self.write(item_id, front, sections)
        if review:
            self.review()

    def write(self, item_id, front, sections):
        front = {"id": item_id, **front}
        if front.get("sources") == "auto":          # what the record tool would have stored at the time of the run
            front["sources"] = [{"file": name, "hash": file_hash(self.root / name)}
                                for name in RECORDED if (self.root / name).is_file()]
        folder = self.root / self.schema["types"][front["type"]]["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        body = "".join("\n## %s\n\n%s\n" % (name, text) for name, text in sections.items())
        (folder / (item_id + ".md")).write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body, encoding="utf-8")

    def review(self, rev_id="REV-0001", findings=None, skip_references=(), only=None, without=(), record_code=True,
               include_drafts=False):
        """Write a final review record that approves engineering items at their current content.

        By default every approved engineering item is the subject; `only` and `without` narrow that.
        """
        project = Project(self.root)
        engineering = [i for i in project.items.values()
                       if project.types[i.type]["lifecycle"] == "engineering"
                       and (i.status == "approved" or include_drafts)
                       and (only is None or i.id in only) and i.id not in without]
        subject = {i.id for i in engineering}
        upstream = sorted({target for i in engineering for role in (i.front.get("links") or {})
                           for target, _ in i.targets(role) if target in project.items and target not in subject})
        self.write(rev_id, {
            "type": "review-record", "status": "final", "checklist": "test checklist v1", "reviewers": ["A. Reviewer"],
            "verdict": "approved",
            "subject": [{"item": i.id, "hash": i.hash} for i in engineering],
            "references": [{"item": target, "hash": project.items[target].hash} for target in upstream
                           if target not in skip_references],
            "findings": findings or [],
            **({"sources": "auto"} if record_code and any(i.type == "software-unit" for i in engineering) else {}),
        }, {})

    def edit(self, item_id, **front_changes):
        front, sections = self.items[item_id]
        front = copy.deepcopy(front)
        front.update(front_changes)
        self.items[item_id] = (front, sections)
        self.write(item_id, front, sections)

    def findings(self, level=None):
        found = Project(self.root).check()
        return [f for f in found if level is None or f["level"] == level]

    def rules(self, level="error"):
        return sorted({(f["rule"], f["item"]) for f in self.findings(level)})


def changed(items, item_id, drop_links=(), **front_changes):
    """A copy of the item set with one item's front matter changed."""
    items = copy.deepcopy(items)
    front, sections = items[item_id]
    front.update(front_changes)
    for role in drop_links:
        front.get("links", {}).pop(role, None)
    return items


class Case(unittest.TestCase):
    def make(self, *args, **kwargs):
        """A fixture that lives until the end of the test."""
        fixture = Fixture(*args, **kwargs)
        self.addCleanup(fixture.tmp.cleanup)
        return fixture


class Examples(unittest.TestCase):
    """The worked examples are free of findings: a reader takes any finding for a defect of the toolkit."""

    def test_the_system_supplier_example_has_no_finding(self):
        example = Path(__file__).resolve().parents[2] / "examples" / "door-control-unit"
        findings = [f for f in Project(example).check() if f["level"] in ("error", "warning")]
        self.assertEqual(findings, [])

    def test_the_software_supplier_example_has_no_error(self):
        example = Path(__file__).resolve().parents[2] / "examples" / "power-window"
        self.assertEqual([f for f in Project(example).check() if f["level"] == "error"], [])


class GenericPractices(unittest.TestCase):
    """Observations per generic practice of level 2, read from the worked example."""

    def test_the_example_shows_planning_but_no_baseline(self):
        from traceability import generic_rows
        example = Path(__file__).resolve().parents[2] / "examples" / "power-window"
        rows = {r["practice"]: r for r in generic_rows(Project(example), "SWE.5")}
        self.assertEqual(len(rows), 11)
        self.assertEqual(rows["GP 2.1.1"]["state"], "evidence present")
        self.assertIn("WP-0008", rows["GP 2.1.1"]["evidence"])
        self.assertEqual(rows["GP 2.2.3"]["state"], "evidence not settled")      # no baseline in the example
        self.assertEqual(rows["GP 2.2.2"]["evidence"], ["PLN-0002"])


class ValidProject(Case):
    def test_clean_project_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_all_slice_rules_are_active(self):
        project = Project(self.make().root)
        active = {r for r in project.rules if project.active(r)}
        self.assertTrue({"COV-06", "COV-07", "COV-09", "COV-12", "COV-19", "COV-22"} <= active)
        self.assertFalse({"COV-02", "COV-13", "COV-14", "COV-16"} & active)   # SYS.2, SWE.5, SWE.6, SYS.5 out of scope


class Hashing(Case):
    def test_status_does_not_change_the_hash(self):
        front = {"id": "X-1", "status": "draft", "title": "t"}
        self.assertEqual(content_hash(front, "body\n"), content_hash({**front, "status": "approved"}, "body\n"))

    def test_trailing_whitespace_and_line_endings_do_not_change_the_hash(self):
        front = {"id": "X-1", "title": "t"}
        self.assertEqual(content_hash(front, "\n## A\n\ntext\n"), content_hash(front, "## A  \r\n\r\ntext   \r\n\r\n"))

    def test_registering_the_code_of_a_unit_does_not_change_the_hash(self):
        front = {"id": "UNT-1", "title": "t"}
        self.assertEqual(content_hash(front, "text"), content_hash({**front, "source_files": ["src/a.c"]}, "text"))

    def test_any_other_change_changes_the_hash(self):
        front = {"id": "X-1", "title": "t"}
        self.assertNotEqual(content_hash(front, "text"), content_hash(front, "text."))
        self.assertNotEqual(content_hash(front, "text"), content_hash({**front, "title": "u"}, "text"))


class Structure(Case):
    def test_missing_attribute_for_the_reached_stage(self):
        items = changed(base_items(), "SWR-0001")
        del items["SWR-0001"][0]["verification_method"]
        self.assertIn(("SCHEMA", "SWR-0001"), self.make(items).rules())

    def test_value_outside_the_allowed_list(self):
        self.assertIn(("SCHEMA", "SWR-0001"), self.make(changed(base_items(), "SWR-0001", asil="E")).rules())

    def test_missing_section(self):
        items = base_items()
        del items["SWR-0001"][1]["Verification criteria"]
        self.assertIn(("SCHEMA", "SWR-0001"), self.make(items).rules())

    def test_imported_item_needs_only_the_always_attributes(self):
        self.assertNotIn(("SCHEMA", "SYR-0001"), self.make().rules())
        items = changed(base_items(), "SYR-0001")
        del items["SYR-0001"][0]["imported"]
        self.assertIn(("SCHEMA", "SYR-0001"), self.make(items).rules())

    def test_unknown_attribute_is_a_warning(self):
        fixture = self.make(changed(base_items(), "SWR-0001", prority="must"))
        self.assertIn(("SCHEMA", "SWR-0001"), fixture.rules("warning"))

    def test_condition_interface_kind_needs_operations(self):
        fixture = self.make(changed(base_items(), "IFC-0001", kind="client-server"))
        messages = [f["message"] for f in fixture.findings("error") if f["item"] == "IFC-0001"]
        self.assertTrue(any("operations" in m and "kind is client-server" in m for m in messages), messages)

    def test_condition_view_kind_needs_a_table_of_the_right_structure(self):
        items = changed(base_items(), "VIEW-0003", table=[{"name": "Task_5ms"}])
        messages = [f["message"] for f in self.make(items).findings("error") if f["item"] == "VIEW-0003"]
        self.assertTrue(any("lacks 'activation'" in m for m in messages), messages)

    def test_structured_entry_lacks_a_mandatory_key(self):
        items = changed(base_items(), "IFC-0001", elements=[{"name": "obstacle", "type": "boolean"}])
        messages = [f["message"] for f in self.make(items).findings("error") if f["item"] == "IFC-0001"]
        self.assertTrue(any("lacks 'direction'" in m for m in messages), messages)

    def test_file_in_the_wrong_folder(self):
        fixture = self.make()
        source = fixture.root / "spec/software/requirements/SWR-0001.md"
        target = fixture.root / "spec/software/architecture/SWR-0001.md"
        source.rename(target)
        self.assertIn(("FORMAT", "SWR-0001"), fixture.rules())


class Links(Case):
    def test_target_does_not_exist(self):
        items = changed(base_items(), "SWR-0001", links={"derived_from": ["SYR-0009"]})
        self.assertIn(("LINK", "SWR-0001"), self.make(items).rules())

    def test_target_of_a_type_the_role_does_not_allow(self):
        items = changed(base_items(), "SWR-0001", links={"derived_from": ["UNT-0001"]})
        self.assertIn(("LINK", "SWR-0001"), self.make(items).rules())

    def test_role_the_type_may_not_carry(self):
        items = changed(base_items(), "SWR-0001", links={"derived_from": ["SYR-0001"],
                                                         "verifies": ["UNT-0001"]})
        self.assertIn(("LINK", "SWR-0001"), self.make(items).rules())

    def test_anchor_names_a_function_the_unit_does_not_design(self):
        items = changed(base_items(), "UT-0001", links={"verifies": ["UNT-0001#Unit_Stop"]})
        self.assertIn(("LINK", "UT-0001"), self.make(items).rules())


class Coverage(Case):
    def expect(self, rule, item, items, **kwargs):
        self.assertIn((rule, item), self.make(items, **kwargs).rules())

    def test_requirement_without_parent(self):
        self.expect("COV-06", "SWR-0001", changed(base_items(), "SWR-0001", drop_links=["derived_from"]))

    def test_internal_requirement_with_rationale_is_accepted(self):
        items = changed(base_items(), "SWR-0001", drop_links=["derived_from"], origin="internal")
        items["SWR-0001"][1]["Rationale"] = "Defensive measure."
        self.assertNotIn(("COV-06", "SWR-0001"), self.make(items).rules())

    def test_system_requirement_allocated_to_software_but_not_refined(self):
        self.expect("COV-05", "SYR-0001", changed(base_items(), "SWR-0001", drop_links=["derived_from"], origin="internal"))

    def test_deriving_from_the_element_does_not_cover_the_requirement(self):
        items = changed(base_items(), "SWR-0001", links={"derived_from": ["SYE-0001"]})
        self.expect("COV-05", "SYR-0001", items)
        unallocated = {k: v for k, v in base_items().items() if v[0]["type"] != "system-element"}
        fixture = self.make(unallocated)
        self.assertTrue(any(f["rule"] == "COV-05" and f["item"] == "project" and "cannot tell" in f["message"]
                            for f in fixture.findings("warning")))
        fixture = self.make(items, config={"trace": {"derive_via_elements": True}})
        self.assertNotIn(("COV-05", "SYR-0001"), fixture.rules())

    def test_link_to_an_obsolete_item(self):
        items = changed(base_items(), "SYR-0001", status="obsolete", superseded_by="a newer delivery")
        self.assertIn(("LINK", "SWR-0001"), self.make(items).rules())

    def test_imported_item_without_source_and_version(self):
        items = changed(base_items(), "SYR-0001", imported=True)
        self.assertIn(("SCHEMA", "SYR-0001"), self.make(items).rules())

    def test_requirement_not_allocated(self):
        self.expect("COV-07", "SWR-0001", changed(base_items(), "CMP-0002", drop_links=["fulfils"]))

    def test_allocation_to_an_interface_counts(self):
        items = changed(base_items(), "CMP-0002", drop_links=["fulfils"])
        items["IFC-0001"][0]["links"] = {"fulfils": ["SWR-0001"]}
        self.assertNotIn(("COV-07", "SWR-0001"), self.make(items).rules())

    def test_component_with_lower_asil_than_a_requirement_it_fulfils(self):
        items = changed(base_items(), "CMP-0002", asil="A")
        self.assertIn(("COV-23", "CMP-0002"), self.make(items).rules())

    def test_a_changed_requirement_makes_the_component_that_fulfils_it_suspect(self):
        fixture = self.make()
        fixture.edit("SWR-0001", title="Detect obstacle quickly")
        self.assertIn(("SUSPECT", "CMP-0002"), fixture.rules())

    def test_approved_item_above_a_draft(self):
        items = changed(base_items(), "SWR-0001", status="draft")
        fixture = self.make(items)
        self.assertIn(("UPSTREAM", "UNT-0001"), fixture.rules())      # the unit implements the draft requirement
        self.assertIn(("UPSTREAM", "CMP-0002"), fixture.rules())      # the component fulfils it

    def test_open_query_about_an_approved_item(self):
        items = base_items()
        items["QRY-0001"] = ({"type": "query", "title": "Reversal distance", "status": "open", "to": "Customer",
                              "asked_at": "2026-01-05", "links": {"about": ["SYR-0001"]}}, {"Question": "Which distance?"})
        fixture = self.make(items)
        self.assertEqual(fixture.rules("warning"), [("QUERY", "SYR-0001")])
        self.assertEqual(fixture.rules("error"), [])

    def test_draft_with_open_findings_of_its_last_review_is_visible(self):
        fixture = self.make(changed(base_items(), "SWR-0001", status="draft"), review=False)
        fixture.review("REV-0001", only=["SWR-0001"], include_drafts=True,
                       findings=[{"id": "F1", "item": "SWR-0001", "text": "x", "severity": "major", "state": "open"}])
        messages = [f["message"] for f in fixture.findings("info") if f["rule"] == "COV-19"]
        self.assertEqual(messages, ["review REV-0001 left findings open: F1"])

    def test_component_without_requirement(self):
        self.expect("COV-08", "CMP-0002", changed(base_items(), "CMP-0002", drop_links=["fulfils"]))

    def test_supplied_component_needs_no_requirement(self):
        items = base_items()
        items["CMP-0003"] = ({"type": "software-component", "title": "Operating system", "status": "approved", "asil": "B",
                              "security_relevant": False, "kind": "basic-software", "layer": "services", "origin": "supplied",
                              "supplier": "Vendor, version 4.2, object code", "resource_budget": {"rom_bytes": 8192},
                              "links": {"part_of": ["CMP-0001"]}},
                             {"Purpose": "Schedules the tasks.", "Responsibility": "Scheduling.", "Dynamic behavior": "Preemptive."})
        self.assertNotIn(("COV-08", "CMP-0003"), self.make(items).rules())

    def test_developed_component_without_design_and_units(self):
        items = base_items()
        del items["CDS-0001"]
        self.expect("COV-09", "CMP-0002", items)

    def test_source_file_listed_but_missing(self):
        items = changed(base_items(), "UNT-0001", source_files=["src/unit.c", "src/unit.h", "src/gone.c"])
        self.expect("COV-10", "UNT-0001", items)

    def test_source_file_without_owner(self):
        self.expect("COV-11", "src/extra.c", base_items(), files={"src/extra.c": "int x;\n"})

    def test_generated_files_need_no_owner(self):
        config = {"paths": {"items": ["plans", "spec", "verification", "records"], "source_roots": ["src"], "generated": ["src/gen/**"]}}
        fixture = self.make(files={"src/gen/Rte.c": "int x;\n"}, config=config)
        self.assertEqual(fixture.rules(), [])

    def test_unit_without_unit_test(self):
        items = base_items()
        del items["UT-0001"]
        items["RUN-0001"][0]["results"] = []
        self.expect("COV-12", "UNT-0001", items)

    def test_unit_missing_from_static_analysis(self):
        items = base_items()
        items["SAR-0001"][0]["results"] = []
        self.expect("COV-12", "UNT-0001", items)

    def test_test_case_without_verdict_in_latest_run(self):
        items = base_items()
        items["RUN-0001"][0]["results"] = []
        self.expect("COV-18", "UT-0001", items)

    def test_only_the_latest_final_run_counts(self):
        items = base_items()
        items["RUN-0002"] = ({"type": "test-run", "status": "final", "level": "unit", "item_under_test": "def456",
                              "environment": "host", "executed_at": "2026-02-01T10:00:00", "results": []}, {})
        self.expect("COV-18", "UT-0001", items)

    def test_failed_case_stays_visible_until_a_problem_report_names_it(self):
        items = base_items()
        items["RUN-0001"][0]["results"][0].update(verdict="failed", reason="expected 3, got 4")
        fixture = self.make(items)
        messages = [f["message"] for f in fixture.findings("error") if f["rule"] == "COV-18"]
        self.assertTrue(messages and "failed in RUN-0001 (expected 3, got 4)" in messages[0], messages)
        items["PRB-0001"] = ({"type": "problem-report", "title": "Off by one", "status": "open", "severity": "major",
                              "found_in": "abc123, RUN-0001", "reported_by": "Tester", "reported_at": "2026-01-03",
                              "detected_by": "unit-test"}, {"Description": "One count too many."})
        fixture = self.make(items)
        self.assertNotIn(("COV-18", "UT-0001"), fixture.rules("error"))
        self.assertIn(("COV-18", "UT-0001"), fixture.rules("warning"))
        fixture.edit("PRB-0001", status="resolved")
        self.assertIn(("COV-18", "UT-0001"), fixture.rules("info"))

    def test_approved_item_without_review(self):
        self.assertIn(("COV-19", "SWR-0001"), self.make(review=False).rules())

    def test_stale_approval_after_a_content_change(self):
        fixture = self.make()
        fixture.edit("SWR-0001", title="Detect obstacle quickly")
        errors = fixture.findings("error")
        self.assertTrue(any(f["rule"] == "COV-19" and f["item"] == "SWR-0001" and "stale" in f["message"] for f in errors))

    def test_suspect_link_after_an_upstream_change(self):
        fixture = self.make()
        fixture.edit("SWR-0001", title="Detect obstacle quickly")
        self.assertIn(("SUSPECT", "UNT-0001"), fixture.rules())     # the unit implements the changed requirement
        self.assertNotIn(("SUSPECT", "UT-0001"), fixture.rules())   # the test verifies the unit, which did not change

    def test_reference_missing_from_the_review_is_a_warning(self):
        inputs = ["SYE-0001", "SYR-0001"]
        fixture = self.make(review=False)
        fixture.review("REV-0001", only=inputs)                                    # input acceptance
        fixture.review("REV-0002", without=inputs, skip_references=["SYR-0001"])  # never compared with SYR-0001
        self.assertEqual(fixture.rules("warning"), [("CONSISTENCY", "SWR-0001")])
        self.assertEqual(fixture.rules("error"), [])

    def test_items_reviewed_together_need_no_separate_reference(self):
        fixture = self.make(review=False)
        everything = list(base_items())
        fixture.review(skip_references=everything)          # subject lists all items, references none
        self.assertEqual(fixture.rules("warning"), [])

    def test_suspect_link_is_found_for_items_reviewed_together(self):
        fixture = self.make(review=False)
        fixture.review(skip_references=list(base_items()))
        fixture.edit("CMP-0002", title="Detection, renamed")
        self.assertIn(("SUSPECT", "UNT-0001"), fixture.rules())   # the unit is part of the changed component

    def test_newest_review_of_the_same_content_decides(self):
        inputs = ["SYE-0001", "SYR-0001"]
        fixture = self.make(review=False)
        fixture.review("REV-0001", only=inputs)
        fixture.review("REV-0002", without=inputs, skip_references=["SYR-0001"])   # leaves a consistency warning
        self.assertIn(("CONSISTENCY", "SWR-0001"), fixture.rules("warning"))
        fixture.review("REV-0003", only=["SWR-0001"])                              # re-review records the parent
        self.assertEqual(fixture.rules("warning"), [])

    def test_earlier_open_finding_on_the_same_content_is_not_overridden(self):
        fixture = self.make(review=False)
        fixture.review("REV-0001", findings=[{"id": "F1", "item": "SWR-0001", "text": "x", "severity": "major", "state": "open"}])
        fixture.review("REV-0002")
        messages = [f["message"] for f in fixture.findings("error") if f["item"] == "SWR-0001"]
        self.assertTrue(any("REV-0001#F1" in m for m in messages), messages)
        fixture.review("REV-0003", findings=[{"id": "F1", "item": "SWR-0001", "text": "settled: not a defect",
                                              "severity": "major", "state": "closed", "closes": "REV-0001#F1"}])
        self.assertEqual([f for f in fixture.findings("error") if f["item"] == "SWR-0001"], [])

    def test_open_review_finding_blocks_the_approval(self):
        fixture = self.make(review=False)
        fixture.review(findings=[{"id": "F1", "item": "SWR-0001", "text": "unit missing", "severity": "minor", "state": "open"}])
        self.assertIn(("COV-19", "SWR-0001"), fixture.rules())
        self.assertNotIn(("COV-19", "CMP-0002"), fixture.rules())

    def test_interface_not_realized_by_a_unit_of_its_provider(self):
        self.expect("COV-21", "IFC-0001", changed(base_items(), "UNT-0001", drop_links=["realizes"]))

    def test_parameter_types_differ_between_design_and_code(self):
        items = changed(base_items(), "UNT-0001", functions=[
            {"name": "Unit_Step", "category": "scheduled", "period_ms": 5, "return_type": "void",
             "arguments": [{"name": "speed", "direction": "in", "type": "uint16"}]}])
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-22"]
        self.assertEqual(messages, ["parameters of Unit_Step differ: design (uint16), code (void)"])

    def test_return_type_differs_between_design_and_code(self):
        items = changed(base_items(), "UNT-0001", functions=[
            {"name": "Unit_Step", "category": "scheduled", "period_ms": 5, "arguments": [],
             "returns": [{"type": "Std_ReturnType", "value": "E_OK", "meaning": "done"}]}])
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-22"]
        self.assertEqual(messages, ["return type of Unit_Step differs: design Std_ReturnType, code void"])

    def test_pointer_and_array_parameters_are_compared_by_type(self):
        code = "#include \"unit.h\"\nvoid Unit_Step(void)\n{\n}\n" \
               "Std_ReturnType Unit_Read(const uint8 *buffer, uint16 values[4], Unit_StateType * const state)\n{\n    return 0;\n}\n"
        items = changed(base_items(), "UNT-0001", functions=[
            {"name": "Unit_Step", "category": "scheduled", "period_ms": 5},
            {"name": "Unit_Read", "category": "public", "return_type": "Std_ReturnType", "arguments": [
                {"name": "buffer", "direction": "in", "type": "const uint8 *"},
                {"name": "values", "direction": "in", "type": "uint16*"},
                {"name": "state", "direction": "out", "type": "Unit_StateType * const"}]}])
        items["UT-0002"] = copy.deepcopy(items["UT-0001"])
        items["UT-0002"][0]["links"] = {"verifies": ["UNT-0001#Unit_Read"]}
        items["RUN-0001"][0]["results"].append({"test": "UT-0002", "verdict": "passed"})
        self.assertEqual(self.make(items, files={"src/unit.c": code}).rules(), [])

    def test_designed_unit_without_code_is_a_warning_not_an_error(self):
        items = changed(base_items(), "UNT-0001", source_files=[])
        del items["UT-0001"], items["RUN-0001"], items["SAR-0001"]
        fixture = self.make(items, scope=["SWE.1", "SWE.2", "SWE.3", "SUP.8"], files={"src/unit.c": None, "src/unit.h": None,
                                                                                      "tests/test_unit.c": None})
        self.assertEqual(fixture.rules("error"), [])
        self.assertIn(("COV-10", "UNT-0001"), fixture.rules("warning"))

    def test_verification_of_a_unit_without_code_is_pending_not_failed(self):
        items = changed(base_items(), "UNT-0001", source_files=[])
        del items["UT-0001"], items["RUN-0001"], items["SAR-0001"]
        fixture = self.make(items, files={"src/unit.c": None, "src/unit.h": None, "tests/test_unit.c": None})
        self.assertEqual(fixture.rules("error"), [])              # a design baseline is possible with SWE.4 in scope
        pending = {rule for rule, item in fixture.rules("warning") if item == "UNT-0001"}
        self.assertLessEqual({"COV-10", "COV-12", "COV-28", "COV-29"}, pending)

    def test_registering_the_code_keeps_the_design_approval(self):
        items = changed(base_items(), "UNT-0001", source_files=[])
        fixture = self.make(items)                               # reviewed while the unit listed no code
        fixture.edit("UNT-0001", source_files=["src/unit.c", "src/unit.h"])
        self.assertNotIn(("COV-19", "UNT-0001"), fixture.rules())

    def test_draft_shows_what_the_next_stage_will_ask_for(self):
        items = changed(base_items(), "SWR-0001", status="draft")
        del items["SWR-0001"][0]["kind"]
        messages = [f["message"] for f in self.make(items).findings("info") if f["rule"] == "SCHEMA"]
        self.assertEqual(messages, ["still to come before review: kind"])

    def test_code_changed_after_the_review_of_the_unit(self):
        fixture = self.make()
        (fixture.root / "src/unit.c").write_text(CODE + "/* edited */\n", encoding="utf-8")
        self.assertIn(("SUSPECT", "UNT-0001"), fixture.rules())

    def test_review_of_a_unit_that_does_not_record_the_code(self):
        fixture = self.make(review=False)
        fixture.review(record_code=False)
        self.assertIn(("CONSISTENCY", "UNT-0001"), fixture.rules("warning"))

    def test_designed_function_missing_from_the_code(self):
        self.expect("COV-22", "UNT-0001", base_items(), files={"src/unit.c": "/* void Unit_Step(void) {} */\n"})

    def test_function_in_the_code_missing_from_the_design(self):
        code = CODE + "\nvoid Unit_Reset(void)\n{\n}\n\nstatic void helper(void)\n{\n}\n"
        messages = [f["message"] for f in self.make(files={"src/unit.c": code}).findings("error")]
        self.assertTrue(any("Unit_Reset" in m for m in messages), messages)
        self.assertFalse(any("helper" in m for m in messages), messages)      # static functions are the unit's own business

    def test_asil_lower_than_what_it_implements(self):
        self.expect("COV-23", "UNT-0001", changed(base_items(), "UNT-0001", asil="A"))

    def test_asil_gap_accepted_with_an_approved_decision(self):
        items = changed(base_items(), "UNT-0001", asil="A")
        items["ADR-0001"] = ({"type": "design-decision", "title": "Decomposition", "status": "approved", "level": "detailed-design",
                              "links": {"concerns": ["UNT-0001"]}},
                             {"Context": "c", "Evaluation criteria": "e", "Alternatives": "a", "Decision": "d", "Consequences": "q"})
        self.assertNotIn(("COV-23", "UNT-0001"), self.make(items).rules())

    def test_view_showing_an_obsolete_item(self):
        self.expect("COV-24", "VIEW-0002", changed(base_items(), "CMP-0002", status="obsolete", superseded_by="replaced by nothing"))

    def test_required_view_kind_missing(self):
        items = base_items()
        del items["VIEW-0004"]
        self.expect("COV-25", "project", items)

    def test_required_view_kind_waived_in_the_configuration(self):
        items = base_items()
        del items["VIEW-0004"]
        fixture = self.make(items, config={"trace": {"views_not_applicable": {"resource-summary": "budget owned by the customer"}}})
        self.assertNotIn(("COV-25", "project"), fixture.rules())

    def test_coverage_below_the_target_of_the_plan(self):
        items = base_items()
        items["RUN-0001"][0]["coverage"][0]["branch_percent"] = 92.5
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-28"]
        self.assertEqual(messages, ["branch_percent is 92.5 in RUN-0001, target for ASIL B is 100"])

    def test_coverage_below_target_with_a_recorded_deviation(self):
        items = base_items()
        items["RUN-0001"][0]["coverage"][0].update(branch_percent=92.5, deviation="defensive default branch, reviewed")
        self.assertNotIn(("COV-28", "UNT-0001"), self.make(items).rules())

    def test_coverage_not_measured(self):
        items = base_items()
        items["RUN-0001"][0]["coverage"] = "not measured: coverage needs gcc with gcov"
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-28"]
        self.assertTrue(messages and "not measured" in messages[0], messages)

    def test_no_target_for_the_asil_means_no_coverage_demand(self):
        items = changed(base_items(), "PLN-0001", coverage_targets={"D": {"statement_percent": 100}})
        del items["RUN-0001"][0]["coverage"]
        self.assertNotIn(("COV-28", "UNT-0001"), self.make(items).rules())

    def test_plan_without_targets_is_reported_as_not_assessed(self):
        items = base_items()
        del items["PLN-0001"][0]["coverage_targets"]
        self.assertIn(("COV-28", "PLN-0001"), self.make(items).rules("warning"))

    def test_public_function_without_a_test_that_names_it(self):
        items = changed(base_items(), "UT-0001", links={"verifies": ["UNT-0001"]})
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-29"]
        self.assertEqual(messages, ["no unit test verifies UNT-0001#Unit_Step"])

    def test_code_changed_after_the_runs(self):
        fixture = self.make()
        (fixture.root / "src/unit.c").write_text(CODE + "/* edited */\n", encoding="utf-8")
        messages = sorted(f["message"] for f in fixture.findings("error") if f["rule"] == "COV-30")
        self.assertEqual(messages, ["src/unit.c changed after RUN-0001: that run does not describe the current code",
                                    "src/unit.c changed after SAR-0001: that run does not describe the current code"])

    def test_test_code_changed_after_the_run(self):
        fixture = self.make()
        (fixture.root / "tests/test_unit.c").write_text(TEST_CODE + "/* edited */\n", encoding="utf-8")
        self.assertIn(("COV-30", "UT-0001"), fixture.rules())

    def test_run_without_source_hashes_is_reported_as_not_assessable(self):
        items = base_items()
        del items["RUN-0001"][0]["sources"]
        fixture = self.make(items)
        self.assertIn(("COV-30", "RUN-0001"), fixture.rules("warning"))
        self.assertEqual(fixture.rules("error"), [])

    def test_test_script_that_does_not_exist(self):
        items = changed(base_items(), "UT-0001", script="tests/missing.c::test_UT_0001")
        self.assertIn(("LINK", "UT-0001"), self.make(items).rules())

    def test_test_function_that_is_not_in_the_script(self):
        items = changed(base_items(), "UT-0001", script="tests/test_unit.c::test_UT_0009")
        self.assertIn(("LINK", "UT-0001"), self.make(items).rules())

    def test_test_case_with_lower_asil_than_the_unit(self):
        self.assertIn(("COV-23", "UT-0001"), self.make(changed(base_items(), "UT-0001", asil="A")).rules())

    def test_strategy_of_a_process_in_scope_is_missing(self):
        items = base_items()
        del items["PLN-0001"]
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-27"]
        self.assertEqual(messages, ["no approved plan of kind unit-verification"])

    def test_no_plan_is_asked_for_processes_out_of_scope(self):
        items = base_items()
        for gone in ("PLN-0001", "PLN-0002", "UT-0001", "RUN-0001", "SAR-0001", "CDS-0001", "UNT-0001"):
            del items[gone]
        rules = {rule for rule, _ in self.make(items, scope=["SWE.1", "SWE.2"], files={}).rules()}
        self.assertNotIn("COV-27", rules)

    def test_baseline_without_communication_record(self):
        items = base_items()
        items["BL-0001"] = ({"type": "baseline", "status": "final", "tag": "v1", "purpose": "requirements freeze", "items": []}, {})
        self.expect("COV-26", "BL-0001", items)
        items["CMR-0001"] = ({"type": "communication-record", "status": "final", "subject": "BL-0001", "audience": ["Customer"],
                              "channel": "release mail", "sent_at": "2026-01-03"}, {})
        self.assertNotIn(("COV-26", "BL-0001"), self.make(items).rules())


@unittest.skipUnless(shutil.which("git"), "git is not available")
class Diff(Case):
    def git(self, root, *arguments):
        subprocess.run(["git", "-C", str(root), "-c", "user.name=T", "-c", "user.email=tester"] + list(arguments),
                       check=True, capture_output=True)

    def diff(self, root, *arguments):
        done = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "traceability.py"),
                               "--project", str(root), "diff"] + list(arguments), capture_output=True, text=True)
        return done.returncode, done.stdout

    def test_the_change_since_the_review_is_shown_from_the_history(self):
        fixture = self.make()
        self.git(fixture.root, "init", "-q")
        self.git(fixture.root, "add", "-A")
        self.git(fixture.root, "commit", "-q", "-m", "reviewed state")
        code, out = self.diff(fixture.root, "SWR-0001")
        self.assertEqual(code, 0, out)
        self.assertIn("unchanged since REV-0001", out)
        fixture.edit("SWR-0001", title="Detect an obstacle early")
        code, out = self.diff(fixture.root, "SWR-0001", "--since", "REV-0001")
        self.assertEqual(code, 0, out)
        self.assertIn("-title: Detect obstacle", out)
        self.assertIn("+title: Detect an obstacle early", out)

    def test_without_the_reviewed_text_the_diff_is_not_assessed(self):
        fixture = self.make()
        self.git(fixture.root, "init", "-q")
        fixture.edit("SWR-0001", title="Detect an obstacle early")
        code, out = self.diff(fixture.root, "SWR-0001")
        self.assertEqual(code, 2, out)
        self.assertIn("NOT ASSESSED", out)


class OpenPoints(Case):
    def test_a_query_not_sent_yet_is_valid_and_says_so(self):
        items = base_items()
        items["QRY-0001"] = ({"type": "query", "title": "Meaning of reverse", "status": "open", "to": "customer",
                              "links": {"about": ["SYR-0001"]}}, {"Question": "Which distance?"})
        fixture = self.make(items)
        self.assertFalse([f for f in fixture.findings("error") if f["item"] == "QRY-0001"])
        messages = [f["message"] for f in fixture.findings("warning") if f["rule"] == "QUERY"]
        self.assertTrue(messages and "not put to its source yet" in messages[0], messages)

    def test_an_open_problem_report_stays_visible_on_the_approved_item(self):
        items = base_items()
        items["PRB-0001"] = ({"type": "problem-report", "title": "Task bound missing", "status": "open",
                              "severity": "major", "found_in": "review REV-0001", "reported_by": "Reviewer",
                              "reported_at": "2026-01-03", "detected_by": "review",
                              "links": {"affects": ["VIEW-0003"]}}, {"Description": "Nothing bounds the task."})
        fixture = self.make(items)
        self.assertIn(("PROBLEM", "VIEW-0003"), fixture.rules("warning"))
        fixture.edit("PRB-0001", status="rejected")
        self.assertNotIn(("PROBLEM", "VIEW-0003"), fixture.rules("warning"))


def planned_items():
    """The base items with a project plan and work packages that deliver every engineering item."""
    items = base_items()
    engineering = [i for i, (front, _) in items.items()
                   if front["type"] not in ("test-run", "static-analysis-run") and not front.get("imported")]
    items["PLN-0003"] = ({"type": "plan", "title": "Project plan", "status": "approved", "kind": "project",
                          "milestones": [{"name": "Release candidate", "date": "2026-03-01",
                                          "baseline_purpose": "release candidate"}]},
                         {"Scope": "One feature.", "Approach": "V model, two milestones.", "Criteria": "All approved.",
                          "Environment and tools": "Git.", "Responsibilities": "Project lead.",
                          "Feasibility": "Feasible with two people.", "Interfaces and commitments": "Customer.",
                          "Reporting": "Monthly."})
    package = {"type": "work-package", "status": "approved", "estimate": 10, "owner": "Project lead"}
    sections = {"Description": "The work.", "Deliverables": "The items.", "Estimate basis": "Expert judgement."}
    items["WP-0001"] = ({**package, "title": "Feature", "category": "engineering", "planned_start": "2026-01-05",
                         "planned_finish": "2026-02-27",
                         "links": {"delivers": [i for i in engineering if not i.startswith("PLN")]}}, sections)
    items["WP-0002"] = ({**package, "title": "Planning", "category": "management", "planned_start": "2026-01-05",
                         "planned_finish": "2026-01-09",
                         "links": {"delivers": ["PLN-0001", "PLN-0002", "PLN-0003"]}}, sections)
    items["WP-0003"] = ({**package, "title": "Configuration management", "category": "support",
                         "planned_start": "2026-01-05", "planned_finish": "2026-02-27"}, sections)
    return items


class ProjectManagement(Case):
    def plan(self, items=None):
        return self.make(planned_items() if items is None else items, scope=SCOPE + ["MAN.3"])

    def test_a_complete_plan_has_no_findings(self):
        self.assertEqual(self.plan().findings(), [])

    def test_an_item_no_work_package_delivers(self):
        items = planned_items()
        items["WP-0001"][0]["links"]["delivers"].remove("CMP-0002")
        self.assertIn(("COV-32", "CMP-0002"), self.plan(items).rules())

    def test_a_missing_category(self):
        items = planned_items()
        del items["WP-0003"]
        self.assertIn(("COV-33", "project"), self.plan(items).rules())

    def test_a_dependency_cycle(self):
        items = planned_items()
        items["WP-0002"][0]["links"]["depends_on"] = ["WP-0003"]
        items["WP-0003"][0]["links"] = {"depends_on": ["WP-0002"]}
        self.assertIn(("COV-31", "WP-0002"), self.plan(items).rules())

    def test_dates_that_do_not_fit(self):
        items = planned_items()
        items["WP-0002"][0]["planned_finish"] = "2026-01-02"
        self.assertIn(("COV-34", "WP-0002"), self.plan(items).rules())

    def test_a_date_must_be_a_date(self):
        items = planned_items()
        items["WP-0002"][0]["planned_start"] = "next week"
        messages = [f["message"] for f in self.plan(items).findings("error") if f["item"] == "WP-0002"]
        self.assertTrue(any("expected a date" in m for m in messages), messages)

    def test_tracking_does_not_make_the_plan_stale(self):
        fixture = self.plan()
        before = Project(fixture.root).items["WP-0001"].hash
        fixture.edit("WP-0001", progress={"actual_effort": 4, "as_of": "2026-01-20"})
        self.assertEqual(Project(fixture.root).items["WP-0001"].hash, before)
        self.assertEqual(fixture.findings("error"), [])

    def test_linking_what_was_delivered_does_not_make_the_plan_stale(self):
        items = planned_items()
        items["WP-0003"][0]["links"] = {"delivers": []}
        fixture = self.plan(items)
        before = Project(fixture.root).items["WP-0003"].hash
        fixture.edit("WP-0003", links={"delivers": ["PLN-0002"]})
        self.assertEqual(Project(fixture.root).items["WP-0003"].hash, before)

    def test_a_changed_deliverable_does_not_make_the_package_suspect(self):
        fixture = self.plan()
        fixture.edit("SWR-0001", title="Detect obstacle, reworded", status="draft")
        rules = {rule for rule, item in fixture.rules() if item.startswith("WP-")}
        self.assertEqual(rules, set())

    def test_progress_is_read_from_the_deliverables(self):
        fixture = self.plan()
        fixture.edit("WP-0001", progress={"completed_on": "2026-02-20"})
        fixture.edit("WP-0002", progress={"completed_on": "2026-01-09"})
        data = progress(Project(fixture.root), as_date("2026-03-02"))
        state = {p["item"]: p for p in data["work_packages"]}
        self.assertEqual(state["WP-0001"]["state"], "done")
        self.assertEqual(state["WP-0003"]["state"], "not started")
        self.assertTrue(state["WP-0003"]["late"])
        self.assertEqual(data["milestones"][0]["state"], "missed")
        fixture.edit("SWR-0001", status="draft")
        state = {p["item"]: p for p in progress(Project(fixture.root), as_date("2026-03-02"))["work_packages"]}
        self.assertEqual(state["WP-0001"]["state"], "done as stated, contradicted")
        self.assertIn("SWR-0001", state["WP-0001"]["unsettled"])


class Impact(Case):
    def downstream(self, fixture, item_id):
        project = Project(fixture.root)
        seen, queue = set(), [item_id]
        while queue:
            for sources in project.incoming[queue.pop()].values():
                for source in sources:
                    if source not in seen and source != item_id:
                        seen.add(source)
                        queue.append(source)
        return seen

    def test_a_requirement_change_reaches_design_and_tests(self):
        self.assertLessEqual({"UNT-0001", "UT-0001"}, self.downstream(self.make(), "SWR-0001"))

    def test_an_interface_change_reaches_the_components_that_use_it(self):
        self.assertIn("CMP-0001", self.downstream(self.make(), "IFC-0001"))

    def test_an_interface_change_reaches_the_component_that_provides_it(self):
        self.assertIn("CMP-0002", self.downstream(self.make(), "IFC-0001"))

    def test_a_changed_interface_makes_provider_and_users_suspect(self):
        fixture = self.make()
        fixture.edit("IFC-0001", title="Obstacle state, renamed")
        suspects = {item for rule, item in fixture.rules() if rule == "SUSPECT"}
        self.assertLessEqual({"CMP-0001", "CMP-0002"}, suspects)

    def test_several_links_to_functions_of_one_unit_are_reported_once(self):
        project = Project(self.make().root)
        for item in project.items.values():
            found = project.dependencies(item)
            self.assertEqual(len(found), len(set(found)), item.id)
        tests = [i for i in project.of_type("unit-test") if len(i.targets("verifies")) > 1]
        if tests:
            self.assertEqual(len([d for d in project.dependencies(tests[0]) if d[1] == "verifies"]),
                             len({target for target, _ in tests[0].targets("verifies")}))

    def test_component_approved_above_a_draft_interface(self):
        fixture = self.make(changed(base_items(), "IFC-0001", status="draft"))
        self.assertIn(("UPSTREAM", "CMP-0002"), fixture.rules())

    def test_a_changed_draft_is_reported_once_as_upstream_not_also_as_suspect(self):
        fixture = self.make()
        fixture.edit("IFC-0001", title="Obstacle state, renamed", status="draft")
        rules = fixture.rules()
        self.assertIn(("UPSTREAM", "CMP-0002"), rules)
        self.assertNotIn(("SUSPECT", "CMP-0002"), rules)

    def test_a_requirement_that_relies_on_another_becomes_suspect_when_it_changes(self):
        items = base_items()
        items["SWR-0002"] = copy.deepcopy(items["SWR-0001"])
        items["SWR-0002"][0]["title"] = "React to the detection"
        items["SWR-0002"][0]["links"] = {"derived_from": ["SYR-0001"], "relies_on": ["SWR-0001"]}
        items["CMP-0002"][0]["links"]["fulfils"] = ["SWR-0001", "SWR-0002"]
        fixture = self.make(items)
        self.assertNotIn(("SUSPECT", "SWR-0002"), fixture.rules())
        fixture.edit("SWR-0001", title="Detect obstacle, reworded")
        self.assertIn(("SUSPECT", "SWR-0002"), fixture.rules())
        self.assertIn("SWR-0002", self.downstream(fixture, "SWR-0001"))


class Scope(Case):
    def test_rules_of_processes_out_of_scope_stay_silent(self):
        items = base_items()
        for gone in ("UT-0001", "RUN-0001", "SAR-0001", "CDS-0001", "UNT-0001"):
            del items[gone]
        rules = {rule for rule, _ in self.make(items, scope=["SWE.1", "SWE.2"], files={}).rules()}
        self.assertFalse({"COV-09", "COV-11", "COV-12", "COV-18", "COV-21"} & rules, rules)

    def test_gaps_on_drafts_are_information_only(self):
        items = changed(base_items(), "SWR-0001", status="draft")
        items["CMP-0002"][0]["links"].pop("fulfils")
        fixture = self.make(items)
        self.assertNotIn(("COV-07", "SWR-0001"), fixture.rules("error"))
        self.assertIn(("COV-07", "SWR-0001"), fixture.rules("info"))


PROBLEM_SCOPE = SCOPE + ["SUP.9"]


def problem_items(**problem):
    """The base thread with a problem-resolution strategy and one problem report, closed and alerted."""
    items = base_items()
    items["PLN-0003"] = ({"type": "plan", "title": "Problem resolution strategy", "status": "approved",
                          "kind": "problem-resolution", "urgent_severities": ["critical"],
                          "alerts": [{"severity": "major", "audience": ["Software lead"]},
                                     {"severity": "critical", "audience": ["Software lead", "Customer"]}]},
                         {"Scope": "All problems.", "Approach": "Record, analyse, resolve, close.", "Criteria": "Retest.",
                          "Environment and tools": "Items.", "Responsibilities": "Software lead."})
    front = {"type": "problem-report", "title": "Detection too late", "status": "closed", "severity": "major",
             "reported_by": "Tester", "reported_at": "2026-01-03", "detected_by": "unit-test",
             "found_in": "abc123, RUN-0001", "origin": "code",
             "closure": {"accepted_by": "Software lead", "accepted_at": "2026-01-10", "evidence": "RUN-0001"},
             "links": {"affects": ["UNT-0001"]}}
    front.update(problem)
    items["PRB-0001"] = (front, {"Description": "Late.", "Cause and impact": "A wrong limit.", "Resolution": "Fixed."})
    items["CMR-0001"] = ({"type": "communication-record", "status": "final", "subject": "PRB-0001",
                          "audience": ["Software lead"], "channel": "mail", "sent_at": "2026-01-03"}, {})
    return items


class ProblemResolution(Case):
    def make(self, items=None, **kwargs):
        kwargs.setdefault("scope", PROBLEM_SCOPE)
        return super().make(problem_items() if items is None else items, **kwargs)

    def test_recorded_alerted_and_closed_problem_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_urgent_problem_without_authorised_action(self):
        items = problem_items(severity="critical", status="open")
        items["CMR-0001"][0]["audience"] = ["Software lead", "Customer"]
        fixture = self.make(items)
        self.assertIn(("COV-39", "PRB-0001"), fixture.rules("warning"))      # open: a warning
        fixture.edit("PRB-0001", status="analysed")
        self.assertIn(("COV-39", "PRB-0001"), fixture.rules("error"))        # analysed: an error
        fixture.edit("PRB-0001", urgent_action={"action": "none: the function is disabled in the release",
                                                "authorised_by": "Software lead", "authorised_at": "2026-01-03"})
        self.assertNotIn("COV-39", {r for r, _ in fixture.rules("error")})

    def test_problem_not_alerted_as_the_strategy_asks(self):
        items = problem_items(severity="critical")
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-40"]
        self.assertTrue(messages and "alerts Customer" in messages[0], messages)

    def test_problem_in_a_baselined_item_needs_a_change_request(self):
        items = problem_items(status="in-resolution", links={"affects": ["SWR-0001"]})
        items["PRB-0001"][0].pop("closure")
        items["BL-0001"] = ({"type": "baseline", "status": "final", "tag": "r1", "purpose": "release candidate",
                             "items": [{"item": "SWR-0001", "hash": "x", "status": "approved"}]}, {})
        self.assertIn(("COV-41", "PRB-0001"), self.make(items).rules())
        items["CR-0001"] = ({"type": "change-request", "title": "Correct the limit", "status": "submitted",
                             "requester": "Software lead", "links": {"resolves": ["PRB-0001"]}},
                            {"Description": "Correct it."})
        self.assertNotIn(("COV-41", "PRB-0001"), self.make(items).rules())

    def test_closure_needs_evidence_and_closed_change_requests(self):
        items = problem_items(closure={"accepted_by": "Software lead", "accepted_at": "2026-01-10",
                                       "evidence": "RUN-0099"})
        items["CR-0001"] = ({"type": "change-request", "title": "Correct the limit", "status": "submitted",
                             "requester": "Software lead", "links": {"resolves": ["PRB-0001"]}},
                            {"Description": "Correct it."})
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-42"]
        self.assertEqual(len(messages), 2, messages)

    def test_closed_problem_without_closure(self):
        items = problem_items()
        items["PRB-0001"][0].pop("closure")
        self.assertIn(("SCHEMA", "PRB-0001"), self.make(items).rules())

    def test_problems_with_ages_and_figures(self):
        from traceability import problems
        items = problem_items()
        items["PRB-0002"] = ({"type": "problem-report", "title": "Later", "status": "open", "severity": "minor",
                              "reported_by": "Tester", "reported_at": "2026-02-01", "detected_by": "review",
                              "found_in": "abc123"}, {"Description": "Later."})
        project = Project(self.make(items).root)
        data = problems(project, as_of(2026, 1, 20))
        self.assertEqual([e["item"] for e in data["problems"]], ["PRB-0001"])     # PRB-0002 not known yet
        self.assertEqual(data["problems"][0]["age_days"], 7)                      # reported to accepted
        later = problems(project, as_of(2026, 2, 11))
        self.assertEqual(later["figures"]["unresolved"], 1)
        self.assertEqual(later["figures"]["by_origin"], {"None": 1, "code": 1})
        self.assertEqual(later["figures"]["unresolved_by_age"]["8 to 30 days"], 1)

    def test_history_reads_the_states_from_git(self):
        fixture = self.make()
        git = ["git", "-c", "user.name=tester", "-c", "user.email=tester", "-C", str(fixture.root)]
        subprocess.run(git[:1] + ["init", "-q", str(fixture.root)], check=True)
        fixture.edit("PRB-0001", status="open")
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "open"], check=True)
        fixture.edit("PRB-0001", status="closed")
        subprocess.run(git + ["commit", "-q", "-am", "closed"], check=True)
        done = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / "traceability.py"),
                               "--project", str(fixture.root), "history", "PRB-0001"], capture_output=True, text=True)
        states = [line.split()[-1] for line in done.stdout.splitlines()]
        self.assertEqual(states, ["open", "closed"], done.stdout + done.stderr)


SYSTEM_SCOPE = SCOPE + ["SWE.5", "SWE.6", "SYS.4", "SYS.5"]


def system_items():
    """The integrated software of integration_items(), integrated into the system in one step and qualified."""
    items = integration_items()
    items["SYE-0002"] = ({"type": "system-element", "title": "Vehicle network", "status": "approved", "asil": "B",
                          "security_relevant": False, "kind": "external", "links": {"fulfils": ["SYR-0001"]}},
                         {"Responsibility": "Neighbours.", "Dynamic behavior": "Not applicable: external."})
    items["SYI-0001"] = ({"type": "system-interface", "title": "Obstacle signal", "status": "approved", "asil": "B",
                          "security_relevant": False, "kind": "hardware-software",
                          "imported": {"source": "Customer architecture", "version": "1"},
                          "links": {"fulfils": ["SYR-0001"]}}, {"Definition": "A signal."})
    plan_sections = {"Scope": "The system.", "Approach": "One step.", "Criteria": "All pass.",
                     "Environment and tools": "Bench.", "Responsibilities": "Tester."}
    case = {"status": "approved", "asil": "B", "execution": "manual", "regression": True}
    items.update({
        "PLN-0005": ({"type": "plan", "title": "System integration strategy", "status": "approved",
                      "kind": "system-integration",
                      "integration_steps": [{"name": "vehicle", "components": ["SYE-0001"], "doubles": ["SYE-0002"]}]},
                     plan_sections),
        "PLN-0006": ({"type": "plan", "title": "System qualification strategy", "status": "approved",
                      "kind": "system-qualification-test"}, plan_sections),
        "SYIT-0001": ({"type": "system-integration-test", "title": "Obstacle signal reaches the software", **case,
                       "environment": "bench", "step": "vehicle", "links": {"verifies": ["SYI-0001"]}},
                      {"Steps": "Signal.", "Expected result": "Seen."}),
        "SYQT-0001": ({"type": "system-qualification-test", "title": "System reverses", **case,
                       "environment": "vehicle", "links": {"verifies": ["SYR-0001"]}},
                      {"Steps": "Block.", "Expected result": "Reverses."}),
        "BLD-0002": ({"type": "build-record", "status": "final", "level": "system", "step": "vehicle",
                      "item_under_test": "B-sample 1", "tool": "bench 3", "executed_at": "2026-01-03T09:00:00",
                      "result": "succeeded",
                      "contents": [{"component": "SYE-0001", "delivered": "abc123", "build": "BLD-0001"}]}, {}),
        "RUN-0004": ({"type": "test-run", "status": "final", "level": "system-integration", "item_under_test": "B-sample 1",
                      "environment": "bench", "executed_at": "2026-01-03T10:00:00", "build": "BLD-0002",
                      "results": [{"test": "SYIT-0001", "verdict": "passed"}]}, {}),
        "RUN-0005": ({"type": "test-run", "status": "final", "level": "system-qualification",
                      "item_under_test": "B-sample 1", "environment": "vehicle", "executed_at": "2026-01-03T11:00:00",
                      "build": "BLD-0002", "results": [{"test": "SYQT-0001", "verdict": "passed"}]}, {}),
    })
    return items


class SystemIntegration(Case):
    def make(self, items=None, **kwargs):
        kwargs.setdefault("scope", SYSTEM_SCOPE)
        kwargs.setdefault("files", INTEGRATION_FILES)
        return super().make(system_items() if items is None else items, **kwargs)

    def test_integrated_and_qualified_system_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_element_in_no_system_step(self):
        items = system_items()
        items["PLN-0005"][0]["integration_steps"] = [{"name": "vehicle", "components": ["SYE-0002"]}]
        self.assertIn(("COV-46", "SYE-0001"), self.make(items).rules())

    def test_system_build_with_older_software(self):
        items = system_items()
        items["BLD-0003"] = changed(items, "BLD-0001", executed_at="2026-01-02T09:30:00")["BLD-0001"]
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-47"]
        self.assertTrue(any("older than the software" in m for m in messages), messages)

    def test_system_integration_test_without_a_step_of_the_plan(self):
        items = changed(system_items(), "SYIT-0001", step="bench")
        rules = self.make(items).rules()
        self.assertIn(("COV-48", "SYIT-0001"), rules)
        self.assertIn(("COV-48", "PLN-0005"), rules)

    def test_qualification_on_a_software_build_is_not_a_system_build(self):
        items = changed(system_items(), "RUN-0005", build="BLD-0001", item_under_test="abc123")
        self.assertIn(("COV-49", "RUN-0005"), self.make(items).rules())

    def test_software_and_system_steps_are_kept_apart(self):
        items = system_items()
        items["PLN-0005"][0]["integration_steps"] = [{"name": "detection", "components": ["SYE-0001"],
                                                      "doubles": ["SYE-0002"]}]
        items["BLD-0002"][0]["step"] = "detection"
        items["SYIT-0001"][0]["step"] = "detection"
        self.assertEqual(self.make(items).findings(), [])        # same step name at both levels


RISK_SCOPE = SCOPE + ["MAN.5"]


def risk_items(**risk):
    """The base thread with a risk-management plan and one risk in treatment."""
    items = base_items()
    items["PLN-0003"] = ({"type": "plan", "title": "Risk management plan", "status": "approved", "kind": "risk-management",
                          "risk_categories": ["technical", "supplier"],
                          "risk_scale": {"probability_levels": 5, "impact_levels": 5, "acceptable_up_to": 6}},
                         {"Scope": "Project risks.", "Approach": "Monthly.", "Criteria": "Exposure.",
                          "Environment and tools": "Items.", "Responsibilities": "Project lead."})
    front = {"type": "risk", "title": "Hall sensor samples late", "status": "in-treatment", "category": "supplier",
             "owner": "Project lead", "identified_at": "2026-01-02", "identified_in": "PLN-0003", "probability": 3,
             "impact": 4, "treatment": [{"action": "second source", "owner": "Purchasing", "state": "open",
                                         "due": "2026-01-20"}],
             "indicators": [{"name": "weeks of delay", "threshold": 2, "value": 1}]}
    front.update(risk)
    items["RSK-0001"] = (front, {"Description": "Late samples.", "Analysis": "One supplier.",
                                 "Treatment and monitoring": "Second source."})
    return items


class RiskManagement(Case):
    def make(self, items=None, **kwargs):
        kwargs.setdefault("scope", RISK_SCOPE)
        return super().make(risk_items() if items is None else items, **kwargs)

    def test_a_risk_in_treatment_with_indicators_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_ratings_outside_the_scale_and_an_unknown_category(self):
        items = risk_items(probability=6, category="weather")
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-50"]
        self.assertEqual(len(messages), 2, messages)

    def test_exposure_above_the_threshold_needs_treatment_or_an_accepted_decision(self):
        items = risk_items(status="analysed")
        for key in ("treatment", "indicators"):
            items["RSK-0001"][0].pop(key)
        fixture = self.make(items)
        self.assertIn(("COV-51", "RSK-0001"), fixture.rules("warning"))
        fixture.edit("RSK-0001", status="accepted", decision="P. Lead, 2026-01-05: second source too expensive")
        self.assertNotIn("COV-51", {r for r, _ in fixture.rules("warning") + fixture.rules("error")})

    def test_a_risk_in_treatment_needs_indicators(self):
        items = risk_items()
        items["RSK-0001"][0].pop("indicators")
        rules = self.make(items).rules()
        self.assertIn(("SCHEMA", "RSK-0001"), rules)
        self.assertIn(("COV-52", "RSK-0001"), rules)

    def test_risks_lists_overdue_treatment_by_exposure(self):
        from traceability import risks
        data = risks(Project(self.make().root), as_of(2026, 1, 25))
        entry = data["risks"][0]
        self.assertEqual((entry["exposure"], entry["above_threshold"], entry["actions_overdue"]),
                         (12, True, ["second source"]))


QA_SCOPE = SCOPE + ["SUP.1"]


def quality_items():
    """The base thread with a quality assurance plan, one process check with a finding, and a report."""
    items = base_items()
    items["PLN-0003"] = ({"type": "plan", "title": "Quality assurance plan", "status": "approved",
                          "kind": "quality-assurance",
                          "quality_checks": [{"name": "release audit", "kind": "process", "scope": ["SWE.4"],
                                              "before": ["release candidate"]}],
                          "escalation": [{"after_days": 7, "to": ["Project lead"]}]},
                         {"Scope": "SWE.4.", "Approach": "Audits.", "Criteria": "Plan.", "Environment and tools": "Items.",
                          "Responsibilities": "Quality engineer."})
    items["QAR-0001"] = ({"type": "quality-record", "status": "final", "kind": "process", "check": "release audit",
                          "subject": ["SWE.4"], "criteria": "PLN-0001", "checked_by": "Q. Engineer",
                          "checked_at": "2026-01-05", "result": "conforms-with-findings",
                          "findings": [{"id": "F1", "text": "No regression rule.", "action": "CA-0001"}],
                          "facts": [{"process": "SWE.4", "practices": []}]},
                         {"Summary": "One finding."})
    items["CA-0001"] = ({"type": "corrective-action", "title": "Write the regression rule", "status": "open",
                         "owner": "Developer", "due": "2026-01-10", "raised_in": "QAR-0001"},
                        {"Deviation": "No rule.", "Action": "Write it."})
    items["QAR-0002"] = ({"type": "quality-record", "status": "final", "kind": "summary", "subject": ["QAR-0001"],
                          "criteria": "PLN-0003", "checked_by": "Q. Engineer", "checked_at": "2026-01-06",
                          "result": "conforms-with-findings", "findings": [{"id": "F1", "text": "Open.", "action": "CA-0001"}],
                          "facts": {}}, {"Summary": "Report."})
    items["BL-0001"] = ({"type": "baseline", "status": "final", "tag": "rc1", "purpose": "release candidate",
                         "created_at": "2026-01-06T10:00:00+00:00",
                         "items": [{"item": "SWR-0001", "hash": "x", "status": "approved"}]}, {})
    items["CMR-0001"] = ({"type": "communication-record", "status": "final", "subject": ["QAR-0002", "BL-0001"],
                          "audience": ["Project lead"], "channel": "mail", "sent_at": "2026-01-06"}, {})
    return items


class QualityAssurance(Case):
    def make(self, items=None, **kwargs):
        kwargs.setdefault("scope", QA_SCOPE)
        return super().make(quality_items() if items is None else items, **kwargs)

    def test_checked_reported_and_communicated_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_baseline_before_the_check_the_plan_asks_for(self):
        items = changed(quality_items(), "QAR-0001", checked_at="2026-01-07")
        self.assertIn(("COV-43", "BL-0001"), self.make(items).rules())

    def test_a_check_of_the_same_day_counts_only_when_written_before_the_baseline(self):
        items = changed(quality_items(), "QAR-0001", checked_at="2026-01-06", recorded_at="2026-01-06T11:00:00+00:00")
        self.assertIn(("COV-43", "BL-0001"), self.make(items).rules())
        items = changed(quality_items(), "QAR-0001", checked_at="2026-01-06", recorded_at="2026-01-06T09:00:00+00:00")
        self.assertNotIn(("COV-43", "BL-0001"), self.make(items).rules())

    def test_finding_without_an_existing_action(self):
        items = changed(quality_items(), "QAR-0001",
                        findings=[{"id": "F1", "text": "No regression rule.", "action": "CA-0099"}])
        self.assertIn(("COV-44", "QAR-0001"), self.make(items).rules())

    def test_report_not_communicated(self):
        items = changed(quality_items(), "CMR-0001", subject=["BL-0001"])
        self.assertIn(("COV-45", "QAR-0002"), self.make(items).rules())

    def test_overdue_non_conformance_is_due_for_escalation_until_escalated(self):
        from traceability import quality
        fixture = self.make()
        data = quality(Project(fixture.root), as_of(2026, 1, 20))
        finding = data["findings"][0]
        self.assertEqual((finding["overdue_days"], finding["escalation_due"]), (10, ["Project lead"]))
        self.assertEqual(data["checks"][0]["last"], "QAR-0001")
        fixture.write("CMR-0002", {"type": "communication-record", "status": "final", "subject": "CA-0001",
                                   "audience": ["Project lead"], "channel": "meeting", "sent_at": "2026-01-19",
                                   "practices": ["SUP.1.BP6"], "agreement": "a second developer from 2026-01-20"}, {})
        finding = quality(Project(fixture.root), as_of(2026, 1, 20))["findings"][0]
        self.assertEqual(finding["escalation_due"], [])
        self.assertEqual(finding["responses"], ["a second developer from 2026-01-20"])


def as_of(year, month, day):
    import datetime
    return datetime.date(year, month, day)


INTEGRATION_SCOPE = SCOPE + ["SWE.5", "SWE.6"]
INTEGRATION_FILES = {"tests/test_integration.c": "static void test_SIT_0001(void)\n{\n}\n",
                     "tests/test_qualification.c": "static void test_SQT_0001(void)\n{\n}\n"}


def integration_items():
    """The base thread, integrated in one step, with a passed integration and qualification test."""
    items = base_items()
    plan_sections = {"Scope": "All components.", "Approach": "Step by step.", "Criteria": "All pass.",
                     "Environment and tools": "Host.", "Responsibilities": "Tester."}
    case = {"status": "approved", "asil": "B", "execution": "automated", "regression": True}
    steps_text = {"Steps": "Run the step.", "Expected result": "The state is reported."}
    items.update({
        "PLN-0003": ({"type": "plan", "title": "Software integration strategy", "status": "approved",
                      "kind": "software-integration",
                      "integration_steps": [{"name": "detection", "components": ["CMP-0001"], "environment": "host"}]},
                     plan_sections),
        "PLN-0004": ({"type": "plan", "title": "Software qualification test strategy", "status": "approved",
                      "kind": "software-qualification-test"}, plan_sections),
        "SIT-0001": ({"type": "software-integration-test", "title": "Obstacle state is passed on", **case,
                      "script": "tests/test_integration.c::test_SIT_0001", "environment": "host", "step": "detection",
                      "links": {"verifies": ["IFC-0001"]}}, steps_text),
        "SQT-0001": ({"type": "software-qualification-test", "title": "Obstacle detected in time", **case,
                      "script": "tests/test_qualification.c::test_SQT_0001", "environment": "software-in-the-loop",
                      "links": {"verifies": ["SWR-0001"]}}, steps_text),
        "BLD-0001": ({"type": "build-record", "status": "final", "step": "detection", "item_under_test": "abc123",
                      "tool": "gcc 13", "executed_at": "2026-01-02T09:00:00", "result": "succeeded",
                      "contents": [{"component": "CMP-0002", "units": ["UNT-0001"]}], "sources": "auto"}, {}),
        "RUN-0002": ({"type": "test-run", "status": "final", "level": "software-integration", "item_under_test": "abc123",
                      "environment": "host", "executed_at": "2026-01-02T11:00:00", "build": "BLD-0001",
                      "results": [{"test": "SIT-0001", "verdict": "passed"}]}, {}),
        "RUN-0003": ({"type": "test-run", "status": "final", "level": "software-qualification",
                      "item_under_test": "abc123", "environment": "software-in-the-loop",
                      "executed_at": "2026-01-02T12:00:00", "build": "BLD-0001",
                      "results": [{"test": "SQT-0001", "verdict": "passed"}]}, {}),
    })
    return items


SUPPLIED = ({"type": "software-component", "title": "Platform", "status": "approved", "asil": "B",
             "security_relevant": False, "kind": "basic-software", "layer": "services", "origin": "supplied",
             "supplier": "the customer, as object code", "resource_budget": {"not_relevant": "customer's"}},
            {"Purpose": "Platform services the customer supplies.", "Responsibility": "Timers.",
             "Dynamic behavior": "Not applicable: services only."})


CS_SUBCLAUSES = ["6.4.%d" % n for n in range(1, 10)] + ["9.3", "9.4", "9.5"] + ["15.%d" % n for n in range(3, 10)]
CS_CONFIG = {"scope": {"processes": SCOPE, "cybersecurity": [6, 9, 15]}}
PLAN_SECTIONS = {"Scope": "The window lifter.", "Approach": "TARA, then goals and concept.", "Criteria": "Reviewed.",
                 "Environment and tools": "Repository.", "Responsibilities": "Cybersecurity lead."}


def cs_items():
    """The base thread with a small TARA on top: one asset, one damage, one threat reduced by one goal."""
    items = copy.deepcopy(base_items())
    for front, _ in items.values():
        if "security_relevant" in front:
            front["security_relevant"] = True
    items["SWR-0001"][0]["links"]["derived_from"].append("CSG-0001")
    items["PLN-0009"] = ({"type": "plan", "title": "Cybersecurity plan", "status": "approved", "kind": "cybersecurity",
                          "tara_method": {"impact_categories": ["safety", "financial", "operational", "privacy"],
                                          "impact_meaning": "severe: a road user can be hurt; major: ...",
                                          "feasibility_approach": "attack-vector", "retain_up_to": 2,
                                          "feasibility_meaning": "high: remote; medium: ...",
                                          "risk_matrix": {"severe": [3, 4, 5, 5], "major": [2, 3, 4, 5],
                                                          "moderate": [1, 2, 3, 4], "negligible": [1, 1, 2, 2]}},
                          "cybersecurity_activities": [{"subclause": s, "decision": "performed",
                                                        "responsible": "Cybersecurity lead"} for s in CS_SUBCLAUSES]},
                         PLAN_SECTIONS)
    items["ITM-0001"] = ({"type": "item-definition", "title": "Window lifter", "status": "approved"},
                         {"Boundary and functions": "Door module and motor.", "Preliminary architecture": "One ECU.",
                          "Operational environment": "Body bus."})
    items["AST-0001"] = ({"type": "asset", "title": "Close command on the bus", "status": "approved",
                          "properties": ["integrity", "authenticity"], "links": {"located_in": ["ITM-0001"]}},
                         {"Description": "The frame that asks the window to close."})
    items["DMG-0001"] = ({"type": "damage-scenario", "title": "Window closes on a hand", "status": "approved",
                          "impact": {"safety": "major", "financial": "negligible", "operational": "moderate",
                                     "privacy": "negligible"}},
                         {"Description": "A passenger is hurt.", "Impact rationale": "Pinching, bounded force."})
    items["THR-0001"] = ({"type": "threat-scenario", "title": "Spoofed close command", "status": "approved",
                          "property": "integrity", "feasibility": "medium", "risk_value": 4, "treatment": ["reduce"],
                          "attack_paths": [{"path": "diagnostic port, forged frame", "feasibility": "medium"},
                                           {"path": "telematics unit, then the bus", "feasibility": "low"}],
                          "links": {"threatens": ["AST-0001"], "leads_to": ["DMG-0001"]}},
                         {"Description": "A forged frame closes the window.", "Treatment rationale": "Reduce: authenticate."})
    items["CSG-0001"] = ({"type": "cybersecurity-goal", "title": "Close commands are authentic", "status": "approved",
                          "links": {"addresses": ["THR-0001"]}}, {"Statement": "Only authentic commands move the window."})
    return items


class Cybersecurity(Case):
    CS_RULES = {"COV-%d" % n for n in range(53, 63)}

    def make(self, items=None, config=CS_CONFIG, **kwargs):
        return super().make(cs_items() if items is None else items, config=config, **kwargs)

    def cs_findings(self, fixture, level="error"):
        return sorted({(f["rule"], f["item"]) for f in fixture.findings(level)
                       if f["rule"] in self.CS_RULES or f["rule"] in ("SCHEMA", "LINK")})

    def test_a_consistent_tara_has_no_findings(self):
        fixture = self.make()
        self.assertEqual(fixture.findings("error"), [])
        self.assertEqual(self.cs_findings(fixture, "warning"), [])

    def test_out_of_scope_the_rules_stay_silent(self):
        fixture = self.make(config={})
        self.assertFalse({r for r, _ in fixture.rules()} & self.CS_RULES)
        items = cs_items()
        del items["PLN-0009"]
        self.assertNotIn(("COV-27", "project"), self.make(items, config={}).rules())

    def test_a_clause_in_scope_needs_the_cybersecurity_plan(self):
        items = cs_items()
        del items["PLN-0009"]
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-27"]
        self.assertIn("no approved plan of kind cybersecurity", messages)

    def test_the_plan_decides_every_subclause_in_scope(self):
        items = cs_items()
        activities = items["PLN-0009"][0]["cybersecurity_activities"]
        activities[:] = [a for a in activities if a["subclause"] != "15.9"]
        activities[0].update(decision="tailored")
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-53"]
        self.assertTrue(any("subclause 15.9 Risk treatment decision" in m for m in messages), messages)
        self.assertTrue(any("6.4.1 is tailored without a rationale" in m for m in messages), messages)

    def test_damage_is_rated_in_every_category_of_the_plan(self):
        items = cs_items()
        del items["DMG-0001"][0]["impact"]["privacy"]
        items["DMG-0001"][0]["impact"]["reputation"] = "major"
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-55"]
        self.assertEqual(len(messages), 2, messages)

    def test_feasibility_is_the_highest_of_the_attack_paths(self):
        fixture = self.make(changed(cs_items(), "THR-0001", feasibility="low", risk_value=3))
        messages = [f["message"] for f in fixture.findings("error") if f["rule"] == "COV-56"]
        self.assertTrue(messages and "highest of its attack paths is medium" in messages[0], messages)

    def test_risk_value_follows_the_matrix_of_the_plan(self):
        fixture = self.make(changed(cs_items(), "THR-0001", risk_value=3))
        messages = [f["message"] for f in fixture.findings("error") if f["rule"] == "COV-57"]
        self.assertTrue(messages and "gives 4 for impact major and feasibility medium" in messages[0], messages)

    def test_a_tara_without_method_is_not_assessed(self):
        items = cs_items()
        del items["PLN-0009"][0]["tara_method"]
        fixture = self.make(items)
        warnings = [f for f in fixture.findings("warning") if f["rule"] == "COV-57"]
        self.assertTrue(warnings and "not assessed" in warnings[0]["message"], warnings)

    def test_reduce_needs_a_goal_and_retain_a_claim(self):
        items = cs_items()
        items["CSG-0001"][0]["links"]["addresses"] = []
        self.assertIn(("COV-58", "THR-0001"), self.make(items).rules())
        fixture = self.make(changed(cs_items(), "THR-0001", treatment=["retain"]))
        messages = [f["message"] for f in fixture.findings("error") if f["rule"] == "COV-58"]
        self.assertTrue(any("no cybersecurity claim" in m for m in messages), messages)
        self.assertTrue(any("above 2 (retain_up_to of PLN-0009)" in m for m in messages), messages)

    def test_a_goal_is_refined_into_requirements(self):
        items = cs_items()
        items["SWR-0001"][0]["links"]["derived_from"] = ["SYR-0001"]
        self.assertIn(("COV-59", "CSG-0001"), self.make(items).rules())

    def test_what_is_derived_from_a_goal_is_security_relevant(self):
        fixture = self.make(changed(cs_items(), "SWR-0001", security_relevant=False))
        self.assertIn(("COV-60", "SWR-0001"), fixture.rules())
        self.assertNotIn(("COV-60", "CMP-0002"), fixture.rules())          # it fulfils a requirement that is not

    def test_listed_values_are_checked(self):
        fixture = self.make(changed(cs_items(), "AST-0001", properties=["integrity", "secrecy"]))
        self.assertIn(("SCHEMA", "AST-0001"), fixture.rules())

    def test_a_vulnerability_to_reduce_needs_its_change(self):
        items = cs_items()
        items["WKN-0001"] = ({"type": "weakness", "title": "Old library version", "status": "in-resolution",
                              "reported_at": "2026-03-01", "found_by": "monitoring", "source": "advisory 2026-17",
                              "vulnerability": True, "risk_value": 3, "treatment": ["reduce"],
                              "links": {"affects": ["UNT-0001"]}},
                             {"Description": "The unit uses an affected version.", "Analysis": "Reachable from the bus."})
        monitoring = {"scope": {"processes": SCOPE, "cybersecurity": [8]}}
        self.assertIn(("COV-61", "WKN-0001"), self.make(items, config=monitoring).rules())
        self.assertNotIn(("COV-61", "WKN-0001"), self.make(items).rules())     # clause 8 not in scope
        items["CR-0001"] = ({"type": "change-request", "title": "Update the library", "status": "approved",
                             "requester": "Cybersecurity lead", "decision": "CCB, 2026-03-02",
                             "links": {"resolves": ["WKN-0001"], "affects": ["UNT-0001"]}},
                            {"Description": "Update.", "Impact analysis": "One unit."})
        self.assertNotIn(("COV-61", "WKN-0001"), self.make(items, config=monitoring).rules())

    def test_a_vulnerability_is_rated_by_the_matrix_and_may_be_corrected_by_another_party(self):
        items = cs_items()
        items["WKN-0001"] = ({"type": "weakness", "title": "Stack weakness", "status": "in-resolution",
                              "reported_at": "2026-03-01", "found_by": "monitoring", "source": "bulletin 7",
                              "vulnerability": True, "impact": "major", "feasibility": "medium", "risk_value": 2,
                              "treatment": ["reduce"], "corrected_by": "platform release 4.3 of the customer, in B2",
                              "links": {"affects": ["UNT-0001"]}},
                             {"Description": "In the platform.", "Analysis": "Reachable from the bus."})
        monitoring = {"scope": {"processes": SCOPE, "cybersecurity": [8]}}
        messages = [f["message"] for f in self.make(items, config=monitoring).findings() if f["rule"] == "COV-61"]
        self.assertEqual(len(messages), 1, messages)                          # corrected_by carries the reduction
        self.assertIn("gives 4 for impact major and feasibility medium", messages[0])
        items["WKN-0001"][0]["risk_value"] = 4
        self.assertNotIn(("COV-61", "WKN-0001"), self.make(items, config=monitoring).rules())

    def test_a_relevant_event_leads_to_weaknesses(self):
        items = cs_items()
        items["CEV-0001"] = ({"type": "cybersecurity-event", "title": "Bulletin 7", "status": "closed",
                              "received_at": "2026-03-01", "source": "supplier bulletin 7", "trigger": "component in use",
                              "relevant": True, "triaged_by": "Cybersecurity lead, 2026-03-02"},
                             {"Description": "Stack weakness.", "Triage": "The release is in use."})
        monitoring = {"scope": {"processes": SCOPE, "cybersecurity": [8]}}
        self.assertIn(("COV-78", "CEV-0001"), self.make(items, config=monitoring).rules())
        items["CEV-0001"][0]["relevant"] = False
        self.assertNotIn(("COV-78", "CEV-0001"), self.make(items, config=monitoring).rules())

    def test_tara_lists_threats_with_what_their_risk_rests_on(self):
        from traceability import tara
        fixture = self.make(changed(cs_items(), "THR-0001", risk_value=3))
        data = tara(Project(fixture.root))
        entry = data["threat_scenarios"][0]
        self.assertEqual((entry["impact"], entry["feasibility"], entry["risk_value"], entry["matrix_value"]),
                         ("major", "medium", 3, 4))
        self.assertEqual(entry["goals"], ["CSG-0001"])
        self.assertEqual(data["figures"]["risk_value_differs"], 1)

    def test_clauses_show_the_evidence_per_work_product(self):
        from traceability import clause_rows
        rows = {r["subclause"]: r for r in clause_rows(Project(self.make().root))}
        self.assertEqual(set(rows), set(CS_SUBCLAUSES))
        goals = {w["work_product"]: w for w in rows["9.4"]["work_products"]}
        self.assertEqual((goals["WP-09-03"]["items"], goals["WP-09-02"]["items"]), (1, 1))
        concept = {w["work_product"]: w for w in rows["9.5"]["work_products"]}
        self.assertEqual(concept["WP-09-06"]["items"], 1)                  # SWR-0001, derived from the goal
        self.assertEqual(rows["6.4.2"]["decision"], "performed")
        self.assertEqual(rows["9.4"]["state"], "evidence present")

    def test_an_item_definition_counts_and_a_review_counts_only_for_its_own_subclause(self):
        from traceability import clause_rows
        example = Project(Path(__file__).resolve().parents[2] / "examples" / "power-window")
        rows = {r["subclause"]: r for r in clause_rows(example, "9")}
        item = {w["work_product"]: w for w in rows["9.3"]["work_products"]}["WP-09-01"]
        self.assertEqual([e["item"] for e in item["evidence"]], ["ITM-0001"])     # used by ISO 26262 as well
        concept = {w["work_product"]: w for w in rows["9.5"]["work_products"]}
        self.assertEqual(concept["WP-09-07"]["items"], 0)          # the reviews of goals are no review of a concept


FS_CONFIG = {"scope": {"processes": SCOPE, "safety": [2, 3, 6, 8, 9]}}


def fs_items():
    """The base thread under ISO 26262: a hazardous event, its goal, the goal refined into SWR-0001, a safety
    analysis of the ASIL B component, the analyser evaluated, a confirmation review. The ASIL determination
    is a test value, not the one of the standard."""
    import yaml as _yaml
    catalog = _yaml.safe_load((Path(__file__).resolve().parents[2] / "iso-26262" / "2018" / "catalog.yaml").read_text(encoding="utf-8"))
    parts = {str(p["id"]): p for p in catalog["parts"]}
    clauses = ["%s:%s" % (n, c["id"]) for n in ("2", "3", "6", "8", "9") for c in parts[n]["clauses"]]
    tables = ["%s:%s" % (n, tb["id"]) for n in ("6", "8") for tb in parts[n]["tables"]]
    items = copy.deepcopy(base_items())
    items["SWR-0001"][0]["links"]["derived_from"].append("SG-0001")
    items["PLN-0009"] = ({"type": "plan", "title": "Safety plan", "status": "approved", "kind": "safety",
                          "safety_activities": [{"clause": c, "decision": "performed", "responsible": "Safety manager"}
                                                for c in clauses],
                          "method_selection": [{"table": tb, "decision": "applied", "applied_in": "PLN-0001"} for tb in tables],
                          "confirmation_measures": [{"measure": "confirmation-review", "subject": "safety plan",
                                                     "independence": "I1"}],
                          "asil_determination": {"S1E4C2": "B"}, "tcl_determination": {"TI2-TD1": "TCL1"}},
                         {"Scope": "The window software.", "Approach": "Per clause.", "Criteria": "Reviewed.",
                          "Environment and tools": "Repository.", "Responsibilities": "Safety manager."})
    items["ITM-0001"] = ({"type": "item-definition", "title": "Window lifter", "status": "approved"},
                         {"Boundary and functions": "Door module.", "Preliminary architecture": "One ECU.",
                          "Operational environment": "Vehicle."})
    for plan_id, kind, extra in (("PLN-0010", "software-integration", {"integration_steps": [{"name": "all", "components": ["CMP-0002"]}]}),
                                 ("PLN-0011", "software-qualification-test", {}), ("PLN-0012", "change-request-management", {}),
                                 ("PLN-0013", "development-interface-agreement",
                                  {"shared_activities": [{"activity": "3:6", "customer": "R", "supplier": "I"}]})):
        items[plan_id] = ({"type": "plan", "title": kind, "status": "approved", "kind": kind, **extra},
                          {"Scope": "x", "Approach": "x", "Criteria": "x", "Environment and tools": "x", "Responsibilities": "x"})
    items["HZE-0001"] = ({"type": "hazardous-event", "title": "Arm trapped while closing", "status": "approved",
                          "malfunction": "closes against an obstacle", "hazard": "trapping", "operational_situation": "parked, child inside",
                          "severity": "S1", "exposure": "E4", "controllability": "C2", "asil": "B",
                          "links": {"arises_in": ["ITM-0001"]}},
                         {"Description": "The window does not reverse.", "Classification rationale": "Test values."})
    items["SG-0001"] = ({"type": "safety-goal", "title": "No trapping by the window", "status": "approved", "asil": "B",
                         "links": {"addresses": ["HZE-0001"]}}, {"Statement": "The window shall not trap an occupant."})
    items["SAN-0001"] = ({"type": "safety-analysis", "title": "FMEA of the detection", "status": "approved",
                          "method": "fmea", "level": "software",
                          "findings": [{"id": "F1", "fault": "obstacle not reported", "effect": "no reversal",
                                        "measure": "plausibility of the speed", "carried_by": "SWR-0001", "state": "closed"}],
                          "links": {"analyses": ["CMP-0002"]}},
                         {"Scope": "CMP-0002.", "Method": "Guide words per output.", "Results": "One finding, closed."})
    items["TEV-0001"] = ({"type": "tool-evaluation", "title": "Static analyser", "status": "approved", "tool": "analyser 1.0",
                           "impact": "TI2", "detection": "TD1", "confidence": "TCL1", "asil": "B"},
                          {"Use cases": "Defect analysis of the units.", "Classification rationale": "Findings are reviewed."})
    items["CFM-0001"] = ({"type": "confirmation-measure", "status": "final", "kind": "confirmation-review",
                          "subject": "safety plan", "items": [], "performed_by": "Independent reviewer",
                          "independence": "I1", "as_of": "2026-02-01", "result": "passed"}, {"Report": "Consistent."})
    return items


class FunctionalSafety(Case):
    FS_RULES = {"COV-%d" % n for n in range(63, 74)}

    def make(self, items=None, config=FS_CONFIG, **kwargs):
        return super().make(fs_items() if items is None else items, config=config, **kwargs)

    def fs_rules(self, fixture, level="error"):
        return sorted((r, i) for r, i in fixture.rules(level) if r in self.FS_RULES or r in ("SCHEMA", "LINK"))

    def messages(self, fixture, rule, level="error"):
        return [f["message"] for f in fixture.findings(level) if f["rule"] == rule]

    def test_a_consistent_safety_thread_has_no_findings(self):
        fixture = self.make()
        self.assertEqual(fixture.findings("error"), [])
        self.assertEqual(self.fs_rules(fixture, "warning"), [])

    def test_out_of_scope_the_rules_stay_silent(self):
        items = fs_items()
        del items["PLN-0009"], items["TEV-0001"]
        fixture = self.make(items, config={})
        self.assertFalse({r for r, _ in fixture.rules()} & (self.FS_RULES | {"COV-27"}))

    def test_the_plan_decides_every_clause_and_every_method_table(self):
        items = fs_items()
        plan = items["PLN-0009"][0]
        plan["safety_activities"] = [a for a in plan["safety_activities"] if a["clause"] != "6:7"]
        plan["method_selection"] = [m for m in plan["method_selection"] if m["table"] != "6:9"]
        plan["method_selection"][0].update(decision="not-applicable")
        fixture = self.make(items)
        self.assertTrue(any("clause 6:7 Software architectural design" in m for m in self.messages(fixture, "COV-63")))
        self.assertTrue(any("table 6:9" in m for m in self.messages(fixture, "COV-64")))
        self.assertTrue(any("not-applicable without a rationale" in m for m in self.messages(fixture, "COV-64")))

    def test_a_method_table_may_be_pending_until_its_date(self):
        items = fs_items()
        items["PLN-0009"][0]["method_selection"][0].update(decision="pending", due="2999-01-01", responsible="Safety manager")
        fixture = self.make(items)
        self.assertEqual(self.messages(fixture, "COV-64"), [])
        self.assertTrue(any("pending until 2999-01-01" in m for m in self.messages(fixture, "COV-64", "warning")))
        items["PLN-0009"][0]["method_selection"][0].update(due="2020-01-01")
        self.assertTrue(any("was due on 2020-01-01" in m for m in self.messages(self.make(items), "COV-64")))

    def test_a_clause_decision_limited_to_named_components(self):
        items = fs_items()
        items["CMP-0002"][0]["origin"] = "supplied"
        items["CMP-0002"][0]["supplier"] = "Library vendor"
        for entry in items["PLN-0009"][0]["safety_activities"]:
            if entry["clause"] == "8:12":
                entry.update(decision="not-applicable", rationale="the platform is under the DIA", items=["CMP-0099"])
        self.assertIn(("COV-75", "CMP-0002"), self.make(items).rules())
        for entry in items["PLN-0009"][0]["safety_activities"]:
            if entry["clause"] == "8:12":
                entry["items"] = ["CMP-0002"]
        self.assertNotIn(("COV-75", "CMP-0002"), self.make(items).rules())

    def test_the_asil_follows_the_determination_the_plan_states(self):
        fixture = self.make(changed(fs_items(), "HZE-0001", asil="A"))
        self.assertTrue(any("gives B for S1E4C2" in m for m in self.messages(fixture, "COV-65")))
        items = fs_items()
        del items["PLN-0009"][0]["asil_determination"]
        warnings = self.messages(self.make(items), "COV-65", "warning")
        self.assertTrue(warnings and "not assessed" in warnings[0], warnings)

    def test_a_hazardous_event_needs_a_goal_of_its_asil(self):
        fixture = self.make(changed(fs_items(), "SG-0001", asil="A"))
        self.assertIn(("COV-66", "SG-0001"), fixture.rules())
        items = fs_items()
        items["SG-0001"][0]["links"]["addresses"] = []
        self.assertIn(("COV-66", "HZE-0001"), self.make(items).rules())

    def test_a_goal_is_refined_into_requirements(self):
        items = fs_items()
        items["SWR-0001"][0]["links"]["derived_from"] = ["SYR-0001"]
        self.assertIn(("COV-67", "SG-0001"), self.make(items).rules())

    def test_findings_of_an_analysis_are_carried_or_argued(self):
        items = fs_items()
        items["SAN-0001"][0]["findings"][0].pop("carried_by")
        self.assertTrue(any("without carried_by or a rationale" in m for m in self.messages(self.make(items), "COV-68")))
        items = fs_items()
        items["SAN-0001"][0]["findings"][0]["state"] = "open"
        self.assertTrue(any("approved with finding F1 open" in m for m in self.messages(self.make(items), "COV-68")))

    def test_safety_relevant_components_are_analysed_and_mixed_asils_need_a_dfa(self):
        items = fs_items()
        items["SAN-0001"][0]["links"]["analyses"] = ["IFC-0001"]
        self.assertIn(("COV-69", "CMP-0002"), self.make(items).rules())
        items = fs_items()
        items["CMP-0003"] = ({"type": "software-component", "title": "Diagnostics", "status": "approved", "asil": "QM",
                              "security_relevant": False, "kind": "application", "layer": "application", "origin": "developed",
                              "resource_budget": {"rom_bytes": 512}, "links": {"part_of": ["CMP-0001"]}},
                             {"Purpose": "Logs.", "Responsibility": "Logs.", "Dynamic behavior": "On request."})
        self.assertTrue(any("no software-level dependent failures analysis" in m
                            for m in self.messages(self.make(items), "COV-69")))

    def test_a_decomposition_rests_on_a_dependent_failures_analysis(self):
        items = fs_items()
        items["ADR-0001"] = ({"type": "design-decision", "title": "Split the detection", "status": "approved",
                              "level": "software", "decomposition": {"requirement": "SWR-0001", "into": ["SWR-0001"],
                                                                     "independence": "SAN-0001"},
                              "links": {"concerns": ["CMP-0002"]}},
                             {"Context": "x", "Evaluation criteria": "x", "Alternatives": "x", "Decision": "x", "Consequences": "x"})
        self.assertTrue(any("not a live dependent failures analysis" in m for m in self.messages(self.make(items), "COV-70")))

    def test_tools_are_evaluated_and_their_confidence_follows_the_plan(self):
        fixture = self.make(changed(fs_items(), "TEV-0001", tool="other analyser 2"))
        self.assertTrue(any("analyser 1.0" in m for m in self.messages(fixture, "COV-72")))
        items = fs_items()
        items["PLN-0009"][0]["tcl_determination"] = {"TI2-TD1": "TCL2"}
        self.assertIn(("COV-71", "TEV-0001"), self.make(items).rules())
        fixture = self.make(changed(fs_items(), "TEV-0001", confidence="TCL2"))
        self.assertIn(("SCHEMA", "TEV-0001"), fixture.rules())                # a qualification method is due

    def test_confirmation_measures_need_their_records_with_enough_independence(self):
        fixture = self.make(changed(fs_items(), "CFM-0001", independence="I0"))
        self.assertTrue(any("do not reach independence I1" in m for m in self.messages(fixture, "COV-73")))

    def test_a_plan_in_work_is_checked_at_the_level_of_its_state(self):
        items = fs_items()
        items["PLN-0009"][0]["status"] = "in-review"
        items["PLN-0009"][0]["safety_activities"] = items["PLN-0009"][0]["safety_activities"][1:]
        fixture = self.make(items)
        self.assertIn(("COV-63", "PLN-0009"), fixture.rules("warning"))
        self.assertNotIn(("COV-63", "PLN-0009"), fixture.rules("error"))

    def test_evidence_per_clause_is_safety_evidence_only(self):
        from traceability import safety_rows
        items = fs_items()
        items["SWR-0002"] = (dict(items["SWR-0001"][0], title="Logging", asil="QM", links={"derived_from": ["SYR-0001"]}),
                             items["SWR-0001"][1])
        rows = {r["clause"]: r for r in safety_rows(Project(self.make(items).root))}
        evidence = {e["item"] for e in rows["6:6"]["evidence"]}
        self.assertIn("SWR-0001", evidence)
        self.assertNotIn("SWR-0002", evidence)

    def test_a_supplier_agreement_needs_the_evaluation_that_selected_the_supplier(self):
        items = fs_items()
        items["SAG-0001"] = ({"type": "supplier-agreement", "title": "Library supply", "status": "approved",
                              "supplier": "Example Libraries Ltd", "components": ["CMP-0002"],
                              "exchanges": [{"name": "releases", "direction": "from-supplier", "content": "library"}],
                              "meetings": [{"name": "progress", "kind": "progress", "cadence": 30}]},
                             {"Joint processes": "x", "Interfaces and responsibilities": "x", "Deviations and escalation": "x"})
        self.assertIn(("COV-76", "SAG-0001"), self.make(items).rules())
        items["SEV-0001"] = ({"type": "supplier-evaluation", "title": "Evaluation", "status": "approved",
                              "supplier": "Example Libraries Ltd", "scope_of_supply": "library", "result": "selected",
                              "criteria": [{"criterion": "process", "result": "met"}], "decided_by": "P. Lead, 2026-01-02"},
                             {"Request for quotation": "x", "Evaluation": "x", "Decision": "x"})
        self.assertNotIn(("COV-76", "SAG-0001"), self.make(items).rules())

    def test_supplied_asil_components_are_qualified_unless_the_plan_waives_it(self):
        items = fs_items()
        items["CMP-0002"][0]["origin"] = "supplied"
        items["CMP-0002"][0]["supplier"] = "Library vendor"
        fixture = self.make(items)
        self.assertIn(("COV-75", "CMP-0002"), fixture.rules())
        items["CQL-0001"] = ({"type": "component-qualification", "title": "Detection library 1.0", "status": "approved",
                              "version": "1.0", "method": "tests", "evidence": "RUN-0001", "result": "qualified",
                              "links": {"qualifies": ["CMP-0002"]}},
                             {"Specification": "x", "Qualification": "x"})
        self.assertNotIn(("COV-75", "CMP-0002"), self.make(items).rules())
        items = fs_items()
        items["CMP-0002"][0]["origin"] = "supplied"
        items["CMP-0002"][0]["supplier"] = "Customer"
        for entry in items["PLN-0009"][0]["safety_activities"]:
            if entry["clause"] == "8:12":
                entry.update(decision="not-applicable", rationale="developed under ISO 26262 by the customer, see the DIA")
        self.assertNotIn(("COV-75", "CMP-0002"), self.make(items).rules())

    def test_a_proven_in_use_argument_qualifies_an_element_and_is_planned(self):
        items = fs_items()
        items["CMP-0002"][0]["origin"] = "reused"
        items["CMP-0002"][0]["supplier"] = "the earlier door module"
        items["PIU-0001"] = ({"type": "proven-in-use-argument", "title": "Detection carried over", "status": "approved",
                              "candidate_version": "Detection 2.1", "credit": ["6:8", "6:9", "6:99"], "target_asil": "B",
                              "incident_rate_limit": "as the safety plan states", "evaluation_hours": "2e8",
                              "observed_incidents": 0, "result": "obtained", "evidence": "change history; field data",
                              "links": {"qualifies": ["CMP-0002"]}},
                             {"Candidate": "x", "Modifications": "x", "Field data": "x", "Conclusion": "x"})
        fixture = self.make(items)
        self.assertNotIn(("COV-75", "CMP-0002"), fixture.rules())             # proven in use instead of qualification
        self.assertIn(("COV-77", "PIU-0001"), fixture.rules())                  # 6:99 is no clause
        self.assertTrue(any("6:99" in f["message"] for f in fixture.findings() if f["rule"] == "COV-77"))
        items["PIU-0001"][0]["credit"] = ["6:8", "26262-6:9"]
        self.assertNotIn(("COV-77", "PIU-0001"), self.make(items).rules())
        for entry in items["PLN-0009"][0]["safety_activities"]:
            if entry["clause"] == "8:14":
                entry.update(decision="not-applicable", rationale="no proven in use argument is made")
        fixture = self.make(items)
        self.assertTrue(any("clause 8:14 is not-applicable" in f["message"] for f in fixture.findings()
                            if f["rule"] == "COV-77"))

    def test_safety_rows_show_decision_and_evidence_per_clause(self):
        from traceability import safety_rows
        rows = {r["clause"]: r for r in safety_rows(Project(self.make().root))}
        self.assertEqual(rows["6:7"]["decision"], "performed")
        self.assertEqual(rows["6:7"]["state"], "evidence present")
        items = fs_items()
        for entry in items["PLN-0009"][0]["safety_activities"]:
            if entry["clause"] == "9:5":
                entry.update(decision="by-customer")
        items["PLN-0009"][0]["safety_activities"] = [e for e in items["PLN-0009"][0]["safety_activities"] if e["clause"] != "8:7"]
        rows = {r["clause"]: r for r in safety_rows(Project(self.make(items).root))}
        self.assertEqual((rows["9:5"]["state"], rows["8:7"]["state"]), ("not ours", "not decided"))
        evidence = {e["item"] for e in rows["6:7"]["evidence"]}
        self.assertIn("CMP-0002", evidence)
        self.assertIn("SAN-0001", evidence)
        self.assertIn("HZE-0001", {e["item"] for e in rows["3:6"]["evidence"]})


class Integration(Case):
    def make(self, items=None, **kwargs):
        kwargs.setdefault("scope", INTEGRATION_SCOPE)
        kwargs.setdefault("files", INTEGRATION_FILES)
        return super().make(integration_items() if items is None else items, **kwargs)

    def steps(self, items, *steps):
        items["PLN-0003"][0]["integration_steps"] = list(steps)
        return items

    def test_integrated_and_tested_project_has_no_findings(self):
        self.assertEqual(self.make().findings(), [])

    def test_component_in_no_step(self):
        items = integration_items()
        items["CMP-0003"] = copy.deepcopy(SUPPLIED)
        self.assertIn(("COV-35", "CMP-0003"), self.make(items).rules())

    def test_component_left_to_others_is_a_double_of_the_last_step(self):
        items = integration_items()
        items["CMP-0003"] = copy.deepcopy(SUPPLIED)
        self.steps(items, {"name": "detection", "components": ["CMP-0001"], "doubles": ["CMP-0003"]})
        self.assertNotIn("COV-35", {r for r, _ in self.make(items).rules()})

    def test_component_in_two_steps(self):
        items = self.steps(integration_items(), {"name": "detection", "components": ["CMP-0002"]},
                           {"name": "again", "components": ["CMP-0001"]})
        self.assertIn(("COV-35", "CMP-0002"), self.make(items).rules())

    def test_double_for_a_component_already_integrated(self):
        items = integration_items()
        items["CMP-0003"] = copy.deepcopy(SUPPLIED)
        self.steps(items, {"name": "detection", "components": ["CMP-0001", "CMP-0003"]},
                   {"name": "rest", "components": [], "doubles": ["CMP-0002"]})
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-35"]
        self.assertTrue(any("names CMP-0002 as a double" in m for m in messages), messages)

    def test_step_without_build(self):
        items = integration_items()
        for key in ("BLD-0001", "RUN-0002", "RUN-0003"):
            items.pop(key)
        self.assertIn(("COV-36", "PLN-0003"), self.make(items).rules())

    def test_step_without_build_is_pending_while_no_unit_has_code(self):
        items = integration_items()
        for key in ("BLD-0001", "RUN-0002", "RUN-0003"):
            items.pop(key)
        items["UNT-0001"][0].pop("source_files")
        fixture = self.make(items)
        self.assertNotIn(("COV-36", "PLN-0003"), fixture.rules())
        self.assertIn(("COV-36", "PLN-0003"), fixture.rules("warning"))

    def test_code_changed_after_the_build(self):
        fixture = self.make()
        (fixture.root / "src/unit.c").write_text(CODE + "/* changed */\n", encoding="utf-8")
        messages = [f["message"] for f in fixture.findings("error") if f["rule"] == "COV-36"]
        self.assertTrue(any("src/unit.c changed after build BLD-0001" in m for m in messages), messages)

    def test_build_that_lacks_a_unit_with_code(self):
        items = integration_items()
        items["BLD-0001"][0]["contents"] = [{"component": "CMP-0002", "units": []}]
        messages = [f["message"] for f in self.make(items).findings("error") if f["rule"] == "COV-36"]
        self.assertTrue(any("does not contain UNT-0001 of CMP-0002" in m for m in messages), messages)

    def test_failed_build(self):
        items = changed(integration_items(), "BLD-0001", result="failed")
        self.assertIn(("COV-36", "PLN-0003"), self.make(items).rules())

    def test_integration_test_names_a_step_the_plan_does_not_have(self):
        items = changed(integration_items(), "SIT-0001", step="elsewhere")
        rules = self.make(items).rules()
        self.assertIn(("COV-37", "SIT-0001"), rules)
        self.assertIn(("COV-37", "PLN-0003"), rules)            # and the step has no test now

    def test_run_on_a_build_of_another_commit(self):
        items = changed(integration_items(), "RUN-0002", item_under_test="def456")
        self.assertIn(("COV-38", "RUN-0002"), self.make(items).rules())

    def test_run_older_than_the_latest_build_of_its_step(self):
        items = integration_items()
        items["BLD-0002"] = copy.deepcopy(items["BLD-0001"])
        items["BLD-0002"][0]["executed_at"] = "2026-01-03T09:00:00"
        rules = self.make(items).rules()
        self.assertIn(("COV-38", "RUN-0002"), rules)
        self.assertIn(("COV-38", "RUN-0003"), rules)

    def test_integration_verdict_counts_only_from_a_run_on_its_step(self):
        items = integration_items()
        self.steps(items, {"name": "detection", "components": ["CMP-0001"]}, {"name": "complete", "components": []})
        items["SIT-0002"] = copy.deepcopy(items["SIT-0001"])
        items["SIT-0002"][0]["step"] = "complete"
        items["BLD-0002"] = changed(items, "BLD-0001", step="complete", executed_at="2026-01-02T09:30:00")["BLD-0001"]
        items["RUN-0004"] = changed(items, "RUN-0002", build="BLD-0002", executed_at="2026-01-02T11:30:00",
                                    results=[{"test": "SIT-0001", "verdict": "passed"}])["RUN-0002"]
        rules = self.make(items).rules()
        self.assertIn(("COV-18", "SIT-0002"), rules)            # step 'complete' ran, but not SIT-0002
        self.assertNotIn(("COV-18", "SIT-0001"), rules)         # its own step's run still counts

    def test_a_run_is_evidence_for_the_process_of_its_level_only(self):
        from traceability import practice_rows
        rows = {r["practice"]: r for r in practice_rows(Project(self.make().root))}
        self.assertEqual(rows["SWE.6.BP4"]["evidence"], 1)        # RUN-0003, not the unit or integration runs
        self.assertEqual(rows["SWE.5.BP4"]["evidence"], 1)        # BLD-0001

    def test_unreviewed_work_package_counts_against_project_management(self):
        items = integration_items()
        items["WP-0001"] = ({"type": "work-package", "title": "All", "status": "approved", "owner": "Lead",
                             "category": "engineering", "estimate": 5, "planned_start": "2026-01-01",
                             "planned_finish": "2026-02-01"}, {"Description": "All.", "Deliverables": "All.",
                                                                "Estimate basis": "Guess."})
        fixture = self.make(items, review=False)
        fixture.review(without=("WP-0001",))
        finding = next(f for f in fixture.findings("error") if f["rule"] == "COV-19" and f["item"] == "WP-0001")
        self.assertEqual(finding["supports"], [])                 # MAN.3 is not in scope; nothing of SWE is blamed

    def test_qualification_run_without_a_build(self):
        items = integration_items()
        items["RUN-0003"][0].pop("build")
        self.assertIn(("COV-38", "RUN-0003"), self.make(items).rules())

    def test_qualification_without_integration_in_scope_needs_no_build(self):
        items = integration_items()
        for key in ("PLN-0003", "SIT-0001", "BLD-0001", "RUN-0002"):
            items.pop(key)
        items["RUN-0003"][0].pop("build")
        self.assertEqual(self.make(items, scope=SCOPE + ["SWE.6"]).findings(), [])


class Version40(unittest.TestCase):
    """Automotive SPICE 4.0, from its draft: practices and generic practices read through `maps_to`."""
    REPO = Path(__file__).resolve().parents[2]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="v40test-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "p"
        shutil.copytree(str(self.REPO / "examples" / "power-window"), str(self.root), ignore=shutil.ignore_patterns("build"))
        config = self.root / "project.yaml"
        text = config.read_text(encoding="utf-8")
        self.assertIn('  version: "3.1"', text)
        config.write_text(text.replace('  version: "3.1"', '  version: "4.0"', 1), encoding="utf-8")

    def test_the_catalogs_are_valid_and_every_mapping_names_a_practice_of_31(self):
        for version in ("3.1", "4.0"):
            done = subprocess.run([sys.executable, str(self.REPO / "tools" / "catalog.py"), "validate", "--version", version],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertIn("0 errors | 0 warnings", done.stdout)

    def test_a_practice_of_40_shows_the_evidence_of_the_31_practices_it_maps_to(self):
        from traceability import practice_rows
        p31 = Project(self.REPO / "examples" / "power-window")
        p40 = Project(self.root)
        rows31 = {r["practice"]: r for r in practice_rows(p31, "SWE.1")}
        rows40 = {r["practice"]: r for r in practice_rows(p40, "SWE.1")}
        self.assertEqual(len(rows40), 6)
        self.assertEqual(rows40["SWE.1.BP5"]["by"][-1], "as 3.1 SWE.1.BP6, SWE.1.BP7")
        self.assertEqual(rows40["SWE.1.BP6"]["state"], rows31["SWE.1.BP8"]["state"])     # communicate
        self.assertGreaterEqual(rows40["SWE.1.BP1"]["evidence"], rows31["SWE.1.BP1"]["evidence"])

    def test_validation_of_40_is_carried_by_tests_of_stakeholder_requirements(self):
        from traceability import practice_rows
        config = self.root / "project.yaml"
        text = config.read_text(encoding="utf-8")
        config.write_text(text.replace("processes: [SWE.1,", "processes: [VAL.1, SWE.1,", 1), encoding="utf-8")
        rows = {r["practice"]: r for r in practice_rows(Project(self.root), "VAL.1")}
        self.assertEqual(rows["VAL.1.BP1"]["state"], "no evidence yet")           # a place for it, nothing there yet
        self.assertIn("link verifies", rows["VAL.1.BP1"]["by"])

    def test_verification_and_documentation_of_31_have_their_evidence_places(self):
        from traceability import practice_rows
        root = Path(self.tmp.name) / "q"
        shutil.copytree(str(self.REPO / "examples" / "power-window"), str(root), ignore=shutil.ignore_patterns("build"))
        config = root / "project.yaml"
        text = config.read_text(encoding="utf-8")
        config.write_text(text.replace("processes: [SWE.1,", "processes: [SUP.2, SUP.4, SUP.7, SWE.1,", 1), encoding="utf-8")
        project = Project(root)
        rows = {r["practice"]: r for r in practice_rows(project, "SUP.2")}
        self.assertEqual(rows["SUP.2.BP3"]["state"], "evidence present")          # the review records of the example
        self.assertEqual(rows["SUP.2.BP1"]["state"], "findings open")             # no verification plan yet
        self.assertTrue(any(f["rule"] == "COV-27" and "verification" in f["message"] for f in project.check()))
        rows = {r["practice"]: r for r in practice_rows(project, "SUP.7")}
        self.assertEqual(rows["SUP.7.BP2"]["state"], "no evidence structure")     # the toolkit's standards: a person judges
        self.assertNotEqual(rows["SUP.7.BP6"]["state"], "no evidence structure")

    def test_generic_practices_of_40_combine_the_observations_of_31(self):
        from traceability import generic_rows
        rows = {r["practice"]: r for r in generic_rows(Project(self.root), "SWE.1")}
        self.assertEqual(sorted(rows), ["GP 2.1.%d" % n for n in range(1, 7)] + ["GP 2.2.%d" % n for n in range(1, 5)])
        self.assertEqual(rows["GP 2.1.6"]["name"], "Manage the interfaces between involved parties")
        done = subprocess.run([sys.executable, str(self.REPO / "tools" / "traceability.py"), "--project", str(self.root),
                               "generic", "SWE.1"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
