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
| 约束总数 | 154 |
| Open（未解决） | 154 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 52 |
| hard | 2 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 2 |
| cross_domain_violation | 36 |
| hard_limit_exceeded | 2 |
| layer_violation | 13 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-1740367 | 孤儿节点: 1740367 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740367 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1740368 | 孤儿节点: 1740368 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740368 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1740369 | 孤儿节点: 1740369 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740369 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1740370 | 孤儿节点: 1740370 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740370 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1740371 | 孤儿节点: 1740371 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740371 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1740372 | 孤儿节点: 1740372 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740372 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1740373 | 孤儿节点: 1740373 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1740373 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1740374 | 孤儿节点: 1740374 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1740374 路径 src/zephyr/autonomy_core/agent_observability.p... |
| V-ORPHAN-1740378 | 孤儿节点: 1740378 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1740378 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1740427 | 孤儿节点: 1740427 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1740427 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1740487 | 孤儿节点: 1740487 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1740487 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1740488 | 孤儿节点: 1740488 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740488 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1740489 | 孤儿节点: 1740489 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740489 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1740490 | 孤儿节点: 1740490 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740490 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1740491 | 孤儿节点: 1740491 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740491 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1740492 | 孤儿节点: 1740492 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740492 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1740493 | 孤儿节点: 1740493 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740493 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1740494 | 孤儿节点: 1740494 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740494 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1740495 | 孤儿节点: 1740495 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740495 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1740496 | 孤儿节点: 1740496 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740496 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1740497 | 孤儿节点: 1740497 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740497 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1740498 | 孤儿节点: 1740498 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740498 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1740499 | 孤儿节点: 1740499 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740499 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1740501 | 孤儿节点: 1740501 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740501 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1740502 | 孤儿节点: 1740502 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1740502 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1740503 | 孤儿节点: 1740503 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740503 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1740504 | 孤儿节点: 1740504 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740504 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1740505 | 孤儿节点: 1740505 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740505 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1740508 | 孤儿节点: 1740508 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740508 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1740509 | 孤儿节点: 1740509 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740509 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1740510 | 孤儿节点: 1740510 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740510 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1740514 | 孤儿节点: 1740514 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740514 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1740515 | 孤儿节点: 1740515 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740515 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1740516 | 孤儿节点: 1740516 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740516 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1740520 | 孤儿节点: 1740520 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740520 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1740522 | 孤儿节点: 1740522 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740522 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1740523 | 孤儿节点: 1740523 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740523 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1740524 | 孤儿节点: 1740524 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740524 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1740525 | 孤儿节点: 1740525 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740525 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1740526 | 孤儿节点: 1740526 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1740526 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1740527 | 孤儿节点: 1740527 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740527 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1740528 | 孤儿节点: 1740528 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740528 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1740529 | 孤儿节点: 1740529 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740529 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1740530 | 孤儿节点: 1740530 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740530 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1740531 | 孤儿节点: 1740531 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740531 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1740532 | 孤儿节点: 1740532 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740532 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1740533 | 孤儿节点: 1740533 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740533 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1740534 | 孤儿节点: 1740534 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740534 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1740535 | 孤儿节点: 1740535 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740535 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1740536 | 孤儿节点: 1740536 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740536 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1740537 | 孤儿节点: 1740537 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740537 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1740538 | 孤儿节点: 1740538 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740538 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1740539 | 孤儿节点: 1740539 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740539 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1740540 | 孤儿节点: 1740540 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740540 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1740541 | 孤儿节点: 1740541 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740541 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1740542 | 孤儿节点: 1740542 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740542 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1740543 | 孤儿节点: 1740543 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740543 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1740544 | 孤儿节点: 1740544 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740544 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1740545 | 孤儿节点: 1740545 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740545 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1740546 | 孤儿节点: 1740546 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740546 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1740547 | 孤儿节点: 1740547 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740547 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1740548 | 孤儿节点: 1740548 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740548 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1740549 | 孤儿节点: 1740549 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740549 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1740550 | 孤儿节点: 1740550 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1740550 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1740552 | 孤儿节点: 1740552 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740552 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1740553 | 孤儿节点: 1740553 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740553 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1740554 | 孤儿节点: 1740554 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740554 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1740555 | 孤儿节点: 1740555 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740555 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1740556 | 孤儿节点: 1740556 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740556 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1740557 | 孤儿节点: 1740557 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1740557 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1740558 | 孤儿节点: 1740558 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740558 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1740559 | 孤儿节点: 1740559 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740559 路径 src/zephyr/data/policy_registry.py 未注册到目录树 |
| V-ORPHAN-1740560 | 孤儿节点: 1740560 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740560 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1740562 | 孤儿节点: 1740562 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740562 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1740563 | 孤儿节点: 1740563 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740563 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1740564 | 孤儿节点: 1740564 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740564 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1740565 | 孤儿节点: 1740565 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740565 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1740566 | 孤儿节点: 1740566 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740566 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-1740567 | 孤儿节点: 1740567 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740567 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1740568 | 孤儿节点: 1740568 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740568 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1740570 | 孤儿节点: 1740570 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740570 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1740571 | 孤儿节点: 1740571 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740571 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1740572 | 孤儿节点: 1740572 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740572 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1740573 | 孤儿节点: 1740573 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740573 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1740574 | 孤儿节点: 1740574 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740574 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1740575 | 孤儿节点: 1740575 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740575 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1740576 | 孤儿节点: 1740576 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740576 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1740577 | 孤儿节点: 1740577 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740577 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1740578 | 孤儿节点: 1740578 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1740578 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1740579 | 孤儿节点: 1740579 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740579 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1740580 | 孤儿节点: 1740580 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740580 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1740581 | 孤儿节点: 1740581 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740581 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1740582 | 孤儿节点: 1740582 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740582 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-1740583 | 孤儿节点: 1740583 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740583 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1740584 | 孤儿节点: 1740584 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1740584 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1740585 | 孤儿节点: 1740585 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1740585 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1740586 | 孤儿节点: 1740586 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1740586 路径 src/zephyr/data_governance/core/__init__.py 未注... |
| V-ORPHAN-1740587 | 孤儿节点: 1740587 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1740587 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1740588 | 孤儿节点: 1740588 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1740588 路径 src/zephyr/data_governance/models/__init__.py ... |
| V-ORPHAN-1740589 | 孤儿节点: 1740589 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1740589 路径 src/zephyr/data_governance/infrastructure/__in... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 503 超过上限 1... |
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
| V-CROSS-D_INFRA_A2A-D_SHARED | 跨域违规: D_INFRA_A2A -> D_SHARED | cross_domain_violation | D_INFRA_A2A | D_SHARED | error | gate | 跨域依赖未声明: D_INFRA_A2A -> D_SHARED |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTEGRATION |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_TRADING |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOVERNANCE |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_ENFORCEMENT |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 503 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1740476 -> 1740707 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1740447 -> 1741218 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1740398 -> 1741698 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1740654 -> 1741120 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1740666 -> 1742760 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1741409 -> 1740993 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1741416 -> 1742243 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1741449 -> 1740725 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1741327 -> 1741656 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1741501 -> 1742220 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1740366 -> 1742648 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1741013 -> 1741247 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1740885 -> 1741158 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1740367 | 孤儿节点: 1740367 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740368 | 孤儿节点: 1740368 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740369 | 孤儿节点: 1740369 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740370 | 孤儿节点: 1740370 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740371 | 孤儿节点: 1740371 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740372 | 孤儿节点: 1740372 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740373 | 孤儿节点: 1740373 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1740374 | 孤儿节点: 1740374 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1740378 | 孤儿节点: 1740378 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1740427 | 孤儿节点: 1740427 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1740487 | 孤儿节点: 1740487 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1740488 | 孤儿节点: 1740488 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740489 | 孤儿节点: 1740489 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740490 | 孤儿节点: 1740490 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740491 | 孤儿节点: 1740491 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740492 | 孤儿节点: 1740492 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740493 | 孤儿节点: 1740493 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740494 | 孤儿节点: 1740494 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740495 | 孤儿节点: 1740495 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740496 | 孤儿节点: 1740496 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740497 | 孤儿节点: 1740497 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740498 | 孤儿节点: 1740498 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740499 | 孤儿节点: 1740499 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740501 | 孤儿节点: 1740501 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740502 | 孤儿节点: 1740502 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1740503 | 孤儿节点: 1740503 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740504 | 孤儿节点: 1740504 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740505 | 孤儿节点: 1740505 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740508 | 孤儿节点: 1740508 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740509 | 孤儿节点: 1740509 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740510 | 孤儿节点: 1740510 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740514 | 孤儿节点: 1740514 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740515 | 孤儿节点: 1740515 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740516 | 孤儿节点: 1740516 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740520 | 孤儿节点: 1740520 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740522 | 孤儿节点: 1740522 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740523 | 孤儿节点: 1740523 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740524 | 孤儿节点: 1740524 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740525 | 孤儿节点: 1740525 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740526 | 孤儿节点: 1740526 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1740527 | 孤儿节点: 1740527 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740528 | 孤儿节点: 1740528 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740529 | 孤儿节点: 1740529 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740530 | 孤儿节点: 1740530 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740531 | 孤儿节点: 1740531 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740532 | 孤儿节点: 1740532 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740533 | 孤儿节点: 1740533 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740534 | 孤儿节点: 1740534 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740535 | 孤儿节点: 1740535 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740536 | 孤儿节点: 1740536 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740537 | 孤儿节点: 1740537 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740538 | 孤儿节点: 1740538 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740539 | 孤儿节点: 1740539 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740540 | 孤儿节点: 1740540 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740541 | 孤儿节点: 1740541 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740542 | 孤儿节点: 1740542 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740543 | 孤儿节点: 1740543 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740544 | 孤儿节点: 1740544 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740545 | 孤儿节点: 1740545 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740546 | 孤儿节点: 1740546 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740547 | 孤儿节点: 1740547 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740548 | 孤儿节点: 1740548 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740549 | 孤儿节点: 1740549 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740550 | 孤儿节点: 1740550 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1740552 | 孤儿节点: 1740552 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740553 | 孤儿节点: 1740553 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740554 | 孤儿节点: 1740554 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740555 | 孤儿节点: 1740555 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740556 | 孤儿节点: 1740556 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740557 | 孤儿节点: 1740557 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1740558 | 孤儿节点: 1740558 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740559 | 孤儿节点: 1740559 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740560 | 孤儿节点: 1740560 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740562 | 孤儿节点: 1740562 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740563 | 孤儿节点: 1740563 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740564 | 孤儿节点: 1740564 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740565 | 孤儿节点: 1740565 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740566 | 孤儿节点: 1740566 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740567 | 孤儿节点: 1740567 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740568 | 孤儿节点: 1740568 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740570 | 孤儿节点: 1740570 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740571 | 孤儿节点: 1740571 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740572 | 孤儿节点: 1740572 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740573 | 孤儿节点: 1740573 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740574 | 孤儿节点: 1740574 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740575 | 孤儿节点: 1740575 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740576 | 孤儿节点: 1740576 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740577 | 孤儿节点: 1740577 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740578 | 孤儿节点: 1740578 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1740579 | 孤儿节点: 1740579 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740580 | 孤儿节点: 1740580 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740581 | 孤儿节点: 1740581 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740582 | 孤儿节点: 1740582 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740583 | 孤儿节点: 1740583 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740584 | 孤儿节点: 1740584 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1740585 | 孤儿节点: 1740585 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1740586 | 孤儿节点: 1740586 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1740587 | 孤儿节点: 1740587 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1740588 | 孤儿节点: 1740588 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1740589 | 孤儿节点: 1740589 | orphan_node | D_DATA_GOV |  | warn | open |
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
| V-CROSS-D_INFRA_A2A-D_SHARED | 跨域违规: D_INFRA_A2A -> D_SHARED | cross_domain_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
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
