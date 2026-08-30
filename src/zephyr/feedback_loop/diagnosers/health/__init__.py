# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health
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
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包health: 自健康/可观测族（DW-242分类，原_health.py聚合迁移而来）

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 action_composition_health_monitor, dr_resilience_metrics, e2e_integration_h…
#   desc: __init__ import L0；__all__ 12 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（12 符号）
#   name_en: __all__
#   intro: action_composition_health_monitor, dr_resilience_metrics, e2e_integration_healt…
#   downstream: zephyr.feedback_loop.diagnosers.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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

__all__ = [
    "action_composition_health_monitor",
    "dr_resilience_metrics",
    "e2e_integration_health",
    "fle_dogfood_monitor",
    "fle_self_slo_metrics",
    "global_health_map",
    "memory_self_check",
    "model_health",
    "self_benchmark",
    "self_bottleneck_detector",
    "self_health_monitor",
    "self_llm_observability",
]
