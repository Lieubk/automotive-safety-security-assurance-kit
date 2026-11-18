# Impact analysis

The analysis answers four questions for the people who decide: what has to change, what
has to be looked at again although it does not change, what the change costs and risks,
and how everyone will know that it is done. The trace graph gives candidates. Whether a
candidate is affected is decided by reading it.

## What the two commands give

`python tools/traceability.py impact <ID>` lists every item that depends on the item,
nearest first. For SWR-0004 of the power window example:

```
1  UNT-0003   software-unit                AntiPinch - obstacle detection state machine  (implements SWR-0004)
2  UT-0013    unit-test                    AntiPinch - settling time and start of monitoring  (verifies UNT-0003)
...
2  UT-0020    unit-test                    AntiPinch - arguments out of range, and null pointer  (verifies UNT-0003)
9 items depend on SWR-0004
```

The number is the distance in links. The bracket names the link and the item through
which the line was reached. A change request that already affects the item appears here
too, with `affects`.

`python tools/traceability.py show <ID>` lists the links of one item in both directions:

```
SWR-0004  software-requirement  [approved]  Obstacle detection during closing  hash f6938033aa97
  derived_from  -> SYR-0001  Limitation of the closing force
  derived_from  -> SYE-0001  Window control software
  allocated_to  -> CMP-0004  AntiPinch - anti-pinch detection
  implements    <- UNT-0003  AntiPinch - obstacle detection state machine
```

How to read them:

- `impact` follows the links that point to the item. Distance 1 is what has to be read
  first. What lies further away is reached through those items and follows only if they
  really change.
- The allocation of a requirement can be stated on either side. With `allocated_to` on
  the requirement, as above, the component is a `->` target in `show` and is not in the
  `impact` list. With `fulfils` on the component, the component is at distance 1 and
  brings everything that hangs on it: its design, its units, its interfaces, the views
  that show it, their tests. Most of these are candidates that reading rules out.
  Either way the component is a candidate when a requirement allocated to it changes.
- Items that share a value or a term without a link between them are in neither
  output. Only a text search finds those.
- Code and test code are not items. They hang on the items: `source_files` of a
  `software-unit`, `script` of a test case.

## Procedure

1. Start set: the items the request names. For a new version of an imported input,
   take the changed, added and removed input items from the comparison that
   `/import-inputs` produces.
2. For every item of the start set run `impact <ID>` and `show <ID>`. The lines at
   distance 1 and the `->` targets of `show` are the first candidates. For a component
   or interface among them, run `show` on it as well: it names the design that refines
   it, its units, and the views that show it.
3. Search for what the links cannot know. Grep the value, the name or the term that
   changes (a limit, a signal name, a state name) in the item folders and in the source
   and test folders. Every hit outside the candidates is a new candidate.
4. Read each candidate by ID, the changed text beside it, and sort it:
   - **changes**: its text, attributes or links will be different;
   - **reviewed again without change**: it links to something that changes, so its
     review is no longer valid for the new version, but its own text stays;
   - **not affected**: say in one line why not.
   For every candidate that changes, its own dependents (the next distance in `impact`)
   become candidates. For one that does not, they are not affected through it. When in
   doubt it is a question for the owner of the item, not a guess.
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

`python tools/traceability.py matrix` is not needed for this; `impact` and `show` give
the same links per item.

## What to look at, by item type

| Candidate | Read | Typical consequence |
|---|---|---|
| imported input | the old and the new text side by side | every item derived from it is at least reviewed again |
| `software-requirement` | `Statement`, `Verification criteria`, `Analysis`; values that other requirements repeat | criteria change with the statement; the qualification tests that verify it follow |
| `software-component`, `software-interface` | `Responsibility`; `elements` and `operations` with ranges, units, timing; the `fulfils` links | an interface change reaches every component under `used_by` |
| `architecture-view` | whether the diagram or the table shows what changes | execution model and resource summary when timing or memory changes |
| `design-decision` | whether its criteria or its context still hold | a decision whose basis is gone is taken again, not edited |
| `component-design`, `software-unit` | constants, state machines, function contracts, `resource_budget`, the evaluation with its risks | the unit tests of every function whose contract changes; a new function needs a test that names it |
| `unit-test` and other test cases | steps and expected results that use the changed value or behaviour | new boundary values; a test case is corrected through review, never weakened |
| `plan` | whether a rule of the plan is touched (a coverage target, a regression rule, a baseline criterion) | the plan itself becomes an affected item |

## Worked example

Request: the closing force limit of SYR-0001 is to apply from a window opening of more
than 4 mm instead of more than 5 mm (new version of the customer's system requirements).

- `impact SYR-0001` lists 19 items: SWR-0003 and SWR-0004 at distance 1, then the units
  UNT-0002 and UNT-0003 that implement them, then all 15 unit test cases of these units.
- `show SWR-0004` adds CMP-0004 (allocation target). `show CMP-0004` adds CDS-0002, the
  interface it provides and the five views that show the component.
- A search for "5 mm" and for `ANTIPINCH_ZONE_LIMIT` adds three places no link leads
  to from SYR-0001: SWR-0008 (automatic closing ends at an opening of 5 mm or less),
  a risk in CDS-0001 that speaks of "the 5 mm zone limit", and the constant in
  `src/antipinch/AntiPinch.h`.

Reading sorts them:

| Result | Items | Reason |
|---|---|---|
| change | SYR-0001; SWR-0004; UNT-0003; UT-0016; CDS-0001 | new version of the input; the limit in statement and criterion 4; the constant in `Behavior`; the boundary values 10 and 11 counts; the risk text that quotes the limit |
| reviewed again, no change | SWR-0003; UT-0013 to UT-0015, UT-0017 to UT-0020 | derived from SYR-0001 but silent on the zone; verify UNT-0003 without using the limit |
| not affected | CMP-0004, CDS-0002; IFC-0003, VIEW-0001 to VIEW-0005; UNT-0002, UT-0006 to UT-0012 | name the protected zone without a value; carry neither the zone nor its limit; reached only through SWR-0003, which does not change |
| question to the requester | SWR-0008 | derived from SYR-0003, not from SYR-0001: does the end of automatic closing follow the new limit? If so, the reused component CMP-0002 is affected and the request grows |

The search found one of the five items that change, and the open question. Without it
the analysis would have been complete by the links and still wrong.
