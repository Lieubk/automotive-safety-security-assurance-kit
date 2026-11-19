# Automotive Safety & Security Assurance Kit

**Process, safety and security assurance for automotive ECU software.**

A set of [Claude Code](https://claude.com/claude-code) skills, agents and hooks, plus
deterministic tools, for developing automotive ECU software in line with Automotive
SPICE 3.1 (and 4.0, from its draft), ISO 26262 and ISO/SAE 21434. Requirements, architecture, design, test cases and evidence live as text
files in the repository - one item per file - and a trace engine checks them.

The toolkit drafts and checks. People decide, review and are accountable.

## At a glance

| Scale | What it covers |
|---|---|
| **38** skills | one per process or task, from project scope to release: system and software engineering (SYS.2 to SYS.5, SWE.1 to SWE.6), project management, quality assurance, configuration, problem and change management, supplier monitoring, release, functional safety and cybersecurity |
| **12** role agents | system engineer, software requirements engineer, software architect, software developer, unit verification engineer, software and system test engineers, safety engineer, cybersecurity engineer, project manager, configuration manager, and an independent reviewer |
| **28** review checklists | the checks a review applies - by script, by an independent reviewer agent, or by a named person |
| **55** item types, **23** link roles, **78** coverage rules | from stakeholder requirement to code, test, review, baseline and release, checked by a deterministic trace engine |
| **32** processes, **265** base practices | Automotive SPICE 3.1, with evidence and open findings per base practice; Automotive SPICE 4.0 from its draft 3.991, **197** base practices mapped onto 3.1 |
| **12** parts, **48** clauses, **669** requirement numbers | ISO 26262:2018 - a decision and its evidence per clause |
| **41** subclauses, **118** requirement identifiers, **42** work products | ISO/SAE 21434:2021 - a decision and its evidence per subclause |
| **40** document kinds, **4** formats | specifications, architecture and design descriptions, test specifications and reports, TARA, safety and cybersecurity plans and cases, project and quality reports - as HTML, PDF, Word or Excel, neutral or in the customer's template |
| **6** exchange routes | ReqIF, AUTOSAR ARXML, Excel, and REST connectors to Polarion, codebeamer and Jama Connect |
| **14** tools, over **9,000** lines of Python | trace engine, record writer, document generator, validators, exchange adapters |
| **325** regression tests | trace engine, records, documents, exchange adapters and hooks |
| **155** items, **31** documents, **345** pages | the worked example of a software supplier: a power window with anti-pinch protection at ASIL B |
| **105** items | the worked example of a system supplier: a door control unit from the OEM's requirements through system architecture, bench integration and qualification, supplier, risks and vulnerability monitoring to a delivered release |

**See what it produces:** [31 documents, 345 pages, generated from the worked example](examples/power-window/documents/) -
requirements, architecture and design, test specifications and reports, traceability, TARA,
safety and cybersecurity cases - as PDF, HTML, Word and Excel.

## Status

Every process of the VDA scope of Automotive SPICE 3.1 has a skill - SYS.2 to SYS.5,
SWE.1 to SWE.6, MAN.3, SUP.1, SUP.8 to SUP.10 and ACQ.4. The worked example runs the
software processes end to end, with ISO 26262 and ISO/SAE 21434 in scope:

| Area | State |
|---|---|
| Process catalog | 32 processes of Automotive SPICE 3.1 with base practices, work products and rating dependencies, 26 of them covered by evidence structures and rules (23 with skills) and the others in the catalog only; 32 processes of Automotive SPICE 4.0 built from the draft 3.991 (which its publisher marks as not for assessments), each base and generic practice mapped to the 3.1 practices whose evidence it reads. Identifiers and official names; descriptions in our own words |
| Item schema | 55 item types, 23 link roles, 78 coverage rules, scope-aware |
| Documents | 40 kinds - specifications, SAD, SDD, test specifications and reports with verdicts, traceability, review, release note, QA, problem, change, project, risk, supplier, TARA report and worksheet, cybersecurity plan and case - generated from the items as HTML, PDF, Word or Excel (`tools/document.py`), in a neutral style or the customer's Word template or Excel workbook, with commit, baseline and the items' hashes; DRAFT when items are not approved |
| ISO 26262 | parts in scope per project; safety plan with a decision per clause and methods per table, hazardous events and safety goals, ASIL carried through requirements and design, safety analyses (FMEA, FTA, DFA), decomposition, tool evaluation, confirmation measures, safety case; `traceability.py safety`; the standard's tables are stated by the project, not copied |
| ISO/SAE 21434 | clauses in scope per project; TARA (assets, damage and threat scenarios, attack paths, risk values from the project's matrix, treatment), goals and claims, concept, security relevance down to code and tests, vulnerability management, cybersecurity case and assessment records; `traceability.py tara` and `clauses` |
| Trace engine | structure, links, coverage, stale approvals, suspect links, impact, traceability matrices, evidence per base practice, changes since a review, progress against the plan, integration steps and the builds and runs on them at software and system level, problems, quality assurance, observations per generic practice of level 2 |
| Exchange | ReqIF import, comparison of a new version, export (`tools/reqif.py`); AUTOSAR Classic models to architecture items and back to a comparison (`tools/arxml.py`); pipeline templates for GitHub Actions and GitLab CI (`ci/`) |
| Skills | project scoping and input registration; project management and risk management (MAN.3, MAN.5); SYS.2 to SYS.5 and SWE.1 to SWE.6; reviews and quality assurance; baselines, change requests and problem resolution; supplier monitoring; trace check, process gates and a mock assessment |
| Hooks | imported inputs, final records and baselined items are protected; every written item is checked |
| Out of scope | hardware development (ISO 26262 part 5) and the hardware-related clauses 8:13; organization-level requirements (ISO/SAE 21434 clause 5, ISO 26262-2 clauses 5 and 7, REU.2, capability level 3) - a project refers to the organization's evidence; motorcycles (ISO 26262 part 12). The catalogs list them; no rule or skill covers them |
| Exchange | ReqIF, Excel (requirements in and out, test results in), Polarion, codebeamer and Jama Connect over REST (written from their public interface descriptions, tested against a simulated server), AUTOSAR ARXML |
| Not yet | Automotive SPICE 4.0 from its released text: the catalog follows the draft 3.991 until then, without the rating consistency rules; HWE, MLE and SUP.11 in the catalog only |

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
- Python 3.10 or later on the PATH as `python` (or `python3`), with PyYAML
  (`python -m pip install pyyaml`); python-docx for Word and openpyxl for customer Excel
  workbooks are optional
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

Clone the repository and look at the worked example first:

```
git clone https://github.com/Lieubk/automotive-safety-security-assurance-kit.git
cd automotive-safety-security-assurance-kit
python tools/traceability.py --project examples/power-window check
python tools/traceability.py --project examples/power-window practices
python tools/traceability.py --project examples/power-window impact SWR-0003
python examples/power-window/tests/unit/run_tests.py
python examples/power-window/tests/integration/run_tests.py
python examples/power-window/tests/qualification/run_tests.py
```

## Install into your project

The toolkit is a Claude Code plugin. Install it into the repository of your project; the
items, records and `project.yaml` live there, the toolkit stays in the plugin.

```
/plugin marketplace add Lieubk/automotive-safety-security-assurance-kit
/plugin install assurance-kit@assurance-kit
```

From a shell, `claude plugin marketplace add Lieubk/automotive-safety-security-assurance-kit`
and `claude plugin install assurance-kit@assurance-kit --scope project` do the same and write
the plugin into the project's `.claude/settings.json`, so that every member of the team is
asked to install it.

Then open Claude Code in your project and run `/aspice-start` (as a plugin skill also
`/assurance-kit:aspice-start`). It asks who you are in the supply chain, what you were
given, and which processes you are responsible for, and writes `project.yaml`. From there
`/next-step` says what to do. A new session prints where the toolkit is installed and the
working agreement; the tools run from your project folder as
`python "<toolkit root>/tools/<script>.py"`. To be asked less often, allow the read-only
ones in your project's `.claude/settings.json` with the path the session prints.

Without the plugin you can still work in a copy of this repository: open it in Claude
Code, and every skill, agent and hook is active there.

## How it is put together

```
aspice/3.1/        process catalog and notes per process
aspice/4.0/        process catalog from the draft 3.991, mapped to 3.1
schema/            item types, links, coverage rules; file layout of an item
tools/             trace engine, record writer, validators, tests
.claude/skills/    one skill per activity
.claude/agents/    roles with boundaries; the reviewing agent cannot write
.claude/hooks/     protection and checks on every write
.claude/docs/      working agreement, command reference, review checklists
.claude-plugin/    plugin manifest and marketplace; hooks/hooks.json runs the hooks from the plugin
examples/          power-window (software supplier), door-control-unit (system supplier)
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
