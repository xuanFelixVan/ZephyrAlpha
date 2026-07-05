# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.capacity_governance.cost_estimator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
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
