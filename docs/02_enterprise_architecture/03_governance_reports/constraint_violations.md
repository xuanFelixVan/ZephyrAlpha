---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 152 |
| Open（未解决） | 152 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 50 |
| hard | 2 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 2 |
| cross_domain_violation | 34 |
| hard_limit_exceeded | 2 |
| layer_violation | 13 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-1039995 | 孤儿节点: 1039995 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1039995 路径 src/zephyr/governance/kb/pipeline/__init__.py ... |
| V-ORPHAN-1039997 | 孤儿节点: 1039997 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1039997 路径 src/zephyr/governance/kb/sentiment_engine/__in... |
| V-ORPHAN-1039998 | 孤儿节点: 1039998 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1039998 路径 src/zephyr/governance/kb/storage/_backend_prot... |
| V-ORPHAN-1039999 | 孤儿节点: 1039999 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1039999 路径 src/zephyr/governance/kb/storage/unified_memor... |
| V-ORPHAN-1040000 | 孤儿节点: 1040000 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040000 路径 src/zephyr/governance/kb/storage/__init__.py 未... |
| V-ORPHAN-1040001 | 孤儿节点: 1040001 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040001 路径 src/zephyr/governance/kb/supply_chain_graph_en... |
| V-ORPHAN-1040002 | 孤儿节点: 1040002 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040002 路径 src/zephyr/governance/observability_governance... |
| V-ORPHAN-1040004 | 孤儿节点: 1040004 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040004 路径 src/zephyr/governance/lifecycle_governance/__i... |
| V-ORPHAN-1040037 | 孤儿节点: 1040037 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040037 路径 src/zephyr/governance/ops_governance/token_bud... |
| V-ORPHAN-1040038 | 孤儿节点: 1040038 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040038 路径 src/zephyr/governance/ops_governance/__init__.... |
| V-ORPHAN-1040041 | 孤儿节点: 1040041 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040041 路径 src/zephyr/governance/persistence/base_repo.py... |
| V-ORPHAN-1040042 | 孤儿节点: 1040042 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040042 路径 src/zephyr/governance/persistence/dataflowgrap... |
| V-ORPHAN-1040046 | 孤儿节点: 1040046 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1040046 路径 src/zephyr/governance/persistence/depgraph_rea... |
| V-ORPHAN-1040252 | 孤儿节点: 1040252 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 1040252 路径 src/zephyr/infrastructure/database_service.py ... |
| V-ORPHAN-1041239 | 孤儿节点: 1041239 | orphan_node | D_SIGQC |  | warn | advisory | 节点 1041239 路径 src/zephyr/signal_quality/_extensions/__init__... |
| V-ORPHAN-1041241 | 孤儿节点: 1041241 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041241 路径 src/zephyr/simulation/__init__.py 未注册到目录树 |
| V-ORPHAN-1041242 | 孤儿节点: 1041242 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041242 路径 src/zephyr/simulation/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1041243 | 孤儿节点: 1041243 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041243 路径 src/zephyr/simulation/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1041245 | 孤儿节点: 1041245 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041245 路径 src/zephyr/simulation/infrastructure/__init__.... |
| V-ORPHAN-1041246 | 孤儿节点: 1041246 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041246 路径 src/zephyr/simulation/models/__init__.py 未注册到目... |
| V-ORPHAN-1041247 | 孤儿节点: 1041247 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041247 路径 src/zephyr/simulation/implementations/__init__... |
| V-ORPHAN-1041248 | 孤儿节点: 1041248 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041248 路径 src/zephyr/simulation/services/__init__.py 未注册... |
| V-ORPHAN-1041250 | 孤儿节点: 1041250 | orphan_node | D_SIMULATION |  | warn | advisory | 节点 1041250 路径 src/zephyr/simulation/_extensions/__init__.py ... |
| V-ORPHAN-1041253 | 孤儿节点: 1041253 | orphan_node | D_TRADING |  | warn | advisory | 节点 1041253 路径 src/zephyr/trading/auto_dispatcher.py 未注册到目录树 |
| V-ORPHAN-1042292 | 孤儿节点: 1042292 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042292 路径 tests/a2a/test_a2a_behavior_fingerprint.py 未注册... |
| V-ORPHAN-1042293 | 孤儿节点: 1042293 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042293 路径 tests/a2a/test_a2a_anomaly_detector.py 未注册到目录树 |
| V-ORPHAN-1042294 | 孤儿节点: 1042294 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042294 路径 tests/a2a/test_a2a_blame_attribution.py 未注册到目录... |
| V-ORPHAN-1042295 | 孤儿节点: 1042295 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042295 路径 tests/test_generate_decision_diagram.py 未注册到目录... |
| V-ORPHAN-1042296 | 孤儿节点: 1042296 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042296 路径 tests/a2a/test_a2a_carbon.py 未注册到目录树 |
| V-ORPHAN-1042297 | 孤儿节点: 1042297 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042297 路径 tests/a2a/test_a2a_causal_trace.py 未注册到目录树 |
| V-ORPHAN-1042298 | 孤儿节点: 1042298 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042298 路径 tests/a2a/test_a2a_card_registry.py 未注册到目录树 |
| V-ORPHAN-1042299 | 孤儿节点: 1042299 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042299 路径 tests/a2a/test_a2a_checkpoint.py 未注册到目录树 |
| V-ORPHAN-1042300 | 孤儿节点: 1042300 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042300 路径 tests/a2a/test_a2a_consent.py 未注册到目录树 |
| V-ORPHAN-1042301 | 孤儿节点: 1042301 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042301 路径 tests/a2a/test_a2a_check.py 未注册到目录树 |
| V-ORPHAN-1042302 | 孤儿节点: 1042302 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042302 路径 tests/a2a/test_a2a_constitutional.py 未注册到目录树 |
| V-ORPHAN-1042303 | 孤儿节点: 1042303 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042303 路径 tests/a2a/test_a2a_collusion_detector.py 未注册到目... |
| V-ORPHAN-1042304 | 孤儿节点: 1042304 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042304 路径 tests/a2a/test_a2a_context_rot.py 未注册到目录树 |
| V-ORPHAN-1042305 | 孤儿节点: 1042305 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042305 路径 tests/a2a/test_a2a_cross_agent_semantic_flow.p... |
| V-ORPHAN-1042306 | 孤儿节点: 1042306 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042306 路径 tests/a2a/test_a2a_dashboard.py 未注册到目录树 |
| V-ORPHAN-1042307 | 孤儿节点: 1042307 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042307 路径 tests/a2a/test_a2a_delegation_chain.py 未注册到目录树 |
| V-ORPHAN-1042308 | 孤儿节点: 1042308 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042308 路径 tests/a2a/test_a2a_economics.py 未注册到目录树 |
| V-ORPHAN-1042309 | 孤儿节点: 1042309 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042309 路径 tests/a2a/test_a2a_debate.py 未注册到目录树 |
| V-ORPHAN-1042310 | 孤儿节点: 1042310 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042310 路径 tests/a2a/test_a2a_formal_verification.py 未注册到... |
| V-ORPHAN-1042311 | 孤儿节点: 1042311 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042311 路径 tests/a2a/test_a2a_failure.py 未注册到目录树 |
| V-ORPHAN-1042312 | 孤儿节点: 1042312 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042312 路径 tests/a2a/test_a2a_forgetting.py 未注册到目录树 |
| V-ORPHAN-1042313 | 孤儿节点: 1042313 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042313 路径 tests/a2a/test_a2a_frame_negotiation.py 未注册到目录... |
| V-ORPHAN-1042331 | 孤儿节点: 1042331 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042331 路径 tests/a2a/test_a2a_security.py 未注册到目录树 |
| V-ORPHAN-1042332 | 孤儿节点: 1042332 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042332 路径 tests/a2a/test_a2a_state.py 未注册到目录树 |
| V-ORPHAN-1042333 | 孤儿节点: 1042333 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042333 路径 tests/a2a/test_a2a_tracing.py 未注册到目录树 |
| V-ORPHAN-1042334 | 孤儿节点: 1042334 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042334 路径 tests/a2a/test_a2a_vector_reputation.py 未注册到目录... |
| V-ORPHAN-1042335 | 孤儿节点: 1042335 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042335 路径 tests/a2a/test_a2a_temporal_admission.py 未注册到目... |
| V-ORPHAN-1042639 | 孤儿节点: 1042639 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042639 路径 tests/capacity/test_batch1_infra.py 未注册到目录树 |
| V-ORPHAN-1042640 | 孤儿节点: 1042640 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042640 路径 tests/capability/test_capability_sync.py 未注册到目... |
| V-ORPHAN-1042641 | 孤儿节点: 1042641 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042641 路径 tests/capacity/test_batch2_governance.py 未注册到目... |
| V-ORPHAN-1042642 | 孤儿节点: 1042642 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042642 路径 tests/capacity/test_batch3_integration.py 未注册到... |
| V-ORPHAN-1042643 | 孤儿节点: 1042643 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042643 路径 tests/capacity/test_capacity_assurance.py 未注册到... |
| V-ORPHAN-1042644 | 孤儿节点: 1042644 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1042644 路径 tests/ce/test_ce_bootstrap.py 未注册到目录树 |
| V-ORPHAN-1043465 | 孤儿节点: 1043465 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043465 路径 tests/io/test_io_paths.py 未注册到目录树 |
| V-ORPHAN-1043466 | 孤儿节点: 1043466 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043466 路径 tests/io/test_depgraph_schema.py 未注册到目录树 |
| V-ORPHAN-1043467 | 孤儿节点: 1043467 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043467 路径 tests/io/test_io_serialization.py 未注册到目录树 |
| V-ORPHAN-1043468 | 孤儿节点: 1043468 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043468 路径 tests/io/test_mcp_launcher.py 未注册到目录树 |
| V-ORPHAN-1043469 | 孤儿节点: 1043469 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043469 路径 tests/io/test_verify_schema_health.py 未注册到目录树 |
| V-ORPHAN-1043470 | 孤儿节点: 1043470 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043470 路径 tests/io/test_mcp_task_claim.py 未注册到目录树 |
| V-ORPHAN-1043471 | 孤儿节点: 1043471 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043471 路径 tests/kb/test_kb_activate.py 未注册到目录树 |
| V-ORPHAN-1043472 | 孤儿节点: 1043472 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043472 路径 tests/kb/test_kb_analyze.py 未注册到目录树 |
| V-ORPHAN-1043473 | 孤儿节点: 1043473 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043473 路径 tests/kb/test_kb_bootstrap.py 未注册到目录树 |
| V-ORPHAN-1043474 | 孤儿节点: 1043474 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043474 路径 tests/kb/test_kb_batch_ingest.py 未注册到目录树 |
| V-ORPHAN-1043475 | 孤儿节点: 1043475 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043475 路径 tests/kb/test_kb_extract.py 未注册到目录树 |
| V-ORPHAN-1043476 | 孤儿节点: 1043476 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043476 路径 tests/kb/test_kb_embedding_migrate.py 未注册到目录树 |
| V-ORPHAN-1043477 | 孤儿节点: 1043477 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043477 路径 tests/kb/test_kb_gate.py 未注册到目录树 |
| V-ORPHAN-1043478 | 孤儿节点: 1043478 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043478 路径 tests/kb/test_kb_freeze.py 未注册到目录树 |
| V-ORPHAN-1043479 | 孤儿节点: 1043479 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043479 路径 tests/kb/test_kb_gate_task.py 未注册到目录树 |
| V-ORPHAN-1043480 | 孤儿节点: 1043480 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043480 路径 tests/kb/test_kb_graph_validator.py 未注册到目录树 |
| V-ORPHAN-1043481 | 孤儿节点: 1043481 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043481 路径 tests/kb/test_kb_ingest.py 未注册到目录树 |
| V-ORPHAN-1043482 | 孤儿节点: 1043482 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043482 路径 tests/kb/test_kb_integrity.py 未注册到目录树 |
| V-ORPHAN-1043483 | 孤儿节点: 1043483 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043483 路径 tests/kb/test_kb_migration_embedding.py 未注册到目录... |
| V-ORPHAN-1043484 | 孤儿节点: 1043484 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043484 路径 tests/kb/test_kb_pipeline_activate.py 未注册到目录树 |
| V-ORPHAN-1043485 | 孤儿节点: 1043485 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043485 路径 tests/kb/test_kb_migration_gate.py 未注册到目录树 |
| V-ORPHAN-1043486 | 孤儿节点: 1043486 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043486 路径 tests/kb/test_kb_reranker.py 未注册到目录树 |
| V-ORPHAN-1043487 | 孤儿节点: 1043487 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043487 路径 tests/kb/test_kb_self_test.py 未注册到目录树 |
| V-ORPHAN-1043488 | 孤儿节点: 1043488 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043488 路径 tests/kb/test_kb_storage_backend.py 未注册到目录树 |
| V-ORPHAN-1043489 | 孤儿节点: 1043489 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043489 路径 tests/kb/test_kb_triage.py 未注册到目录树 |
| V-ORPHAN-1043490 | 孤儿节点: 1043490 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043490 路径 tests/kb/test_kb_vms_memory_backend.py 未注册到目录树 |
| V-ORPHAN-1043957 | 孤儿节点: 1043957 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043957 路径 tests/zephyr/data/test_provider_base.py 未注册到目录... |
| V-ORPHAN-1043958 | 孤儿节点: 1043958 | orphan_node | D_AUDITTEST |  | warn | advisory | 节点 1043958 路径 tests/zephyr/data/__init__.py 未注册到目录树 |
| V-ORPHAN-1043959 | 孤儿节点: 1043959 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043959 路径 data/asset_index/archive/migration_scripts/app... |
| V-ORPHAN-1043960 | 孤儿节点: 1043960 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043960 路径 data/asset_index/archive/migration_scripts/com... |
| V-ORPHAN-1043961 | 孤儿节点: 1043961 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043961 路径 data/asset_index/archive/migration_scripts/che... |
| V-ORPHAN-1043962 | 孤儿节点: 1043962 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043962 路径 data/asset_index/archive/migration_scripts/cre... |
| V-ORPHAN-1043963 | 孤儿节点: 1043963 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043963 路径 data/asset_index/archive/migration_scripts/cro... |
| V-ORPHAN-1043964 | 孤儿节点: 1043964 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043964 路径 data/asset_index/archive/migration_scripts/gen... |
| V-ORPHAN-1043965 | 孤儿节点: 1043965 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043965 路径 data/asset_index/archive/migration_scripts/exe... |
| V-ORPHAN-1043966 | 孤儿节点: 1043966 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043966 路径 data/asset_index/archive/migration_scripts/dom... |
| V-ORPHAN-1043967 | 孤儿节点: 1043967 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043967 路径 data/asset_index/archive/migration_scripts/gen... |
| V-ORPHAN-1043968 | 孤儿节点: 1043968 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043968 路径 data/asset_index/archive/migration_scripts/inj... |
| V-ORPHAN-1043969 | 孤儿节点: 1043969 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043969 路径 data/asset_index/archive/migration_scripts/pre... |
| V-ORPHAN-1043970 | 孤儿节点: 1043970 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043970 路径 data/asset_index/archive/migration_scripts/sca... |
| V-ORPHAN-1043971 | 孤儿节点: 1043971 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043971 路径 data/asset_index/archive/migration_scripts/loc... |
| V-ORPHAN-1043972 | 孤儿节点: 1043972 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043972 路径 data/asset_index/archive/migration_scripts/rol... |
| V-ORPHAN-1043973 | 孤儿节点: 1043973 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1043973 路径 data/asset_index/archive/migration_scripts/sha... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 479 超过上限 1... |
| V-CAP-D_TRADING | 容量超限: D_TRADING | capacity_exceeded | D_TRADING |  | hard | gate | 域 D_TRADING(交易运营) production 节点 280 超过上限 150，需拆分或提升上限 (ARCH-... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_GOVERNANCE | 跨域违规: D_AUTONOMY_CORE -> D_GOVERNANCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOVERNANCE |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTELLIGENCE |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY_LLM | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY_LLM | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY_LLM | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SECURITY_LLM |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_BACKTEST -> D_GOVERNANCE |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_FACTOR -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_FRONTEND-D_GOVERNANCE | 跨域违规: D_FRONTEND -> D_GOVERNANCE | cross_domain_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FRONTEND -> D_GOVERNANCE |
| V-CROSS-D_FRONTEND-D_TRADING | 跨域违规: D_FRONTEND -> D_TRADING | cross_domain_violation | D_FRONTEND | D_TRADING | error | gate | 跨域依赖未声明: D_FRONTEND -> D_TRADING |
| V-CROSS-D_GOVERNANCE-D_FACTOR | 跨域违规: D_GOVERNANCE -> D_FACTOR | cross_domain_violation | D_GOVERNANCE | D_FACTOR | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_FACTOR |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_A2A |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INTELLIGENCE |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_OPS |
| V-CROSS-D_GOVERNANCE-D_PF_CORE | 跨域违规: D_GOVERNANCE -> D_PF_CORE | cross_domain_violation | D_GOVERNANCE | D_PF_CORE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_PF_CORE |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_REPORTING |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_SECURITY |
| V-CROSS-D_GOVERNANCE-D_SECURITY_LLM | 跨域违规: D_GOVERNANCE -> D_SECURITY_LLM | cross_domain_violation | D_GOVERNANCE | D_SECURITY_LLM | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_SECURITY_LLM |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_TRADING |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOVERNANCE |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRA_RECOVERY | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INTEGRATION |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_SECURITY |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_TRADING |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOVERNANCE |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_ENFORCEMENT |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 479 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1039341 -> 1039963 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1039389 -> 1040147 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1039341 -> 1040648 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1039595 -> 1040049 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1039611 -> 1041712 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1040360 -> 1039924 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1040367 -> 1041192 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1040380 -> 1039703 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1040273 -> 1040604 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1040389 -> 1041121 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1039308 -> 1041596 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1039943 -> 1039911 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1039812 -> 1040087 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1039995 | 孤儿节点: 1039995 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1039997 | 孤儿节点: 1039997 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1039998 | 孤儿节点: 1039998 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1039999 | 孤儿节点: 1039999 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040000 | 孤儿节点: 1040000 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040001 | 孤儿节点: 1040001 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040002 | 孤儿节点: 1040002 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040004 | 孤儿节点: 1040004 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040037 | 孤儿节点: 1040037 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040038 | 孤儿节点: 1040038 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040041 | 孤儿节点: 1040041 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040042 | 孤儿节点: 1040042 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040046 | 孤儿节点: 1040046 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1040252 | 孤儿节点: 1040252 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-1041239 | 孤儿节点: 1041239 | orphan_node | D_SIGQC |  | warn | open |
| V-ORPHAN-1041241 | 孤儿节点: 1041241 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041242 | 孤儿节点: 1041242 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041243 | 孤儿节点: 1041243 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041245 | 孤儿节点: 1041245 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041246 | 孤儿节点: 1041246 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041247 | 孤儿节点: 1041247 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041248 | 孤儿节点: 1041248 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041250 | 孤儿节点: 1041250 | orphan_node | D_SIMULATION |  | warn | open |
| V-ORPHAN-1041253 | 孤儿节点: 1041253 | orphan_node | D_TRADING |  | warn | open |
| V-ORPHAN-1042292 | 孤儿节点: 1042292 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042293 | 孤儿节点: 1042293 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042294 | 孤儿节点: 1042294 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042295 | 孤儿节点: 1042295 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042296 | 孤儿节点: 1042296 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042297 | 孤儿节点: 1042297 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042298 | 孤儿节点: 1042298 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042299 | 孤儿节点: 1042299 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042300 | 孤儿节点: 1042300 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042301 | 孤儿节点: 1042301 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042302 | 孤儿节点: 1042302 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042303 | 孤儿节点: 1042303 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042304 | 孤儿节点: 1042304 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042305 | 孤儿节点: 1042305 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042306 | 孤儿节点: 1042306 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042307 | 孤儿节点: 1042307 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042308 | 孤儿节点: 1042308 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042309 | 孤儿节点: 1042309 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042310 | 孤儿节点: 1042310 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042311 | 孤儿节点: 1042311 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042312 | 孤儿节点: 1042312 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042313 | 孤儿节点: 1042313 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042331 | 孤儿节点: 1042331 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042332 | 孤儿节点: 1042332 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042333 | 孤儿节点: 1042333 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042334 | 孤儿节点: 1042334 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042335 | 孤儿节点: 1042335 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042639 | 孤儿节点: 1042639 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042640 | 孤儿节点: 1042640 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042641 | 孤儿节点: 1042641 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042642 | 孤儿节点: 1042642 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042643 | 孤儿节点: 1042643 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1042644 | 孤儿节点: 1042644 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043465 | 孤儿节点: 1043465 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043466 | 孤儿节点: 1043466 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043467 | 孤儿节点: 1043467 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043468 | 孤儿节点: 1043468 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043469 | 孤儿节点: 1043469 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043470 | 孤儿节点: 1043470 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043471 | 孤儿节点: 1043471 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043472 | 孤儿节点: 1043472 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043473 | 孤儿节点: 1043473 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043474 | 孤儿节点: 1043474 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043475 | 孤儿节点: 1043475 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043476 | 孤儿节点: 1043476 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043477 | 孤儿节点: 1043477 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043478 | 孤儿节点: 1043478 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043479 | 孤儿节点: 1043479 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043480 | 孤儿节点: 1043480 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043481 | 孤儿节点: 1043481 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043482 | 孤儿节点: 1043482 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043483 | 孤儿节点: 1043483 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043484 | 孤儿节点: 1043484 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043485 | 孤儿节点: 1043485 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043486 | 孤儿节点: 1043486 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043487 | 孤儿节点: 1043487 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043488 | 孤儿节点: 1043488 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043489 | 孤儿节点: 1043489 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043490 | 孤儿节点: 1043490 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043957 | 孤儿节点: 1043957 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043958 | 孤儿节点: 1043958 | orphan_node | D_AUDITTEST |  | warn | open |
| V-ORPHAN-1043959 | 孤儿节点: 1043959 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043960 | 孤儿节点: 1043960 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043961 | 孤儿节点: 1043961 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043962 | 孤儿节点: 1043962 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043963 | 孤儿节点: 1043963 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043964 | 孤儿节点: 1043964 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043965 | 孤儿节点: 1043965 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043966 | 孤儿节点: 1043966 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043967 | 孤儿节点: 1043967 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043968 | 孤儿节点: 1043968 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043969 | 孤儿节点: 1043969 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043970 | 孤儿节点: 1043970 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043971 | 孤儿节点: 1043971 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043972 | 孤儿节点: 1043972 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1043973 | 孤儿节点: 1043973 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | open |
| V-CAP-D_TRADING | 容量超限: D_TRADING | capacity_exceeded | D_TRADING |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOVERNANCE | 跨域违规: D_AUTONOMY_CORE -> D_GOVERNANCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY_LLM | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY_LLM | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY_LLM | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_FRONTEND-D_GOVERNANCE | 跨域违规: D_FRONTEND -> D_GOVERNANCE | cross_domain_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-CROSS-D_FRONTEND-D_TRADING | 跨域违规: D_FRONTEND -> D_TRADING | cross_domain_violation | D_FRONTEND | D_TRADING | error | open |
| V-CROSS-D_GOVERNANCE-D_FACTOR | 跨域违规: D_GOVERNANCE -> D_FACTOR | cross_domain_violation | D_GOVERNANCE | D_FACTOR | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | open |
| V-CROSS-D_GOVERNANCE-D_PF_CORE | 跨域违规: D_GOVERNANCE -> D_PF_CORE | cross_domain_violation | D_GOVERNANCE | D_PF_CORE | error | open |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | open |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | open |
| V-CROSS-D_GOVERNANCE-D_SECURITY_LLM | 跨域违规: D_GOVERNANCE -> D_SECURITY_LLM | cross_domain_violation | D_GOVERNANCE | D_SECURITY_LLM | error | open |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRA_RECOVERY | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | open |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
