# [A_module] module_id=MOD-INT_escalation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-168 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.escalation
# [INVARIANTS] BudgetAlert 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.budget_enforcement;zephyr.security.escalation
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer.py
# [TTL] task_bound

from zephyr.integration.shared_08.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = [
    "BudgetAlert",
    "BudgetSeverity",
    "BudgetType",
    "budget_alert",
]
