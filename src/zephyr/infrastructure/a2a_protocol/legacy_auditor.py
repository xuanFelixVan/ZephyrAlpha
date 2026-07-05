# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] zephyr.infrastructure.a2a_protocol.legacy_auditor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.audit_trail.contracts
# [CONSUMERS] zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计记录不可被修改; 审计条目必须包含 agent_id 和 timestamp
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer
# [TESTS] tests/test_a2a_protocol.py
# [A_module] module_id=MOD-INF_legacy_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3

G-CT-008 契约：A2A → Audit 审计 Agent 间通信.

"""

from __future__ import annotations


class A2AAuditor:
    """Agent-to-Agent 通信审计."""

    def log_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        session_id: str = "",
    ) -> dict:
        # lazy import to avoid L0→L2 circular dependency (Phase 2 P2 import cycle fix)
        from zephyr.governance.audit_trail.contracts import AuditWriter

        return AuditWriter.write(
            agent_id=from_agent,
            permission="a2a_message",
            resource=f"a2a://{to_agent}",
            decision_basis=f"A2A→Audit: {message_type}",
            session_id=session_id,
            granted=True,
            metadata={"from": from_agent, "to": to_agent, "type": message_type},
        )
