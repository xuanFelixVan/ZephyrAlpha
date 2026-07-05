# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.execution.order
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] pf_core; ex_core; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_order | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from enum import Enum


class OrderSide(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

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
