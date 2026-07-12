# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包guard: 守卫/自审计/反馈防御族（DW-244分类，原_guard.py聚合迁移而来）

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

__all__ = ['alert_desensitization_curve', 'guard_cascade_detector', 'guard_oscillation_detector', 'placebo_action_detector', 'positive_feedback_defense', 'recursive_diagnosis_trust_evaluator', 'self_audit', 'self_diagnosis_data_leak_detector', 'self_ha', 'temporal_coherence_of_self_model']

