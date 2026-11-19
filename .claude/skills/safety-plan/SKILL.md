---
name: safety-plan
description: "Project-dependent functional safety management of ISO 26262 (part 2 clause 6, part 8 clause 11): safety roles, impact analysis of what is new, changed or reused, the safety plan with a decision per clause in scope and tailoring with reasons, the methods applied per table of parts 4, 5, 6 and 8, the ASIL and tool confidence determinations as the project applies them, confirmation reviews, audit and assessment with their independence, tool evaluation and qualification, and the safety case. Use when a part of ISO 26262 is under scope.safety and no approved plan of kind safety exists (COV-27), when the trace check reports COV-63, COV-64, COV-71 to COV-73, when a tool is introduced, or before a release."
argument-hint: "['plan', 'methods', 'tools', 'confirmation', 'case', or nothing for the state per clause]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *), Bash(python tools/record.py confirmation-measure *), Bash(python tools/record.py safety-case *)
---

# Functional safety management of the project (ISO 26262-2 clause 6, 26262-8 clause 11)

Sets up how the project achieves functional safety and shows that it did: who is
responsible, which clause of the standard is done how, which methods are applied at
which ASIL, which tools can be trusted, who confirms the work with which independence,
and the argument at the end. The result is a `plan` of kind `safety`, `tool-evaluation`
items, `confirmation-measure` records and a `safety-case`.

| Clause | What this skill does | Evidence it leaves |
|---|---|---|
| 26262-2:6 Project dependent safety management | asks for the safety roles, the impact analysis, the decision per clause and the confirmation measures; drafts the safety plan | plan of kind `safety` (26262-2:6.5.3); COV-27, COV-63 |
| 26262-4:5, 26262-5:5, 26262-6:5 General topics | asks which methods the project applies per table of the parts in scope, as it reads the standard, and where they are written | `method_selection` of the plan; COV-64 |
| 26262-3:6, 26262-8:11 determinations | has the project state the ASIL and tool confidence determinations it applies, so that `check` can compare | `asil_determination`, `tcl_determination` of the plan; COV-65, COV-71 |
| 26262-8:11 Confidence in the use of software tools | evaluates every tool the records name: use cases, impact, detection, confidence level; qualification where needed | `tool-evaluation` (26262-8:11.5.1, 11.5.2); COV-71, COV-72 |
| 26262-2:6 confirmation measures | prepares confirmation reviews, the audit and the assessment; records what the independent person states | `confirmation-measure` records (26262-2:6.5.5); COV-73 |
| 26262-2:6 safety case | prepares the evidence per clause; the responsible person writes the argument | `safety-case` (26262-2:6.5.4) |
| 26262-8:5 Interfaces within distributed developments | drafts the development interface agreement with the customer or a supplier; records the agreement only when the user states it | plan of kind `development-interface-agreement` (26262-8:5.5.2) |
| 26262-2:6 release for production | not a record of its own: a baseline whose communication record names the case and the assessment | `/baseline` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. `scope.safety` empty or absent: say that the project declares no part of ISO 26262
   and stop; `/aspice-start` adds them.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py safety`. Read `COV-27` for kind `safety`, `COV-63`,
   `COV-64`, `COV-71` to `COV-73`. The checks run on the plan while it is drafted.
4. Say early which answers keep reviews from approving, so that the user can get them in
   time: who is safety manager and who performs the confirmation reviews with which
   independence (PLN-170, PLN-172); for every supplied or reused component of ASIL A to D,
   who accepted its evidence, or that the development interface agreement leaves it to the
   customer (ARC-11); an analysis of every component of ASIL A to D before the architecture
   review (ARC-85). Determinations not stated yet do not block: `check` reports what they
   leave unassessed.

## Steps

### 1. Roles, impact analysis, plan (26262-2:6)
- Read `references/safety-plan-template.md`. Ask, one at a time: the safety manager and
  the other safety roles; what is new, changed or reused and what that means for the
  activities (the impact analysis goes into `Scope`); the decision per clause.
- `safety` lists every clause of the parts in scope: one entry per clause in
  `safety_activities`, written `"<part>:<clause>"`. Tailored and not-applicable entries
  need the user's reason; by-customer and by-supplier need the development interface
  agreement with that party.

### 1a. Development interface agreement (26262-8:5)
- Where a customer or supplier performs part of the safety activities, draft the plan of
  kind `development-interface-agreement` with `shared_activities`, in the same form as the
  cybersecurity interface agreement of `/cybersecurity-plan`.
  Record the agreement only when the user states that both parties agreed.

### 2. Methods per table
- For every table of parts 4, 5, 6 and 8 in scope, ask which methods the project applies
  for which ASIL, as the responsible people read the standard, and where they are
  written (the unit verification, integration and qualification strategies, the coding
  guideline). Write one `method_selection` entry per table. The toolkit lists the
  tables by number and title only.

### 3. Determinations
- Ask the safety manager to state the ASIL determination and the tool confidence
  determination the project applies, typed from their copy of the standard into
  `asil_determination` and `tcl_determination`. Without them, `check` reports ASILs and
  confidence levels as not assessed.

### 4. Tools (26262-8:11)
- `COV-72` lists the tools the build and analysis records name that no evaluation covers.
  For each, read `references/tool-evaluation.md` and evaluate with the user: use cases,
  what an error of the tool could introduce or hide, how likely it is detected. The
  confidence level follows from the plan's determination; TCL2 and TCL3 need a
  qualification method and its evidence.

### 5. Confirmation measures
- The plan's `confirmation_measures` name what is confirmed, by which measure, with which
  independence. When a measure is done, record what the named person states:
  `python tools/record.py confirmation-measure --kind <kind> --subject "<as in the plan>"
  --item <ID> ... --performed-by "<name>" --independence <I0..I3> --result <result> --report <file>`.

### 6. Safety case
- Run `python tools/traceability.py safety` and show the evidence per clause and the open
  findings. The person responsible writes the argument; write their words to a file and,
  on their yes, run `python tools/record.py safety-case --prepared-by "<name>" --argument <file>`.

## Writing

- Show each plan or evaluation before writing it and ask: "May I write PLN-NNNN in
  `plans/`?" IDs from `python tools/record.py next-id <type>`; status `draft`; approval
  through `/review` with `plan.md` or `tool-evaluation.md`.
- Names, independence and results come from the user; reports and arguments are the
  words of the person who stands behind them.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py safety`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-27`, `COV-63`, `COV-64`, `COV-71` to `COV-73`: report each with what closes it.

## Hand-over

1. The clause table with what was done and what is open.
2. The decisions per clause and the clauses without evidence, as `safety` prints them.
3. Decisions still owed: roles, tailoring, methods, determinations, assessors.
4. Next: `/review`; `/hara`, `/safety-concept`, `/safety-analysis`; `/baseline` for the release.

## Do not

- Do not copy the tables of ISO 26262 - methods, ASIL or TCL determination, independence -
  into the toolkit or into a plan written by the toolkit; the project types what it applies.
- Do not decide tailoring, independence, a confidence level or a confirmation result in
  anyone's name.
- Do not write the safety case argument or a confirmation report yourself.
