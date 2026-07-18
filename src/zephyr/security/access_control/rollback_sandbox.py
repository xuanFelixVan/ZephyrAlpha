# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.rollback_sandbox
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.test_rollback_sandbox; tests.agent_rbac.test_forensic_c
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""RollbackSandbox - isolate/execute/rollback pattern for reversible operations.

治本(2026-07-19): 实现 isolate/execute/rollback 以匹配 tests/agent_rbac/test_forensic_c.py 契约.
- isolate(op_id, before_data) -> SandboxedOperation (默认 reversible=True)
- execute(op_id, after_data) 标记已执行
- rollback(op_id) -> {success: bool}, reversible=False 时 success=False
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SandboxedOperation:
    op_id: str = ""
    before_data: str = ""
    after_data: str = ""
    executed: bool = False
    reversible: bool = True
    rolled_back: bool = False


class RollbackSandbox:
    def __init__(self) -> None:
        self._operations: dict[str, SandboxedOperation] = {}

    def isolate(self, op_id: str, before_data: str) -> SandboxedOperation:
        op = SandboxedOperation(op_id=op_id, before_data=before_data)
        self._operations[op_id] = op
        return op

    def execute(self, op_id: str, after_data: str) -> None:
        op = self._operations.get(op_id)
        if op is None:
            op = SandboxedOperation(op_id=op_id)
            self._operations[op_id] = op
        op.after_data = after_data
        op.executed = True

    def rollback(self, op_id: str) -> dict[str, Any]:
        op = self._operations.get(op_id)
        if op is None:
            return {"success": False, "reason": "not_found"}
        if not op.reversible:
            return {"success": False, "reason": "irreversible"}
        op.rolled_back = True
        return {"success": True}


__all__ = ["RollbackSandbox", "SandboxedOperation"]
