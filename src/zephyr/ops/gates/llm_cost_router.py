# [A_module] module_id=MOD-UNK_llm_cost_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.gates.llm_cost_router

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""LLM Cost Router — v0.3.0 R20

Blindspot: All LLM calls use costliest model regardless of task criticality.
Risk: R20 — FLE burns budget on low-value diagnostics.
"""

from dataclasses import dataclass


@dataclass
class LLMCostRouter:
    budget_monthly: float = 1000.0
    spent: float = 0.0

    def route(self, task_priority: int) -> str:
        return "cheap-model" if task_priority < 5 else "best-model"
