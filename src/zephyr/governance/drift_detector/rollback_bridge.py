"""G-CT-006 契约：Drift → Rollback 漂移触发回滚."""

from __future__ import annotations


class DriftRollbackBridge:
    """行为漂移→回滚触发."""

    def on_drift_detected(
        self, agent_id: str, drift_type: str, severity: str
    ) -> dict:
        return {
            "triggered": severity in {"HIGH", "CRITICAL"},
            "agent_id": agent_id,
            "drift_type": drift_type,
            "action": "ROLLBACK" if severity in {"HIGH", "CRITICAL"} else "OBSERVE",
        }
