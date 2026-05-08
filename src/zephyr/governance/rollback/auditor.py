"""G-CT-004 契约：Rollback → Audit 记录回滚操作."""

from __future__ import annotations

from zephyr.governance.audit_trail.contracts import AuditWriter


class RollbackAuditor:
    """回滚后自动记录审计."""

    def log_rollback(
        self,
        agent_id: str,
        resource: str,
        rollback_target: str,
        session_id: str = "",
    ) -> dict:
        return AuditWriter.write(
            agent_id=agent_id,
            permission="rollback",
            resource=resource,
            decision_basis=f"Rollback→Audit: {rollback_target}",
            session_id=session_id,
            granted=True,
            metadata={"rollback_target": rollback_target},
        )
