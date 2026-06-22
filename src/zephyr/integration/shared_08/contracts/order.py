# [A_module] module_id=MOD-INT_order | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# ==== BEGIN CODGEN:CTR-004 ====
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext
from zephyr.shared.contracts import OrderSide, OrderStatus, OrderType

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-29"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/order.py

CTR-004: Order / 委托指令

L05 → L06 核心数据契约。单笔委托指令（可变对象，随生命周期更新状态）。

SSoT: cross_layer_contracts.yaml -> CTR-004
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 L05 中生成订单或在 L06 中处理订单时，MUST 使用 Order 类型。 Order 是可变对象（frozen=false），状态通过 OrderStatus 状态机驱动。 状态转移路径为：PENDING → SUBMITTED → PARTIAL → FILLED / CANCELLED / REJECTED。 不允许从 FILLED/CANCELLED/REJECTED 回到 SUBMITTED（单向不可逆）。 quantity 和 limit_price 使用 Decimal 类型，禁止 float。 L05 生成订单时 status 默认为 PENDING，L06 在执行过程中更新状态。 订单被券商拒绝时，status MUST 变为 REJECTED，并抛出 ExecutionRejectionError（CTR-ERR-005）。
"""


@dataclass
class Order:
    idempotency_key: str
    idempotency_key: str
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
