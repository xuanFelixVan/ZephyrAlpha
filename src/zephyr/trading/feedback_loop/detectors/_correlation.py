# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors._correlation
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK__correlation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

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
