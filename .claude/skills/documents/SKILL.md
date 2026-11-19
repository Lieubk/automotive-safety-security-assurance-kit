---
name: documents
description: "Generate the documents a customer, an assessor or a reviewer expects - software requirements specification, software architecture description (SAD), software detailed design (SDD), TARA report - as HTML or Word, from the items of the project, in a neutral style or in the customer's Word template, for the working state or for a baseline. Use before a delivery or a milestone, when a review is held with people who do not read the item files, or when someone asks for a document of the project."
argument-hint: "[document kind, 'list', or nothing to see what can be generated]"
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(python tools/document.py *), Bash(python tools/traceability.py *), Bash(git status *), Bash(git log *), Bash(git tag *)
---

# Documents from the items

Turns the items of the project into the documents that people outside the repository
read. The items stay the source: a document is generated, never edited, and generated
again after the items change. Each document says where it comes from - commit, changes
not committed, baseline, the items with their states and content hashes - and is
marked DRAFT when it shows items that are not approved or comes from uncommitted
changes.

| Document | Built from | Typical use |
|---|---|---|
| `software-requirements-specification` | software requirements, their upstream and allocation | agreement of requirements with the customer (the agreement itself is a communication record, not the document) |
| `software-architecture-description` | views, components, interfaces, design decisions, allocation | the SAD of SWE.2, design freeze |
| `software-detailed-design` | component designs, software units, detailed design decisions | the SDD of SWE.3 |
| `tara-report` | item definition, the plan's method, assets, damage and threat scenarios, goals, claims | the TARA of ISO/SAE 21434 for the customer |

`python tools/document.py list` shows the kinds of `schema/documents.yaml` and how many
items of each type the project has.

## Before you start

1. No `project.yaml`: stop. "This project has no scope yet. Run `/aspice-start` first."
2. Run `python tools/traceability.py check` and `python tools/document.py list`. Errors of
   the check concern the content of a document: say which before generating it.

## Steps

### 1. What, for whom, in which state
- Ask which document, who reads it, and in which state:
  - for a delivery or a milestone: a baseline. The document shows only the items of the
    baseline and is refused when one of them changed since; the working tree has to be
    at the baseline's tag (`git tag`, `git log`). Checking out the tag is the user's step.
  - for a review or a discussion: the working state, approved items only, or with
    `--include-drafts` the items in work too, marked DRAFT.
- Ask for the format: HTML (one file, opens anywhere; Mermaid diagrams are drawn when
  the reader is online, otherwise their source shows) or Word.

### 2. Template
- Ask whether the customer gave a Word template (.docx or .dotx). If not, say that a
  neutral style is used and suggest asking the customer for theirs: cover page,
  headers and footers, styles. Read `references/templates.md` for what a template needs.
- A template the customer gave is kept in the project, for example under `templates/`,
  and named with `--template`; `/aspice-start` records it as `documents.template` in
  `project.yaml` so that every document uses it.

### 3. Generate
- Run `python tools/document.py build <kind> --format html|docx [--baseline BL-ID]
  [--template <file>] [--include-drafts]`. The file goes to `build/documents/` unless
  `--out` names another place. Quote the line the tool prints, with its DRAFT reasons.
- DOCX needs the package python-docx. If the tool says it is missing, report that the
  Word version is NOT ASSESSED and offer the HTML version.

### 4. Hand over
- Name the file, the commit or baseline and the number of items. A document for a
  delivery travels with the baseline: `/baseline` records its communication, naming the
  baseline the document was generated from.
- Comments of readers on a document come back as review findings, queries or change
  requests on the items, never as edits of the document.

## Checks before you finish

- The tool printed `wrote ...` for every document asked for; quote each line.
- A document marked DRAFT is not handed over as released. Say why it is a draft.

## Hand-over

1. The documents written: kind, format, file, commit or baseline, items, DRAFT or not.
2. Findings of the check that concern their content.
3. Next: `/review` for items that kept a document a draft; `/baseline` for a delivery.

## Do not

- Do not edit a generated document to correct its content; correct the items.
- Do not hand over a document generated from uncommitted changes or with items that are
  not approved as if it were released.
- Do not put a customer's template, logo or document numbers into the toolkit itself;
  they belong to the project that received them.
