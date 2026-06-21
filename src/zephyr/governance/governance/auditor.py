# [A_module] module_id=MOD-GOV_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

# [MODULE] zephyr.infrastructure.rollback.governance.auditor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-004 契约：Rollback → Audit 记录回滚操作."""

# STUB: from zephyr.governance.contracts import AuditWriter
# Reason: zephyr.infrastructure.rollback.contracts module does not exist yet
try:
    import importlib as _il
    _mod = _il.import_module("zephyr.infrastructure.rollback.contracts")
    AuditWriter = _mod.AuditWriter
except (ImportError, AttributeError):
    class AuditWriter:
        def write(self, **kwargs):
            return kwargs

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
