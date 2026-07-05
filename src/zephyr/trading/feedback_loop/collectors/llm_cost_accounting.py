# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.llm_cost_accounting
# [DOMAIN] D_OPS
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_llm_cost_accounting | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
