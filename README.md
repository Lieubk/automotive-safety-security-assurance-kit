# Automotive SPICE toolkit for ECU software

A set of [Claude Code](https://claude.com/claude-code) skills, agents and hooks, plus
deterministic tools, for developing automotive ECU software in line with Automotive
SPICE 3.1. Requirements, architecture, design, test cases and evidence live as text
files in the repository - one item per file - and a trace engine checks them.

The toolkit drafts and checks. People decide, review and are accountable.

## Status

Early. One vertical slice works end to end and is demonstrated by the example:

| Area | State |
|---|---|
| Process catalog | 23 processes of Automotive SPICE 3.1 with base practices, work products and rating dependencies (identifiers and official names; descriptions in our own words) |
| Item schema | 34 item types, 17 link roles, 49 coverage rules, scope-aware |
| Trace engine | structure, links, coverage, stale approvals, suspect links, impact, traceability matrices, evidence per base practice, changes since a review, progress against the plan, integration steps and the builds and runs on them at software and system level, problems, quality assurance, observations per generic practice of level 2 |
| Skills | project scoping and input registration; project management (MAN.3); SYS.2 to SYS.5 and SWE.1 to SWE.6; reviews and quality assurance; baselines, change requests and problem resolution; supplier monitoring; trace check, process gates and a mock assessment |
| Hooks | imported inputs, final records and baselined items are protected; every written item is checked |
| Not yet | risk management (MAN.5), exchange with ALM tools (ReqIF), ISO 26262 and ISO/SAE 21434 extensions, Automotive SPICE 4.0 |

## What it does not do

- It does not rate capability levels and is not an assessment. It shows evidence and
  gaps; assessors rate.
- It does not replace qualified tools. It drives the compiler, test tool and analyser a
  project uses and records what they reported.
- It does not reach hardware. Tests on a target or a test bench are specified, traced
  and recorded here, and executed there.
- It does not approve anything. An item becomes approved through a review with a named
  person's verdict.

## Requirements

- Claude Code
- Python 3.10 or later with PyYAML (`python -m pip install pyyaml`)
- Git
- For the example: a C compiler (gcc, clang, or Visual Studio on Windows); gcc with gcov
  for coverage

## Models

Each agent names the model its work needs, so that judgement gets the strongest model
and routine work a cheaper one:

| Agent or skill | Model | Effort |
|---|---|---|
| `aspice-reviewer`, `software-architect`, `system-engineer` | `opus` | high |
| `software-requirements-engineer`, `software-developer` | `sonnet` | high |
| `unit-verification-engineer`, `software-test-engineer`, `system-test-engineer`, `configuration-manager`, `project-manager` | `sonnet` | medium |
| `/trace-check`, `/next-step` (run in a fork) | `haiku` | low, medium |
| every other skill | the model of your session | your setting |

The names are aliases. On the Anthropic API they resolve to the newest model of the
family; on other providers they may resolve to an earlier version. To run every agent
on one model instead, set `CLAUDE_CODE_SUBAGENT_MODEL` to that model and
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to `1` (Claude Code v2.1.257 or later), or change
`model` in the agent's file under `.claude/agents/`. The reasons for each choice are in
`.claude/docs/skill-authoring.md`, "Model and effort".

## Quick start

Look at the worked example first:

```
python tools/traceability.py --project examples/power-window check
python tools/traceability.py --project examples/power-window practices
python tools/traceability.py --project examples/power-window impact SWR-0003
python examples/power-window/tests/unit/run_tests.py
python examples/power-window/tests/integration/run_tests.py
python examples/power-window/tests/qualification/run_tests.py
```

Then start your own project in a copy of this repository: open it in Claude Code and
run `/aspice-start`. It asks who you are in the supply chain, what you were given, and
which processes you are responsible for, and writes `project.yaml`. From there
`/next-step` says what to do.

## How it is put together

```
aspice/3.1/        process catalog and notes per process
schema/            item types, links, coverage rules; file layout of an item
tools/             trace engine, record writer, validators, tests
.claude/skills/    one skill per activity
.claude/agents/    roles with boundaries; the reviewing agent cannot write
.claude/hooks/     protection and checks on every write
.claude/docs/      working agreement, command reference, review checklists
examples/          power window control with anti-pinch protection
ci/                pipeline templates for projects (GitHub Actions, GitLab CI)
```

Three ideas carry the design:

1. **Facts come from tools.** Coverage, link status and test results are computed or
   taken from tool output, never stated from memory. Evidence records are written by
   tooling.
2. **Approval is bound to content.** A review record names each item with a content
   hash and the upstream versions it was compared against. Change the item and its
   approval is stale; change an upstream item and the links to it are suspect.
3. **Scope decides the rules.** A project declares the processes it is responsible
   for. Only their rules apply, and what comes from outside is an imported input that
   is accepted, not edited.

The rules of work are in [.claude/docs/working-agreement.md](.claude/docs/working-agreement.md).

## Automotive SPICE

Automotive SPICE is a registered trademark of the Verband der Automobilindustrie e.V.
(VDA). This project is not affiliated with or endorsed by the VDA. It does not
reproduce the Automotive SPICE process assessment model: it refers to processes, base
practices and work products by their identifiers and official names and describes what
they expect in its own words. The model itself is available from the VDA QMC and is
the reference for anything normative.

## License

MIT, see [LICENSE](LICENSE).
