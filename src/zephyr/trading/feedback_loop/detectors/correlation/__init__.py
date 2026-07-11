# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_correlation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包correlation: 跨信号/系统关联与因果族（DW-244分类，原_correlation.py聚合迁移而来）

_SUBMODULES = [
    "cross_signal_validator",
    "cross_system_correlator",
    "multi_signal_correlator",
    "trace_causal_bridge",
    "decision_provenance",
    "dependency_freshness_monitor",
    "action_efficacy_decay_detector",
    "action_interaction_detector",
    "action_side_effect_cumulative_detector",
    "agent_trajectory_anomaly_detector",
    "ensemble_detector",
    "fle_performance_regression_detector",
    "external_health",
    "external_validation_checkpoint",
    "rumor_noise_filter",
    "traffic_replay_validator",
]

__all__ = ['action_efficacy_decay_detector', 'action_interaction_detector', 'action_side_effect_cumulative_detector', 'agent_trajectory_anomaly_detector', 'cross_signal_validator', 'cross_system_correlator', 'decision_provenance', 'dependency_freshness_monitor', 'ensemble_detector', 'external_health', 'external_validation_checkpoint', 'fle_performance_regression_detector', 'multi_signal_correlator', 'rumor_noise_filter', 'trace_causal_bridge', 'traffic_replay_validator']

