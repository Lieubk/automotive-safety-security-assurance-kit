# Customer software requirements review checklist

Version 1. Applies to: `software-requirement`. Extends: software-requirements v2.
Supports: SWE.1.BP1, SWE.1.BP7.

A checklist of the project, not of the toolkit. In the worked example the customer of
the door module asks its software suppliers for three checks on top of their own when
software requirements are reviewed (invented for the example). The project keeps them
here. Its quality assurance plan (PLN-0007) takes "the review checklist of the type"
as the criteria of a review; for software requirements that is now this checklist.

A review of software requirements in this project cites `customer-software-requirements
v1`. It applies the checks of the toolkit's `software-requirements` v2 and the checks
below, and `tools/record.py review` asks for a result for each of them. The toolkit's
checklist can no longer be cited on its own here.

Kinds: `script` - a tool answers it; `semantic` - needs reading and judgement, a model
may propose and a person confirms; `accountable` - only a person can state it.

## Customer additions

| ID | Check | How to check | Kind |
|---|---|---|---|
| CSR-01 | Every time value is stated in milliseconds, with a tolerance | read `Statement` and `Verification criteria` | semantic |
| CSR-02 | A requirement with an `asil` other than QM states what the software does when an input it depends on is invalid or missing, or names the requirement that does | read the statement and the related requirements | semantic |
| CSR-03 | A requirement that asks for less than the system requirement it refines has been agreed with the customer | ask the project lead; the note names who at the customer agreed and when | accountable |
