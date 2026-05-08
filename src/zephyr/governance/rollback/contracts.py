"""G-CT-002 Rollback 消费端 — on_audit_anomaly() 接口."""

from __future__ import annotations

from zephyr.governance.audit_trail.anomaly import AnomalyEvent


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
