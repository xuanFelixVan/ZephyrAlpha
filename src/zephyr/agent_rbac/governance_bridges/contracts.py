# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.governance_bridges.contracts

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-001 契约生产端 — RBAC 侧调用 Audit 的集成代码."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from zephyr.audit_trail.bridges.contracts import AuditWriter


class RBACAuditBridge:
    """RBAC→Audit 桥接器 — G-CT-001 生产端."""

    def __init__(self) -> None:
        self._audit = AuditWriter()

    def check_and_log(
        self,
        agent_id: str,
        permission: str,
        resource: str,
        session_id: str = "",
    ) -> dict[str, Any]:
        """执行权限检查并记录审计."""
        granted = self._check_permission(agent_id, permission, resource)

        decision_basis = (
            f"RBAC: agent={agent_id} perm={permission} res={resource}"
        )

        record = self._audit.write(
            agent_id=agent_id,
            permission=permission,
            resource=resource,
            decision_basis=decision_basis,
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            granted=granted,
        )

        return {
            "granted": granted,
            "audit_record": record,
        }

    @staticmethod
    def _check_permission(agent_id: str, permission: str, resource: str) -> bool:
        """权限检查（Phase 2 实现完整 RBAC 逻辑）."""
        allowed_permissions = {"read", "write", "execute"}
        return permission in allowed_permissions
