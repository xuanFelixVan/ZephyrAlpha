# [A_module] module_id=MOD-UNK__guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.detectors._guard
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.observability.feedback_loop.detectors.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py

_SUBMODULES = [
    "guard_cascade_detector",
    "guard_oscillation_detector",
    "positive_feedback_defense",
    "placebo_action_detector",
    "self_audit",
    "self_diagnosis_data_leak_detector",
    "self_ha",
    "alert_desensitization_curve",
    "temporal_coherence_of_self_model",
    "recursive_diagnosis_trust_evaluator",
]
