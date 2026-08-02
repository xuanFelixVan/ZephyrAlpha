# [BLUEPRINT] MOD-EX-002 | docs/03_modules/_domain_execution_core/position_tracker/blueprint.md
# [MODULE] zephyr.ex_core.position_tracker.tracker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.position; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] zephyr.governance.adapters.simulation_broker; zephyr.ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额计算; PositionSnapshot frozen不可变; apply_fill需显式side(Fill契约无side字段)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_position_tracker.py
# [TTL] permanent
"""D_EXECUTION_CORE — Position Tracker (持仓跟踪器)

从 SimulationBroker 拆出的独立持仓跟踪模块。每笔成交（Fill）驱动持仓更新，
任何时刻可产出 PositionSnapshot（CTR-006）供 D-RISK/D-PORTFOLIO/D-REPORTING 消费。

设计真源: D:/临时工作区/依赖图/08-D-EX-CORE-执行核心域.md §1 D-EX-CORE-04
蓝图: docs/03_modules/_domain_execution_core/position_tracker/blueprint.md

核心职责（阶段1）:
  - 维护 symbol → (quantity, avg_cost) 持仓状态
  - 维护 cash 余额（买入扣、卖出加）
  - 从 Fill 回调更新持仓（平均成本法）
  - 产出 PositionSnapshot (CTR-006)

阶段2扩展（本次不实现，见蓝图 §4）:
  - SQLite 持久化 / Redis 实时更新 / T+1 锁定 / FIFO-LIFO / unrealized_pnl
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from threading import Lock

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot

_logger = logging.getLogger(__name__)


class PositionTracker:
    """持仓跟踪器 — Fill 回调驱动，产出 PositionSnapshot (CTR-006)。

    从 SimulationBroker 拆出，为回测/模拟/实盘三态提供统一的持仓跟踪逻辑。

    Usage:
        tracker = PositionTracker(initial_cash=Decimal("1000000"))

        # 应用成交（需显式传入 side，因 Fill 契约无 side 字段）
        tracker.apply_fill(fill, OrderSide.BUY)

        # 产出持仓快照
        snapshot = tracker.get_positions()
        # snapshot.holdings, snapshot.cash, snapshot.total_market_value ...

    Thread Safety:
        内部加 threading.Lock 保护持仓状态。可在多线程环境安全调用
        apply_fill / get_positions（如 TradingSession 定时调仓 + fill 回调并发）。
    """

    def __init__(
        self,
        initial_cash: Decimal = Decimal("1000000"),
        portfolio_id: str = "position_tracker",
    ) -> None:
        self._initial_cash = initial_cash
        self._cash = initial_cash
        self._portfolio_id = portfolio_id
        self._holdings: dict[str, Decimal] = {}
        self._avg_costs: dict[str, Decimal] = {}
        self._lock = Lock()

    # ── Stage 4 公共化（只读 properties）──

    @property
    def cash(self) -> Decimal:
        """只读：当前现金余额。"""
        return self._cash

    @property
    def holdings(self) -> dict[str, Decimal]:
        """只读：持仓数量快照（返回副本，调用方修改不影响内部状态）。"""
        with self._lock:
            return dict(self._holdings)

    @property
    def avg_costs(self) -> dict[str, Decimal]:
        """只读：平均成本快照（返回副本）。"""
        with self._lock:
            return dict(self._avg_costs)

    # ── 核心方法 ──

    def apply_fill(self, fill: Fill, side: OrderSide) -> None:
        """应用成交——更新持仓数量、平均成本、现金。

        Args:
            fill: 成交回报（CTR-005，不可变）。使用 fill_price/filled_quantity/commission。
            side: 买卖方向（Fill 契约无 side 字段，需调用方从 Order 传入）。

        Note:
            阶段1不做幂等去重（同一 fill_id 重复调用会重复更新）。
            幂等性由调用方保证（SimulationBroker 的 _simulate_fill 天然一次性）。
            阶段2将增加 fill_id 去重（见蓝图 §4）。
        """
        with self._lock:
            symbol = fill.symbol
            fill_qty = fill.filled_quantity
            fill_price = fill.fill_price
            commission = fill.commission

            current_qty = self._holdings.get(symbol, Decimal("0"))
            current_avg = self._avg_costs.get(symbol, Decimal("0"))

            if side == OrderSide.BUY:
                new_qty = current_qty + fill_qty
                if new_qty != 0:
                    total_cost = (current_avg * current_qty) + (fill_price * fill_qty)
                    self._avg_costs[symbol] = total_cost / new_qty
                self._holdings[symbol] = new_qty
                self._cash -= fill_qty * fill_price + commission
            else:
                # SELL
                new_qty = current_qty - fill_qty
                # 卖出：avg_cost 不变（成本已锁定），盈亏在现金端实现
                if new_qty == 0:
                    self._avg_costs[symbol] = Decimal("0")
                # new_qty < 0（空头）时保留原 avg_cost
                self._holdings[symbol] = new_qty
                self._cash += fill_qty * fill_price - commission

            _logger.debug(
                "apply_fill: symbol=%s side=%s qty=%s price=%s cash=%s holding=%s",
                symbol,
                side,
                fill_qty,
                fill_price,
                self._cash,
                self._holdings[symbol],
            )

    def get_positions(self) -> PositionSnapshot:
        """产出持仓快照（CTR-006），不可变 frozen dataclass。

        market_value 计算：阶段1用 qty × avg_cost（与 SimulationBroker 一致）。
        阶段2将改为 qty × 实时价（需 PriceProvider 注入）。
        """
        with self._lock:
            market_values: dict[str, Decimal] = {}
            for symbol, qty in self._holdings.items():
                avg_price = self._avg_costs.get(symbol, Decimal("0"))
                market_values[symbol] = qty * avg_price if avg_price > 0 else Decimal("0")

            total_mv = sum(market_values.values(), Decimal("0"))
            # 过滤零持仓（qty=0 的标的不出现在 holdings 中）
            active_holdings = {s: q for s, q in self._holdings.items() if q != 0}
            active_mv = {s: mv for s, mv in market_values.items() if self._holdings.get(s, Decimal("0")) != 0}

            return PositionSnapshot(
                as_of_timestamp=datetime.now(UTC),
                portfolio_id=self._portfolio_id,
                idempotency_key=str(uuid.uuid4()),
                cash=self._cash,
                gross_leverage=float(total_mv / self._initial_cash) if self._initial_cash > 0 else 0.0,
                holdings=active_holdings,
                market_values=active_mv,
                total_market_value=total_mv,
            )

    def reset(self) -> None:
        """重置到初始状态（测试用）。"""
        with self._lock:
            self._cash = self._initial_cash
            self._holdings.clear()
            self._avg_costs.clear()


__all__ = ["PositionTracker"]
