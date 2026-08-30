# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.cost_estimator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
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
#   name: pricing 参数
#   fields: 参数 pricing（无注解）
#   code: cost_estimator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CostEstimator
#   name_en: CostEstimator
#   intro: class CostEstimator 源码 L61-L73
#   desc: 公共方法（定义序）: estimate, check_budget；源码 L61-L73
#   inputs: pricing
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CostEstimator
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostEstimate:
    operation: str
    estimated_tokens: int
    estimated_cost_usd: float
    model_id: str


class CostEstimator:
    def __init__(self, pricing: dict[str, tuple[float, float]] | None = None):
        self._pricing = pricing or {"default": (0.01, 0.03)}

    def estimate(
        self, operation: str, input_tokens: int, output_tokens: int = 0, model_id: str = "default"
    ) -> CostEstimate:
        input_price, output_price = self._pricing.get(model_id, self._pricing["default"])
        total = (input_tokens * input_price + output_tokens * output_price) / 1000.0
        return CostEstimate(operation, input_tokens + output_tokens, total, model_id)

    def check_budget(self, estimate: CostEstimate, budget_usd: float) -> bool:
        return estimate.estimated_cost_usd <= budget_usd
