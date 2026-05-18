# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.collectors.llm_cost_accounting

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""LLM Cost Accounting — v0.4.0 R35

Blindspot: LLM API costs unaccounted; budget invisible.
Risk: R35 — Surprise bill from runaway LLM calls.
"""
from dataclasses import dataclass

@dataclass
class LLMCostAccounting:
    total_cost: float = 0.0

    def record(self, model: str, tokens: int) -> None:
        self.total_cost += tokens * 0.00001
