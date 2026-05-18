# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.fill

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l06_trade_execution; l07_post_trade_analytics

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-005 ====
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from zephyr.shared.contracts.core.trace_context import TraceContext

@dataclass(frozen=True)
class Fill:
    fill_id: str
    fill_price: Decimal
    fill_timestamp: datetime
    filled_quantity: Decimal
    idempotency_key: str
    order_id: str
    strategy_id: str
    symbol: str
    broker_fill_id: str | None = None
    commission: Decimal = Decimal("0")
    schema_version: str = "1.0"
    slippage: Decimal | None = None
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-005 ====
