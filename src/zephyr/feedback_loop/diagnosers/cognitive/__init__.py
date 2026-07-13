# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_cognitive | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包cognitive: 认知/调优族（DW-242分类，原_cognitive.py聚合迁移而来）

_SUBMODULES = [
    "cognitive_load",
    "cognitive_load_budget",
    "adaptive_param_tuning",
    "confidence_decomposer",
    "socratic_questions",
    "gamification",
    "tone_adapter",
    "tone_adapter_v2",
    "meta_guard_latency_budget",
    "collaborative_learning",
]

__all__ = ['adaptive_param_tuning', 'cognitive_load', 'cognitive_load_budget', 'collaborative_learning', 'confidence_decomposer', 'gamification', 'meta_guard_latency_budget', 'socratic_questions', 'tone_adapter', 'tone_adapter_v2']

