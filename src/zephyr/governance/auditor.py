# [A_module] module_id=MOD-RES_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

# [MODULE] zephyr.infrastructure.rollback.auditor

# [INVARIANTS] 审计记录不可篡改

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] rollback_executor;rollback_verifier;auto_rollback_trigger

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] RollbackError;AuditError

# [TESTS] tests/rollback/

"""[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

G-CT-004 契约：Rollback → Audit 记录回滚操作.

"""

from __future__ import annotations

import importlib as _il

_mod = _il.import_module("zephyr.governance.audit_trail.contracts")
AuditWriter = _mod.AuditWriter


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
