# ==== BEGIN CODGEN:CTR-004 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.order
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from dataclasses import dataclass, field

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
from zephyr.trading.trading_contracts.execution.order import OrderSide
from zephyr.trading.trading_contracts.execution.order import OrderStatus
from zephyr.trading.trading_contracts.execution.order import OrderType
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-07-02"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/order.py

CTR-004: Order / 委托指令

D_PORTFOLIO_CORE → D_EXECUTION_CORE 核心数据契约。单笔委托指令（可变对象，随生命周期更新状态）。

SSoT: cross_layer_contracts.yaml -> CTR-004
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当你需要在 D_PORTFOLIO_CORE 中生成订单或在 D_EXECUTION_CORE 中处理订单时，MUST 使用 Order 类型。 Order 是可变对象（frozen=false），状态通过 OrderStatus 状态机驱动。 状态转移路径为：PENDING → SUBMITTED → PARTIAL → FILLED / CANCELLED / REJECTED。 不允许从 FILLED/CANCELLED/REJECTED 回到 SUBMITTED（单向不可逆）。 quantity 和 limit_price 使用 Decimal 类型，禁止 float。 D_PORTFOLIO_CORE 生成订单时 status 默认为 PENDING，D_EXECUTION_CORE 在执行过程中更新状态。 订单被券商拒绝时，status MUST 变为 REJECTED，并抛出 ExecutionRejectionError（CTR-ERR-005）。
"""

@dataclass
class Order:
    idempotency_key: str
    order_id: str
    order_type: OrderType
    quantity: Decimal
    side: OrderSide
    strategy_id: str
    symbol: str
    avg_fill_price: Optional[Decimal] = None
    broker_order_id: Optional[str] = None
    created_at: Optional[datetime] = None
    filled_quantity: Decimal = Decimal("0")
    limit_price: Optional[Decimal] = None
    schema_version: str = "1.0"
    status: OrderStatus = OrderStatus.PENDING
    trace_context: Optional[TraceContext] = None
    updated_at: Optional[datetime] = None

# ==== END CODGEN:CTR-004 ====








