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
| 约束总数 | 172 |
| Open（未解决） | 172 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 72 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| cross_domain_violation | 60 |
| layer_violation | 11 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-6269370 | 孤儿节点: 6269370 | orphan_node | D_INFRA_RUNTIME |  | warn | advisory | 节点 6269370 路径 docs/01_policies_and_standards/_registry/catal... |
| V-ORPHAN-6772868 | 孤儿节点: 6772868 | orphan_node |  |  | warn | advisory | 节点 6772868 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-6772880 | 孤儿节点: 6772880 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 6772880 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-6772888 | 孤儿节点: 6772888 | orphan_node | D_DATA |  | warn | advisory | 节点 6772888 路径 src/zephyr/data/backfill_checker.py 未注册到目录树 |
| V-ORPHAN-6772890 | 孤儿节点: 6772890 | orphan_node | D_DATA |  | warn | advisory | 节点 6772890 路径 src/zephyr/data/capability_validator.py 未注册到目录... |
| V-ORPHAN-6772892 | 孤儿节点: 6772892 | orphan_node | D_DATA |  | warn | advisory | 节点 6772892 路径 src/zephyr/data/error_classifier.py 未注册到目录树 |
| V-ORPHAN-6772895 | 孤儿节点: 6772895 | orphan_node | D_DATA |  | warn | advisory | 节点 6772895 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-6772896 | 孤儿节点: 6772896 | orphan_node | D_DATA |  | warn | advisory | 节点 6772896 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-6772897 | 孤儿节点: 6772897 | orphan_node | D_DATA |  | warn | advisory | 节点 6772897 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-6772899 | 孤儿节点: 6772899 | orphan_node | D_DATA |  | warn | advisory | 节点 6772899 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-6772900 | 孤儿节点: 6772900 | orphan_node | D_DATA |  | warn | advisory | 节点 6772900 路径 src/zephyr/data/local_replay.py 未注册到目录树 |
| V-ORPHAN-6772902 | 孤儿节点: 6772902 | orphan_node | D_DATA |  | warn | advisory | 节点 6772902 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-6772903 | 孤儿节点: 6772903 | orphan_node | D_DATA |  | warn | advisory | 节点 6772903 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-6772906 | 孤儿节点: 6772906 | orphan_node | D_DATA |  | warn | advisory | 节点 6772906 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-6772907 | 孤儿节点: 6772907 | orphan_node | D_DATA |  | warn | advisory | 节点 6772907 路径 src/zephyr/data/table_registry.py 未注册到目录树 |
| V-ORPHAN-6772908 | 孤儿节点: 6772908 | orphan_node | D_DATA |  | warn | advisory | 节点 6772908 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-6772910 | 孤儿节点: 6772910 | orphan_node | D_DATA |  | warn | advisory | 节点 6772910 路径 src/zephyr/data/ch_config.py 未注册到目录树 |
| V-ORPHAN-6772912 | 孤儿节点: 6772912 | orphan_node | D_DATA |  | warn | advisory | 节点 6772912 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-6772913 | 孤儿节点: 6772913 | orphan_node | D_DATA |  | warn | advisory | 节点 6772913 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-6772918 | 孤儿节点: 6772918 | orphan_node | D_DATA |  | warn | advisory | 节点 6772918 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-6772919 | 孤儿节点: 6772919 | orphan_node | D_DATA |  | warn | advisory | 节点 6772919 路径 src/zephyr/data/trading_calendar.py 未注册到目录树 |
| V-ORPHAN-6772920 | 孤儿节点: 6772920 | orphan_node | D_DATA |  | warn | advisory | 节点 6772920 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-6772921 | 孤儿节点: 6772921 | orphan_node | D_DATA |  | warn | advisory | 节点 6772921 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-6772922 | 孤儿节点: 6772922 | orphan_node | D_DATA |  | warn | advisory | 节点 6772922 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-6772923 | 孤儿节点: 6772923 | orphan_node | D_DATA |  | warn | advisory | 节点 6772923 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-6772924 | 孤儿节点: 6772924 | orphan_node | D_DATA |  | warn | advisory | 节点 6772924 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-6772925 | 孤儿节点: 6772925 | orphan_node | D_DATA |  | warn | advisory | 节点 6772925 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-6772926 | 孤儿节点: 6772926 | orphan_node | D_DATA |  | warn | advisory | 节点 6772926 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-6772927 | 孤儿节点: 6772927 | orphan_node | D_DATA |  | warn | advisory | 节点 6772927 路径 src/zephyr/data/ch_reader.py 未注册到目录树 |
| V-ORPHAN-6772928 | 孤儿节点: 6772928 | orphan_node | D_DATA |  | warn | advisory | 节点 6772928 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-6772932 | 孤儿节点: 6772932 | orphan_node | D_DATA |  | warn | advisory | 节点 6772932 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-6772943 | 孤儿节点: 6772943 | orphan_node | D_DATA |  | warn | advisory | 节点 6772943 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-6772945 | 孤儿节点: 6772945 | orphan_node | D_DATA |  | warn | advisory | 节点 6772945 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-6772965 | 孤儿节点: 6772965 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6772965 路径 src/zephyr/ex_core/adapters/risk_validation_br... |
| V-ORPHAN-6772967 | 孤儿节点: 6772967 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6772967 路径 src/zephyr/ex_core/adapters/__init__.py 未注册到目录... |
| V-ORPHAN-6772976 | 孤儿节点: 6772976 | orphan_node | D_EX_CORE |  | warn | advisory | 节点 6772976 路径 src/zephyr/ex_core/adapters/miniqmt_broker.py ... |
| V-ORPHAN-6772979 | 孤儿节点: 6772979 | orphan_node | D_EX_SOR |  | warn | advisory | 节点 6772979 路径 src/zephyr/ex_sor/_extensions/__init__.py 未注册到... |
| V-ORPHAN-6772984 | 孤儿节点: 6772984 | orphan_node | D_FACTOR |  | warn | advisory | 节点 6772984 路径 src/zephyr/factor/value_factor.py 未注册到目录树 |
| V-ORPHAN-6772987 | 孤儿节点: 6772987 | orphan_node | D_FACTOR |  | warn | advisory | 节点 6772987 路径 src/zephyr/factor/momentum_factor.py 未注册到目录树 |
| V-ORPHAN-6773332 | 孤儿节点: 6773332 | orphan_node |  |  | warn | advisory | 节点 6773332 路径 src/zephyr/frontend/__init__.py 未注册到目录树 |
| V-ORPHAN-6773334 | 孤儿节点: 6773334 | orphan_node |  |  | warn | advisory | 节点 6773334 路径 src/zephyr/frontend/dashboard/__init__.py 未注册到... |
| V-ORPHAN-6773337 | 孤儿节点: 6773337 | orphan_node | D_FRONTEND |  | warn | advisory | 节点 6773337 路径 src/zephyr/frontend/dashboard/components/backt... |
| V-ORPHAN-6773348 | 孤儿节点: 6773348 | orphan_node |  |  | warn | advisory | 节点 6773348 路径 src/zephyr/frontend/dashboard/components/__ini... |
| V-ORPHAN-6773357 | 孤儿节点: 6773357 | orphan_node | D_FRONTEND |  | warn | advisory | 节点 6773357 路径 src/zephyr/frontend/dashboard/components/chart... |
| V-ORPHAN-6773365 | 孤儿节点: 6773365 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773365 路径 src/zephyr/governance/adapters/risk_validation... |
| V-ORPHAN-6773367 | 孤儿节点: 6773367 | orphan_node |  |  | warn | advisory | 节点 6773367 路径 src/zephyr/governance/adapters/__init__.py 未注册... |
| V-ORPHAN-6773379 | 孤儿节点: 6773379 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773379 路径 src/zephyr/governance/adapters/simulation_brok... |
| V-ORPHAN-6773408 | 孤儿节点: 6773408 | orphan_node | D_GOV_AUDIT |  | warn | advisory | 节点 6773408 路径 src/zephyr/governance/audit/default_attributio... |
| V-ORPHAN-6773411 | 孤儿节点: 6773411 | orphan_node |  |  | warn | advisory | 节点 6773411 路径 src/zephyr/governance/compliance_gate_a6/__ini... |
| V-ORPHAN-6773431 | 孤儿节点: 6773431 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773431 路径 src/zephyr/governance/data_governance/akshare_... |
| V-ORPHAN-6773436 | 孤儿节点: 6773436 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773436 路径 src/zephyr/governance/data_governance/miniqmt_... |
| V-ORPHAN-6773442 | 孤儿节点: 6773442 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773442 路径 src/zephyr/governance/engine/pipeline_base.py ... |
| V-ORPHAN-6773448 | 孤儿节点: 6773448 | orphan_node |  |  | warn | advisory | 节点 6773448 路径 src/zephyr/governance/engine/__init__.py 未注册到目... |
| V-ORPHAN-6773475 | 孤儿节点: 6773475 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773475 路径 src/zephyr/governance/implementations/default_... |
| V-ORPHAN-6773479 | 孤儿节点: 6773479 | orphan_node |  |  | warn | advisory | 节点 6773479 路径 src/zephyr/governance/implementations/__init__... |
| V-ORPHAN-6773508 | 孤儿节点: 6773508 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773508 路径 src/zephyr/governance/observability_governance... |
| V-ORPHAN-6773510 | 孤儿节点: 6773510 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773510 路径 src/zephyr/governance/implementations/default_... |
| V-ORPHAN-6773636 | 孤儿节点: 6773636 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 6773636 路径 src/zephyr/governance/strategies/strategy_regi... |
| V-ORPHAN-6773642 | 孤儿节点: 6773642 | orphan_node |  |  | warn | advisory | 节点 6773642 路径 src/zephyr/governance/strategies/__init__.py 未... |
| V-ORPHAN-6773775 | 孤儿节点: 6773775 | orphan_node | D_SECURITY |  | warn | advisory | 节点 6773775 路径 src/zephyr/gov_drift/alert_router.py 未注册到目录树 |
| V-ORPHAN-6773819 | 孤儿节点: 6773819 | orphan_node | D_SECURITY |  | warn | advisory | 节点 6773819 路径 src/zephyr/gov_drift/runbook_generator.py 未注册到... |
| V-ORPHAN-6773850 | 孤儿节点: 6773850 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 6773850 路径 src/zephyr/gov_enforcement/__init__.py 未注册到目录树 |
| V-ORPHAN-6773851 | 孤儿节点: 6773851 | orphan_node | D_GOV_DRIFT |  | warn | advisory | 节点 6773851 路径 src/zephyr/gov_drift/detector_core/bridges/dri... |
| V-ORPHAN-6774406 | 孤儿节点: 6774406 | orphan_node | D_INTEGRATION |  | warn | advisory | 节点 6774406 路径 src/zephyr/integration/vector_memory/vector_br... |
| V-ORPHAN-6774436 | 孤儿节点: 6774436 | orphan_node | D_INTELLIGENCE |  | warn | advisory | 节点 6774436 路径 src/zephyr/intelligence/model_profiling/exam_r... |
| V-ORPHAN-6774464 | 孤儿节点: 6774464 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6774464 路径 src/zephyr/ml_train/inference_base.py 未注册到目录树 |
| V-ORPHAN-6774466 | 孤儿节点: 6774466 | orphan_node |  |  | warn | advisory | 节点 6774466 路径 src/zephyr/ml_train/__init__.py 未注册到目录树 |
| V-ORPHAN-6774469 | 孤儿节点: 6774469 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6774469 路径 src/zephyr/ml_train/implementations/default_in... |
| V-ORPHAN-6774470 | 孤儿节点: 6774470 | orphan_node |  |  | warn | advisory | 节点 6774470 路径 src/zephyr/ml_train/implementations/__init__.p... |
| V-ORPHAN-6774474 | 孤儿节点: 6774474 | orphan_node | D_ML_TRAIN |  | warn | advisory | 节点 6774474 路径 src/zephyr/ml_train/trainer_base.py 未注册到目录树 |
| V-ORPHAN-6774565 | 孤儿节点: 6774565 | orphan_node | D_PF_CORE |  | warn | advisory | 节点 6774565 路径 src/zephyr/pf_core/strategy_engine/__init__.py... |
| V-ORPHAN-6774575 | 孤儿节点: 6774575 | orphan_node | D_REPORTING |  | warn | advisory | 节点 6774575 路径 src/zephyr/reporting/default_attribution_engin... |
| V-ORPHAN-6774580 | 孤儿节点: 6774580 | orphan_node | D_REPORTING |  | warn | advisory | 节点 6774580 路径 src/zephyr/reporting/default_tca_engine.py 未注册... |
| V-ORPHAN-6774588 | 孤儿节点: 6774588 | orphan_node |  |  | warn | advisory | 节点 6774588 路径 src/zephyr/risk/__init__.py 未注册到目录树 |
| V-ORPHAN-6774589 | 孤儿节点: 6774589 | orphan_node |  |  | warn | advisory | 节点 6774589 路径 src/zephyr/reporting/__init__.py 未注册到目录树 |
| V-ORPHAN-6774598 | 孤儿节点: 6774598 | orphan_node |  |  | warn | advisory | 节点 6774598 路径 src/zephyr/risk/implementations/__init__.py 未注... |
| V-ORPHAN-6775059 | 孤儿节点: 6775059 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775059 路径 src/zephyr/signal_fundamental/__init__.py 未注册到... |
| V-ORPHAN-6775061 | 孤儿节点: 6775061 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775061 路径 src/zephyr/signal_fundamental/capital/capital_... |
| V-ORPHAN-6775063 | 孤儿节点: 6775063 | orphan_node |  |  | warn | advisory | 节点 6775063 路径 src/zephyr/signal_fundamental/capital/__init__... |
| V-ORPHAN-6775064 | 孤儿节点: 6775064 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775064 路径 src/zephyr/signal_fundamental/capital/capital_... |
| V-ORPHAN-6775065 | 孤儿节点: 6775065 | orphan_node |  |  | warn | advisory | 节点 6775065 路径 src/zephyr/signal_fundamental/combiner/impl/__... |
| V-ORPHAN-6775066 | 孤儿节点: 6775066 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775066 路径 src/zephyr/signal_fundamental/capital/default_... |
| V-ORPHAN-6775067 | 孤儿节点: 6775067 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775067 路径 src/zephyr/signal_fundamental/gen/aggregator_b... |
| V-ORPHAN-6775069 | 孤儿节点: 6775069 | orphan_node |  |  | warn | advisory | 节点 6775069 路径 src/zephyr/signal_fundamental/combiner/__init_... |
| V-ORPHAN-6775072 | 孤儿节点: 6775072 | orphan_node |  |  | warn | advisory | 节点 6775072 路径 src/zephyr/signal_fundamental/gen/implementati... |
| V-ORPHAN-6775074 | 孤儿节点: 6775074 | orphan_node |  |  | warn | advisory | 节点 6775074 路径 src/zephyr/signal_fundamental/gen/__init__.py ... |
| V-ORPHAN-6775076 | 孤儿节点: 6775076 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | advisory | 节点 6775076 路径 src/zephyr/signal_fundamental/strategy/capital... |
| V-ORPHAN-6775079 | 孤儿节点: 6775079 | orphan_node |  |  | warn | advisory | 节点 6775079 路径 src/zephyr/signal_fundamental/strategy/impleme... |
| V-ORPHAN-6775081 | 孤儿节点: 6775081 | orphan_node |  |  | warn | advisory | 节点 6775081 路径 src/zephyr/signal_fundamental/strategy/__init_... |
| V-ORPHAN-6775083 | 孤儿节点: 6775083 | orphan_node |  |  | warn | advisory | 节点 6775083 路径 src/zephyr/signal_fundamental/synth/__init__.p... |
| V-ORPHAN-6775092 | 孤儿节点: 6775092 | orphan_node |  |  | warn | advisory | 节点 6775092 路径 src/zephyr/simulation/__init__.py 未注册到目录树 |
| V-ORPHAN-6775094 | 孤儿节点: 6775094 | orphan_node |  |  | warn | advisory | 节点 6775094 路径 src/zephyr/simulation/implementations/__init__... |
| V-ORPHAN-6775169 | 孤儿节点: 6775169 | orphan_node | D_TRADING |  | warn | advisory | 节点 6775169 路径 src/zephyr/trading/trading_contracts/portfolio... |
| V-ORPHAN-6775173 | 孤儿节点: 6775173 | orphan_node | D_TRADING |  | warn | advisory | 节点 6775173 路径 src/zephyr/trading/trading_contracts/portfolio... |
| V-ORPHAN-6775174 | 孤儿节点: 6775174 | orphan_node |  |  | warn | advisory | 节点 6775174 路径 src/zephyr/trading/trading_contracts/portfolio... |
| V-ORPHAN-6775235 | 孤儿节点: 6775235 | orphan_node | D_DATA |  | warn | advisory | 节点 6775235 路径 scripts/ch/apply_market_tables_ddl.py 未注册到目录树 |
| V-ORPHAN-6775419 | 孤儿节点: 6775419 | orphan_node | D_GOV_SCRIPTS |  | warn | advisory | 节点 6775419 路径 scripts/governance/d5_architecture/generators/... |
| V-ORPHAN-6775424 | 孤儿节点: 6775424 | orphan_node | D_GOV_SCRIPTS |  | warn | advisory | 节点 6775424 路径 scripts/governance/d5_architecture/generators/... |
| V-ORPHAN-6775695 | 孤儿节点: 6775695 | orphan_node | D_GOV_SCRIPTS |  | warn | advisory | 节点 6775695 路径 scripts/governance/_sync/fix_orphan_deps.py 未注... |
| V-ORPHAN-6775711 | 孤儿节点: 6775711 | orphan_node | D_FRONTEND |  | warn | advisory | 节点 6775711 路径 scripts/tests/test_frontend_components.py 未注册到... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_DATA -> D_GOV_ENFORCEMENT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_FACTOR -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DETECTORS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOVERNANCE |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_DRIFT |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INTEGRATION |
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
| V-CROSS-D_GOV_RULE-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_RULE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_RULE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOV_RULE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_DATA |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_REPAIR |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_GOV_AUDIT |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_INTELLIGENCE |
| V-CROSS-D_INTELLIGENCE-D_GOVERNANCE | 跨域违规: D_INTELLIGENCE -> D_GOVERNANCE | cross_domain_violation | D_INTELLIGENCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_GOVERNANCE |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INTELLIGENCE -> D_INTEGRATION |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | gate | 跨域依赖未声明: D_ML_TRAIN -> D_TRADING |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_GOVERNANCE |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_SHARED |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | gate | 跨域依赖未声明: D_PF_CORE -> D_PF_ALLOC |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_REPORTING -> D_INFRASTRUCTURE |
| V-CROSS-D_SECURITY-D_GOV_DRIFT | 跨域违规: D_SECURITY -> D_GOV_DRIFT | cross_domain_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_DRIFT |
| V-CROSS-D_TRADING-D_INFRASTRUCTURE | 跨域违规: D_TRADING -> D_INFRASTRUCTURE | cross_domain_violation | D_TRADING | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_TRADING -> D_INFRASTRUCTURE |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 6772838 -> 6773700 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 6772739 -> 6773993 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 6772802 -> 6774415 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 6773281 -> 6773700 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 6773008 -> 6773562 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 6773009 -> 6773359 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 6773333 -> 6773562 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 6773349 -> 6775165 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 层级违规: 6773934 -> 6773354 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | gate | 层级违规: 6773921 -> 6773612 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 6773947 -> 6773952 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-6269370 | 孤儿节点: 6269370 | orphan_node | D_INFRA_RUNTIME |  | warn | open |
| V-ORPHAN-6772868 | 孤儿节点: 6772868 | orphan_node |  |  | warn | open |
| V-ORPHAN-6772880 | 孤儿节点: 6772880 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-6772888 | 孤儿节点: 6772888 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772890 | 孤儿节点: 6772890 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772892 | 孤儿节点: 6772892 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772895 | 孤儿节点: 6772895 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772896 | 孤儿节点: 6772896 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772897 | 孤儿节点: 6772897 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772899 | 孤儿节点: 6772899 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772900 | 孤儿节点: 6772900 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772902 | 孤儿节点: 6772902 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772903 | 孤儿节点: 6772903 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772906 | 孤儿节点: 6772906 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772907 | 孤儿节点: 6772907 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772908 | 孤儿节点: 6772908 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772910 | 孤儿节点: 6772910 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772912 | 孤儿节点: 6772912 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772913 | 孤儿节点: 6772913 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772918 | 孤儿节点: 6772918 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772919 | 孤儿节点: 6772919 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772920 | 孤儿节点: 6772920 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772921 | 孤儿节点: 6772921 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772922 | 孤儿节点: 6772922 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772923 | 孤儿节点: 6772923 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772924 | 孤儿节点: 6772924 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772925 | 孤儿节点: 6772925 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772926 | 孤儿节点: 6772926 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772927 | 孤儿节点: 6772927 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772928 | 孤儿节点: 6772928 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772932 | 孤儿节点: 6772932 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772943 | 孤儿节点: 6772943 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772945 | 孤儿节点: 6772945 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6772965 | 孤儿节点: 6772965 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6772967 | 孤儿节点: 6772967 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6772976 | 孤儿节点: 6772976 | orphan_node | D_EX_CORE |  | warn | open |
| V-ORPHAN-6772979 | 孤儿节点: 6772979 | orphan_node | D_EX_SOR |  | warn | open |
| V-ORPHAN-6772984 | 孤儿节点: 6772984 | orphan_node | D_FACTOR |  | warn | open |
| V-ORPHAN-6772987 | 孤儿节点: 6772987 | orphan_node | D_FACTOR |  | warn | open |
| V-ORPHAN-6773332 | 孤儿节点: 6773332 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773334 | 孤儿节点: 6773334 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773337 | 孤儿节点: 6773337 | orphan_node | D_FRONTEND |  | warn | open |
| V-ORPHAN-6773348 | 孤儿节点: 6773348 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773357 | 孤儿节点: 6773357 | orphan_node | D_FRONTEND |  | warn | open |
| V-ORPHAN-6773365 | 孤儿节点: 6773365 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773367 | 孤儿节点: 6773367 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773379 | 孤儿节点: 6773379 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773408 | 孤儿节点: 6773408 | orphan_node | D_GOV_AUDIT |  | warn | open |
| V-ORPHAN-6773411 | 孤儿节点: 6773411 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773431 | 孤儿节点: 6773431 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773436 | 孤儿节点: 6773436 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773442 | 孤儿节点: 6773442 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773448 | 孤儿节点: 6773448 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773475 | 孤儿节点: 6773475 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773479 | 孤儿节点: 6773479 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773508 | 孤儿节点: 6773508 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773510 | 孤儿节点: 6773510 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773636 | 孤儿节点: 6773636 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-6773642 | 孤儿节点: 6773642 | orphan_node |  |  | warn | open |
| V-ORPHAN-6773775 | 孤儿节点: 6773775 | orphan_node | D_SECURITY |  | warn | open |
| V-ORPHAN-6773819 | 孤儿节点: 6773819 | orphan_node | D_SECURITY |  | warn | open |
| V-ORPHAN-6773850 | 孤儿节点: 6773850 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-6773851 | 孤儿节点: 6773851 | orphan_node | D_GOV_DRIFT |  | warn | open |
| V-ORPHAN-6774406 | 孤儿节点: 6774406 | orphan_node | D_INTEGRATION |  | warn | open |
| V-ORPHAN-6774436 | 孤儿节点: 6774436 | orphan_node | D_INTELLIGENCE |  | warn | open |
| V-ORPHAN-6774464 | 孤儿节点: 6774464 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6774466 | 孤儿节点: 6774466 | orphan_node |  |  | warn | open |
| V-ORPHAN-6774469 | 孤儿节点: 6774469 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6774470 | 孤儿节点: 6774470 | orphan_node |  |  | warn | open |
| V-ORPHAN-6774474 | 孤儿节点: 6774474 | orphan_node | D_ML_TRAIN |  | warn | open |
| V-ORPHAN-6774565 | 孤儿节点: 6774565 | orphan_node | D_PF_CORE |  | warn | open |
| V-ORPHAN-6774575 | 孤儿节点: 6774575 | orphan_node | D_REPORTING |  | warn | open |
| V-ORPHAN-6774580 | 孤儿节点: 6774580 | orphan_node | D_REPORTING |  | warn | open |
| V-ORPHAN-6774588 | 孤儿节点: 6774588 | orphan_node |  |  | warn | open |
| V-ORPHAN-6774589 | 孤儿节点: 6774589 | orphan_node |  |  | warn | open |
| V-ORPHAN-6774598 | 孤儿节点: 6774598 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775059 | 孤儿节点: 6775059 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775061 | 孤儿节点: 6775061 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775063 | 孤儿节点: 6775063 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775064 | 孤儿节点: 6775064 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775065 | 孤儿节点: 6775065 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775066 | 孤儿节点: 6775066 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775067 | 孤儿节点: 6775067 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775069 | 孤儿节点: 6775069 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775072 | 孤儿节点: 6775072 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775074 | 孤儿节点: 6775074 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775076 | 孤儿节点: 6775076 | orphan_node | D_FUNDAMENTAL_SIGNAL |  | warn | open |
| V-ORPHAN-6775079 | 孤儿节点: 6775079 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775081 | 孤儿节点: 6775081 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775083 | 孤儿节点: 6775083 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775092 | 孤儿节点: 6775092 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775094 | 孤儿节点: 6775094 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775169 | 孤儿节点: 6775169 | orphan_node | D_TRADING |  | warn | open |
| V-ORPHAN-6775173 | 孤儿节点: 6775173 | orphan_node | D_TRADING |  | warn | open |
| V-ORPHAN-6775174 | 孤儿节点: 6775174 | orphan_node |  |  | warn | open |
| V-ORPHAN-6775235 | 孤儿节点: 6775235 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-6775419 | 孤儿节点: 6775419 | orphan_node | D_GOV_SCRIPTS |  | warn | open |
| V-ORPHAN-6775424 | 孤儿节点: 6775424 | orphan_node | D_GOV_SCRIPTS |  | warn | open |
| V-ORPHAN-6775695 | 孤儿节点: 6775695 | orphan_node | D_GOV_SCRIPTS |  | warn | open |
| V-ORPHAN-6775711 | 孤儿节点: 6775711 | orphan_node | D_FRONTEND |  | warn | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | open |
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
| V-CROSS-D_GOV_RULE-D_GOV_ENFORCEMENT | 跨域违规: D_GOV_RULE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOV_RULE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_DATA | 跨域违规: D_GOV_SCRIPTS -> D_DATA | cross_domain_violation | D_GOV_SCRIPTS | D_DATA | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | open |
| V-CROSS-D_INTEGRATION-D_GOV_AUDIT | 跨域违规: D_INTEGRATION -> D_GOV_AUDIT | cross_domain_violation | D_INTEGRATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_INTEGRATION-D_INTELLIGENCE | 跨域违规: D_INTEGRATION -> D_INTELLIGENCE | cross_domain_violation | D_INTEGRATION | D_INTELLIGENCE | error | open |
| V-CROSS-D_INTELLIGENCE-D_GOVERNANCE | 跨域违规: D_INTELLIGENCE -> D_GOVERNANCE | cross_domain_violation | D_INTELLIGENCE | D_GOVERNANCE | error | open |
| V-CROSS-D_INTELLIGENCE-D_INTEGRATION | 跨域违规: D_INTELLIGENCE -> D_INTEGRATION | cross_domain_violation | D_INTELLIGENCE | D_INTEGRATION | error | open |
| V-CROSS-D_ML_TRAIN-D_TRADING | 跨域违规: D_ML_TRAIN -> D_TRADING | cross_domain_violation | D_ML_TRAIN | D_TRADING | error | open |
| V-CROSS-D_ORCHESTRATOR-D_GOVERNANCE | 跨域违规: D_ORCHESTRATOR -> D_GOVERNANCE | cross_domain_violation | D_ORCHESTRATOR | D_GOVERNANCE | error | open |
| V-CROSS-D_ORCHESTRATOR-D_SHARED | 跨域违规: D_ORCHESTRATOR -> D_SHARED | cross_domain_violation | D_ORCHESTRATOR | D_SHARED | error | open |
| V-CROSS-D_PF_CORE-D_PF_ALLOC | 跨域违规: D_PF_CORE -> D_PF_ALLOC | cross_domain_violation | D_PF_CORE | D_PF_ALLOC | error | open |
| V-CROSS-D_REPORTING-D_INFRASTRUCTURE | 跨域违规: D_REPORTING -> D_INFRASTRUCTURE | cross_domain_violation | D_REPORTING | D_INFRASTRUCTURE | error | open |
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
