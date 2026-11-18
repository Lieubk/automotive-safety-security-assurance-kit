# SUP.8 Configuration Management

## Intent
Configuration management protects the integrity of everything a process or project produces and gets the right versions to the people who need them. It rests on a strategy, a set of identified configuration items, controlled change, baselines that are complete and consistent, status reporting and safe storage. The process belongs to the VDA scope and has rating-consistency guidance.

## Outcomes
1. A configuration management strategy exists.
2. Every configuration item produced by a process or project is identified, defined and baselined as the strategy prescribes.
3. Changes to configuration items and their releases are under control.
4. Changes and releases reach the parties who need them.
5. The status of configuration items and of changes to them is recorded and reported.
6. Baselines are complete and consistent.
7. Storage of configuration items is under control.

## Base practices
| BP | Official short name | What must be true | Typical evidence | Rating rule IDs |
|---|---|---|---|---|
| SUP.8.BP1 | Develop a configuration management strategy | A strategy states who is responsible, which tools and repositories are used, access rights, naming rules, what qualifies as a configuration item, when and how baselines are drawn, how branches are created and merged, and how revision history is kept. | Configuration management plan covering these topics; variant handling concept | SAP.RL.1, SAP.RL.2, SAP.RL.3, SAP.RL.4, SUP.8.RL.1, SUP.8.RL.2, SUP.8.RL.3, SUP.8.RL.4, SUP.8.RL.5, SUP.8.RC.1 |
| SUP.8.BP2 | Identify configuration items | Configuration items are identified and documented as the strategy defines. | Configuration item list; repository structure matching the list | APA.RL.4, SUP.8.RL.14, CL2.RC.13 |
| SUP.8.BP3 | Establish a configuration management system | A configuration management system that implements the strategy is in place. | Configured repositories and tools; access control settings; evidence of use | SUP.8.RL.11, SUP.8.RL.12, SUP.8.RL.13, SUP.8.RL.14, CL2.RC.15 |
| SUP.8.BP4 | Establish branch management | Where development runs in parallel from a common base, branching is managed as the strategy defines. | Branch model description; branch and merge history conforming to it; merge verification evidence | SUP.8.RL.9, SUP.8.RL.10, SUP.8.RL.14 |
| SUP.8.BP5 | Control modifications and releases | Control mechanisms defined by the strategy exist and are used to govern changes to configuration items and their release. | Check-in history linked to change requests; protected branches; release tags with approval | SUP.8.RL.14, SUP.8.RC.3, CL2.RC.15 |
| SUP.8.BP6 | Establish baselines | Baselines for internal use and for delivery outside the project are created as the strategy defines. | Baseline tags or labels with content lists; baseline records | SUP.8.RL.6, SUP.8.RL.7, SUP.8.RL.8, SUP.8.RC.2, SUP.8.RL.14, CL2.RC.15 |
| SUP.8.BP7 | Report configuration status | The status of configuration items is recorded and reported so that project management and other processes can rely on it. | Configuration status reports | SUP.8.RC.3 |
| SUP.8.BP8 | Verify the information about configured items | It is verified that the information held on configured items and baselines is complete, and that baselines are consistent. | Baseline audit records; configuration audit records | SUP.8.RL.6, SUP.8.RL.7, SUP.8.RL.8, SUP.8.RC.2, SUP.8.RL.9, SUP.8.RL.10, SUP.8.RC.3, SUP.8.RC.4, CL2.RC.18 |
| SUP.8.BP9 | Manage the storage of configuration items and baselines | Storage, long-term archiving and backup of the configuration management systems are scheduled and resourced so that items and baselines stay intact and available. | Backup and archiving concept; backup logs; restore test records | SUP.8.RL.11, SUP.8.RL.12, SUP.8.RL.13, SUP.8.RC.3, SUP.8.RC.5, SUP.8.RC.6 |

Interpretation hints:
- The strategy normally also covers product or software variants, for instance those that arise from different sets of application parameters.
- A branch strategy states when branching is allowed, whether it needs authorization, how merging is done, and which checks prove that all changes were integrated consistently and nothing else was damaged.
- Items typically placed under control: customer deliverables, chosen internal work products, bought-in products, tooling, and anything else needed to create or describe them.
- Baseline questions connect to SPL.2 Product Release.
- Regular status figures (how many items are in work, checked in, tested, released) help project management and phases such as software integration.
- Baseline audits and configuration management audits are the usual way to implement BP8.
- Backup, storage and archiving may have to outlast the guaranteed life of the storage media; contracts may define the required availability.

## Output work products
| WP ID | Official name | Outcomes | What it should contain (own words) |
|---|---|---|---|
| 06-02 | Handling and storage guide | 3, 4, 5, 7 | How items are stored, handled, backed up, archived and retrieved. |
| 08-04 | Configuration management plan | 1, 2, 7 | The strategy topics of BP1 plus item identification and storage arrangements. |
| 08-14 | Recovery plan | 1, 7 | How configuration data and systems are restored after loss: steps, responsibilities, test interval. |
| 13-08 | Baseline | 2, 3, 4, 5, 6 | A named, immutable set of item versions with purpose, date and approval. |
| 13-10 | Configuration management record | 2, 5, 7 | Status and history of configuration items; audit and backup records. |
| 14-01 | Change history | 3 | Per item: what changed, why, by whom, when and in which version. |
| 16-03 | Configuration management system | 1, 3, 4 | The repositories and tools with their configuration (access, branches, hooks). |

## Dependencies
Rating-consistency relations from the VDA guideline. `A -> B` means the rating of A depends on B; `<->` marks a relation that applies in both directions. Only IDs are recorded here.

| From | To | Kind | ID | Relation |
|---|---|---|---|---|
| SUP.8.BP2 | SUP.8.BP1 | rule | SUP.8.RL.14 | Item identification follows the strategy. |
| SUP.8.BP3 | SUP.8.BP1 | rule | SUP.8.RL.14 | The system follows the strategy. |
| SUP.8.BP4 | SUP.8.BP1 | rule | SUP.8.RL.14 | Branch management follows the strategy. |
| SUP.8.BP5 | SUP.8.BP1 | rule | SUP.8.RL.14 | Change and release control follows the strategy. |
| SUP.8.BP6 | SUP.8.BP1 | rule | SUP.8.RL.14 | Baselining follows the strategy. |
| SUP.8.BP5 | SUP.8.BP2 | recommendation | SUP.8.RC.3 | Control is exercised for the identified items. |
| SUP.8.BP7 | SUP.8.BP2 | recommendation | SUP.8.RC.3 | Status is reported for the identified items. |
| SUP.8.BP8 | SUP.8.BP2 | recommendation | SUP.8.RC.3 | Information is verified for the identified items. |
| SUP.8.BP9 | SUP.8.BP2 | recommendation | SUP.8.RC.3 | Storage is managed for the identified items. |
| SUP.8.BP8 | SUP.8.BP6 | recommendation | SUP.8.RC.4 | Verification uses the established baselines. |
| SUP.8.BP9 | SUP.8.BP3 | recommendation | SUP.8.RC.5 | Storage is managed for the configuration management system. |
| SUP.8.BP9 | SUP.8.BP6 | recommendation | SUP.8.RC.6 | Storage management uses the established baselines. |
| SUP.8.BP1 | SPL.2.BP3 | recommendation (<->) | SUP.8.RC.7 | The strategy reflects the release classification and numbering scheme. |
| SUP.8.BP6 | SPL.2.BP13 | recommendation (<->) | SUP.8.RC.8 | Baselines support delivery to the customer. |
| SUP.8.BP7 | MAN.3.BP10 | recommendation (<->) | SUP.8.RC.9 | Configuration status reporting supports project progress reporting. |

Seen from other processes: SUP.1.BP2 and SUP.8.BP8 are mutually related by recommendation SUP.1.RC.9.

## Automation notes
Assumed set-up: all configuration items are files in git repositories (or referenced by pinned version if they live elsewhere, such as tools and acquired components); the strategy is a text file; baselines are annotated tags accompanied by a manifest.

Script (deterministic):
- The strategy file has a non-empty section for each required topic (responsibilities, tools and repositories, item criteria, naming, access rights, baseline criteria, branching and merging, revision history, variants, storage).
- Configuration item list versus repository content in both directions: every listed item exists, no deliverable file is unlisted, generated artefacts are not committed unless listed.
- Naming rules as regular expressions for files, branches and tags; violations fail the pipeline.
- Repository settings match the strategy: protected branches, mandatory review, no force push, access groups as defined.
- Branch policy from history: changes reach integration branches only through reviewed merges, merges are followed by a passing pipeline, branches older than a limit are reported.
- Baseline creation: annotated (preferably signed) tag plus a manifest listing every item with commit hash or version, including external tool versions and pinned dependencies.
- Baseline audit: every item in the manifest exists at the tag with matching hash, each has the required status and review record, trace links resolve inside the baseline, and the build from the tag reproduces the delivered binaries.
- Status report: number of items per state, changes since the previous baseline, open change requests per item.
- Storage: freshness of backup logs and date of the last successful restore test.

LLM (semantic judgement):
- Compare the written strategy with observed practice (branch names, tag pattern, who merges) and report mismatches in plain language.
- Summarize the difference between two baselines into a readable change overview linked to change requests.
- Judge whether an unlisted file is a configuration item under the stated criteria.

Human (accountability):
- Approving baselines, granting access rights, deciding exceptions to branch policy.
- Backup and archiving infrastructure, retention periods and contractual availability; sign-off of configuration audits.
