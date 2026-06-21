# [A_module] module_id=MOD-UNK__reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.detectors._reliability
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.observability.feedback_loop.detectors.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py

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
