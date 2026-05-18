# [BLUEPRINT] MOD-INF-024 | docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md | §12

# [MODULE] zephyr.budget_enforcer.rbac_bridge

# [INVARIANTS] RBAC配额降级规则不可绕过;权限降级必须审计

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md

# [CONSUMERS] zephyr.budget_enforcer

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id

# [TESTS] tests/test_budget_enforcer.py

"""[BLUEPRINT] MOD-INF-024 | docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md | §12

G-CT-007 契约：Budget → RBAC 配额限制.

"""





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


