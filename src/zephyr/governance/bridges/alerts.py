# [A_module] module_id=MOD-RES_alerts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md

# [MODULE] zephyr.infrastructure.budget_enforcement.bridges.alerts

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-006 — BudgetAlert re-exported from shared.contracts.escalation.

Canonical definition: zephyr.shared.contracts.escalation.budget_alert
"""

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = ["BudgetAlert", "BudgetSeverity", "BudgetType"]
