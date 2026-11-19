---
name: safety-concept
description: "Refine safety goals into the safety requirements of ISO 26262 and carry their ASIL down (part 3 clause 7, part 4 clause 6, part 6 clause 6, part 9 clause 5): functional safety requirements with safe states and fault tolerance, technical safety requirements with safety mechanisms, software safety requirements, their allocation, ASIL inheritance, ASIL decomposition as a design decision resting on a dependent failures analysis, and validation of the goals. Use when safety goals are approved and no requirement is derived from them (COV-67), when an ASIL does not follow its source (COV-23), when a decomposition is planned (COV-70), or when a goal changes."
argument-hint: "[an SG ID, 'functional', 'technical', 'software', 'decompose', or nothing for the goals and their requirements]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Safety concept (ISO 26262-3 clause 7, 26262-4 clause 6, 26262-6 clause 6)

Turns each safety goal into requirements that elements of the architecture can fulfil,
and keeps the ASIL with them. The requirements are the existing `system-requirement`
and `software-requirement` items with an `asil`: functional safety requirements derived
from goals, technical ones derived from those, software ones derived from the technical
ones or, in a software-only scope, from the goals. The engineering skills of each level
write and allocate them; this skill keeps the safety thread.

| Clause | What this skill does | Evidence it leaves |
|---|---|---|
| 26262-3:7 Functional safety concept | proposes functional safety requirements per goal: what is detected, the safe state, the fault tolerant time, warnings, degradation; their allocation follows in the architecture | system requirements with `derived_from` a goal (26262-3:7.5.1); COV-67, COV-23 |
| 26262-4:6 Technical safety concept | proposes technical safety requirements and safety mechanisms for the system elements, with the hardware-software interface | system requirements, elements, interfaces of ASIL above QM (26262-4:6.5.1 to 6.5.4) through `/sys-requirements`, `/sys-architecture` |
| 26262-6:6 Specification of software safety requirements | proposes software safety requirements from the technical ones and the hardware-software interface | software requirements with `asil` (26262-6:6.5.1) through `/sw-requirements` |
| 26262-9:5 Requirements decomposition | prepares a decomposition as a design decision with the dependent failures analysis it rests on | `design-decision` with `decomposition`; COV-70, COV-23 |
| 26262-4:8 Safety validation | asks for a system qualification test per goal on the vehicle where part 4 is in scope | system qualification tests that verify goals |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. None of the parts 3, 4, 6, 9 under `scope.safety`: say so and stop.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py safety`. Read `COV-23`, `COV-67`, `COV-70`.
4. Goals not approved and not received from the customer: name `/hara` and stop; the
   concept builds on approved goals.

## Steps

### 1. Functional safety requirements (26262-3:7)
- Read `references/safety-requirements.md`. For each goal show the hazardous events and
  propose requirements: fault detection, the transition to the safe state within the
  fault tolerant time, warnings to the driver, degraded operation, arbitration of
  requests. Each `derived_from` the goal, `asil` not lower than the goal's (`COV-23`).
- Allocation to elements of the preliminary architecture: `/sys-architecture`.

### 2. Technical and software safety requirements (26262-4:6, 26262-6:6)
- Technical: safety mechanisms per element (plausibility, monitoring, redundancy,
  watchdog), the hardware-software interface, requirements for production and service.
  `/sys-requirements` and `/sys-architecture` write and allocate them.
- Software: what the software has to detect, react to and guarantee, with timing,
  derived from the technical requirements or the goals. `/sw-requirements` writes them.
- Ask for the verification method each needs at its ASIL; the plan's `method_selection`
  says which methods apply.

### 3. Decomposition (26262-9:5)
- Only where the user wants to split a requirement onto independent elements with lower
  ASILs. Draft a `design-decision` with `decomposition` (requirement, into, independence)
  and ask `/safety-analysis` for the dependent failures analysis it rests on. The
  allowed schemes are in the standard; the user states which is applied.

### 4. Validation (26262-4:8)
- Part 4 in scope: each goal needs a system qualification test that `verifies` it, run on
  the vehicle (`/sys-qualification-test`).

## Writing

- Show each requirement or decision before writing it and ask: "May I write SWR-NNNN in
  `spec/software/requirements/`?" IDs from `python tools/record.py next-id <type>`;
  status `draft`; approval through `/review`.
- Items of other levels are written by the skill that owns them; propose and hand over.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py safety`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-23`, `COV-67`, `COV-70`: report each with what closes it.

## Hand-over

1. The clause table with what was done and what is open.
2. Per goal: its requirements, their ASIL and allocation, as `show` and `matrix` print them.
3. Decisions still owed: safe states, fault tolerance times, decompositions.
4. Next: `/review`; `/safety-analysis` for the architecture; the requirement and
   architecture skills of each level.

## Do not

- Do not lower an ASIL without an approved decomposition decision and its analysis.
- Do not choose a safe state, a fault tolerant time or a decomposition for the user.
- Do not edit a goal or requirement received from the customer.
