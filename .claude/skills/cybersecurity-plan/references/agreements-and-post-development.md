# Interface agreement and post-development plans

All are of type `plan` in `plans/`, reviewed with `plan.md` (the part for their kind).

## Cybersecurity interface agreement (21434:7.4.3)

`kind: cybersecurity-interface-agreement`. One per other party.

```yaml
id: PLN-0010
type: plan
title: Cybersecurity interface agreement with the vehicle manufacturer
status: draft
kind: cybersecurity-interface-agreement
shared_activities:
  - {activity: "9.3 Item definition", customer: R, supplier: S, exchange: "item definition at concept freeze"}
  - {activity: "15 TARA of the door module", customer: A, supplier: R, exchange: "TARA items as ReqIF at each milestone"}
  - {activity: "8.3 Monitoring of the reused components", customer: I, supplier: R,
     exchange: "advisories that affect a delivered version, within 5 working days"}
  - {activity: "13.3 Incident response", customer: R, supplier: S}
```

R performs, A approves, S supports, I is informed, `-` no part. Sections as for every
plan; `Scope` names the parties and the contract, `Approach` how information and
vulnerabilities are exchanged, `Responsibilities` the contacts by role.

The agreement exists when both sides agreed. Record it only when the user states it:

```
python tools/record.py communication --subject PLN-0010 --audience "Vehicle manufacturer" --channel "signed agreement" --agreement "agreed by the customer's cybersecurity manager on 2026-05-12"
```

## Production control plan (21434:12)

`kind: production-control`. `Approach` lists each cybersecurity requirement for
post-development and the production step that puts it in place - keys injected, debug
access locked, the configuration written - and how the step is checked. `Environment and
tools` says how the production equipment and the data it handles are protected.

## Incident response plan (21434:13.3)

`kind: cybersecurity-incident-response`. `Approach`: who is told, how fast, who decides the
remedy, how it is delivered (an update goes through the same processes as development),
when the incident is closed. It refers to the problem resolution strategy for
escalation and to the interface agreement for what the customer does.

## End of cybersecurity support (21434:14.3)

`kind: end-of-cybersecurity-support`. `Approach`: how and when customers learn that
support ends, and what happens to vulnerabilities that are open at that date.
