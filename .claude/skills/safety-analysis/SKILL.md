---
name: safety-analysis
description: "Safety analyses of ISO 26262 (part 9 clauses 6 to 8, part 6 clause 7, part 4 clause 6): FMEA, FTA, HAZOP or another method on system or software elements, dependent failures analysis for coexistence of different ASILs and for decompositions, findings with the measures that answer them, carried into requirements or design, and the verification of the analyses. Use when an element of ASIL A to D has no analysis (COV-69), when a decomposition needs its independence argued (COV-70), when findings are open (COV-68), or when an analysed element changes."
argument-hint: "[an element or SAN ID, 'fmea', 'fta', 'dfa', or nothing for the elements and their analyses]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Safety analyses (ISO 26262-9 clauses 6 to 8, 26262-6 clause 7, 26262-4 clause 6)

Examines how elements can fail and what that does to the safety goals, and makes sure
each weakness found is answered by a measure carried into a requirement or the design,
or argued. A `safety-analysis` item holds one analysis of one or more elements at one
level, with its findings as a structured list.

| Clause | What this skill does | Evidence it leaves |
|---|---|---|
| 26262-9:8 Safety analyses | runs an inductive (FMEA) or deductive (FTA) analysis with the user on the elements in question | `safety-analysis` with `analyses` and `findings` (26262-9:8.5.1); COV-68 |
| 26262-6:7 Software architectural design | analyses every software component of ASIL A to D at software level; argues freedom from interference where ASILs mix | software-level analyses (26262-6:7.5.2, 7.5.3); COV-69 |
| 26262-4:6 Technical safety concept | analyses the system elements of ASIL A to D at system level | system-level analyses (26262-4:6.5.7); COV-69 |
| 26262-9:6, 26262-9:7 Coexistence, dependent failures | analyses common causes and cascading failures between elements that must be independent or free from interference | `safety-analysis` of method `dfa` (26262-9:7.5.1); COV-69, COV-70 |
| verification of the analyses | prepares their review | review records (26262-9:8.5.2, 7.5.2) through `/review` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. None of the parts 4, 6, 9 under `scope.safety`: say so and stop.
3. Run `python tools/traceability.py check` and `python tools/traceability.py safety`.
   Read `COV-68` to `COV-70`. The analysed elements must exist: an analysis of an
   architecture that is not drafted yet waits for `/sw-architecture` or `/sys-architecture`.

## Steps

### 1. What to analyse
- From `COV-69`: the components and elements of ASIL A to D without an analysis, and
  whether ASILs coexist without a dependent failures analysis. From `COV-70`: the
  decompositions waiting for theirs. Ask the user which analysis to do now.

### 2. Method and scope
- Read `references/analysis-templates.md`. Agree on the method: FMEA (from each failure
  mode of an element to its effect), FTA (from a violated goal down to causes), DFA
  (common causes and cascades between elements that must be independent). Write
  `Scope` (elements, depth, the goals or requirements it is measured against) and
  `Method` (guide words, fault models, initiators).

### 3. Findings
- Work through the elements with the user, reading their items (`show <ID>`): interfaces,
  units, timing, shared resources. Each finding: the fault, its effect up to the goal, the
  measure that prevents, detects or controls it, and `carried_by` the requirement or
  element that carries the measure. A measure without a carrier is a new requirement or
  a design change: hand it to the skill that owns the item.
- A finding that needs no measure is closed with a `rationale` the user states.

### 4. Results and review
- Write `Results`: what the analysis shows as a whole and what stays open. Status
  `in-review` when complete.
- Order of approval: the analysis is drafted on the drafted architecture and read by the
  architecture review (ARC-85 asks that it exists, not that it is approved); the
  architecture is approved first, then the analysis with `/review` and
  `.claude/docs/checklists/safety-analysis.md`, because an approved analysis may not rest
  on elements that are not (`UPSTREAM`).

## Writing

- Show each analysis before writing it and ask: "May I write SAN-NNNN in
  `spec/safety/analyses/`?" IDs from `python tools/record.py next-id safety-analysis`;
  status `draft`.
- When an analysed element changes, the analysis is suspect (`analyses` link): run
  `python tools/traceability.py impact <ID>` and redo what changed.

## Checks before you finish

Run `python tools/traceability.py check`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-68` to `COV-70`: report each with what closes it.

## Hand-over

1. The clause table with what was done and what is open.
2. The analyses with their open findings and the measures handed on.
3. Next: `/review`; the requirement or architecture skill for new measures;
   `/safety-concept` for decompositions.

## Do not

- Do not close a finding without a carrier or the user's rationale.
- Do not state a failure rate, a diagnostic coverage or a probability nobody measured or
  sourced.
- Do not copy example analyses or tables of the standard into items.
