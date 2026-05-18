# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.asymmetric_audit

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""非对称审计——高代价审计操作双人/多人确认+quorum."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuditQuorum(BaseModel):
    operation: str
    required_approvers: int = 2
    current_approvals: list[str] = Field(default_factory=list)
    status: str = "PENDING"


class AsymmetricAudit:
    def __init__(self) -> None:
        self._quorums: dict[str, AuditQuorum] = {}
        self._history: list[dict[str, Any]] = []

    def require_quorum(self, operation: str, required_approvers: int = 2) -> AuditQuorum:
        q = AuditQuorum(operation=operation, required_approvers=required_approvers)
        self._quorums[operation] = q
        return q

    def approve(self, operation: str, approver_id: str) -> dict[str, Any]:
        q = self._quorums.get(operation)
        if not q:
            return {"approved": False, "reason": "no_quorum_required", "operation": operation}

        if approver_id in q.current_approvals:
            return {"approved": False, "reason": "duplicate_approval", "operation": operation}

        q.current_approvals.append(approver_id)
        if len(q.current_approvals) >= q.required_approvers:
            q.status = "APPROVED"
            self._history.append({"operation": operation, "status": "APPROVED", "approvers": list(q.current_approvals)})

        return {"approved": q.status == "APPROVED", "operation": operation, "current": len(q.current_approvals), "required": q.required_approvers}
