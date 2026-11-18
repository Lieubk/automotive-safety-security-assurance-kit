---
name: trace-check
description: "Run the trace engine and explain what it reports: findings grouped by rule, what each rule means in plain words, which base practice it matters for, and which skill resolves it. Reads only and fixes nothing. Use when the check shows errors or warnings, before a review, a baseline or a process gate, or when someone asks what a FORMAT, SCHEMA, LINK, COV, UPSTREAM, SUSPECT, CONSISTENCY or QUERY line means."
argument-hint: "[--all to include drafts, and optionally a rule name or an item ID to narrow the explanation]"
allowed-tools: Read, Glob, Grep, Bash(python tools/traceability.py *)
context: fork
model: haiku
effort: low
background: false
---

# Trace check, explained

Runs `python tools/traceability.py check` and turns its lines into something a team can
act on: what is wrong, why it matters, who resolves it. The facts come from the engine
and are quoted as printed; the explanation comes from `references/rules.md`. The skill
changes no file. It performs no process on its own; it shows where the traceability
and consistency practices of the processes in scope stand.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| Traceability practices in scope: SYS.2.BP6, SYS.3.BP6, SYS.4.BP7, SYS.5.BP5, SWE.1.BP6, SWE.2.BP7, SWE.3.BP5, SWE.4.BP5, SWE.5.BP7, SWE.6.BP5, SUP.10.BP8 | reports links that are missing, broken or not allowed, per rule | none: the links in the items are the evidence; `matrix` prints them |
| Consistency practices in scope: SYS.2.BP7, SYS.3.BP7, SYS.4.BP8, SYS.5.BP6, SWE.1.BP7, SWE.2.BP8, SWE.3.BP6, SWE.4.BP6, SWE.5.BP8, SWE.6.BP6 | reports stale approvals, approvals above items that are not approved, items and code changed after their review, and comparisons no review recorded | none: the review records written by `/review` are the evidence |
| Every other practice a finding names in its bracket | says which practice the finding stands against | none |
| Whether a practice is fulfilled | not done here: `/process-gate` gives a verdict per practice | - |

## Before you start

1. If there is no `project.yaml`, say so before anything else: without a scope the
   engine treats every process as in scope, and the summary line says
   `scope: all processes`. Run the check anyway if the user wants it, and point to
   `/aspice-start`.
2. Run `python tools/traceability.py status` and `python tools/traceability.py check`.
   Every command of this skill takes `--project <dir>` right after the script name when
   the project is not the current directory.
3. If a command does not run (no Python, no PyYAML, a broken `project.yaml`), stop:
   "Trace check: NOT ASSESSED - <what failed>". Do not explain findings from memory or
   from an earlier run.

## Steps

### 1. Run the check
- Default: `python tools/traceability.py check`. With `--all`, or when the user asks
  about drafts: `python tools/traceability.py check --all`, which adds the `info` lines:
  gaps on drafts, and per item what its next state will still require.
- Quote the summary line exactly, for example:
  `73 items | scope: SUP.8, SWE.1, SWE.2, SWE.3, SWE.4 | 21 of 30 coverage rules active | 0 errors, 0 warnings, 0 on drafts`

### 2. Say what was checked and what was not
- Repeat the number of active coverage rules and name the processes in scope.
- Read `references/rules.md`. From the column "Processes" of its coverage table list
  the rules that are inactive for this scope and say in one sentence each group what
  therefore went unchecked. For the scope above: nothing about system requirements and
  system architecture as the project's own work (`COV-01` to `COV-04`), about
  integration and qualification tests (`COV-13` to `COV-16`), or about change requests
  (`COV-20`).
- If the summary says "N on drafts" and `--all` was not used, say that N `info` lines
  are hidden.

### 3. Group the findings
- Group by rule, then by item. The same line can be printed several times; count items.
- Order: `FORMAT`, `SCHEMA`, `LINK` first (a coverage result on a malformed item is not
  reliable); then `UPSTREAM`, `COV-19` and `SUSPECT` (approvals that do not hold); then
  the other coverage rules by number; then `CONSISTENCY` and `QUERY`; then `info`
  lines, previews last.
- Name lines without a bracket separately: they count for no practice of the project
  but are findings all the same - a finding on an imported item, or an open query.
- With a rule name or an item ID as argument, show only those lines. The summary line
  and step 2 are still reported in full.

### 4. Explain each group
For each rule that occurs, from `references/rules.md`:
- what the rule expects and what the message says is missing, in plain words;
- the typical cause, offered as a possibility, not as a diagnosis;
- the base practices in the bracket of the line and why the finding matters for them
  ("Why a finding matters"), and what the level means here: an approved item breaking
  a rule (`error`), an item in review not there yet (`warning`), a draft (`info`);
- the skill that resolves it, after checking that it is installed;
- whether the schema allows a waiver, and what the waiver consists of. A waiver is
  written by the authoring skill and reviewed; say that this skill does not apply it.

Use facts to make a group concrete: `python tools/traceability.py show <ID>` for the
links of one or two example items, `python tools/traceability.py impact <ID>` for what
depends on an item whose approval is stale or whose change made others suspect,
`python tools/traceability.py list --status draft` for the drafts behind the `info`
lines. Read an item only when the user asks about its content.

### 5. Read a clean result correctly
With 0 errors and 0 warnings say what that establishes and what it does not:
- no active rule objects to an approved or reviewed item;
- inactive rules checked nothing (step 2), and drafts are only checked with `--all`;
- no rule reads meaning: whether a requirement is right or a test proves anything is
  decided in `/review`;
- practices the schema has no evidence structure for are not covered at all:
  `/process-gate` lists them.

## Writing

This skill writes nothing: no item, no record, no status, no report file. If the user
wants a finding resolved, name the skill and stop.

## Checks before you finish

- Every rule name that appears in the output is explained, and every explanation comes
  from `references/rules.md`. A rule name that is not in that file is reported as
  unknown, with the line, instead of being guessed at.
- The counts per group add up to the numbers of the summary line (lines, not items; say
  both where they differ).
- The number of active rules and the processes in scope are in the answer.

## Hand-over

Report, in this order:
1. The summary line, quoted, and the verdict of the trace check: `FAIL` with errors,
   `CONCERNS` with warnings only, `PASS` with neither - "PASS for the N active rules of
   <processes>" - or `NOT ASSESSED` when the engine did not run.
2. What was not checked: inactive rules, hidden drafts.
3. The groups, in the order of step 3, each with meaning, practices, resolving skill and
   waiver.
4. Next: the skill that resolves the first group; `/review` for `UPSTREAM`, `COV-19`,
   `SUSPECT` and `CONSISTENCY`; `/process-gate` for a verdict per base practice.

## Do not

- Do not fix anything, and do not offer to "just add the link".
- Do not explain a finding away. A coverage finding that is expected at this stage is
  still reported, with the reason why it is expected.
- Do not call a clean result "traceability is complete" or "consistent": say which
  rules ran.
- Do not invent a rule, a waiver or a skill that `references/rules.md`, the schema or
  the installed skills do not name.
