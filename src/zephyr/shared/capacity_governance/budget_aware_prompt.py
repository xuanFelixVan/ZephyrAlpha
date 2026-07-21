# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.budget_aware_prompt
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
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptBudget:
    max_tokens: int
    used_tokens: int
    remaining_tokens: int


class BudgetAwarePrompt:
    def __init__(self, token_budget: int = 4000, reserve_for_response: int = 1000):
        self._budget = token_budget
        self._reserve = reserve_for_response
        self._used = 0

    def allocate(self, prompt_tokens: int) -> PromptBudget:
        available = self._budget - self._reserve - self._used
        if prompt_tokens > available:
            prompt_tokens = max(0, available)
        self._used += prompt_tokens
        return PromptBudget(self._budget, self._used, self._budget - self._used)

    def reset(self) -> None:
        self._used = 0

    def can_fit(self, tokens: int) -> bool:
        return tokens <= (self._budget - self._reserve - self._used)
