---
name: cybersecurity-concept
description: "Turn approved cybersecurity goals into the cybersecurity concept and carry it into development (ISO/SAE 21434 clauses 9.5, 10 and 11): cybersecurity controls and requirements derived from each goal, requirements on the operational environment, their allocation to system or software elements, security relevance carried down to design, code and tests, verification of the specifications, integration and verification with methods chosen for cybersecurity, and validation of the goals. Use when goals are approved and no requirement is derived from them (COV-59), when security relevance does not follow the goals (COV-60), when goals lack validation (COV-62), or when a goal or a security-relevant requirement changes."
argument-hint: "[a CSG ID, 'allocate', 'verify', 'validate', or nothing for the goals and their requirements]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Cybersecurity concept and development (ISO/SAE 21434 clauses 9.5, 10, 11)

Decides with the user how each cybersecurity goal is achieved - which technical or
operational controls, which requirements on the item, its components and its
environment - and makes sure the engineering processes carry those requirements down:
allocated in the architecture, marked security-relevant, designed, implemented,
verified and, at vehicle level, validated. Requirements are the existing
`system-requirement` and `software-requirement` items with `derived_from` the goal; the
engineering skills do the work at each level, this skill keeps the thread.

| Subclause | What this skill does | Evidence it leaves |
|---|---|---|
| 21434:9.5 Cybersecurity concept | proposes controls per goal; drafts requirements derived from the goal and requirements on the operational environment; the allocation follows in the architecture | requirements with `derived_from` a goal (WP-09-06); COV-59; their review (WP-09-07) through `/review` |
| 21434:10.4.1 Design | carries security relevance down the architecture, design and code; asks for the coding rules and design notations; records weaknesses found | `security_relevant` on derived and allocated items (WP-10-01); COV-60; conventions in `project.yaml` (WP-10-03); `weakness` items (WP-10-05) |
| 21434:10.4.2 Integration and verification | makes sure the integration and qualification tests cover the security-relevant items, with methods chosen for cybersecurity | test cases verifying security-relevant items (WP-10-06); runs (WP-10-07) |
| 21434:11 Cybersecurity validation | asks for a system qualification test per goal where clause 11 is in scope | system qualification tests that verify goals (WP-11-01); COV-62 |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. None of the clauses 9, 10, 11 under `scope.cybersecurity`: say so and stop.
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py clauses`. Read `COV-59`, `COV-60`, `COV-62`.
4. Goals not approved: say that the concept builds on approved goals and name `/tara`
   (or `/import-inputs` for goals received from the customer). Do not derive from drafts.

## Steps

### 1. Controls per goal (9.5)
- Read `references/concept.md`. For each approved goal, show it with the threat
  scenarios it addresses (`show <CSG-ID>`, `tara`) and propose controls: what protects the
  asset on each attack path. Ask the user to choose; a control is a design decision when
  alternatives were weighed: `/sys-architecture` or `/sw-architecture` records it.
- Requirements on the operational environment (what the vehicle, the backend or the
  workshop has to provide) are requirements allocated to an external system element.

### 2. Requirements (9.5, 10.4.1)
- Draft the requirements: `system-requirement` where SYS.2 is in scope, otherwise
  `software-requirement`; each `derived_from` the goal, `security_relevant: true`,
  stating what is protected, not how. The conventions of `/sys-requirements` or
  `/sw-requirements` apply, and so does their checklist.
- Allocation: `/sys-architecture` or `/sw-architecture`. Elements that fulfil a
  security-relevant requirement are security-relevant themselves (`COV-60`).

### 3. Security relevance downwards (10.4.1)
- Run `python tools/traceability.py impact <CSG-ID>` for each goal and list the items
  below it. Items without `security_relevant: true` are reported by `COV-60` once they
  derive from or fulfil a security-relevant item; propose the change, the owner of the
  item decides through the skill of its level.
- Ask for the coding rules and design notations the project uses for security-relevant
  code (for example MISRA C and a secure coding standard) and where they are recorded
  (`conventions` in `project.yaml`, `/aspice-start`).
- A weakness found in design, code or review is recorded as a `weakness` with
  `found_by: design` or `review`: `/vulnerability-management`.

### 4. Integration, verification and validation (10.4.2, 11)
- For each security-relevant requirement, check that a qualification or integration
  test verifies it (`matrix`). Ask which methods the plans name for cybersecurity:
  requirements-based tests, interface tests, fuzzing, penetration tests, resource tests.
  Missing methods are a change of the integration or qualification plan:
  `/sw-integration-test`, `/sw-qualification-test`, `/sys-integration-test`.
- Clause 11 in scope: each goal needs a system qualification test that `verifies` it
  (`COV-62`), specified with `/sys-qualification-test` and run on the vehicle.

## Writing

- Show each requirement before writing it and ask: "May I write SWR-NNNN in
  `spec/software/requirements/`?" IDs from `python tools/record.py next-id <type>`;
  status `draft`; approval through `/review`.
- Do not change items of other levels here: propose, and name the skill that owns them.

## Checks before you finish

Run `python tools/traceability.py check` and `python tools/traceability.py clauses 9`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-59`, `COV-60`, `COV-62`: report each with what closes it.

## Hand-over

1. The subclause table with what was done and what is open.
2. Per goal: its requirements, their allocation, the tests that verify them, as
   `matrix` and `show` print them.
3. Decisions still owed: controls, methods of verification, coding rules.
4. Next: `/review` for the requirements; the architecture, design and test skills named
   above; `/vulnerability-management` for weaknesses found.

## Do not

- Do not choose a control or a verification method for the user.
- Do not mark an item security-relevant or not in anyone's name; propose it.
- Do not derive requirements from a goal that is not approved, and do not edit a goal
  received from the customer.
