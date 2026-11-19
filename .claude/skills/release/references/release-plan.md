# Release plan

File `plans/PLN-NNNN.md`, type `plan`, `kind: release`. The checklist is `plan.md`,
part "Kind release". The values are invented.

## Decisions to ask before drafting

| Decision | Typical options | Lands in |
|---|---|---|
| Which content goes into which release | by milestone of the project plan; by customer order | `Scope` |
| Classification | A-, B-, C-sample, series; engineering release | `Approach` |
| Numbering | `R<major>.<minor>`; the customer's scheme; the tag names of the baselines | `Approach` |
| Build and build environment | the build of the last integration step; the customer builds from sources | `Environment and tools` |
| Release products | sources, binaries, documents, records | `Scope` |
| Support | duration and service level per classification | `Approach` |
| Media and packaging | archive with checksums through the customer's portal | `Environment and tools` |
| Approval and delivery | who approves; how the receipt is confirmed | `Responsibilities`, `Criteria` |

## Template

```markdown
---
id: PLN-0013
type: plan
title: Release plan
status: draft
kind: release
---

## Scope

R1.0 at the delivery milestone: the C sources of the developed units, the component and
interface descriptions, the verification records, the safety case.

## Approach

Classification B-sample until the customer's series release; numbering R<major>.<minor>,
the baseline tag carries the same name. Support: defect corrections for B-samples for six
months.

## Criteria

Released only from a final baseline with no error in the trace check; approved by the
project lead; delivered when the customer confirms the receipt.

## Environment and tools

The build of the last integration step; an archive with checksums through the customer's
supplier portal.

## Responsibilities

Project lead: approval. Configuration manager: release record and delivery.
```
