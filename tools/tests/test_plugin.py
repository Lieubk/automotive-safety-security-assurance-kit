"""Tests of the packaging as a Claude Code plugin: manifest, marketplace, hooks, and what the hooks do when the
toolkit is installed into another project.

Run:  python -m unittest discover -s tools/tests -v
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESERVED = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Manifest(unittest.TestCase):
    def test_the_manifest_names_paths_that_exist_inside_the_plugin(self):
        plugin = load(".claude-plugin/plugin.json")
        self.assertRegex(plugin["name"], r"^[a-z][a-z0-9-]*$")
        self.assertFalse(plugin["name"].startswith(RESERVED) or plugin["name"] in ("claude", "anthropic", "claude-code"))
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        for key in ("skills", "agents"):
            for path in plugin[key]:
                self.assertTrue(path.startswith("./") and ".." not in path, path)
                self.assertTrue((ROOT / path).exists(), path)
        skills = [p for folder in plugin["skills"] for p in (ROOT / folder).glob("*/SKILL.md")]
        self.assertEqual(len(skills), len(list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))))
        listed = {Path(p).name for p in plugin["agents"]}
        self.assertEqual(listed, {p.name for p in (ROOT / ".claude" / "agents").glob("*.md")})   # every agent, no other
        self.assertTrue(plugin["hooks"].startswith("./") and (ROOT / plugin["hooks"]).is_file())

    def test_the_marketplace_lists_the_plugin_at_its_root(self):
        market, plugin = load(".claude-plugin/marketplace.json"), load(".claude-plugin/plugin.json")
        self.assertTrue(market["name"] and market["owner"]["name"])
        self.assertEqual([(p["name"], p["source"]) for p in market["plugins"]], [(plugin["name"], "./")])

    def test_the_plugin_hooks_are_those_of_the_repository_run_from_the_plugin(self):
        plugin_hooks = load("hooks/hooks.json")["hooks"]
        settings_hooks = load(".claude/settings.json")["hooks"]
        self.assertEqual({e: [g.get("matcher") for g in groups] for e, groups in plugin_hooks.items()},
                         {e: [g.get("matcher") for g in groups] for e, groups in settings_hooks.items()})
        for groups in plugin_hooks.values():
            for hook in (h for g in groups for h in g["hooks"]):
                self.assertNotIn("CLAUDE_PROJECT_DIR", hook["command"])
                self.assertEqual(hook["command"].count("${CLAUDE_PLUGIN_ROOT}/.claude/hooks/aspice_hooks.py"), 2)

    def test_every_skill_and_agent_says_where_the_toolkit_is(self):
        for path in list((ROOT / ".claude" / "skills").glob("*/SKILL.md")) + list((ROOT / ".claude" / "agents").glob("*.md")):
            self.assertIn("Toolkit root: `${CLAUDE_PLUGIN_ROOT}`", path.read_text(encoding="utf-8"), path)


class AsPlugin(unittest.TestCase):
    """The hook script run as Claude Code runs a plugin's hooks: from the plugin, in another project."""

    def run_hook(self, event, payload, project):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project), CLAUDE_PLUGIN_ROOT=str(ROOT))
        done = subprocess.run([sys.executable, str(ROOT / ".claude" / "hooks" / "aspice_hooks.py"), event],
                              input=json.dumps(payload), capture_output=True, text=True, cwd=str(project), env=env)
        return done.returncode, done.stdout

    def test_a_new_session_in_a_project_hears_where_the_toolkit_is(self):
        with tempfile.TemporaryDirectory() as project:
            code, out = self.run_hook("session-start", {}, Path(project))
            self.assertEqual(code, 0)
            self.assertIn("installed as a plugin. Toolkit root: %s" % ROOT.as_posix(), out)
            self.assertIn("# Working agreement", out)
            self.assertIn("no project.yaml yet", out)

    def test_an_agent_may_call_the_toolkit_by_its_full_path(self):
        sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
        import aspice_hooks
        call = 'python "%s/tools/traceability.py" --project . check' % ROOT.as_posix()
        self.assertEqual(aspice_hooks.toolkit_relative(call), "python tools/traceability.py --project . check")
        self.assertEqual(aspice_hooks.toolkit_relative('python "${CLAUDE_PLUGIN_ROOT}/tools/record.py" next-id plan'),
                         "python tools/record.py next-id plan")
        with tempfile.TemporaryDirectory() as other:                # a tools/ folder elsewhere is not the toolkit
            foreign = 'python "%s/tools/traceability.py" check' % Path(other).as_posix()
            self.assertEqual(aspice_hooks.toolkit_relative(foreign), foreign)
        self.assertEqual(aspice_hooks.agent_commands("assurance-kit:aspice-reviewer"),
                         aspice_hooks.agent_commands("aspice-reviewer"))
        with tempfile.TemporaryDirectory() as project:
            payload = {"agent_type": "assurance-kit:aspice-reviewer", "tool_input": {"command": call}}
            code, out = self.run_hook("pre-shell", payload, Path(project))
            self.assertEqual(code, 0)
            self.assertNotIn("deny", out)


if __name__ == "__main__":
    unittest.main()
