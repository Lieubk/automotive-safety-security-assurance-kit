# What the toolkit cannot evidence for SUP.8

`python tools/traceability.py practices SUP.8` prints one row per base practice. For the
power window example, before any baseline exists:

```
practice    state                  evidence  settled errors warnings  name
SUP.8.BP1   evidence present              1        1      0        0  Develop a configuration management strategy
SUP.8.BP2   no evidence structure         0        0      0        0  Identify configuration items
SUP.8.BP3   no evidence structure         0        0      0        0  Establish a configuration management system
SUP.8.BP4   no evidence structure         0        0      0        0  Establish branch management
SUP.8.BP5   no evidence structure         0        0      0        0  Control modifications and releases
SUP.8.BP6   no evidence yet               0        0      0        0  Establish baselines
SUP.8.BP7   no evidence yet               0        0      0        0  Report configuration status
SUP.8.BP8   no evidence structure         0        0      0        0  Verify the information about configured items
SUP.8.BP9   no evidence structure         0        0      0        0  Manage the storage of configuration items and baselines
```

`no evidence structure` means: the schema has no item type, link or rule for the
practice, so the toolkit cannot tell whether it is performed. It is not a finding and
not a pass. A person shows the practice with evidence the toolkit does not hold. The
skill names that evidence, asks whether it exists, and reports the answer as the
user's statement.

## Practice by practice

| Practice | What the toolkit contributes | What it cannot show | What a person provides |
|---|---|---|---|
| SUP.8.BP2 Identify configuration items | every item is a file with an ID that is never reused, in the folder of its type; with SWE.3 in scope every source file must belong to a unit (COV-11); a baseline record lists the approved items | whether everything that should be controlled is on the list: test code, scripts, tool configuration, compilers, deliveries from others | the list of configuration items in the `Scope` of the plan, kept up to date; for what lives outside the repository, the pinned version and where it is kept |
| SUP.8.BP3 Establish a configuration management system | works on a Git repository; inside a session the write hook refuses changes to accepted imported inputs, to final records and to the items a baseline protects | how the repository is set up; changes made outside a session (they only show up later, as a stale approval in the trace check) | the repository settings: who has which access, protection of the main branch, mandatory review of merges, no rewriting of history, who may set tags |
| SUP.8.BP4 Establish branch management | checks the branch once, when a baseline is taken | whether branches are created, named, merged and checked as the plan says | the branch and merge history, merge requests with their reviewer and their check results, exceptions with who allowed them |
| SUP.8.BP5 Control modifications and releases | change requests with `affects` links; the write hook for baselined items; stale approvals, suspect links and code changed after its runs (`COV-30`) in the trace check; no baseline while errors exist; commit and tag only on the user's word | that every commit touching a baselined item belongs to an approved change request; who released a delivery | commit messages or merge requests that name the change request; the release decision for each delivery with who took it |
| SUP.8.BP8 Verify the information about configured items | `python tools/traceability.py audit <baseline ID>` on the content of the tag: every listed item with its hash and state, and approved items the record does not list; the trace check at the tag | that an audit took place: the command prints an observation and writes no record; that the delivered binaries can be rebuilt from the tag; whether the rules of the plan are followed | the output of the audit with date, commit and the name of who ran and confirmed it, kept where the plan says, or a review record on the baseline record that cites `baseline v1`; a build from the tag where binaries are delivered; configuration audits by quality assurance |
| SUP.8.BP9 Manage the storage of configuration items and baselines | nothing. A clone holds the history but is not a backup concept | everything about storage | where the repository is hosted and who operates it; backup schedule and logs; a restore that was actually tried; the archive of delivery baselines with the tools needed to reproduce them; the retention period from the contract |

## The practices that do have a structure

| Practice | What the row means | What it does not mean |
|---|---|---|
| SUP.8.BP1 | an approved plan of kind `configuration-management` exists | that the plan is followed |
| SUP.8.BP6 | baseline records exist and are final | that they were taken when the plan says, or audited |
| SUP.8.BP7 | the same baseline records exist: each lists the approved items with hash and status | that status is reported between baselines. Regular reporting is a routine of the people involved; `status`, `list` and `check` give the content at any commit, `audit` what has changed since a baseline |

## Work products

Of the output work products of SUP.8 the toolkit yields 08-04 (the plan) and 13-08 (the
baseline record with its tag). Change history (14-01) is the version control history
together with the change requests. The toolkit holds nothing for 06-02, 08-14 and
16-03, and for 13-10 only the status part: handling and storage rules, the recovery
plan, the description of the repository set-up and audit or backup records are provided
by people, usually as part of the plan or next to it.

## How to say it in the hand-over

- Quote the `practices` output, then one line per practice without evidence structure:
  what was asked, what the user answered, what is still missing.
- Do not write "fulfilled" or "not fulfilled". The toolkit prepares evidence and shows
  gaps; an assessment rates.
