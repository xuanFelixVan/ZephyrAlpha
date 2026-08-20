# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.asymmetric_audit
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_forensic_a
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AsymmetricAudit - quorum-based approval for high-risk operations.

治本(2026-07-19): 实现 require_quorum/approve 以匹配 tests/agent_rbac/test_forensic_a.py 契约.
- require_quorum(operation, required_approvers): 登记操作所需 quorum
- approve(operation, approver): 累计不同 approver, 达到 quorum 时 approved=True
- duplicate approver 被拒绝(approved=False)
"""

from __future__ import annotations

from typing import Any


class AsymmetricAudit:
    def __init__(self) -> None:
        self._quorums: dict[str, int] = {}
        self._approvers: dict[str, set[str]] = {}

    def require_quorum(self, operation: str, required_approvers: int) -> None:
        self._quorums[operation] = required_approvers
        self._approvers.setdefault(operation, set())

    def approve(self, operation: str, approver: str) -> dict[str, Any]:
        required = self._quorums.get(operation, 1)
        approvers = self._approvers.setdefault(operation, set())
        if approver in approvers:
            return {
                "approved": False,
                "reason": "duplicate_approver",
                "current": len(approvers),
                "required": required,
            }
        approvers.add(approver)
        approved = len(approvers) >= required
        return {
            "approved": approved,
            "current": len(approvers),
            "required": required,
        }


__all__ = ["AsymmetricAudit"]
