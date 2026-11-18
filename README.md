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
| Item schema | 24 item types, 12 link roles, 28 coverage rules, scope-aware |
| Trace engine | structure, links, coverage, stale approvals, suspect links, impact, traceability matrices, evidence per base practice |
| Skills | project scoping and input registration; SWE.1 to SWE.4; reviews; baselines and change requests; trace check and process gates |
| Hooks | imported inputs, final records and baselined items are protected; every written item is checked |
| Not yet | system level skills (SYS), software integration and qualification test (SWE.5, SWE.6), project management, quality assurance as a process, exchange with ALM tools (ReqIF), ISO 26262 and ISO/SAE 21434 extensions, Automotive SPICE 4.0 |

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

## Quick start

Look at the worked example first:

```
python tools/traceability.py --project examples/power-window check
python tools/traceability.py --project examples/power-window practices
python tools/traceability.py --project examples/power-window impact SWR-0003
python examples/power-window/tests/unit/run_tests.py
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
