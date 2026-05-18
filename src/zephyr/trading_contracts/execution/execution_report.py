# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.execution_report

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l07_post_trade_analytics

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ==== BEGIN CODGEN:CTR-P1-007 ====

from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class ExecutionReport:
    order_id: str
    symbol: str
    direction: str
    intended_quantity: int
    actual_quantity: int
    intended_price: Decimal
    vwap_price: Decimal
    slippage_bps: float
    commission: Decimal
    execution_start: str
    execution_end: str
    broker_id: str
    idempotency_key: str
    algo_type: str = "NONE"
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-007 ====
