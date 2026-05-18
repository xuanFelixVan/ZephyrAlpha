# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.error_budget

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Error Budget 状态机——monthly budget + burn_rate + exhaust_policy。"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ErrorBudget(BaseModel):
    contract_id: str
    monthly_budget_minutes: float = 43.8
    consumed_minutes: float = 0.0
    burn_rate: float = 1.0
    exhausted: bool = False
    escalated: bool = False


class ErrorBudgetManager:
    def __init__(self):
        self._budgets: dict[str, ErrorBudget] = {}

    def init_budget(self, contract_id: str) -> ErrorBudget:
        budget = ErrorBudget(contract_id=contract_id)
        self._budgets[contract_id] = budget
        return budget

    def record_consumption(self, contract_id: str, minutes: float) -> ErrorBudget | None:
        budget = self._budgets.get(contract_id)
        if budget is None:
            return None
        budget.consumed_minutes += minutes
        budget.burn_rate = budget.consumed_minutes / budget.monthly_budget_minutes * 30.0
        if budget.burn_rate > 10.0:
            budget.escalated = True
        if budget.consumed_minutes >= budget.monthly_budget_minutes:
            budget.exhausted = True
        return budget

    def remaining(self, contract_id: str) -> float:
        budget = self._budgets.get(contract_id)
        if budget is None:
            return 0.0
        return max(0.0, budget.monthly_budget_minutes - budget.consumed_minutes)

    def is_exhausted(self, contract_id: str) -> bool:
        budget = self._budgets.get(contract_id)
        return budget.exhausted if budget else False
