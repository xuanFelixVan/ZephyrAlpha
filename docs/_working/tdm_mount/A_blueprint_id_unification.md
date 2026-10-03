---
ttl: task_bound
completes_when: 总筹消费并裁决未匹配清单后本件转归档
title: "任务A·蓝图 module_id 统一清单（机生）"
owner: st-tdm-mount-flash-20261003
generation: machine_generated
generator: .runtime/tmp/tdm_mount/task_a_fill_ids.py（本批一次性脚本，不入产）
---

# 任务A·蓝图 module_id 统一清单

> 匹配真源=depgraph PG nodes 表（三链优先级：blueprint_dir_node > node_blueprint_id > dir_path_node）；未命中不编造进清单。

## 计数（字段，勿散文引用）

- total_blueprints: 306
- already_with_module_id: 158
- filled_now: 144
- unmatched: 4
- bad_format_existing: 0

## 分域补齐数

| 域 | 补齐数 |
|---|---|
| _domain_signal | 61 |
| _domain_risk | 6 |
| _domain_position | 2 |
| _domain_trading | 4 |
| _domain_sell_decision | 0 |
| _domain_execution_core | 1 |
| _domain_regime | 4 |
| _domain_factor | 8 |
| _domain_portfolio_core | 6 |
| _domain_portfolio_alloc | 2 |
| _domain_plan_engine | 9 |
| _domain_autonomy_core | 15 |
| _domain_backtest | 2 |
| _domain_simulation | 2 |
| _domain_fundamental_signal | 2 |
| _domain_signal_quality | 4 |
| _domain_ex_sor | 1 |
| _domain_mkt_data | 0 |
| _domain_execution_sim | 1 |
| _domain_digital_twin | 1 |
| _domain_pf_alloc | 0 |
| _domain_ml_serve | 0 |
| _domain_machine_learning_train | 13 |

## 本次补齐明细（144 行）

| 域 | 蓝图 | module_id | 匹配源 |
|---|---|---|---|
| _domain_signal | docs/03_modules/_domain_signal/auction_microstructure_analyzer/blueprint.md | MOD-SIG-089 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/banker_pattern_simulator/blueprint.md | MOD-SIG-113 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/bottom_confirmation_entry/blueprint.md | MOD-SIG-103 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/calendar_effects_model/blueprint.md | MOD-SIG-122 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/capital_behavior_orchestrator/blueprint.md | MOD-SIG-088 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/causal_ml_engine/blueprint.md | MOD-SIG-127 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/crowd_game_simulator/blueprint.md | MOD-SIG-114 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/day_trade_pnl_estimator/blueprint.md | MOD-SIG-132 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/event_causal_reasoner/blueprint.md | MOD-SIG-112 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/event_conditional_density/blueprint.md | MOD-SIG-123 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/extreme_sentiment_reversal_detector/blueprint.md | MOD-SIG-099 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/factor_result_bridge/blueprint.md | MOD-SIG-087 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/fake_move_distribution/blueprint.md | MOD-SIG-124 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/false_breakout_trap_detector/blueprint.md | MOD-SIG-100 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/futures_basis_monitor/blueprint.md | MOD-SIG-058 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/gap_fill_model/blueprint.md | MOD-SIG-092 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/industry_chain_graph/blueprint.md | MOD-SIG-125 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/intraday_size_style/blueprint.md | MOD-SIG-120 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/intraday_volume_orderflow/blueprint.md | MOD-SIG-093 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/lhb_premium_analyzer/blueprint.md | MOD-SIG-057 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/limit_up_ecosystem_leadership/blueprint.md | MOD-SIG-097 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/limit_up_potential_scorer/blueprint.md | MOD-SIG-102 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/mainline_candidates/blueprint.md | MOD-SIG-061 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/multi_factor_timing_overlay/blueprint.md | MOD-SIG-108 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/multi_indicator_divergence/blueprint.md | MOD-SIG-095 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/next_day_probability_gate/blueprint.md | MOD-SIG-104 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/option_sentiment/blueprint.md | MOD-SIG-059 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/orderflow_network_panic/blueprint.md | MOD-SIG-121 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/overnight_conduction_model/blueprint.md | MOD-SIG-117 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/overnight_return_expectancy/blueprint.md | MOD-SIG-107 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md | MOD-SIG-145 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/pattern_evidence_certifier/blueprint.md | MOD-SIG-148 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/pattern_lifecycle/blueprint.md | MOD-SIG-149 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/pattern_match_strategy_library/blueprint.md | MOD-SIG-105 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/pattern_series_transform/blueprint.md | MOD-SIG-146 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/pattern_signal_runtime/blueprint.md | MOD-SIG-147 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/pattern_to_signal_mapper/blueprint.md | MOD-SIG-115 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/relative_strength_screener/blueprint.md | MOD-SIG-096 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/risk_event_consumer/blueprint.md | MOD-SIG-088 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/sector_crowding_launch/blueprint.md | MOD-SIG-119 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/sector_divergence/blueprint.md | MOD-SIG-060 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/sector_leader/blueprint.md | MOD-SIG-062 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/sector_momentum_persistence/blueprint.md | MOD-SIG-098 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/selection_funnel_skeleton/blueprint.md | MOD-SIG-086 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/sell_news_overdraft_detector/blueprint.md | MOD-SIG-106 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/sentiment_price_divergence/blueprint.md | MOD-SIG-101 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/shared_kernel_sync/blueprint.md | MOD-SIG-133 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/signal_factory/blueprint.md | MOD-SIG-087 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/signal_weight_adjuster/blueprint.md | MOD-SIG-131 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/similar_day_inference/blueprint.md | MOD-SIG-063 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/stock_relation_gnn/blueprint.md | MOD-SIG-126 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/strategy_cross_vote_funnel/blueprint.md | MOD-SIG-109 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/strategy_decay_certifier/blueprint.md | MOD-SIG-150 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/strategy_matrix_3d/blueprint.md | MOD-SIG-130 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/supply_chain_momentum/blueprint.md | MOD-SIG-118 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/t0_trading_pipeline/blueprint.md | MOD-SIG-090 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/tcp_rm_conformal/blueprint.md | MOD-SIG-128 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/unified_pattern_engine/blueprint.md | MOD-SIG-091 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/volume_regime_adaptive/blueprint.md | MOD-SIG-129 | depgraph:node_blueprint_id |
| _domain_signal | docs/03_modules/_domain_signal/wyckoff_accumulation_signal/blueprint.md | MOD-SIG-094 | depgraph:blueprint_dir_node |
| _domain_signal | docs/03_modules/_domain_signal/wyckoff_secondary_test/blueprint.md | MOD-SIG-116 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/hedge_execution_skill/blueprint.md | MOD-RK-042 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/risk_contagion_modeler/blueprint.md | MOD-RK-046 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/risk_policy_persister/blueprint.md | MOD-RK-044 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/risk_signal_sequencer/blueprint.md | MOD-RK-41 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/var_data_prefetcher/blueprint.md | MOD-RK-043 | depgraph:node_blueprint_id |
| _domain_risk | docs/03_modules/_domain_risk/var_query_builder/blueprint.md | MOD-RK-045 | depgraph:node_blueprint_id |
| _domain_position | docs/03_modules/_domain_position/core_satellite_allocator/blueprint.md | MOD-POS-025 | depgraph:node_blueprint_id |
| _domain_position | docs/03_modules/_domain_position/position_adjudication_center/blueprint.md | MOD-POS-024 | depgraph:node_blueprint_id |
| _domain_trading | docs/03_modules/_domain_trading/reference_data_manager/blueprint.md | MOD-TRADING-014 | depgraph:node_blueprint_id |
| _domain_trading | docs/03_modules/_domain_trading/settlement_record_aggregate/blueprint.md | MOD-TRADING-010 | depgraph:node_blueprint_id |
| _domain_trading | docs/03_modules/_domain_trading/three_way_reconciliation/blueprint.md | MOD-TRADING-013 | depgraph:node_blueprint_id |
| _domain_trading | docs/03_modules/_domain_trading/trading_order_aggregate/blueprint.md | MOD-TRADING-009 | depgraph:node_blueprint_id |
| _domain_execution_core | docs/03_modules/_domain_execution_core/execution_param_optimizer/blueprint.md | MOD-EX-064 | depgraph:node_blueprint_id |
| _domain_regime | docs/03_modules/_domain_regime/cross_sectional_features/blueprint.md | MOD-REGIME-007 | depgraph:node_blueprint_id |
| _domain_regime | docs/03_modules/_domain_regime/market_forecast_fusion/blueprint.md | MOD-REGIME-012 | depgraph:node_blueprint_id |
| _domain_regime | docs/03_modules/_domain_regime/style_regime_model/blueprint.md | MOD-REGIME-014 | depgraph:node_blueprint_id |
| _domain_regime | docs/03_modules/_domain_regime/volatility_squeeze_breakout/blueprint.md | MOD-REGIME-013 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/auto_feature_discoverer/blueprint.md | MOD-FAC-001 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/factor_lifecycle_runner/blueprint.md | MOD-L02-LIFECYCLE | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/factor_model_co_evaluator/blueprint.md | MOD-FAC-005 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/factor_vote_mining/blueprint.md | MOD-FAC-004 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/gp_strategy_discovery/blueprint.md | MOD-FAC-003 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/llm_evolutionary_search/blueprint.md | MOD-FAC-006 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/signature_feature_extractor/blueprint.md | MOD-FAC-002 | depgraph:node_blueprint_id |
| _domain_factor | docs/03_modules/_domain_factor/strategy_iteration_upgrader/blueprint.md | MOD-FAC-007 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/exposure_manager/blueprint.md | MOD-PF-011 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/funnel_portfolio_adjudicator/blueprint.md | MOD-PF-010 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/rebalance_cost_analyzer/blueprint.md | MOD-PF-014 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/rl_portfolio_execution/blueprint.md | MOD-PF-013 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/strategy_capacity_estimator/blueprint.md | MOD-PF-012 | depgraph:node_blueprint_id |
| _domain_portfolio_core | docs/03_modules/_domain_portfolio_core/strategy_factory/blueprint.md | MOD-PF-009 | depgraph:node_blueprint_id |
| _domain_portfolio_alloc | docs/03_modules/_domain_portfolio_alloc/regime_bma_weighting/blueprint.md | MOD-PA-015 | depgraph:node_blueprint_id |
| _domain_portfolio_alloc | docs/03_modules/_domain_portfolio_alloc/strategy_screener_3d/blueprint.md | MOD-PA-014 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/boundary_revision_engine/blueprint.md | MOD-PLAN-006 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/llm_premarket_analysis/blueprint.md | MOD-PLAN-007 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/overnight_boundary_reviser/blueprint.md | MOD-PLAN-004 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/plan_deviation_monitor/blueprint.md | MOD-PLAN-022 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/premarket_workflow/blueprint.md | MOD-PLAN-021 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/premarket_workflow_engine/blueprint.md | MOD-PLAN-023 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/scenario_planner/blueprint.md | MOD-PLAN-005 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/scenario_playbook/blueprint.md | MOD-PLAN-019 | depgraph:node_blueprint_id |
| _domain_plan_engine | docs/03_modules/_domain_plan_engine/track_fusion/blueprint.md | MOD-PLAN-020 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/ai_ops_autonomy_card/blueprint.md | MOD-AU-013 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/autonomy_boundary_gate/blueprint.md | MOD-AU-001 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/autonomy_level_registry/blueprint.md | MOD-AU-005 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/execution_layer_agents/blueprint.md | MOD-EXE-AGENTS | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/kill_switch_orchestrator/blueprint.md | MOD-AU-002 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/knowledge_classifier/blueprint.md | MOD-FACTORY-001 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/module_mapper/blueprint.md | MOD-FACTORY-002 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/non_ai_boundary_guard/blueprint.md | MOD-AU-012 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/per_agent_gate/blueprint.md | MOD-AU-006 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/researcher_agent/blueprint.md | MOD-AU-008 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/risk_manager_agent/blueprint.md | MOD-AU-007 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/signal_analyst_agent/blueprint.md | MOD-AU-009 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/t0_trader_agent/blueprint.md | MOD-AU-011 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/timing_analyst_agent/blueprint.md | MOD-AU-010 | depgraph:node_blueprint_id |
| _domain_autonomy_core | docs/03_modules/_domain_autonomy_core/vote_review_shell/blueprint.md | MOD-VOTE_REVIEW_SHELL | depgraph:node_blueprint_id |
| _domain_backtest | docs/03_modules/_domain_backtest/layered_validation_pipeline/blueprint.md | MOD-BT-027 | depgraph:node_blueprint_id |
| _domain_backtest | docs/03_modules/_domain_backtest/strategy_cpcv_matrix/blueprint.md | MOD-BT-028 | depgraph:node_blueprint_id |
| _domain_simulation | docs/03_modules/_domain_simulation/overfitting_protection_gate/blueprint.md | MOD-SIM-028 | depgraph:node_blueprint_id |
| _domain_simulation | docs/03_modules/_domain_simulation/quality_assurance_selfdrive/blueprint.md | MOD-AUDITTEST-001 | depgraph:node_blueprint_id |
| _domain_fundamental_signal | docs/03_modules/_domain_fundamental_signal/pead_event_model/blueprint.md | MOD-SIG-110 | depgraph:node_blueprint_id |
| _domain_fundamental_signal | docs/03_modules/_domain_fundamental_signal/trace_context_store/blueprint.md | MOD-SIG-111 | depgraph:node_blueprint_id |
| _domain_signal_quality | docs/03_modules/_domain_signal_quality/signal_dedup/blueprint.md | MOD-SIGQC-003 | depgraph:node_blueprint_id |
| _domain_signal_quality | docs/03_modules/_domain_signal_quality/signal_degradation_monitor/blueprint.md | MOD-SIGQC-004 | depgraph:node_blueprint_id |
| _domain_signal_quality | docs/03_modules/_domain_signal_quality/signal_explainability_guarantor/blueprint.md | MOD-SIGQC-006 | depgraph:node_blueprint_id |
| _domain_signal_quality | docs/03_modules/_domain_signal_quality/signal_quality_benchmark/blueprint.md | MOD-SIGQC-005 | depgraph:node_blueprint_id |
| _domain_ex_sor | docs/03_modules/_domain_ex_sor/sor_agent/blueprint.md | MOD-XS-015 | depgraph:node_blueprint_id |
| _domain_execution_sim | docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md | MOD-EXSIM-001 | depgraph:node_blueprint_id |
| _domain_digital_twin | docs/03_modules/_domain_digital_twin/market_twin_simulator/blueprint.md | MOD-DT-001 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/continual_learning_antiforget/blueprint.md | MOD-ML-018 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/decision_annotation_dataset/blueprint.md | MOD-ML-014 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/decision_tree_decision_architecture/blueprint.md | MOD-ML-016 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/kan_density_head/blueprint.md | MOD-ML-017 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/ml_model_factory/blueprint.md | MOD-ML-013 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/model_version_registry/blueprint.md | MOD-ML-012 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/patchtst_density_encoder/blueprint.md | MOD-ML-011 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/qnn_two_stage/blueprint.md | MOD-ML-010 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/reproducibility_manager/blueprint.md | MOD-ML-020 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/research_asset_versioning/blueprint.md | MOD-ML-022 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/research_data_manager/blueprint.md | MOD-ML-019 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/research_data_sandbox/blueprint.md | MOD-ML-021 | depgraph:node_blueprint_id |
| _domain_machine_learning_train | docs/03_modules/_domain_machine_learning_train/ts_augmentation/blueprint.md | MOD-ML-015 | depgraph:node_blueprint_id |

## 已有 module_id（校验过，158 行）

- 其中同时带 blueprint_id 的: 13
- 已档未改（不重复写）: 158

## 未匹配清单（4 行，逐条带已查源+原因）

- _domain_ml_serve | docs/03_modules/_domain_ml_serve/codegen_model_adapter/blueprint.md | bid=MOD-MLS-003 | 原因: depgraph 无该 blueprint_id 节点且目录路径未注册
- _domain_ml_serve | docs/03_modules/_domain_ml_serve/deep_review_model_adapter/blueprint.md | bid=MOD-MLS-004 | 原因: depgraph 无该 blueprint_id 节点且目录路径未注册
- _domain_ml_serve | docs/03_modules/_domain_ml_serve/model_compression_accelerator/blueprint.md | bid=MOD-MLS-002 | 原因: depgraph 无该 blueprint_id 节点且目录路径未注册
- _domain_ml_serve | docs/03_modules/_domain_ml_serve/model_drift_monitor/blueprint.md | bid=MOD-MLS-001 | 原因: depgraph 无该 blueprint_id 节点且目录路径未注册

## 未匹配四条考古注记（2026-10-03 实查）

- depgraph nodes 全表 `blueprint_id LIKE 'MOD-MLS%'` 零命中——ml_serve 四蓝图（MOD-MLS-001~004）的模块从未入图；盘上唯一关联物=algo_flow 配置册（docs/03_modules/_domain_ml_serve/algo_flow/*.yaml，config 节点无 blueprint_id）。
- 相关代码的图内近邻：tests/model/test_model_drift_monitor.py 注册在 MOD-INF-023（非 MOD-MLS-001）。
- 结论：四条属「蓝图有 ID、架构图无节点」的真孤儿候选，补 ID 前须先补图（施工单禁发明/禁照抄无真源 ID，故不填）；交总筹裁决（补图 or 蓝图退役）。
