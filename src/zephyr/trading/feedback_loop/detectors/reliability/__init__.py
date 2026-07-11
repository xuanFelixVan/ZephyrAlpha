# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.reliability
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.detectors.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新detectors/__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [A_module] module_id=MOD-UNK_reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [GOV-DOC-018] 子包reliability: 可靠性/容量/混沌/运维族（DW-244分类，原_reliability.py聚合迁移而来）

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

__all__ = ['autoscale_remediation', 'blast_radius', 'blast_radius_budget', 'capacity_forecast', 'chaos_engineering', 'ebpf_monitor', 'flag_lifecycle', 'maintenance_coordinator', 'metric_cardinality_guard', 'openfeature', 'otel_adapter', 'regulatory_audit', 'resolution_tracker', 'runbook_executor', 'version_migrator']

