# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain-ex_core/execution-core/blueprint.md
# [MODULE] zephyr.ex_core.order_manager
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.broker_interface; zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_order_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ex_core
# category: order_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — Order Manager

订单管理器。管理订单全生命周期：创建->风控校验->路由->状态跟踪。

CTR 契约：
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE
  生产者 — CTR-005 (Fill) -> D_REPORTING
  生产者 — CTR-ERR-005 (ExecutionRejectionError) -> D_PORTFOLIO_CORE, D_REPORTING

SSoT: cross_layer_contracts.yaml -> CTR-004 + CTR-005
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from zephyr.governance.trading_contracts.broker_interface import BrokerInterface
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

_logger = logging.getLogger(__name__)


class OrderAction(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    SUBMIT = "submit"
    CANCEL = "cancel"
    MODIFY = "modify"


class OrderManager:
    """订单管理器——订单生命周期状态机驱动"""

    VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
        OrderStatus.PENDING: {OrderStatus.SUBMITTED, OrderStatus.CANCELLED},
        OrderStatus.SUBMITTED: {OrderStatus.PARTIAL, OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
        OrderStatus.PARTIAL: {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
        OrderStatus.FILLED: set(),
        OrderStatus.CANCELLED: set(),
        OrderStatus.REJECTED: set(),
    }

    def __init__(self, brokers: dict[str, BrokerInterface] | None = None):
        self._brokers = brokers or {}
        self._orders: dict[str, Order] = {}
        self._fills: dict[str, list[Fill]] = defaultdict(list)
        self._fill_callbacks: list[Callable[[Fill], None]] = []
        self._order_callbacks: list[Callable[[Order], None]] = []
        self._pending_orders: list[Order] = []

    def register_broker(self, broker_id: str, broker: BrokerInterface) -> None:
        self._brokers[broker_id] = broker
        broker.register_fill_callback(self._on_fill)
        _logger.info("Broker registered: broker_id=%s", broker_id)

    def register_fill_callback(self, callback: Callable[[Fill], None]) -> None:
        self._fill_callbacks.append(callback)

    def create_order(
        self,
        symbol: str,
        strategy_id: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        limit_price: Decimal | None = None,
        broker_id: str = "simulation",
    ) -> Order:
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            symbol=symbol,
            strategy_id=strategy_id,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
            broker_order_id=None,
            idempotency_key=str(uuid.uuid4()),
        )
        self._orders[order_id] = order
        self._pending_orders.append(order)
        _logger.info("Order created: order_id=%s symbol=%s side=%s qty=%s", order_id, symbol, side, quantity)
        return order

    def _transition_status(self, order: Order, new_status: OrderStatus) -> None:
        """状态机校验并转换订单状态

        基于 VALID_TRANSITIONS 校验状态转换合法性，违规抛 ValueError。

        Args:
            order: 订单对象
            new_status: 目标状态

        Raises:
            ValueError: 非法状态转换
        """
        allowed = self.VALID_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"非法状态转换: {order.status} -> {new_status} (order_id={order.order_id})"
            )
        order.status = new_status
        order.updated_at = datetime.now(UTC)

    def submit_order(self, order_id: str, broker_id: str = "simulation") -> str:
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        broker = self._brokers.get(broker_id)
        if not broker:
            raise ValueError(f"Broker not found: {broker_id}")

        self._transition_status(order, OrderStatus.SUBMITTED)

        broker_order_id = broker.submit_order(order)
        order.broker_order_id = broker_order_id
        order.updated_at = datetime.now(UTC)

        return broker_order_id

    def cancel_order(self, order_id: str) -> bool:
        """撤单——同时通知券商端撤销

        P0-1 修复: 必须调用 broker.cancel_order 通知券商端，
        否则本地显示已撤但券商端订单仍挂单，导致资金损失风险。

        Args:
            order_id: 订单ID

        Returns:
            True = 撤单成功（本地+券商端均成功）
        """
        order = self._orders.get(order_id)
        if not order:
            return False

        # 状态机校验
        if order.status not in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}:
            return False

        # 通知券商端撤单（若有 broker_order_id）
        if order.broker_order_id:
            broker = self._brokers.get("simulation")  # 默认 simulation broker
            # 查找该 order 所属的 broker（通过 broker_order_id 反查）
            for bid, b in self._brokers.items():
                try:
                    if b.query_order(order.broker_order_id) is not None:
                        broker = b
                        break
                except Exception:
                    continue
            if broker is not None:
                try:
                    broker.cancel_order(order.broker_order_id)
                except Exception as e:
                    _logger.error(
                        "券商端撤单失败: order_id=%s broker_order_id=%s error=%s",
                        order_id, order.broker_order_id, e,
                        exc_info=True,
                    )
                    return False

        self._transition_status(order, OrderStatus.CANCELLED)
        _logger.info("Order cancelled: order_id=%s", order_id)
        return True

    def get_order(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def get_orders_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]

    def get_open_orders(self) -> list[Order]:
        return [
            o
            for o in self._orders.values()
            if o.status in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}
        ]

    def get_fills_for_order(self, order_id: str) -> list[Fill]:
        return self._fills.get(order_id, [])

    def get_all_fills(self) -> list[Fill]:
        return [f for fills in self._fills.values() for f in fills]

    def _on_fill(self, fill: Fill) -> None:
        self._fills[fill.order_id].append(fill)

        order = self._orders.get(fill.order_id)
        if order:
            order.filled_quantity = (order.filled_quantity or Decimal("0")) + fill.filled_quantity
            order.avg_fill_price = (
                (
                    (order.avg_fill_price or Decimal("0")) * (order.filled_quantity - fill.filled_quantity)
                    + fill.fill_price * fill.filled_quantity
                )
                / order.filled_quantity
                if order.filled_quantity > 0
                else fill.fill_price
            )
            order.updated_at = datetime.now(UTC)

            if order.filled_quantity >= order.quantity:
                try:
                    self._transition_status(order, OrderStatus.FILLED)
                except ValueError as e:
                    _logger.warning("成交回调状态转换跳过: %s", e)
            elif order.filled_quantity > 0:
                try:
                    self._transition_status(order, OrderStatus.PARTIAL)
                except ValueError as e:
                    _logger.warning("成交回调状态转换跳过: %s", e)

        for callback in self._fill_callbacks:
            try:
                callback(fill)
            except Exception as e:
                _logger.error("Fill callback error: %s", e, exc_info=True)

    @property
    def order_count(self) -> int:
        return len(self._orders)

    @property
    def fill_count(self) -> int:
        return sum(len(fills) for fills in self._fills.values())


__all__ = ["OrderAction", "OrderManager"]
