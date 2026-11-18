# Deriving unit test cases from the unit design

A unit test case answers one question: does the unit do what its design says, in this
situation? The situation and the expected answer both come from the `software-unit`
item. The code is what is being judged; it cannot also be the witness.

## What to read in the unit design

| Design element | Read it for | It yields |
|---|---|---|
| `functions[].arguments` with `min`, `max`, `invalid`, `resolution` | the range of every input and the values with a special meaning | equivalence classes and boundary values |
| `functions[].returns` | every return value and what it means | one case or more per return value |
| `functions[].errors` (condition, reaction) | what is refused and what happens then | one error case per entry, in every state the entry names |
| `functions[].preconditions` and `postconditions` | what must hold before, what is promised after | checks in `Expected result`; the start state in `Preconditions` |
| `data[]` with `min`, `max`, `initial` | stored values, their limits and start values | counter limits, saturation, wrap-around, state after initialisation |
| `Behavior` | algorithm, constants, states and transitions | normal cases, thresholds, cycle counts, one case per transition |
| `Error handling` | detection and reaction for every error | error cases, and what must stay unchanged |
| `Dynamic behavior` | contexts, protection, timing | what a test double can observe (an exclusive area entered and left), and what the host cannot show |
| `links.uses` | the services and units the unit calls | the test doubles needed, and the failures to inject |
| `links.implements` | the requirements the unit fulfils directly | a cross-check: the values in their `Verification criteria` must agree with the design |

If design and requirement disagree on a value, stop: that is a finding for
`/sw-detailed-design`, not a choice the test author makes.

## Techniques

Use them in this order for every designed function of category `public`, `scheduled` or
`callback`; `check` reports `COV-29` for each such function that no test case names in
`verifies`, as a pending warning while the unit has no code and as an error afterwards.
`local` functions are tested through the functions that call them.

1. **Normal behaviour.** For each thing the function is designed to do, one case with
   typical values. Every postcondition is checked at least once.
2. **Equivalence classes.** Split each input into ranges in which the design treats all
   values alike, including the ranges it refuses. One representative per class is
   enough inside a class; the boundaries are handled next.
3. **Boundary values.** At every limit the design names, test the last value on each
   side: the largest accepted and the smallest refused, the cycle before a time limit
   and the cycle at it, a counter at its maximum and the next event. Include the ends of
   the data type where arithmetic can wrap (an unsigned difference across the wrap of a
   timer, a counter that must saturate).
4. **Error returns and invalid inputs.** One case per `errors` entry: null pointer,
   value out of range, enumeration value that does not exist. Check the return value,
   the reaction, and that everything the design calls "unchanged" is unchanged.
5. **States and transitions.** Reach every state; take every transition in the design
   once at least; at every guard show both outcomes (taken, not taken). Also apply every
   input class in every state: what does an invalid argument do in each of them?
6. **Behaviour over several calls.** Filters, debounce counters, timeouts and
   confirmation counts need sequences: run the number of cycles and check at the cycle
   before the change and at the cycle of the change. Interrupt a sequence and check
   that it starts again.
7. **Injected failure of called services** (units with an ASIL, or as the strategy
   says). For each service the unit calls: let the test double return its error value.
   Check the designed reaction, that the unit's data is unchanged where the design says
   so, and that the unit recovers when the service works again.
8. **Experience.** Add cases for faults that are typical for this kind of code: off by
   one at a cycle count, values left over after a new initialisation, the same event
   twice, the order of two conditions that become true in the same call. Each such case
   still names its design basis. If there is none, the design has a gap.

One item holds one test idea, not one check: steps that share a set-up and a purpose
belong together, as "limits of the speed drop and of its confirmation" does. A case that
needs three unrelated set-ups is three cases.

## Where the expected result comes from

- From a value or formula in the design, worked out by hand and written as a number:
  "reference speed 129", not "reference speed as computed".
- For a calculation that rounds, work the example out: 500000 / 3334 is 149.97; the
  design says "rounded down", so the expected value is 149.
- Never from running the code and writing down what it returned. A test built that way
  passes by construction and fails only when the code changes.
- If the design does not determine the result, ask instead of deciding. Typical gaps:
  the reaction to an invalid value in one particular state, the result at exactly the
  limit ("more than" or "at least"?), the order of two checks.

Where the question goes depends on who owns the design:

- A unit the project designs: the question is listed for the designer in the hand-over
  and answered by a change of the unit item through `/sw-detailed-design`.
- A unit that is an imported input: the question is a `query` item, so that it stays
  visible until it is answered. File `records/queries/<ID>.md`, attributes `to` (the
  source of the input, by role) and `asked_at`, status `open`, `links.about` with the
  unit ID, and a section `Question` that quotes the design text and says what is
  missing. Ask the user before writing it; never edit the imported unit.

## Worked example: `AntiPinch_Step` of UNT-0003

**Inputs and their classes**, from `arguments` and `Error handling`:

| Argument | Classes | Boundaries |
|---|---|---|
| `position` | 0 to 10 counts: below the zone limit; 11 to 960: protected; 961 to 65534: out of range; 65535: not referenced, legal | 10 / 11; 960 / 961; 65534 / 65535 |
| `speed_mm_s` | 0 to 500: valid; above 500: out of range | 500 / 501 |
| `motion` | 0 stopped, 1 opening, 2 closing; above 2: out of range | 2 / 3; a value far outside (255) |

**States and transitions**, from the state diagram in `Behavior`: IDLE, SETTLING,
MONITORING and REVERSING, and the nine transitions between them.

**Limits inside the behaviour**: 20 settling cycles; a drop is more than 20 mm/s below
the reference; 2 drop cycles in a row confirm; the reference speed is at least 50 mm/s;
a reversal ends 240 counts further open, at 960 at most, or in cycle 400.

**Derivation table.** Each row is one design statement with the technique that turns it
into a case. The last column names the test case of the example that resulted.

| Design statement | Technique | Values chosen | Case |
|---|---|---|---|
| IDLE to SETTLING on closing; SETTLING to MONITORING in closing cycle 20; back to IDLE when not closing | transitions; boundary of the cycle count; both classes of "not closing" | 19 and 20 cycles; stopped and opening; settling interrupted and restarted | UT-0013 |
| A speed more than 20 mm/s below the reference in 2 cycles in a row gives REVERSING | normal behaviour | reference 150, speed 129 twice; standstill (speed 0) | UT-0014 |
| "more than 20", "2 in a row" | boundary values, both sides | drop of exactly 20 for 40 cycles: never; drop of 21 for single cycles: never; two in a row: obstacle | UT-0015 |
| Detection only above 10 counts; 65535 counts as above | boundary values; the special value | 10, 11, a drop that continues from 11 to 10, 65535 | UT-0016 |
| Reference at least 50 mm/s; low-pass follows a slow change | boundary; behaviour over several calls | closing at 30: reference 50; 29 is a drop; ramp from 150 to 100 without an obstacle | UT-0017 |
| Reversal ends at detection position + 240, limited to 960 | boundary values | 839 / 840 after detection at 600; 959 / 960 after detection at 800 | UT-0018 |
| Reversal ends in cycle 400 | boundary values; no target and target not reached | 399 / 400 cycles with position 65535; the same with a window that does not move | UT-0019 |
| Argument out of range: reaction per state; null pointer at the read function | error returns in every state; boundaries of each range | 961, 65534, 501, 3 refused; 960, 65535, 500, 0 accepted; refused cycles count towards the 400 | UT-0020 |

**What the table shows is missing.** `Behavior` says that entering IDLE clears the
counters. No row leaves MONITORING while a drop cycle is counted, so nothing would notice
a half-confirmed drop that survives a stop and makes the next closing movement reverse
one cycle early. That is one more case: the transition MONITORING to IDLE with a pending
drop, then the first drop cycle of the next movement. It is the item shown in
`test-case-template.md`. The example reaches full statement and branch coverage without
this case: coverage did not find the gap, the design did.

**What is not a test case.** `Error handling` names a state variable outside 0 to 3. No
call through the interface of the unit can produce it, and a test that writes the
file-scope variable would test the implementation. The statement is covered by the code
review, and by structural coverage showing whether code for it exists that no test
reaches (see "Coverage and deviations" in `running-and-recording.md`).

**Injected failures.** `AntiPinch_Step` calls no service, so technique 7 has nothing to
inject, and the test cases say "no stubs". `WindowPos_Step` of UNT-0002 calls the capture
service of UNT-0001; its `errors` entry "does not return E_OK" becomes UT-0011, where the
test double returns `E_NOT_OK` and position, speed and pending pulses must be unchanged.

## Showing the derivation to the user

Before writing, show one table per unit: design statement, technique, values, proposed
test case title, functions for `verifies`. List separately:

- design statements for which no case is proposed, each with the reason (not reachable
  through the interface, shown by review, left to another level by the strategy);
- open questions: places where the design does not determine the expected result.

## Signs that a case was derived from the code

- The expected value has more digits or another rounding than the design gives.
- The steps follow the branches of the implementation rather than the statements of the
  design, or name `local` functions as the thing tested.
- The case exists "for coverage" and has no design basis.
- The design is silent on the situation, yet the case has an expected result and no
  question was raised.
- Only the paths that work are tested, with the values the developer tried.

Each of these is a finding in the self-check and in the review.
