# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.governance.adapters.simulation_broker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order; zephyr.trading.trading_contracts.execution.position
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
# [A_module] module_id=MOD-EXE_simulation_broker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

# ---
# domain: ex_core
# category: broker_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — Simulation Broker Adapter

模拟券商适配器。实现 BrokerInterface (OCP-003)，用于回测和模拟交易。

核心职责：
  - 模拟订单提交/撤销/查询
  - 模拟成交生成（含滑点/佣金）
  - 模拟持仓查询
  - 成交回调通知

CTR 契约：
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE
  生产者 — CTR-005 (Fill) -> D_REPORTING
  生产者 — CTR-006 (PositionSnapshot) -> D_RISK, D_REPORTING, D_ML_TRAIN
  生产者 — CTR-ERR-005 (ExecutionRejectionError) -> D_PORTFOLIO_CORE, D_REPORTING

SSoT: cross_layer_contracts.yaml -> OCP-003 + CTR-004 + CTR-005 + CTR-006
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal

from zephyr.trading.trading_contracts.broker_interface import BrokerInterface
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot

_logger = logging.getLogger(__name__)

FillCallback = Callable[[Fill], None]


class SimulationBroker(BrokerInterface):
    """模拟券商——实现 BrokerInterface，用于回测和模拟交易"""

    broker_id: str = "simulation"

    def __init__(
        self,
        initial_cash: Decimal = Decimal("1000000"),
        commission_rate: Decimal = Decimal("0.0003"),
        slippage_bps: Decimal = Decimal("1"),
        fill_latency_ms: int = 10,
    ):
        self._connected = False
        self._initial_cash = initial_cash
        self._cash = initial_cash
        self._commission_rate = commission_rate
        self._slippage_bps = slippage_bps
        self._fill_latency_ms = fill_latency_ms
        self._orders: dict[str, Order] = {}
        self._fills: dict[str, Fill] = {}
        self._positions: dict[str, Decimal] = defaultdict(Decimal)
        self._avg_cost: dict[str, Decimal] = {}
        self._fill_callbacks: list[FillCallback] = []
        self._order_id_counter = 0

    def connect(self) -> bool:
        self._connected = True
        _logger.info("SimulationBroker connected. initial_cash=%s", self._initial_cash)
        return True

    def disconnect(self) -> None:
        self._connected = False
        _logger.info("SimulationBroker disconnected. final_cash=%s", self._cash)

    def submit_order(self, order: Order) -> str:
        if not self._connected:
            raise ConnectionError("SimulationBroker not connected")

        broker_order_id = f"sim-{self._order_id_counter}"
        self._order_id_counter += 1
        self._orders[broker_order_id] = order
        _logger.info(
            "Order submitted: broker_order_id=%s order_id=%s symbol=%s side=%s qty=%s",
            broker_order_id,
            order.order_id,
            order.symbol,
            order.side,
            order.quantity,
        )

        self._simulate_fill(order, broker_order_id)

        return broker_order_id

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            _logger.info("Order cancelled: order_id=%s", order_id)
            return True
        _logger.warning("Order not found for cancel: order_id=%s", order_id)
        return False

    def query_order(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def get_positions(self) -> PositionSnapshot:
        market_values: dict[str, Decimal] = {}
        for symbol, qty in self._positions.items():
            avg_price = self._avg_cost.get(symbol, Decimal("0"))
            market_values[symbol] = qty * avg_price if avg_price > 0 else Decimal("0")

        total_mv = sum(market_values.values(), Decimal("0"))

        now = datetime.now(UTC)
        return PositionSnapshot(
            as_of_timestamp=now,
            portfolio_id="simulation",
            idempotency_key=str(uuid.uuid4()),
            total_market_value=total_mv,
            cash=self._cash,
            gross_leverage=float(total_mv / self._initial_cash) if self._initial_cash > 0 else 0.0,
            holdings=dict(self._positions),
            market_values=dict(market_values),
        )

    def register_fill_callback(self, callback: FillCallback) -> None:
        self._fill_callbacks.append(callback)

    @property
    def broker_id_prop(self) -> str:
        return "simulation"

    @property
    def supports_realtime_fills(self) -> bool:
        return True

    def _simulate_fill(self, order: Order, broker_order_id: str) -> None:
        """模拟成交——创建 Fill 并更新持仓"""
        fill_price = order.limit_price if order.limit_price else Decimal("100")
        slippage = self._slippage_bps / Decimal("10000")

        if order.side and order.side.name == "BUY":
            fill_price = fill_price * (Decimal("1") + slippage)
        else:
            fill_price = fill_price * (Decimal("1") - slippage)

        commission = order.quantity * fill_price * self._commission_rate

        fill_id = str(uuid.uuid4())
        fill = Fill(
            fill_id=fill_id,
            order_id=order.order_id,
            symbol=order.symbol,
            strategy_id=order.strategy_id,
            filled_quantity=order.quantity,
            fill_price=fill_price,
            fill_timestamp=datetime.now(UTC),
            commission=commission,
            slippage=slippage,
            broker_fill_id=broker_order_id,
            idempotency_key=str(uuid.uuid4()),
        )

        self._fills[fill_id] = fill
        self._update_positions(order, fill_price, commission)

        for callback in self._fill_callbacks:
            try:
                callback(fill)
            except Exception as e:
                _logger.error("Fill callback error: %s", e, exc_info=True)

    def _update_positions(self, order: Order, fill_price: Decimal, commission: Decimal) -> None:
        symbol = order.symbol
        current_qty = self._positions[symbol]
        current_cost = self._avg_cost.get(symbol, Decimal("0"))

        if order.side and order.side.name == "BUY":
            new_qty = current_qty + order.quantity
            if new_qty != 0:
                total_cost = (current_cost * current_qty) + (fill_price * order.quantity)
                self._avg_cost[symbol] = total_cost / new_qty if new_qty != 0 else Decimal("0")
            self._positions[symbol] = new_qty
            self._cash -= order.quantity * fill_price + commission
        else:
            new_qty = current_qty - order.quantity
            if new_qty != 0:
                total_cost = current_cost * current_qty
                self._avg_cost[symbol] = total_cost / new_qty if new_qty != 0 else Decimal("0")
            else:
                self._avg_cost[symbol] = Decimal("0")
            self._positions[symbol] = new_qty
            self._cash += order.quantity * fill_price - commission

    def get_fills(self) -> dict[str, Fill]:
        return dict(self._fills)


__all__ = ["SimulationBroker"]
