"""G-CT-008 契约：A2A → Audit 审计 Agent 间通信."""

from __future__ import annotations

from zephyr.governance.audit_trail.contracts import AuditWriter


class A2AAuditor:
    """Agent-to-Agent 通信审计."""

    def log_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        session_id: str = "",
    ) -> dict:
        return AuditWriter.write(
            agent_id=from_agent,
            permission="a2a_message",
            resource=f"a2a://{to_agent}",
            decision_basis=f"A2A→Audit: {message_type}",
            session_id=session_id,
            granted=True,
            metadata={"from": from_agent, "to": to_agent, "type": message_type},
        )
