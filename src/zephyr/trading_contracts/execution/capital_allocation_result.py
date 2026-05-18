# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.capital_allocation_result

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l03_signal_generation

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-P1-003 ====

from dataclasses import dataclass, field

@dataclass(frozen=True)
class CapitalAllocationResult:
    allocation_date: str
    total_allocated_weight: float
    allocation_method: str
    idempotency_key: str
    strategy_allocations: dict[str, float] = field(default_factory=dict)
    rebalance_threshold: float = 0.05
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-003 ====
