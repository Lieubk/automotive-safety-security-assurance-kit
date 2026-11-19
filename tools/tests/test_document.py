"""Tests for the document generator (tools/document.py), on a copy of the worked example.

Run:  python -m unittest discover -s tools/tests -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "power-window"

try:
    import docx
except ImportError:                                   # DOCX is optional; the HTML tests still run
    docx = None
try:
    import openpyxl
except ImportError:                                   # needed only for the customer's Excel templates
    openpyxl = None


class Documents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="doctest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "p"
        shutil.copytree(str(EXAMPLE), str(self.project), ignore=shutil.ignore_patterns("build"))

    def tool(self, script, *arguments):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / script), "--project", str(self.project)]
                              + [str(a) for a in arguments], capture_output=True, text=True)
        return done.returncode, done.stdout

    def html(self, kind, *extra):
        out = Path(self.tmp.name) / ("%s.html" % kind)
        code, text = self.tool("document.py", "build", kind, "--out", out, *extra)
        self.assertEqual(code, 0, text)
        return out.read_text(encoding="utf-8")

    def test_every_kind_is_generated_from_the_items(self):
        code, out = self.tool("document.py", "list")
        self.assertEqual(code, 0, out)
        for kind in ("software-requirements-specification", "software-architecture-description",
                     "software-detailed-design", "tara-report"):
            self.assertIn(kind, out)
        page = self.html("software-architecture-description")
        self.assertIn('id="CMP-0004"', page)
        self.assertIn('<pre class="mermaid">', page)
        self.assertIn("Items in this document", page)
        self.assertNotIn('class="banner"', page)                  # everything shown is approved

    def test_every_kind_of_the_definitions_builds_on_the_example(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from document import definitions
        for kind in definitions():
            out = Path(self.tmp.name) / ("%s.html" % kind)
            code, text = self.tool("document.py", "build", kind, "--out", out, "--as-of", "2026-06-05")
            self.assertEqual(code, 0, "%s: %s" % (kind, text))

    def test_test_reports_show_every_case_with_its_verdict(self):
        page = self.html("software-integration-test-report")
        self.assertIn("result summary", page)
        self.assertIn("<td>SIT-0001</td>", page.replace('<a href="#SIT-0001">SIT-0001</a>', "SIT-0001"))
        self.assertIn("<td>passed</td>", page)

    def test_xlsx_has_a_sheet_per_chapter_and_a_row_per_attack_path(self):
        import re
        import zipfile
        out = Path(self.tmp.name) / "tara.xlsx"
        code, text = self.tool("document.py", "build", "tara-worksheet", "--out", out)
        self.assertEqual(code, 0, text)
        with zipfile.ZipFile(out) as z:
            names = re.findall(r'<sheet name="([^"]+)"', z.read("xl/workbook.xml").decode("utf-8"))
            self.assertEqual(names, ["Document", "Method", "TARA worksheet", "Items"])
            sheet = z.read("xl/worksheets/sheet3.xml").decode("utf-8")
        self.assertEqual(sheet.count("THR-0001"), 2)                      # two attack paths, two rows
        self.assertIn("CSG-0001", sheet)

    def test_the_word_template_of_the_project_does_not_stop_other_formats(self):
        if docx is None:
            self.skipTest("python-docx is not installed")
        template = docx.Document()
        template.add_paragraph("{{content}}")
        template.save(str(self.project / "customer.docx"))
        config = self.project / "project.yaml"
        config.write_text(config.read_text(encoding="utf-8") + "documents:\n  template: customer.docx\n", encoding="utf-8")
        self.html("software-requirements-specification")                     # html ignores the Word template
        out = Path(self.tmp.name) / "x.xlsx"
        code, text = self.tool("document.py", "build", "software-requirements-specification", "--out", out)
        self.assertEqual(code, 0, text)

    def test_items_left_out_are_named(self):
        path = self.project / "spec" / "cybersecurity" / "tara" / "THR-0002.md"
        path.write_text(path.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1), encoding="utf-8")
        code, text = self.tool("document.py", "build", "tara-report", "--out", Path(self.tmp.name) / "t.html")
        self.assertEqual(code, 0, text)
        self.assertIn("left out: 1 items that are not approved (THR-0002)", text)
        page = (Path(self.tmp.name) / "t.html").read_text(encoding="utf-8")
        self.assertIn("left out because not yet approved: THR-0002", page)    # said in the document, not only here

    def test_the_tara_report_shows_the_method_and_the_risks(self):
        page = self.html("tara-report")
        self.assertIn("risk matrix", page)
        self.assertIn('id="THR-0001"', page)
        self.assertIn("CSG-0001", page)

    def test_items_not_approved_stay_out_unless_asked_and_then_mark_the_document(self):
        path = self.project / "spec" / "cybersecurity" / "tara" / "THR-0002.md"
        path.write_text(path.read_text(encoding="utf-8").replace("status: approved", "status: draft", 1), encoding="utf-8")
        self.assertNotIn('id="THR-0002"', self.html("tara-report"))
        page = self.html("tara-report", "--include-drafts")
        self.assertIn('id="THR-0002"', page)
        self.assertIn('class="banner">DRAFT', page)

    def test_a_document_of_a_baseline_is_refused_when_its_items_changed(self):
        code, out = self.tool("record.py", "baseline", "--tag", "design-1", "--purpose", "design freeze")
        self.assertEqual(code, 0, out)
        page = self.html("software-requirements-specification", "--baseline", "BL-0001")
        self.assertIn("BL-0001 (tag design-1)", page)
        path = self.project / "spec" / "software" / "requirements" / "SWR-0001.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nOne more sentence.\n", encoding="utf-8")
        code, out = self.tool("document.py", "build", "software-requirements-specification", "--baseline", "BL-0001",
                              "--out", Path(self.tmp.name) / "x.html")
        self.assertEqual(code, 1)
        self.assertIn("differ from baseline BL-0001", out)

    def test_pdf_is_printed_from_the_html_or_reported_as_not_assessed(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import document
        out = Path(self.tmp.name) / "srs.pdf"
        code, text = self.tool("document.py", "build", "software-requirements-specification", "--format", "pdf", "--out", out)
        if document.find_browsers():
            self.assertEqual(code, 0, text)
            self.assertEqual(out.read_bytes()[:4], b"%PDF")
        else:
            self.assertEqual(code, 1)
            self.assertIn("NOT ASSESSED", text)
        found = document.find_browsers
        document.find_browsers = lambda: []
        try:
            data, reason = document.html_to_pdf("<p>x</p>")
        finally:
            document.find_browsers = found
        self.assertIsNone(data)
        self.assertIn("no Chromium-family browser", reason)

    def test_a_word_template_does_not_apply_to_a_pdf_printed_from_html(self):
        code, text = self.tool("document.py", "build", "software-requirements-specification", "--format", "pdf",
                               "--pdf-from", "html", "--template", Path(self.tmp.name) / "t.dotx")
        self.assertEqual(code, 2)
        self.assertIn("applies to --format docx", text)

    @unittest.skipIf(docx is None, "python-docx is not installed")
    def test_docx_in_neutral_style_and_in_the_customer_template(self):
        out = Path(self.tmp.name) / "sdd.docx"
        code, text = self.tool("document.py", "build", "software-detailed-design", "--out", out)
        self.assertEqual(code, 0, text)
        headings = [p.text for p in docx.Document(str(out)).paragraphs if p.style.name.startswith("Heading")]
        self.assertIn("Component designs", headings)
        template = docx.Document()
        template.add_paragraph("Customer cover: {{title}} for {{project}}")
        template.add_paragraph("{{content}}")
        template.add_paragraph("Customer closing page")
        template_path = Path(self.tmp.name) / "customer.docx"
        template.save(str(template_path))
        out = Path(self.tmp.name) / "sdd-customer.docx"
        code, text = self.tool("document.py", "build", "software-detailed-design", "--format", "docx",
                               "--template", template_path, "--out", out)
        self.assertEqual(code, 0, text)
        paragraphs = [p.text for p in docx.Document(str(out)).paragraphs]
        self.assertEqual(paragraphs[0], "Customer cover: Software detailed design for Power window control")
        self.assertEqual(paragraphs[-1], "Customer closing page")                  # content went where {{content}} was
        self.assertNotIn("{{content}}", paragraphs)

    @unittest.skipIf(openpyxl is None, "openpyxl is not installed")
    def test_the_customer_excel_template_is_filled_and_keeps_its_form(self):
        from openpyxl.formatting.rule import CellIsRule
        from openpyxl.styles import PatternFill
        from openpyxl.worksheet.datavalidation import DataValidation
        folder = Path(self.tmp.name) / "templates"
        folder.mkdir()
        book = openpyxl.Workbook()
        cover = book.active
        cover.title = "Cover"
        cover.merge_cells("B2:E2")
        cover["B2"] = "Integration test report"
        spec = book.create_sheet("Specification")
        spec.append(["Customer form"])
        spec.append([])
        spec.append(["Test ID", "Description", "Expected result", "Result", "Remark", "No"])
        spec.append(["EXAMPLE-1", "sample row of an earlier report", "", "Pass", "old remark", "=ROW()-3"])
        green = PatternFill("solid", start_color="FFC6EFCE")
        for cell in spec[4]:
            cell.fill = green
        verdicts = DataValidation(type="list", formula1='"Pass,Fail"')
        spec.add_data_validation(verdicts)
        verdicts.add("D4:D200")
        spec.conditional_formatting.add("D4:D200", CellIsRule(operator="equal", formula=['"Fail"'], fill=green))
        reqs = book.create_sheet("Requirements")
        reqs.append(["ID", "Requirement", "Derived from", "Status", "No"])
        book.save(str(folder / "customer.xlsx"))
        (folder / "report.yaml").write_text(
            "template: customer.xlsx\n"
            "cells:\n  - {sheet: Cover, cell: B4, value: 'Project {{project}}, commit {{commit}}'}\n"
            "tables:\n"
            "  - {sheet: Specification, header_row: 3, from: table,\n"
            "     columns: {Test ID: test case, Description: title, Expected result: expected result, Result: verdict},\n"
            "     values: {Result: {passed: Pass, failed: Fail}}}\n",
            encoding="utf-8")
        out = Path(self.tmp.name) / "report.xlsx"
        code, text = self.tool("document.py", "build", "software-integration-test-report", "--format", "xlsx",
                               "--template", folder / "report.yaml", "--out", out)
        self.assertEqual(code, 0, text)
        filled = openpyxl.load_workbook(str(out))
        sheet = filled["Specification"]
        self.assertRegex(str(sheet["A4"].value), r"^[A-Z]+-\d{4}$")         # the first test case, not the sample
        self.assertIn(sheet["D4"].value, ("Pass", "Fail"))                   # in the words of the drop-down list
        self.assertIsNone(sheet["E4"].value)                    # the earlier report's rows are cleared in every column
        self.assertEqual(sheet["F4"].value, "=ROW()-3")                       # formulas stay
        self.assertEqual(sheet["A5"].fill.start_color.rgb, "FFC6EFCE")       # later rows take the form's style
        self.assertEqual(len(sheet.data_validations.dataValidation), 1)
        self.assertEqual(len(sheet.conditional_formatting), 1)
        self.assertIn("B2:E2", [str(r) for r in filled["Cover"].merged_cells.ranges])
        self.assertTrue(str(filled["Cover"]["B4"].value).startswith("Project Power window control, commit "))
        self.assertIn("Document information", filled.sheetnames)

        (folder / "srs.yaml").write_text(
            "template: customer.xlsx\n"
            "tables:\n  - {sheet: Requirements, header_row: 1, from: items, types: [software-requirement],\n"
            "     columns: {No: '#', ID: id, Requirement: 'section:Statement', Derived from: 'link:derived_from',\n"
            "               Status: status}}\n",
            encoding="utf-8")
        code, text = self.tool("document.py", "build", "software-requirements-specification", "--format", "xlsx",
                               "--template", folder / "srs.yaml", "--out", out)
        self.assertEqual(code, 0, text)
        rows = list(openpyxl.load_workbook(str(out))["Requirements"].values)
        self.assertEqual(rows[1][0], "SWR-0001")
        self.assertTrue(rows[1][1] and rows[1][2] and rows[1][3] == "approved")
        self.assertEqual([r[4] for r in rows[1:4]], [1, 2, 3])               # the header No stays a word

        (folder / "bad.yaml").write_text(
            "template: customer.xlsx\ntables:\n  - {sheet: Specification, header_row: 3, from: table,\n"
            "     columns: {Test ID: test case, Priority: priority}}\n", encoding="utf-8")
        code, text = self.tool("document.py", "build", "software-integration-test-report", "--format", "xlsx",
                               "--template", folder / "bad.yaml", "--out", out)
        self.assertEqual(code, 1)
        self.assertIn("has no header 'Priority'", text)


if __name__ == "__main__":
    unittest.main()
