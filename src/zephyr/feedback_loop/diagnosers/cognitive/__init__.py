# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包cognitive: 认知/调优族（DW-242分类，原_cognitive.py聚合迁移而来）

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/diagnosers/cognitive/cognitive__init__.yaml
"""

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

__all__ = [
    "adaptive_param_tuning",
    "cognitive_load",
    "cognitive_load_budget",
    "collaborative_learning",
    "confidence_decomposer",
    "gamification",
    "meta_guard_latency_budget",
    "socratic_questions",
    "tone_adapter",
    "tone_adapter_v2",
]
