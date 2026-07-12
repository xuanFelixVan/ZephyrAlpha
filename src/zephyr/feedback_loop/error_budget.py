# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.error_budget
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_error_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Error Budget 状态机——monthly budget + burn_rate + exhaust_policy。"""


from pydantic import BaseModel


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
