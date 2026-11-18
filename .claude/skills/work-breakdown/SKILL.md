---
name: work-breakdown
description: "Break the project's work into work packages and activities with owners, estimates, planned dates and dependencies, link each package to the items it delivers, and keep the breakdown consistent with the project plan and its milestones (Automotive SPICE MAN.3.BP4, BP5, BP8, BP9). Use after the project plan exists, when the trace check reports COV-31 to COV-34, when items exist that no work package delivers (COV-32), or when the plan has to be adjusted."
argument-hint: "[nothing to plan or adjust everything, a release or feature to plan, 'link' to link new items, or work package IDs to adjust]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *)
---

# Work breakdown and schedule (MAN.3)

Turns the project plan into work packages: what is to be done, by whom, with which
estimate, from when to when, after what, and which items each package delivers. The
breakdown is the schedule as well: every package and activity carries its dates. The
trace engine checks the structure and the dates (COV-31 to COV-34); `progress` reads
from the delivered items how far each package has come.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| MAN.3.BP4 Define, monitor and adjust project activities | work packages and activities of trackable size with their dependencies; adjusted when the plan changes | `work-package` items, `part_of`, `depends_on`, `delivers`, `activities` |
| MAN.3.BP5 Define, monitor and adjust project estimates and resources | an estimate per package with its basis; compared with the actual effort of finished packages | `estimate`, `Estimate basis`; actuals under `progress` |
| MAN.3.BP8 Define, monitor and adjust project schedule | planned start and finish per package and activity, fitted to milestones and dependencies | `planned_start`, `planned_finish`; COV-34 |
| MAN.3.BP9 Ensure consistency | every item delivered by a package; dates of packages, activities and milestones agree; estimates fit the resources | COV-32, COV-34; the comparisons of step 6 |
| MAN.3.BP1 to BP3, BP6, BP7 | not here: `/project-plan` | - |
| MAN.3.BP10 | not here: `/project-status` | - |

## Before you start

1. If there is no `project.yaml`, stop: "This project has no scope yet. Run
   `/aspice-start` first."
2. If `MAN.3` is not in `scope.processes`, stop: "Project management is out of scope for
   this project. I plan no work packages."
3. Run `python tools/traceability.py status`, `python tools/traceability.py check` and
   `python tools/traceability.py progress` (each takes `--project <dir>` after the script
   name when the project is not the current directory).
4. Find the plan of kind `project` (Grep `kind: project` in `plans/`). Without one, stop
   and name `/project-plan`. A plan still in draft or in review may be planned against
   at risk: say that the packages have to be checked against it again once it is
   approved, because nothing in the check links the two.
5. With the argument `link`, go to step 4 alone. With package IDs, work on those only:
   an approved package that changes loses its approval; say so first.

## Steps

### 1. What has to be done
Read the plan: scope, milestones, estimation method, roles. List the processes in
scope and what each produces for the release (the item types of `schema/items.yaml`
whose `supports` name the process). Add the management and support work: planning and
reporting, reviews, configuration management, change requests, quality assurance - as
far as those processes are in scope. Show the list and ask whether it is complete.

### 2. Structure
Read `references/work-package-template.md`. Propose a tree: a top package per release
or feature, below it packages per process or per component, and packages for
management and support work (COV-33 asks for all three categories). A package is small
enough when its state can change within one reporting period of the plan; otherwise
split it. Activities inside a package are the steps of the toolkit: drafting with the
authoring skill, `/review`, implementation, verification.

### 3. Owners, estimates, dates, dependencies
For each package ask for the owner, the estimate in the plan's unit with its basis, and
planned start and finish. Propose dependencies from the V-model order (requirements
before architecture before design before code before verification) and from the
deliveries the plan names under `Interfaces and commitments`; the user confirms each.
A package that needs a delivery from outside starts after the date of that commitment.

### 4. Link what is delivered
For every item that exists, set `delivers` on the package that produces it. `check`
reports items no package delivers (COV-32). Linking is tracking and does not make an
approved package stale. A package whose deliverables do not exist yet says what they
will be in `Deliverables`, and is linked when they appear.

### 5. Estimates against actuals
Where packages are finished (`progress`), compare actual effort with the estimate and
show the ratio. If the user wants to adjust open estimates because of it, that is a
change of those packages (step 3), recorded in their `Estimate basis`.

### 6. Consistency
Run `check` and `progress`. Then compare, and show the user:
- every milestone of the plan against the planned finish of the packages whose
  deliverables it needs: none finishes after it;
- per owner, the summed estimates of overlapping packages against the time the plan's
  resources give that role: name every overload;
- every commitment under `Interfaces and commitments` that delivers to the project
  against the packages that depend on it.
What does not fit is a decision for the user: move dates, change scope, add resources -
or adjust the plan with `/project-plan`.

### 7. Self-check
Apply `.claude/docs/checklists/work-breakdown.md`. Show the findings as proposals.

## Writing

- Show the tree as a table (ID, parent, title, category, owner, estimate, start,
  finish, depends on, delivers) and ask: "May I write these N work packages to
  `plans/work-packages/`?" IDs from `python tools/record.py next-id work-package`.
  Layout: `references/work-package-template.md`. Status `draft`.
- An approved package that changes in plan content - dates, estimate, owner,
  structure: change the `status` line to `draft` first, then the content.
- `delivers` and `progress` are tracking: change them with Edit without touching the
  status.

## Checks before you finish

Run `python tools/traceability.py check --all` and `python tools/traceability.py progress`.
- `FORMAT`, `SCHEMA`, `LINK` on packages written in this session: fix them.
- `COV-31` (cycle, two parents) and `COV-34` (dates): fix them or name them as open.
- `COV-32` and `COV-33` should be gone for what this session planned. Quote what remains.
- Quote the summary line of `progress`.

## Hand-over

Report, in this order:
1. The base practice table with what was done in this session.
2. The tree with estimates and dates; the sum of the estimates per release and per owner.
3. What did not fit in step 6 and what the user decided; open questions.
4. Next: `/review` of the work packages (checklist `work-breakdown`); `/project-status`
   once work has started.

## Do not

- Do not commit a date, an estimate or an owner the user has not confirmed.
- Do not mark a package done: completion is stated by its owner in `progress` and
  checked against its deliverables by `progress`.
- Do not change the project plan here; propose the change and name `/project-plan`.
- Do not set any status but `draft`.
