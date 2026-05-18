# [BLUEPRINT] MOD-INF-001 | 03_modules/l01_infrastructure/capacity-assurance/blueprint.md | §

# [MODULE] zephyr.capacity_assurance.modules.context_budget_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] deprecated
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]
# [TESTS]

"""
Context Budget Guard — Context 预算慢泄漏检测 (盲点 #17)

DEPRECATED: Use zephyr.budget_enforcer.ContextWasteDetector + zephyr.budget_enforcer.context_budget.ContextBudget.
SSoT: MOD-INF-024 budget_enforcer. This module is retained for backward compatibility only.
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


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
