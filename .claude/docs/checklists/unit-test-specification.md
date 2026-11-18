# Unit test specification review checklist

Version 1. Applies to: `unit-test`, and the test code its `script` names. Supports:
SWE.4.BP2, SWE.4.BP4, SWE.4.BP5, SWE.4.BP6.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

Review the test cases with the unit design open beside them, not with the code. The
code is opened for the part on test code only, and then next to the item, to see
whether the test function does what the item says.

Test cases are written from the design and may be reviewed before the unit has code.
Apply the parts that have something to look at:

- "Each test case" and "The set of test cases of a unit": always.
- "The test code behind a test case": once the test functions exist. An automated case
  needs `script` before approval, so a review that approves includes this part.
- "The results of a unit": once a test run and an analysis run of the unit's code are
  recorded.

Name the parts that were not applied in the review; their checks are not recorded as
passed. For a unit without code `check` prints `COV-12`, `COV-28` and `COV-29` as
warnings ending in "(pending: the unit has no code yet)". Pending means that the rule
applies as soon as the code exists; nothing is wrong yet. One pending line still is a
finding against the test cases: `COV-29`, a designed function that no test case names.

## Each test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| UT-01 | Mandatory attributes and sections for its state are present, values are allowed | `check`: no `SCHEMA` or `FORMAT` finding on the item | script |
| UT-02 | It verifies at least one unit that is still valid, and every `#<function>` anchor names a function the unit designs | `check`: no `COV-17` finding and no `LINK` finding about `verifies` on the item | script |
| UT-03 | `verifies` names every function whose behaviour the case checks, and no function that is only used to set up or to read back | read `Steps` and `Expected result` against the links | semantic |
| UT-04 | `asil` is not lower than the ASIL of any unit verified | `check`: no `COV-23` finding on the item | script |
| UT-05 | The design basis is named: unit, section or function contract, and the requirement criterion where one fixes a value | read the text before the first heading | semantic |
| UT-06 | Every expected value is found in the design or can be calculated from it; none is there only because the code returns it | read the item beside the unit design; recalculate one value per case | semantic |
| UT-07 | Where the design does not determine the result, a query to the designer exists instead of an expected value | ask the author for the queries; read the hand-over of the authoring session | semantic |
| UT-08 | `Preconditions` give the test program, the test doubles, the start state and every term the steps use; the case does not rely on another case having run | read the section | semantic |
| UT-09 | `Steps` are numbered and concrete: calls, values, units, number of cycles | read the section | semantic |
| UT-10 | `Expected result` has an entry for every step and is exact: a value, a state, a return value; no "works", "correct", "as expected" | read both sections side by side | semantic |
| UT-11 | A boundary case names the values on both sides of the limit, and the limit is the one the design states ("more than" against "at least") | compare with the constant or range in the design | semantic |
| UT-12 | An error case checks the return value, the designed reaction, and that what the design calls unchanged is unchanged | compare with `errors` of the function and `Error handling` | semantic |
| UT-13 | The case has one purpose that its title states; steps that do not serve it are absent | read title and steps | semantic |
| UT-14 | `environment` and `regression` agree with the strategy; a case left out of the regression set has a reason | compare with the unit verification plan | semantic |

## The set of test cases of a unit

| ID | Check | How to check | Kind |
|---|---|---|---|
| UT-20 | Every function of category `public`, `scheduled` or `callback` is named by an anchor of at least one test case | `check`: no `COV-29` finding on the unit, pending or not | script |
| UT-21 | For every such function: its normal behaviour, each return value and each `errors` entry has a case | walk the function contract against the cases | semantic |
| UT-22 | Every argument and every stored value with a range is tested at its limits, on both sides | walk `arguments` and `data` against the cases | semantic |
| UT-23 | Every state is reached and every transition of the design is taken; guards are shown with both outcomes | walk the state diagram against the cases | semantic |
| UT-24 | Counters, filters and time limits are tested at the cycle before the change and at the cycle of the change | walk the constants of `Behavior` against the cases | semantic |
| UT-25 | For a unit with an ASIL: the failure of every called service is injected, or the strategy says why not | walk the `uses` links and the strategy | semantic |
| UT-26 | Design statements without a test case are listed with a reason (not reachable through the interface, shown by review, left to another level) | read the derivation table of the authoring session | semantic |
| UT-27 | No case lacks a design basis, and no two cases check the same thing | read the set | semantic |
| UT-28 | The test cases were compared with the current, approved unit design | `check`: no `SUSPECT` on the test cases and no `COV-19` on the unit; `hash --upstream <IDs>` lists the design versions | script |
| UT-29 | What the host cannot show for this unit (timing, stack, behaviour of the target compiler) is named in the strategy and assigned to another level | read `Scope` of the unit verification plan | semantic |
| UT-30 | The test cases were derived from the design and not from the finished code | ask the author how the expected results were obtained | accountable |
| UT-31 | The reviewer did not write the test cases or the unit, and is as independent as the strategy requires for the unit's ASIL | ask who wrote and who reviews; compare with `Responsibilities` of the plan | accountable |

## The test code behind a test case

| ID | Check | How to check | Kind |
|---|---|---|---|
| UT-40 | `script` is set, and the file and the function it names exist | `check`: no `SCHEMA` finding about `script` and no `LINK` finding "script names ..." on the item | script |
| UT-41 | The function does what the item says, step by step: same calls, same values, same order | read function and item side by side | semantic |
| UT-42 | Every entry of `Expected result` is asserted; no check is commented out, widened to a range the item does not give, or placed where it cannot fail | read the function; count the checks against the entries | semantic |
| UT-43 | Expected values in the code are the literals of the item, not results of a copy of the unit's calculation | read the function | semantic |
| UT-44 | The function sets up its own start state and its verdict does not depend on the order of the cases | read the start of the function and the reset of the test doubles | semantic |
| UT-45 | The unit is reached only through its designed functions: no access to file-scope data, no test-only code or switch in the unit's sources | read the test file; search the unit's sources for test switches | semantic |
| UT-46 | Test doubles return prepared values and count calls; they contain no logic of the unit under test or of the unit they replace, and their signatures are those of the designed services | read the test doubles beside the interface or unit they stand for | semantic |
| UT-47 | The test program reports one verdict per case, and a failed check cannot end in a pass (no check after an unconditional return, no verdict printed by hand) | read `main` and the use of the assertion macros | semantic |
| UT-48 | Stand-in headers for the platform define only what the unit uses and agree with the platform's definitions | read the stand-ins beside the interface items | semantic |

## The results of a unit

| ID | Check | How to check | Kind |
|---|---|---|---|
| UT-60 | Test cases and test functions correspond one to one: no function without an item, no approved item without a result | `python tools/record.py test-run` writes a record only then; otherwise it names the test case | script |
| UT-61 | Every test case has a verdict in the latest final unit run, a `not-run` or `blocked` verdict carries a reason, and no test file has changed since that run | `check`: no `COV-18` and no `COV-30` finding on the test cases | script |
| UT-62 | The unit has an entry in the latest static analysis run | `check`: no `COV-12` finding on the unit | script |
| UT-63 | Structural coverage of the unit reaches the target for its ASIL in every metric that has one, or the coverage entry carries a deviation | `check`: no `COV-28` finding on the unit | script |
| UT-64 | A coverage deviation names the code, the reason and who accepted it; the reason holds against the design, and the code is not simply untested | read `deviation` in the `coverage` entry of the latest unit run and the design statement it cites | semantic |
| UT-65 | The code the latest runs covered is the present code | `check`: no `COV-30` finding on the unit | script |
| UT-66 | That code was reviewed against the unit design, in a review recorded with the code revision | `check`: no `SUSPECT` and no `CONSISTENCY` finding about source files on the unit | script |
| UT-67 | Coverage deviations, and analysis findings that are open or recorded as justified, were accepted by the person the strategy names | read `deviation` and `deviations` in the latest runs; ask who accepted them, and when | accountable |
