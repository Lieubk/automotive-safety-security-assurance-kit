# Configuration management plan

File: `plans/<ID>.md`. Type `plan`, `kind: configuration-management`. Attributes and
sections are those of type `plan` in `schema/items.yaml`. A project has one such plan.
While SUP.8 is in scope the trace check reports `COV-27` until the plan is approved, and
`python tools/record.py baseline` then refuses every baseline that is not an internal
one.

The plan is the strategy (SUP.8.BP1). It is also the only place where the practices
without an evidence structure are answered at all: which things are configuration items,
how the repository is set up, how branches are handled, how storage is secured. Write
every rule so that a person can show against it that the rule is kept.

## Decisions to ask the user before drafting

Ask these, with the options, and write down the answers. Do not fill in a value the user
has not given; a value taken from the template below is a proposal and is shown as one.

| Decision | Typical options | Lands in |
|---|---|---|
| What is under configuration management | item files; records with the tool output they refer to; code and test code; build and test scripts; project configuration; imported inputs; tools and compilers by pinned version | `Scope` |
| What is deliberately not | build output that can be reproduced; personal notes | `Scope`, with the reason |
| How a version is identified | an item by ID and content hash; the whole by a commit; a released state by a tag | `Approach` |
| Product variants | none; one code base with items marked by `variants`; a baseline per variant | `Approach` |
| Repository | one Git repository; several, with the rule that ties their versions together | `Environment and tools` |
| Access rights | who may change the main branch, who may set tags, who administers | `Environment and tools`, `Responsibilities` |
| Branch rules | what always holds on the main branch; when a branch is created and how it is named; how it is merged and who reviews the merge; who may allow an exception | `Approach` |
| What shows that a merge is good | trace check without error; unit tests of the affected units; a reviewer who is not the author | `Approach` |
| Change control | from which moment an item changes only through a change request; how imported inputs are treated | `Approach`; has to agree with the change request management plan where one exists |
| Baseline purposes | for each purpose: when it is due and how its tag is formed | `Approach` |
| Which purposes are internal | those that are not communicated | `Approach`, and with the same words under `trace.internal_baselines` in `project.yaml` |
| What a baseline must fulfil | no error in the trace check; which items have to be approved for which purpose; no open change request, or the open ones accepted as known open points | `Criteria` |
| Baseline audit | before which baselines; who performs it; what happens when a difference shows; where its output is kept | `Criteria` |
| Who is informed of which baseline | per purpose: roles and parties, and the channel | `Criteria` |
| Status reporting | what is reported, from which command or record, to whom, how often | `Approach` |
| Storage, backup, archiving | where the repository is hosted; how often it is backed up; how long deliveries are kept; when a restore is tried | `Environment and tools` |
| Who does what | roles, not names of people | `Responsibilities` |
| When the plan is updated | new repository or tool, change of scope, a new release line | `Scope` |

Three answers have consequences in the tools. Say so when you ask:

- The purposes. `python tools/record.py baseline --purpose` takes the text as it is. A
  purpose counts as internal only if it equals an entry of `trace.internal_baselines`,
  character by character. Internal means: created even while the check reports errors,
  every plan and engineering item is listed whatever its state, nothing is protected
  afterwards, and no communication record is demanded (COV-26).
- The branch. The skill compares the first line of `git status --short --branch` with
  the branch the plan names.
- What has to be approved. A baseline that is not internal lists the approved items
  only and leaves the others out without stopping. The plan therefore has to say what
  must be approved for each purpose, or a freeze can be taken with half its content.

## Template

The values are those of the power window example (`examples/power-window`, plan
PLN-0002) and are invented. Replace every one of them with what the user decides.

```markdown
---
id: PLN-0002
type: plan
title: Configuration management plan
status: draft
kind: configuration-management
---

## Scope

Under configuration management is everything the project produces, and everything
needed to reproduce a delivery:

| Configuration items | Where |
|---|---|
| Plans, requirements, architecture, design, test cases | item files under `plans/`, `spec/`, `verification/` |
| Evidence: reviews, test runs, analysis runs, baselines, communication | item files under `records/` and `verification/runs/`, tool output under `verification/evidence/` |
| Change requests | item files under `records/changes/` |
| Source code and test code | `src/`, `tests/` |
| Build and test scripts, project configuration | `tests/**/*.py`, `project.yaml` |
| Imported inputs | item files marked `imported`, unchanged from what was received |
| Compiler and analyser | not stored; name and version are recorded with every run |

Not under this plan: build output (`build/`), because it is reproducible from the above.

Declared limitation: the basic software of the door module is integrated by the
customer and is not a configuration item here. The stand-in headers for host builds are.

This plan is revised when the repository or a tool changes, when the process scope in
`project.yaml` changes, and when a second release line is opened.

## Approach

Identification. Every item has an ID that is never reused and is the name of its file.
A version of an item is identified by its content hash, a version of the whole by a
commit, a released state by a tag. The product has no variants; if one is added, items
that do not apply to all variants carry `variants`, and each baseline names its variant
in the tag.

Version control. One Git repository holds all configuration items. History on the main
branch is never rewritten.

Branches.
- `main` always holds a state in which the trace check reports no error.
- Work happens on a short-lived branch per task or change request, named after it.
- A branch reaches `main` through a reviewed merge request. The reviewer is not the
  author. Before the merge the trace check and the unit tests of the affected units
  have run on the branch without error.
- Exceptions are allowed by the Configuration Manager and noted in the merge request.

Change control.
- Items that are in no baseline change freely on a branch. An approved item that
  changes loses its approval until it is reviewed again.
- An item inside a baseline changes only through an approved change request that names
  it. A commit that changes such an item names the change request in its message.
- Imported inputs are never edited. A problem with an input goes to its source as a
  query; a new version from the source is registered as a new version.

Baselines. A baseline is a tag on `main` plus a baseline record that lists the approved
items with content hash and status.

| Purpose | When | Tag |
|---|---|---|
| working | at any time, for internal reference; lists every item in its present state and protects nothing | `work-<date>` |
| requirements freeze | software requirements approved | `req-<n>` |
| design freeze | architecture and detailed design approved | `design-<n>` |
| release candidate | unit verification complete for the release content | `rc-<release>-<n>` |
| delivery | handed to the customer | `rel-<release>` |

`working` is the only internal purpose (`trace.internal_baselines` in `project.yaml`).

Status reporting. `python tools/traceability.py status` and `check` give the status of
all items at any commit. The Configuration Manager passes both outputs to the project
lead with every baseline and at least once a month.

## Criteria

A baseline other than `working` is created only when:
- the trace check reports no error at the commit to be tagged;
- every item the purpose is about is approved (the table above), so that none of them
  is left out of the record; for a delivery this means every item;
- no change request that affects a listed item is open, unless the project lead has
  accepted it as a known open point; it is then named in the baseline notice.

Baseline audit. Before a delivery, `python tools/traceability.py audit` is run on the
content of the tag: every listed item with its hash and state, and no approved item
unlisted. Any difference stops the delivery. The Configuration Manager confirms the result and keeps the output, with
date and commit, in the delivery documents.

Communication. A baseline other than `working` is made known as follows; who was
informed is recorded in a communication record that names the baseline.

| Purpose | Informed |
|---|---|
| requirements freeze | software architect, software developers, unit verification, customer system engineering |
| design freeze | software developers, unit verification |
| release candidate | project lead, quality assurance, with the unit verification results |
| delivery | customer system engineering and customer integration, with the status output |

## Environment and tools

- Git. The repository is hosted on the team's server. Only the Configuration Manager
  may set tags and change branch protection; `main` accepts merge requests only.
- `tools/traceability.py` for status, impact, content hashes and the baseline audit;
  `tools/record.py` for baseline and communication records.
- Backup: the server is backed up daily by the operator of the server; a restore of the
  repository is tried once per release and noted by the Configuration Manager.
- Retention: delivery baselines and everything they reference are kept for the period
  the customer contract requires.

## Responsibilities

| Activity | Performs | Checks or approves |
|---|---|---|
| Keeping this plan and the branch rules | Configuration Manager | project lead |
| Creating baselines, setting tags, baseline audit | Configuration Manager | project lead for delivery |
| Reviewing merge requests | a team member who is not the author | - |
| Deciding on change requests | Change Control Board | - |
| Following the rules in daily work | everyone who commits | Configuration Manager, by sampling |
```

## Notes

- The five sections are those the schema demands of a `plan`. `Scope`, `Approach` and
  `Criteria` are needed before review, the other two before approval.
- The plan is a configuration item itself and is listed in every baseline. After the
  first baseline it changes only through `/change-request`.
- The skill reads from the plan: the purposes with their conditions and tag patterns,
  the branch, the criteria, the audit rule and who is informed. Everything else in the
  plan is checked by people only. Leave out rules that nobody is going to check.
- A baseline that is not internal protects the items it lists against changes of
  content and against being retired. Registering `source_files` on a listed unit is
  neither, so code can be written for a baselined design without a change request.
- If the internal purposes of the plan and `trace.internal_baselines` differ, tell the
  user which one to correct. This skill does not change `project.yaml`.
- Roles in the plan, people in `project.yaml`: no names of persons in the plan.
