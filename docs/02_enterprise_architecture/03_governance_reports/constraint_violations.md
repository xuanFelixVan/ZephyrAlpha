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
| V-ORPHAN-1611829 | 孤儿节点: 1611829 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611829 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1611830 | 孤儿节点: 1611830 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611830 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1611831 | 孤儿节点: 1611831 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611831 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1611832 | 孤儿节点: 1611832 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611832 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1611834 | 孤儿节点: 1611834 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611834 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1611835 | 孤儿节点: 1611835 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611835 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1611836 | 孤儿节点: 1611836 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1611836 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1611837 | 孤儿节点: 1611837 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1611837 路径 src/zephyr/autonomy_core/all_skill_modules.py ... |
| V-ORPHAN-1611839 | 孤儿节点: 1611839 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1611839 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1611890 | 孤儿节点: 1611890 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1611890 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1611902 | 孤儿节点: 1611902 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1611902 路径 src/zephyr/autonomy_core/skills/skill_context_... |
| V-ORPHAN-1611949 | 孤儿节点: 1611949 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611949 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1611950 | 孤儿节点: 1611950 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1611950 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1611951 | 孤儿节点: 1611951 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611951 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1611952 | 孤儿节点: 1611952 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611952 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1611953 | 孤儿节点: 1611953 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611953 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1611954 | 孤儿节点: 1611954 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611954 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1611955 | 孤儿节点: 1611955 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611955 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1611956 | 孤儿节点: 1611956 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611956 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1611957 | 孤儿节点: 1611957 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611957 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1611958 | 孤儿节点: 1611958 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611958 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1611959 | 孤儿节点: 1611959 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611959 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1611960 | 孤儿节点: 1611960 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611960 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1611961 | 孤儿节点: 1611961 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611961 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1611962 | 孤儿节点: 1611962 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611962 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1611963 | 孤儿节点: 1611963 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611963 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1611964 | 孤儿节点: 1611964 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1611964 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1611965 | 孤儿节点: 1611965 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611965 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1611969 | 孤儿节点: 1611969 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611969 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1611971 | 孤儿节点: 1611971 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611971 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1611972 | 孤儿节点: 1611972 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611972 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1611974 | 孤儿节点: 1611974 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611974 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1611976 | 孤儿节点: 1611976 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611976 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1611977 | 孤儿节点: 1611977 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611977 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1611979 | 孤儿节点: 1611979 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611979 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1611982 | 孤儿节点: 1611982 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611982 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1611983 | 孤儿节点: 1611983 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611983 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1611984 | 孤儿节点: 1611984 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611984 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1611986 | 孤儿节点: 1611986 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611986 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1611987 | 孤儿节点: 1611987 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611987 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1611988 | 孤儿节点: 1611988 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1611988 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1611989 | 孤儿节点: 1611989 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611989 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1611990 | 孤儿节点: 1611990 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611990 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1611991 | 孤儿节点: 1611991 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611991 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1611992 | 孤儿节点: 1611992 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611992 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1611993 | 孤儿节点: 1611993 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611993 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1611994 | 孤儿节点: 1611994 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611994 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1611995 | 孤儿节点: 1611995 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611995 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1611996 | 孤儿节点: 1611996 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611996 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1611997 | 孤儿节点: 1611997 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611997 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1611998 | 孤儿节点: 1611998 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611998 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1611999 | 孤儿节点: 1611999 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1611999 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1612000 | 孤儿节点: 1612000 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612000 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1612001 | 孤儿节点: 1612001 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612001 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1612002 | 孤儿节点: 1612002 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612002 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1612003 | 孤儿节点: 1612003 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612003 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1612004 | 孤儿节点: 1612004 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612004 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1612005 | 孤儿节点: 1612005 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612005 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1612006 | 孤儿节点: 1612006 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612006 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1612007 | 孤儿节点: 1612007 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612007 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1612008 | 孤儿节点: 1612008 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612008 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1612009 | 孤儿节点: 1612009 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612009 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1612010 | 孤儿节点: 1612010 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612010 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1612011 | 孤儿节点: 1612011 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612011 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1612012 | 孤儿节点: 1612012 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1612012 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1612013 | 孤儿节点: 1612013 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612013 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1612015 | 孤儿节点: 1612015 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612015 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1612016 | 孤儿节点: 1612016 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612016 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1612017 | 孤儿节点: 1612017 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612017 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1612018 | 孤儿节点: 1612018 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612018 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1612019 | 孤儿节点: 1612019 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1612019 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1612020 | 孤儿节点: 1612020 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612020 路径 src/zephyr/data/policy_registry.py 未注册到目录树 |
| V-ORPHAN-1612021 | 孤儿节点: 1612021 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612021 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1612023 | 孤儿节点: 1612023 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612023 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1612024 | 孤儿节点: 1612024 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612024 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1612025 | 孤儿节点: 1612025 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612025 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1612026 | 孤儿节点: 1612026 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612026 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1612027 | 孤儿节点: 1612027 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612027 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1612028 | 孤儿节点: 1612028 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612028 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1612029 | 孤儿节点: 1612029 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612029 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-1612031 | 孤儿节点: 1612031 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612031 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1612032 | 孤儿节点: 1612032 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612032 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1612033 | 孤儿节点: 1612033 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612033 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1612034 | 孤儿节点: 1612034 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612034 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1612035 | 孤儿节点: 1612035 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612035 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1612036 | 孤儿节点: 1612036 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612036 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1612037 | 孤儿节点: 1612037 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612037 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1612038 | 孤儿节点: 1612038 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612038 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1612039 | 孤儿节点: 1612039 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612039 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1612040 | 孤儿节点: 1612040 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1612040 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1612041 | 孤儿节点: 1612041 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612041 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1612042 | 孤儿节点: 1612042 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612042 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1612043 | 孤儿节点: 1612043 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612043 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1612044 | 孤儿节点: 1612044 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612044 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-1612045 | 孤儿节点: 1612045 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612045 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1612046 | 孤儿节点: 1612046 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1612046 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1612047 | 孤儿节点: 1612047 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1612047 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1612048 | 孤儿节点: 1612048 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1612048 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1612049 | 孤儿节点: 1612049 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1612049 路径 src/zephyr/data_governance/core/__init__.py 未注... |
| V-ORPHAN-1612050 | 孤儿节点: 1612050 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1612050 路径 src/zephyr/data_governance/infrastructure/__in... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 497 超过上限 1... |
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
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 497 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1611938 -> 1612168 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1611910 -> 1612683 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1611858 -> 1613160 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1612115 -> 1612588 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1612128 -> 1614220 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1612871 -> 1612454 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1612879 -> 1613705 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1612910 -> 1612742 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1612790 -> 1613115 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1612963 -> 1613695 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1611828 -> 1614107 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1612475 -> 1612443 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1612346 -> 1612621 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1611829 | 孤儿节点: 1611829 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611830 | 孤儿节点: 1611830 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611831 | 孤儿节点: 1611831 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611832 | 孤儿节点: 1611832 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611834 | 孤儿节点: 1611834 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611835 | 孤儿节点: 1611835 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611836 | 孤儿节点: 1611836 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1611837 | 孤儿节点: 1611837 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1611839 | 孤儿节点: 1611839 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1611890 | 孤儿节点: 1611890 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1611902 | 孤儿节点: 1611902 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1611949 | 孤儿节点: 1611949 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611950 | 孤儿节点: 1611950 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1611951 | 孤儿节点: 1611951 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611952 | 孤儿节点: 1611952 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611953 | 孤儿节点: 1611953 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611954 | 孤儿节点: 1611954 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611955 | 孤儿节点: 1611955 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611956 | 孤儿节点: 1611956 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611957 | 孤儿节点: 1611957 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611958 | 孤儿节点: 1611958 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611959 | 孤儿节点: 1611959 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611960 | 孤儿节点: 1611960 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611961 | 孤儿节点: 1611961 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611962 | 孤儿节点: 1611962 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611963 | 孤儿节点: 1611963 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611964 | 孤儿节点: 1611964 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1611965 | 孤儿节点: 1611965 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611969 | 孤儿节点: 1611969 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611971 | 孤儿节点: 1611971 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611972 | 孤儿节点: 1611972 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611974 | 孤儿节点: 1611974 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611976 | 孤儿节点: 1611976 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611977 | 孤儿节点: 1611977 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611979 | 孤儿节点: 1611979 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611982 | 孤儿节点: 1611982 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611983 | 孤儿节点: 1611983 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611984 | 孤儿节点: 1611984 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611986 | 孤儿节点: 1611986 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611987 | 孤儿节点: 1611987 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611988 | 孤儿节点: 1611988 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1611989 | 孤儿节点: 1611989 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611990 | 孤儿节点: 1611990 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611991 | 孤儿节点: 1611991 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611992 | 孤儿节点: 1611992 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611993 | 孤儿节点: 1611993 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611994 | 孤儿节点: 1611994 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611995 | 孤儿节点: 1611995 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611996 | 孤儿节点: 1611996 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611997 | 孤儿节点: 1611997 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611998 | 孤儿节点: 1611998 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1611999 | 孤儿节点: 1611999 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612000 | 孤儿节点: 1612000 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612001 | 孤儿节点: 1612001 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612002 | 孤儿节点: 1612002 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612003 | 孤儿节点: 1612003 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612004 | 孤儿节点: 1612004 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612005 | 孤儿节点: 1612005 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612006 | 孤儿节点: 1612006 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612007 | 孤儿节点: 1612007 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612008 | 孤儿节点: 1612008 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612009 | 孤儿节点: 1612009 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612010 | 孤儿节点: 1612010 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612011 | 孤儿节点: 1612011 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612012 | 孤儿节点: 1612012 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1612013 | 孤儿节点: 1612013 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612015 | 孤儿节点: 1612015 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612016 | 孤儿节点: 1612016 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612017 | 孤儿节点: 1612017 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612018 | 孤儿节点: 1612018 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612019 | 孤儿节点: 1612019 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1612020 | 孤儿节点: 1612020 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612021 | 孤儿节点: 1612021 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612023 | 孤儿节点: 1612023 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612024 | 孤儿节点: 1612024 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612025 | 孤儿节点: 1612025 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612026 | 孤儿节点: 1612026 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612027 | 孤儿节点: 1612027 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612028 | 孤儿节点: 1612028 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612029 | 孤儿节点: 1612029 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612031 | 孤儿节点: 1612031 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612032 | 孤儿节点: 1612032 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612033 | 孤儿节点: 1612033 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612034 | 孤儿节点: 1612034 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612035 | 孤儿节点: 1612035 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612036 | 孤儿节点: 1612036 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612037 | 孤儿节点: 1612037 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612038 | 孤儿节点: 1612038 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612039 | 孤儿节点: 1612039 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612040 | 孤儿节点: 1612040 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1612041 | 孤儿节点: 1612041 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612042 | 孤儿节点: 1612042 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612043 | 孤儿节点: 1612043 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612044 | 孤儿节点: 1612044 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612045 | 孤儿节点: 1612045 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612046 | 孤儿节点: 1612046 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1612047 | 孤儿节点: 1612047 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1612048 | 孤儿节点: 1612048 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1612049 | 孤儿节点: 1612049 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1612050 | 孤儿节点: 1612050 | orphan_node | D_DATA_GOV |  | warn | open |
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
