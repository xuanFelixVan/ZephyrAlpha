# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.governance.auditor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-008 契约：A2A → Audit 审计 Agent 间通信."""

from __future__ import annotations

from zephyr.audit_trail.bridges.contracts import AuditWriter


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
