"""G-CT-007 契约：Budget → RBAC 配额限制."""

from __future__ import annotations


class BudgetRBACBridge:
    """预算消耗→RBAC权限降级."""

    def check_budget(self, agent_id: str, token_used: int, token_limit: int) -> dict:
        exceeded = token_used > token_limit
        return {
            "agent_id": agent_id,
            "token_used": token_used,
            "token_limit": token_limit,
            "exceeded": exceeded,
            "action": "REVOKE_WRITE" if exceeded else "ALLOW",
        }
