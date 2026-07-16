# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_value_attribution
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""context_value_attribution.py — KE 级 ROI 归因 (B2, DD76, TASK-015 beta v)"""

import math
from dataclasses import dataclass


@dataclass
class KEAttribution:
    ke_id: str
    task_success_rate: float
    token_cost: int
    roi: float = 0.0


class ValueAttributor:
    """KE 级价值归因: ROI = task_success_rate * inverse(token_cost) (DD76)."""

    def attribute(self, ke_id: str, success_rate: float, token_cost: int) -> KEAttribution:
        inv_cost = 1.0 / math.log(max(2, token_cost))
        roi = success_rate * inv_cost
        return KEAttribution(ke_id=ke_id, task_success_rate=success_rate, token_cost=token_cost, roi=round(roi, 4))

    def rank_ke(self, attributions: list[KEAttribution]) -> list[KEAttribution]:
        return sorted(attributions, key=lambda a: a.roi, reverse=True)
