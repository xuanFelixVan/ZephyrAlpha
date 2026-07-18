# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-19 02:25:51
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=639 / dataflow=25 / decision=319 / blueprint=72
- 问题总数: 487
  - 孤儿（仅一图）: 487
  - 状态漂移（blueprint 缺 design_maturity）: 0
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 0

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| MOD-AUTONOMY_PERM | decision | layer:MOD-AUTONOMY_PERM |
| MOD-GOV_DRIFT_bridges | decision | layer:MOD-GOV_DRIFT_bridges |
| MOD-GOV_DRIFT_det_bridge | decision | layer:MOD-GOV_DRIFT_det_bridge |
| MOD-GOV_DRIFT_detector_core | decision | layer:MOD-GOV_DRIFT_detector_core |
| MOD-SECURITY | decision | layer:MOD-SECURITY |
| MOD-SECURITY-LLM | decision | layer:MOD-SECURITY-LLM |
| MOD-TRADING | decision | layer:MOD-TRADING |
| MOD-GOV-029 | depgraph | scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py |
| MOD-GOV-blueprint_amodule_consistency_gate | depgraph | tests/governance/commit_gates/test_blueprint_amodule_consistency_gate.py |
| MOD-GOV-domain_fk_gate | depgraph | tests/governance/commit_gates/test_domain_fk_gate.py |
| MOD-GOV-no_import_side_effect_gate | depgraph | tests/governance/commit_gates/test_no_import_side_effect_gate.py |
| MOD-GOV-reconciliation_registry | depgraph | tests/governance/audit/test_blueprint_frontmatter_reconciler_post_commit.py |
| MOD-GOV-rename_depgraph_sync_gate | depgraph | tests/governance/commit_gates/test_rename_depgraph_sync_gate.py |
| MOD-GOV-ruling_reference_gate | depgraph | tests/governance/commit_gates/test_ruling_reference_gate.py |
| MOD-GOV_DQ | depgraph | scripts/governance/data_quality/check_tick_duplication.py |
| MOD-INF-012B | depgraph | scripts/governance/migrate_sqlite_to_pg/migrate_data.py |
| MOD-INF-040 | depgraph | src/zephyr/signal_quality/__init__.py |
| MOD-SEC-immutable_core | depgraph | config/immutable_core.yaml |
| MOD-TEST-202 | depgraph | tests/skill/test_agent_spec_adversarial.py |
| MOD-TEST-203 | depgraph | tests/autonomy/test_agent_spec_e2e.py |
| MOD-TEST-204 | depgraph | tests/audit/test_audit_adversarial.py |
| MOD-TEST-205 | depgraph | tests/audit/test_audit_integration_fracture.py |
| MOD-TEST-206 | depgraph | tests/governance/code_quality/test_code_dedup_engine_red_team.py |
| MOD-TEST-207 | depgraph | tests/kb/test_cross_layer_systems_red_team.py |
| MOD-TEST-208 | depgraph | tests/kb/test_kb_adversarial.py |
| MOD-TEST-209 | depgraph | tests/infrastructure/test_kb_redteam.py |
| MOD-TEST-210 | depgraph | tests/infrastructure/test_mcp_red_team.py |
| MOD-TEST-211 | depgraph | tests/autonomy/test_pipeline_bridge_integration.py |
| MOD-TEST-212 | depgraph | tests/agent_rbac/test_rbac_adversarial.py |
| MOD-TEST-213 | depgraph | tests/rollback/test_rollback_adversarial.py |
| MOD-TEST-215 | depgraph | tests/infrastructure/test_telemetry_red_team.py |
| MOD-TEST-216 | depgraph | tests/agent_rbac/__init__.py |
| MOD-TEST-217 | depgraph | tests/alpha_signal/__init__.py |
| MOD-TEST-218 | depgraph | tests/alpha_signal/test_adversarial_alpha_signal.py |
| MOD-TEST-219 | depgraph | tests/architecture/__init__.py |
| MOD-TEST-220 | depgraph | tests/architecture/test_contract_consistency.py |
| MOD-TEST-221 | depgraph | tests/architecture/test_cross_module_contracts.py |
| MOD-TEST-222 | depgraph | tests/architecture/test_layer_isolation.py |
| MOD-TEST-223 | depgraph | tests/architecture/test_money_and_docs.py |
| MOD-TEST-224 | depgraph | tests/asset_inventory/__init__.py |
| MOD-TEST-225 | depgraph | tests/asset_inventory/test_classifier_asset_inventory.py |
| MOD-TEST-226 | depgraph | tests/asset_inventory/test_concurrent.py |
| MOD-TEST-227 | depgraph | tests/asset_inventory/test_dashboard_asset_inventory.py |
| MOD-TEST-228 | depgraph | tests/asset_inventory/test_dependency_asset_inventory.py |
| MOD-TEST-229 | depgraph | tests/asset_inventory/test_emergency_bypass.py |
| MOD-TEST-230 | depgraph | tests/asset_inventory/test_git_metadata.py |
| MOD-TEST-231 | depgraph | tests/asset_inventory/test_index_generator_asset_inventory.py |
| MOD-TEST-232 | depgraph | tests/asset_inventory/test_knowledge_transfer.py |
| MOD-TEST-233 | depgraph | tests/asset_inventory/test_lifecycle_asset_inventory.py |
| MOD-TEST-234 | depgraph | tests/asset_inventory/test_models_asset_inventory.py |
| MOD-TEST-235 | depgraph | tests/asset_inventory/test_multi_ide.py |
| MOD-TEST-236 | depgraph | tests/asset_inventory/test_notifications.py |
| MOD-TEST-237 | depgraph | tests/asset_inventory/test_reconciler_asset_inventory.py |
| MOD-TEST-238 | depgraph | tests/asset_inventory/test_registry_adapter_asset_inventory.py |
| MOD-TEST-239 | depgraph | tests/asset_inventory/test_scanner_asset_inventory.py |
| MOD-TEST-240 | depgraph | tests/asset_inventory/test_schema_evolution_asset_inventory.py |
| MOD-TEST-241 | depgraph | tests/asset_inventory/test_security_enforcer.py |
| MOD-TEST-242 | depgraph | tests/asset_inventory/test_trust_anchor_asset_inventory.py |
| MOD-TEST-243 | depgraph | tests/kb/benchmark_vms_e2e.py |
| MOD-TEST-244 | depgraph | tests/kb/benchmark_vms_v2.py |
| MOD-TEST-246 | depgraph | tests/chaos/__init__.py |
| MOD-TEST-247 | depgraph | tests/chaos/test_mcp_chaos.py |
| MOD-TEST-248 | depgraph | tests/conftest.py |
| MOD-TEST-250 | depgraph | tests/contracts/_meta/test_contract_test_anchors.py |
| MOD-TEST-251 | depgraph | tests/contracts/_meta/test_import_chain.py |
| MOD-TEST-252 | depgraph | tests/contracts/_meta/test_schema_stability.py |
| MOD-TEST-253 | depgraph | tests/contracts/__init__.py |
| MOD-TEST-254 | depgraph | tests/contracts/test_ct_ce_lsg_001.py |
| MOD-TEST-255 | depgraph | tests/contracts/test_ct_ce_vms_001.py |
| MOD-TEST-256 | depgraph | tests/contracts/test_ct_fle_db_001.py |
| MOD-TEST-257 | depgraph | tests/contracts/test_ct_fle_orc_001.py |
| MOD-TEST-258 | depgraph | tests/contracts/test_ct_health_001.py |
| MOD-TEST-259 | depgraph | tests/contracts/test_ct_kb_vms_001.py |
| MOD-TEST-260 | depgraph | tests/contracts/test_ct_orc_ce_001.py |
| MOD-TEST-261 | depgraph | tests/contracts/test_ct_orc_gate_001.py |
| MOD-TEST-262 | depgraph | tests/contracts/test_ct_orc_script_001.py |
| MOD-TEST-263 | depgraph | tests/contracts/test_ct_orc_vms_001.py |
| MOD-TEST-264 | depgraph | tests/contracts/test_ct_pipe_orc_001.py |
| MOD-TEST-265 | depgraph | tests/contracts/test_ct_rbk_gate_001.py |
| MOD-TEST-266 | depgraph | tests/contracts/test_ct_script_gate_001.py |
| MOD-TEST-267 | depgraph | tests/contracts/test_ct_script_kb_001.py |
| MOD-TEST-268 | depgraph | tests/contracts/test_ct_tele_fle_001.py |
| MOD-TEST-270 | depgraph | tests/kb/test_kb_full_pipeline.py |
| MOD-TEST-272 | depgraph | tests/governance/__init__.py |
| MOD-TEST-273 | depgraph | tests/governance/conftest.py |
| MOD-TEST-274 | depgraph | tests/governance/shared/test_a2a_phase4_hold.py |
| MOD-TEST-275 | depgraph | tests/governance/security/test_adversarial_contract_attacks.py |
| MOD-TEST-276 | depgraph | tests/governance/integration/test_all_scripts.py |
| MOD-TEST-277 | depgraph | tests/governance/budget/test_budget_enforcer_smoke.py |
| MOD-TEST-278 | depgraph | tests/governance/budget/test_budget_enforcer_submodules.py |
| MOD-TEST-279 | depgraph | tests/governance/audit/test_cycle_dependency_audit_isolation.py |
| MOD-TEST-280 | depgraph | tests/governance/scripts_governance/test_dependency_graph_acyclic.py |
| MOD-TEST-281 | depgraph | tests/governance/security/test_gct_001_rbac_to_audit.py |
| MOD-TEST-282 | depgraph | tests/governance/audit/test_gct_002_audit_to_rollback.py |
| MOD-TEST-283 | depgraph | tests/governance/governance_e2e/test_gct_003_rollback_to_escalation.py |
| MOD-TEST-284 | depgraph | tests/governance/security/test_gct_004_escalation_to_rbac.py |
| MOD-TEST-285 | depgraph | tests/governance/drift/test_gct_005_drift_to_rollback.py |
| MOD-TEST-286 | depgraph | tests/governance/audit/test_gct_006_budget_to_escalation.py |
| MOD-TEST-287 | depgraph | tests/governance/shared/test_gct_007_spec_to_rbac_audit.py |
| MOD-TEST-288 | depgraph | tests/governance/shared/test_gct_008_a2a_to_rbac_escalation.py |
| MOD-TEST-289 | depgraph | tests/governance/budget/test_gct_024_hard_checks.py |
| MOD-TEST-290 | depgraph | tests/governance/drift/test_gct_integration.py |
| MOD-TEST-291 | depgraph | tests/governance/governance_e2e/test_gov_5system_integration.py |
| MOD-TEST-292 | depgraph | tests/governance/shared/test_jsonl_pipeline.py |
| MOD-TEST-293 | depgraph | tests/governance/governance_e2e/test_p0_i1_depends_on_integration.py |
| MOD-TEST-294 | depgraph | tests/governance/audit/test_p0_i2_construction_order.py |
| MOD-TEST-295 | depgraph | tests/governance/security/test_p0_u1_contract_smoke.py |
| MOD-TEST-296 | depgraph | tests/governance/shared/test_p0_u2_input_validation.py |
| MOD-TEST-297 | depgraph | tests/governance/governance_e2e/test_phase1_gate_check.py |
| MOD-TEST-298 | depgraph | tests/governance/shared/test_phase4_gate_check.py |
| MOD-TEST-299 | depgraph | tests/governance/shared/test_phase_gates.py |
| MOD-TEST-300 | depgraph | tests/governance/security/test_security_scripts.py |
| MOD-TEST-301 | depgraph | tests/infrastructure/__init__.py |
| MOD-TEST-302 | depgraph | tests/infrastructure/drift_red_blue_adversarial.py |
| MOD-TEST-303 | depgraph | tests/infrastructure/test_capacity_runtime_red_blue.py |
| MOD-TEST-304 | depgraph | tests/infrastructure/test_cross_blueprint_e2e.py |
| MOD-TEST-305 | depgraph | tests/infrastructure/test_delegation_manager.py |
| MOD-TEST-306 | depgraph | tests/infrastructure/test_delegation_safety.py |
| MOD-TEST-307 | depgraph | tests/infrastructure/test_drift_e2e_pipeline.py |
| MOD-TEST-308 | depgraph | tests/infrastructure/test_drift_extended_e2e.py |
| MOD-TEST-309 | depgraph | tests/infrastructure/test_drift_trigger_recovery.py |
| MOD-TEST-310 | depgraph | tests/infrastructure/test_economic_guard.py |
| MOD-TEST-311 | depgraph | tests/infrastructure/test_escalation_adversarial.py |
| MOD-TEST-312 | depgraph | tests/infrastructure/test_escalation_e2e.py |
| MOD-TEST-313 | depgraph | tests/infrastructure/test_escalation_engine.py |
| MOD-TEST-314 | depgraph | tests/infrastructure/test_escalation_hooks.py |
| MOD-TEST-315 | depgraph | tests/infrastructure/test_escalation_phase3.py |
| MOD-TEST-316 | depgraph | tests/infrastructure/test_rebound_detector.py |
| MOD-TEST-319 | depgraph | tests/trading/integration/test_agent_e2e.py |
| MOD-TEST-320 | depgraph | tests/governance/data_layer/test_akshare_real_data.py |
| MOD-TEST-321 | depgraph | tests/kb/test_audit08_service_layer_wiring.py |
| MOD-TEST-322 | depgraph | tests/infrastructure/test_auto_telemetry_bootstrap.py |
| MOD-TEST-323 | depgraph | tests/infrastructure/test_beta_e2e.py |
| MOD-TEST-324 | depgraph | tests/governance/trading/test_e2e_pipeline.py |
| MOD-TEST-325 | depgraph | tests/autonomy/test_evolution_e2e.py |
| MOD-TEST-326 | depgraph | tests/gate/test_gate_e2e.py |
| MOD-TEST-327 | depgraph | tests/kb/test_kb_pipeline_gate_order.py |
| MOD-TEST-328 | depgraph | tests/infrastructure/test_mcp_e2e.py |
| MOD-TEST-329 | depgraph | tests/phase/test_phase_c_import_chain.py |
| MOD-TEST-330 | depgraph | tests/infrastructure/test_phase_e_layers.py |
| MOD-TEST-331 | depgraph | tests/governance/trading/test_phase_e_main_flow.py |
| MOD-TEST-332 | depgraph | tests/trading/pipeline/test_phase_f_layers.py |
| MOD-TEST-333 | depgraph | tests/trading/pipeline/test_phase_g_perf.py |
| MOD-TEST-334 | depgraph | tests/autonomy/test_pipeline_skill_injection.py |
| MOD-TEST-335 | depgraph | tests/rollback/test_rollback_e2e.py |
| MOD-TEST-336 | depgraph | tests/governance/orchestrator/test_verify_b54_b56_b59_deep.py |
| MOD-TEST-337 | depgraph | tests/llm_security/__init__.py |
| MOD-TEST-338 | depgraph | tests/ml_experiment/__init__.py |
| MOD-TEST-339 | depgraph | tests/ml_experiment/test_adversarial_ml_experiment.py |
| MOD-TEST-340 | depgraph | tests/ml_experiment/test_adversarial_ml.py |
| MOD-TEST-342 | depgraph | tests/infrastructure/test_mcp_stress.py |
| MOD-TEST-343 | depgraph | tests/trading/test_admission_response.py |
| MOD-TEST-344 | depgraph | tests/agent/test_agent_debate.py |
| MOD-TEST-345 | depgraph | tests/agent/test_agent_dispatch.py |
| MOD-TEST-346 | depgraph | tests/ai/test_ai_code_standards.py |
| MOD-TEST-347 | depgraph | tests/ai/test_ai_self_diagnosis.py |
| MOD-TEST-348 | depgraph | tests/governance/lifecycle/test_api_lifecycle.py |
| MOD-TEST-349 | depgraph | tests/autonomy/test_autonomy_monitor.py |
| MOD-TEST-350 | depgraph | tests/governance/integration/test_autopilot.py |
| MOD-TEST-351 | depgraph | tests/blueprint/test_blueprint_code_sync.py |
| MOD-TEST-354 | depgraph | tests/blueprint/test_blueprint_decomposer.py |
| MOD-TEST-355 | depgraph | tests/governance/resilience/test_broker_resilience.py |
| MOD-TEST-356 | depgraph | tests/governance/trading/test_bus_factor_defense.py |
| MOD-TEST-357 | depgraph | tests/gate/test_circuit_breaker_root.py |
| MOD-TEST-358 | depgraph | tests/observability/test_cli_summary.py |
| MOD-TEST-359 | depgraph | tests/code_dedup_engine/__init__.py |
| MOD-TEST-360 | depgraph | tests/code_dedup_engine/test_config_test_code_dedup_engine.py |
| MOD-TEST-361 | depgraph | tests/code_dedup_engine/test_degradation_edge.py |
| MOD-TEST-362 | depgraph | tests/code_dedup_engine/test_micro_clone.py |
| MOD-TEST-363 | depgraph | tests/code_dedup_engine/test_scanner_cross.py |
| MOD-TEST-364 | depgraph | tests/code_dedup_engine/test_scanner_raw.py |
| MOD-TEST-365 | depgraph | tests/code_dedup_engine/test_self_scan_integrity.py |
| MOD-TEST-366 | depgraph | tests/governance/delegation/test_consequence_manager.py |
| MOD-TEST-367 | depgraph | tests/context/test_context_engine.py |
| MOD-TEST-368 | depgraph | tests/context/test_context_guard.py |
| MOD-TEST-369 | depgraph | tests/context/test_context_manager_gov.py |
| MOD-TEST-370 | depgraph | tests/context/test_context_recycling.py |
| MOD-TEST-371 | depgraph | tests/infrastructure/test_core_models.py |
| MOD-TEST-372 | depgraph | tests/f_lifecycle/test_daemon_registry.py |
| MOD-TEST-373 | depgraph | tests/data/test_data_classification.py |
| MOD-TEST-374 | depgraph | tests/data/test_data_quality.py |
| MOD-TEST-375 | depgraph | tests/decision/test_decision_fatigue.py |
| MOD-TEST-376 | depgraph | tests/decision/test_decision_fatigue_cli.py |
| MOD-TEST-377 | depgraph | tests/dependency/test_dependency_graph.py |
| MOD-TEST-378 | depgraph | tests/utils/test_diff_planner.py |
| MOD-TEST-379 | depgraph | tests/utils/test_dogfooding.py |
| MOD-TEST-380 | depgraph | tests/blueprint/test_draft_assistant.py |
| MOD-TEST-381 | depgraph | tests/event/test_event_bus.py |
| MOD-TEST-382 | depgraph | tests/event/test_event_reactor.py |
| MOD-TEST-383 | depgraph | tests/governance/shared/test_execution_tuner.py |
| MOD-TEST-384 | depgraph | tests/trading/test_failure_matcher.py |
| MOD-TEST-385 | depgraph | tests/governance/compliance/test_financial_compliance.py |
| MOD-TEST-386 | depgraph | tests/governance/governance_e2e/test_gov_architecture_principles.py |
| MOD-TEST-387 | depgraph | tests/governance/governance_e2e/test_gov_consequence_manager.py |
| MOD-TEST-388 | depgraph | tests/governance/governance_e2e/test_gov_data_source_reliability.py |
| MOD-TEST-389 | depgraph | tests/governance/governance_e2e/test_gov_microstructure_defense.py |
| MOD-TEST-390 | depgraph | tests/governance/governance_e2e/test_gov_session_concurrency.py |
| MOD-TEST-391 | depgraph | tests/utils/test_handbook.py |
| MOD-TEST-392 | depgraph | tests/utils/test_healthcheck_service.py |
| MOD-TEST-393 | depgraph | tests/event/test_hook_dispatcher.py |
... 共 487 行（仅展示前 200 行）

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

> 无状态漂移。

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

> 无设计态孤立。

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
