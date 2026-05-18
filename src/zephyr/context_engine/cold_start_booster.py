# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.cold_start_booster

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""cold_start_booster.py — 冷启动 (DD107, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ColdStartProfile:
    ke_count: int
    strategy: str  # "auto_seed" | "manual_tune"
    estimated_commit_count: int


class ColdStartBooster:
    """build 发现 KE count < min_count → 自动种子 KE (DD107)."""
    def detect_cold_start(self, ke_count: int, min_count: int = 5) -> ColdStartProfile:
        if ke_count < min_count:
            return ColdStartProfile(ke_count=ke_count, strategy="auto_seed", estimated_commit_count=100 * (min_count - ke_count))
        return ColdStartProfile(ke_count=ke_count, strategy="manual_tune", estimated_commit_count=0)
