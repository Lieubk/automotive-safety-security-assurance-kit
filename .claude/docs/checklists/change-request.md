# Change request review checklist

Version 1. Applies to: `change-request`. Supports: SUP.10.BP2, SUP.10.BP3, SUP.10.BP4,
SUP.10.BP5, SUP.10.BP6, SUP.10.BP7, SUP.10.BP8.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

Part A is applied before a change request is put before the deciding body. Part B is
the review of the implementation, applied before the change request is set to
`verified`. `/change-request` applies both and records the review of the
implementation itself; `/review` does not take change requests. The affected items
themselves are reviewed with the checklists of their types. `<ID>` is the ID of the
change request. Where SUP.10 is out of scope, `COV-20` is not active: answer CRQ-02
from `show <ID>`.

In a review record this checklist is cited as `change-request v1`. The record of the
implementation review carries a result for every check of both parts: part A is
answered again on the present text of the change request, and a check that cannot
apply any more or does not apply to this request (CRQ-15 after implementation, CRQ-40
without a problem report) is `not-applicable` with that reason as its note. A check
that waits for an answer nobody can give yet stays `not-assessed`: the change request
then stays `implemented`, and the review is recorded when the answer exists.

## Part A - before the decision

| ID | Check | How to check | Kind |
|---|---|---|---|
| CRQ-01 | Mandatory attributes and sections for its state are present | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| CRQ-02 | It names at least one affected item, and every link target exists | `check`: no `COV-20` and no `LINK` finding on the item; `show <ID>` lists the `affects` lines | script |
| CRQ-03 | Requester, request, reason and source are stated so that someone who was not part of the discussion understands what is wanted and why | read `Description` | semantic |
| CRQ-04 | It is one change: nothing unrelated is bundled into it | read `Description` and the list of affected items | semantic |
| CRQ-05 | A change that comes from a new version of an input names the input and the version; a change caused by a problem links the problem report with `resolves`; a change raised by an answered query names the query under `affects` | read `Description`; `show <ID>` lists the links | semantic |
| CRQ-06 | The candidates were collected from `impact` and `show` for every item the request names, and from a text search for what changes | read `Impact analysis`; run `impact` for the named items and compare | semantic |
| CRQ-07 | Every candidate is sorted - changes, reviewed again without change, not affected - with a reason the text of the item supports | read the candidates beside the analysis | semantic |
| CRQ-08 | Every item said to change is under `affects`, and every item under `affects` is explained in the analysis | compare `show <ID>` with the section | semantic |
| CRQ-09 | The code and test files that change are named | compare with `source_files` and `script` of the affected items | semantic |
| CRQ-10 | Other open change requests on the same items are named, with the order in which they have to be implemented | `impact` of each affected item lists the change requests that affect it; compare with the analysis | semantic |
| CRQ-11 | The highest ASIL and the security relevance of the items that change are stated, and it is said whether the person responsible for functional safety has to be involved | compare with `asil` and `security_relevant` of the items | semantic |
| CRQ-12 | The regression scope names test cases and analyses and follows the regression rule of the plan for that test level | compare with the approved plan | semantic |
| CRQ-13 | Each confirmation criterion can be decided from a record or a command output, and together they cover every item that changes | read the criteria against the list of items | semantic |
| CRQ-14 | Effort, effect on the release schedule and risks are stated, each with what it rests on | read `Impact analysis` | semantic |
| CRQ-15 | No affected item has been changed for this request yet | `audit <baseline ID>` for the baseline that lists them prints no line for an affected item | script |
| CRQ-16 | The owners of the affected items stand behind the analysis and the estimate | ask who was consulted and who estimated | accountable |
| CRQ-17 | Open questions to the requester do not stand in the way of a decision, or the decision is to wait for them | ask the user | accountable |

## Part B - implementation, before closing

| ID | Check | How to check | Kind |
|---|---|---|---|
| CRQ-30 | The decision is recorded with who decided and when, priority and target release | `check`: no `SCHEMA` finding on the change request; read `decision` | semantic |
| CRQ-31 | The decision was taken before the first affected item changed | compare the date in `decision` with the version control history of the affected items | semantic |
| CRQ-32 | Every item under `affects` is approved again or obsolete, and a query under `affects` is closed | `show <ID>` for the list; `check`: no `COV-19` and no `UPSTREAM` finding on any of them; `list --status draft` | script |
| CRQ-33 | No item still refers to an old version of something that changed, and the changed code of every unit was reviewed in a review that names the code revision | `check`: no `SUSPECT` and no `CONSISTENCY` finding on an item named in the analysis | script |
| CRQ-34 | Each item changed as the analysis said | read the changed items against "Items that change" | semantic |
| CRQ-35 | Nothing changed that the request does not name; an item added later was added to the analysis and put before the deciding body | compare the changes made since the decision with `affects` | semantic |
| CRQ-36 | The change went through every level it touches: from the requirement to design, code and test cases, or the analysis says why a level is not touched | follow the chain with `show` from the highest affected item down | semantic |
| CRQ-37 | Every test case of the regression scope has a verdict in a final run on the changed state, and all passed | `check`: no `COV-18` and no `COV-30` finding on the units and test cases concerned; `status` names the latest run; read `results` of that run record | script |
| CRQ-38 | Coverage and static analysis of the changed units still meet the plan, and every new or changed function is named by a unit test | `check`: no `COV-12`, `COV-28` or `COV-29` finding on the units | script |
| CRQ-39 | Each confirmation criterion is met, and the record that shows it is named | go through the criteria one by one | semantic |
| CRQ-40 | A linked problem report: the change removes what the problem report describes | read the problem report beside the changed items | semantic |
| CRQ-41 | Questions to the requester are answered, or carried into a new change request | read the analysis; ask the user | accountable |
| CRQ-42 | At least one reviewer of the implementation did not implement the change | ask who implemented and who reviews | accountable |
