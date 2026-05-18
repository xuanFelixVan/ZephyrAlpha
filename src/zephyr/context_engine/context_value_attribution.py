# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.context_value_attribution

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""context_value_attribution.py — KE 级 ROI 归因 (B2, DD76, TASK-015 beta v)"""
from __future__ import annotations
from dataclasses import dataclass
import math


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
