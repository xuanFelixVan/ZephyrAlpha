# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.reliability
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
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包reliability: 可靠性/容量/混沌/运维族（DW-244分类，原_reliability.py聚合迁移而来）

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
#   intro: 再导出 autoscale_remediation, blast_radius, blast_radius_budget, capacity_forecast…
#   desc: __init__ import L0；__all__ 15 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（15 符号）
#   name_en: __all__
#   intro: autoscale_remediation, blast_radius, blast_radius_budget, capacity_forecast, ch…
#   downstream: zephyr.feedback_loop.detectors.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

_SUBMODULES = [
    "blast_radius",
    "blast_radius_budget",
    "capacity_forecast",
    "chaos_engineering",
    "autoscale_remediation",
    "maintenance_coordinator",
    "metric_cardinality_guard",
    "version_migrator",
    "resolution_tracker",
    "runbook_executor",
    "regulatory_audit",
    "ebpf_monitor",
    "otel_adapter",
    "openfeature",
    "flag_lifecycle",
]

__all__ = [
    "autoscale_remediation",
    "blast_radius",
    "blast_radius_budget",
    "capacity_forecast",
    "chaos_engineering",
    "ebpf_monitor",
    "flag_lifecycle",
    "maintenance_coordinator",
    "metric_cardinality_guard",
    "openfeature",
    "otel_adapter",
    "regulatory_audit",
    "resolution_tracker",
    "runbook_executor",
    "version_migrator",
]
