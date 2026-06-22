# [A_module] module_id=MOD-ORC_staleness_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.staleness_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""staleness_manager.py — 全局过期检测 (DD112, TASK-019)"""

from dataclasses import dataclass


@dataclass
class StalenessReport:
    ke_id: str
    age_days: float
    ttl_days: float
    exceeded: bool
    proposed_action: str  # "mark_legacy" | "rebuild_embedding" | "delete"


class StalenessManager:
    """per-KE TTL 定时任务 + 批量标记 legacy (DD112)."""

    def check(self, ke_id: str, age_days: float, ttl_days: float = 90) -> StalenessReport:
        exceeded = age_days > ttl_days
        action = "mark_legacy" if exceeded else "active"
        return StalenessReport(
            ke_id=ke_id, age_days=age_days, ttl_days=ttl_days, exceeded=exceeded, proposed_action=action
        )
