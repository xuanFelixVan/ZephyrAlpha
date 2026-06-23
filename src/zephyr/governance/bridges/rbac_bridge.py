# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.infrastructure.budget_enforcement.bridges.rbac_bridge
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.bridges.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_rbac_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""G-CT-007 契约：Budget → RBAC 配额限制."""


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
