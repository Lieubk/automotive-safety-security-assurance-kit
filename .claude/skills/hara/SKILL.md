---
name: hara
description: "Hazard analysis and risk assessment of ISO 26262 part 3 (clauses 5 and 6): the item definition, hazards from malfunctions of the item, hazardous events in operational situations classified by severity, exposure and controllability, their ASIL by the determination the safety plan states, and the safety goals with safe states and fault tolerant time intervals. Use when part 3 is under scope.safety and the HARA is to be done or redone after a change of the item, or when the trace check reports COV-65 or COV-66."
argument-hint: "['item', 'hazards', 'classify', 'goals', an HZE or SG ID, or nothing for the state of the HARA]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Hazard analysis and risk assessment (ISO 26262-3 clauses 5, 6)

Finds out what the item can do wrong at vehicle level, in which situations that harms
someone, and how much protection each case needs. The result is an `item-definition`,
`hazardous-event` items classified by severity, exposure and controllability with their
ASIL, and the `safety-goal` items that answer them. The classification is the
judgement of the people named in the safety plan; the skill proposes with reasons.

| Clause | What this skill does | Evidence it leaves |
|---|---|---|
| 26262-3:5 Item definition | describes functions, boundary, interfaces, environment and dependencies, from the system architecture where it exists | `item-definition` (26262-3:5.5.1), shared with ISO/SAE 21434 |
| 26262-3:6 Hazard analysis and risk assessment | proposes malfunctions, hazards and operational situations; the responsible people classify; the ASIL follows the determination of the safety plan; safety goals are written | `hazardous-event` with `arises_in`; `safety-goal` with `addresses` (26262-3:6.5.1); COV-65, COV-66; its review (26262-3:6.5.2) through `/review` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Part 3 not under `scope.safety`: say that the HARA is not the project's and stop. A
   HARA or safety goals received from the customer are inputs: `/import-inputs`
   registers them unchanged.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py safety 3`. Read `COV-27` for kind `safety`, `COV-65`,
   `COV-66`.
4. No approved safety plan with `asil_determination`: say that the ASILs cannot be checked
   (`check` reports it as not assessed) and offer `/safety-plan`. The project types the
   determination there from the standard; the toolkit does not carry it.

## Steps

### 1. Item definition (26262-3:5)
- An item definition written for ISO/SAE 21434 serves here too; read it and complete what
  safety needs: functions and their behaviour at vehicle level, known hazards, legal
  requirements, the elements the item depends on. Read `references/hara-templates.md`.
- An imported item definition (`imported`, delivered by the customer) is never edited.
  When clause 3:5 is the project's, write the project's own item definition, naming the
  delivered one in its text and taking over what still holds; otherwise what safety
  needs from it is a `query` to whoever delivered it (`/import-inputs`).

### 2. Malfunctions, hazards, situations
- For each function, propose malfunctioning behaviours with a guide-word method the
  plan names (for example: no function, function when not requested, too much, too
  little, too early, too late, stuck). For each, the hazard at vehicle level and the
  operational situations in which it matters (speed, road, weather, occupants,
  workshop). One `hazardous-event` per combination that counts, `arises_in` the item.

### 3. Classification (ASIL)
- Propose severity, exposure and controllability with the reasons in
  `Classification rationale`: who is harmed and how badly, how often the situation
  occurs, who could avoid the harm and how. The responsible people rate; record their
  ratings and who gave them.
- The ASIL is the one the plan's `asil_determination` gives; `check` compares (`COV-65`).
  Never pick an ASIL by judgement when the plan's determination gives one.

### 4. Safety goals
- For every hazardous event of ASIL A to D, a `safety-goal` that `addresses` it, with an
  ASIL not lower than the highest event it addresses (`COV-66`), its safe state and fault
  tolerant time interval where one applies. Similar events may share a goal.
- Goals go to `/safety-concept`, which refines them into requirements (`COV-67`).

## Writing

- Show each item before writing it and ask: "May I write HZE-NNNN in
  `spec/safety/hara/`?" IDs from `python tools/record.py next-id <type>`; status `draft`.
- Ratings are recorded as the named people state them; a proposal nobody confirmed stays
  marked as a proposal in the rationale.
- After a change of an approved item: `python tools/traceability.py impact <ID>`.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py safety 3`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-65`, `COV-66`: report each with what closes it.

## Hand-over

1. The clause table with what was done and what is open.
2. The hazardous events by ASIL with their goals, as `safety` prints them.
3. Ratings still owed by people.
4. Next: `/review` with `.claude/docs/checklists/hara.md`; `/safety-concept`.

## Do not

- Do not rate severity, exposure or controllability in anyone's name, and do not lower a
  rating to reach a lower ASIL.
- Do not copy the classification tables or the ASIL determination of ISO 26262 into
  items; the safety plan holds what the project applies.
- Do not edit a HARA item received from the customer; questions go back as a `query`.
