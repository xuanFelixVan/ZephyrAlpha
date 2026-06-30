# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers._cognitive
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK__cognitive | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

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
