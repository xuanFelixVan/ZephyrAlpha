---
doc_type: audit_report
title: 四图对齐报告
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-08-04 10:44:05
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=906 / dataflow=270 / decision=693 / blueprint=164
- 问题总数: 49
  - 孤儿（仅一图）: 48
  - 状态漂移（blueprint 缺 design_maturity）: 0
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 1

## 1. 孤儿节点（仅一图存在）

| module_id | graph | 名称 / Name | entity_name |
|---|---|---|---|
| MOD-H1-REDIS-HOT | dataflow | — | MOD-H1-REDIS-HOT |
| CFG-rule-enforcement-registry | decision | — | layer:CFG-rule-enforcement-registry |
| CFG-rule-registry-collection | decision | — | layer:CFG-rule-registry-collection |
| CFG-scripts-registry | decision | — | layer:CFG-scripts-registry |
| CFG-test-suite-registry | decision | — | layer:CFG-test-suite-registry |
| MOD-CFG_RULE_ENFORCEMENT | depgraph | — | docs/01_policies_and_standards/_registry/catalogs/rule_enforcement_registry.yaml |
| MOD-CFG_RULE_REGISTRY | depgraph | 规则注册表收集 / rule_registry_collection | docs/01_policies_and_standards/_registry/catalogs/rule_registry_collection.yaml |
| MOD-CFG_SCRIPTS | depgraph | — | docs/01_policies_and_standards/_registry/catalogs/scripts_registry.yaml |
| MOD-CFG_TEST_SUITE | depgraph | 测试suite注册表 / test_suite_registry | docs/01_policies_and_standards/_registry/catalogs/test_suite_registry.yaml |
| MOD-GOV_ALIGN_BATTLE_MAP | depgraph | — | scripts/governance/align_battle_map.py |
| MOD-GOV_DEAD_PUBLIC_WRAPPER_RECONCILER | depgraph | — | src/zephyr/governance/audit/dead_public_wrapper_reconciler.py |
| MOD-GOV_DIAGNOSE_BREADTH | depgraph | diagnosebreadth失败 / diagnose_breadth_failed | scripts/diagnose_breadth_failed.py |
| MOD-GOV_DIAGNOSE_DEPGRAPH | depgraph | — | scripts/governance/d5_architecture/diagnose_depgraph.py |
| MOD-GOV_GATE_CHAIN | depgraph | — | scripts/governance/run_gate_chain.py |
| MOD-GOV_GENERATE_CANDIDATE_MODULE_REPORT | depgraph | — | scripts/governance/d5_architecture/generators/generate_candidate_module_report.py |
| MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | depgraph | — | src/zephyr/governance/audit/git_guard_bypass_reconciler.py |
| MOD-GOV_PHASE_A_BACKUP | depgraph | — | scripts/governance/_archive/one_off/phase_a_backup.py |
| MOD-GOV_TRANSLATION_COVERAGE_RECONCILER | depgraph | — | src/zephyr/governance/audit/translation_coverage_reconciler.py |
| MOD-GOV_ZOOMABLE_HTML | depgraph | 可缩放 Mermaid HTML 生成器（共享模块）。 / zoomable_html | scripts/governance/d5_architecture/generators/zoomable_html.py |
| MOD-INF-046 | depgraph | 测试残留目录一次性清理工具 | scripts/ops/cleanup_runtime_tmp_residue.py |
| MOD-POS_SERVICES | depgraph | — | src/zephyr/position/services/__init__.py |
| MOD-RUNTIME_INTRADAY | depgraph | — | src/zephyr/runtime/__init__.py |
| MOD-SIG-006 | depgraph | — | src/zephyr/signal_fundamental/audit/__init__.py |
| MOD-SIG-021 | depgraph | 机构行为分析器 / institutional_behavior_analyzer | src/zephyr/signal_ashare/institutional_behavior_analyzer.py |
| MOD-SIG-022 | depgraph | 资本流模式分析器 / capital_flow_pattern_analyzer | src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py |
| MOD-SIG-023 | depgraph | 短期股票选择器 / short_term_stock_selector | src/zephyr/signal_ashare/short_term_stock_selector.py |
| MOD-SIG-024 | depgraph | 日内买卖点分析器 / intraday_buy_sell_point_analyzer | src/zephyr/signal_ashare/intraday_buy_sell_point_analyzer.py |
| MOD-SIG-025 | depgraph | 市场情绪分析器 / market_sentiment_analyzer | src/zephyr/signal_ashare/market_sentiment_analyzer.py |
| MOD-SIG-026 | depgraph | 板块分析器 / sector_analyzer | src/zephyr/signal_ashare/sector_analyzer.py |
| MOD-SIG-033 | depgraph | 游资中继情绪引擎 / youzi_relay_emotion_engine | src/zephyr/signal_ashare/youzi_relay_emotion_engine.py |
| MOD-SIG-034 | depgraph | 量化短期强度引擎 / quant_short_term_strength_engine | src/zephyr/signal_ashare/quant_short_term_strength_engine.py |
| MOD-SIG-035 | depgraph | 双引擎融合决策引擎 / dual_engine_fusion_decision_engine | src/zephyr/signal_ashare/dual_engine_fusion_decision_engine.py |
| MOD-TEST-001 | depgraph | — | tests/governance/rule_bridge/test_gate_auto_registrar.py |
| MOD-TEST_GATE_INV_DRIFT | depgraph | 测试check门禁inventory漂移 / test_check_gate_inventory_drift | tests/governance/generators/test_check_gate_inventory_drift.py |
| MOD-TEST_GATE_REGISTRY_GEN | depgraph | 测试生成门禁注册表 / test_generate_gate_registry | tests/governance/generators/test_generate_gate_registry.py |
| MOD-TEST_METRICS_SERVER | depgraph | — | tests/zephyr/shared/observability/test_metrics_server.py |
| MOD-TEST_STRATEGY_RUNNER_TICK | depgraph | — | tests/pf_core/test_strategy_runner_tick.py |
| MOD-TEST_SURGE_FALL_STRATEGY | depgraph | — | tests/pf_core/test_intraday_surge_fall_strategy.py |
| MOD-XS-001 | depgraph | optimal订单路由器 / optimal_order_router | src/zephyr/ex_sor/core/optimal_order_router.py |
| MOD-XS-002 | depgraph | 经纪人适配器管理器 / broker_adapter_manager | src/zephyr/ex_sor/core/broker_adapter_manager.py |
| MOD-XS-004 | depgraph | 执行调度器 / execution_scheduler | src/zephyr/ex_sor/core/execution_scheduler.py |
| MOD-XS-005 | depgraph | 算法交易引擎 / algo_trading_engine | src/zephyr/ex_sor/core/algo_trading_engine.py |
| MOD-XS-011 | depgraph | 算法执行选择器 / algo_execution_selector | src/zephyr/ex_sor/core/algo_execution_selector.py |
| MOD-XS-013 | depgraph | — | src/zephyr/ex_sor/api/broker_api_connector.py |
| MOD-XS-014 | depgraph | — | src/zephyr/ex_sor/api/api_rate_limiter.py |
| MOD-requirements_version_sync | depgraph | — | scripts/governance/d8_doc_sync/requirements_version_sync_reconciler.py |
| SH-DB-003 | depgraph | — | src/zephyr/governance/persistence/battle_map_reader.py |
| SH-GOV-001 | depgraph | — | scripts/governance/oneoff/data_domain_audit_query.py |

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

> 无状态漂移。

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

| module_id | graph | 名称 / Name | entity_name |
|---|---|---|---|
| MOD-H1-REDIS-HOT | dataflow | — | MOD-H1-REDIS-HOT |

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
