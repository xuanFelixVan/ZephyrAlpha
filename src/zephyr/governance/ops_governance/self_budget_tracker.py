# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.self_budget_tracker
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
# [A_module] module_id=MOD-RES_self_budget_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass


@dataclass
class SelfBudgetStatus:
    tokens_used: int
    budget_cap: int
    usage_ratio: float
    efficiency: float
    should_disable_safeguards: bool
    advice: str


class SelfBudgetTracker:
    def __init__(self, daily_cap: int = 50000, efficiency_threshold: float = 0.5):
        self._daily_cap = daily_cap
        self._efficiency_threshold = efficiency_threshold
        self._tokens_used: int = 0
        self._useful_tokens: int = 0
        self._wasted_tokens: int = 0
        self._start_of_day: float = time.time()

    def record_usage(self, tokens: int, useful: bool = True) -> None:
        self._tokens_used += tokens
        if useful:
            self._useful_tokens += tokens
        else:
            self._wasted_tokens += tokens

    def status(self) -> SelfBudgetStatus:
        usage_ratio = self._tokens_used / self._daily_cap if self._daily_cap else 0.0
        efficiency = self._useful_tokens / max(self._tokens_used, 1)

        should_disable = efficiency < self._efficiency_threshold and self._tokens_used > 1000

        if should_disable:
            advice = f"自预算效率 {efficiency:.1%} < {self._efficiency_threshold:.0%}，建议禁用部分护卫减少消耗"
        elif usage_ratio > 0.8:
            advice = "自预算消耗 >80%，建议降低护卫强度"
        elif usage_ratio > 0.5:
            advice = f"自预算消耗 {usage_ratio:.0%}，注意控制"
        else:
            advice = "自预算正常"

        return SelfBudgetStatus(
            tokens_used=self._tokens_used,
            budget_cap=self._daily_cap,
            usage_ratio=usage_ratio,
            efficiency=efficiency,
            should_disable_safeguards=should_disable,
            advice=advice,
        )

    def remaining(self) -> int:
        return max(self._daily_cap - self._tokens_used, 0)

    def reset_daily(self) -> None:
        self._tokens_used = 0
        self._useful_tokens = 0
        self._wasted_tokens = 0
        self._start_of_day = time.time()
