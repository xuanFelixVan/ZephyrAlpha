# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.position

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l06_trade_execution; l07_post_trade_analytics; l04_risk_management; l11_ml_platform

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
# ==== BEGIN CODGEN:CTR-006 ====
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from zephyr.shared.contracts.core.trace_context import TraceContext

@dataclass(frozen=True)
class PositionSnapshot:
    as_of_timestamp: datetime
    idempotency_key: str
    portfolio_id: str
    cash: Decimal = Decimal("0")
    gross_leverage: float = 1.0
    holdings: dict[str, Decimal] = field(default_factory=dict)
    market_values: dict[str, Decimal] = field(default_factory=dict)
    schema_version: str = "1.0"
    total_market_value: Decimal = Decimal("0")
    trace_context: TraceContext | None = None


# ==== END CODGEN:CTR-006 ====
