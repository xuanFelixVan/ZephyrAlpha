# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.governance.contracts
# [DOMAIN] D-INFRA_OPS
# [DEPENDENCIES] zephyr.governance.audit_trail.bridges.anomaly
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""G-CT-002 Rollback 消费端 — on_audit_anomaly() 接口."""

from __future__ import annotations

from zephyr.governance.audit_trail.bridges.anomaly import AnomalyEvent


class RollbackHandler:
    """回滚处理器 — G-CT-002 消费端."""

    def on_audit_anomaly(self, event: AnomalyEvent) -> dict:
        """接收 Audit 异常事件 → 触发回滚流程."""
        action = self._determine_action(event)

        return {
            "triggered": True,
            "event_type": event.event_type,
            "action": action,
            "agent_id": event.agent_id,
            "resource_path": event.resource_path,
            "rollback_target": f"rollback:{event.operation_signature}@{event.resource_path}",
        }

    @staticmethod
    def _determine_action(event: AnomalyEvent) -> str:
        if event.severity == "HIGH":
            return "IMMEDIATE_ROLLBACK"
        return "FLAGGED_FOR_REVIEW"
