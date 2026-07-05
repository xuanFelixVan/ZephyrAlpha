# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包reliability: 可靠性/守卫族（DW-242分类，原_reliability.py聚合迁移而来）

_SUBMODULES = [
    "amplification_guard",
    "api_dependency_metrics",
    "burn_rate_alerter",
    "burnout_alarm",
    "capacity_aware_repair",
    "cold_start_conservative_mode",
    "context_truncation",
    "context_window_pressure_manager",
    "cross_guard_conflict_detector",
    "cross_session_consistency_validator",
    "data_volume_growth_monitor",
    "feedback_delay_compensator",
    "guard_interaction_topology_mapper",
    "guard_self_consistency_auditor",
    "human_anomaly_flood_detector",
    "latency_slo",
    "llm_provider_integrity",
    "llm_quality_regression",
    "model_rotation",
    "model_rotation_v2",
    "model_version_semantic_drift",
    "numerical_stability_guard",
    "operational_seasonality",
    "prompt_fingerprint",
    "prompt_sanitizer",
    "recovery_time_stats",
    "regime_gain_scheduling",
    "retirement_planner",
    "slo_capacity_metrics",
    "system_entropy_monitor",
    "temporal_integrity_guard",
    "timezone_semantic_reasoner",
    "toil_quantification",
    "value_added_baseline",
    "zombie_fle_detector",
]

__all__ = ['amplification_guard', 'api_dependency_metrics', 'burn_rate_alerter', 'burnout_alarm', 'capacity_aware_repair', 'cold_start_conservative_mode', 'context_truncation', 'context_window_pressure_manager', 'cross_guard_conflict_detector', 'cross_session_consistency_validator', 'data_volume_growth_monitor', 'feedback_delay_compensator', 'guard_interaction_topology_mapper', 'guard_self_consistency_auditor', 'human_anomaly_flood_detector', 'latency_slo', 'llm_provider_integrity', 'llm_quality_regression', 'model_rotation', 'model_rotation_v2', 'model_version_semantic_drift', 'numerical_stability_guard', 'operational_seasonality', 'prompt_fingerprint', 'prompt_sanitizer', 'recovery_time_stats', 'regime_gain_scheduling', 'retirement_planner', 'slo_capacity_metrics', 'system_entropy_monitor', 'temporal_integrity_guard', 'timezone_semantic_reasoner', 'toil_quantification', 'value_added_baseline', 'zombie_fle_detector']

