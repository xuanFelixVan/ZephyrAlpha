# [A_module] module_id=MOD-ORC_position_optimizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.position_optimizer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""position_optimizer.py — 位置优化 (DD104, TASK-019)"""

from dataclasses import dataclass


@dataclass
class PositionScore:
    section_name: str
    page: int
    priority: float
    is_optimal: bool


class PositionOptimizer:
    """Order KE 优先注入前 20%, avoid truncation tail (DD104)."""

    def optimize_order(self, ke_items: list[tuple[str, float]]) -> list[PositionScore]:
        ranked = sorted(ke_items, key=lambda x: x[1], reverse=True)
        total = len(ranked)
        return [
            PositionScore(section_name=k, page=i, priority=s, is_optimal=i < total * 0.2)
            for i, (k, s) in enumerate(ranked)
        ]
