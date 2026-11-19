# Safety analysis items

Folder `spec/safety/analyses/`, type `safety-analysis`, prefix `SAN`. Values are invented
for the power window example.

## FMEA at software level

```yaml
id: SAN-0001
type: safety-analysis
title: FMEA of the anti-pinch detection
status: draft
method: fmea
level: software
findings:
  - id: F1
    fault: "speed from WindowPos frozen at its last value"
    effect: "AntiPinch sees no slow-down at an obstacle; no reversal; SG-0001 violated"
    measure: "WindowPos marks its speed stale after two missing Hall edges; AntiPinch treats stale as obstacle"
    carried_by: SWR-0006
    state: closed
  - id: F2
    fault: "AntiPinch scheduled late under load"
    effect: "reversal later than the fault tolerant time"
    measure: "execution in the 5 ms task with a budget; load measured on the target"
    carried_by: VIEW-0004
    state: open
links:
  analyses: [CMP-0004, CMP-0003, IFC-0002]
```

Sections: `Scope` - elements, interfaces, the goals or requirements measured against;
`Method` - the guide words per output (no value, wrong value, too late, too early,
stuck) or the fault models; `Results` - the overall picture and what is open.

## Dependent failures analysis

`method: dfa`, `level: software` or `system`. The findings are the dependent failure
initiators found between the elements that must be independent or free from
interference: shared memory, shared execution time, shared resources such as the
communication stack, common development errors, common inputs. Each with the measure:
memory protection, timing supervision, diverse implementation, separate inputs.

## FTA

`method: fta`. The top event is the violation of a safety goal; the findings are the
minimal cut sets or the basic events that matter, each with its measure. The tree itself
is kept as a diagram in `Results` (Mermaid) or as a file the item names.
