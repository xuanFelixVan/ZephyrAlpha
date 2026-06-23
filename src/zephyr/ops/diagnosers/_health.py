# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.diagnosers._health
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.ops.diagnosers.__init__
# [CONSUMERS] zephyr.observability.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK__health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

_SUBMODULES = [
    "action_composition_health_monitor",
    "self_health_monitor",
    "self_benchmark",
    "self_bottleneck_detector",
    "global_health_map",
    "e2e_integration_health",
    "memory_self_check",
    "self_llm_observability",
    "fle_dogfood_monitor",
    "fle_self_slo_metrics",
    "model_health",
    "dr_resilience_metrics",
]
