# Capability level 2: what the toolkit does not assess

The verdicts of the gate concern base practices: whether the outcomes of a process
exist. Level 2 asks in addition whether the work of that process is managed and whether
its work products are kept under control. That is judged per process, by generic
practices, and almost all of the evidence lies outside the item files.

When `aspice.target_level` in `project.yaml` is 2 or higher, run
`python tools/traceability.py generic <PROCESS>` for each process gated and list every
generic practice with the observation it prints - the state, the evidence IDs and the
note. If the key is absent or empty, ask the user for the target level; do not assume
one. Do not shorten the list to a sentence, and do not replace a line by "probably fine".

The observation is not a verdict. Map it as for base practices: `findings open` is FAIL;
`no evidence yet` and `evidence not settled` are CONCERNS at most; `evidence present` is
PASS only after a sample of the evidence was read against the row of the practice in
`aspice/3.1/notes/capability-levels.md`; `a person has to judge` and everything the
note says is not in the repository are **NOT ASSESSED by the toolkit**, with the
question a person has to answer.

Say with the list:

- A gate without FAIL is a statement about level 1 at most. It says nothing about level 2.
- Level 2 builds on level 1: a FAIL or CONCERNS above stands against level 2 before any
  generic practice is looked at.
- The generic practices are judged for each process separately ("is the work on the
  software requirements planned?"), not once for the project.
- Weak project management shows in the first group for every process; weak quality
  assurance and configuration management show in the second group for every process.

## Performance management (PA 2.1)

| Generic practice | What a person would look for, per process | Where the repository gives a starting point |
|---|---|---|
| GP 2.1.1 | objectives for carrying out this process: what is due when, how much effort and which resources it may take, which quality the outputs must reach, with assumptions and constraints | where MAN.3 is in scope: the work packages whose `process` is this process (`estimate`, `planned_finish`, `Deliverables`) and the milestones of the project plan; the strategy of the process for quality objectives |
| GP 2.1.2 | a plan for this process: activities with owners, effort and dates, milestones, estimates that are kept current, planned reviews of its work products | the work packages of the process with their `activities`; `release` on requirements shows content per release |
| GP 2.1.3 | plan against actual for the tasks of this process, deviations that were noticed and written down, status reports | `python tools/traceability.py progress` for the packages of the process; `project-status-report` records |
| GP 2.1.4 | what was done when the plan was missed: actions with owners and closure, re-planned dates with the reason, escalations | `corrective-action` items that address the packages or items of the process; escalations in `communication-record` items (`quality`) |
| GP 2.1.5 | who performs, who verifies and who approves each work product type of this process; the skills each role needs; that the people concerned were told | `Responsibilities` sections of the plans; `people` in `project.yaml`; `reviewers` in the review records |
| GP 2.1.6 | people, tools, licences and test equipment planned and really available; training or coaching of the people assigned; access to the inputs they need | `toolchain` in `project.yaml`; `Environment and tools` sections of the plans |
| GP 2.1.7 | who takes part in this process and exchanges what with whom; agreed channels and rhythm; minutes, action items, confirmations between the parties | `communication-record` items, with `agreement` where one was recorded; `inputs` in `project.yaml` |

## Work product management (PA 2.2)

| Generic practice | What a person would look for, per process | Where the repository gives a starting point |
|---|---|---|
| GP 2.2.1 | what each work product type of this process has to contain and how it is structured; quality criteria; criteria for review and approval, defined before the review | the type in `schema/items.yaml` with its attributes, sections and lifecycle; the checklists under `.claude/docs/checklists/` with their versions |
| GP 2.2.2 | rules for identification, versioning, storage, status, approval and distribution of the work products; how they depend on each other | the `plan` of kind `configuration-management`; `schema/item-format.md`; the link roles of the schema |
| GP 2.2.3 | which work products are controlled; their history and change records; baselines that tie versions to a product configuration; access; a revision status anyone can find | version control history; `baseline` records; `change-request` items; `status` and `hash` |
| GP 2.2.4 | reviews held as planned, against the criteria defined for the work product; findings followed to closure; rework and renewed approval | `review-record` items that name checklist and version, the date, the result of every check and the findings with their state; `quality-record` items of kind `work-product` where SUP.1 is in scope; whether the reviews were held as planned is not in the repository |

A starting point is not evidence. It tells the person who looks where to begin; whether
it is enough is that person's judgement. The keys of `project.yaml` named above
(`people`, `toolchain`, `inputs`) may be absent or empty: then say so instead of
describing what they would hold.

## Level 3

When the target is 3, add one line: the generic practices of level 3 (PA 3.1 and
PA 3.2) concern the standard process of the organization and how the project derives
its own process from it. That evidence is not in a project repository. NOT ASSESSED by
the toolkit.
