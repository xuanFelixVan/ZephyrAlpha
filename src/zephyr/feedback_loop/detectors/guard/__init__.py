# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包guard: 守卫/自审计/反馈防御族（DW-244分类，原_guard.py聚合迁移而来）

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/detectors/guard/guard__init__.yaml
"""

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

__all__ = [
    "alert_desensitization_curve",
    "guard_cascade_detector",
    "guard_oscillation_detector",
    "placebo_action_detector",
    "positive_feedback_defense",
    "recursive_diagnosis_trust_evaluator",
    "self_audit",
    "self_diagnosis_data_leak_detector",
    "self_ha",
    "temporal_coherence_of_self_model",
]
