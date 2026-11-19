---
name: process-gate
description: "Readiness check of one process or of every process in scope: a verdict per base practice and per process (PASS, CONCERNS, FAIL, NOT ASSESSED), built from the trace engine's observations by a fixed mapping plus a semantic sample of the evidence. Use before a baseline, a release, a delivery or an assessment, or to see what a process still lacks. It is a self-check by the team, not an assessment and not a rating."
argument-hint: "[a process ID such as SWE.1, or nothing for every process in scope]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(python tools/traceability.py *)
---

# Process gate
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Answers one question per process: is it ready, and if not, what stands against it. The
skill takes the observations of `python tools/traceability.py practices` and `check`,
maps each to a verdict by the table in `references/verdicts.md`, reads a sample of the
evidence against what each base practice expects, and reports both kinds of result
apart. This is a readiness check by the team itself. It is not an assessment, gives no
rating and no capability level.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| Every base practice of the process asked for | maps the engine's observation to a verdict and reads a sample of the evidence | none: the items and records are the evidence; the report, saved on request under `reports/`, is a plain file |
| Practices the schema has no evidence structure for | NOT ASSESSED by the toolkit; asks what evidence exists outside the repository | the answer, reported as the user's statement |
| GP 2.1.1 to GP 2.1.7 and GP 2.2.1 to GP 2.2.4, when the target level is 2 or higher | lists them as NOT ASSESSED by the toolkit, with what a person would look for | - |
| SUP.1.BP3 | not done here: a gate the team runs on its own work is not an independent check of process activities; `/quality-assurance` uses the report as input for the check of the person the quality assurance plan names | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. Run `python tools/traceability.py status` and `python tools/traceability.py check
   --all` and read both. Every command of this skill takes `--project <dir>` right
   after the script name when the project is not the current directory. If the
   commands do not run, stop: every verdict is NOT ASSESSED, with the reason (for
   example PyYAML is missing).
3. With `26262` or `21434` (optionally a part or clause: `26262 6`, `21434 15`) as
   argument, the gate runs per clause of that standard: read `references/standards.md`
   and use `python tools/traceability.py safety [PART] --json` or
   `python tools/traceability.py clauses [CLAUSE] --json` in place of `practices`; the
   steps below apply to clauses as they do to base practices.
   With a process as argument run `python tools/traceability.py practices <PROCESS>`.
   If it answers "<PROCESS> is not in the scope of this project", stop: "<PROCESS>: NOT
   ASSESSED - out of scope." Do not gate a process the project is not responsible for.
   Without an argument run `python tools/traceability.py practices`.
4. Say before any result: "This is a readiness check by the team itself, not an
   assessment and not a rating."
5. Ask what the gate is for: a baseline (which purpose), a release (which one), a
   delivery, or the current state. The answer decides how unfinished items count.

## Steps

### 1. Collect the facts
- Keep the `practices` table and the summary line of `check`, both as printed.
- From the output of `check --all` note three things the states alone do not show:
  units without code (`COV-10 ... designed but not implemented`), items in draft or
  in review whose last review left findings open (`COV-19 ... left findings open`),
  and lines without a bracket. The report names all three.
- Run `python tools/traceability.py practices <PROCESS> --json` as well: `by` names the
  item types, link roles and rules that feed each practice.
- Read `references/verdicts.md` now. It holds the mapping, what the states do not
  tell, and the rules for the sample.
- If the gate is for a baseline that already exists, run
  `python tools/traceability.py audit <BL-ID>` and quote it: it lists every item that
  differs from what the baseline recorded.

### 2. Map each practice to a verdict
A finding is counted for the process that produces the item it is on. Quote `check`
lines without a bracket separately; `references/verdicts.md` says what they mean.

| State printed by `practices` | Verdict |
|---|---|
| `findings open` | FAIL; quote the `check` lines behind it |
| `no evidence yet` | FAIL; name the item types that would carry the evidence |
| `evidence not settled` | FAIL when an unsettled item carries open review findings or belongs to what the gate is for; otherwise CONCERNS (`references/verdicts.md`) |
| `warnings open` | CONCERNS; quote the warnings. Warnings marked pending on units without code: `references/verdicts.md` |
| `no evidence structure` | NOT ASSESSED by the toolkit; go to step 3 |
| `evidence present` | PASS for the deterministic part only; go to step 4 |

### 3. Practices without evidence structure
Ask, practice by practice or grouped: "The toolkit holds no evidence for <practice>.
What evidence exists outside this repository, and who can show it?" Report the answer
as "stated by <who answered>". The verdict stays NOT ASSESSED: a statement is not a
check. "Nothing exists" is reported as stated, too.

### 4. Sample the evidence
For each practice with `evidence present`:
- Read at least three of the items or records behind it, or all if there are fewer.
  Choose as `references/verdicts.md` says, not the three that look best.
- Read the row of the practice in `aspice/3.1/notes/<PROCESS>.md` and compare what it
  says must be true with what the sampled items contain. Under `aspice.version` 4.0 the
  notes are those of 3.1: read the rows of the practices its `maps_to` names, and the
  intent of the 4.0 practice in `aspice/4.0/processes/<PROCESS>.yaml`.
- Report what was read (IDs), what was looked for, and what was found, with the text.
- No concern: the practice is PASS, stated as "deterministic part by the engine, sample
  of N of M read". A concern: CONCERNS, as a proposal the user confirms or rejects.
  Sample not possible (notes or items cannot be read): NOT ASSESSED, with the reason.

### 5. Verdict per process
The process verdict is the worst verdict among its practices, in the order FAIL, NOT
ASSESSED, CONCERNS, PASS. Always give the count per verdict next to it, so that a NOT
ASSESSED does not hide the concerns beside it.

### 6. Capability level
Read `aspice.target_level` in `project.yaml`. If the key is absent or empty, ask the
user for the target level; do not assume level 1. For level 2 or higher
read `references/level-2.md` and list every generic practice of level 2 as NOT ASSESSED
by the toolkit, with what a person would look for. Say plainly: a result at level 1 is
not a result at level 2, whatever the verdicts above are.

### 7. Report
Build the report from `references/output-format.md` and show it. Then ask whether to
save it.

## Writing

- Nothing is written unless the user asks for the report file.
- Ask: "May I save this report as `reports/process-gate-<scope>-<date>.md`?" It is a
  plain Markdown file, not an item: no front matter, no ID, not in a folder listed
  under `paths.items`. If `reports` is listed there, ask for another folder.
- The file starts with the sentence of step 4 of "Before you start" and names who asked
  for the gate and what it was for.

## Checks before you finish

- Every base practice of every process gated has exactly one verdict, and the numbers
  in the report are those `practices` and `check` printed in this session.
- Every NOT ASSESSED names what was not assessed and why; every PASS names what was
  read; every FAIL and CONCERNS quotes a line or a text.
- Every `check` line without a bracket is quoted and its consequence stated.
- No item, record or status changed: run `python tools/traceability.py check --all`
  again and compare the summary line with the one from the start.

## Hand-over

Report, in this order:
1. The sentence that this is a self-check, what the gate was for, and the summary line
   of `check` with the number of active coverage rules and the processes in scope.
2. Per process: the practice table with engine state, deterministic result, sample
   result and verdict; then the process verdict with the count per verdict.
3. Statements by people, each with who made it.
4. The level 2 list, when the target level is 2 or higher.
5. Next, by cause: `/review` for approvals and consistency; the authoring skill for
   missing or unsettled items; `/baseline` for what was not communicated;
   `/trace-check` for an explanation of single findings.

## Do not

- Do not rate: no N, P, L or F, no percentage of achievement, no capability level.
- Do not turn a statement of the user into PASS, and do not let a clean `check` stand
  for practices the toolkit cannot see.
- Do not fix findings, change a status or write a record. This skill reads.
- Do not reuse numbers from an earlier run or from memory.
- Do not call the result an assessment, an audit or a release decision. People decide
  what happens with a FAIL or a CONCERNS.
