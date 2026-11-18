"""Regression tests for the trace engine.

Each test builds a small, fully valid project in a temporary directory, breaks
exactly one thing, and expects the engine to report exactly that.

Run:  python -m unittest discover -s tools/tests -v
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traceability import Project, content_hash, file_hash  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
