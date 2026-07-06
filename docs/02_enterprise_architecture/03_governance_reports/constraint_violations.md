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
| 约束总数 | 164 |
| Open（未解决） | 164 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 62 |
| hard | 2 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 2 |
| cross_domain_violation | 35 |
| hard_limit_exceeded | 2 |
| layer_violation | 24 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-949906 | 孤儿节点: 949906 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949906 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-949907 | 孤儿节点: 949907 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949907 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-949908 | 孤儿节点: 949908 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949908 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-949909 | 孤儿节点: 949909 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949909 路径 src/zephyr/alt_data/infrastructure/__init__.py ... |
| V-ORPHAN-949910 | 孤儿节点: 949910 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949910 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-949911 | 孤儿节点: 949911 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949911 路径 src/zephyr/alt_data/_extensions/__init__.py 未注册... |
| V-ORPHAN-949912 | 孤儿节点: 949912 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 949912 路径 src/zephyr/alt_data/services/__init__.py 未注册到目录... |
| V-ORPHAN-949914 | 孤儿节点: 949914 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 949914 路径 src/zephyr/autonomy_core/file_autoregister.py 未... |
| V-ORPHAN-949916 | 孤儿节点: 949916 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 949916 路径 src/zephyr/autonomy_core/phase_planner.py 未注册到目... |
| V-ORPHAN-949968 | 孤儿节点: 949968 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 949968 路径 src/zephyr/autonomy_core/integration/__init__.p... |
| V-ORPHAN-950026 | 孤儿节点: 950026 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950026 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-950027 | 孤儿节点: 950027 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 950027 路径 src/zephyr/autonomy_core/skills/__init__.py 未注册... |
| V-ORPHAN-950028 | 孤儿节点: 950028 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950028 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到目... |
| V-ORPHAN-950029 | 孤儿节点: 950029 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950029 路径 src/zephyr/autonomy_perm/infrastructure/__init_... |
| V-ORPHAN-950030 | 孤儿节点: 950030 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950030 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目录... |
| V-ORPHAN-950031 | 孤儿节点: 950031 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950031 路径 src/zephyr/autonomy_perm/models/__init__.py 未注册... |
| V-ORPHAN-950032 | 孤儿节点: 950032 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950032 路径 src/zephyr/autonomy_perm/red_blue_validator/att... |
| V-ORPHAN-950033 | 孤儿节点: 950033 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950033 路径 src/zephyr/autonomy_perm/red_blue_validator/byp... |
| V-ORPHAN-950034 | 孤儿节点: 950034 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950034 路径 src/zephyr/autonomy_perm/red_blue_validator/gam... |
| V-ORPHAN-950035 | 孤儿节点: 950035 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950035 路径 src/zephyr/autonomy_perm/red_blue_validator/con... |
| V-ORPHAN-950036 | 孤儿节点: 950036 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950036 路径 src/zephyr/autonomy_perm/red_blue_validator/con... |
| V-ORPHAN-950037 | 孤儿节点: 950037 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950037 路径 src/zephyr/autonomy_perm/red_blue_validator/def... |
| V-ORPHAN-950038 | 孤儿节点: 950038 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950038 路径 src/zephyr/autonomy_perm/red_blue_validator/__i... |
| V-ORPHAN-950039 | 孤儿节点: 950039 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950039 路径 src/zephyr/autonomy_perm/services/__init__.py 未... |
| V-ORPHAN-950040 | 孤儿节点: 950040 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 950040 路径 src/zephyr/autonomy_perm/_extensions/__init__.p... |
| V-ORPHAN-950041 | 孤儿节点: 950041 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950041 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-950042 | 孤儿节点: 950042 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950042 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-950043 | 孤儿节点: 950043 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950043 路径 src/zephyr/backtest/core/matching_engine.py 未注册... |
| V-ORPHAN-950045 | 孤儿节点: 950045 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950045 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-950046 | 孤儿节点: 950046 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950046 路径 src/zephyr/backtest/core/data_handler.py 未注册到目录... |
| V-ORPHAN-950047 | 孤儿节点: 950047 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950047 路径 src/zephyr/backtest/core/matching_logic.py 未注册到... |
| V-ORPHAN-950048 | 孤儿节点: 950048 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950048 路径 src/zephyr/backtest/core/decision_gate.py 未注册到目... |
| V-ORPHAN-950049 | 孤儿节点: 950049 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950049 路径 src/zephyr/backtest/core/overfitting_detector.p... |
| V-ORPHAN-950050 | 孤儿节点: 950050 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950050 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录树 |
| V-ORPHAN-950051 | 孤儿节点: 950051 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950051 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-950052 | 孤儿节点: 950052 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950052 路径 src/zephyr/backtest/core/tick_replay.py 未注册到目录树 |
| V-ORPHAN-950053 | 孤儿节点: 950053 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950053 路径 src/zephyr/backtest/core/portfolio.py 未注册到目录树 |
| V-ORPHAN-950054 | 孤儿节点: 950054 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950054 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目录... |
| V-ORPHAN-950058 | 孤儿节点: 950058 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950058 路径 src/zephyr/backtest/infrastructure/__init__.py ... |
| V-ORPHAN-950059 | 孤儿节点: 950059 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950059 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-950060 | 孤儿节点: 950060 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950060 路径 src/zephyr/backtest/io/backtest_result_sink.py ... |
| V-ORPHAN-950062 | 孤儿节点: 950062 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950062 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-950063 | 孤儿节点: 950063 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950063 路径 src/zephyr/backtest/io/result_repository.py 未注册... |
| V-ORPHAN-950064 | 孤儿节点: 950064 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950064 路径 src/zephyr/backtest/services/__init__.py 未注册到目录... |
| V-ORPHAN-950065 | 孤儿节点: 950065 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950065 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-950066 | 孤儿节点: 950066 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 950066 路径 src/zephyr/backtest/_extensions/__init__.py 未注册... |
| V-ORPHAN-950067 | 孤儿节点: 950067 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950067 路径 src/zephyr/compliance/financial_compliance.py 未... |
| V-ORPHAN-950068 | 孤儿节点: 950068 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950068 路径 src/zephyr/compliance/artifact_scanner.py 未注册到目... |
| V-ORPHAN-950069 | 孤儿节点: 950069 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950069 路径 src/zephyr/compliance/compliance_manager.py 未注册... |
| V-ORPHAN-950070 | 孤儿节点: 950070 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950070 路径 src/zephyr/compliance/default_security_gateway.... |
| V-ORPHAN-950071 | 孤儿节点: 950071 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950071 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-950072 | 孤儿节点: 950072 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950072 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-950073 | 孤儿节点: 950073 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950073 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-950074 | 孤儿节点: 950074 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950074 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-950075 | 孤儿节点: 950075 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950075 路径 src/zephyr/compliance/security_gateway_base.py ... |
| V-ORPHAN-950076 | 孤儿节点: 950076 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950076 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-950077 | 孤儿节点: 950077 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950077 路径 src/zephyr/compliance/audit_orchestrator/__init... |
| V-ORPHAN-950078 | 孤儿节点: 950078 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950078 路径 src/zephyr/compliance/audit_trail/__init__.py 未... |
| V-ORPHAN-950079 | 孤儿节点: 950079 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950079 路径 src/zephyr/compliance/audit_trail/bridges/__ini... |
| V-ORPHAN-950080 | 孤儿节点: 950080 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950080 路径 src/zephyr/compliance/behavioral_admission/__in... |
| V-ORPHAN-950081 | 孤儿节点: 950081 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950081 路径 src/zephyr/compliance/behavioral_auditor/__init... |
| V-ORPHAN-950082 | 孤儿节点: 950082 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950082 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-950083 | 孤儿节点: 950083 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950083 路径 src/zephyr/compliance/compliance_gate_a6/__init... |
| V-ORPHAN-950084 | 孤儿节点: 950084 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950084 路径 src/zephyr/compliance/infrastructure/__init__.p... |
| V-ORPHAN-950085 | 孤儿节点: 950085 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950085 路径 src/zephyr/compliance/implementations/__init__.... |
| V-ORPHAN-950086 | 孤儿节点: 950086 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950086 路径 src/zephyr/compliance/services/__init__.py 未注册到... |
| V-ORPHAN-950087 | 孤儿节点: 950087 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950087 路径 src/zephyr/compliance/models/__init__.py 未注册到目录... |
| V-ORPHAN-950088 | 孤儿节点: 950088 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950088 路径 src/zephyr/compliance/_extensions/__init__.py 未... |
| V-ORPHAN-950090 | 孤儿节点: 950090 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 950090 路径 src/zephyr/compliance/zero_knowledge_audit_stub... |
| V-ORPHAN-950091 | 孤儿节点: 950091 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950091 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录树 |
| V-ORPHAN-950092 | 孤儿节点: 950092 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950092 路径 src/zephyr/cross_asset/infrastructure/__init__.... |
| V-ORPHAN-950093 | 孤儿节点: 950093 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950093 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-950094 | 孤儿节点: 950094 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950094 路径 src/zephyr/cross_asset/models/__init__.py 未注册到目... |
| V-ORPHAN-950095 | 孤儿节点: 950095 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950095 路径 src/zephyr/cross_asset/_extensions/__init__.py ... |
| V-ORPHAN-950096 | 孤儿节点: 950096 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950096 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-950097 | 孤儿节点: 950097 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 950097 路径 src/zephyr/cross_asset/services/__init__.py 未注册... |
| V-ORPHAN-950098 | 孤儿节点: 950098 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950098 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-950099 | 孤儿节点: 950099 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950099 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-950102 | 孤儿节点: 950102 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950102 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-950103 | 孤儿节点: 950103 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950103 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-950105 | 孤儿节点: 950105 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950105 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-950107 | 孤儿节点: 950107 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950107 路径 src/zephyr/data/implementations/akshare_provide... |
| V-ORPHAN-950108 | 孤儿节点: 950108 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950108 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-950109 | 孤儿节点: 950109 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950109 路径 src/zephyr/data/implementations/baostock_provid... |
| V-ORPHAN-950110 | 孤儿节点: 950110 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950110 路径 src/zephyr/data/implementations/ifind_provider.... |
| V-ORPHAN-950111 | 孤儿节点: 950111 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950111 路径 src/zephyr/data/implementations/miniqmt_provide... |
| V-ORPHAN-950112 | 孤儿节点: 950112 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950112 路径 src/zephyr/data/implementations/tickflow_provid... |
| V-ORPHAN-950113 | 孤儿节点: 950113 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950113 路径 src/zephyr/data/implementations/tdx_provider.py... |
| V-ORPHAN-950114 | 孤儿节点: 950114 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950114 路径 src/zephyr/data/implementations/rss_provider.py... |
| V-ORPHAN-950115 | 孤儿节点: 950115 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950115 路径 src/zephyr/data/implementations/tushare_provide... |
| V-ORPHAN-950116 | 孤儿节点: 950116 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 950116 路径 src/zephyr/data/implementations/__init__.py 未注册... |
| V-ORPHAN-950117 | 孤儿节点: 950117 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950117 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-950118 | 孤儿节点: 950118 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950118 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-950119 | 孤儿节点: 950119 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950119 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-950120 | 孤儿节点: 950120 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950120 路径 src/zephyr/data_eng/infrastructure/__init__.py ... |
| V-ORPHAN-950121 | 孤儿节点: 950121 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950121 路径 src/zephyr/data_eng/services/__init__.py 未注册到目录... |
| V-ORPHAN-950122 | 孤儿节点: 950122 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950122 路径 src/zephyr/data_eng/_extensions/__init__.py 未注册... |
| V-ORPHAN-950123 | 孤儿节点: 950123 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 950123 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-950124 | 孤儿节点: 950124 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 950124 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-950125 | 孤儿节点: 950125 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 950125 路径 src/zephyr/data_governance/api/__init__.py 未注册到... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 476 超过上限 1... |
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
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTEGRATION |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_TRADING |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOVERNANCE |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_ENFORCEMENT |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 476 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 949986 -> 950744 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 950191 -> 950647 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 950878 -> 950251 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 950915 -> 951751 (L0_infrastructure -> L1_foundation) |
| V-LAYER-D_INFRA_RECOVERY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOVERNANCE | error | gate | 层级违规: 951079 -> 950620 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | gate | 层级违规: 951102 -> 951715 (L0_infrastructure -> L1_foundation) |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 950848 -> 950214 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 950850 -> 951204 (L0_infrastructure -> L1_foundation) |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 950852 -> 951715 (L0_infrastructure -> L1_foundation) |
| V-LAYER-D_INFRA_TELEMETRY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_TELEMETRY | D_GOVERNANCE | error | gate | 层级违规: 951119 -> 950449 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | gate | 层级违规: 951121 -> 951715 (L0_infrastructure -> L1_foundation) |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | gate | 层级违规: 951233 -> 950577 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_INTELLIGENCE | error | gate | 层级违规: 951148 -> 951271 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOVERNANCE | error | gate | 层级违规: 951176 -> 950577 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 951184 -> 950701 (L1_foundation -> L2_domain) |
| V-LAYER-D_REPORTING-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_REPORTING | D_TRADING | error | gate | 层级违规: 951335 -> 952303 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 951490 -> 950262 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 951490 -> 950744 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_INTELLIGENCE | error | gate | 层级违规: 951455 -> 951243 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_TRADING | error | gate | 层级违规: 951457 -> 951914 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | gate | 层级违规: 951775 -> 950297 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_ENFORCEMENT | error | gate | 层级违规: 951746 -> 950701 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | gate | 层级违规: 951794 -> 951296 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_SIMULATION | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_SIMULATION | error | gate | 层级违规: 951794 -> 951837 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-949906 | 孤儿节点: 949906 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949907 | 孤儿节点: 949907 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949908 | 孤儿节点: 949908 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949909 | 孤儿节点: 949909 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949910 | 孤儿节点: 949910 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949911 | 孤儿节点: 949911 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949912 | 孤儿节点: 949912 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-949914 | 孤儿节点: 949914 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-949916 | 孤儿节点: 949916 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-949968 | 孤儿节点: 949968 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-950026 | 孤儿节点: 950026 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950027 | 孤儿节点: 950027 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-950028 | 孤儿节点: 950028 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950029 | 孤儿节点: 950029 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950030 | 孤儿节点: 950030 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950031 | 孤儿节点: 950031 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950032 | 孤儿节点: 950032 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950033 | 孤儿节点: 950033 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950034 | 孤儿节点: 950034 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950035 | 孤儿节点: 950035 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950036 | 孤儿节点: 950036 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950037 | 孤儿节点: 950037 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950038 | 孤儿节点: 950038 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950039 | 孤儿节点: 950039 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950040 | 孤儿节点: 950040 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-950041 | 孤儿节点: 950041 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950042 | 孤儿节点: 950042 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950043 | 孤儿节点: 950043 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950045 | 孤儿节点: 950045 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950046 | 孤儿节点: 950046 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950047 | 孤儿节点: 950047 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950048 | 孤儿节点: 950048 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950049 | 孤儿节点: 950049 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950050 | 孤儿节点: 950050 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950051 | 孤儿节点: 950051 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950052 | 孤儿节点: 950052 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950053 | 孤儿节点: 950053 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950054 | 孤儿节点: 950054 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950058 | 孤儿节点: 950058 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950059 | 孤儿节点: 950059 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950060 | 孤儿节点: 950060 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950062 | 孤儿节点: 950062 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950063 | 孤儿节点: 950063 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950064 | 孤儿节点: 950064 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950065 | 孤儿节点: 950065 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950066 | 孤儿节点: 950066 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-950067 | 孤儿节点: 950067 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950068 | 孤儿节点: 950068 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950069 | 孤儿节点: 950069 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950070 | 孤儿节点: 950070 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950071 | 孤儿节点: 950071 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950072 | 孤儿节点: 950072 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950073 | 孤儿节点: 950073 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950074 | 孤儿节点: 950074 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950075 | 孤儿节点: 950075 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950076 | 孤儿节点: 950076 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950077 | 孤儿节点: 950077 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950078 | 孤儿节点: 950078 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950079 | 孤儿节点: 950079 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950080 | 孤儿节点: 950080 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950081 | 孤儿节点: 950081 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950082 | 孤儿节点: 950082 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950083 | 孤儿节点: 950083 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950084 | 孤儿节点: 950084 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950085 | 孤儿节点: 950085 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950086 | 孤儿节点: 950086 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950087 | 孤儿节点: 950087 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950088 | 孤儿节点: 950088 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950090 | 孤儿节点: 950090 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-950091 | 孤儿节点: 950091 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950092 | 孤儿节点: 950092 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950093 | 孤儿节点: 950093 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950094 | 孤儿节点: 950094 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950095 | 孤儿节点: 950095 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950096 | 孤儿节点: 950096 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950097 | 孤儿节点: 950097 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-950098 | 孤儿节点: 950098 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950099 | 孤儿节点: 950099 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950102 | 孤儿节点: 950102 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950103 | 孤儿节点: 950103 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950105 | 孤儿节点: 950105 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950107 | 孤儿节点: 950107 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950108 | 孤儿节点: 950108 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950109 | 孤儿节点: 950109 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950110 | 孤儿节点: 950110 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950111 | 孤儿节点: 950111 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950112 | 孤儿节点: 950112 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950113 | 孤儿节点: 950113 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950114 | 孤儿节点: 950114 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950115 | 孤儿节点: 950115 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950116 | 孤儿节点: 950116 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-950117 | 孤儿节点: 950117 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950118 | 孤儿节点: 950118 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950119 | 孤儿节点: 950119 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950120 | 孤儿节点: 950120 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950121 | 孤儿节点: 950121 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950122 | 孤儿节点: 950122 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950123 | 孤儿节点: 950123 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-950124 | 孤儿节点: 950124 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-950125 | 孤儿节点: 950125 | orphan_node | D_DATA_GOV |  | warn | open |
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
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | open |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INFRA_TELEMETRY-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_TELEMETRY | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | open |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | open |
| V-LAYER-D_INTEGRATION-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_INTELLIGENCE | error | open |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOVERNANCE | error | open |
| V-LAYER-D_INTEGRATION_GATEWAY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION_GATEWAY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_REPORTING-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_REPORTING | D_TRADING | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_SECURITY-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_INTELLIGENCE | error | open |
| V-LAYER-D_SECURITY-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_TRADING | error | open |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | open |
| V-LAYER-D_SHARED-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | open |
| V-LAYER-D_SHARED-D_SIMULATION | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_SIMULATION | error | open |
