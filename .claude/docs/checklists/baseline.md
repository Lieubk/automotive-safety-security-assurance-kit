# Baseline review checklist

Version 1. Applies to: `baseline`, `communication-record`. Supports: SUP.8.BP5,
SUP.8.BP6, SUP.8.BP7, SUP.8.BP8, SWE.1.BP8, SWE.2.BP9, SWE.3.BP7, SWE.4.BP7.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

What is checked before a baseline is created, after it is anchored, when it is audited
and when it is communicated. `/baseline` applies it. The configuration management plan
itself is reviewed with `.claude/docs/checklists/plan.md`. "The plan" below is the
approved plan of kind `configuration-management`. For a baseline with an internal
purpose only BSL-04 and BSL-10 to BSL-12 apply before, and BSL-20 to BSL-22 after.

## Before the record is created

| ID | Check | How to check | Kind |
|---|---|---|---|
| BSL-01 | An approved configuration management plan exists | `check`: no `COV-27` finding that names kind configuration-management | script |
| BSL-02 | The trace check reports no error | `check`: the summary line shows `0 errors` | script |
| BSL-03 | Every earlier baseline is communicated | `check`: no `COV-26` finding | script |
| BSL-04 | The purpose is one the plan defines and is written exactly as there; a purpose treated as internal is listed under `trace.internal_baselines` | compare the purpose with the plan and with `project.yaml` | semantic |
| BSL-05 | The baseline is due: what the plan demands for this purpose is the case | compare `status` with the plan | semantic |
| BSL-06 | Nothing the purpose is about will be left out: no item that the plan wants in this baseline is unapproved | `list --status draft` and `list --status in-review`; compare the items printed with what the plan demands for the purpose | semantic |
| BSL-07 | Where items are left out, the user knows which, and the role the plan names accepts it | ask who accepts | accountable |
| BSL-08 | No change request is open | `list --type change-request`: every line shows `closed` or `rejected` | script |
| BSL-09 | Where BSL-08 fails, the role the plan names accepts each open change request as a known open point, and it will be named in the baseline notice | read the open change requests; ask who accepts | accountable |
| BSL-10 | The baseline is taken on the branch the plan names | `git status --short --branch`: the first line names that branch | script |
| BSL-11 | The working tree is clean: nothing modified, staged or untracked | `git status --short --branch`: no line after the first | script |
| BSL-12 | The tag follows the pattern of the plan and is not in use | `git tag --list <tag>` prints nothing; Grep `^tag:` in `records/baselines/` shows no record with it | script |
| BSL-13 | For a release candidate or delivery: the latest verification runs belong to the state that is frozen | `check`: no `COV-30` finding, neither on a unit or test case nor as a warning on a run | script |
| BSL-14 | The person the plan makes responsible wants this baseline now, and knows that every listed item is changed or retired afterwards only through a change request | ask who asked for the baseline | accountable |

## After record, commit and tag

| ID | Check | How to check | Kind |
|---|---|---|---|
| BSL-20 | The record is well-formed and carries the tag and purpose that were asked for | `check`: no `SCHEMA`, `FORMAT` or `LINK` finding on the record; read `tag` and `purpose` | script |
| BSL-21 | The commit that holds the record adds the record and nothing else | `git log -1 --stat --format=%s <tag>` names one file, the record | script |
| BSL-22 | The tag points to that commit and the working tree is clean again | `git log -1 --format=%H <tag>` and `git log -1 --format=%H` print the same commit; `git status --short --branch` | script |
| BSL-23 | Commit and tag are where the audience can fetch them | ask whether both were pushed | accountable |

## Audit

| ID | Check | How to check | Kind |
|---|---|---|---|
| BSL-30 | The tag exists, and the audit runs on its content | `git tag --list <tag>` prints the tag; `git log -1 --format=%H <tag>` is the commit of the folder the audit runs on | script |
| BSL-31 | Every listed item exists at the tag with the listed hash and state, and no approved item at the tag is unlisted | `audit <baseline ID>` on the content of the tag: `0 differences`, exit code 0 | script |
| BSL-32 | The trace check at the tag reports no error other than `COV-26` for this baseline | `check` on the content of the tag | script |
| BSL-34 | The person the plan makes responsible confirms the audit result, keeps the output where the plan says, and decides what happens on a difference | ask who confirms and where the output is kept | accountable |

## Communication

| ID | Check | How to check | Kind |
|---|---|---|---|
| BSL-40 | A final communication record names the baseline | `check`: no `COV-26` finding on the baseline | script |
| BSL-41 | The audience is the one the plan names for this purpose, given as roles or parties, and no party that builds on the content is missing | compare `audience` with the plan and with who uses the items | semantic |
| BSL-42 | The record says how the audience was informed and on which day | read `channel` and `sent_at` | semantic |
| BSL-43 | What was sent lets the audience understand what they received: content, items left out, changes since the previous baseline, known open points | read the notice that was sent | semantic |
| BSL-44 | For verification results: the summary lets a reader judge the consequences (what passed, what failed, coverage against target, open findings, what was not verified) | read the summary; compare with the run records named as subject | semantic |
| BSL-45 | Each communicate practice in scope has a record whose subject and audience fit it: requirements (SWE.1.BP8), architecture (SWE.2.BP9), detailed design (SWE.3.BP7), unit verification results (SWE.4.BP7) | read `subject` and `audience` of the records | semantic |
| BSL-46 | The communication took place as recorded | ask who informed whom, and when | accountable |
| BSL-47 | An agreement in the record was really reached, by the parties named | ask who agreed to what | accountable |
