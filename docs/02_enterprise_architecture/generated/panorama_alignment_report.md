# 三图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-09 05:46:06
- 数据源: depgraph (PostgreSQL)
- 三图节点数: depgraph=4414 / dataflow=27 / decision=154
- 问题总数: 4401
  - 孤儿（仅一图）: 4345
  - 状态漂移（design_maturity 不一致）: 4
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 52

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| aggregate.ohlc_bar | dataflow | aggregate.ohlc_bar |
| backtest.calc_metrics | dataflow | backtest.calc_metrics |
| backtest.fills | dataflow | backtest.fills |
| backtest.match_fills | dataflow | backtest.match_fills |
| backtest.nav_series | dataflow | backtest.nav_series |
| backtest.replay_ticks | dataflow | backtest.replay_ticks |
| backtest.result | dataflow | backtest.result |
| backtest.run_event_driven | dataflow | backtest.run_event_driven |
| backtest.target_weights | dataflow | backtest.target_weights |
| backtest.tick_event | dataflow | backtest.tick_event |
| backtest.update_portfolio | dataflow | backtest.update_portfolio |
| check.risk_limits | dataflow | check.risk_limits |
| compute.momentum_20d | dataflow | compute.momentum_20d |
| compute.value_factor | dataflow | compute.value_factor |
| execute.order | dataflow | execute.order |
| factor.momentum_20d | dataflow | factor.momentum_20d |
| factor.value_factor | dataflow | factor.value_factor |
| fill.executed | dataflow | fill.executed |
| generate.order | dataflow | generate.order |
| ingest.ifind_kline | dataflow | ingest.ifind_kline |
| market_data.ohlc_bar | dataflow | market_data.ohlc_bar |
| market_data.tick | dataflow | market_data.tick |
| order.target | dataflow | order.target |
| position.snapshot | dataflow | position.snapshot |
| risk.limits | dataflow | risk.limits |
| signal.composite | dataflow | signal.composite |
| synthesize.signal | dataflow | synthesize.signal |
| CFG-rule-enforcement-registry | depgraph | docs/01_policies_and_standards/_registry/catalogs/rule_enforcement_registry.yaml |
| CFG-rule-registry-collection | depgraph | docs/01_policies_and_standards/_registry/catalogs/rule_registry_collection.yaml |
| CFG-scripts-registry | depgraph | docs/01_policies_and_standards/_registry/catalogs/scripts_registry.yaml |
| CFG-test-suite-registry | depgraph | docs/01_policies_and_standards/_registry/catalogs/test_suite_registry.yaml |
| INFRA-DB-001 | depgraph | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |
| INFRA-DB-002 | depgraph | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |
| INFRA-DB-003 | depgraph | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |
| INFRA-DB-006 | depgraph | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |
| MOD-014 | depgraph | src/zephyr/infrastructure/observability/notifier.py |
| MOD-014 | depgraph | src/zephyr/infrastructure/sla/sla_monitor.py |
| MOD-AUTONOMY_CORE | depgraph | src/zephyr/autonomy_core/__init__.py |
| MOD-AUTONOMY_CORE | depgraph | src/zephyr/autonomy_core/vibe_coding_quality_gate.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/attack_registry.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/constitution_guard.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/convergence_checker.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/defense_runner.py |
| MOD-AUTONOMY_PERM | depgraph | src/zephyr/autonomy_perm/red_blue_validator/game_day_runner.py |
| MOD-BIZ-002 | depgraph | src/zephyr/trading/trading_contracts/portfolio/contracts/__init__.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/result_repository.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/decision_gate.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/data_handler.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/metrics.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/portfolio.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_engine.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/metrics.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/overfitting_detector.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/pit_manager.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/walk_forward.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/backtest_result_sink.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/result_repository.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/__init__.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_logic.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/tick_replay.py/ |
| MOD-BT-001 | depgraph | tests/test_backtest_decisiongraph_adapter.py |
| MOD-BT-001 | depgraph | tests/test_event_driven_engine.py |
| MOD-BT-001 | depgraph | tests/test_matching_engine.py |
| MOD-BT-001 | depgraph | tests/test_tick_replay_data_handler.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/data_handler.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/engine_base.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_engine.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_logic.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/portfolio.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/tick_replay.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/implementations/event_driven_engine.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/implementations/__init__.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/decisiongraph_adapter.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/implementations/vectorized_engine.py |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/backtest_result_sink.py/ |
| MOD-CONTEXT_ENGINE | depgraph | docs/03_modules/_cross_layer/context_engine/blueprint.md |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_checkpoint_manager.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_citation_walker.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_complexity_budget.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_context_pipeline_red_blue.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_fragmentation_index.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_integrity_check.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_lsg_pattern_tracker.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_shadow_canary.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_solo_dev_safety_net.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_staleness_manager.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_vector_bridge.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/autonomy/test_verify_paths.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/ce/test_ce_bootstrap.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/ce/test_ce_explain_cli.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/ce/test_ce_playground_v2.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/ce/test_ce_vibe_shortcuts.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/cold/test_cold_start_booster.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/config/test_config_safety_guard.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/context/test_context_budget_tracker.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/context/test_context_debt_score.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/context/test_context_health_score.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/context/test_context_model_strategy.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/context/test_context_pipeline_auto.py |
| MOD-CONTEXT_ENGINE | depgraph | tests/knowledge_engine/test_knowledge_distiller.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/atomic_injector.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/ce_bootstrap.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/ce_explain_cli.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/ce_vibe_shortcuts.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/ce_file_lister.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/ce_playground_v2.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/checkpoint_manager.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/cold_start_booster.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_assembler.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/complexity_budget.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/contextual_fetch_api.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_budget.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_budget_tracker.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_debt_score.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_evictor.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_evaluator.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_health_score.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_model_strategy.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_outcome_tracker.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_injector.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_pipeline.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_playground.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_rot_model.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_rule_registry.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_pipeline_auto.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/context_value_attribution.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/curation_loop.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/domain_decay_config.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/diff_injector.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/memory_bank.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/fallback_staleness_gate.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/diversity_constraint.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/integrity_check.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/mode_manager.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/position_optimizer.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/shadow_canary.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/staleness_manager.py |
| MOD-CONTEXT_ENGINE | depgraph | src/zephyr/autonomy_core/context/vector_bridge.py |
| MOD-CROSS_ASSET | depgraph | src/zephyr/cross_asset/ |
| MOD-DATABASE | depgraph | scripts/governance/meta/mutation_test_post_sync_validator.py |
| MOD-DATABASE | depgraph | tests/db/test_db_query.py |
| MOD-DATABASE | depgraph | tests/db/test_db_transition.py |
| MOD-DATABASE | depgraph | tests/governance/data_layer/test_sqlite_schema_root.py |
| MOD-DATABASE | depgraph | tests/governance/persistence/test_base_repo.py |
| MOD-DATABASE | depgraph | tests/governance/shared/test_post_sync_validation.py |
| MOD-DATABASE | depgraph | tests/io/test_depgraph_schema.py |
| MOD-DATABASE | depgraph | tests/llm_security/test_db.py |
| MOD-DATABASE | depgraph | tests/task/test_task_repo_auto_commit.py |
| MOD-DIGITAL_TWIN | depgraph | src/zephyr/digital_twin/ |
| MOD-FEEDBACK_LOOP | depgraph | docs/03_modules/_cross_layer/feedback_loop/blueprint.md |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/alert_dispatcher.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/db_writer.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/protocols.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/actors/saga_compensator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/collectors/feedback_collector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/collectors/metrics_collector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/collectors/__init__.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/anomaly_clustering.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/anomaly_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/emergent_behavior_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/heisenbug_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/flapping_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/log_anomaly.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/intermittent_failure_pattern.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/infinite_loop_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/silent_corruption_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/synthetic_anomaly_generator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/__init__.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/anomaly/temporal_pattern.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/action_efficacy_decay_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/action_interaction_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/action_side_effect_cumulative_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/cross_signal_validator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/cross_system_correlator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/agent_trajectory_anomaly_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/decision_provenance.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/dependency_freshness_monitor.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/ensemble_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/external_validation_checkpoint.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/external_health.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/fle_performance_regression_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/multi_signal_correlator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/rumor_noise_filter.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/concept_drift.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/__init__.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/traffic_replay_validator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/config_drift.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/correlation/trace_causal_bridge.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/context_window_contamination_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/diminishing_returns_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/gradual_poisoning_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/ensemble_drift.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/__init__.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/drift/trend_cycle_separator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/guard/alert_desensitization_curve.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/guard/guard_cascade_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/guard/guard_oscillation_detector.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/guard/recursive_diagnosis_trust_evaluator.py |
| MOD-FEEDBACK_LOOP | depgraph | src/zephyr/trading/feedback_loop/detectors/guard/placebo_action_detector.py |
... 共 4345 行（仅展示前 200 行）

## 2. 状态漂移（design_maturity 不一致）

| module_id | depgraph | dataflow | decision |
|---|---|---|---|
| MOD-L02-001 | prototype | - | production |
| MOD-L04-001 | prototype | - | design |
| MOD-L05-001 | prototype | - | design |
| MOD-MKT_DATA | prototype | - | production |

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

| module_id | graph | entity_name |
|---|---|---|
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/result_repository.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/data_handler.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/metrics.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/portfolio.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_engine.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/matching_logic.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/core/tick_replay.py/ |
| MOD-BT-001 | depgraph | src/zephyr/backtest/io/backtest_result_sink.py/ |
| MOD-CONTEXT_ENGINE | depgraph | docs/03_modules/_cross_layer/context_engine/blueprint.md |
| MOD-CROSS_ASSET | depgraph | src/zephyr/cross_asset/ |
| MOD-DIGITAL_TWIN | depgraph | src/zephyr/digital_twin/ |
| MOD-FEEDBACK_LOOP | depgraph | docs/03_modules/_cross_layer/feedback_loop/blueprint.md |
| MOD-GATE_ENGINE | depgraph | docs/03_modules/_cross_layer/gate_engine/blueprint.md |
| MOD-GOV-ALIGN-PANORAMAS | depgraph | scripts/governance/d5_architecture/generators/ |
| MOD-GOVERNANCE | depgraph | docs/03_modules/_domain_governance/blueprint.md |
| MOD-INF-005 | depgraph | docs/03_modules/_domain_governance/governance_automation/blueprint.md |
| MOD-INF-009 | depgraph | docs/03_modules/_cross_layer/pipeline/blueprint.md |
| MOD-INF-011 | depgraph | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md |
| MOD-INF-016 | depgraph | docs/03_modules/_cross_layer/shared_core/blueprint.md |
| MOD-INF-017 | depgraph | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md |
| MOD-INF-019 | depgraph | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md |
| MOD-INF-020 | depgraph | docs/03_modules/_domain_governance/audit_trail/blueprint.md |
| MOD-INF-021 | depgraph | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md |
| MOD-INF-022 | depgraph | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md |
| MOD-INF-023 | depgraph | docs/03_modules/_domain_governance/drift_detector/blueprint.md |
| MOD-INF-024 | depgraph | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md |
| MOD-INF-027 | depgraph | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md |
| MOD-INF-028 | depgraph | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md |
| MOD-INF-029 | depgraph | docs/03_modules/_cross_layer/orphan_judge/blueprint.md |
| MOD-INF-030 | depgraph | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md |
| MOD-INF-030 | depgraph | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md |
| MOD-INF-031 | depgraph | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md |
| MOD-INF-033 | depgraph | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md |
| MOD-INF-034 | depgraph | docs/03_modules/_cross_layer/model_profiler/blueprint.md |
| MOD-INF-036 | depgraph | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md |
| MOD-INF-037 | depgraph | docs/03_modules/_domain_governance/registry_governance/blueprint.md |
| MOD-INF-039 | depgraph | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md |
| MOD-INFRA_OPS | depgraph | src/zephyr/infra_ops/ |
| MOD-L00-001 | depgraph | src/zephyr/governance/data_governance/miniqmt_provider.py/ |
| MOD-L06-001 | depgraph | src/zephyr/ex_core/adapters/miniqmt_broker.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/chart_factory.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/backtest_results.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/tick_replay.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/order_book.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/position_monitor.py/ |
| MOD-L08-001 | depgraph | src/zephyr/frontend/dashboard/components/trade_panel.py/ |
| MOD-MASTER_BLUEPRINT | depgraph | docs/03_modules/_master_blueprint/blueprint_agent_spec.md |
| MOD-MASTER_BLUEPRINT | depgraph | docs/03_modules/_master_blueprint/blueprint.md |
| MOD-PF_ALLOC | depgraph | src/zephyr/pf_alloc/ |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | depgraph | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md |
| MOD-SIMULATION | depgraph | src/zephyr/simulation/ |
| SH-DB-001 | depgraph | docs/03_modules/_cross_layer/database/blueprint.md |

## 5. 处置建议

- 孤儿节点：决定是否需在另两图登记对应 module_id，或在一图删除
- 状态漂移：以最成熟状态为准，统一更新（建议 production > prototype > design）
- 域不一致：核对真源并统一 domain_id
- 设计态孤立：评估设计态是否需要同步到另两图
