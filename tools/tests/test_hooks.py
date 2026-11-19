"""Tests for the Claude Code hooks (.claude/hooks/aspice_hooks.py).

Each test feeds the hook the JSON payload Claude Code would send and checks what
comes back. They run against a copy of the worked example, so nothing in the
repository is touched.

Run:  python -m unittest discover -s tools/tests -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "aspice_hooks.py"
EXAMPLE = ROOT / "examples" / "power-window"


def run_hook(event, payload):
    done = subprocess.run([sys.executable, str(HOOK), event], input=json.dumps(payload),
                          capture_output=True, text=True)
    return done.returncode, done.stdout.strip(), done.stderr.strip()


class HookCase(unittest.TestCase):
    def setUp(self):
        # a copy outside the repository: the hook finds the project through the project.yaml above the file
        self.tmp = tempfile.TemporaryDirectory(prefix="hooktest-", ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "p"
        shutil.copytree(str(EXAMPLE), str(self.project), ignore=shutil.ignore_patterns("build"))

    def path(self, relative):
        return self.project / relative

    def edit(self, relative, old, new):
        return {"tool_name": "Edit", "tool_input": {"file_path": str(self.path(relative)), "old_string": old, "new_string": new}}

    def decision(self, payload):
        code, out, err = run_hook("pre-write", payload)
        self.assertEqual(code, 0, err)
        if not out:
            return None, ""
        answer = json.loads(out)["hookSpecificOutput"]
        return answer["permissionDecision"], answer["permissionDecisionReason"]


class PreWrite(HookCase):
    def test_accepted_imported_input_is_read_only(self):
        verdict, reason = self.decision(self.edit("spec/system/requirements/SYR-0001.md", "title:", "title: changed"))
        self.assertEqual(verdict, "deny")
        self.assertIn("imported input", reason)

    def test_imported_input_may_be_corrected_until_it_is_accepted(self):
        for record in self.path("records/reviews").glob("*.md"):
            record.unlink()                                   # no acceptance review yet
        verdict, _ = self.decision(self.edit("spec/system/requirements/SYR-0001.md", "title:", "title: changed"))
        self.assertIsNone(verdict)

    def test_new_version_of_an_imported_input_may_replace_the_old_content(self):
        target = self.path("spec/system/requirements/SYR-0001.md")
        text = target.read_text(encoding="utf-8")
        import re
        version = re.search(r"version: *(\S+)", text).group(0)
        payload = {"tool_name": "Write", "tool_input": {
            "file_path": str(target), "content": text.replace(version, "version: next-delivery") + "\nNew sentence.\n"}}
        self.assertEqual(self.decision(payload)[0], None)

    def test_new_version_of_a_baselined_input_needs_a_change_request(self):
        self.baseline("SYR-0001")
        target = self.path("spec/system/requirements/SYR-0001.md")
        text = target.read_text(encoding="utf-8")
        import re
        version = re.search(r"version: *(\S+)", text).group(0)
        payload = {"tool_name": "Write", "tool_input": {
            "file_path": str(target), "content": text.replace(version, "version: next-delivery") + "\nNew sentence.\n"}}
        verdict, reason = self.decision(payload)
        self.assertEqual(verdict, "deny")
        self.assertIn("change request", reason)

    def test_links_of_an_accepted_imported_element_may_be_updated(self):
        verdict, _ = self.decision(self.edit("spec/system/architecture/SYE-0001.md", "SYR-0004]", "SYR-0004, SYR-0005]"))
        self.assertIsNone(verdict)

    def test_accepted_imported_input_may_be_marked_obsolete(self):
        verdict, _ = self.decision(self.edit("spec/system/requirements/SYR-0001.md", "status: approved",
                                             "status: obsolete\nsuperseded_by: withdrawn by the customer"))
        self.assertIsNone(verdict)

    def test_final_record_is_never_edited(self):
        verdict, reason = self.decision(self.edit("verification/runs/RUN-0001.md", "verdict: passed", "verdict: failed"))
        self.assertEqual(verdict, "deny")
        self.assertIn("final record", reason)

    def test_ordinary_item_may_be_edited(self):
        verdict, _ = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "title:", "title: changed"))
        self.assertIsNone(verdict)

    def test_new_file_is_not_held_up(self):
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(self.path("spec/software/requirements/SWR-0099.md")),
                                                        "content": "---\nid: SWR-0099\n---\n"}}
        self.assertEqual(self.decision(payload), (None, ""))

    def test_file_outside_any_project_is_not_held_up(self):
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(ROOT / "README.md"), "content": "x"}}
        self.assertEqual(self.decision(payload), (None, ""))

    def baseline(self, item_id, purpose="design freeze"):
        sys.path.insert(0, str(ROOT / "tools"))
        from traceability import Project
        item = Project(self.project).items[item_id]
        record = "---\nid: BL-0001\ntype: baseline\nstatus: final\ntag: design-1\npurpose: %s\n" \
                 "items:\n- {item: %s, hash: %s, status: approved}\n---\n" % (purpose, item.id, item.hash)
        folder = self.path("records/baselines")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "BL-0001.md").write_text(record, encoding="utf-8")

    def test_baselined_item_needs_a_change_request(self):
        self.baseline("SWR-0001")
        verdict, reason = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "title:", "title: changed"))
        self.assertEqual(verdict, "deny")
        self.assertIn("change request", reason)

    def test_internal_baseline_freezes_nothing(self):
        self.baseline("SWR-0001", purpose="working")
        verdict, _ = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "title:", "title: changed"))
        self.assertIsNone(verdict)

    def test_baselined_item_with_an_approved_change_request(self):
        self.baseline("SWR-0001")
        folder = self.path("records/changes")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "CR-0001.md").write_text(
            "---\nid: CR-0001\ntype: change-request\ntitle: Adjust\nstatus: approved\nrequester: Customer\n"
            "decision: board, today\nlinks:\n  affects: [SWR-0001]\n---\n\n## Description\n\nx\n\n## Impact analysis\n\ny\n",
            encoding="utf-8")
        verdict, _ = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "title:", "title: changed"))
        self.assertIsNone(verdict)

    def test_status_change_alone_is_not_a_content_change(self):
        self.baseline("SWR-0001")
        verdict, _ = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "status: approved", "status: in-review"))
        self.assertIsNone(verdict)

    def test_retiring_a_baselined_item_needs_a_change_request(self):
        self.baseline("SWR-0001")
        verdict, reason = self.decision(self.edit("spec/software/requirements/SWR-0001.md", "status: approved",
                                                  "status: obsolete"))
        self.assertEqual(verdict, "deny")
        self.assertIn("retiring", reason)

    def test_registering_code_on_a_baselined_unit_needs_no_change_request(self):
        self.baseline("UNT-0003")
        verdict, _ = self.decision(self.edit("spec/software/design/UNT-0003.md", "  - src/antipinch/AntiPinch.c",
                                             "  - src/antipinch/AntiPinch.c\n  - src/antipinch/AntiPinch_Cfg.h"))
        self.assertIsNone(verdict)


class PostWrite(HookCase):
    def feedback(self, relative):
        code, out, err = run_hook("post-write", {"tool_name": "Write", "tool_input": {"file_path": str(self.path(relative))}})
        self.assertEqual(code, 0, err)
        return json.loads(out)["reason"] if out else ""

    def test_valid_item_gives_no_feedback(self):
        self.assertEqual(self.feedback("spec/software/requirements/SWR-0001.md"), "")

    def test_schema_violation_is_handed_back(self):
        target = self.path("spec/software/requirements/SWR-0001.md")
        target.write_text(target.read_text(encoding="utf-8").replace("asil: ", "asil: X", 1), encoding="utf-8")
        self.assertIn("SCHEMA SWR-0001", self.feedback("spec/software/requirements/SWR-0001.md"))

    def test_content_change_of_an_approved_item_is_called_out(self):
        target = self.path("spec/software/requirements/SWR-0001.md")
        target.write_text(target.read_text(encoding="utf-8") + "\nAdded sentence.\n", encoding="utf-8")
        text = self.feedback("spec/software/requirements/SWR-0001.md")
        self.assertIn("no final review record covers its current content", text)
        self.assertIn("/review", text)

    def test_file_without_front_matter_in_an_item_folder(self):
        self.path("spec/software/requirements/SWR-0098.md").write_text("just text\n", encoding="utf-8")
        self.assertIn("FORMAT", self.feedback("spec/software/requirements/SWR-0098.md"))

    def test_files_that_are_not_items_are_ignored(self):
        self.assertEqual(self.feedback("README.md"), "")


class AgentCommands(unittest.TestCase):
    def shell(self, agent, command):
        payload = {"tool_name": "Bash", "tool_input": {"command": command}}
        if agent:
            payload["agent_type"] = agent
        code, out, err = run_hook("pre-shell", payload)
        self.assertEqual(code, 0, err)
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else None

    def test_an_agent_runs_the_commands_its_file_allows(self):
        self.assertIsNone(self.shell("aspice-reviewer", "python tools/traceability.py --project p show SWR-0001"))

    def test_an_agent_may_name_the_project_after_the_script(self):
        self.assertIsNone(self.shell("software-architect", 'python tools/record.py --project "C:/a b/p" next-id plan'))
        self.assertEqual(self.shell("software-architect", "python tools/record.py --project p review --verdict approved X"),
                         "deny")

    def test_an_agent_cannot_run_anything_else(self):
        self.assertEqual(self.shell("aspice-reviewer", "python -c \"open('x.py', 'w').write('')\""), "deny")
        self.assertEqual(self.shell("aspice-reviewer", "python tools/traceability.py check && python x.py"), "deny")
        self.assertEqual(self.shell("aspice-reviewer", "python tools/traceability.py check > out.txt"), "deny")

    def test_the_main_conversation_and_unknown_agents_are_not_restricted(self):
        self.assertIsNone(self.shell(None, "python x.py"))
        self.assertIsNone(self.shell("general-purpose", "python x.py"))


class OtherEvents(unittest.TestCase):
    def test_session_start_reports_the_state(self):
        code, out, _ = run_hook("session-start", {})
        self.assertEqual(code, 0)
        self.assertIn("Automotive SPICE toolkit", out)

    def test_pre_shell_ignores_commands_that_do_not_commit(self):
        code, out, _ = run_hook("pre-shell", {"tool_name": "Bash", "tool_input": {"command": "git status"}})
        self.assertEqual((code, out), (0, ""))

    def test_only_real_commits_into_the_toolkit_are_scanned(self):
        sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
        import aspice_hooks
        here = str(ROOT)
        self.assertEqual(aspice_hooks.commit_targets("echo 'git commit' && git log --grep commit", here), [])
        self.assertEqual(aspice_hooks.commit_targets("git -c user.name=a commit -m b", here), [ROOT])
        with tempfile.TemporaryDirectory() as other:
            targets = aspice_hooks.commit_targets('cd "%s" && git add . && git commit -m x' % other, here)
            self.assertEqual([t.resolve() for t in targets], [Path(other).resolve()])
            self.assertFalse(aspice_hooks.commits_into_toolkit(targets[0]))
            self.assertFalse(any(aspice_hooks.commits_into_toolkit(t)
                                 for t in aspice_hooks.commit_targets("git -C %s commit -m x" % other, here)))
        self.assertTrue(aspice_hooks.commits_into_toolkit(ROOT / "examples"))
        self.assertTrue(aspice_hooks.commits_into_toolkit(Path("$REPO")))

    def test_unknown_event_is_an_error(self):
        code, _, err = run_hook("nonsense", {})
        self.assertEqual(code, 1)
        self.assertIn("usage", err)


if __name__ == "__main__":
    unittest.main()
