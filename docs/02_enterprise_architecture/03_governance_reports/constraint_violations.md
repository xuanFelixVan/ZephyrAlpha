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
| 约束总数 | 159 |
| Open（未解决） | 159 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 57 |
| hard | 2 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 2 |
| cross_domain_violation | 34 |
| hard_limit_exceeded | 2 |
| layer_violation | 20 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-1004534 | 孤儿节点: 1004534 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004534 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1004536 | 孤儿节点: 1004536 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004536 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1004537 | 孤儿节点: 1004537 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004537 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1004538 | 孤儿节点: 1004538 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004538 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1004539 | 孤儿节点: 1004539 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004539 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1004540 | 孤儿节点: 1004540 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004540 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1004541 | 孤儿节点: 1004541 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1004541 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1004543 | 孤儿节点: 1004543 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1004543 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1004596 | 孤儿节点: 1004596 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1004596 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1004655 | 孤儿节点: 1004655 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004655 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1004656 | 孤儿节点: 1004656 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1004656 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1004657 | 孤儿节点: 1004657 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004657 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1004658 | 孤儿节点: 1004658 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004658 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1004659 | 孤儿节点: 1004659 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004659 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1004660 | 孤儿节点: 1004660 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004660 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1004661 | 孤儿节点: 1004661 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004661 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1004662 | 孤儿节点: 1004662 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004662 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1004663 | 孤儿节点: 1004663 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004663 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1004664 | 孤儿节点: 1004664 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004664 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1004665 | 孤儿节点: 1004665 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004665 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1004666 | 孤儿节点: 1004666 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004666 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1004667 | 孤儿节点: 1004667 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004667 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1004668 | 孤儿节点: 1004668 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004668 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1004669 | 孤儿节点: 1004669 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004669 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1004670 | 孤儿节点: 1004670 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004670 路径 src/zephyr/backtest/core/data_handler.py 未注册到目... |
| V-ORPHAN-1004671 | 孤儿节点: 1004671 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1004671 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1004673 | 孤儿节点: 1004673 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004673 路径 src/zephyr/backtest/core/matching_engine.py 未注... |
| V-ORPHAN-1004674 | 孤儿节点: 1004674 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004674 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1004675 | 孤儿节点: 1004675 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004675 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1004676 | 孤儿节点: 1004676 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004676 路径 src/zephyr/backtest/core/matching_logic.py 未注册... |
| V-ORPHAN-1004677 | 孤儿节点: 1004677 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004677 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1004678 | 孤儿节点: 1004678 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004678 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1004679 | 孤儿节点: 1004679 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004679 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1004680 | 孤儿节点: 1004680 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004680 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1004681 | 孤儿节点: 1004681 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004681 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1004682 | 孤儿节点: 1004682 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004682 路径 src/zephyr/backtest/core/portfolio.py 未注册到目录树 |
| V-ORPHAN-1004683 | 孤儿节点: 1004683 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004683 路径 src/zephyr/backtest/core/tick_replay.py 未注册到目录... |
| V-ORPHAN-1004687 | 孤儿节点: 1004687 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004687 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1004688 | 孤儿节点: 1004688 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004688 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1004689 | 孤儿节点: 1004689 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004689 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1004691 | 孤儿节点: 1004691 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004691 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1004692 | 孤儿节点: 1004692 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004692 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1004693 | 孤儿节点: 1004693 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004693 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1004694 | 孤儿节点: 1004694 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1004694 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1004695 | 孤儿节点: 1004695 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004695 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1004696 | 孤儿节点: 1004696 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004696 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1004697 | 孤儿节点: 1004697 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004697 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1004698 | 孤儿节点: 1004698 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004698 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1004699 | 孤儿节点: 1004699 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004699 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1004700 | 孤儿节点: 1004700 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004700 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1004701 | 孤儿节点: 1004701 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004701 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1004702 | 孤儿节点: 1004702 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004702 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1004703 | 孤儿节点: 1004703 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004703 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1004704 | 孤儿节点: 1004704 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004704 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1004705 | 孤儿节点: 1004705 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004705 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1004706 | 孤儿节点: 1004706 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004706 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1004707 | 孤儿节点: 1004707 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004707 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1004708 | 孤儿节点: 1004708 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004708 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1004709 | 孤儿节点: 1004709 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004709 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1004710 | 孤儿节点: 1004710 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004710 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1004711 | 孤儿节点: 1004711 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004711 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1004712 | 孤儿节点: 1004712 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004712 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1004713 | 孤儿节点: 1004713 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004713 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1004714 | 孤儿节点: 1004714 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004714 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1004715 | 孤儿节点: 1004715 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004715 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1004716 | 孤儿节点: 1004716 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004716 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1004717 | 孤儿节点: 1004717 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004717 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1004719 | 孤儿节点: 1004719 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004719 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1004720 | 孤儿节点: 1004720 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1004720 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1004721 | 孤儿节点: 1004721 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004721 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1004722 | 孤儿节点: 1004722 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004722 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1004723 | 孤儿节点: 1004723 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004723 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1004724 | 孤儿节点: 1004724 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004724 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1004725 | 孤儿节点: 1004725 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004725 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1004726 | 孤儿节点: 1004726 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1004726 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1004727 | 孤儿节点: 1004727 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004727 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1004728 | 孤儿节点: 1004728 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004728 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1004731 | 孤儿节点: 1004731 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004731 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1004732 | 孤儿节点: 1004732 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004732 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1004733 | 孤儿节点: 1004733 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004733 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1004734 | 孤儿节点: 1004734 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004734 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1004736 | 孤儿节点: 1004736 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004736 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1004737 | 孤儿节点: 1004737 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004737 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1004739 | 孤儿节点: 1004739 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004739 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1004740 | 孤儿节点: 1004740 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004740 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1004741 | 孤儿节点: 1004741 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004741 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1004742 | 孤儿节点: 1004742 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004742 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1004743 | 孤儿节点: 1004743 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004743 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1004744 | 孤儿节点: 1004744 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004744 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1004745 | 孤儿节点: 1004745 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1004745 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1004746 | 孤儿节点: 1004746 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004746 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1004747 | 孤儿节点: 1004747 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004747 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1004748 | 孤儿节点: 1004748 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004748 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1004749 | 孤儿节点: 1004749 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004749 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1004750 | 孤儿节点: 1004750 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004750 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-1004751 | 孤儿节点: 1004751 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004751 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1004752 | 孤儿节点: 1004752 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1004752 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1004753 | 孤儿节点: 1004753 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1004753 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1004754 | 孤儿节点: 1004754 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1004754 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1004755 | 孤儿节点: 1004755 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1004755 路径 src/zephyr/data_governance/core/__init__.py 未注... |
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
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1004614 -> 1005376 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1004820 -> 1005277 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1005520 -> 1006379 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOVERNANCE | error | gate | 层级违规: 1005698 -> 1005093 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | gate | 层级违规: 1005718 -> 1006408 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1005478 -> 1004843 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1005488 -> 1005832 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1005475 -> 1006346 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_TELEMETRY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_TELEMETRY | D_GOVERNANCE | error | gate | 层级违规: 1005755 -> 1005077 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | gate | 层级违规: 1005758 -> 1006346 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | gate | 层级违规: 1005859 -> 1005208 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOVERNANCE | error | gate | 层级违规: 1005805 -> 1005088 (L1_foundation -> L2_domain) |
| V-LAYER-D_REPORTING-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_REPORTING | D_TRADING | error | gate | 层级违规: 1005970 -> 1006935 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1006078 -> 1005277 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1005040 -> 1005313 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_TRADING | error | gate | 层级违规: 1006090 -> 1006485 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | gate | 层级违规: 1006403 -> 1004927 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1006376 -> 1005334 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | gate | 层级违规: 1006423 -> 1005929 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_SIMULATION | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_SIMULATION | error | gate | 层级违规: 1006423 -> 1006464 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1004534 | 孤儿节点: 1004534 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004536 | 孤儿节点: 1004536 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004537 | 孤儿节点: 1004537 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004538 | 孤儿节点: 1004538 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004539 | 孤儿节点: 1004539 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004540 | 孤儿节点: 1004540 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004541 | 孤儿节点: 1004541 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1004543 | 孤儿节点: 1004543 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1004596 | 孤儿节点: 1004596 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1004655 | 孤儿节点: 1004655 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004656 | 孤儿节点: 1004656 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1004657 | 孤儿节点: 1004657 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004658 | 孤儿节点: 1004658 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004659 | 孤儿节点: 1004659 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004660 | 孤儿节点: 1004660 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004661 | 孤儿节点: 1004661 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004662 | 孤儿节点: 1004662 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004663 | 孤儿节点: 1004663 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004664 | 孤儿节点: 1004664 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004665 | 孤儿节点: 1004665 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004666 | 孤儿节点: 1004666 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004667 | 孤儿节点: 1004667 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004668 | 孤儿节点: 1004668 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004669 | 孤儿节点: 1004669 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004670 | 孤儿节点: 1004670 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004671 | 孤儿节点: 1004671 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1004673 | 孤儿节点: 1004673 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004674 | 孤儿节点: 1004674 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004675 | 孤儿节点: 1004675 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004676 | 孤儿节点: 1004676 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004677 | 孤儿节点: 1004677 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004678 | 孤儿节点: 1004678 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004679 | 孤儿节点: 1004679 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004680 | 孤儿节点: 1004680 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004681 | 孤儿节点: 1004681 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004682 | 孤儿节点: 1004682 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004683 | 孤儿节点: 1004683 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004687 | 孤儿节点: 1004687 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004688 | 孤儿节点: 1004688 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004689 | 孤儿节点: 1004689 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004691 | 孤儿节点: 1004691 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004692 | 孤儿节点: 1004692 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004693 | 孤儿节点: 1004693 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004694 | 孤儿节点: 1004694 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1004695 | 孤儿节点: 1004695 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004696 | 孤儿节点: 1004696 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004697 | 孤儿节点: 1004697 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004698 | 孤儿节点: 1004698 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004699 | 孤儿节点: 1004699 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004700 | 孤儿节点: 1004700 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004701 | 孤儿节点: 1004701 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004702 | 孤儿节点: 1004702 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004703 | 孤儿节点: 1004703 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004704 | 孤儿节点: 1004704 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004705 | 孤儿节点: 1004705 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004706 | 孤儿节点: 1004706 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004707 | 孤儿节点: 1004707 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004708 | 孤儿节点: 1004708 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004709 | 孤儿节点: 1004709 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004710 | 孤儿节点: 1004710 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004711 | 孤儿节点: 1004711 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004712 | 孤儿节点: 1004712 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004713 | 孤儿节点: 1004713 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004714 | 孤儿节点: 1004714 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004715 | 孤儿节点: 1004715 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004716 | 孤儿节点: 1004716 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004717 | 孤儿节点: 1004717 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004719 | 孤儿节点: 1004719 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004720 | 孤儿节点: 1004720 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1004721 | 孤儿节点: 1004721 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004722 | 孤儿节点: 1004722 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004723 | 孤儿节点: 1004723 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004724 | 孤儿节点: 1004724 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004725 | 孤儿节点: 1004725 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004726 | 孤儿节点: 1004726 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1004727 | 孤儿节点: 1004727 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004728 | 孤儿节点: 1004728 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004731 | 孤儿节点: 1004731 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004732 | 孤儿节点: 1004732 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004733 | 孤儿节点: 1004733 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004734 | 孤儿节点: 1004734 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004736 | 孤儿节点: 1004736 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004737 | 孤儿节点: 1004737 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004739 | 孤儿节点: 1004739 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004740 | 孤儿节点: 1004740 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004741 | 孤儿节点: 1004741 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004742 | 孤儿节点: 1004742 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004743 | 孤儿节点: 1004743 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004744 | 孤儿节点: 1004744 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004745 | 孤儿节点: 1004745 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1004746 | 孤儿节点: 1004746 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004747 | 孤儿节点: 1004747 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004748 | 孤儿节点: 1004748 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004749 | 孤儿节点: 1004749 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004750 | 孤儿节点: 1004750 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004751 | 孤儿节点: 1004751 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004752 | 孤儿节点: 1004752 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1004753 | 孤儿节点: 1004753 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1004754 | 孤儿节点: 1004754 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1004755 | 孤儿节点: 1004755 | orphan_node | D_DATA_GOV |  | warn | open |
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
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INFRA_TELEMETRY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_TELEMETRY | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | open |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | open |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOVERNANCE | error | open |
| V-LAYER-D_REPORTING-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_REPORTING | D_TRADING | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_SECURITY-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_TRADING | error | open |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | open |
| V-LAYER-D_SHARED-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | open |
| V-LAYER-D_SHARED-D_SIMULATION | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_SIMULATION | error | open |
