# [A_module] module_id=MOD-INF_context_budget_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md

# [MODULE] zephyr.infrastructure.capacity_assurance.context_budget_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] deprecated
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]
# [TESTS]

"""
Context Budget Guard — Context 预算慢泄漏检测 (盲点 #17)

DEPRECATED: Use zephyr.infrastructure.budget_enforcement.ContextWasteDetector + zephyr.infrastructure.budget_enforcement.context_budget.ContextBudget.
SSoT: MOD-INF-024 budget-enforcer. This module is retained for backward compatibility only.
"""

import time


class ContextBudgetGuard:
    """
    Context 预算守护 (盲点 #17)
    """

    WARN_THRESHOLD = 0.80
    CRITICAL_THRESHOLD = 0.95
    SLI_ID = "CAP-CTX-001"

    def __init__(self, max_context_tokens: int = 128000):
        self.max_context_tokens = max_context_tokens

    def check(self, current_tokens: int) -> dict:
        usage = current_tokens / self.max_context_tokens
        level = "HEALTHY"
        if usage > self.CRITICAL_THRESHOLD:
            level = "CRITICAL"
        elif usage > self.WARN_THRESHOLD:
            level = "WARNING"

        return {
            "sli_id": self.SLI_ID,
            "current_tokens": current_tokens,
            "max_tokens": self.max_context_tokens,
            "usage_pct": round(usage * 100, 1),
            "level": level,
            "suggestion": "Consider truncation or summarization" if level != "HEALTHY" else "",
            "timestamp": time.time(),
        }
