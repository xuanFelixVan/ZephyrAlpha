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
| V-ORPHAN-1527414 | 孤儿节点: 1527414 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 1527414 路径 src/zephyr/__init__.py 未注册到目录树 |
| V-ORPHAN-1527415 | 孤儿节点: 1527415 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527415 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1527416 | 孤儿节点: 1527416 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527416 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1527417 | 孤儿节点: 1527417 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527417 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1527418 | 孤儿节点: 1527418 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527418 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1527419 | 孤儿节点: 1527419 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527419 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1527420 | 孤儿节点: 1527420 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527420 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1527421 | 孤儿节点: 1527421 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1527421 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1527422 | 孤儿节点: 1527422 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1527422 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1527423 | 孤儿节点: 1527423 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1527423 路径 src/zephyr/autonomy_core/agent_observability.p... |
| V-ORPHAN-1527476 | 孤儿节点: 1527476 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1527476 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1527535 | 孤儿节点: 1527535 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1527535 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1527536 | 孤儿节点: 1527536 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527536 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1527537 | 孤儿节点: 1527537 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527537 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1527538 | 孤儿节点: 1527538 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527538 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1527539 | 孤儿节点: 1527539 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527539 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1527540 | 孤儿节点: 1527540 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527540 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1527541 | 孤儿节点: 1527541 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527541 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1527542 | 孤儿节点: 1527542 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527542 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1527543 | 孤儿节点: 1527543 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527543 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1527544 | 孤儿节点: 1527544 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527544 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1527545 | 孤儿节点: 1527545 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527545 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1527546 | 孤儿节点: 1527546 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527546 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1527547 | 孤儿节点: 1527547 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527547 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1527548 | 孤儿节点: 1527548 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527548 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1527549 | 孤儿节点: 1527549 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527549 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1527550 | 孤儿节点: 1527550 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1527550 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1527551 | 孤儿节点: 1527551 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527551 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1527552 | 孤儿节点: 1527552 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527552 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1527558 | 孤儿节点: 1527558 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527558 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1527559 | 孤儿节点: 1527559 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527559 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1527561 | 孤儿节点: 1527561 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527561 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1527562 | 孤儿节点: 1527562 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527562 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1527563 | 孤儿节点: 1527563 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527563 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1527567 | 孤儿节点: 1527567 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527567 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1527569 | 孤儿节点: 1527569 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527569 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1527570 | 孤儿节点: 1527570 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527570 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1527571 | 孤儿节点: 1527571 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527571 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1527572 | 孤儿节点: 1527572 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527572 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1527573 | 孤儿节点: 1527573 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527573 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1527574 | 孤儿节点: 1527574 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527574 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1527575 | 孤儿节点: 1527575 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1527575 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1527576 | 孤儿节点: 1527576 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527576 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1527577 | 孤儿节点: 1527577 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527577 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1527578 | 孤儿节点: 1527578 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527578 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1527579 | 孤儿节点: 1527579 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527579 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1527580 | 孤儿节点: 1527580 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527580 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1527581 | 孤儿节点: 1527581 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527581 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1527582 | 孤儿节点: 1527582 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527582 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1527583 | 孤儿节点: 1527583 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527583 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1527584 | 孤儿节点: 1527584 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527584 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1527585 | 孤儿节点: 1527585 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527585 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1527586 | 孤儿节点: 1527586 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527586 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1527587 | 孤儿节点: 1527587 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527587 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1527588 | 孤儿节点: 1527588 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527588 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1527589 | 孤儿节点: 1527589 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527589 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1527590 | 孤儿节点: 1527590 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527590 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1527591 | 孤儿节点: 1527591 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527591 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1527592 | 孤儿节点: 1527592 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527592 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1527593 | 孤儿节点: 1527593 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527593 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1527594 | 孤儿节点: 1527594 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527594 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1527595 | 孤儿节点: 1527595 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527595 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1527596 | 孤儿节点: 1527596 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527596 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1527597 | 孤儿节点: 1527597 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527597 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1527598 | 孤儿节点: 1527598 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1527598 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1527599 | 孤儿节点: 1527599 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527599 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1527600 | 孤儿节点: 1527600 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527600 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1527601 | 孤儿节点: 1527601 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527601 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1527602 | 孤儿节点: 1527602 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527602 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1527604 | 孤儿节点: 1527604 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527604 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1527605 | 孤儿节点: 1527605 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1527605 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1527607 | 孤儿节点: 1527607 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527607 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1527609 | 孤儿节点: 1527609 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527609 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1527610 | 孤儿节点: 1527610 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527610 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1527611 | 孤儿节点: 1527611 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527611 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1527612 | 孤儿节点: 1527612 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527612 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1527615 | 孤儿节点: 1527615 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527615 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1527616 | 孤儿节点: 1527616 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527616 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1527617 | 孤儿节点: 1527617 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527617 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1527618 | 孤儿节点: 1527618 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527618 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1527619 | 孤儿节点: 1527619 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527619 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1527620 | 孤儿节点: 1527620 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527620 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1527621 | 孤儿节点: 1527621 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527621 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1527622 | 孤儿节点: 1527622 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527622 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1527623 | 孤儿节点: 1527623 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527623 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1527624 | 孤儿节点: 1527624 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527624 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1527625 | 孤儿节点: 1527625 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1527625 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1527626 | 孤儿节点: 1527626 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527626 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1527627 | 孤儿节点: 1527627 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527627 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1527628 | 孤儿节点: 1527628 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527628 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1527629 | 孤儿节点: 1527629 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527629 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-1527630 | 孤儿节点: 1527630 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527630 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1527631 | 孤儿节点: 1527631 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527631 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1527632 | 孤儿节点: 1527632 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527632 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1527633 | 孤儿节点: 1527633 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1527633 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1527634 | 孤儿节点: 1527634 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527634 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1527635 | 孤儿节点: 1527635 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527635 路径 src/zephyr/data_governance/services/__init__.p... |
| V-ORPHAN-1527636 | 孤儿节点: 1527636 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527636 路径 src/zephyr/data_governance/core/__init__.py 未注... |
| V-ORPHAN-1527637 | 孤儿节点: 1527637 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527637 路径 src/zephyr/data_governance/models/__init__.py ... |
| V-ORPHAN-1527638 | 孤儿节点: 1527638 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1527638 路径 src/zephyr/data_governance/infrastructure/__in... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 483 超过上限 1... |
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
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 483 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1527526 -> 1527757 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1527495 -> 1528260 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1527444 -> 1528741 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1527700 -> 1528167 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1527713 -> 1529798 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1528449 -> 1528038 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1528456 -> 1529285 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1528489 -> 1527771 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1528368 -> 1528699 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1528543 -> 1529262 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1527414 -> 1529689 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1528056 -> 1528024 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1527926 -> 1528201 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1527414 | 孤儿节点: 1527414 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-1527415 | 孤儿节点: 1527415 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527416 | 孤儿节点: 1527416 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527417 | 孤儿节点: 1527417 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527418 | 孤儿节点: 1527418 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527419 | 孤儿节点: 1527419 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527420 | 孤儿节点: 1527420 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527421 | 孤儿节点: 1527421 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1527422 | 孤儿节点: 1527422 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1527423 | 孤儿节点: 1527423 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1527476 | 孤儿节点: 1527476 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1527535 | 孤儿节点: 1527535 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1527536 | 孤儿节点: 1527536 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527537 | 孤儿节点: 1527537 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527538 | 孤儿节点: 1527538 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527539 | 孤儿节点: 1527539 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527540 | 孤儿节点: 1527540 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527541 | 孤儿节点: 1527541 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527542 | 孤儿节点: 1527542 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527543 | 孤儿节点: 1527543 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527544 | 孤儿节点: 1527544 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527545 | 孤儿节点: 1527545 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527546 | 孤儿节点: 1527546 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527547 | 孤儿节点: 1527547 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527548 | 孤儿节点: 1527548 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527549 | 孤儿节点: 1527549 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527550 | 孤儿节点: 1527550 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1527551 | 孤儿节点: 1527551 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527552 | 孤儿节点: 1527552 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527558 | 孤儿节点: 1527558 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527559 | 孤儿节点: 1527559 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527561 | 孤儿节点: 1527561 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527562 | 孤儿节点: 1527562 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527563 | 孤儿节点: 1527563 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527567 | 孤儿节点: 1527567 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527569 | 孤儿节点: 1527569 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527570 | 孤儿节点: 1527570 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527571 | 孤儿节点: 1527571 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527572 | 孤儿节点: 1527572 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527573 | 孤儿节点: 1527573 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527574 | 孤儿节点: 1527574 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527575 | 孤儿节点: 1527575 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1527576 | 孤儿节点: 1527576 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527577 | 孤儿节点: 1527577 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527578 | 孤儿节点: 1527578 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527579 | 孤儿节点: 1527579 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527580 | 孤儿节点: 1527580 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527581 | 孤儿节点: 1527581 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527582 | 孤儿节点: 1527582 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527583 | 孤儿节点: 1527583 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527584 | 孤儿节点: 1527584 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527585 | 孤儿节点: 1527585 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527586 | 孤儿节点: 1527586 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527587 | 孤儿节点: 1527587 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527588 | 孤儿节点: 1527588 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527589 | 孤儿节点: 1527589 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527590 | 孤儿节点: 1527590 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527591 | 孤儿节点: 1527591 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527592 | 孤儿节点: 1527592 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527593 | 孤儿节点: 1527593 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527594 | 孤儿节点: 1527594 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527595 | 孤儿节点: 1527595 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527596 | 孤儿节点: 1527596 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527597 | 孤儿节点: 1527597 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527598 | 孤儿节点: 1527598 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1527599 | 孤儿节点: 1527599 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527600 | 孤儿节点: 1527600 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527601 | 孤儿节点: 1527601 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527602 | 孤儿节点: 1527602 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527604 | 孤儿节点: 1527604 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527605 | 孤儿节点: 1527605 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1527607 | 孤儿节点: 1527607 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527609 | 孤儿节点: 1527609 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527610 | 孤儿节点: 1527610 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527611 | 孤儿节点: 1527611 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527612 | 孤儿节点: 1527612 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527615 | 孤儿节点: 1527615 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527616 | 孤儿节点: 1527616 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527617 | 孤儿节点: 1527617 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527618 | 孤儿节点: 1527618 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527619 | 孤儿节点: 1527619 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527620 | 孤儿节点: 1527620 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527621 | 孤儿节点: 1527621 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527622 | 孤儿节点: 1527622 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527623 | 孤儿节点: 1527623 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527624 | 孤儿节点: 1527624 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527625 | 孤儿节点: 1527625 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1527626 | 孤儿节点: 1527626 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527627 | 孤儿节点: 1527627 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527628 | 孤儿节点: 1527628 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527629 | 孤儿节点: 1527629 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527630 | 孤儿节点: 1527630 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527631 | 孤儿节点: 1527631 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527632 | 孤儿节点: 1527632 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1527633 | 孤儿节点: 1527633 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1527634 | 孤儿节点: 1527634 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1527635 | 孤儿节点: 1527635 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1527636 | 孤儿节点: 1527636 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1527637 | 孤儿节点: 1527637 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1527638 | 孤儿节点: 1527638 | orphan_node | D_DATA_GOV |  | warn | open |
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
