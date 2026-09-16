# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
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
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包reliability: 可靠性/容量/混沌/运维族（DW-244分类，原_reliability.py聚合迁移而来）

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_feedback_loop/algo_flow/detectors/reliability/reliability__init__.yaml
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
