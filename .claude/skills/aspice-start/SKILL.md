---
name: aspice-start
description: "Set up or change the scope of a project: role in the supply chain, inputs received, processes the team is responsible for, assessment scope, target capability level, safety and security, platform, toolchain, paths and accountable people. Writes project.yaml and nothing else. Use at the start of every project, when no project.yaml exists, or when role, scope or inputs change."
argument-hint: "[nothing for a new project, or the part to change: role, inputs, processes, assessment, level, safety, platform, toolchain, paths, people]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *)
---

# Project intake and scoping

Where a project starts depends on who the team is in the supply chain and on what it
was given. This skill asks for both, has the user mark out the processes the team is
responsible for, and writes the answers to `project.yaml` in the project root. It
writes nothing else: no items, no plans, no records. Every other skill reads this file
first, and the trace engine runs only the rules of the processes named in it.

The skill performs no process of the catalog. It records the decisions that these
practices start from; none of the rows is evidence for a rating on its own.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| MAN.3.BP1 Define the scope of work | records which processes the team is responsible for and which an assessment will rate; goals, deliverables and exclusions of the project are defined by `/project-plan` | `scope` in `project.yaml` |
| MAN.3.BP7 Identify, monitor and adjust project interfaces and agreed commitments | records who delivered which input and who is accountable for reviews; the interfaces and commitments of the project are kept by `/project-plan` | `inputs`, `people` |
| SYS.1.BP1 Obtain stakeholder requirements and requests | records which documents were received, in which version and when; their content is registered by `/import-inputs` | `inputs` |
| SUP.8.BP2 Identify configuration items | records where items and code live and which code is generated or third-party; the list of configuration items belongs to the configuration management plan | `paths` |

## Before you start

1. Look for `project.yaml` in the project root. If it exists, this is a re-run: read
   it, read "Changing an existing file" in `references/project-yaml.md`, show the
   current file, ask what is to change and go through only the steps concerned.
2. Run `python tools/traceability.py status`. If it lists items although there is no
   `project.yaml`, say so: without a scope the trace engine runs every rule. Every
   command of this skill takes `--project <dir>` after the script name when the
   project is not the current directory; `project.yaml` is then written there.
3. Read `aspice/<version>/index.yaml` (`aspice.version` of an existing file, 3.1
   otherwise) and list the installed skills with Glob `.claude/skills/*/SKILL.md`.
   Step 3 states both as facts, not from memory.
4. Ask one step at a time, in the order below. After each answer restate what will be
   recorded and get a yes before the next question. "Not decided yet" is a valid
   answer: record an empty value and list it as open in the hand-over. Never derive
   an answer from an earlier one without asking.

## Steps

### 1. Role in the supply chain
Ask which of these the team is: vehicle manufacturer; system supplier (delivers an
ECU: system and software); software supplier to a system supplier; supplier of a
software component only; engineering service working on defined work packages.
Read `references/roles-and-processes.md` and show the typical process set of the role
as a starting proposal for step 3. Say that it is a proposal: the role decides nothing.

### 2. Inputs received
Go through the levels one by one: stakeholder or customer requirements, system
requirements, system architecture and interfaces, software requirements, software
architecture, component descriptions or models, existing code. For each level ask
whether something was received and, if so, per document: source (its name as the
deliverer calls it), version, date received, format. The `level` values are in
`references/project-yaml.md`. What was not received is not recorded; step 10 shows
whether it is missing.

### 3. Processes the team is responsible for
First ask which version of Automotive SPICE the customer or the assessment uses: `3.1`
(the default) or `4.0`. Before the user decides, say what 4.0 means here, from "Model
version" in `references/roles-and-processes.md`. Record the answer as `aspice.version`.

Show every process of `aspice/<version>/index.yaml`, grouped as in
`references/roles-and-processes.md`: ID, name, whether it is in the VDA scope, and
what the toolkit has for it today (an authoring skill that is installed; or catalog,
schema and trace rules only; or the catalog only). Mark the typical set of the role.
Ask the user to pick. Read the picked list back and have it confirmed. Do not pick for
the user, do not add a process because the role suggests it, and do not accept an
empty list: it would put every process in scope.

### 4. Assessment
Ask whether an assessment is planned and, if so, which processes it will rate. Read
"Responsibility and assessment scope" in `references/roles-and-processes.md`.
- Every process the assessment rates but the team is not responsible for gets a
  warning: no rule of it is active, no skill produces its evidence, and the assessment
  will ask for it all the same. A requirement set delivered by a customer does not by
  itself take the analysis process out of an assessment.
- Offer the two ways out (take the process into the responsibility, or clarify with
  whoever commissions the assessment where the process is rated) and let the user
  decide. Record both lists as stated, also when they stay different.

### 5. Target capability level
Ask for the level the processes in scope aim at: 1, 2 or 3. Explain what changes, in
the few lines of "Target level" in `references/roles-and-processes.md`. Warn when the
target is 2 or 3 and `MAN.3`, `SUP.1` or `SUP.8` is neither in the responsibility nor
in the assessment scope. The toolkit shows gaps; it does not rate.

### 6. Safety and security
Ask for the highest ASIL of any function of the product (QM, A, B, C, D) and whether
the product is cybersecurity relevant. Say what follows: items carry `asil` and
`security_relevant`, an item may not fall below what it is derived from (COV-23), and
unit coverage targets are set per ASIL in the unit verification plan (COV-28). QM is a
statement, not a default: if nobody has decided yet, leave the value empty.
When the highest ASIL is above QM, ask which parts of ISO 26262 the team is responsible
for and which the customer or a supplier performs (show the parts of
`iso-26262/2018/catalog.yaml` with their level); a software supplier typically has parts
2 (clause 6), 6, 8 and 9. Write them under `scope.safety`. Part 5 (hardware) and part 12
(motorcycles) are outside what the toolkit supports: if named, say so; the catalog lists
them, no rule checks them. Organization-level clauses (ISO 26262-2 clauses 5 and 7,
ISO/SAE 21434 clause 5) are the organization's: the plans decide them `by-organization`.
When the product is cybersecurity relevant, ask which clauses of ISO/SAE 21434 the team
is responsible for and which the customer or a supplier performs (show the clauses of
`iso-sae-21434/2021/catalog.yaml` with their level: organization, project, lifecycle,
method). Write the team's under `scope.cybersecurity`. Clause 5 is the organization's,
not a project's; say so if it is named.
Then ask for the project's rules that reviews check against, one by one, as listed
under `conventions` in `references/project-yaml.md`: what the safety plan or the
customer demands of the design notation and of review independence per ASIL, the
naming convention, the limits for functions. Record what the user states and where it
is written; for "nothing" or "not known yet" leave the value empty and say which
toolkit default applies until someone states otherwise.

### 7. Platform and toolchain
Ask: AUTOSAR Classic or not (if not, what instead); microcontroller; language
standard; coding guideline set; compiler; static analyser; unit test tool; coverage
tool; the requirements or ALM tool the items must be exchanged with. Name and version
for each tool. Say plainly: requirements arrive best as ReqIF (`/import-inputs` reads
it with `tools/reqif.py`) and AUTOSAR models as ARXML (`/sw-architecture` with
`tools/arxml.py`); other formats are read as documents; a verification tool that is
missing later shows up as `NOT ASSESSED`, never as a silent skip.

### 8. Where things live
Ask for the source roots, and for the patterns of generated and of third-party code.
Explain: every file under a source root must belong to exactly one software unit
(COV-11) unless a pattern exempts it. The folder of each item type is fixed by
`schema/items.yaml`; `paths.items` only names the folders that are scanned, so keep
the default unless the user has a reason. Check with Glob that the source roots exist;
one that does not exist yet is recorded and listed as open.

### 9. People
Ask for the names and roles of the people who are accountable: who reviews and
approves inputs, requirements, architecture, design and code, and test cases; who
decides on change requests; who the contact at the source of each input is. Review
records need real names and at least one reviewer who did not write the item: say so
if only one person is named. Record only names the user gives.

Some accountable checks of the review checklists can only be answered by a role: ask
for the person who holds it, and say which reviews stall without them.
- `safety.highest_asil` above QM: who is responsible for functional safety (system
  architecture SYA-84, unit verification PLN-29, safety analyses).
- System level in scope: who leads hardware, software and mechanics, or who speaks for
  them (system architecture SYA-83, integration strategy).
- `security.relevant`: who is responsible for cybersecurity.
A role that does not exist in the project is recorded as such under `people` with the
reason; the check then is answered `not-applicable` with that reason, never `pass`.

### 10. Derive the starting point
Read `references/starting-point.md`. From the answers derive and explain:
- the first process in scope, and every other process whose upstream is out of scope;
- the inputs at each such boundary: received (to be registered with `/import-inputs`
  and accepted through an input acceptance review) or needed but not received (a gap
  the user must close with the source);
- the plans the scope needs (`plan_kinds` in `schema/items.yaml`, rule COV-27);
- with SWE.1 in scope, the trace route: ask whether every system requirement allocated
  to software gets its own software requirement (the default, COV-05), or whether
  tracing through the software element is to count (`trace.derive_via_elements`);
- the order of work, with the skill for each step or the note that none exists today;
- the warnings of steps 3 to 5.

## Writing

- Build the complete file from the template in `references/project-yaml.md`: every
  key, in that order, unanswered values empty.
- Show the whole file and the starting point, then ask: "May I write this to
  `project.yaml`?" Write that one file. In a re-run show and edit only what changes.
- Say that the file now holds names of real people: it belongs in the project
  repository, not in anything that is published.

## Checks before you finish

Run `python tools/traceability.py check` and quote the summary line.
- The command stops with a YAML error: the file is broken; fix it and run again.
- The scope in the summary line must be the list confirmed in step 3.
- `COV-27` (one per plan the scope needs) and, with `SWE.2` in scope, `COV-25` are
  expected on a new project. Report them as the first work list, not as defects.
- In a re-run compare the number of active coverage rules before and after, and say
  which went silent or became active.

## Hand-over

Report, in this order:
1. The base practice table with what was recorded in this session.
2. The scope as written: role, processes, assessment scope, target level, and every
   warning the user decided to live with.
3. The starting point of step 10, and the open answers (empty values).
4. Next: `/import-inputs` for the boundary inputs; if there are none, the first
   authoring skill of step 10. `/next-step` says at any time where the project stands.

## Do not

- Do not choose or change the processes in scope on your own judgement.
- Do not write an empty `scope.processes`, and do not drop a process silently:
  removing one silences its rules, which hides findings without resolving them.
- Do not write items, plans, records or folders. This skill writes `project.yaml`.
- Do not record an assessment, an agreement or a name the user has not stated.
- Do not call the scope sufficient for a capability level. An assessment rates.
