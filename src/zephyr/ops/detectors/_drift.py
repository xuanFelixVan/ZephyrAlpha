# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.detectors._drift
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
# [A_module] module_id=MOD-UNK__drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

_SUBMODULES = [
    "concept_drift",
    "config_drift",
    "ensemble_drift",
    "gradual_poisoning_detector",
    "diminishing_returns_detector",
    "context_window_contamination_detector",
    "regime_detector",
    "trend_cycle_separator",
]
