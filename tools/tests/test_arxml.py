"""Tests for reading the architecture from an AUTOSAR model (tools/arxml.py).

Run:  python -m unittest discover -s tools/tests -v
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

MODEL = """<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES><AR-PACKAGE><SHORT-NAME>Window</SHORT-NAME><ELEMENTS>
    <SENDER-RECEIVER-INTERFACE><SHORT-NAME>WindowMotion</SHORT-NAME><DATA-ELEMENTS>
      <VARIABLE-DATA-PROTOTYPE><SHORT-NAME>position</SHORT-NAME><TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/Types/uint16</TYPE-TREF></VARIABLE-DATA-PROTOTYPE>
      <VARIABLE-DATA-PROTOTYPE><SHORT-NAME>speed</SHORT-NAME><TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/Types/uint16</TYPE-TREF></VARIABLE-DATA-PROTOTYPE>
    </DATA-ELEMENTS></SENDER-RECEIVER-INTERFACE>
    <CLIENT-SERVER-INTERFACE><SHORT-NAME>MovementCommand</SHORT-NAME><OPERATIONS>
      <CLIENT-SERVER-OPERATION><SHORT-NAME>RequestMovement</SHORT-NAME><ARGUMENTS>
        <ARGUMENT-DATA-PROTOTYPE><SHORT-NAME>direction</SHORT-NAME><TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/Types/uint8</TYPE-TREF><DIRECTION>IN</DIRECTION></ARGUMENT-DATA-PROTOTYPE>
      </ARGUMENTS></CLIENT-SERVER-OPERATION>
    </OPERATIONS></CLIENT-SERVER-INTERFACE>
    <COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE><SHORT-NAME>WindowPos</SHORT-NAME><PORTS>
      <P-PORT-PROTOTYPE><SHORT-NAME>Motion</SHORT-NAME><PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">/Window/WindowMotion</PROVIDED-INTERFACE-TREF></P-PORT-PROTOTYPE>
    </PORTS></COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE>
    <APPLICATION-SW-COMPONENT-TYPE><SHORT-NAME>WindowCmd</SHORT-NAME><PORTS>
      <R-PORT-PROTOTYPE><SHORT-NAME>Motion</SHORT-NAME><REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">/Window/WindowMotion</REQUIRED-INTERFACE-TREF></R-PORT-PROTOTYPE>
      <R-PORT-PROTOTYPE><SHORT-NAME>Cmd</SHORT-NAME><REQUIRED-INTERFACE-TREF DEST="CLIENT-SERVER-INTERFACE">/Window/MovementCommand</REQUIRED-INTERFACE-TREF></R-PORT-PROTOTYPE>
    </PORTS></APPLICATION-SW-COMPONENT-TYPE>
    <SENSOR-ACTUATOR-SW-COMPONENT-TYPE><SHORT-NAME>MotorDrive</SHORT-NAME><PORTS>
      <P-PORT-PROTOTYPE><SHORT-NAME>Cmd</SHORT-NAME><PROVIDED-INTERFACE-TREF DEST="CLIENT-SERVER-INTERFACE">/Window/MovementCommand</PROVIDED-INTERFACE-TREF></P-PORT-PROTOTYPE>
    </PORTS></SENSOR-ACTUATOR-SW-COMPONENT-TYPE>
    <COMPOSITION-SW-COMPONENT-TYPE><SHORT-NAME>PowerWindowApp</SHORT-NAME><COMPONENTS>
      <SW-COMPONENT-PROTOTYPE><SHORT-NAME>pos</SHORT-NAME><TYPE-TREF DEST="COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE">/Window/WindowPos</TYPE-TREF></SW-COMPONENT-PROTOTYPE>
      <SW-COMPONENT-PROTOTYPE><SHORT-NAME>cmd</SHORT-NAME><TYPE-TREF DEST="APPLICATION-SW-COMPONENT-TYPE">/Window/WindowCmd</TYPE-TREF></SW-COMPONENT-PROTOTYPE>
    </COMPONENTS></COMPOSITION-SW-COMPONENT-TYPE>
  </ELEMENTS></AR-PACKAGE></AR-PACKAGES>
</AUTOSAR>
"""


class Arxml(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="arxmltest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        (self.project / "project.yaml").write_text("scope:\n  processes: [SWE.2]\n", encoding="utf-8")
        self.model = self.project / "model" / "window.arxml"
        self.model.parent.mkdir()
        self.model.write_text(MODEL, encoding="utf-8")

    def arxml(self, *arguments):
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "arxml.py"), "--project", str(self.project)]
                              + [str(a) for a in arguments], capture_output=True, text=True)
        return done.returncode, done.stdout

    def item(self, item_id):
        path = next(self.project.rglob(item_id + ".md"))
        return yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])

    def test_import_builds_components_and_interfaces_from_the_ports(self):
        code, out = self.arxml("import", self.model)
        self.assertEqual(code, 0, out)
        self.assertIn("4 components and 2 interfaces", out)
        motion = self.item("IFC-0002")                    # interfaces in name order: MovementCommand, WindowMotion
        self.assertEqual(motion["kind"], "sender-receiver")
        self.assertEqual(motion["provided_by"], "CMP-0004")
        self.assertEqual(motion["used_by"], ["CMP-0003"])             # components: MotorDrive, PowerWindowApp, WindowCmd, WindowPos
        self.assertEqual([e["name"] for e in motion["elements"]], ["position", "speed"])
        command = self.item("IFC-0001")
        self.assertEqual(command["operations"][0]["arguments"][0], {"name": "direction", "direction": "in", "type": "uint8"})
        self.assertEqual(self.item("CMP-0003")["links"]["part_of"], ["CMP-0002"])
        self.assertEqual(self.item("CMP-0002")["kind"], "composition")
        self.assertEqual(self.item("CMP-0004")["model"], "model/window.arxml")

    def test_compare_reports_where_the_items_left_the_model(self):
        self.arxml("import", self.model)
        code, out = self.arxml("compare", self.model)
        self.assertEqual(code, 0, out)
        self.model.write_text(MODEL.replace("<SHORT-NAME>speed</SHORT-NAME>", "<SHORT-NAME>velocity</SHORT-NAME>"),
                              encoding="utf-8")
        code, out = self.arxml("compare", self.model)
        self.assertEqual(code, 1)
        self.assertIn("elements position, velocity in the model, position, speed in the item", out)

    def test_a_second_import_is_refused(self):
        self.arxml("import", self.model)
        code, out = self.arxml("import", self.model)
        self.assertEqual(code, 1)
        self.assertIn("compare instead", out)


if __name__ == "__main__":
    unittest.main()
