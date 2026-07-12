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
| error | 59 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| cross_domain_violation | 36 |
| layer_violation | 22 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-2203921 | 孤儿节点: 2203921 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203921 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-2203922 | 孤儿节点: 2203922 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203922 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-2203923 | 孤儿节点: 2203923 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203923 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2203924 | 孤儿节点: 2203924 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203924 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2203925 | 孤儿节点: 2203925 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203925 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2203926 | 孤儿节点: 2203926 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203926 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-2203927 | 孤儿节点: 2203927 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2203927 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-2203940 | 孤儿节点: 2203940 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2203940 路径 src/zephyr/autonomy_core/trigger_router.py 未注册... |
| V-ORPHAN-2203981 | 孤儿节点: 2203981 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2203981 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-2204011 | 孤儿节点: 2204011 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2204011 路径 src/zephyr/autonomy_core/skills/skill_knowledg... |
| V-ORPHAN-2204041 | 孤儿节点: 2204041 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2204041 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-2204042 | 孤儿节点: 2204042 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204042 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-2204043 | 孤儿节点: 2204043 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204043 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-2204044 | 孤儿节点: 2204044 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204044 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-2204045 | 孤儿节点: 2204045 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204045 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-2204046 | 孤儿节点: 2204046 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204046 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-2204047 | 孤儿节点: 2204047 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204047 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2204048 | 孤儿节点: 2204048 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204048 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-2204049 | 孤儿节点: 2204049 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204049 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-2204050 | 孤儿节点: 2204050 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204050 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-2204051 | 孤儿节点: 2204051 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204051 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2204052 | 孤儿节点: 2204052 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204052 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-2204053 | 孤儿节点: 2204053 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204053 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-2204054 | 孤儿节点: 2204054 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204054 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-2204055 | 孤儿节点: 2204055 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2204055 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-2204056 | 孤儿节点: 2204056 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204056 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2204057 | 孤儿节点: 2204057 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204057 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-2204058 | 孤儿节点: 2204058 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204058 路径 src/zephyr/backtest/core/engine_base.py 未注册到目录... |
| V-ORPHAN-2204059 | 孤儿节点: 2204059 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204059 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-2204063 | 孤儿节点: 2204063 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204063 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-2204064 | 孤儿节点: 2204064 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204064 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-2204067 | 孤儿节点: 2204067 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204067 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-2204068 | 孤儿节点: 2204068 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204068 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-2204070 | 孤儿节点: 2204070 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204070 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2204073 | 孤儿节点: 2204073 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204073 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-2204074 | 孤儿节点: 2204074 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204074 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-2204075 | 孤儿节点: 2204075 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204075 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-2204077 | 孤儿节点: 2204077 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204077 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-2204078 | 孤儿节点: 2204078 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204078 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2204079 | 孤儿节点: 2204079 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204079 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-2204080 | 孤儿节点: 2204080 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204080 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-2204081 | 孤儿节点: 2204081 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204081 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-2204082 | 孤儿节点: 2204082 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204082 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-2204083 | 孤儿节点: 2204083 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204083 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-2204084 | 孤儿节点: 2204084 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2204084 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-2204085 | 孤儿节点: 2204085 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204085 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-2204086 | 孤儿节点: 2204086 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204086 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-2204087 | 孤儿节点: 2204087 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204087 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-2204088 | 孤儿节点: 2204088 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204088 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-2204089 | 孤儿节点: 2204089 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204089 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-2204090 | 孤儿节点: 2204090 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204090 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2204091 | 孤儿节点: 2204091 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204091 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-2204092 | 孤儿节点: 2204092 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204092 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-2204093 | 孤儿节点: 2204093 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204093 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-2204094 | 孤儿节点: 2204094 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204094 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-2204095 | 孤儿节点: 2204095 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204095 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-2204096 | 孤儿节点: 2204096 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204096 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-2204097 | 孤儿节点: 2204097 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204097 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-2204098 | 孤儿节点: 2204098 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204098 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-2204099 | 孤儿节点: 2204099 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204099 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2204100 | 孤儿节点: 2204100 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204100 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-2204101 | 孤儿节点: 2204101 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204101 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-2204102 | 孤儿节点: 2204102 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204102 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-2204103 | 孤儿节点: 2204103 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204103 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-2204104 | 孤儿节点: 2204104 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2204104 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-2204106 | 孤儿节点: 2204106 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204106 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-2204107 | 孤儿节点: 2204107 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204107 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2204108 | 孤儿节点: 2204108 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204108 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-2204109 | 孤儿节点: 2204109 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204109 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-2204110 | 孤儿节点: 2204110 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204110 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-2204111 | 孤儿节点: 2204111 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2204111 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-2204112 | 孤儿节点: 2204112 | orphan_node | D_DATA |  | warn | advisory | 节点 2204112 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-2204113 | 孤儿节点: 2204113 | orphan_node | D_DATA |  | warn | advisory | 节点 2204113 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-2204114 | 孤儿节点: 2204114 | orphan_node | D_DATA |  | warn | advisory | 节点 2204114 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-2204115 | 孤儿节点: 2204115 | orphan_node | D_DATA |  | warn | advisory | 节点 2204115 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-2204118 | 孤儿节点: 2204118 | orphan_node | D_DATA |  | warn | advisory | 节点 2204118 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-2204119 | 孤儿节点: 2204119 | orphan_node | D_DATA |  | warn | advisory | 节点 2204119 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-2204120 | 孤儿节点: 2204120 | orphan_node | D_DATA |  | warn | advisory | 节点 2204120 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-2204121 | 孤儿节点: 2204121 | orphan_node | D_DATA |  | warn | advisory | 节点 2204121 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-2204122 | 孤儿节点: 2204122 | orphan_node | D_DATA |  | warn | advisory | 节点 2204122 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-2204123 | 孤儿节点: 2204123 | orphan_node | D_DATA |  | warn | advisory | 节点 2204123 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-2204125 | 孤儿节点: 2204125 | orphan_node | D_DATA |  | warn | advisory | 节点 2204125 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-2204126 | 孤儿节点: 2204126 | orphan_node | D_DATA |  | warn | advisory | 节点 2204126 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-2204128 | 孤儿节点: 2204128 | orphan_node | D_DATA |  | warn | advisory | 节点 2204128 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-2204129 | 孤儿节点: 2204129 | orphan_node | D_DATA |  | warn | advisory | 节点 2204129 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-2204130 | 孤儿节点: 2204130 | orphan_node | D_DATA |  | warn | advisory | 节点 2204130 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-2204131 | 孤儿节点: 2204131 | orphan_node | D_DATA |  | warn | advisory | 节点 2204131 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-2204132 | 孤儿节点: 2204132 | orphan_node | D_DATA |  | warn | advisory | 节点 2204132 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-2204133 | 孤儿节点: 2204133 | orphan_node | D_DATA |  | warn | advisory | 节点 2204133 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-2204134 | 孤儿节点: 2204134 | orphan_node | D_DATA |  | warn | advisory | 节点 2204134 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-2204135 | 孤儿节点: 2204135 | orphan_node | D_DATA |  | warn | advisory | 节点 2204135 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-2204136 | 孤儿节点: 2204136 | orphan_node | D_DATA |  | warn | advisory | 节点 2204136 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-2204137 | 孤儿节点: 2204137 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204137 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-2204138 | 孤儿节点: 2204138 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204138 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-2204139 | 孤儿节点: 2204139 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204139 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2204140 | 孤儿节点: 2204140 | orphan_node | D_DATA |  | warn | advisory | 节点 2204140 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-2204141 | 孤儿节点: 2204141 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204141 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2204142 | 孤儿节点: 2204142 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204142 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2204143 | 孤儿节点: 2204143 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204143 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-2204144 | 孤儿节点: 2204144 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2204144 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_AUDIT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_AUDIT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_AUDIT |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_KB | 跨域违规: D_AUTONOMY_CORE -> D_GOV_KB | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_KB | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_KB |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_RULE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_RULE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_RULE |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTELLIGENCE |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SECURITY |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_BACKTEST -> D_GOVERNANCE |
| V-CROSS-D_COMPLIANCE-D_GOVERNANCE | 跨域违规: D_COMPLIANCE -> D_GOVERNANCE | cross_domain_violation | D_COMPLIANCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOVERNANCE |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_AUDIT |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_DRIFT |
| V-CROSS-D_COMPLIANCE-D_GOV_ENFORCEMENT | 跨域违规: D_COMPLIANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_COMPLIANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_COMPLIANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_COMPLIANCE-D_INFRA_RUNTIME | 跨域违规: D_COMPLIANCE -> D_INFRA_RUNTIME | cross_domain_violation | D_COMPLIANCE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_INFRA_RUNTIME |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_SECURITY |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_DATA -> D_GOV_ENFORCEMENT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_EX_CORE -> D_INFRASTRUCTURE |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_SIGLEGACY | 跨域违规: D_FACTOR -> D_SIGLEGACY | cross_domain_violation | D_FACTOR | D_SIGLEGACY | error | gate | 跨域依赖未声明: D_FACTOR -> D_SIGLEGACY |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOVERNANCE |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_DRIFT |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RECOVERY | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INTEGRATION |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_ORCHESTRATOR |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SECURITY |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SHARED |
| V-CROSS-D_GOVERNANCE-D_FEEDBACK_LOOP | 跨域违规: D_GOVERNANCE -> D_FEEDBACK_LOOP | cross_domain_violation | D_GOVERNANCE | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_FEEDBACK_LOOP |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 2204029 -> 2204893 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_KB | error | gate | 层级违规: 2203951 -> 2205139 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 2204003 -> 2205116 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 2203951 -> 2205558 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 2204494 -> 2204893 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 2204518 -> 2204335 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 2204226 -> 2204980 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 2204549 -> 2204797 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 2204561 -> 2206285 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 层级违规: 2205034 -> 2204568 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2205036 -> 2205074 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 层级违规: 2204821 -> 2204727 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 层级违规: 2204832 -> 2204947 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2204830 -> 2205090 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | gate | 层级违规: 2204714 -> 2205145 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_RULE | error | gate | 层级违规: 2204714 -> 2205099 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 层级违规: 2203920 -> 2204517 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 2203920 -> 2206106 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_OPS-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOVERNANCE | error | gate | 层级违规: 2204755 -> 2204852 (L1_foundation -> L2_domain) |
| V-LAYER-D_OPS-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOV_DRIFT | error | gate | 层级违规: 2204754 -> 2205009 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 2204973 -> 2204794 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 层级违规: 2205023 -> 2205006 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-2203921 | 孤儿节点: 2203921 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203922 | 孤儿节点: 2203922 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203923 | 孤儿节点: 2203923 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203924 | 孤儿节点: 2203924 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203925 | 孤儿节点: 2203925 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203926 | 孤儿节点: 2203926 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203927 | 孤儿节点: 2203927 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2203940 | 孤儿节点: 2203940 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2203981 | 孤儿节点: 2203981 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2204011 | 孤儿节点: 2204011 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2204041 | 孤儿节点: 2204041 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2204042 | 孤儿节点: 2204042 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204043 | 孤儿节点: 2204043 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204044 | 孤儿节点: 2204044 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204045 | 孤儿节点: 2204045 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204046 | 孤儿节点: 2204046 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204047 | 孤儿节点: 2204047 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204048 | 孤儿节点: 2204048 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204049 | 孤儿节点: 2204049 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204050 | 孤儿节点: 2204050 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204051 | 孤儿节点: 2204051 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204052 | 孤儿节点: 2204052 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204053 | 孤儿节点: 2204053 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204054 | 孤儿节点: 2204054 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204055 | 孤儿节点: 2204055 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2204056 | 孤儿节点: 2204056 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204057 | 孤儿节点: 2204057 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204058 | 孤儿节点: 2204058 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204059 | 孤儿节点: 2204059 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204063 | 孤儿节点: 2204063 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204064 | 孤儿节点: 2204064 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204067 | 孤儿节点: 2204067 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204068 | 孤儿节点: 2204068 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204070 | 孤儿节点: 2204070 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204073 | 孤儿节点: 2204073 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204074 | 孤儿节点: 2204074 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204075 | 孤儿节点: 2204075 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204077 | 孤儿节点: 2204077 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204078 | 孤儿节点: 2204078 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204079 | 孤儿节点: 2204079 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204080 | 孤儿节点: 2204080 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204081 | 孤儿节点: 2204081 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204082 | 孤儿节点: 2204082 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204083 | 孤儿节点: 2204083 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204084 | 孤儿节点: 2204084 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2204085 | 孤儿节点: 2204085 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204086 | 孤儿节点: 2204086 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204087 | 孤儿节点: 2204087 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204088 | 孤儿节点: 2204088 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204089 | 孤儿节点: 2204089 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204090 | 孤儿节点: 2204090 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204091 | 孤儿节点: 2204091 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204092 | 孤儿节点: 2204092 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204093 | 孤儿节点: 2204093 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204094 | 孤儿节点: 2204094 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204095 | 孤儿节点: 2204095 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204096 | 孤儿节点: 2204096 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204097 | 孤儿节点: 2204097 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204098 | 孤儿节点: 2204098 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204099 | 孤儿节点: 2204099 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204100 | 孤儿节点: 2204100 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204101 | 孤儿节点: 2204101 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204102 | 孤儿节点: 2204102 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204103 | 孤儿节点: 2204103 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204104 | 孤儿节点: 2204104 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2204106 | 孤儿节点: 2204106 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204107 | 孤儿节点: 2204107 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204108 | 孤儿节点: 2204108 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204109 | 孤儿节点: 2204109 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204110 | 孤儿节点: 2204110 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204111 | 孤儿节点: 2204111 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2204112 | 孤儿节点: 2204112 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204113 | 孤儿节点: 2204113 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204114 | 孤儿节点: 2204114 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204115 | 孤儿节点: 2204115 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204118 | 孤儿节点: 2204118 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204119 | 孤儿节点: 2204119 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204120 | 孤儿节点: 2204120 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204121 | 孤儿节点: 2204121 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204122 | 孤儿节点: 2204122 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204123 | 孤儿节点: 2204123 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204125 | 孤儿节点: 2204125 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204126 | 孤儿节点: 2204126 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204128 | 孤儿节点: 2204128 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204129 | 孤儿节点: 2204129 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204130 | 孤儿节点: 2204130 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204131 | 孤儿节点: 2204131 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204132 | 孤儿节点: 2204132 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204133 | 孤儿节点: 2204133 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204134 | 孤儿节点: 2204134 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204135 | 孤儿节点: 2204135 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204136 | 孤儿节点: 2204136 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204137 | 孤儿节点: 2204137 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204138 | 孤儿节点: 2204138 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204139 | 孤儿节点: 2204139 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204140 | 孤儿节点: 2204140 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2204141 | 孤儿节点: 2204141 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204142 | 孤儿节点: 2204142 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204143 | 孤儿节点: 2204143 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2204144 | 孤儿节点: 2204144 | orphan_node | D_DATA_ENG |  | warn | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_AUDIT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_AUDIT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_KB | 跨域违规: D_AUTONOMY_CORE -> D_GOV_KB | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_KB | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_RULE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_RULE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | open |
| V-CROSS-D_COMPLIANCE-D_GOVERNANCE | 跨域违规: D_COMPLIANCE -> D_GOVERNANCE | cross_domain_violation | D_COMPLIANCE | D_GOVERNANCE | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_ENFORCEMENT | 跨域违规: D_COMPLIANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_COMPLIANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_COMPLIANCE-D_INFRA_RUNTIME | 跨域违规: D_COMPLIANCE -> D_INFRA_RUNTIME | cross_domain_violation | D_COMPLIANCE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | open |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_SIGLEGACY | 跨域违规: D_FACTOR -> D_SIGLEGACY | cross_domain_violation | D_FACTOR | D_SIGLEGACY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RECOVERY | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | open |
| V-CROSS-D_GOVERNANCE-D_FEEDBACK_LOOP | 跨域违规: D_GOVERNANCE -> D_FEEDBACK_LOOP | cross_domain_violation | D_GOVERNANCE | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_KB | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_RULE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_OPS-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOVERNANCE | error | open |
| V-LAYER-D_OPS-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOV_DRIFT | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | open |
