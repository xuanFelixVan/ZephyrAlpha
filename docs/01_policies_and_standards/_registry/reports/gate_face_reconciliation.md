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
| generated_at | 2026-10-05T16:13:26+00:00 |
| head_commit | 48df2da55a7b317ad19c63fb34b76f04ae96e9b6 |
| generator | `scripts/governance/generate_gate_face_reconciliation.py` |
| roster | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` |
| roster_entries | 106 |
| roster_declared_total_gates | 106 |
| enabled | 98 |
| disabled | 8 |
| loaded_in_process | 98 |
| load_aggregate_error | none |
| trigger_conditional | 24 |
| trigger_always_run | 74 |
| red_count | 74 |

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
| CAPABILITY-OVERLAP | enabled=true | 1 | —（空） | 0 | no |
| DIRECTORY-CONTRACT | enabled=true | 1 | —（空） | 0 | no |
| TTL-METADATA | enabled=false | 0 | —（空） | 0 | no |
| FILE-PLACEMENT-TTL | enabled=false | 0 | —（空） | 0 | no |
| CREATE-GUARD | enabled=true | 1 | —（空） | 0 | no |
| RULE-EXECUTION-PAIRING | enabled=true | 1 | `docs/01_policies_and_standards/rules/`(87), `rule_`(320) | 403 | no |
| REFERENCE-INTEGRITY | enabled=true | 1 | `docs/*.md`(4818), `docs/*.yaml`(4169), `docs/*.json`(2) | 8989 | no |
| RULE-FOUR-WAY-ALIGN | enabled=true | 1 | `docs/01_policies_and_standards/rules/`(87), `rule_`(320) | 403 | no |
| RULING-COMMIT-VERIFIED | enabled=true | 1 | —（空） | 0 | no |
| R5-DIGIT-SUFFIX | enabled=true | 1 | `docs/`(9110), `scripts/`(1393), `src/`(4080), `data/`(1022) | 15024 | no |
| TRANSLATION-COVERAGE | enabled=true | 1 | —（空） | 0 | no |
| TDM-MOUNT-COVERAGE | enabled=true | 1 | —（空） | 0 | no |
| ENCODING-SAFETY | enabled=true | 1 | —（空） | 0 | no |
| SSOT-REDEFINITION | enabled=true | 1 | —（空） | 0 | no |
| UNSAFE-DICT-SPREAD | enabled=true | 1 | `src/*.py`(3807), `scripts/*.py`(1201), `schemas/*.py`(236), `sitecustomize.py`(1) | 5245 | no |
| PURE-SHIM | enabled=true | 1 | —（空） | 0 | no |
| PURE-ASSERTION | enabled=true | 1 | —（空） | 0 | no |
| NOQA-VALIDATION | enabled=true | 1 | —（空） | 0 | no |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | enabled=true | 1 | —（空） | 0 | no |
| DATETIME-NOW-FORBIDDEN | enabled=true | 1 | —（空） | 0 | no |
| GATE-VOCAB | enabled=true | 1 | —（空） | 0 | no |
| SNAPSHOT-DRIFT | enabled=true | 1 | —（空） | 0 | no |
| FILE-COPY | enabled=true | 1 | `src/*.py`(3807), `scripts/*.py`(1201), `schemas/*.py`(236), `sitecustomize.py`(1) | 5245 | no |
| ID-UNIQUENESS | enabled=true | 1 | `.pre-commit-config.yaml`(1) | 1 | no |
| EXEMPT-ZONE-FM | enabled=false | 0 | —（空） | 0 | no |
| MODULE-ID-CONSISTENCY | enabled=false | 0 | —（空） | 0 | no |
| PERMANENT-SYSTEM-TRIGGER | enabled=true | 1 | —（空） | 0 | no |
| MSG-EXPOSURE | enabled=true | 1 | —（空） | 0 | no |
| EMPTY-HANDLER | enabled=true | 1 | —（空） | 0 | no |
| ORPHAN-MODULE | enabled=true | 1 | —（空） | 0 | no |
| DOC-REF-BROKEN | enabled=false | 0 | —（空） | 0 | no |
| FUNCTION-DUP | enabled=true | 1 | `src/*.py`(3807), `scripts/*.py`(1201), `schemas/*.py`(236), `sitecustomize.py`(1) | 5245 | no |
| NO-BARE-GETENV | enabled=true | 1 | —（空） | 0 | no |
| MSG-STYLE | enabled=true | 1 | —（空） | 0 | no |
| NO-UPWARD-IMPORT | enabled=true | 1 | —（空） | 0 | no |
| NO-HARDCODED-URL | enabled=true | 1 | —（空） | 0 | no |
| MAP-ALIGNMENT | enabled=true | 1 | `src/zephyr/governance/depgraph_schema.py`(1), `src/zephyr/governance/persistence/dataflowgraph_schema.py`(1), `src/zephyr/governance/persistence/decisiongraph_schema.py`(1), `scripts/governance/apply_depgraph.py`(1), `scripts/governance/apply_dataflowgraph.py`(1), `scripts/governance/apply_decisiongraph.py`(1), `scripts/governance/generate_project_depgraph.py`(1), `docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml`(1), `scripts/governance/d5_architecture/generators/align_panoramas.py`(1), `docs/03_modules/*.md`(1454), `config/construction_workflow_map.yaml`(1), `config/strategy_card_lifecycle_map.yaml`(1), `scripts/governance/d5_architecture/validators/validate_construction_steps.py`(1), `scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py`(1), `scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py`(1), `scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py`(1), `src/zephyr/gov_enforcement/commit_gates/map_family/construction_workflow_map_gate.py`(0), `src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py`(0), `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md`(1), `docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml`(1), `docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml`(1), `docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`(1), `docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`(1), `config/data_supply_chain_map.yaml`(1), `scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py`(1), `scripts/governance/d5_architecture/validators/validate_data_supply_chain_map.py`(1), `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`(1), `config/trading_day_cycle_map.yaml`(1), `scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py`(1), `scripts/governance/d5_architecture/validators/validate_trading_day_cycle_map.py`(1), `docs/_working/map_build/fig13_daycycle/00_skeleton.md`(1), `config/trading_decision_map.yaml`(1), `src/zephyr/plan_engine/daily_loop_master_switch.py`(1), `src/zephyr/data/trading_calendar.py`(1), `src/zephyr/data/config/resource_profile_registry.yaml`(0), `config/dev_delivery_map.yaml`(1), `scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py`(1), `scripts/governance/d5_architecture/validators/validate_dev_delivery_map.py`(1), `docs/_working/map_build/fig11_delivery/00_skeleton.md`(1), `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`(1), `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`(1), `config/flags.yaml`(1) | 1492 | no |
| NO-BARE-SQL | enabled=true | 1 | —（空） | 0 | no |
| CH-BATCH-SIZE | enabled=true | 1 | —（空） | 0 | no |
| CH-FINAL-GATE | enabled=true | 1 | —（空） | 0 | no |
| CH-VERSION-COL | enabled=true | 1 | `schema`(332), `ddl`(35) | 367 | no |
| COMPLEXITY-GUARD | enabled=true | 1 | `src/*.py`(3807), `scripts/*.py`(1201), `schemas/*.py`(236), `sitecustomize.py`(1) | 5245 | no |
| ALGO-NOTE-SYNC | enabled=true | 1 | —（空） | 0 | no |
| ALGO-FLOW-LINK | enabled=true | 1 | —（空） | 0 | no |
| META-TESTS-COVERAGE | enabled=true | 1 | `src/zephyr/gov_enforcement/commit_gates/`(130) | 130 | no |
| TEST-SOURCE-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| BLUEPRINT-FORMAT | enabled=false | 0 | —（空） | 0 | no |
| GATE-DOMAIN-FK | enabled=true | 1 | `*.py`(6609) | 6609 | no |
| BLUEPRINT-HEADER | enabled=false | 0 | —（空） | 0 | no |
| CAP-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| NO-IMPORT-SIDE-EFFECT | enabled=true | 1 | —（空） | 0 | no |
| DEPGRAPH-FRESHNESS | enabled=true | 1 | `src/`(4080), `scripts/`(1393) | 5473 | no |
| RECONCILER-HEALTH | enabled=true | 1 | —（空） | 0 | no |
| SCRIPTS-IMPORT-INTEGRITY | enabled=false | 0 | `scripts/*.py`(1201) | 1201 | no |
| GIT-CALL-BUDGET | enabled=true | 1 | —（空） | 0 | no |
| BARE-SUBPROCESS | enabled=true | 1 | —（空） | 0 | no |
| UNDEFINED-NAME | enabled=true | 1 | —（空） | 0 | no |
| IMPORT-INTEGRITY | enabled=true | 1 | —（空） | 0 | no |
| CAPABILITY-LOOKUP-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| GATE-PRECOMMIT-OFFLINE | enabled=true | 1 | `.pre-commit-config.yaml`(1) | 1 | no |
| FOLDER-CAPACITY-HARD-LIMIT | enabled=true | 1 | —（空） | 0 | no |
| DEPGRAPH-ENFORCEMENT | enabled=true | 1 | —（空） | 0 | no |
| DERIVATION-ANNOTATION | enabled=true | 1 | —（空） | 0 | no |
| RELATIVE-PATH-LITERAL | enabled=true | 1 | —（空） | 0 | no |
| CONSUMERS-ACCURACY | enabled=true | 1 | `capability_canonical`(1) | 1 | no |
| SCHEMA-FILE-EXISTS | enabled=true | 1 | `schema`(332) | 332 | no |
| ASYNCIO-RUN-IN-CONTEXT | enabled=true | 1 | `src/zephyr/*.py`(3807) | 3807 | no |
| MUTABLE-CONST-WITHOUT-FINAL | enabled=true | 1 | —（空） | 0 | no |
| OPEN-WITHOUT-WITH | enabled=true | 1 | —（空） | 0 | no |
| ZEPHYR-ENV-DIRECT-ACCESS | enabled=true | 1 | —（空） | 0 | no |
| MCP-VERSION-FIELD | enabled=true | 1 | —（空） | 0 | no |
| PROTECTED-PATHS | enabled=true | 1 | —（空） | 0 | no |
| BLUEPRINT-NODE-ID-HARDCODE | enabled=true | 1 | —（空） | 0 | no |
| WORKTREE-REQUIRED | enabled=true | 1 | —（空） | 0 | no |
| TEST-RESIDUE-SSOT | enabled=true | 1 | —（空） | 0 | no |
| SECRET-REGISTRY-CONSISTENCY | enabled=true | 1 | —（空） | 0 | no |
| NO-SECRET-HARDCODE | enabled=true | 1 | —（空） | 0 | no |
| RECONCILER-FILE-OPS | enabled=true | 1 | `src/zephyr/governance/`(339), `src/zephyr/gov_enforcement/`(305), `scripts/governance/`(754), `scripts/backup/`(15) | 1413 | no |
| REGISTRY-CODE-ANCHOR | enabled=true | 1 | —（空） | 0 | no |
| STASH-ACCUMULATION | enabled=true | 1 | —（空） | 0 | no |
| TABLE-NAME-REGISTRY | enabled=true | 1 | —（空） | 0 | no |
| GATE-ERRCODE-CONSISTENCY | enabled=true | 1 | `architecture_model/contracts/`(3) | 3 | no |
| HOT-FILE-BASE-FRESHNESS | enabled=true | 1 | —（空） | 0 | no |
| STATE-VOCAB-REGISTRY | enabled=true | 1 | `src/zephyr/shared/vocab/`(2), `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml`(1), `added:*.py`(0) | 3 | no |
| TAG-VOCAB | enabled=true | 1 | `library`(139), `catalogs/`(87) | 225 | no |
| BLOOD-FLESH | enabled=true | 1 | `src/zephyr/*.py`(3807), `scripts/*.py`(1201), `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`(1) | 5009 | no |
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
| TAKEOVER-PENDING | enabled=true | 1 | —（空） | 0 | no |

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
| CAPABILITY-OVERLAP | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DIRECTORY-CONTRACT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CREATE-GUARD | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| RULING-COMMIT-VERIFIED | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TRANSLATION-COVERAGE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TDM-MOUNT-COVERAGE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ENCODING-SAFETY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SSOT-REDEFINITION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PURE-SHIM | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PURE-ASSERTION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NOQA-VALIDATION | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| DATETIME-NOW-FORBIDDEN | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| GATE-VOCAB | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| SNAPSHOT-DRIFT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| PERMANENT-SYSTEM-TRIGGER | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MSG-EXPOSURE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| EMPTY-HANDLER | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ORPHAN-MODULE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-BARE-GETENV | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| MSG-STYLE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-UPWARD-IMPORT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-HARDCODED-URL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-BARE-SQL | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CH-BATCH-SIZE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CH-FINAL-GATE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ALGO-NOTE-SYNC | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| ALGO-FLOW-LINK | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| TEST-SOURCE-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| CAP-CONSISTENCY | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| NO-IMPORT-SIDE-EFFECT | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| RECONCILER-HEALTH | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| GIT-CALL-BUDGET | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
| BARE-SUBPROCESS | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
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
| NO-SECRET-HARDCODE | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |
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
| TAKEOVER-PENDING | R2-trigger-empty-always-run | files_trigger 空=每链全跑（1A.3 悬案②同款） |

## 声明禁用门（informational，不进红名单）

| gate_id | 进程内实载 |
|---|---|
| TTL-METADATA | 0 |
| FILE-PLACEMENT-TTL | 0 |
| EXEMPT-ZONE-FM | 0 |
| MODULE-ID-CONSISTENCY | 0 |
| DOC-REF-BROKEN | 0 |
| BLUEPRINT-FORMAT | 0 |
| BLUEPRINT-HEADER | 0 |
| SCRIPTS-IMPORT-INTEGRITY | 0 |

> 本表=只读报告件：禁据此改任何门禁 enabled 态（flag 翻转=Owner 门位）；
> 判据真源=docs/_working/total_command_closeout/10_wave_plan.md §1A.3。
