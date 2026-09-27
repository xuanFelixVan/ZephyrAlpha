---
ttl: permanent
doc_type: register
module_id: RPT-GATE-FACE-RECONCILIATION
generated_by: scripts/governance/generate_gate_face_reconciliation.py
regenerate: python scripts/governance/generate_gate_face_reconciliation.py
---

<!-- 机生件（禁手改）：scripts/governance/generate_gate_face_reconciliation.py 产出 | 波 1A.3 触发面三列对账表 | 重算=重跑该生成器 -->
# 门禁触发面三列对账表

| 字段 | 值 |
|---|---|
| generated_at | 2026-09-27T06:15:33+00:00 |
| head_commit | 5306c714c3d97a4a83d981419d6b8722a0b00ad2 |
| generator | `scripts/governance/generate_gate_face_reconciliation.py` |
| roster | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` |
| roster_entries | 104 |
| roster_declared_total_gates | 104 |
| enabled | 100 |
| disabled | 4 |
| loaded_in_process | 100 |
| load_aggregate_error | none |
| trigger_conditional | 29 |
| trigger_always_run | 71 |
| red_count | 71 |

## 三列主表（行=名册每台门；行序=名册物理序）

| gate_id | 名册声明 | 进程内实载 | files_trigger | HEAD 命中文件数 | 死触发 |
|---|---|---|---|---|---|
| HELD-OVERLAP | enabled=true | 1 | —（空） | 0 | no |
| FORGED-GW-MARKER | enabled=true | 1 | —（空） | 0 | no |
| FOREIGN-CHANGE-DETECTION | enabled=true | 1 | —（空） | 0 | no |
| DERIVED-FILE-DELETION-PROTECTION | enabled=true | 1 | —（空） | 0 | no |
| COMMIT-SCOPE | enabled=true | 1 | —（空） | 0 | no |
| SESSION-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| CLAIM-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| CAPABILITY-OVERLAP | enabled=false | 0 | —（空） | 0 | no |
| DIRECTORY-CONTRACT | enabled=true | 1 | —（空） | 0 | no |
| TTL-METADATA | enabled=true | 1 | —（空） | 0 | no |
| FILE-PLACEMENT-TTL | enabled=true | 1 | —（空） | 0 | no |
| CREATE-GUARD | enabled=true | 1 | —（空） | 0 | no |
| RULE-EXECUTION-PAIRING | enabled=true | 1 | `docs/01_policies_and_standards/rules/`(87), `rule_`(377) | 460 | no |
| REFERENCE-INTEGRITY | enabled=true | 1 | `docs/`(8286) | 8286 | no |
| RULE-FOUR-WAY-ALIGN | enabled=true | 1 | `docs/01_policies_and_standards/rules/`(87), `rule_`(377) | 460 | no |
| RULING-COMMIT-VERIFIED | enabled=true | 1 | —（空） | 0 | no |
| R5-DIGIT-SUFFIX | enabled=true | 1 | `docs/`(8286), `scripts/`(1354), `src/`(4033), `data/`(976) | 14101 | no |
| TRANSLATION-COVERAGE | enabled=true | 1 | —（空） | 0 | no |
| ENCODING-SAFETY | enabled=true | 1 | —（空） | 0 | no |
| SSOT-REDEFINITION | enabled=true | 1 | —（空） | 0 | no |
| UNSAFE-DICT-SPREAD | enabled=true | 1 | `.py`(8943) | 8943 | no |
| PURE-SHIM | enabled=true | 1 | —（空） | 0 | no |
| PURE-ASSERTION | enabled=true | 1 | —（空） | 0 | no |
| NOQA-VALIDATION | enabled=true | 1 | —（空） | 0 | no |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | enabled=true | 1 | —（空） | 0 | no |
| DATETIME-NOW-FORBIDDEN | enabled=true | 1 | —（空） | 0 | no |
| GATE-VOCAB | enabled=false | 0 | —（空） | 0 | no |
| SNAPSHOT-DRIFT | enabled=true | 1 | —（空） | 0 | no |
| FILE-COPY | enabled=true | 1 | `.py`(8943) | 8943 | no |
| ID-UNIQUENESS | enabled=true | 1 | `.pre-commit-config.yaml`(1) | 1 | no |
| EXEMPT-ZONE-FM | enabled=true | 1 | —（空） | 0 | no |
| MODULE-ID-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| PERMANENT-SYSTEM-TRIGGER | enabled=false | 0 | —（空） | 0 | no |
| MSG-EXPOSURE | enabled=true | 1 | —（空） | 0 | no |
| EMPTY-HANDLER | enabled=true | 1 | —（空） | 0 | no |
| ORPHAN-MODULE | enabled=true | 1 | —（空） | 0 | no |
| DOC-REF-BROKEN | enabled=true | 1 | —（空） | 0 | no |
| FUNCTION-DUP | enabled=true | 1 | `.py`(8943) | 8943 | no |
| NO-BARE-GETENV | enabled=true | 1 | `.env`(1), `secret`(36), `credential`(6), `token`(16), `password`(0), `api_key`(0), `private_key`(1) | 60 | no |
| MSG-STYLE | enabled=true | 1 | —（空） | 0 | no |
| NO-UPWARD-IMPORT | enabled=true | 1 | —（空） | 0 | no |
| NO-HARDCODED-URL | enabled=true | 1 | —（空） | 0 | no |
| MAP-ALIGNMENT | enabled=true | 1 | `docs/02_enterprise_architecture/`(53), `docs/03_modules/`(4797), `alignment_checklist`(1) | 4851 | no |
| NO-BARE-SQL | enabled=true | 1 | —（空） | 0 | no |
| CH-BATCH-SIZE | enabled=true | 1 | —（空） | 0 | no |
| CH-FINAL-GATE | enabled=true | 1 | —（空） | 0 | no |
| CH-VERSION-COL | enabled=true | 1 | `schema`(345), `ddl`(37) | 382 | no |
| COMPLEXITY-GUARD | enabled=true | 1 | `.py`(8943) | 8943 | no |
| ALGO-NOTE-SYNC | enabled=true | 1 | —（空） | 0 | no |
| ALGO-FLOW-LINK | enabled=false | 0 | —（空） | 0 | no |
| META-TESTS-COVERAGE | enabled=true | 1 | `tests/`(3901) | 3901 | no |
| TEST-SOURCE-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| BLUEPRINT-FORMAT | enabled=true | 1 | —（空） | 0 | no |
| GATE-DOMAIN-FK | enabled=true | 1 | `.py`(8943) | 8943 | no |
| BLUEPRINT-HEADER | enabled=true | 1 | —（空） | 0 | no |
| CAP-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| NO-IMPORT-SIDE-EFFECT | enabled=true | 1 | —（空） | 0 | no |
| DEPGRAPH-FRESHNESS | enabled=true | 1 | `src/`(4033), `scripts/`(1354), `depgraph`(45) | 5414 | no |
| RECONCILER-HEALTH | enabled=true | 1 | `governance`(2543) | 2543 | no |
| SCRIPTS-IMPORT-INTEGRITY | enabled=true | 1 | `scripts/`(1354) | 1354 | no |
| GIT-CALL-BUDGET | enabled=true | 1 | —（空） | 0 | no |
| BARE-SUBPROCESS | enabled=true | 1 | `.env`(1), `secret`(36), `credential`(6), `token`(16), `password`(0), `api_key`(0), `private_key`(1) | 60 | no |
| UNDEFINED-NAME | enabled=true | 1 | —（空） | 0 | no |
| IMPORT-INTEGRITY | enabled=true | 1 | —（空） | 0 | no |
| CAPABILITY-LOOKUP-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| GATE-PRECOMMIT-OFFLINE | enabled=true | 1 | `.pre-commit-config.yaml`(1) | 1 | no |
| FOLDER-CAPACITY-HARD-LIMIT | enabled=true | 1 | —（空） | 0 | no |
| DEPGRAPH-ENFORCEMENT | enabled=true | 1 | —（空） | 0 | no |
| DERIVATION-ANNOTATION | enabled=true | 1 | —（空） | 0 | no |
| RELATIVE-PATH-LITERAL | enabled=true | 1 | —（空） | 0 | no |
| CONSUMERS-ACCURACY | enabled=true | 1 | `capability_canonical`(1) | 1 | no |
| SCHEMA-FILE-EXISTS | enabled=true | 1 | `schema`(345) | 345 | no |
| ASYNCIO-RUN-IN-CONTEXT | enabled=true | 1 | `.py`(8943) | 8943 | no |
| MUTABLE-CONST-WITHOUT-FINAL | enabled=true | 1 | —（空） | 0 | no |
| OPEN-WITHOUT-WITH | enabled=true | 1 | —（空） | 0 | no |
| ZEPHYR-ENV-DIRECT-ACCESS | enabled=true | 1 | —（空） | 0 | no |
| MCP-VERSION-FIELD | enabled=true | 1 | —（空） | 0 | no |
| PROTECTED-PATHS | enabled=true | 1 | —（空） | 0 | no |
| BLUEPRINT-NODE-ID-HARDCODE | enabled=true | 1 | —（空） | 0 | no |
| WORKTREE-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| TEST-RESIDUE-SSOT | enabled=true | 1 | —（空） | 0 | no |
| SECRET-REGISTRY-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| NO-SECRET-HARDCODE | enabled=true | 1 | `.env`(1), `secret`(36), `credential`(6), `token`(16), `password`(0), `api_key`(0), `private_key`(1) | 60 | no |
| RECONCILER-FILE-OPS | enabled=true | 1 | `governance`(2543) | 2543 | no |
| REGISTRY-CODE-ANCHOR | enabled=true | 1 | —（空） | 0 | no |
| STASH-ACCUMULATION | enabled=true | 1 | —（空） | 0 | no |
| TABLE-NAME-REGISTRY | enabled=true | 1 | —（空） | 0 | no |
| GATE-ERRCODE-CONSISTENCY | enabled=true | 1 | `architecture_model/contracts/`(3) | 3 | no |
| HOT-FILE-BASE-FRESHNESS | enabled=true | 1 | —（空） | 0 | no |
| STATE-VOCAB-REGISTRY | enabled=true | 1 | `src/`(4033), `.py`(8943) | 9215 | no |
| TAG-VOCAB | enabled=true | 1 | `library`(119), `catalogs/`(86) | 204 | no |
| BLOOD-FLESH | enabled=true | 1 | `.py`(8943) | 8943 | no |
| FRONTEND-TRUTH-SOURCE | enabled=true | 1 | —（空） | 0 | no |
| BUSINESS-REGISTRY | enabled=true | 1 | —（空） | 0 | no |
| REGISTRY-MASS-DELETION | enabled=true | 1 | —（空） | 0 | no |
| REGISTRY-YAML-PARSE | enabled=true | 1 | —（空） | 0 | no |
| SPLIT-COORDINATION | enabled=true | 1 | —（空） | 0 | no |
| SYNTAX-VALIDATION | enabled=true | 1 | —（空） | 0 | no |
| RESOURCE-SCHEDULE | enabled=true | 1 | `tasks.yaml`(1), `config/`(124) | 124 | no |
| REAL-KEY-REFERENCE-SCAN | enabled=true | 1 | —（空） | 0 | no |
| TASK-ORDER-DOCS-LOCK | enabled=true | 1 | —（空） | 0 | no |
| CONSTITUTION-LINE-LIMIT | enabled=true | 1 | —（空） | 0 | no |
| DOC-HEADER-SUITE | enabled=true | 1 | —（空） | 0 | no |
| FMS-HYGIENE | enabled=true | 1 | —（空） | 0 | no |

## 红名单（判据：声明有实载 0｜触发面空｜死触发命中 0）

| gate_id | 红态 | 说明 |
|---|---|---|
| HELD-OVERLAP | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FORGED-GW-MARKER | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FOREIGN-CHANGE-DETECTION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DERIVED-FILE-DELETION-PROTECTION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| COMMIT-SCOPE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SESSION-REQUIRED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CLAIM-REQUIRED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DIRECTORY-CONTRACT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TTL-METADATA | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FILE-PLACEMENT-TTL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CREATE-GUARD | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| RULING-COMMIT-VERIFIED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TRANSLATION-COVERAGE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ENCODING-SAFETY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SSOT-REDEFINITION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PURE-SHIM | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PURE-ASSERTION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NOQA-VALIDATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DATETIME-NOW-FORBIDDEN | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SNAPSHOT-DRIFT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| EXEMPT-ZONE-FM | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MODULE-ID-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MSG-EXPOSURE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| EMPTY-HANDLER | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ORPHAN-MODULE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DOC-REF-BROKEN | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MSG-STYLE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-UPWARD-IMPORT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-HARDCODED-URL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-BARE-SQL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CH-BATCH-SIZE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CH-FINAL-GATE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ALGO-NOTE-SYNC | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TEST-SOURCE-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| BLUEPRINT-FORMAT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| BLUEPRINT-HEADER | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CAP-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-IMPORT-SIDE-EFFECT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| GIT-CALL-BUDGET | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| UNDEFINED-NAME | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| IMPORT-INTEGRITY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CAPABILITY-LOOKUP-REQUIRED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FOLDER-CAPACITY-HARD-LIMIT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DEPGRAPH-ENFORCEMENT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DERIVATION-ANNOTATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| RELATIVE-PATH-LITERAL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MUTABLE-CONST-WITHOUT-FINAL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| OPEN-WITHOUT-WITH | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ZEPHYR-ENV-DIRECT-ACCESS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MCP-VERSION-FIELD | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PROTECTED-PATHS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| BLUEPRINT-NODE-ID-HARDCODE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| WORKTREE-REQUIRED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TEST-RESIDUE-SSOT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SECRET-REGISTRY-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| REGISTRY-CODE-ANCHOR | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| STASH-ACCUMULATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TABLE-NAME-REGISTRY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| HOT-FILE-BASE-FRESHNESS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FRONTEND-TRUTH-SOURCE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| BUSINESS-REGISTRY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| REGISTRY-MASS-DELETION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| REGISTRY-YAML-PARSE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SPLIT-COORDINATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SYNTAX-VALIDATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| REAL-KEY-REFERENCE-SCAN | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TASK-ORDER-DOCS-LOCK | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CONSTITUTION-LINE-LIMIT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DOC-HEADER-SUITE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| FMS-HYGIENE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |

## 声明禁用门（informational，不进红名单）

| gate_id | 进程内实载 |
|---|---|
| CAPABILITY-OVERLAP | 0 |
| GATE-VOCAB | 0 |
| PERMANENT-SYSTEM-TRIGGER | 0 |
| ALGO-FLOW-LINK | 0 |

> 本表=只读报告件：禁据此改任何门禁 enabled 态（flag 翻转=Owner 门位）；
> 判据真源=docs/_working/total_command_closeout/10_wave_plan.md §1A.3。
