---
name: release
description: "Release a product from a baseline and deliver it (Automotive SPICE SPL.2, ISO 26262-2 release for production, ISO/SAE 21434 release for post-development): the release plan with content, classification, numbering, build, support and delivery; per release the checks that the baseline, the documents and the safety and cybersecurity cases are in place, the approval by a named person, the release record with its release note, and the delivery with the receipt. Use when a release is to be delivered to a customer, when SPL.2 is in scope and no approved plan of kind release exists (COV-27), or when the trace check reports COV-74."
argument-hint: "['plan', a release name, or nothing for the releases and their delivery]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python tools/traceability.py *), Bash(python tools/record.py next-id *), Bash(python tools/record.py release *), Bash(python tools/record.py communication *), Bash(python tools/document.py *), Bash(git tag *), Bash(git log *), Bash(git status *)
---

# Product release (SPL.2; ISO 26262-2:6; ISO/SAE 21434 6.4.9)

Turns a baseline into a delivered release: what it contains, who approved it, what was
handed over, and that the customer received it. A `release` record holds one release,
written by `record.py release` from the baseline and the state of the project; a
communication record holds its delivery and the receipt.

| Base practice | What this skill does | Evidence it leaves |
|---|---|---|
| SPL.2.BP1 to BP4, BP6 to BP8 | drafts the release plan: what goes into which release, classification and numbering, build and its environment, support, media and packaging | plan of kind `release` |
| SPL.2.BP5 Build the release from configured items | names the baseline and the build record the release comes from; refuses a baseline that changed | `baseline`, `build` of the release record |
| SPL.2.BP9, BP12 Release documentation and release note | generates the documents of the baseline with `/documents`; the release note is written by who releases | `Release note` of the record; documents built with `--baseline` |
| SPL.2.BP10, BP11 Approval and consistency | records who approved; the tool refuses while the check has errors | `approved_by`, `check` of the record; COV-74 |
| SPL.2.BP13 Deliver the release | records the delivery and the receipt | communication record naming the release, with `agreement`; COV-74 |
| 26262-2:6 release for production | requires the safety case and lists the functional safety assessments | `kinds` with `release-for-production`; `cases` |
| 21434:6.4.9 release for post-development | requires the cybersecurity case and lists the assessments | `kinds` with `release-for-post-development`; `cases` |

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Run `python tools/traceability.py check` and `python tools/traceability.py status`.
   Read `COV-27` for kind `release` (when SPL.2 is in scope) and `COV-74`.
3. No final baseline for the release: name `/baseline` and stop. A release is made from a
   baseline others rely on, never from an internal one.

## Steps

### 1. Release plan (SPL.2 in scope)
- Read `references/release-plan.md`. Ask: which content goes into which release, the
  classification (samples, series) and the numbering scheme, how the release is built and
  in which environment, the support that comes with it, the media and packaging, who
  approves. Draft the plan of kind `release`; `/review` approves it.

### 2. Readiness
- The working tree has to be at the baseline's tag (`git tag`, `git status`); checking it
  out is the user's step. Run `check`: the tool refuses a release while it reports errors.
- Release for production (ISO 26262 in scope): the safety case exists
  (`record.py safety-case`, `/safety-plan`), and the functional safety assessment where the
  plan names one. Release for post-development (ISO/SAE 21434 in scope): the cybersecurity
  case, and the assessment where the plan calls for one.
- Documents: generate the ones the customer expects with
  `python tools/document.py build <kind> --baseline <BL-ID>` (`/documents`).

### 3. Approval and record
- Ask who approves the release and when; the release note is written by who releases -
  content, changes since the last release, known limitations, open problems. Write it to
  a file, show it, and on the user's yes run:
  `python tools/record.py release --baseline <BL-ID> --release "<name>" --kind <kind> ...
  --product "name=<name>;version=<v>;file=<file>" --approved-by "<name>" --approved-at <date>
  --delivered-to "<customer>" --note <file>`.

### 4. Delivery
- When the user states that the release was handed over, record it:
  `python tools/record.py communication --subject <REL-ID> --audience "<customer>"
  --channel "<how>" --sent-at <date> --agreement "<who confirmed the receipt, when>"`.
  Without a receipt, leave out `--agreement`; `COV-74` keeps a warning until it is stated.

## Writing

- Show the plan before writing it and ask: "May I write PLN-NNNN in `plans/`?" IDs from
  `python tools/record.py next-id plan`; status `draft`; approval through `/review`.
- A release record is final once written; a corrected release is a new release.

## Checks before you finish

Run `python tools/traceability.py check`.
- `FORMAT`, `SCHEMA`, `LINK` on items written in this session: fix them.
- `COV-27` and `COV-74`: report each with what closes it.

## Hand-over

1. The table with what was done and what is open.
2. The release: baseline, products, approval, open problems, cases, delivery and receipt.
3. Next: `/next-step`; `/problem-resolution` for problems the release note lists.

## Do not

- Do not approve a release or state a receipt in anyone's name.
- Do not release from an internal baseline or from a working tree that differs from it.
- Do not leave known open problems out of the release note.
