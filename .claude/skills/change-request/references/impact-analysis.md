# Impact analysis

The analysis answers four questions for the people who decide: what has to change, what
has to be looked at again although it does not change, what the change costs and risks,
and how everyone will know that it is done. The trace graph gives candidates. Whether a
candidate is affected is decided by reading it.

## What the two commands give

`python tools/traceability.py impact <ID>` lists every item that depends on the item,
nearest first. For SWR-0004 of the power window example it begins

```
1  CMP-0004   software-component           AntiPinch - anti-pinch detection  (fulfils SWR-0004)
1  UNT-0003   software-unit                AntiPinch - obstacle detection state machine  (implements SWR-0004)
2  CDS-0002   component-design             Detailed design of AntiPinch  (refines CMP-0004)
2  UT-0013    unit-test                    AntiPinch - settling time and start of monitoring  (verifies UNT-0003)
```

and ends with `17 items depend on SWR-0004`. The number is the distance in links. The
bracket names the link and the item through which the line was reached. A change request
that already affects the item, and a query about it, appear here too.

`python tools/traceability.py show <ID>` lists the links of one item in both directions:

```
SWR-0004  software-requirement  [approved]  Obstacle detection during closing  hash ac44902f7e17
  derived_from  -> SYR-0001  Limitation of the closing force
  derived_from  -> SYE-0001  Window control software
  fulfils       <- CMP-0004  AntiPinch - anti-pinch detection
  implements    <- UNT-0003  AntiPinch - obstacle detection state machine
```

How to read them:

- `impact` follows every link that points to the item, and then every link that points
  to those items, to the end. 44 items is more than half of the example: the component
  that fulfils the requirement brings its design, its interfaces, the views that show
  it, the components that use those interfaces, and their units and tests.
- The list is therefore not the list of affected items. Distance 1 is what has to be
  read. An item at distance 2 or more is reached through an item before it and follows
  only if that item really changes.
- Items that share a value or a term without a link between them are in neither
  output. Only a text search finds those.
- Code and test code are not items. They hang on the items: `source_files` of a
  `software-unit`, `script` of a test case.

## Procedure

1. Start set: the items the request names. For a new version of an imported input,
   take the changed, added and removed input items from the comparison that
   `/import-inputs` produces.
2. For every item of the start set run `impact <ID>` and read the items at distance 1,
   each beside the changed text. Sort every one:
   - **changes**: its text, attributes or links will be different;
   - **reviewed again without change**: it links to something that changes, so its
     review is no longer valid for the new version, but its own text stays;
   - **not affected**: say in one line why not.
3. Go on to distance 2 only behind the items that change, then to distance 3 behind
   those that change at distance 2, and so on. Behind an item that does not change the
   walk ends: what hangs on it is not affected through it. `show <ID>` on an item that
   changes lists what hangs on it directly.
4. Search for what the links cannot know. Grep the value, the name or the term that
   changes (a limit, a signal name, a state name) in the item folders and in the source
   and test folders. Read every hit that the walk has not covered, and sort it too.
   When in doubt it is a question for the owner of the item, not a guess.
5. Code and tests: for each unit that changes, the files under `source_files` and what
   changes in them; for each test case, the function under `script`. Changed code is
   reviewed afterwards (a review recorded with the code revision), and the test and
   analysis runs of the unit are repeated.
6. Other change requests: an open request on one of the same items is a dependency.
   Say which one has to come first, or that they have to be decided together.
7. Safety and security: name the highest `asil` among the items that change and whether
   one is `security_relevant`. If a `design-decision` that documents an ASIL
   decomposition concerns one of them, it is a candidate too. Whether a safety analysis
   has to be repeated is a question for the person responsible for functional safety;
   put it to the user, do not answer it.
8. Regression scope: which test cases are run again and which analysis is repeated.
   Take the rule from the approved plan of the level (for unit level, the regression
   rule of the unit verification strategy), and name the test cases by ID.
9. Confirmation criteria: how everyone will see that the change is implemented. Each
   criterion names a record or a command output: an item approved against the new
   version, a test case passed in a run on the changed state, no `SUSPECT` line.
10. Effort, schedule, risk: ask the user or the owners of the affected items. A figure
    you derive is a proposal and is written as one, with what it rests on.

The sorting can be checked against the tools later: once the first item has changed,
`python tools/traceability.py check` reports `SUSPECT` on the approved items of the
project that link to it. An item that the analysis called "not affected" and that
turns up there was sorted wrongly.

## What to look at, by item type

| Candidate | Read | Typical consequence |
|---|---|---|
| imported input | the old and the new text side by side | every item derived from it is at least reviewed again |
| `software-requirement` | `Statement`, `Verification criteria`, `Analysis`; values that other requirements repeat | the element that fulfils it and the units that implement it are at least reviewed again; the qualification tests that verify it follow |
| `software-component`, `software-interface` | `Responsibility`; `elements` and `operations` with ranges, units, timing; the `fulfils` links | an interface change reaches every component under `used_by` |
| `architecture-view` | whether the diagram or the table shows what changes | execution model and resource summary when timing or memory changes |
| `design-decision` | whether its criteria or its context still hold | a decision whose basis is gone is taken again, not edited |
| `component-design`, `software-unit` | constants, state machines, function contracts, `resource_budget`, the evaluation with its risks | the unit tests of every function whose contract changes; a new function needs a test that names it |
| `unit-test` and other test cases | steps and expected results that use the changed value or behaviour | new boundary values; a test case is corrected through review, never weakened |
| `plan` | whether a rule of the plan is touched (a coverage target, a regression rule, a baseline criterion) | the plan itself becomes an affected item |

## Worked example

Request: the closing force limit of SYR-0001 is to apply from a window opening of more
than 4 mm instead of more than 5 mm (new version of the customer's system requirements).

- `impact SYR-0001` ends with `39 items depend on SYR-0001`. At distance 1 it names
  SWR-0003 and SWR-0004 (derived from it) and the system elements SYE-0001 and SYE-0002
  (they fulfil it). Reading: SWR-0004 carries the limit and changes. SWR-0003 says
  nothing about the zone. The two system elements are inputs, unchanged in version 2.2.
- Behind SWR-0004 at the next distance: CMP-0004 (fulfils it) and UNT-0003 (implements
  it). CMP-0004 names the protected zone without a value; UNT-0003 holds the limit as a
  constant and changes.
- Behind UNT-0003: its eight unit test cases. UT-0016 uses the boundary values of the
  limit and changes; the other seven do not use it.
- Nothing behind SWR-0003, the system elements and CMP-0004 is followed: they do not
  change. That ends the walk after 14 of the 50 items.
- A search for "5 mm" and for `ANTIPINCH_ZONE_LIMIT` adds three places no link leads
  to from SYR-0001: SWR-0008 (automatic closing ends at an opening of 5 mm or less),
  a risk in CDS-0001 that speaks of "the 5 mm zone limit", and the constant in
  `src/antipinch/AntiPinch.h`.

| Result | Items | Reason |
|---|---|---|
| change | SYR-0001; SWR-0004; UNT-0003; UT-0016; CDS-0001 | new version of the input; the limit in statement and criterion 4; the constant in `Behavior`; the boundary values 10 and 11 counts; the risk text that quotes the limit |
| reviewed again, no change | SWR-0003; CMP-0004; UT-0013 to UT-0015, UT-0017 to UT-0020 | derived from SYR-0001 but silent on the zone; fulfils SWR-0004 but names no value; verify UNT-0003 without using the limit |
| not affected | SYE-0001, SYE-0002; everything behind SWR-0003 and CMP-0004 | inputs that version 2.2 leaves as they are; reached only through items that do not change |
| question to the requester | SWR-0008 | derived from SYR-0003, not from SYR-0001: does the end of automatic closing follow the new limit? If so, the reused component CMP-0002 is affected and the request grows |

The search found one of the five items that change, and the open question. Without it
the analysis would have been complete by the links and still wrong.
