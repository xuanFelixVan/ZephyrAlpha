# [BLUEPRINT] MOD-INF-024 | docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md | §12

# [MODULE] zephyr.budget_enforcer.alerts

# [INVARIANTS] 告警阈值不可被静默;告警事件必须可审计

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md

# [CONSUMERS] zephyr.budget_enforcer

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 budget_context 和 operation_id

# [TESTS] tests/test_budget_enforcer.py

"""G-CT-006 — BudgetAlert re-exported from shared.contracts.escalation.

Canonical definition: zephyr.shared.contracts.escalation.budget_alert
"""

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = ["BudgetAlert", "BudgetSeverity", "BudgetType"]


