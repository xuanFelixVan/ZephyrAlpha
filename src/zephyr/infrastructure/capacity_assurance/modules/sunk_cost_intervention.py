# [A_module] module_id=MOD-INF_sunk_cost_intervention | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md

# [MODULE] zephyr.infrastructure.capacity_assurance.sunk_cost_intervention

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] deprecated
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]
# [TESTS]

"""
Sunk Cost Intervention — 沉没成本干预 (盲点 #37)

DEPRECATED: Use zephyr.infrastructure.budget_enforcement.SelfBudgetTracker + zephyr.infrastructure.budget_enforcement.BurnRateMonitor.
SSoT: MOD-INF-024 budget-enforcer. This module is retained for backward compatibility only.
"""

import time


class SunkCostIntervention:
    """
    沉没成本干预 (盲点 #37)
    """

    TOKEN_SHARE_THRESHOLD = 0.30
    WINDOW_HOURS = 48

    def __init__(self):
        self._module_costs: dict[str, list[tuple[float, float]]] = {}

    def record(self, module: str, tokens_used: int, cost_usd: float):
        if module not in self._module_costs:
            self._module_costs[module] = []
        self._module_costs[module].append((time.time(), tokens_used))

    def analyze(self) -> dict:
        total_tokens = sum(sum(r[1] for r in recs) for recs in self._module_costs.values())
        if total_tokens == 0:
            return {"interventions": []}

        interventions = []
        for module, records in self._module_costs.items():
            module_tokens = sum(r[1] for r in records)
            share = module_tokens / max(total_tokens, 1)
            if share > self.TOKEN_SHARE_THRESHOLD:
                interventions.append(
                    {
                        "module": module,
                        "token_share": round(share, 2),
                        "suggestion": f"Module {module} consumes {share:.1%} of tokens — consider replacing or simplifying.",
                    }
                )

        return {"interventions": interventions, "total_tokens": total_tokens}
