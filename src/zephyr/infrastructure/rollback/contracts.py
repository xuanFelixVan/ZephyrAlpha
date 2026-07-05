# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.contracts
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.governance.audit_trail.anomaly
# [CONSUMERS] rollback包内所有模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-002 Rollback 消费端接口契约
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 定义所有回滚异常类型
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-INF_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md

G-CT-002 Rollback 消费端 — on_audit_anomaly() 接口.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

# lazy import to avoid L0→L2 circular dependency (Phase 2 P2 import cycle fix)
if TYPE_CHECKING:
    from zephyr.governance.audit_trail.anomaly import AnomalyResult as AnomalyEvent


class RollbackHandler:
    """回滚处理器 — G-CT-002 消费端."""

    def on_audit_anomaly(self, event: AnomalyEvent) -> dict:
        """接收 Audit 异常事件 → 触发回滚流程."""

        action = self._determine_action(event)

        return {
            "triggered": True,
            "event_type": event.signature.value if hasattr(event, "signature") else "unknown",
            "action": action,
            "agent_id": event.evidence.get("agent_id", "unknown") if hasattr(event, "evidence") else "unknown",
            "resource_path": event.evidence.get("resource", "unknown") if hasattr(event, "evidence") else "unknown",
            "rollback_target": f"rollback:{event.signature.value}@{event.evidence.get('resource', 'unknown') if hasattr(event, 'evidence') else 'unknown'}",
        }

    @staticmethod
    def _determine_action(event: AnomalyEvent) -> str:
        if event.severity == "HIGH":
            return "IMMEDIATE_ROLLBACK"

        return "FLAGGED_FOR_REVIEW"
