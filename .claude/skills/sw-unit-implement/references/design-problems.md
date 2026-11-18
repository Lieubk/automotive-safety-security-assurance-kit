# When implementing shows that the design is wrong or incomplete

Writing code is the hardest test a unit design gets, and it regularly finds something.
What happens next decides whether design and code still describe the same unit
afterwards. The rule: the problem goes back to the design through its owner. It is
never patched silently in code, and the approved item is never edited to match what
was coded.

## Recognise it

| Kind | Sign while coding | Power window example |
|---|---|---|
| Gap | you would have to choose something that changes a result, an error reaction, a stored value or a signature | `Behavior` says the reference speed follows the speed "through a low-pass filter" and gives neither the filter constant nor the rounding |
| Contradiction | two places of the design, or design and interface, or design and requirement, cannot both hold | `returns` lists `E_NOT_OK` for a null pointer, `Error handling` has no such row; the range of `position` in the unit differs from IFC-0002 |
| Error | implemented as written, the unit would do something the requirement or common sense rules out | the drop condition written as `reference - speed > 20` goes below zero for an unsigned type when the speed is above the reference |
| Not implementable | the design asks for what language, platform or budget does not give | a division the 5 ms budget cannot hold; an exclusive area service the supplied basic software does not provide |
| Missing element | the code needs a function another unit must call, a variable, a file or a platform resource the design does not name | a second header for types shared with another unit |
| Limit broken | the function as designed cannot stay inside the complexity, nesting or parameter limit of the design evaluation | - |

Not a design problem, and decided by the developer: local variable names, the order of
independent statements, how a condition is written, splitting a designed function into
file-local helpers that add no behaviour.

If you are unsure which side a point is on, treat it as a design problem and ask. A
question costs minutes; a silent assumption is found in the code review at best, and
on the vehicle at worst.

## What to do

1. **Stop** work on the affected function or variable. Do not write the body "for
   now", do not leave a `TODO`, do not implement the variant you think is meant.
   Functions the problem does not touch may be completed.
2. **State the problem** so that the owner can decide without reading the code:
   - the design element: `UNT-0003#AntiPinch_Step`, or the section and row;
   - what the design says, quoted, and what is missing or in conflict, with the other
     item where there is one (IFC-0002, SWR-0004);
   - why it matters: which result, error reaction or signature depends on it;
   - the options you see, each with its consequence for behaviour, tests and other
     units. A recommendation is welcome; a decision is not yours.
3. **Ask the user** who owns the design of this unit and how the problem reaches them.
   Tell the user in the same message which functions wait for the answer.
4. **The owner changes the design**, with `/sw-detailed-design`. That sets the item
   back to `draft`; its approval and everything built on it becomes stale, and
   `python tools/traceability.py impact <UNT-ID>` lists the unit tests and units that
   depend on it. An item inside a baseline whose purpose is not internal changes only
   through an approved change request (`/change-request`); the write hook refuses the
   edit otherwise.
5. **The changed design is reviewed** (`/review`). Only then does this skill continue,
   from the new approved item: read it again, do not continue from the conversation.
6. **Report** every raised problem in the hand-over, with its state: open, decided,
   design changed and approved.

Where the project is responsible for problem resolution (SUP.9 in `scope.processes`)
and the design was already baselined or delivered, the problem is also recorded as a
`problem-report`; ask the user whether that applies.

## While the answer is open

- Code that does not depend on the answer is written, compared and built as usual.
- The affected function is not written at all, or the files are not handed over as
  complete. A unit with an open design problem is reported as incomplete; the check
  will still show `COV-22` for a designed function without a definition, and that
  finding is left standing because it is true.
- Never bridge the time with an assumption in code. If the user explicitly asks for a
  preliminary implementation to keep others working, write it only after they have
  named who accepted the assumption, mark the place with the problem as it was
  stated, and list it in the hand-over as not conforming to an approved design.

## What never happens

- The code quietly does something the design does not say, "because it is obviously
  meant".
- A public function, a global variable or a file appears that the design does not name.
- What a `software-unit` or `component-design` item says is edited by this skill: not
  a signature, not a constant, not a typo. Every such change is the owner's step. The
  only entry this skill makes is `source_files`, the list of the files it wrote.
- The status of an item is set back to `approved` after a "small" change.
- A reviewer's finding against the code is closed by changing the design to fit.

## When the design changes under existing code

The reverse case: the unit item was changed and approved again, and the code still
follows the old version. The check shows it as `COV-22` when a function was added,
renamed or removed or when parameter or return types changed, and not at all when a
constant, a range, a reaction or a variable changed. Therefore:

1. Read the new item completely and compare it with the code element by element
   (`from-design-to-code.md`, "Comparison"); do not rely on the description of the
   change alone.
2. Change the code to the new design.
3. Say in the hand-over that earlier test runs, analysis runs and the code review of
   the unit describe the old code and have to be repeated. The check says the same:
   `COV-30` for the runs, `SUSPECT` for the review, until `/sw-unit-verify` and
   `/review` have covered the new code.
