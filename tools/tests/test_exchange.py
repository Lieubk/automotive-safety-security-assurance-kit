"""Tests for the spreadsheet and ALM exchange (tools/xlsx.py, tools/alm.py), on copies of the worked example.

The ALM tests run against a simulated server in this process that answers as the public
descriptions of the three interfaces say; they show the client's behaviour, not a real
server's.

Run:  python -m unittest discover -s tools/tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "power-window"
sys.path.insert(0, str(ROOT / "tools"))
import document  # noqa: E402


def workbook(path, sheet, header, rows):
    doc = document.Doc("delivery")
    doc.add("heading", 1, sheet, None)
    doc.add("table", header, rows)
    info = {"project": "p", "generated_at": "2026-01-01T00:00:00", "commit": "-", "uncommitted_changes": False,
            "baseline": "none", "items": [], "draft_reasons": [], "history": []}
    Path(path).write_bytes(document.to_xlsx(doc, info))


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="exchangetest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "p"
        shutil.copytree(str(EXAMPLE), str(self.project), ignore=shutil.ignore_patterns("build"))

    def tool(self, script, *arguments, env=None):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / script), "--project", str(self.project)]
                              + [str(a) for a in arguments], capture_output=True, text=True,
                              env=dict(os.environ, **(env or {})))
        return done.returncode, done.stdout + done.stderr


class Spreadsheets(Case):
    HEADER = ["Req ID", "Name", "Requirement text", "ASIL"]
    ROWS = [["CUS-1", "Close by one touch", "The window shall close by one touch.", "B"],
            ["CUS-2", "Open by one touch", "The window shall open by one touch.", "QM"]]

    def test_requirements_from_a_sheet_are_registered_and_a_new_version_compared(self):
        book = Path(self.tmp.name) / "req.xlsx"
        workbook(book, "Requirements", self.HEADER, self.ROWS)
        columns = ["--column", "source_id=Req ID", "--column", "title=Name", "--column", "text=Requirement text",
                   "--column", "asil=ASIL"]
        code, out = self.tool("xlsx.py", "import", book, "--sheet", "Requirements", "--header-row", "2",
                              "--type", "stakeholder-requirement", "--source", "Customer sheet", "--version", "1", *columns)
        self.assertEqual(code, 0, out)
        text = (self.project / "spec" / "stakeholder" / "STK-0001.md").read_text(encoding="utf-8")
        self.assertIn("source_id: CUS-1", text)
        self.assertIn("asil: B", text)
        rows = [list(self.ROWS[0]), ["CUS-3", "Stop", "The window shall stop on request.", "QM"]]
        rows[0][2] = "The window shall close by one touch within 4 s."
        workbook(book, "Requirements", self.HEADER, rows)
        code, out = self.tool("xlsx.py", "compare", book, "--sheet", "Requirements", "--header-row", "2",
                              "--source", "Customer sheet", *columns)
        self.assertIn("1 new, 1 changed, 1 removed, 0 unchanged", out)

    def test_yes_and_no_cells_become_true_and_false_and_dates_ahead_are_refused(self):
        book = Path(self.tmp.name) / "req.xlsx"
        workbook(book, "Requirements", ["Req ID", "Requirement text", "Security"],
                 [["CUS-1", "The window shall close by one touch.", "Yes"], ["CUS-2", "The window shall open.", "no"]])
        columns = ["--column", "source_id=Req ID", "--column", "text=Requirement text",
                   "--column", "security_relevant=Security"]
        base = ["import", book, "--sheet", "Requirements", "--header-row", "2", "--type", "stakeholder-requirement",
                "--source", "Customer sheet", "--version", "1"] + columns
        code, out = self.tool("xlsx.py", *base, "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertIn("security_relevant: true", out)
        code, out = self.tool("xlsx.py", *base, "--received", "2999-01-01")
        self.assertNotEqual(code, 0)
        self.assertIn("lies in the future", out)
        code, out = self.tool("xlsx.py", *base)
        self.assertEqual(code, 0, out)
        texts = [(self.project / "spec" / "stakeholder" / ("STK-000%d.md" % n)).read_text(encoding="utf-8") for n in (1, 2)]
        self.assertIn("security_relevant: true", texts[0])
        self.assertIn("security_relevant: false", texts[1])
        workbook(book, "Requirements", ["Req ID", "Requirement text", "Security"],
                 [["CUS-9", "The window shall stop.", "maybe"]])
        code, out = self.tool("xlsx.py", *base[:-len(columns) - 4], "--source", "Other sheet", "--version", "1", *columns)
        self.assertNotEqual(code, 0)
        self.assertIn("'maybe' is not one of true, false", out)

    def test_a_sheet_of_test_results_becomes_the_results_of_a_run(self):
        book = Path(self.tmp.name) / "results.xlsx"
        workbook(book, "Test case", ["No", "Test Case ID", "Test Result", "Remark"],
                 [["1", "SQT-0001", "Passed", ""], ["2", "SQT-0002", "Failed", "late by 20 ms"],
                  ["3", "SQT-0003", "Not Test", "bench busy"], ["4", "XYZ-9", "Passed", ""]])
        out_file = Path(self.tmp.name) / "results.json"
        code, out = self.tool("xlsx.py", "results", book, "--sheet", "Test case", "--header-row", "2",
                              "--column", "test=Test Case ID", "--column", "verdict=Test Result",
                              "--column", "reason=Remark", "--out", out_file)
        self.assertEqual(code, 0, out)
        self.assertIn("left out: XYZ-9", out)
        results = {r["test"]: r for r in json.loads(out_file.read_text(encoding="utf-8"))["results"]}
        self.assertEqual(results["SQT-0001"]["verdict"], "passed")
        self.assertEqual((results["SQT-0002"]["verdict"], results["SQT-0002"]["reason"]), ("failed", "late by 20 ms"))
        self.assertEqual((results["SQT-0003"]["verdict"], results["SQT-0003"]["reason"]), ("not-run", "bench busy"))

    def test_items_are_exported_to_a_sheet(self):
        out_file = Path(self.tmp.name) / "out.xlsx"
        code, out = self.tool("xlsx.py", "export", "--type", "software-requirement", "--out", out_file)
        self.assertEqual(code, 0, out)
        sheets = __import__("xlsx").read_workbook(out_file)
        self.assertIn("SWR-0001", [row[0] for row in sheets["Items"] if row])


class Server(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *args):
        pass

    def answer(self, body, code=200):
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def handle_any(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length else None
        Server.calls.append((self.command, url.path, body, self.headers.get("Authorization")))
        if self.headers.get("Authorization") != "Bearer secret":
            return self.answer({"error": "unauthorized"}, 401)
        q = parse_qs(url.query)
        if url.path == "/polarion/rest/v1/projects/WIN/workitems" and self.command == "GET":
            page = q["page[number]"][0]
            if page == "1":
                return self.answer({"data": [{"type": "workitems", "id": "WIN/WIN-11", "attributes": {
                    "title": "Close by one touch", "description": {"type": "text/html", "value": "<p>The window shall close.</p>"},
                    "severity": "B"}}], "links": {"next": "page 2"}})
            return self.answer({"data": [{"type": "workitems", "id": "WIN/WIN-12", "attributes": {
                "title": "Open by one touch", "description": {"type": "text/html", "value": "<p>The window shall open.</p>"}}}],
                "links": {}})
        if url.path == "/polarion/rest/v1/projects/WIN/workitems" and self.command == "POST":
            return self.answer({"data": [{"type": "workitems", "id": "WIN/WIN-%d" % (100 + len(Server.calls))}]}, 201)
        if url.path.startswith("/polarion/rest/v1/projects/WIN/workitems/") and self.command == "PATCH":
            return self.answer({})
        if url.path == "/api/v3/trackers/7/items" and self.command == "GET":
            return self.answer({"page": 1, "pageSize": 100, "total": 1, "itemRefs": [{"id": 501, "name": "Stop"}]})
        if url.path == "/api/v3/items/501":
            return self.answer({"id": 501, "name": "Stop", "description": "The window shall stop on request."})
        if url.path == "/rest/v1/abstractitems":
            return self.answer({"meta": {"status": "OK", "pageInfo": {"startIndex": 0, "resultCount": 1, "totalResults": 1}},
                                "data": [{"id": 9001, "documentKey": "PW-REQ-1", "itemType": 89,
                                          "fields": {"name": "Reverse", "description": "<p>The window shall reverse.</p>"}}]})
        return self.answer({"error": "not simulated: %s %s" % (self.command, url.path)}, 404)

    do_GET = do_POST = do_PUT = do_PATCH = handle_any


class AlmTools(Case):
    def setUp(self):
        super().setUp()
        Server.calls = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Server)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        self.env = {"ALM_TOKEN": "secret"}

    def test_polarion_work_items_are_pulled_page_by_page(self):
        code, out = self.tool("alm.py", "pull", "polarion", "--url", self.url, "--alm-project", "WIN",
                              "--type", "stakeholder-requirement", "--source", "Customer Polarion", "--version", "2026-05",
                              "--map", "asil=severity", env=self.env)
        self.assertEqual(code, 0, out)
        self.assertIn("wrote 2 stakeholder-requirement items", out)
        text = (self.project / "spec" / "stakeholder" / "STK-0001.md").read_text(encoding="utf-8")
        self.assertIn("source_id: WIN-11", text)
        self.assertIn("asil: B", text)
        self.assertIn("The window shall close.", text)
        self.assertTrue(all(c[3] == "Bearer secret" for c in Server.calls))

    def test_codebeamer_and_jama_items_are_pulled(self):
        code, out = self.tool("alm.py", "pull", "codebeamer", "--url", self.url, "--tracker", "7",
                              "--type", "stakeholder-requirement", "--source", "CB", "--version", "1", "--dry-run", env=self.env)
        self.assertEqual(code, 0, out)
        self.assertIn("would write 1", out)
        code, out = self.tool("alm.py", "pull", "jama", "--url", self.url, "--alm-project", "3", "--item-type", "89",
                              "--type", "stakeholder-requirement", "--source", "Jama", "--version", "1", "--dry-run", env=self.env)
        self.assertEqual(code, 0, out)
        self.assertIn("would write 1", out)

    def test_push_creates_once_and_updates_after(self):
        args = ["push", "polarion", "--url", self.url, "--alm-project", "WIN", "--type", "software-requirement"]
        code, out = self.tool("alm.py", *args, env=self.env)
        self.assertEqual(code, 0, out)
        self.assertIn("9 created, 0 updated", out)
        code, out = self.tool("alm.py", *args, env=self.env)
        self.assertEqual(code, 0, out)
        self.assertIn("0 created, 9 updated", out)
        self.assertTrue((self.project / ".alm" / "map.json").exists())

    def test_without_credentials_nothing_is_sent(self):
        code, out = self.tool("alm.py", "pull", "polarion", "--url", self.url, "--alm-project", "WIN",
                              "--type", "stakeholder-requirement", "--source", "x", "--version", "1",
                              env={"ALM_TOKEN": "", "ALM_USER": "", "ALM_PASSWORD": ""})
        self.assertEqual(code, 1)
        self.assertIn("no credentials", out)
        self.assertEqual(Server.calls, [])


if __name__ == "__main__":
    unittest.main()
