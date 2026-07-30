# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.trading_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.trading.trading_contracts.broker_interface; zephyr.governance.strategies.strategy_base; zephyr.governance.adapters.risk_validation_bridge; zephyr.shared.contracts.order; zephyr.shared.contracts.position; zephyr.shared.contracts.risk_limits; zephyr.shared.contracts.fill
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 只编排不重造——复用 OrderManager/BrokerInterface/StrategyBase/RiskValidationPort；权重驱动非订单驱动
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_trading_session.py
# [TTL] permanent
"""D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器

连接 行情→策略→风控→下单→持仓跟踪 的实时编排器，使盘中模拟盘可运行。
设计原则：
  1. 只编排不重造——复用 OrderManager / BrokerInterface / risk_validator / StrategyBase
  2. 权重驱动——策略返回 dict[str, float] 目标权重，TradingSession 计算 delta 生成订单
  3. broker 注入——切换 broker（SimulationBroker/MiniQmtBroker）即可在回测/模拟/实盘间切换
  4. 可手动可自动——rebalance() 可手动调用，也可由内置定时器自动触发

三态一致性：同一 TradingSession 切换 SimulationBroker / MiniQmtBroker，调仓逻辑一致。
"""

from __future__ import annotations

import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationPort,
    RiskViolation,
)
from zephyr.governance.strategies.strategy_base import StrategyBase
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_logger = logging.getLogger(__name__)

SignalProvider = Callable[[list[str]], dict[str, float]]
PriceProvider = Callable[[list[str]], dict[str, Decimal]]

# 需要撤单的活跃状态
_ACTIVE_STATUSES = frozenset({OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL})


def _default_risk_limits() -> RiskLimits:
    """构建默认 RiskLimits（A 股多头：单标的 10%、杠杆 1.0）。"""
    now = datetime.now(timezone.utc)
    return RiskLimits(
        as_of_date=now,
        idempotency_key=f"session-default-{now.isoformat()}",
        max_single_position=0.10,
        max_gross_leverage=1.0,
    )


def _default_constraints() -> dict[str, Any]:
    return {"top_n": 10, "max_single": 0.10}


@dataclass
class TradingSessionConfig:
    """TradingSession 配置。

    Attributes:
        universe: 标的池，如 ["600000.SH", "000001.SZ", ...]
        broker_id: OrderManager 中注册的 broker_id
        strategy_id: 策略标识（写入 Order.strategy_id）
        rebalance_interval_seconds: 自动调仓间隔秒数（0=仅手动）
        strategy_constraints: 传给 strategy.generate_target_weights 的约束
        min_order_qty: 最小下单股数（A 股 100）
        round_lot: 整手数（A 股 100）
        risk_limits: 风控限额
    """

    universe: list[str]
    broker_id: str = "miniqmt"
    strategy_id: str = "trading_session"
    rebalance_interval_seconds: int = 0
    strategy_constraints: dict[str, Any] = field(default_factory=_default_constraints)
    min_order_qty: int = 100
    round_lot: int = 100
    risk_limits: RiskLimits = field(default_factory=_default_risk_limits)


class TradingSession:
    """盘中实时调仓编排器。

    一次 rebalance() 循环：
        signal_provider(universe) → signals
        → strategy.generate_target_weights(universe, signals, constraints) → target_weights
        → broker.get_positions() → current PositionSnapshot
        → price_provider(universe) → current_prices
        → _compute_order_deltas(target_weights, positions, prices) → orders
        → 逐单 risk_validator.validate_order() → 阻断 HALT 违规
        → 逐单 order_manager.create_order() + submit_order()
        → 返回已提交订单列表
    """

    def __init__(
        self,
        broker: BrokerInterface,
        strategy: StrategyBase,
        risk_validator: RiskValidationPort,
        signal_provider: SignalProvider,
        price_provider: PriceProvider,
        order_manager: OrderManager,
        config: TradingSessionConfig,
    ) -> None:
        self._broker = broker
        self._strategy = strategy
        self._risk_validator = risk_validator
        self._signal_provider = signal_provider
        self._price_provider = price_provider
        self._order_manager = order_manager
        self._config = config
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._running = False
        self._fills: list[Fill] = []
        self._submitted_orders: list[Order] = []
        self._blocked_orders: list[Order] = []

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def start(self) -> None:
        """连接 broker + 注册 fill 回调 + 启动定时器（如果 interval > 0）。"""
        if self._running:
            _logger.warning("TradingSession already running")
            return
        self._broker.connect()
        self._broker.register_fill_callback(self._on_fill)
        self._running = True
        _logger.info(
            "TradingSession started: broker=%s universe=%d interval=%ds",
            self._config.broker_id,
            len(self._config.universe),
            self._config.rebalance_interval_seconds,
        )
        self._schedule_next()

    def stop(self) -> None:
        """撤所有未成交单 + 停定时器 + 断开 broker。"""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self._cancel_pending_orders()
        self._broker.disconnect()
        _logger.info("TradingSession stopped: %s", self.get_session_report())

    # ------------------------------------------------------------------
    # 核心调仓
    # ------------------------------------------------------------------

    def rebalance(self) -> list[Order]:
        """执行一次完整调仓循环，返回已提交订单列表。"""
        with self._lock:
            return self._do_rebalance()

    def _do_rebalance(self) -> list[Order]:
        """实际调仓逻辑（调用方已持锁）。"""
        signals = self._signal_provider(self._config.universe)
        target_weights = self._strategy.generate_target_weights(
            self._config.universe,
            signals,
            self._config.strategy_constraints,
        )
        positions = self._broker.get_positions()
        prices = self._price_provider(self._config.universe)
        deltas = self._compute_order_deltas(target_weights, positions, prices)
        submitted = self._validate_and_submit(deltas, target_weights, positions)
        _logger.info(
            "rebalance: signals=%d weights=%d deltas=%d submitted=%d blocked=%d",
            len(signals),
            len(target_weights),
            len(deltas),
            len(submitted),
            len(deltas) - len(submitted),
        )
        return submitted

    def _compute_order_deltas(
        self,
        target_weights: dict[str, float],
        positions: PositionSnapshot,
        prices: dict[str, Decimal],
    ) -> list[Order]:
        """目标权重 → 订单 delta 列表（未注册到 OrderManager 的值对象）。

        - total_asset = cash + total_market_value
        - target_qty = (total_asset * weight / price) 向下取整到 round_lot
        - delta_qty = target_qty - current_qty，忽略 < min_order_qty 的微调
        - 持仓中但不在 target_weights 的标的 → 全部卖出
        """
        total_asset = positions.cash + positions.total_market_value
        if total_asset <= 0:
            _logger.warning("total_asset <= 0, skip rebalance: %s", total_asset)
            return []

        orders: list[Order] = []
        for symbol, weight in target_weights.items():
            order = self._make_delta_order(symbol, weight, total_asset, positions, prices)
            if order:
                orders.append(order)

        # 持仓中但不在目标权重 → 清仓卖出
        for symbol, qty in positions.holdings.items():
            if qty > 0 and symbol not in target_weights:
                order = self._make_sell_all_order(symbol, qty, prices)
                if order:
                    orders.append(order)
        return orders

    def _make_delta_order(
        self,
        symbol: str,
        weight: float,
        total_asset: Decimal,
        positions: PositionSnapshot,
        prices: dict[str, Decimal],
    ) -> Order | None:
        """单个标的的目标权重 → 买入/卖出 delta 订单。"""
        price = prices.get(symbol)
        if not price or price <= 0:
            _logger.debug("skip %s: no valid price", symbol)
            return None
        target_qty = self._calc_target_qty(total_asset, weight, price)
        current_qty = positions.holdings.get(symbol, Decimal("0"))
        delta = target_qty - current_qty
        return self._build_order_if_significant(symbol, delta, price)

    def _make_sell_all_order(
        self,
        symbol: str,
        qty: Decimal,
        prices: dict[str, Decimal],
    ) -> Order | None:
        """清仓卖出订单（标的不在目标权重中）。"""
        price = prices.get(symbol)
        if not price or price <= 0:
            _logger.debug("skip sell-all %s: no valid price", symbol)
            return None
        return self._build_order_if_significant(symbol, -qty, price)

    def _calc_target_qty(self, total_asset: Decimal, weight: float, price: Decimal) -> Decimal:
        """目标权重 → 目标持仓数量（向下取整到 round_lot）。"""
        raw_qty = (total_asset * Decimal(str(weight))) / price
        lots = raw_qty // self._config.round_lot
        return lots * self._config.round_lot

    def _build_order_if_significant(
        self,
        symbol: str,
        delta: Decimal,
        price: Decimal,
    ) -> Order | None:
        """delta 显著（>= min_order_qty）则构建 Order 值对象，否则返回 None。"""
        if abs(delta) < self._config.min_order_qty:
            return None
        side = OrderSide.BUY if delta > 0 else OrderSide.SELL
        return Order(
            order_id=f"ts-{symbol}-{uuid.uuid4().hex[:8]}",
            idempotency_key=f"ts-{symbol}-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            strategy_id=self._config.strategy_id,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=abs(delta),
            limit_price=price,
            created_at=datetime.now(timezone.utc),
        )

    def _validate_and_submit(
        self,
        deltas: list[Order],
        target_weights: dict[str, float],
        positions: PositionSnapshot,
    ) -> list[Order]:
        """逐单风控验证 + 创建并提交订单。返回已提交订单列表。"""
        current_holdings_float = {
            s: float(q) for s, q in positions.holdings.items()
        }
        submitted: list[Order] = []
        for order in deltas:
            target_weight = float(target_weights.get(order.symbol, 0.0))
            if self._is_blocked_by_risk(order.symbol, target_weight, current_holdings_float):
                self._blocked_orders.append(order)
                continue
            registered = self._order_manager.create_order(
                symbol=order.symbol,
                strategy_id=self._config.strategy_id,
                side=order.side,
                order_type=order.order_type,
                quantity=order.quantity,
                limit_price=order.limit_price,
                broker_id=self._config.broker_id,
            )
            self._order_manager.submit_order(registered.order_id, self._config.broker_id)
            self._submitted_orders.append(registered)
            submitted.append(registered)
        return submitted

    def _is_blocked_by_risk(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
    ) -> bool:
        """风控验证：存在 HALT 级违规则返回 True（阻断）。"""
        violations: list[RiskViolation] = self._risk_validator.validate_order(
            symbol=symbol,
            target_weight=target_weight,
            current_holdings=current_holdings,
            limits=self._config.risk_limits,
        )
        halt = any(v.severity == "HALT" for v in violations)
        if halt:
            _logger.warning(
                "order blocked by risk HALT: symbol=%s violations=%s",
                symbol,
                [(v.constraint, v.description) for v in violations],
            )
        return halt

    # ------------------------------------------------------------------
    # 成交回调 + 报告
    # ------------------------------------------------------------------

    def _on_fill(self, fill: Fill) -> None:
        """成交回调——记录成交 + 日志。"""
        self._fills.append(fill)
        _logger.info(
            "fill: symbol=%s qty=%s price=%s order=%s",
            fill.symbol,
            fill.filled_quantity,
            fill.fill_price,
            fill.order_id,
        )

    def get_session_report(self) -> dict[str, Any]:
        """返回会话统计：已提交/已阻断/已成交数 + 运行状态。"""
        return {
            "running": self._running,
            "submitted_count": len(self._submitted_orders),
            "blocked_count": len(self._blocked_orders),
            "fill_count": len(self._fills),
            "broker_id": self._config.broker_id,
            "universe_size": len(self._config.universe),
        }

    # ------------------------------------------------------------------
    # 定时器
    # ------------------------------------------------------------------

    def _schedule_next(self) -> None:
        """调度下一次自动调仓（interval > 0 时）。"""
        if not self._running or self._config.rebalance_interval_seconds <= 0:
            return
        self._timer = threading.Timer(
            self._config.rebalance_interval_seconds,
            self._scheduled_rebalance,
        )
        self._timer.daemon = True
        self._timer.start()

    def _scheduled_rebalance(self) -> None:
        """定时器回调——执行调仓后重新调度。"""
        if not self._running:
            return
        try:
            with self._lock:
                self._do_rebalance()
        except Exception:
            _logger.exception("scheduled rebalance failed")
        self._schedule_next()

    def _cancel_pending_orders(self) -> None:
        """撤销所有活跃订单。"""
        for order in self._submitted_orders:
            if order.status in _ACTIVE_STATUSES:
                try:
                    self._order_manager.cancel_order(order.order_id)
                except Exception:
                    _logger.exception("failed to cancel order %s", order.order_id)


__all__ = ["TradingSession", "TradingSessionConfig", "SignalProvider", "PriceProvider"]
