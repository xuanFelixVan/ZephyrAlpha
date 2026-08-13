# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.trading_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.ex_core.cancel_rate_guard; zephyr.trading.trading_contracts.broker_interface; zephyr.governance.strategies.strategy_base; zephyr.governance.adapters.risk_validation_bridge; zephyr.shared.contracts.order; zephyr.shared.contracts.position; zephyr.shared.contracts.risk_limits; zephyr.shared.contracts.fill
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只编排不重造——复用 OrderManager/BrokerInterface/StrategyBase/RiskValidationPort/CancelRateGuard；权重驱动非订单驱动；资金预占串行扣减+拒单回滚
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_trading_session.py
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: target_weights(策略目标权重) + positions(持仓快照cash/holdings/total_market_value) + prices(当前价格)
# I2: risk_limits(风控限额) + config(熔断阈值/资金费率) + CancelRateGuard(撤单率状态)
# F1: _compute_order_deltas(差额下单: 目标qty-当前qty, 先卖后买排序, 板块整手取整)
# F2: _is_blocked_by_circuit_breaker(订单层熔断: 单票单笔≤4%/单票≤10笔日/全账户≤50笔日)
# A1: _validate_and_submit(资金预占: 串行扣减available_cash+卖出预占释放+提交前拦截+拒单回滚)
# A2: CancelRateGuard(can_place_order冻结拦截+can_submit_now限频+record_submit计数)
# A3: _handle_rejection(拒单分类: 涨跌停/资金/持仓不重试, 价格/连接重试1次)
# O1: submitted_orders(已提交订单) + blocked_orders(已拦截订单) + session_report(统计)
# [/ALGO_FLOW]
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
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_manager import OrderManager, RejectionAction
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
    # 订单层熔断（40_execution_broker §2.8）
    max_single_order_pct: Decimal = Decimal("0.04")  # 单票单笔≤4%账户市值
    max_symbol_orders_per_day: int = 10  # 单票≤10笔/日
    max_total_orders_per_day: int = 50  # 全账户≤50笔/日
    # 资金预占（40_execution_broker §2.14 决策⑬）
    estimated_cost_rate: Decimal = Decimal("0.003")  # 千三含佣金+印花+过户+滑点（偏保守多预留）


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
        cancel_rate_guard: CancelRateGuard | None = None,
    ) -> None:
        self._broker = broker
        self._strategy = strategy
        self._risk_validator = risk_validator
        self._signal_provider = signal_provider
        self._price_provider = price_provider
        self._order_manager = order_manager
        self._config = config
        self._cancel_rate_guard = cancel_rate_guard or CancelRateGuard()
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._running = False
        self._fills: list[Fill] = []
        self._submitted_orders: list[Order] = []
        self._blocked_orders: list[Order] = []
        # 订单层熔断当日计数（40_execution_broker §2.8）
        self._symbol_order_counts: dict[str, int] = defaultdict(int)
        self._total_order_count_today: int = 0

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
        """逐单风控验证 + 资金预占 + 创建并提交订单。返回已提交订单列表。

        执行顺序（40_execution_broker §2.1 架构总览）：
          盘前检查链（风控）→ 资金预占预校验 → 订单层熔断 → 提交 broker。
        先卖后买——卖出释放 T+0 资金再买入，避免资金不足（error_code=54）。
        A 股 T+0 资金：当日卖出回笼资金可立即用于当日买入（§2.6 决策⑤）。
        资金预占（§2.14 决策⑬）：串行扣减 available_cash，提交前本地拦截，
        拒单时回滚预占额度。
        """
        # 先卖后买：SELL 排前释放资金，BUY 排后利用释放资金
        # （Python sorted 稳定，保持同侧内相对顺序不变）
        sorted_deltas = sorted(deltas, key=lambda o: 0 if o.side is OrderSide.SELL else 1)
        current_holdings_float = {s: float(q) for s, q in positions.holdings.items()}
        submitted: list[Order] = []

        # ── 资金预占初始化（§2.14 决策⑬）──
        available_cash = positions.cash
        pending_release = Decimal("0")  # 待成交卖出单的预估净回笼资金
        cost_rate = self._config.estimated_cost_rate

        for order in sorted_deltas:
            # ── 盘前检查链 Step 1-3: 风控检查（仓位/行业/杠杆/Kill Switch）──
            target_weight = float(target_weights.get(order.symbol, 0.0))
            if self._is_blocked_by_risk(order.symbol, target_weight, current_holdings_float):
                self._blocked_orders.append(order)
                continue

            # ── 盘前检查链 Step 4: 撤单率冻结检查（§2.13 决策⑫）──
            if not self._cancel_rate_guard.can_place_order():
                _logger.error(
                    "CancelRateGuard FROZEN: 拒单 symbol=%s cancel_rate=%.2f%%",
                    order.symbol,
                    self._cancel_rate_guard.cancel_rate * 100,
                )
                self._blocked_orders.append(order)
                continue

            # ── 资金预占预校验（§2.14 决策⑬）──
            if order.side is OrderSide.SELL:
                # 卖出：预占=0，预估回笼累加到 pending_release（T+0 资金可立即用于买入）
                estimated_release = order.quantity * (order.limit_price or Decimal("0")) * (1 - cost_rate)
                pending_release += estimated_release
            else:
                # 买入：预估占用 = 数量 × 价格 × (1 + 费率)
                estimated_cost = order.quantity * (order.limit_price or Decimal("0")) * (1 + cost_rate)
                if estimated_cost > available_cash + pending_release:
                    _logger.warning(
                        "资金预占拦截: symbol=%s 预估占用=%s > 可用现金=%s + 待回笼=%s",
                        order.symbol,
                        estimated_cost,
                        available_cash,
                        pending_release,
                    )
                    self._blocked_orders.append(order)
                    continue
                # 串行扣减可用资金
                available_cash -= estimated_cost

            # ── 订单层熔断（§2.8.3）──
            if self._is_blocked_by_circuit_breaker(order, positions):
                # 熔断拦截：回滚资金预占
                if order.side is OrderSide.SELL:
                    pending_release -= order.quantity * (order.limit_price or Decimal("0")) * (1 - cost_rate)
                else:
                    available_cash += order.quantity * (order.limit_price or Decimal("0")) * (1 + cost_rate)
                self._blocked_orders.append(order)
                continue

            # ── 提交订单 ──
            try:
                # 限频检查（§2.13 决策⑫）
                if not self._cancel_rate_guard.can_submit_now():
                    _logger.warning(
                        "CancelRateGuard 限频: symbol=%s 15笔/秒已满，稍后重试",
                        order.symbol,
                    )
                    # 回滚资金预占
                    if order.side is OrderSide.SELL:
                        pending_release -= order.quantity * (order.limit_price or Decimal("0")) * (1 - cost_rate)
                    else:
                        available_cash += order.quantity * (order.limit_price or Decimal("0")) * (1 + cost_rate)
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
                self._cancel_rate_guard.record_submit()
                self._submitted_orders.append(registered)
                submitted.append(registered)
            except Exception as exc:  # noqa: BLE001 — 拒单分类处理，不阻断后续订单
                # 拒单回滚资金预占（§2.14 决策⑬）
                if order.side is OrderSide.SELL:
                    pending_release -= order.quantity * (order.limit_price or Decimal("0")) * (1 - cost_rate)
                else:
                    available_cash += order.quantity * (order.limit_price or Decimal("0")) * (1 + cost_rate)
                self._handle_rejection(order, exc)
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

    def _handle_rejection(self, order: Order, error: Exception) -> None:
        """拒单分类处理（40_execution_broker §2.7 层3）。

        根据 error_code 分类：涨跌停/资金/持仓不重试，价格/连接重试1次。
        MVP 阶段仅记录日志 + 归入 blocked_orders；重试/冻结/对账由上层 Saga 处理。
        """
        raw_code = getattr(error, "error_code", None)
        action = (
            self._order_manager.classify_rejection(raw_code) if isinstance(raw_code, int) else RejectionAction.ABANDON
        )
        self._blocked_orders.append(order)
        if action is RejectionAction.ALERT_FREEZE:
            _logger.error(
                "拒单[资金不足] 冻结策略新开仓: symbol=%s error=%s",
                order.symbol,
                error,
            )
        elif action is RejectionAction.ALERT_RECONCILE:
            _logger.error(
                "拒单[持仓不足] 触发持仓对账: symbol=%s error=%s",
                order.symbol,
                error,
            )
        elif action is RejectionAction.ABANDON:
            _logger.warning(
                "拒单[放弃] symbol=%s error_code=%s error=%s",
                order.symbol,
                raw_code,
                error,
            )
        else:
            # RETRY_ONCE / IDEMPOTENT_RETURN：MVP 仅记录，上层 Saga 处理重试
            _logger.info(
                "拒单[%s] 待上层处理: symbol=%s error=%s",
                action,
                order.symbol,
                error,
            )

    def _is_blocked_by_circuit_breaker(
        self,
        order: Order,
        positions: PositionSnapshot,
    ) -> bool:
        """订单层熔断检查（40_execution_broker §2.8）。

        三项检查：单票单笔≤4%市值 / 单票≤10笔日 / 全账户≤50笔日。
        通过则计数+1返回 False；触发则返回 True（调用方归入 blocked_orders）。
        """
        cfg = self._config
        total_asset = positions.cash + positions.total_market_value

        # 1. 单票单笔量 ≤4% 账户市值
        order_value = order.quantity * (order.limit_price or Decimal("0"))
        if total_asset > 0 and order_value / total_asset > cfg.max_single_order_pct:
            _logger.warning(
                "订单层熔断[单笔超限]: symbol=%s order_value=%s pct=%.4f > %.4f",
                order.symbol,
                order_value,
                float(order_value / total_asset),
                float(cfg.max_single_order_pct),
            )
            return True

        # 2. 单票下单频次 ≤10 笔/日
        if self._symbol_order_counts[order.symbol] >= cfg.max_symbol_orders_per_day:
            _logger.warning(
                "订单层熔断[单票频次]: symbol=%s count=%d >= %d",
                order.symbol,
                self._symbol_order_counts[order.symbol],
                cfg.max_symbol_orders_per_day,
            )
            return True

        # 3. 全账户下单频次 ≤50 笔/日
        if self._total_order_count_today >= cfg.max_total_orders_per_day:
            _logger.warning(
                "订单层熔断[全账户频次]: count=%d >= %d",
                self._total_order_count_today,
                cfg.max_total_orders_per_day,
            )
            return True

        # 通过熔断，计数+1（含拒单尝试，防疯狂重试推高撤单率）
        self._symbol_order_counts[order.symbol] += 1
        self._total_order_count_today += 1
        return False

    def reset_daily_circuit_breaker(self) -> None:
        """重置当日熔断计数（每个交易日开始调用）。"""
        self._symbol_order_counts.clear()
        self._total_order_count_today = 0

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
