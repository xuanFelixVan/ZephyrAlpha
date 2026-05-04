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

from zephyr.shared.contracts.trace_context import TraceContext

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/order.py

CTR-004: Order / 委托指令

L05 → L06 核心数据契约。单笔委托指令（可变对象，随生命周期更新状态）。

SSoT: cross-layer-contracts.yaml → CTR-004
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L05 中生成订单或在 L06 中处理订单时，MUST 使用 Order 类型。 Order 是可变对象（frozen=false），状态通过 OrderStatus 状态机驱动。 状态转移路径为：PENDING → SUBMITTED → PARTIAL → FILLED / CANCELLED / REJECTED。 不允许从 FILLED/CANCELLED/REJECTED 回到 SUBMITTED（单向不可逆）。 quantity 和 limit_price 使用 Decimal 类型，禁止 float。 L05 生成订单时 status 默认为 PENDING，L06 在执行过程中更新状态。 订单被券商拒绝时，status MUST 变为 REJECTED，并抛出 ExecutionRejectionError（CTR-ERR-005）。
"""

@dataclass
class Order:
    order_id: str
    symbol: str
    strategy_id: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal("0")
    schema_version: str = "1.0"
    limit_price: Optional[Decimal] = None
    avg_fill_price: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    broker_order_id: Optional[str] = None
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-004 ====
