"""Tests for the ReqIF exchange (tools/reqif.py): export, import, and comparing a new version.

Run:  python -m unittest discover -s tools/tests -v
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "power-window"

FOREIGN = """<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <CORE-CONTENT><REQ-IF-CONTENT>
    <DATATYPES>
      <DATATYPE-DEFINITION-ENUMERATION IDENTIFIER="dt-prio" LONG-NAME="Priority">
        <SPECIFIED-VALUES><ENUM-VALUE IDENTIFIER="ev-high" LONG-NAME="high"/></SPECIFIED-VALUES>
      </DATATYPE-DEFINITION-ENUMERATION>
    </DATATYPES>
    <SPEC-TYPES><SPEC-OBJECT-TYPE IDENTIFIER="t1"><SPEC-ATTRIBUTES>
      <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="a-id" LONG-NAME="Object Identifier"/>
      <ATTRIBUTE-DEFINITION-XHTML IDENTIFIER="a-text" LONG-NAME="Object Text"/>
      <ATTRIBUTE-DEFINITION-ENUMERATION IDENTIFIER="a-prio" LONG-NAME="Priority"/>
    </SPEC-ATTRIBUTES></SPEC-OBJECT-TYPE></SPEC-TYPES>
    <SPEC-OBJECTS>
      <SPEC-OBJECT IDENTIFIER="_x1"><VALUES>
        <ATTRIBUTE-VALUE-STRING THE-VALUE="CUS-12"><DEFINITION><ATTRIBUTE-DEFINITION-STRING-REF>a-id</ATTRIBUTE-DEFINITION-STRING-REF></DEFINITION></ATTRIBUTE-VALUE-STRING>
        <ATTRIBUTE-VALUE-XHTML><DEFINITION><ATTRIBUTE-DEFINITION-XHTML-REF>a-text</ATTRIBUTE-DEFINITION-XHTML-REF></DEFINITION>
          <THE-VALUE><xhtml:div><xhtml:p>The window shall close by <xhtml:b>one touch</xhtml:b>.</xhtml:p><xhtml:p>It stops at the closed end.</xhtml:p></xhtml:div></THE-VALUE>
        </ATTRIBUTE-VALUE-XHTML>
        <ATTRIBUTE-VALUE-ENUMERATION><DEFINITION><ATTRIBUTE-DEFINITION-ENUMERATION-REF>a-prio</ATTRIBUTE-DEFINITION-ENUMERATION-REF></DEFINITION>
          <VALUES><ENUM-VALUE-REF>ev-high</ENUM-VALUE-REF></VALUES></ATTRIBUTE-VALUE-ENUMERATION>
      </VALUES></SPEC-OBJECT>
    </SPEC-OBJECTS>
  </REQ-IF-CONTENT></CORE-CONTENT>
</REQ-IF>
"""


class ReqIF(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="reqiftest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "target"
        self.target.mkdir()
        (self.target / "project.yaml").write_text("scope:\n  processes: [SYS.2]\n", encoding="utf-8")

    def reqif(self, project, *arguments):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "reqif.py"), "--project", str(project)]
                              + [str(a) for a in arguments], capture_output=True, text=True)
        return done.returncode, done.stdout

    def export_example(self):
        out = Path(self.tmp.name) / "swr.reqif"
        code, text = self.reqif(EXAMPLE, "export", "--type", "software-requirement", "--out", out)
        self.assertEqual(code, 0, text)
        return out

    def front(self, path):
        return yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])

    def test_exported_requirements_come_back_unchanged(self):
        file = self.export_example()
        code, out = self.reqif(self.target, "import", file, "--type", "stakeholder-requirement", "--source", "Customer",
                               "--version", "1", "--received", "2026-11-19")
        self.assertEqual(code, 0, out)
        item = self.front(self.target / "spec" / "stakeholder" / "STK-0004.md")
        self.assertEqual(item["imported"]["source_id"], "SWR-0004")
        code, out = self.reqif(self.target, "compare", file, "--source", "Customer")
        self.assertIn("0 new, 0 changed, 0 removed, 9 unchanged", out)

    def test_a_new_version_is_compared_not_imported_over_the_old_one(self):
        file = self.export_example()
        self.reqif(self.target, "import", file, "--type", "stakeholder-requirement", "--source", "Customer", "--version", "1")
        code, out = self.reqif(self.target, "import", file, "--type", "stakeholder-requirement", "--source", "Customer",
                               "--version", "2")
        self.assertEqual(code, 1)
        self.assertIn("compare the new version first", out)
        changed = Path(self.tmp.name) / "v2.reqif"
        changed.write_text(file.read_text(encoding="utf-8").replace("480 mm", "470 mm", 1), encoding="utf-8")
        code, out = self.reqif(self.target, "compare", changed, "--source", "Customer")
        self.assertIn("1 changed", out)

    def test_a_file_of_another_tool_with_its_own_attribute_names(self):
        file = Path(self.tmp.name) / "foreign.reqif"
        file.write_text(FOREIGN, encoding="utf-8")
        code, out = self.reqif(self.target, "import", file, "--type", "stakeholder-requirement", "--source", "OEM spec",
                               "--version", "3", "--id-attribute", "Object Identifier", "--text-attribute", "Object Text",
                               "--dry-run")
        self.assertIn("(CUS-12)\nThe window shall close by one touch.", out)       # the user sees what the mapping reads
        self.assertFalse((self.target / "spec" / "stakeholder" / "STK-0001.md").exists())
        code, out = self.reqif(self.target, "import", file, "--type", "stakeholder-requirement", "--source", "OEM spec",
                               "--version", "3", "--id-attribute", "Object Identifier", "--text-attribute", "Object Text")
        self.assertEqual(code, 0, out)
        text = (self.target / "spec" / "stakeholder" / "STK-0001.md").read_text(encoding="utf-8")
        self.assertIn("source_id: CUS-12", text)
        code, out = self.reqif(self.target, "compare", file, "--source", "OEM spec", "--id-attribute", "Object Identifier",
                               "--text-attribute", "Object Text")
        self.assertEqual(code, 0, out)
        self.assertIn("The window shall close by one touch.\n\nIt stops at the closed end.", text)


if __name__ == "__main__":
    unittest.main()
