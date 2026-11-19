# SPL.2 Product Release

## Intent
Product release controls how a product version leaves the project and reaches the customer it is meant for. Content is planned, the release is built from controlled items in a defined environment, documented, approved against criteria, delivered, and its receipt is confirmed. The process belongs to the extended VDA scope; no rating-consistency guidance of its own is attached to it.

## Outcomes
1. It is decided what a product release contains.
2. The release is put together from configuration-controlled items.
3. The documentation that goes with a release is specified and written.
4. The way the release is delivered, and on what medium, is decided.
5. The release is approved against defined criteria.
6. The release reaches the intended customer.
7. Receipt of the release is confirmed.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SPL.2.BP1 | Define the functional content of releases | A release plan states which functionality goes into which release. | Release plan mapping features or requirements to releases, including which application parameters take effect in which release | none |
| SPL.2.BP2 | Define release products | What a release consists of is stated. | Release content definition: software, documentation, accompanying tools where stated, sample stage | none |
| SPL.2.BP3 | Establish a product release classification and numbering scheme | Releases are classified and numbered by a scheme that reflects their purpose and what recipients may expect from them. | Versioning scheme description; release identifiers that follow it | none |
| SPL.2.BP4 | Define the build activities and build environment | The build is reproducible: its steps and its environment are specified and maintained. | Build procedure or scripts; build environment definition under configuration control | none |
| SPL.2.BP5 | Build the release from configured items | Only configuration-controlled items go into the build, which safeguards the integrity of the release. | Build log referencing a baseline; build manifest | none |
| SPL.2.BP6 | Communicate the type, service level and duration of support for a release | For each release, the kind of support, its service level and how long it lasts are determined and made known. | Support statement in the release documentation or the agreement | none |
| SPL.2.BP7 | Determine the delivery media type for the release | What the customer needs decides the delivery medium. | Delivery method stated in the release plan or the agreement | none |
| SPL.2.BP8 | Identify the packaging for the release media | Each kind of medium has its packaging defined. | Packaging and protection specification | none |
| SPL.2.BP9 | Define and produce the product release documentation/release notes | All documentation supporting the release is written, reviewed, approved and at hand. | Release documentation set with review and approval status | none |
| SPL.2.BP10 | Ensure product release approval before delivery | The release criteria are met before the release goes out. | Release criteria checklist with results; approval record dated before delivery | none |
| SPL.2.BP11 | Ensure consistency | The software release number agrees with the paper label and, where one exists, the label on the memory device. | Identifier cross-check record | none |
| SPL.2.BP12 | Provide a release note | Information describing the key characteristics of the release accompanies it. | Release note | none |
| SPL.2.BP13 | Deliver the release to the intended customer | Hand-over to the intended customer takes place and receipt is positively confirmed. | Delivery record; acknowledgement of receipt | none |

Interpretation hints:
- Release products may include programming tools; in automotive projects a release is often tied to a sample stage such as A, B or C.
- A numbering scheme may distinguish major release, feature release, defect repair, alpha or beta state and the iteration within alpha or beta.
- All parties should build in the same specified environment.
- Where relevant, flash the software onto the matching hardware revision before the release goes out.
- Delivery may be on an intermediate medium handed to the customer, direct (for example as firmware inside the package), or both; electronic delivery by placing the release on a server is possible, and the release may have to be duplicated first.
- Packaging for some media needs physical or electronic protection, for example encryption.
- A release note may hold an introduction, environment requirements, installation steps, how to start the product, new features, resolved defects, known defects and workarounds.
- Any channel can serve for confirming receipt: in person, electronic, postal, phone or a distribution service.
- The practices of this process lean on SUP.8 Configuration Management.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 08-16 | Release plan | 1, 3 | Planned releases with content, dates, type, recipients and applicable parameter sets. |
| 11-03 | Product release information | 1, 3, 4, 6 | Release note and accompanying information: identification, content, changes, known issues, installation, support. |
| 11-04 | Product release package | 2, 3, 6 | The deliverable set: binaries, parameter files, documentation, manifest with checksums. |
| 11-07 | Temporary solution | 6 | A workaround or interim fix delivered ahead of the regular release, with scope and limits. |
| 13-06 | Delivery record | 6, 7 | What was delivered to whom, when, by which channel, and the confirmation of receipt. |
| 13-13 | Product release approval record | 5 | Evaluation of each release criterion and the approval decision with approver and date. |
| 15-03 | Configuration status report | 2 | The item versions that make up the release baseline and their status. |
| 18-06 | Product release criteria | 5, 7 | The conditions a release must meet before delivery. |

## Dependencies
No rating-consistency relations of its own are recorded for this process.

Seen from SUP.8: SPL.2.BP3 and SUP.8.BP1 are mutually related by recommendation SUP.8.RC.7 (the configuration management strategy reflects the release classification and numbering scheme), and SPL.2.BP13 and SUP.8.BP6 by recommendation SUP.8.RC.8 (baselines support delivery to the customer).

## Automation notes
Assumed set-up: releases are produced by a pipeline from a tag; the release plan, the release criteria and the versioning scheme are data files; the build environment is defined as code (container image or pinned toolchain manifest).

Script (deterministic):
- The release plan assigns every planned feature or requirement ID to a release; for a release candidate, the planned IDs are compared with the IDs whose implementation and verification status is complete in the release baseline.
- The release identifier matches the versioning scheme (regular expression) and is identical in the tag, the version embedded in the binary, the parameter files, the release note and any label file.
- The build runs only from a tag on a protected branch, in the pinned environment; the manifest lists every input with hash; a rebuild reproduces the same output hashes.
- Release criteria as a gate: required tests passed, no open problem above the permitted severity, reviews closed, static analysis within limits, baseline audit passed; the gate result is stored as part of the approval record.
- The release note is assembled from change requests and problems closed since the previous release plus the open known problems; mandatory sections are present.
- The package manifest carries checksums and, where required, a signature or encryption step; the delivery record stores package hash, recipient, channel, timestamp and acknowledgement.

LLM (semantic judgement):
- Rewrite the generated change list into release notes a customer can read, and check that known limitations and workarounds are described honestly and completely.
- Compare the narrative of the release plan with the actual content and point out silent scope changes.

Human (accountability):
- The release approval itself, in particular for safety-related software; commitments on support type, level and duration; obtaining the confirmation of receipt from the customer.
