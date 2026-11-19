---
name: component-qualification
description: "Qualify a software component that was not developed for this project under ISO 26262 (part 8 clause 12): a supplied library, an operating system, a component reused from elsewhere, when it carries requirements of ASIL A to D - its specification at the version used, the qualification method and evidence, the result and its restrictions; or argue an element proven in use from its field history (part 8 clause 14). Use when the trace check reports COV-75 or COV-77, when a supplied or reused component of ASIL A to D enters the architecture, when an element in series production is carried over, or when a version changes."
argument-hint: "[a CMP ID, a CQL or PIU ID, or nothing for the components that need a qualification]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Qualification of software components (ISO 26262-8 clause 12)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Shows that a component the project did not develop under the standard is fit for the
safety requirements allocated to it. A `component-qualification` item holds one
qualification of one component at one version, linked to it with `qualifies`. Where the
component was developed under ISO 26262 by the party of an interface agreement, the
safety plan says so for clause 8:12 instead, and no qualification is written.

| Clause | What this skill does | Evidence it leaves |
|---|---|---|
| 26262-8:12 Qualification of software components | lists the supplied and reused components of ASIL A to D; with the user, writes the specification of the component, the method and evidence of its qualification, the result and restrictions | `component-qualification` (26262-8:12.5.1 to 12.5.3); COV-75; its review through `/review` |
| 26262-8:14 Proven in use argument | when the user wants field history to replace parts of the lifecycle: the candidate, its modifications, the field data against the limit the safety plan states, the credit | `proven-in-use-argument` (26262-8:14.5.1, 14.5.2); COV-77; its review with `proven-in-use.md` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Part 8 not under `scope.safety`: say so and stop.
3. Run `python tools/traceability.py check` and read `COV-75`. Read the safety plan's
   entry for clause 8:12: when it is not-applicable or by-customer with a reason, say so
   and stop unless the user wants a qualification anyway.

## Steps

### 1. Which components
- From `COV-75`: the components of origin supplied or reused with ASIL A to D and no
  approved qualification. For each, `show <CMP-ID>`: the requirements allocated to it,
  the interfaces it provides and uses, `supplier` and version.

### 2. Specification
- Read `references/qualification-template.md`. Write with the user what the component
  does at the version used: functions, interfaces, configuration, resources, the
  assumptions of use its documentation states. Questions to the supplier become a
  `query` to whoever delivered it.

### 3. Method, evidence, result
- Ask how the component is qualified: analysis of its documentation against the
  allocated requirements, tests of those requirements on the component (as unit or
  integration tests of this project, with their runs), or both, at the depth its ASIL
  calls for. Name the evidence; a test result exists only as a run record.
- Documents of another party that the evidence rests on (a supplier's test report, a
  customer's field data report or safety manual) are listed under `inputs` of
  `project.yaml` with version and date received, and kept under `inputs/`, so that the
  reviewer reads the same version (`/aspice-start` adds the entry).
- The result and any restrictions are the safety manager's statement. Restrictions are
  carried into the architecture or the requirements of the components that use it.

### 4. Proven in use instead (clause 8:14)
- Only when the user chooses it and field data exists. Read
  `references/proven-in-use-template.md`. The safety plan must decide clause 8:14
  performed or tailored and state the incident rate limits in its `method_selection`
  for the proven in use tables; a missing plan entry is `/safety-plan` work first.
- The evaluation period, the incidents counted and the result are the safety manager's
  statements from field data that exists; nothing is estimated here.

### 5. Review
- Status `in-review` when complete; `/review` with
  `.claude/docs/checklists/component-qualification.md`, or `proven-in-use.md`.

## Writing

- Show the item before writing it and ask: "May I write CQL-NNNN in
  `spec/software/qualification/`?" IDs from
  `python tools/record.py next-id component-qualification`; status `draft`.
- A new version of the component makes the qualification suspect (`qualifies` link):
  qualify the new version.

## Checks before you finish

Run `python tools/traceability.py check`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-75`: report each component that is still without an approved qualification.
- `COV-77`: report each argument whose element, credit or plan entry is missing.

## Hand-over

1. The components and their qualification state.
2. Restrictions and where they were carried.
3. Next: `/review`; `/sw-architecture` for restrictions; `/sw-unit-verify` or
   `/sw-integration-test` for the tests a qualification needs.

## Do not

- Do not state a component qualified without evidence that exists in the project.
- Do not qualify a component the safety plan leaves to another party, unless the user asks.
- Do not change the component or its supplier's documents.
