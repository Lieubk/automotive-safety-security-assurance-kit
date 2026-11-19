---
name: project-plan
description: "Write and keep the project plan (Automotive SPICE MAN.3): scope of work, life cycle and milestones, feasibility, estimation approach and resources, skills, interfaces and commitments, reporting. Use when MAN.3 is in scope and no approved plan of kind project exists (COV-27), when scope, milestones, resources or commitments change, or before the work breakdown is drafted."
argument-hint: "[nothing for a new plan, or the part to change: scope, life cycle, milestones, feasibility, resources, skills, interfaces, reporting]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Project plan (MAN.3)
> Toolkit root: `${CLAUDE_PLUGIN_ROOT}` - where this shows a placeholder instead of a folder, it is the repository you are in. The `tools/`, `schema/`, `aspice/`, `iso-26262/`, `iso-sae-21434/`, `examples/` and `.claude/docs/` named here and in the references lie in the toolkit root; run its tools from the project folder as `python "<toolkit root>/tools/<script>.py"`.

Writes the plan of kind `project`: what the project delivers and what it leaves out,
the life cycle and its milestones, whether the goals can be reached with the people and
time at hand, how work is estimated, which skills it takes, which parties the project
depends on and what it has committed to, and how progress is reported. The work itself
is broken down by `/work-breakdown`; progress is measured by `/project-status`.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| MAN.3.BP1 Define the scope of work | goals, deliverables, exclusions and what they rest on | `Scope` of the plan of kind `project` |
| MAN.3.BP2 Define project life cycle | phases or releases and milestones, each with its date and the baseline that marks it | `Approach`, `milestones` |
| MAN.3.BP3 Evaluate feasibility of the project | collects facts, assumptions and risks; records the decision a named person took | `Feasibility` |
| MAN.3.BP5 Define, monitor and adjust project estimates and resources | the estimation method and the resources and where they come from; the estimates are in the work packages | `Approach`, `Environment and tools` |
| MAN.3.BP6 Ensure required skills, knowledge, and experience | roles, the skills each needs, gaps and how they are closed | `Responsibilities` |
| MAN.3.BP7 Identify, monitor and adjust project interfaces and agreed commitments | parties, what is exchanged, commitments with dates and state | `Interfaces and commitments` |
| MAN.3.BP4, MAN.3.BP8, MAN.3.BP9 | not here: work packages, schedule and their consistency belong to `/work-breakdown` | - |
| MAN.3.BP10 Review and report progress of the project | sets cadence, audience and the thresholds that call for corrective action; the reports are written by `/project-status` | `Reporting` |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `MAN.3` is not in `scope.processes`, stop: "Project management is out of scope
   for this project. I write no project plan."
3. Run `python tools/traceability.py status` and `python tools/traceability.py check`
   (each command takes `--project <dir>` after the script name when the project is not
   the current directory). Grep `kind: project` in `plans/`.
4. An approved project plan that is to change: say that its approval becomes stale and
   run `python tools/traceability.py impact <PLN-ID>`. Work on the part named in the
   argument only.
5. Read `inputs`, `people` and `scope` in `project.yaml`, and the plan of kind
   `configuration-management` if one exists: its baseline purposes mark milestones.

## Steps

Read `references/plan-template.md` before the first question. It holds the layout and
an example for every section. Ask part by part; write down the user's answers in their
words; where the user has no answer, leave the part open and say so. Never fill in a
date, a name, a skill or a commitment yourself.

### 1. Scope of work
Ask for the goals and the reason for the project, what is delivered (software releases,
evidence, documents), what is explicitly not part of it, and which agreement or set of
inputs the scope rests on. Compare with `scope.processes` and `inputs`: a process in
scope whose work the scope does not mention, or an input that nothing in the scope
uses, is a question to the user.

### 2. Life cycle and milestones
Propose phases or releases from the processes in scope and from the milestones of the
customer the user names. Each milestone gets the date the user states and the purpose
of the baseline that marks it reached, exactly as the configuration management plan
writes it. A milestone without such a baseline is allowed; `progress` then reports it
as not assessed, and the plan says how it is decided instead.

### 3. Estimation and resources
Ask how effort is estimated (method, unit, who estimates), and which resources the
work needs - people, tools and licences, test equipment, hardware samples - and where
each comes from and from when.

### 4. Skills
Per role: what the work demands (for example the platform, the coding guideline, the
safety standard at the project's ASIL), who brings it, and the gaps with how and by
when they are closed. Ask; never judge a person's competence.

### 5. Interfaces and commitments
List every party the project receives from or delivers to: the sources under `inputs`,
the customer, suppliers, other projects, internal units. For each: what is exchanged,
the contact role, and the commitments in both directions with date and state (agreed,
open), as the user states them.

### 6. Feasibility
Put together what is known: scope, milestones, resources, estimates if work packages
exist (`python tools/traceability.py progress`), assumptions and risks. Ask the person
who decides for the decision - feasible, feasible under named conditions, not feasible
- and write it with that person and the date. Do not propose it.

### 7. Reporting
Ask for cadence, audience and content of status reports, and for the thresholds that
call for a corrective action (for example a package late by more than one reporting
period, effort above estimate by a stated share, a milestone at risk).

### 8. Self-check
Apply the parts "Every plan" and "Kind project" of `.claude/docs/checklists/plan.md`.
Show the findings as proposals; correct what the user accepts.

## Writing

- Show the draft and ask: "May I write the project plan to `plans/<ID>.md`?" Take the
  ID from `python tools/record.py next-id plan`. Status `draft`, `kind: project`.
- Changing an approved plan: change the `status` line to `draft` first, then the content.
- Sections: `Scope`, `Approach` (life cycle, estimation method), `Criteria` (when a
  milestone counts as reached, when the plan is revised), `Environment and tools`,
  `Responsibilities` (roles, skills, gaps), `Feasibility`, `Interfaces and commitments`,
  `Reporting`; attribute `milestones`.

## Checks before you finish

Run `python tools/traceability.py check --all` and `python tools/traceability.py progress`.
- `FORMAT`, `SCHEMA` and `LINK` on the plan: fix them. Read the "still to come" line.
- Expected and to be said: `COV-27` for kind `project` until `/review` has approved the
  plan; `COV-32` and `COV-33` until `/work-breakdown` has planned the work.
- `progress` lists every milestone with its state; one without a baseline purpose shows
  as not assessed. Quote the lines.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session and what is open.
2. The feasibility decision as recorded, with who took it; the assumptions and risks.
3. The milestones with dates; commitments that are still open.
4. Parts the user could not answer yet.
5. Next: `/review` of the plan; `/work-breakdown` for the work packages.

## Do not

- Do not decide feasibility, commit a date or accept a risk for the user.
- Do not invent a date, a person, a skill, a resource or a commitment.
- Do not record an agreement with another party that the user has not stated.
- Do not write work packages here, and do not set any status but `draft`.
