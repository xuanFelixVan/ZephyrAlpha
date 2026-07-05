# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.auditor
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.governance.audit_trail.contracts
# [CONSUMERS] rollback_executor;rollback_verifier;auto_rollback_trigger
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;AuditError
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-INF_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md

G-CT-004 契约：Rollback → Audit 记录回滚操作.

"""

from __future__ import annotations


class RollbackAuditor:
    """回滚后自动记录审计."""

    def log_rollback(
        self,
        agent_id: str,
        resource: str,
        rollback_target: str,
        session_id: str = "",
    ) -> dict:
        # lazy import to avoid L0→L2 circular dependency (Phase 2 P2 import cycle fix)
        from zephyr.governance.audit_trail.contracts import AuditWriter

        return AuditWriter.write(
            agent_id=agent_id,
            permission="rollback",
            resource=resource,
            decision_basis=f"Rollback→Audit: {rollback_target}",
            session_id=session_id,
            granted=True,
            metadata={"rollback_target": rollback_target},
        )
