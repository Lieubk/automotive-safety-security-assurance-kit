# SUP.7 Documentation

## Intent
The documentation process makes sure the recorded information a process produces is planned, written to agreed standards, checked, distributed and kept current. The process belongs to the extended VDA scope; no rating-consistency guidance is attached to it.

## Outcomes
1. A strategy states which documentation is to be produced throughout the product or service life cycle.
2. The standards to follow when writing documentation are identified.
3. The documentation that the process or project has to produce is identified.
4. Content and purpose of every document are specified, reviewed and approved.
5. Documentation is written and made available in line with the identified standards.
6. Documentation is maintained according to defined criteria.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.7.BP1 | Develop a documentation management strategy | A strategy says what gets documented, at which point of the product or service life cycle, and where it is kept. | Documentation plan or strategy | none |
| SUP.7.BP2 | Establish standards for documentation | Standards for writing, changing and maintaining documents are in place. | Templates; structure, style and naming rules | none |
| SUP.7.BP3 | Specify documentation requirements | The attributes a document must carry are specified, for example an identifier, a title, a date, the author, reviewer and approver, a version history, the purpose, a content outline and a distribution list. | Template header or metadata schema | none |
| SUP.7.BP4 | Identify the relevant documentation to be produced | The documents that have to be written are listed for whichever development life cycle is in use. | Document list or work product list per life cycle phase | none |
| SUP.7.BP5 | Develop documentation | Documents are written at the defined process points following the standards and policy, and their content and purpose are reviewed and approved as appropriate. | Documents with review and approval status | none |
| SUP.7.BP6 | Check documentation | A document is reviewed before it is distributed and, where required, authorized before distribution or release. | Review records; authorization records | none |
| SUP.7.BP7 | Distribute documentation | Documents reach all affected parties through the defined channels and media, and delivery is confirmed where that is necessary. | Distribution records; receipt confirmations | none |
| SUP.7.BP8 | Maintain documentation | Documents are kept current as the documentation strategy requires. | Change history; superseded versions marked | none |

Interpretation hints:
- A strategy may define controls such as: approval for adequacy before issue; periodic review, update and renewed approval; marking of changes and of the current revision status; availability of valid versions where they are used; legibility and identifiability; controlled distribution; protection against accidental use of obsolete documents. It may also set confidentiality levels, copyright notices and liability disclaimers.
- Documentation written for users has to be accurate about what the system and its software do and how they are operated, and has to be easy for those users to follow.
- Documentation should itself pass verification or validation.
- Documents that belong to a product baseline, or whose stability matters, are changed and distributed under SUP.8.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-26 | Documentation plan | 1, 2 | Which documents are produced when, by whom, to which standard, and how they are controlled. |
| 13-01 | Acceptance record | 4, 5 | Evidence that a document was accepted or authorized for use. |
| 13-19 | Review record | 4, 5 | Document and version reviewed, reviewers, criteria, findings and their disposition. |
| 14-01 | Change history | 5, 6 | Per document: versions, dates, authors and what changed. |
| 14-11 | Work product list | 3 | The documents and other work products the project has to produce, with owner and status. |

## Dependencies
No rating-consistency relations are recorded for this process.

Related processes by content: documents that need control are handled under SUP.8 (see the hint to BP8).

## Evidence in this toolkit
Documents are generated from the items (`tools/document.py`); the items are the documentation
that is kept and changed, a document is a view of them at a commit or a baseline.

| BP | Carried by | Left to people |
|---|---|---|
| BP1 | the configuration management plan (where and under which control documents are kept) | - |
| BP2, BP3 | none in the project: the item format, the schema and `schema/documents.yaml` of the toolkit, and the customer's template, are the standards and requirements | whether they are the project's |
| BP4 | the project plan: which documents are delivered at which milestone | - |
| BP5 | none as an item: documents are built from approved items, marked DRAFT otherwise | - |
| BP6 | review records of the items a document shows | authorization before release |
| BP7 | communication records with `--practice SUP.7.BP7`; releases with their delivery | - |
| BP8 | change requests, and suspect links after a change | - |

## Automation notes
Assumed set-up: documents are Markdown, reStructuredText or similar text sources with a metadata block, built into deliverable formats by a pipeline; review and approval happen through merge requests; version history comes from the version control system.

Script (deterministic):
- Every document carries the mandatory metadata (identifier, title, status, author, reviewer, approver, version, date, distribution) and the values are well-formed; identifiers are unique.
- Every document on the document list exists, and every document in the repository is on the list.
- Structure follows the template for its type (mandatory headings present, in order); internal links and cross-references resolve; the document set builds without warnings.
- A document with status "released" has a merged review with approval by someone other than the author, and its version matches a tag.
- The change history is generated from commit history, so it cannot diverge from the actual changes.
- Obsolete documents are marked and excluded from the published set; published artefacts correspond to tagged sources.
- Distribution: the release of a document triggers a notification to its distribution list, and the notification is logged.

LLM (semantic judgement):
- Does the content match the stated purpose and outline, and is it understandable for the intended reader, especially for user documentation?
- Does user documentation still describe actual behaviour after a change (compare against requirements and interface definitions)?
- Consistency of terminology across documents.

Human (accountability):
- Approval and authorization, classification of confidentiality, and any legal wording.
