# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-008 契约：A2A → Audit 审计 Agent 间通信."""

# STUB: from zephyr.governance.escalation.contracts import AuditWriter
# Reason: zephyr.infrastructure.rollback.contracts does not export AuditWriter yet
try:
    import importlib as _il

    _mod = _il.import_module("zephyr.infrastructure.rollback.contracts")
    AuditWriter = _mod.AuditWriter
except (ImportError, AttributeError):

    class AuditWriter:
        def write(self, **kwargs):
            return kwargs


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
