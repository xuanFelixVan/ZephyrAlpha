# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.trading_contracts.execution.order

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] l05_portfolio_construction; l06_trade_execution; l07_post_trade_analytics

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# ==== BEGIN CODGEN:CTR-004 ====
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from zephyr.shared.contracts.core.trace_context import TraceContext

@dataclass
class Order:
    idempotency_key: str
    order_id: str
    order_type: OrderType
    quantity: Decimal
    side: OrderSide
    strategy_id: str
    symbol: str
    avg_fill_price: Decimal | None = None
    broker_order_id: str | None = None
    created_at: datetime | None = None
    filled_quantity: Decimal = Decimal("0")
    limit_price: Decimal | None = None
    schema_version: str = "1.0"
    status: OrderStatus = OrderStatus.PENDING
    trace_context: TraceContext | None = None
    updated_at: datetime | None = None


# ==== END CODGEN:CTR-004 ====
