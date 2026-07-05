# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.bridges.alerts
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.escalation.budget_alert
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
# [A_module] module_id=MOD-RES_alerts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-006 — BudgetAlert re-exported from shared.contracts.escalation.

Canonical definition: zephyr.shared.contracts.escalation.budget_alert
"""

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = ["BudgetAlert", "BudgetSeverity", "BudgetType"]
