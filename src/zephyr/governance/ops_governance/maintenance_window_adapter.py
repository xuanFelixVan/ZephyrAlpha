# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.maintenance_window_adapter
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 维护窗口适配不可跳过;阈值调整必须审计
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_maintenance_window_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Maintenance Window Adapter — v0.10.0 计划维护窗口适配器。
"""

from __future__ import annotations


class MaintenanceWindowAdapter:
    def __init__(self):
        self._in_maintenance = False

    def start_maintenance(self) -> None:
        self._in_maintenance = True

    def end_maintenance(self) -> None:
        self._in_maintenance = False

    @property
    def in_maintenance(self) -> bool:
        return self._in_maintenance

    def adjust_escalation(self, original_level: str) -> str:
        if self._in_maintenance and original_level == "auto_guard":
            return "autonomous"
        return original_level
