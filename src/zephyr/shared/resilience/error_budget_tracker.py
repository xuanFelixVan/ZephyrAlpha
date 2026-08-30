# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.error_budget_tracker
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loop.auto_evolution
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: slo_target 参数
#   fields: 参数 slo_target（无注解）
#   code: error_budget_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: window_hours 参数
#   fields: 参数 window_hours（无注解）
#   code: error_budget_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ErrorBudgetTracker
#   name_en: ErrorBudgetTracker
#   intro: class ErrorBudgetTracker 源码 L67-L94
#   desc: 公共方法（定义序）: record_success, record_error, status；源码 L67-L94
#   inputs: slo_target window_hours
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ErrorBudgetTracker
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__ ; zephyr.feedback_loo…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetStatus:
    total_budget: float
    consumed: float
    remaining: float
    burn_rate: float
    time_to_exhaustion_hours: float


class ErrorBudgetTracker:
    def __init__(self, slo_target: float = 0.999, window_hours: float = 720.0):
        if slo_target < 0.0 or slo_target >= 1.0:
            raise ValueError(f"slo_target must be in [0.0, 1.0), got {slo_target}")
        if window_hours <= 0:
            raise ValueError(f"window_hours must be > 0, got {window_hours}")
        self._slo_target = slo_target
        self._window_hours = window_hours
        self._errors: int = 0
        self._total_requests: int = 0

    def record_success(self) -> None:
        self._total_requests += 1

    def record_error(self) -> None:
        self._errors += 1
        self._total_requests += 1

    def status(self) -> BudgetStatus:
        budget = 1.0 - self._slo_target
        if self._total_requests == 0:
            return BudgetStatus(budget, 0.0, budget, 0.0, float("inf"))
        error_rate = self._errors / self._total_requests
        consumed = max(0.0, error_rate - (1.0 - self._slo_target - budget))
        remaining = max(0.0, budget - consumed)
        burn_rate = consumed / self._window_hours if self._window_hours > 0 else 0.0
        tte = remaining / burn_rate if burn_rate > 0 else float("inf")
        return BudgetStatus(budget, consumed, remaining, burn_rate, tte)
