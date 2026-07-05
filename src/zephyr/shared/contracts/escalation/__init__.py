# [A_module] module_id=MOD-SHR_escalation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.escalation
# [INVARIANTS] BudgetAlert 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.budget_enforcement;zephyr.security.escalation
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer.py
# [TTL] permanent

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = [
    "BudgetAlert",
    "BudgetSeverity",
    "BudgetType",
    "budget_alert",
]
