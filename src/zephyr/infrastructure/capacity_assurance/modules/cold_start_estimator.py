# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.modules.cold_start_estimator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_cold_start_estimator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Cold Start Estimator — 冷启动预算估算 (盲点 #27)
特性：
  - 人工标注初始 budget：Day-0 按 50% 分配给新生模块
  - 渐进学习：实时反馈摄入校准
"""


class ColdStartEstimator:
    """
    冷启动估算器 (盲点 #27)
    """

    DAY0_BUDGET_PCT = 0.50

    def __init__(self):
        self._initial_budgets: dict[str, float] = {}
        self._observed_costs: dict[str, list[float]] = {}

    def set_initial_budget(self, module: str, budget: float):
        self._initial_budgets[module] = budget

    def get_day0_budget(self, module: str) -> float:
        initial = self._initial_budgets.get(module, 0)
        return initial * self.DAY0_BUDGET_PCT

    def record_cost(self, module: str, cost: float):
        if module not in self._observed_costs:
            self._observed_costs[module] = []
        self._observed_costs[module].append(cost)

    def calibrate(self, module: str) -> float | None:
        costs = self._observed_costs.get(module, [])
        if not costs:
            return None
        return sum(costs) / len(costs)
