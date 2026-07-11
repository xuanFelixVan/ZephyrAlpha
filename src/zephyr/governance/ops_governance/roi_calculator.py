# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.roi_calculator
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_roi_calculator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass


@dataclass
class ROIResult:
    tokens_spent: int
    tokens_saved: int
    cost_spent: float
    cost_saved: float
    net_roi: float
    verdict: str


class ROICalculator:
    def __init__(self):
        self._total_spent_tokens: int = 0
        self._total_saved_tokens: int = 0
        self._total_spent_cost: float = 0.0
        self._total_saved_cost: float = 0.0

    def record_spend(self, tokens: int, cost: float) -> None:
        self._total_spent_tokens += tokens
        self._total_spent_cost += cost

    def record_save(self, tokens: int, cost: float) -> None:
        self._total_saved_tokens += tokens
        self._total_saved_cost += cost

    def compute(self) -> ROIResult:
        net_tokens = self._total_saved_tokens - self._total_spent_tokens
        net_cost = self._total_saved_cost - self._total_spent_cost

        if self._total_spent_cost <= 0:  # 5.167.1 修复: 累积花费浮点比较改 <= 0 (防御负数与浮点零)
            token_ratio = self._total_saved_tokens - self._total_spent_tokens
            return ROIResult(
                tokens_spent=self._total_spent_tokens,
                tokens_saved=self._total_saved_tokens,
                cost_spent=self._total_spent_cost,
                cost_saved=self._total_saved_cost,
                net_roi=float(token_ratio),
                verdict="NEUTRAL" if token_ratio >= 0 else "NEGATIVE",
            )

        token_roi = (net_tokens / self._total_spent_tokens) if self._total_spent_tokens else 0.0
        cost_roi = (net_cost / self._total_spent_cost) if self._total_spent_cost else 0.0
        net_roi = (token_roi + cost_roi) / 2

        if net_roi > 1.0:
            verdict = "EXCELLENT"
        elif net_roi > 0.5:
            verdict = "GOOD"
        elif net_roi >= 0.0:
            verdict = "NEUTRAL"
        elif net_roi > -0.5:
            verdict = "POOR"
        else:
            verdict = "TERRIBLE"

        return ROIResult(
            tokens_spent=self._total_spent_tokens,
            tokens_saved=self._total_saved_tokens,
            cost_spent=round(self._total_spent_cost, 6),
            cost_saved=round(self._total_saved_cost, 6),
            net_roi=round(net_roi, 4),
            verdict=verdict,
        )

    def reset(self) -> None:
        self._total_spent_tokens = 0
        self._total_saved_tokens = 0
        self._total_spent_cost = 0.0
        self._total_saved_cost = 0.0
