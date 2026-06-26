# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.detectors._anomaly
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.ops.detectors.__init__
# [CONSUMERS] zephyr.observability.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK__anomaly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

_SUBMODULES = [
    "anomaly_detector",
    "anomaly_clustering",
    "log_anomaly",
    "emergent_behavior_detector",
    "heisenbug_detector",
    "intermittent_failure_pattern",
    "silent_corruption_detector",
    "synthetic_anomaly_generator",
    "temporal_pattern",
    "infinite_loop_detector",
    "flapping_detector",
]
