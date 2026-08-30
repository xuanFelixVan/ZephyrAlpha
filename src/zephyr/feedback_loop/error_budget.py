# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.error_budget
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""



Error Budget 状态机——monthly budget + burn_rate + exhaust_policy。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: error_budget.py
# 层: 算法
# - id: A1
#   name_zh: ① ErrorBudgetManager
#   name_en: ErrorBudgetManager
#   intro: class ErrorBudgetManager 源码 L63-L103
#   desc: 公共方法（定义序）: budgets, init_budget, record_consumption, remaining, is_exhausted；源码 L63-L103
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ErrorBudgetManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def budgets(self) -> dict[str, ErrorBudget]:
        """只读：budgets（Stage 4 公共化）。"""
        return self._budgets

    @budgets.setter
    def budgets(self, value):
        """写入：budgets（Stage 4 公共化）。"""
        self._budgets = value

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
