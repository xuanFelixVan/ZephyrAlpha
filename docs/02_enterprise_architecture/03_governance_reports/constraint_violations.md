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
| 约束总数 | 236 |
| Open（未解决） | 236 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 135 |
| hard | 1 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 1 |
| cross_domain_violation | 91 |
| hard_limit_exceeded | 1 |
| layer_violation | 42 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-2401967 | 孤儿节点: 2401967 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401967 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2401969 | 孤儿节点: 2401969 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401969 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-2401970 | 孤儿节点: 2401970 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401970 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2401971 | 孤儿节点: 2401971 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401971 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-2401973 | 孤儿节点: 2401973 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401973 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-2401974 | 孤儿节点: 2401974 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401974 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2401975 | 孤儿节点: 2401975 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2401975 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-2402024 | 孤儿节点: 2402024 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2402024 路径 src/zephyr/autonomy_core/context/memory_bank.p... |
| V-ORPHAN-2402030 | 孤儿节点: 2402030 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2402030 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-2402088 | 孤儿节点: 2402088 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2402088 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-2402089 | 孤儿节点: 2402089 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402089 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-2402090 | 孤儿节点: 2402090 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402090 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-2402091 | 孤儿节点: 2402091 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402091 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-2402092 | 孤儿节点: 2402092 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402092 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-2402093 | 孤儿节点: 2402093 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402093 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-2402094 | 孤儿节点: 2402094 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402094 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-2402095 | 孤儿节点: 2402095 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402095 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-2402096 | 孤儿节点: 2402096 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402096 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2402097 | 孤儿节点: 2402097 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402097 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2402098 | 孤儿节点: 2402098 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402098 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-2402099 | 孤儿节点: 2402099 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402099 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-2402100 | 孤儿节点: 2402100 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402100 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-2402101 | 孤儿节点: 2402101 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402101 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-2402102 | 孤儿节点: 2402102 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2402102 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-2402103 | 孤儿节点: 2402103 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402103 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-2402104 | 孤儿节点: 2402104 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402104 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-2402106 | 孤儿节点: 2402106 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402106 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2402110 | 孤儿节点: 2402110 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402110 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-2402111 | 孤儿节点: 2402111 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402111 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-2402112 | 孤儿节点: 2402112 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402112 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-2402115 | 孤儿节点: 2402115 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402115 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-2402116 | 孤儿节点: 2402116 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402116 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-2402117 | 孤儿节点: 2402117 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402117 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2402121 | 孤儿节点: 2402121 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402121 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-2402123 | 孤儿节点: 2402123 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402123 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-2402124 | 孤儿节点: 2402124 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402124 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-2402125 | 孤儿节点: 2402125 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402125 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-2402126 | 孤儿节点: 2402126 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402126 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2402127 | 孤儿节点: 2402127 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402127 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-2402128 | 孤儿节点: 2402128 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402128 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-2402129 | 孤儿节点: 2402129 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402129 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-2402130 | 孤儿节点: 2402130 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2402130 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-2402131 | 孤儿节点: 2402131 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402131 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-2402132 | 孤儿节点: 2402132 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402132 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-2402133 | 孤儿节点: 2402133 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402133 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-2402134 | 孤儿节点: 2402134 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402134 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-2402135 | 孤儿节点: 2402135 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402135 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-2402136 | 孤儿节点: 2402136 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402136 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2402137 | 孤儿节点: 2402137 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402137 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-2402138 | 孤儿节点: 2402138 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402138 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-2402139 | 孤儿节点: 2402139 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402139 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-2402140 | 孤儿节点: 2402140 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402140 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-2402141 | 孤儿节点: 2402141 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402141 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-2402142 | 孤儿节点: 2402142 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402142 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-2402143 | 孤儿节点: 2402143 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402143 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-2402144 | 孤儿节点: 2402144 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402144 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-2402145 | 孤儿节点: 2402145 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402145 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-2402146 | 孤儿节点: 2402146 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402146 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2402147 | 孤儿节点: 2402147 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402147 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-2402148 | 孤儿节点: 2402148 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402148 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-2402149 | 孤儿节点: 2402149 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402149 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2402150 | 孤儿节点: 2402150 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402150 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-2402151 | 孤儿节点: 2402151 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402151 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-2402152 | 孤儿节点: 2402152 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402152 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-2402154 | 孤儿节点: 2402154 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2402154 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-2402155 | 孤儿节点: 2402155 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402155 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-2402156 | 孤儿节点: 2402156 | orphan_node | D_DATA |  | warn | advisory | 节点 2402156 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-2402157 | 孤儿节点: 2402157 | orphan_node | D_DATA |  | warn | advisory | 节点 2402157 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-2402158 | 孤儿节点: 2402158 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402158 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-2402160 | 孤儿节点: 2402160 | orphan_node | D_DATA |  | warn | advisory | 节点 2402160 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-2402161 | 孤儿节点: 2402161 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2402161 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-2402162 | 孤儿节点: 2402162 | orphan_node | D_DATA |  | warn | advisory | 节点 2402162 路径 src/zephyr/data/backfill_checker.py 未注册到目录树 |
| V-ORPHAN-2402163 | 孤儿节点: 2402163 | orphan_node | D_DATA |  | warn | advisory | 节点 2402163 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-2402164 | 孤儿节点: 2402164 | orphan_node | D_DATA |  | warn | advisory | 节点 2402164 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-2402165 | 孤儿节点: 2402165 | orphan_node | D_DATA |  | warn | advisory | 节点 2402165 路径 src/zephyr/data/policy_registry.py 未注册到目录树 |
| V-ORPHAN-2402166 | 孤儿节点: 2402166 | orphan_node | D_DATA |  | warn | advisory | 节点 2402166 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-2402167 | 孤儿节点: 2402167 | orphan_node | D_DATA |  | warn | advisory | 节点 2402167 路径 src/zephyr/data/tick_subscriber.py 未注册到目录树 |
| V-ORPHAN-2402168 | 孤儿节点: 2402168 | orphan_node | D_DATA |  | warn | advisory | 节点 2402168 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-2402169 | 孤儿节点: 2402169 | orphan_node | D_DATA |  | warn | advisory | 节点 2402169 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-2402170 | 孤儿节点: 2402170 | orphan_node | D_DATA |  | warn | advisory | 节点 2402170 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-2402171 | 孤儿节点: 2402171 | orphan_node | D_DATA |  | warn | advisory | 节点 2402171 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-2402173 | 孤儿节点: 2402173 | orphan_node | D_DATA |  | warn | advisory | 节点 2402173 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-2402174 | 孤儿节点: 2402174 | orphan_node | D_DATA |  | warn | advisory | 节点 2402174 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-2402175 | 孤儿节点: 2402175 | orphan_node | D_DATA |  | warn | advisory | 节点 2402175 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-2402176 | 孤儿节点: 2402176 | orphan_node | D_DATA |  | warn | advisory | 节点 2402176 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-2402177 | 孤儿节点: 2402177 | orphan_node | D_DATA |  | warn | advisory | 节点 2402177 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-2402178 | 孤儿节点: 2402178 | orphan_node | D_DATA |  | warn | advisory | 节点 2402178 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-2402179 | 孤儿节点: 2402179 | orphan_node | D_DATA |  | warn | advisory | 节点 2402179 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-2402180 | 孤儿节点: 2402180 | orphan_node | D_DATA |  | warn | advisory | 节点 2402180 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-2402181 | 孤儿节点: 2402181 | orphan_node | D_DATA |  | warn | advisory | 节点 2402181 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-2402182 | 孤儿节点: 2402182 | orphan_node | D_DATA |  | warn | advisory | 节点 2402182 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-2402183 | 孤儿节点: 2402183 | orphan_node | D_DATA |  | warn | advisory | 节点 2402183 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-2402184 | 孤儿节点: 2402184 | orphan_node | D_DATA |  | warn | advisory | 节点 2402184 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-2402185 | 孤儿节点: 2402185 | orphan_node | D_DATA |  | warn | advisory | 节点 2402185 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-2402186 | 孤儿节点: 2402186 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402186 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2402187 | 孤儿节点: 2402187 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402187 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2402188 | 孤儿节点: 2402188 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402188 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-2402189 | 孤儿节点: 2402189 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402189 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2402190 | 孤儿节点: 2402190 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402190 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-2402191 | 孤儿节点: 2402191 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2402191 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | gate | 域 D_SHARED(shared_services) production 节点 155 超过上限 150，需拆分或提... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_DIAGNOSERS | 跨域违规: D_AUTONOMY_CORE -> D_FBL_DIAGNOSERS | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_FBL_DIAGNOSERS |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_VERIFICATION | 跨域违规: D_AUTONOMY_CORE -> D_FBL_VERIFICATION | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_FBL_VERIFICATION |
| V-CROSS-D_AUTONOMY_CORE-D_FEEDBACK_LOOP | 跨域违规: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP | cross_domain_violation | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_OPS_RESILIENCE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RECOVERY | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RECOVERY | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RECOVERY |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_ORCHESTRATOR | 跨域违规: D_AUTONOMY_CORE -> D_ORCHESTRATOR | cross_domain_violation | D_AUTONOMY_CORE | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_ORCHESTRATOR |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_CORE-D_TRADING | 跨域违规: D_AUTONOMY_CORE -> D_TRADING | cross_domain_violation | D_AUTONOMY_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_TRADING |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_AUDIT |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_DRIFT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_EX_CORE -> D_INFRASTRUCTURE |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_FBL_VERIFICATION -> D_GOV_AUDIT |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DETECTORS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SHARED |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_AUDIT |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_DRIFT |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOVERNANCE-D_GOV_SCRIPTS | 跨域违规: D_GOVERNANCE -> D_GOV_SCRIPTS | cross_domain_violation | D_GOVERNANCE | D_GOV_SCRIPTS | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_SCRIPTS |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_RISK | 跨域违规: D_GOVERNANCE -> D_RISK | cross_domain_violation | D_GOVERNANCE | D_RISK | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_RISK |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_TRADING |
| V-CROSS-D_GOV_AUDIT-D_AUTONOMY_CORE | 跨域违规: D_GOV_AUDIT -> D_AUTONOMY_CORE | cross_domain_violation | D_GOV_AUDIT | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_AUTONOMY_CORE |
| V-CROSS-D_GOV_AUDIT-D_FBL_DIAGNOSERS | 跨域违规: D_GOV_AUDIT -> D_FBL_DIAGNOSERS | cross_domain_violation | D_GOV_AUDIT | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_FBL_DIAGNOSERS |
| V-CROSS-D_GOV_AUDIT-D_FEEDBACK_LOOP | 跨域违规: D_GOV_AUDIT -> D_FEEDBACK_LOOP | cross_domain_violation | D_GOV_AUDIT | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_FEEDBACK_LOOP |
| V-CROSS-D_GOV_AUDIT-D_GOVERNANCE | 跨域违规: D_GOV_AUDIT -> D_GOVERNANCE | cross_domain_violation | D_GOV_AUDIT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOVERNANCE |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_AUDIT-D_GOV_RULE | 跨域违规: D_GOV_AUDIT -> D_GOV_RULE | cross_domain_violation | D_GOV_AUDIT | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_RULE |
| V-CROSS-D_GOV_AUDIT-D_INFRA_A2A | 跨域违规: D_GOV_AUDIT -> D_INFRA_A2A | cross_domain_violation | D_GOV_AUDIT | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_INFRA_A2A |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_SHARED |
| V-CROSS-D_GOV_CODE_QUALITY-D_AUTONOMY_CORE | 跨域违规: D_GOV_CODE_QUALITY -> D_AUTONOMY_CORE | cross_domain_violation | D_GOV_CODE_QUALITY | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_AUTONOMY_CORE |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_DRIFT-D_INTEGRATION | 跨域违规: D_GOV_DRIFT -> D_INTEGRATION | cross_domain_violation | D_GOV_DRIFT | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_INTEGRATION |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_SHARED |
| V-CROSS-D_GOV_ENFORCEMENT-D_FBL_DETECTORS | 跨域违规: D_GOV_ENFORCEMENT -> D_FBL_DETECTORS | cross_domain_violation | D_GOV_ENFORCEMENT | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_FBL_DETECTORS |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_RULE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_RULE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_RULE |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INTEGRATION |
| V-CROSS-D_GOV_KB-D_SHARED | 跨域违规: D_GOV_KB -> D_SHARED | cross_domain_violation | D_GOV_KB | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_KB -> D_SHARED |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_FACTOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_FACTOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_FACTOR |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_KB | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_KB | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOV_KB |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_A2A | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RECOVERY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RUNTIME | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INTEGRATION |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_OPS |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_ORCHESTRATOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SECURITY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SECURITY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_SECURITY |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_SHARED |
| V-CROSS-D_GOV_REPAIR-D_FACTOR | 跨域违规: D_GOV_REPAIR -> D_FACTOR | cross_domain_violation | D_GOV_REPAIR | D_FACTOR | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_FACTOR |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOVERNANCE |
| V-CROSS-D_GOV_REPAIR-D_GOV_AUDIT | 跨域违规: D_GOV_REPAIR -> D_GOV_AUDIT | cross_domain_violation | D_GOV_REPAIR | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_AUDIT |
| V-CROSS-D_GOV_REPAIR-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_REPAIR -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_REPAIR | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_REPAIR-D_GOV_DRIFT | 跨域违规: D_GOV_REPAIR -> D_GOV_DRIFT | cross_domain_violation | D_GOV_REPAIR | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_DRIFT |
| V-CROSS-D_GOV_REPAIR-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_REPAIR -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_REPAIR | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_REPAIR-D_GOV_KB | 跨域违规: D_GOV_REPAIR -> D_GOV_KB | cross_domain_violation | D_GOV_REPAIR | D_GOV_KB | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_KB |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_REPAIR-D_GOV_RULE | 跨域违规: D_GOV_REPAIR -> D_GOV_RULE | cross_domain_violation | D_GOV_REPAIR | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_GOV_RULE |
| V-CROSS-D_GOV_REPAIR-D_INFRASTRUCTURE | 跨域违规: D_GOV_REPAIR -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_REPAIR | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_INFRASTRUCTURE |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RECOVERY | 跨域违规: D_GOV_REPAIR -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_INFRA_RECOVERY |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RUNTIME | 跨域违规: D_GOV_REPAIR -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_REPAIR-D_OPS | 跨域违规: D_GOV_REPAIR -> D_OPS | cross_domain_violation | D_GOV_REPAIR | D_OPS | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_OPS |
| V-CROSS-D_GOV_REPAIR-D_TRADING | 跨域违规: D_GOV_REPAIR -> D_TRADING | cross_domain_violation | D_GOV_REPAIR | D_TRADING | error | gate | 跨域依赖未声明: D_GOV_REPAIR -> D_TRADING |
| V-CROSS-D_GOV_RULE-D_INFRA_RUNTIME | 跨域违规: D_GOV_RULE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_RULE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_RULE-D_SHARED | 跨域违规: D_GOV_RULE -> D_SHARED | cross_domain_violation | D_GOV_RULE | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_SHARED |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_DRIFT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_DRIFT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_DRIFT |
| V-CROSS-D_GOV_SCRIPTS-D_SECURITY | 跨域违规: D_GOV_SCRIPTS -> D_SECURITY | cross_domain_violation | D_GOV_SCRIPTS | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_SECURITY |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_SHARED |
| V-CROSS-D_INFRA_A2A-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_A2A -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_INFRA_A2A -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_INFRA_RECOVERY-D_FBL_DETECTORS | 跨域违规: D_INFRA_RECOVERY -> D_FBL_DETECTORS | cross_domain_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_FBL_DETECTORS |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_RULE |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTELLIGENCE |
| V-CROSS-D_INTEGRATION-D_TRADING | 跨域违规: D_INTEGRATION -> D_TRADING | cross_domain_violation | D_INTEGRATION | D_TRADING | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_TRADING |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_INTEGRATION |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_REPORTING -> D_INFRASTRUCTURE |
| V-CROSS-D_SECURITY-D_FBL_VERIFICATION | 跨域违规: D_SECURITY -> D_FBL_VERIFICATION | cross_domain_violation | D_SECURITY | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_SECURITY -> D_FBL_VERIFICATION |
| V-CROSS-D_SHARED-D_INTEGRATION | 跨域违规: D_SHARED -> D_INTEGRATION | cross_domain_violation | D_SHARED | D_INTEGRATION | error | gate | 跨域依赖未声明: D_SHARED -> D_INTEGRATION |
| V-CROSS-D_SIGLEGACY-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_TRADING -> D_INFRASTRUCTURE |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | gate | 域 D_SHARED(shared_services) production 节点 155 超过硬上限 150 (ARC... |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 2402076 -> 2402912 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 2406574 -> 2403206 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 2402000 -> 2403698 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_TRADING | error | gate | 层级违规: 2405268 -> 2404405 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 2402543 -> 2402912 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 2402261 -> 2402806 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_AUDIT | error | gate | 层级违规: 2405708 -> 2402929 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 2402273 -> 2402618 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 2402595 -> 2402806 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2403164 -> 2403173 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_FACTOR | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | gate | 层级违规: 2402810 -> 2402242 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 层级违规: 2402813 -> 2402870 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 层级违规: 2402780 -> 2402952 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | gate | 层级违规: 2402780 -> 2403055 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | gate | 层级违规: 2402698 -> 2403246 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 2403309 -> 2403314 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | error | gate | 层级违规: 2403370 -> 2402690 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_DETECTORS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | gate | 层级违规: 2405411 -> 2402369 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_AUDIT | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOV_AUDIT | error | gate | 层级违规: 2403521 -> 2402952 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | gate | 层级违规: 2405383 -> 2402985 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_ORCHESTRATOR | error | gate | 层级违规: 2405407 -> 2403797 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | gate | 层级违规: 2403524 -> 2404083 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | gate | 层级违规: 2404409 -> 2402065 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 层级违规: 2406400 -> 2402554 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 2403491 -> 2402811 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | gate | 层级违规: 2403566 -> 2402782 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_RULE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | gate | 层级违规: 2404409 -> 2403208 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 2403291 -> 2403654 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_INTELLIGENCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | gate | 层级违规: 2404411 -> 2403721 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | gate | 层级违规: 2404409 -> 2403787 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SECURITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SECURITY | error | gate | 层级违规: 2404409 -> 2403924 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 2404416 -> 2404273 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | gate | 层级违规: 2403580 -> 2404257 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | gate | 层级违规: 2403625 -> 2403627 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOV_RULE | error | gate | 层级违规: 2404141 -> 2403195 (L1_foundation -> L2_domain) |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | gate | 层级违规: 2403597 -> 2404404 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 2403976 -> 2402806 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 层级违规: 2403100 -> 2403101 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_KB | error | gate | 层级违规: 2406456 -> 2403255 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | gate | 层级违规: 2405541 -> 2402624 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_AUDIT | error | gate | 层级违规: 2404331 -> 2402962 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_RULE | error | gate | 层级违规: 2405779 -> 2403206 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-2401967 | 孤儿节点: 2401967 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401969 | 孤儿节点: 2401969 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401970 | 孤儿节点: 2401970 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401971 | 孤儿节点: 2401971 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401973 | 孤儿节点: 2401973 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401974 | 孤儿节点: 2401974 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2401975 | 孤儿节点: 2401975 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2402024 | 孤儿节点: 2402024 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2402030 | 孤儿节点: 2402030 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2402088 | 孤儿节点: 2402088 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2402089 | 孤儿节点: 2402089 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402090 | 孤儿节点: 2402090 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402091 | 孤儿节点: 2402091 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402092 | 孤儿节点: 2402092 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402093 | 孤儿节点: 2402093 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402094 | 孤儿节点: 2402094 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402095 | 孤儿节点: 2402095 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402096 | 孤儿节点: 2402096 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402097 | 孤儿节点: 2402097 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402098 | 孤儿节点: 2402098 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402099 | 孤儿节点: 2402099 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402100 | 孤儿节点: 2402100 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402101 | 孤儿节点: 2402101 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402102 | 孤儿节点: 2402102 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2402103 | 孤儿节点: 2402103 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402104 | 孤儿节点: 2402104 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402106 | 孤儿节点: 2402106 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402110 | 孤儿节点: 2402110 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402111 | 孤儿节点: 2402111 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402112 | 孤儿节点: 2402112 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402115 | 孤儿节点: 2402115 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402116 | 孤儿节点: 2402116 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402117 | 孤儿节点: 2402117 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402121 | 孤儿节点: 2402121 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402123 | 孤儿节点: 2402123 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402124 | 孤儿节点: 2402124 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402125 | 孤儿节点: 2402125 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402126 | 孤儿节点: 2402126 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402127 | 孤儿节点: 2402127 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402128 | 孤儿节点: 2402128 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402129 | 孤儿节点: 2402129 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402130 | 孤儿节点: 2402130 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2402131 | 孤儿节点: 2402131 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402132 | 孤儿节点: 2402132 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402133 | 孤儿节点: 2402133 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402134 | 孤儿节点: 2402134 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402135 | 孤儿节点: 2402135 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402136 | 孤儿节点: 2402136 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402137 | 孤儿节点: 2402137 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402138 | 孤儿节点: 2402138 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402139 | 孤儿节点: 2402139 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402140 | 孤儿节点: 2402140 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402141 | 孤儿节点: 2402141 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402142 | 孤儿节点: 2402142 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402143 | 孤儿节点: 2402143 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402144 | 孤儿节点: 2402144 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402145 | 孤儿节点: 2402145 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402146 | 孤儿节点: 2402146 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402147 | 孤儿节点: 2402147 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402148 | 孤儿节点: 2402148 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402149 | 孤儿节点: 2402149 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402150 | 孤儿节点: 2402150 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402151 | 孤儿节点: 2402151 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402152 | 孤儿节点: 2402152 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402154 | 孤儿节点: 2402154 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2402155 | 孤儿节点: 2402155 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402156 | 孤儿节点: 2402156 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402157 | 孤儿节点: 2402157 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402158 | 孤儿节点: 2402158 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402160 | 孤儿节点: 2402160 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402161 | 孤儿节点: 2402161 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2402162 | 孤儿节点: 2402162 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402163 | 孤儿节点: 2402163 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402164 | 孤儿节点: 2402164 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402165 | 孤儿节点: 2402165 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402166 | 孤儿节点: 2402166 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402167 | 孤儿节点: 2402167 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402168 | 孤儿节点: 2402168 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402169 | 孤儿节点: 2402169 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402170 | 孤儿节点: 2402170 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402171 | 孤儿节点: 2402171 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402173 | 孤儿节点: 2402173 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402174 | 孤儿节点: 2402174 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402175 | 孤儿节点: 2402175 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402176 | 孤儿节点: 2402176 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402177 | 孤儿节点: 2402177 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402178 | 孤儿节点: 2402178 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402179 | 孤儿节点: 2402179 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402180 | 孤儿节点: 2402180 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402181 | 孤儿节点: 2402181 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402182 | 孤儿节点: 2402182 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402183 | 孤儿节点: 2402183 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402184 | 孤儿节点: 2402184 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402185 | 孤儿节点: 2402185 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2402186 | 孤儿节点: 2402186 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2402187 | 孤儿节点: 2402187 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2402188 | 孤儿节点: 2402188 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2402189 | 孤儿节点: 2402189 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2402190 | 孤儿节点: 2402190 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2402191 | 孤儿节点: 2402191 | orphan_node | D_DATA_ENG |  | warn | open |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_DIAGNOSERS | 跨域违规: D_AUTONOMY_CORE -> D_FBL_DIAGNOSERS | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_FBL_VERIFICATION | 跨域违规: D_AUTONOMY_CORE -> D_FBL_VERIFICATION | cross_domain_violation | D_AUTONOMY_CORE | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_FEEDBACK_LOOP | 跨域违规: D_AUTONOMY_CORE -> D_FEEDBACK_LOOP | cross_domain_violation | D_AUTONOMY_CORE | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_OPS_RESILIENCE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RECOVERY | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RECOVERY | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_ORCHESTRATOR | 跨域违规: D_AUTONOMY_CORE -> D_ORCHESTRATOR | cross_domain_violation | D_AUTONOMY_CORE | D_ORCHESTRATOR | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_TRADING | 跨域违规: D_AUTONOMY_CORE -> D_TRADING | cross_domain_violation | D_AUTONOMY_CORE | D_TRADING | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_AUDIT | 跨域违规: D_GOVERNANCE -> D_GOV_AUDIT | cross_domain_violation | D_GOVERNANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_SCRIPTS | 跨域违规: D_GOVERNANCE -> D_GOV_SCRIPTS | cross_domain_violation | D_GOVERNANCE | D_GOV_SCRIPTS | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_RISK | 跨域违规: D_GOVERNANCE -> D_RISK | cross_domain_violation | D_GOVERNANCE | D_RISK | error | open |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | open |
| V-CROSS-D_GOV_AUDIT-D_AUTONOMY_CORE | 跨域违规: D_GOV_AUDIT -> D_AUTONOMY_CORE | cross_domain_violation | D_GOV_AUDIT | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_GOV_AUDIT-D_FBL_DIAGNOSERS | 跨域违规: D_GOV_AUDIT -> D_FBL_DIAGNOSERS | cross_domain_violation | D_GOV_AUDIT | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_GOV_AUDIT-D_FEEDBACK_LOOP | 跨域违规: D_GOV_AUDIT -> D_FEEDBACK_LOOP | cross_domain_violation | D_GOV_AUDIT | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOVERNANCE | 跨域违规: D_GOV_AUDIT -> D_GOVERNANCE | cross_domain_violation | D_GOV_AUDIT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_RULE | 跨域违规: D_GOV_AUDIT -> D_GOV_RULE | cross_domain_violation | D_GOV_AUDIT | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_AUDIT-D_INFRA_A2A | 跨域违规: D_GOV_AUDIT -> D_INFRA_A2A | cross_domain_violation | D_GOV_AUDIT | D_INFRA_A2A | error | open |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_AUTONOMY_CORE | 跨域违规: D_GOV_CODE_QUALITY -> D_AUTONOMY_CORE | cross_domain_violation | D_GOV_CODE_QUALITY | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_GOV_DRIFT-D_GOV_AUDIT | 跨域违规: D_GOV_DRIFT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_DRIFT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_DRIFT-D_INTEGRATION | 跨域违规: D_GOV_DRIFT -> D_INTEGRATION | cross_domain_violation | D_GOV_DRIFT | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_FBL_DETECTORS | 跨域违规: D_GOV_ENFORCEMENT -> D_FBL_DETECTORS | cross_domain_violation | D_GOV_ENFORCEMENT | D_FBL_DETECTORS | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_RULE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_RULE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_KB-D_SHARED | 跨域违规: D_GOV_KB -> D_SHARED | cross_domain_violation | D_GOV_KB | D_SHARED | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_FACTOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_FACTOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_AUDIT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_DRIFT | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOV_KB | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOV_KB | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_A2A | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RECOVERY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_RUNTIME | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_OPS | 跨域违规: D_GOV_OPS_RESILIENCE -> D_OPS | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_OPS | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_ORCHESTRATOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_ORCHESTRATOR | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SECURITY | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SECURITY | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SECURITY | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | open |
| V-CROSS-D_GOV_REPAIR-D_FACTOR | 跨域违规: D_GOV_REPAIR -> D_FACTOR | cross_domain_violation | D_GOV_REPAIR | D_FACTOR | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOVERNANCE | 跨域违规: D_GOV_REPAIR -> D_GOVERNANCE | cross_domain_violation | D_GOV_REPAIR | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_AUDIT | 跨域违规: D_GOV_REPAIR -> D_GOV_AUDIT | cross_domain_violation | D_GOV_REPAIR | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_REPAIR -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_REPAIR | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_DRIFT | 跨域违规: D_GOV_REPAIR -> D_GOV_DRIFT | cross_domain_violation | D_GOV_REPAIR | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_REPAIR -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_REPAIR | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_KB | 跨域违规: D_GOV_REPAIR -> D_GOV_KB | cross_domain_violation | D_GOV_REPAIR | D_GOV_KB | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_REPAIR -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_REPAIR | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_REPAIR-D_GOV_RULE | 跨域违规: D_GOV_REPAIR -> D_GOV_RULE | cross_domain_violation | D_GOV_REPAIR | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_REPAIR-D_INFRASTRUCTURE | 跨域违规: D_GOV_REPAIR -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_REPAIR | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RECOVERY | 跨域违规: D_GOV_REPAIR -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOV_REPAIR-D_INFRA_RUNTIME | 跨域违规: D_GOV_REPAIR -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_REPAIR | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_REPAIR-D_OPS | 跨域违规: D_GOV_REPAIR -> D_OPS | cross_domain_violation | D_GOV_REPAIR | D_OPS | error | open |
| V-CROSS-D_GOV_REPAIR-D_TRADING | 跨域违规: D_GOV_REPAIR -> D_TRADING | cross_domain_violation | D_GOV_REPAIR | D_TRADING | error | open |
| V-CROSS-D_GOV_RULE-D_INFRA_RUNTIME | 跨域违规: D_GOV_RULE -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_RULE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_RULE-D_SHARED | 跨域违规: D_GOV_RULE -> D_SHARED | cross_domain_violation | D_GOV_RULE | D_SHARED | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_DRIFT | 跨域违规: D_GOV_SCRIPTS -> D_GOV_DRIFT | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_SECURITY | 跨域违规: D_GOV_SCRIPTS -> D_SECURITY | cross_domain_violation | D_GOV_SCRIPTS | D_SECURITY | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_SHARED | 跨域违规: D_GOV_SCRIPTS -> D_SHARED | cross_domain_violation | D_GOV_SCRIPTS | D_SHARED | error | open |
| V-CROSS-D_INFRA_A2A-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_A2A -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_FBL_DETECTORS | 跨域违规: D_INFRA_RECOVERY -> D_FBL_DETECTORS | cross_domain_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_RULE | 跨域违规: D_INFRA_RUNTIME -> D_GOV_RULE | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | open |
| V-CROSS-D_INTEGRATION-D_TRADING | 跨域违规: D_INTEGRATION -> D_TRADING | cross_domain_violation | D_INTEGRATION | D_TRADING | error | open |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | open |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_SECURITY-D_FBL_VERIFICATION | 跨域违规: D_SECURITY -> D_FBL_VERIFICATION | cross_domain_violation | D_SECURITY | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_SHARED-D_INTEGRATION | 跨域违规: D_SHARED -> D_INTEGRATION | cross_domain_violation | D_SHARED | D_INTEGRATION | error | open |
| V-CROSS-D_SIGLEGACY-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_SIGLEGACY -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_SIGLEGACY | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | open |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_TRADING | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_FACTOR | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_DRIFT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | open |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_GOV_OPS_RESILIENCE | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_FBL_DETECTORS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_FBL_DETECTORS | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_AUDIT | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RECOVERY | D_GOV_AUDIT | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_GOV_CODE_QUALITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_GOV_CODE_QUALITY | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_ORCHESTRATOR | error | open |
| V-LAYER-D_INFRA_RECOVERY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RECOVERY | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_OPS_RESILIENCE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_GOV_OPS_RESILIENCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_RULE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_RULE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTELLIGENCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SECURITY | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SECURITY | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INFRA_TELEMETRY-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_TELEMETRY | D_SHARED | error | open |
| V-LAYER-D_INTEGRATION-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOVERNANCE | error | open |
| V-LAYER-D_INTEGRATION-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_GOV_RULE | error | open |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | open |
| V-LAYER-D_SECURITY-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_KB | error | open |
| V-LAYER-D_SHARED-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOVERNANCE | error | open |
| V-LAYER-D_SHARED-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_AUDIT | error | open |
| V-LAYER-D_SHARED-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SHARED | D_GOV_RULE | error | open |
