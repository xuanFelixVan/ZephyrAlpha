# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.escalation
# [INVARIANTS] BudgetAlert 告警阈值不可被静默;告警事件必须可审计
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.budget_enforcer;zephyr.escalation_engine
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_budget_enforcer.py

from zephyr.shared.contracts.escalation.budget_alert import BudgetAlert, BudgetSeverity, BudgetType

__all__ = ["BudgetAlert", "BudgetSeverity", "BudgetType"]
