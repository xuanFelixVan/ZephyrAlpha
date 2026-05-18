"""G-CT-003 消费端 — Escalation.on_rollback_failure() + G-CT-004/G-CT-006/G-CT-008 升级入口."""
from __future__ import annotations

from typing import Any

from zephyr.rollback.governance.result_types import RollbackResult


class EscalationContracts:
    """升级协议入口 — G-CT-003/004/006/008 消费端."""

    def on_rollback_failure(self, result: RollbackResult) -> dict[str, Any]:
        if not result.needs_escalation:
            return {"escalated": False, "reason": "no_escalation_needed", "rollback_id": result.rollback_id}

        return {
            "escalated": True,
            "rollback_id": result.rollback_id,
            "target": result.target,
            "status": result.status.value,
            "validation_result": result.validation_result.value,
            "error_detail": result.error_detail,
            "ticket_id": f"ESC-{result.rollback_id}",
            "priority": "P1" if result.status.value == "FAILED" else "P2",
        }

    def on_budget_alert(self, alert: Any) -> dict[str, Any]:
        from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert

        if not isinstance(alert, BudgetAlert):
            return {"escalated": False, "reason": "invalid_alert_type"}

        severity = alert.severity.value
        response = {
            "escalated": True,
            "alert_id": alert.alert_id,
            "session_id": alert.session_id,
            "severity": severity,
            "action": "notify" if severity == "WARNING" else "escalate",
        }

        if severity == "CRITICAL":
            response["ticket_id"] = f"ESC-BUDGET-{alert.alert_id}"
            response["priority"] = "P0"

        return response

    def on_a2a_failure(self, communication: Any) -> dict[str, Any]:
        return {
            "escalated": True,
            "a2a_id": getattr(communication, "a2a_id", ""),
            "from_agent": getattr(communication, "from_agent_id", ""),
            "to_agent": getattr(communication, "to_agent_id", ""),
            "action": "retry_or_degrade",
            "ticket_id": f"ESC-A2A-{getattr(communication, 'a2a_id', 'unknown')}",
        }
