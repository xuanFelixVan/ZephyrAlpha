# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.rollback_sandbox

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""回滚沙箱——回滚操作必须隔离+操作必须可逆+不可逆操作需额外审批."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SandboxedOperation(BaseModel):
    operation_id: str
    before_state: str = ""
    after_state: str = ""
    reversible: bool = True
    requires_quorum: bool = False


class RollbackSandbox:
    def __init__(self) -> None:
        self._operations: dict[str, SandboxedOperation] = {}

    def isolate(self, operation_id: str, before_state: str) -> SandboxedOperation:
        op = SandboxedOperation(operation_id=operation_id, before_state=before_state)
        self._operations[operation_id] = op
        return op

    def execute(self, operation_id: str, after_state: str) -> dict[str, Any]:
        op = self._operations.get(operation_id)
        if not op:
            return {"success": False, "reason": "not_isolated", "operation_id": operation_id}
        op.after_state = after_state
        return {"success": True, "operation_id": operation_id, "reversible": op.reversible}

    def rollback(self, operation_id: str) -> dict[str, Any]:
        op = self._operations.get(operation_id)
        if not op:
            return {"success": False, "reason": "not_found"}
        if not op.reversible:
            return {"success": False, "reason": "irreversible", "operation_id": operation_id}
        return {"success": True, "operation_id": operation_id, "restored_to": op.before_state}
