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
| 约束总数 | 171 |
| Open（未解决） | 171 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 71 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| cross_domain_violation | 59 |
| layer_violation | 11 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-6876437 | 孤儿节点: 6876437 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 6876437 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-6876438 | 孤儿节点: 6876438 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 6876438 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-6876439 | 孤儿节点: 6876439 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 6876439 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-6876440 | 孤儿节点: 6876440 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 6876440 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-6876450 | 孤儿节点: 6876450 | orphan_node | D_DATA |  | warn | advisory | 节点 6876450 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-6876459 | 孤儿节点: 6876459 | orphan_node | D_DATA |  | warn | advisory | 节点 6876459 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-6876469 | 孤儿节点: 6876469 | orphan_node | D_DATA |  | warn | advisory | 节点 6876469 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-6876471 | 孤儿节点: 6876471 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 6876471 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-6876478 | 孤儿节点: 6876478 | orphan_node | D_DATA |  | warn | advisory | 节点 6876478 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-6876487 | 孤儿节点: 6876487 | orphan_node | D_DATA |  | warn | advisory | 节点 6876487 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-6876504 | 孤儿节点: 6876504 | orphan_node | D_EX_SOR |  | warn | advisory | 节点 6876504 路径 src/zephyr/ex_sor/infrastructure/__init__.py 未... |
| V-ORPHAN-6876507 | 孤儿节点: 6876507 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 6876507 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-6876522 | 孤儿节点: 6876522 | orphan_node | D_DATA |  | warn | advisory | 节点 6876522 路径 src/zephyr/data/trading_calendar.py 未注册到目录树 |
| V-ORPHAN-6876530 | 孤儿节点: 6876530 | orphan_node | D_EX_SOR |  | warn | advisory | 节点 6876530 路径 src/zephyr/ex_sor/__init__.py 未注册到目录树 |
| V-ORPHAN-6876540 | 孤儿节点: 6876540 | orphan_node | D_DATA |  | warn | advisory | 节点 6876540 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-6876557 | 孤儿节点: 6876557 | orphan_node | D_DATA |  | warn | advisory | 节点 6876557 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-6876582 | 孤儿节点: 6876582 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6876582 路径 src/zephyr/ex_core/adapters/__init__.py 未注册到目录... |
| V-ORPHAN-6876589 | 孤儿节点: 6876589 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 6876589 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-6876594 | 孤儿节点: 6876594 | orphan_node | D_DATA |  | warn | advisory | 节点 6876594 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-6876601 | 孤儿节点: 6876601 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6876601 路径 src/zephyr/ex_core/adapters/risk_validation_br... |
| V-ORPHAN-6876611 | 孤儿节点: 6876611 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6876611 路径 src/zephyr/ex_core/adapters/miniqmt_broker.py ... |
| V-ORPHAN-6876614 | 孤儿节点: 6876614 | orphan_node | D_DATA |  | warn | advisory | 节点 6876614 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-6876624 | 孤儿节点: 6876624 | orphan_node | D_DATA |  | warn | advisory | 节点 6876624 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-6876643 | 孤儿节点: 6876643 | orphan_node | D_DATA |  | warn | advisory | 节点 6876643 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-6876648 | 孤儿节点: 6876648 | orphan_node |  |  | warn | advisory | 节点 6876648 路径 src/zephyr/data/wal_codec/tsv_codec.py 未注册到目录树 |
| V-ORPHAN-6876654 | 孤儿节点: 6876654 | orphan_node | D_DATA |  | warn | advisory | 节点 6876654 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-6876658 | 孤儿节点: 6876658 | orphan_node |  |  | warn | advisory | 节点 6876658 路径 src/zephyr/data/wal_codec/codec_registry.py 未注... |
| V-ORPHAN-6876663 | 孤儿节点: 6876663 | orphan_node | D_DATA |  | warn | advisory | 节点 6876663 路径 src/zephyr/data/local_replay.py 未注册到目录树 |
| V-ORPHAN-6876667 | 孤儿节点: 6876667 | orphan_node | D_DATA |  | warn | advisory | 节点 6876667 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-6876676 | 孤儿节点: 6876676 | orphan_node | D_DATA |  | warn | advisory | 节点 6876676 路径 src/zephyr/data/redundant_source/__init__.py 未... |
| V-ORPHAN-6876699 | 孤儿节点: 6876699 | orphan_node | D_DATA |  | warn | advisory | 节点 6876699 路径 src/zephyr/data/cross_source_validator.py 未注册到... |
| V-ORPHAN-6876723 | 孤儿节点: 6876723 | orphan_node |  |  | warn | advisory | 节点 6876723 路径 src/zephyr/data/redundant_source/backup_tick_p... |
| V-ORPHAN-6876729 | 孤儿节点: 6876729 | orphan_node | D_DATA |  | warn | advisory | 节点 6876729 路径 src/zephyr/data/ch_reader.py 未注册到目录树 |
| V-ORPHAN-6876733 | 孤儿节点: 6876733 | orphan_node | D_DATA |  | warn | advisory | 节点 6876733 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-6876738 | 孤儿节点: 6876738 | orphan_node | D_DATA |  | warn | advisory | 节点 6876738 路径 src/zephyr/data/ch_config.py 未注册到目录树 |
| V-ORPHAN-6876742 | 孤儿节点: 6876742 | orphan_node | D_DATA |  | warn | advisory | 节点 6876742 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-6876747 | 孤儿节点: 6876747 | orphan_node | D_DATA |  | warn | advisory | 节点 6876747 路径 src/zephyr/data/capability_validator.py 未注册到目录... |
| V-ORPHAN-6876751 | 孤儿节点: 6876751 | orphan_node | D_DATA |  | warn | advisory | 节点 6876751 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-6876756 | 孤儿节点: 6876756 | orphan_node | D_DATA |  | warn | advisory | 节点 6876756 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-6876760 | 孤儿节点: 6876760 | orphan_node | D_DATA |  | warn | advisory | 节点 6876760 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-6876765 | 孤儿节点: 6876765 | orphan_node | D_DATA |  | warn | advisory | 节点 6876765 路径 src/zephyr/data/backfill_checker.py 未注册到目录树 |
| V-ORPHAN-6876768 | 孤儿节点: 6876768 | orphan_node | D_FACTOR |  | warn | advisory | 节点 6876768 路径 src/zephyr/factor/value_factor.py 未注册到目录树 |
| V-ORPHAN-6876769 | 孤儿节点: 6876769 | orphan_node | D_DATA |  | warn | advisory | 节点 6876769 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-6876774 | 孤儿节点: 6876774 | orphan_node | D_DATA |  | warn | advisory | 节点 6876774 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-6876777 | 孤儿节点: 6876777 | orphan_node | D_FACTOR |  | warn | advisory | 节点 6876777 路径 src/zephyr/factor/momentum_factor.py 未注册到目录树 |
| V-ORPHAN-6876778 | 孤儿节点: 6876778 | orphan_node | D_DATA |  | warn | advisory | 节点 6876778 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-6876804 | 孤儿节点: 6876804 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 6876804 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-6876845 | 孤儿节点: 6876845 | orphan_node |  |  | warn | advisory | 节点 6876845 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-6877066 | 孤儿节点: 6877066 | orphan_node |  |  | warn | advisory | 节点 6877066 路径 src/zephyr/frontend/__init__.py 未注册到目录树 |
| V-ORPHAN-6877072 | 孤儿节点: 6877072 | orphan_node | D_FRONTEND |  | warn | advisory | 节点 6877072 路径 src/zephyr/frontend/dashboard/components/backt... |
| V-ORPHAN-6877074 | 孤儿节点: 6877074 | orphan_node |  |  | warn | advisory | 节点 6877074 路径 src/zephyr/frontend/dashboard/__init__.py 未注册到... |
| V-ORPHAN-6877075 | 孤儿节点: 6877075 | orphan_node | D_FRONTEND |  | warn | advisory | 节点 6877075 路径 src/zephyr/frontend/dashboard/components/chart... |
| V-ORPHAN-6877086 | 孤儿节点: 6877086 | orphan_node |  |  | warn | advisory | 节点 6877086 路径 src/zephyr/frontend/dashboard/components/__ini... |
| V-ORPHAN-6877096 | 孤儿节点: 6877096 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877096 路径 src/zephyr/governance/adapters/risk_validation... |
| V-ORPHAN-6877098 | 孤儿节点: 6877098 | orphan_node |  |  | warn | advisory | 节点 6877098 路径 src/zephyr/governance/adapters/__init__.py 未注册... |
| V-ORPHAN-6877099 | 孤儿节点: 6877099 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877099 路径 src/zephyr/governance/adapters/simulation_brok... |
| V-ORPHAN-6877125 | 孤儿节点: 6877125 | orphan_node | D_GOV_AUDIT |  | warn | advisory | 节点 6877125 路径 src/zephyr/governance/audit/default_attributio... |
| V-ORPHAN-6877146 | 孤儿节点: 6877146 | orphan_node |  |  | warn | advisory | 节点 6877146 路径 src/zephyr/governance/compliance_gate_a6/__ini... |
| V-ORPHAN-6877162 | 孤儿节点: 6877162 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877162 路径 src/zephyr/governance/data_governance/akshare_... |
| V-ORPHAN-6877176 | 孤儿节点: 6877176 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877176 路径 src/zephyr/governance/engine/pipeline_base.py ... |
| V-ORPHAN-6877177 | 孤儿节点: 6877177 | orphan_node |  |  | warn | advisory | 节点 6877177 路径 src/zephyr/governance/engine/__init__.py 未注册到目... |
| V-ORPHAN-6877178 | 孤儿节点: 6877178 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877178 路径 src/zephyr/governance/data_governance/miniqmt_... |
| V-ORPHAN-6877211 | 孤儿节点: 6877211 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877211 路径 src/zephyr/governance/implementations/default_... |
| V-ORPHAN-6877212 | 孤儿节点: 6877212 | orphan_node |  |  | warn | advisory | 节点 6877212 路径 src/zephyr/governance/implementations/__init__... |
| V-ORPHAN-6877213 | 孤儿节点: 6877213 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877213 路径 src/zephyr/governance/implementations/default_... |
| V-ORPHAN-6877245 | 孤儿节点: 6877245 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877245 路径 src/zephyr/governance/observability_governance... |
| V-ORPHAN-6877372 | 孤儿节点: 6877372 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877372 路径 src/zephyr/governance/strategies/strategy_regi... |
| V-ORPHAN-6877373 | 孤儿节点: 6877373 | orphan_node |  |  | warn | advisory | 节点 6877373 路径 src/zephyr/governance/strategies/__init__.py 未... |
| V-ORPHAN-6877788 | 孤儿节点: 6877788 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6877788 路径 src/zephyr/infrastructure/a2a_protocol/governa... |
| V-ORPHAN-6878122 | 孤儿节点: 6878122 | orphan_node | D_INTEGRATION |  | warn | advisory | 节点 6878122 路径 src/zephyr/integration/vector_memory/context_i... |
| V-ORPHAN-6878123 | 孤儿节点: 6878123 | orphan_node | D_INTEGRATION |  | warn | advisory | 节点 6878123 路径 src/zephyr/integration/vector_memory/cross_col... |
| V-ORPHAN-6878203 | 孤儿节点: 6878203 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6878203 路径 src/zephyr/ml_train/inference_base.py 未注册到目录树 |
| V-ORPHAN-6878204 | 孤儿节点: 6878204 | orphan_node |  |  | warn | advisory | 节点 6878204 路径 src/zephyr/ml_train/implementations/__init__.p... |
| V-ORPHAN-6878208 | 孤儿节点: 6878208 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6878208 路径 src/zephyr/ml_train/trainer_base.py 未注册到目录树 |
| V-ORPHAN-6878209 | 孤儿节点: 6878209 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6878209 路径 src/zephyr/ml_train/implementations/default_in... |
| V-ORPHAN-6878210 | 孤儿节点: 6878210 | orphan_node |  |  | warn | advisory | 节点 6878210 路径 src/zephyr/ml_train/__init__.py 未注册到目录树 |
| V-ORPHAN-6878301 | 孤儿节点: 6878301 | orphan_node | D_PF_CORE |  | warn | advisory | 节点 6878301 路径 src/zephyr/pf_core/strategy_engine/__init__.py... |
| V-ORPHAN-6878307 | 孤儿节点: 6878307 | orphan_node | D_REPORTING |  | warn | advisory | 节点 6878307 路径 src/zephyr/reporting/default_tca_engine.py 未注册... |
| V-ORPHAN-6878309 | 孤儿节点: 6878309 | orphan_node |  |  | warn | advisory | 节点 6878309 路径 src/zephyr/reporting/__init__.py 未注册到目录树 |
| V-ORPHAN-6878312 | 孤儿节点: 6878312 | orphan_node | D_REPORTING |  | warn | advisory | 节点 6878312 路径 src/zephyr/reporting/default_attribution_engin... |
| V-ORPHAN-6878324 | 孤儿节点: 6878324 | orphan_node |  |  | warn | advisory | 节点 6878324 路径 src/zephyr/risk/__init__.py 未注册到目录树 |
| V-ORPHAN-6878333 | 孤儿节点: 6878333 | orphan_node |  |  | warn | advisory | 节点 6878333 路径 src/zephyr/risk/implementations/__init__.py 未注... |
| V-ORPHAN-6878798 | 孤儿节点: 6878798 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878798 路径 src/zephyr/signal_fundamental/capital/capital_... |
| V-ORPHAN-6878802 | 孤儿节点: 6878802 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878802 路径 src/zephyr/signal_fundamental/__init__.py 未注册到... |
| V-ORPHAN-6878803 | 孤儿节点: 6878803 | orphan_node |  |  | warn | advisory | 节点 6878803 路径 src/zephyr/signal_fundamental/capital/__init__... |
| V-ORPHAN-6878805 | 孤儿节点: 6878805 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878805 路径 src/zephyr/signal_fundamental/capital/capital_... |
| V-ORPHAN-6878806 | 孤儿节点: 6878806 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878806 路径 src/zephyr/signal_fundamental/capital/default_... |
| V-ORPHAN-6878807 | 孤儿节点: 6878807 | orphan_node |  |  | warn | advisory | 节点 6878807 路径 src/zephyr/signal_fundamental/combiner/impl/__... |
| V-ORPHAN-6878809 | 孤儿节点: 6878809 | orphan_node |  |  | warn | advisory | 节点 6878809 路径 src/zephyr/signal_fundamental/gen/__init__.py ... |
| V-ORPHAN-6878810 | 孤儿节点: 6878810 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878810 路径 src/zephyr/signal_fundamental/gen/aggregator_b... |
| V-ORPHAN-6878811 | 孤儿节点: 6878811 | orphan_node |  |  | warn | advisory | 节点 6878811 路径 src/zephyr/signal_fundamental/combiner/__init_... |
| V-ORPHAN-6878812 | 孤儿节点: 6878812 | orphan_node |  |  | warn | advisory | 节点 6878812 路径 src/zephyr/signal_fundamental/gen/implementati... |
| V-ORPHAN-6878813 | 孤儿节点: 6878813 | orphan_node |  |  | warn | advisory | 节点 6878813 路径 src/zephyr/signal_fundamental/strategy/__init_... |
| V-ORPHAN-6878815 | 孤儿节点: 6878815 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6878815 路径 src/zephyr/signal_fundamental/strategy/capital... |
| V-ORPHAN-6878818 | 孤儿节点: 6878818 | orphan_node |  |  | warn | advisory | 节点 6878818 路径 src/zephyr/signal_fundamental/strategy/impleme... |
| V-ORPHAN-6878823 | 孤儿节点: 6878823 | orphan_node |  |  | warn | advisory | 节点 6878823 路径 src/zephyr/signal_fundamental/synth/__init__.p... |
| V-ORPHAN-6878827 | 孤儿节点: 6878827 | orphan_node |  |  | warn | advisory | 节点 6878827 路径 src/zephyr/simulation/__init__.py 未注册到目录树 |
| V-ORPHAN-6878836 | 孤儿节点: 6878836 | orphan_node |  |  | warn | advisory | 节点 6878836 路径 src/zephyr/simulation/implementations/__init__... |
| V-ORPHAN-6878908 | 孤儿节点: 6878908 | orphan_node | D_TRADING |  | warn | advisory | 节点 6878908 路径 src/zephyr/trading/trading_contracts/portfolio... |
| V-ORPHAN-6878911 | 孤儿节点: 6878911 | orphan_node | D_TRADING |  | warn | advisory | 节点 6878911 路径 src/zephyr/trading/trading_contracts/portfolio... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_DATA -> D_GOV_ENFORCEMENT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_FACTOR -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOVERNANCE |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_ORCHESTRATOR |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SHARED |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_INFRASTRUCTURE | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_TRADING | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_TRADING | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_TRADING | error | gate | 跨域依赖未声明: D_FUNDAMENTAL_SIGNAL -> D_TRADING |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOVERNANCE-D_INFRASTRUCTURE | 跨域违规: D_GOVERNANCE -> D_INFRASTRUCTURE | cross_domain_violation | D_GOVERNANCE | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRASTRUCTURE |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_A2A |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_OPS |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_REPORTING |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_TRADING |
| V-CROSS-D_GOV_AUDIT-D_GOVERNANCE | 跨域违规: D_GOV_AUDIT -> D_GOVERNANCE | cross_domain_violation | D_GOV_AUDIT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOVERNANCE |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_AUDIT-D_REPORTING | 跨域违规: D_GOV_AUDIT -> D_REPORTING | cross_domain_violation | D_GOV_AUDIT | D_REPORTING | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_REPORTING |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_SHARED |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_DATA |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOVERNANCE | 跨域违规: D_GOV_CODE_QUALITY -> D_GOVERNANCE | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOVERNANCE |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_CODE_QUALITY-D_INFRA_RUNTIME | 跨域违规: D_GOV_CODE_QUALITY -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_CODE_QUALITY | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_INFRA_RUNTIME |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_SHARED |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_SHARED |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_AUDIT |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRASTRUCTURE | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INFRASTRUCTURE |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_SECURITY |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_FACTOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_FACTOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_FACTOR |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_A2A | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INTEGRATION |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTELLIGENCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTELLIGENCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_INTELLIGENCE |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | gate | 跨域依赖未声明: D_GOV_OPS_RESILIENCE -> D_SHARED |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_DATA |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_REPAIR |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_GOV_AUDIT |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_INTELLIGENCE |
| V-CROSS-D_INTELLIGENCE-D_GOVERNANCE | 跨域违规: D_INTELLIGENCE -> D_GOVERNANCE | cross_domain_violation | D_INTELLIGENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_GOVERNANCE |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_INTEGRATION |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | gate | 跨域依赖未声明: D_ML_TRAIN -> D_TRADING |
| V-CROSS-D_ORCHESTRATOR-D_AUTONOMY_CORE | 跨域违规: D_ORCHESTRATOR -> D_AUTONOMY_CORE | cross_domain_violation | D_ORCHESTRATOR | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_AUTONOMY_CORE |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_GOVERNANCE |
| V-CROSS-D_ORCHESTRATOR-D_INFRA_RUNTIME | 跨域违规: D_ORCHESTRATOR -> D_INFRA_RUNTIME | cross_domain_violation | D_ORCHESTRATOR | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_INFRA_RUNTIME |
| V-CROSS-D_ORCHESTRATOR-D_INTEGRATION | 跨域违规: D_ORCHESTRATOR -> D_INTEGRATION | cross_domain_violation | D_ORCHESTRATOR | D_INTEGRATION | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_INTEGRATION |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_SHARED |
| V-CROSS-D_PF_ALLOC-D_INFRASTRUCTURE | 跨域违规: D_PF_ALLOC -> D_INFRASTRUCTURE | cross_domain_violation | D_PF_ALLOC | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_PF_ALLOC -> D_INFRASTRUCTURE |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | gate | 跨域依赖未声明: D_PF_CORE -> D_PF_ALLOC |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_REPORTING -> D_INFRASTRUCTURE |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOVERNANCE |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_DRIFT |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_TRADING -> D_INFRASTRUCTURE |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 6876820 -> 6877433 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 6876820 -> 6877734 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 6876859 -> 6878156 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 6877014 -> 6877382 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 6876657 -> 6877305 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 6876543 -> 6877092 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 6877071 -> 6877305 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 6877082 -> 6878901 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 层级违规: 6877666 -> 6877089 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | gate | 层级违规: 6877659 -> 6877136 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 6877678 -> 6877677 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-6876437 | 孤儿节点: 6876437 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-6876438 | 孤儿节点: 6876438 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-6876439 | 孤儿节点: 6876439 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-6876440 | 孤儿节点: 6876440 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-6876450 | 孤儿节点: 6876450 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876459 | 孤儿节点: 6876459 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876469 | 孤儿节点: 6876469 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876471 | 孤儿节点: 6876471 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-6876478 | 孤儿节点: 6876478 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876487 | 孤儿节点: 6876487 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876504 | 孤儿节点: 6876504 | orphan_node | D_EX_SOR |  | warn | open |
| V-ORPHAN-6876507 | 孤儿节点: 6876507 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-6876522 | 孤儿节点: 6876522 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876530 | 孤儿节点: 6876530 | orphan_node | D_EX_SOR |  | warn | open |
| V-ORPHAN-6876540 | 孤儿节点: 6876540 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876557 | 孤儿节点: 6876557 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876582 | 孤儿节点: 6876582 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6876589 | 孤儿节点: 6876589 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-6876594 | 孤儿节点: 6876594 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876601 | 孤儿节点: 6876601 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6876611 | 孤儿节点: 6876611 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6876614 | 孤儿节点: 6876614 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876624 | 孤儿节点: 6876624 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876643 | 孤儿节点: 6876643 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876648 | 孤儿节点: 6876648 | orphan_node |  |  | warn | open |
| V-ORPHAN-6876654 | 孤儿节点: 6876654 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876658 | 孤儿节点: 6876658 | orphan_node |  |  | warn | open |
| V-ORPHAN-6876663 | 孤儿节点: 6876663 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876667 | 孤儿节点: 6876667 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876676 | 孤儿节点: 6876676 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876699 | 孤儿节点: 6876699 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876723 | 孤儿节点: 6876723 | orphan_node |  |  | warn | open |
| V-ORPHAN-6876729 | 孤儿节点: 6876729 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876733 | 孤儿节点: 6876733 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876738 | 孤儿节点: 6876738 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876742 | 孤儿节点: 6876742 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876747 | 孤儿节点: 6876747 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876751 | 孤儿节点: 6876751 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876756 | 孤儿节点: 6876756 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876760 | 孤儿节点: 6876760 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876765 | 孤儿节点: 6876765 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876768 | 孤儿节点: 6876768 | orphan_node | D_FACTOR |  | warn | open |
| V-ORPHAN-6876769 | 孤儿节点: 6876769 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876774 | 孤儿节点: 6876774 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876777 | 孤儿节点: 6876777 | orphan_node | D_FACTOR |  | warn | open |
| V-ORPHAN-6876778 | 孤儿节点: 6876778 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6876804 | 孤儿节点: 6876804 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-6876845 | 孤儿节点: 6876845 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877066 | 孤儿节点: 6877066 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877072 | 孤儿节点: 6877072 | orphan_node | D_FRONTEND |  | warn | open |
| V-ORPHAN-6877074 | 孤儿节点: 6877074 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877075 | 孤儿节点: 6877075 | orphan_node | D_FRONTEND |  | warn | open |
| V-ORPHAN-6877086 | 孤儿节点: 6877086 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877096 | 孤儿节点: 6877096 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877098 | 孤儿节点: 6877098 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877099 | 孤儿节点: 6877099 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877125 | 孤儿节点: 6877125 | orphan_node | D_GOV_AUDIT |  | warn | open |
| V-ORPHAN-6877146 | 孤儿节点: 6877146 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877162 | 孤儿节点: 6877162 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877176 | 孤儿节点: 6877176 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877177 | 孤儿节点: 6877177 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877178 | 孤儿节点: 6877178 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877211 | 孤儿节点: 6877211 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877212 | 孤儿节点: 6877212 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877213 | 孤儿节点: 6877213 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877245 | 孤儿节点: 6877245 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877372 | 孤儿节点: 6877372 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6877373 | 孤儿节点: 6877373 | orphan_node |  |  | warn | open |
| V-ORPHAN-6877788 | 孤儿节点: 6877788 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6878122 | 孤儿节点: 6878122 | orphan_node | D_INTEGRATION |  | warn | open |
| V-ORPHAN-6878123 | 孤儿节点: 6878123 | orphan_node | D_INTEGRATION |  | warn | open |
| V-ORPHAN-6878203 | 孤儿节点: 6878203 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6878204 | 孤儿节点: 6878204 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878208 | 孤儿节点: 6878208 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6878209 | 孤儿节点: 6878209 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6878210 | 孤儿节点: 6878210 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878301 | 孤儿节点: 6878301 | orphan_node | D_PF_CORE |  | warn | open |
| V-ORPHAN-6878307 | 孤儿节点: 6878307 | orphan_node | D_REPORTING |  | warn | open |
| V-ORPHAN-6878309 | 孤儿节点: 6878309 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878312 | 孤儿节点: 6878312 | orphan_node | D_REPORTING |  | warn | open |
| V-ORPHAN-6878324 | 孤儿节点: 6878324 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878333 | 孤儿节点: 6878333 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878798 | 孤儿节点: 6878798 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878802 | 孤儿节点: 6878802 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878803 | 孤儿节点: 6878803 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878805 | 孤儿节点: 6878805 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878806 | 孤儿节点: 6878806 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878807 | 孤儿节点: 6878807 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878809 | 孤儿节点: 6878809 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878810 | 孤儿节点: 6878810 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878811 | 孤儿节点: 6878811 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878812 | 孤儿节点: 6878812 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878813 | 孤儿节点: 6878813 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878815 | 孤儿节点: 6878815 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6878818 | 孤儿节点: 6878818 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878823 | 孤儿节点: 6878823 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878827 | 孤儿节点: 6878827 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878836 | 孤儿节点: 6878836 | orphan_node |  |  | warn | open |
| V-ORPHAN-6878908 | 孤儿节点: 6878908 | orphan_node | D_TRADING |  | warn | open |
| V-ORPHAN-6878911 | 孤儿节点: 6878911 | orphan_node | D_TRADING |  | warn | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | open |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_INFRASTRUCTURE | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_INFRASTRUCTURE | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_FUNDAMENTAL_SIGNAL-D_TRADING | 跨域违规: D_FUNDAMENTAL_SIGNAL -> D_TRADING | cross_domain_violation | D_FUNDAMENTAL_SIGNAL | D_TRADING | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_CODE_QUALITY | 跨域违规: D_GOVERNANCE -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOVERNANCE | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOVERNANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOVERNANCE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRASTRUCTURE | 跨域违规: D_GOVERNANCE -> D_INFRASTRUCTURE | cross_domain_violation | D_GOVERNANCE | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | open |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | open |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOVERNANCE | 跨域违规: D_GOV_AUDIT -> D_GOVERNANCE | cross_domain_violation | D_GOV_AUDIT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_AUDIT -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_AUDIT | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_AUDIT-D_REPORTING | 跨域违规: D_GOV_AUDIT -> D_REPORTING | cross_domain_violation | D_GOV_AUDIT | D_REPORTING | error | open |
| V-CROSS-D_GOV_AUDIT-D_SHARED | 跨域违规: D_GOV_AUDIT -> D_SHARED | cross_domain_violation | D_GOV_AUDIT | D_SHARED | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOVERNANCE | 跨域违规: D_GOV_CODE_QUALITY -> D_GOVERNANCE | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_INFRA_RUNTIME | 跨域违规: D_GOV_CODE_QUALITY -> D_INFRA_RUNTIME | cross_domain_violation | D_GOV_CODE_QUALITY | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_SHARED | 跨域违规: D_GOV_CODE_QUALITY -> D_SHARED | cross_domain_violation | D_GOV_CODE_QUALITY | D_SHARED | error | open |
| V-CROSS-D_GOV_DRIFT-D_SHARED | 跨域违规: D_GOV_DRIFT -> D_SHARED | cross_domain_violation | D_GOV_DRIFT | D_SHARED | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_AUDIT | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_AUDIT | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRASTRUCTURE | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRASTRUCTURE | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_FACTOR | 跨域违规: D_GOV_OPS_RESILIENCE -> D_FACTOR | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_FACTOR | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_GOVERNANCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INFRA_A2A | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INFRA_A2A | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTEGRATION | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTEGRATION | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_INTELLIGENCE | 跨域违规: D_GOV_OPS_RESILIENCE -> D_INTELLIGENCE | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOV_OPS_RESILIENCE-D_SHARED | 跨域违规: D_GOV_OPS_RESILIENCE -> D_SHARED | cross_domain_violation | D_GOV_OPS_RESILIENCE | D_SHARED | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | open |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | open |
| V-CROSS-D_INTELLIGENCE-D_GOVERNANCE | 跨域违规: D_INTELLIGENCE -> D_GOVERNANCE | cross_domain_violation | D_INTELLIGENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | open |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | open |
| V-CROSS-D_ORCHESTRATOR-D_AUTONOMY_CORE | 跨域违规: D_ORCHESTRATOR -> D_AUTONOMY_CORE | cross_domain_violation | D_ORCHESTRATOR | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | open |
| V-CROSS-D_ORCHESTRATOR-D_INFRA_RUNTIME | 跨域违规: D_ORCHESTRATOR -> D_INFRA_RUNTIME | cross_domain_violation | D_ORCHESTRATOR | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_ORCHESTRATOR-D_INTEGRATION | 跨域违规: D_ORCHESTRATOR -> D_INTEGRATION | cross_domain_violation | D_ORCHESTRATOR | D_INTEGRATION | error | open |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | open |
| V-CROSS-D_PF_ALLOC-D_INFRASTRUCTURE | 跨域违规: D_PF_ALLOC -> D_INFRASTRUCTURE | cross_domain_violation | D_PF_ALLOC | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | open |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | open |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
