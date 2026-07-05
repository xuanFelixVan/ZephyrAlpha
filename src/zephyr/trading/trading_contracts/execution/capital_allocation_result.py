# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.capital_allocation_result
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] signal
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_capital_allocation_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
