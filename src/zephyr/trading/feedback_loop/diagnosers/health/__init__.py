# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.diagnosers.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新diagnosers/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包health: 自健康/可观测族（DW-242分类，原_health.py聚合迁移而来）

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

__all__ = ['action_composition_health_monitor', 'dr_resilience_metrics', 'e2e_integration_health', 'fle_dogfood_monitor', 'fle_self_slo_metrics', 'global_health_map', 'memory_self_check', 'model_health', 'self_benchmark', 'self_bottleneck_detector', 'self_health_monitor', 'self_llm_observability']

