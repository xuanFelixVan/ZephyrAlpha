# [BLUEPRINT] MOD-RPT-004 | docs/03_modules/_domain_reporting/realtime_pnl_dashboard/blueprint.md
# [MODULE] zephyr.reporting.realtime_pnl_dashboard
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.ex_core.position_tracker.tracker; zephyr.trading.pnl_calculator; zephyr.shared.contracts.fill; zephyr.shared.contracts.position; zephyr.shared.contracts.risk.risk_dashboard_snapshot; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.frontend
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额计算(return_pct除外); DashboardSnapshot/PositionPnlEntry frozen不可变; realized_pnl_total仅record_fill修改(refresh只读); total_pnl=realized+unrealized恒成立; 纯消费层不发布事件不改持仓
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDashboardInputError(ZA-RPT-0001)
# [TESTS] tests/reporting/test_realtime_pnl_dashboard.py
# [A_module] module_id=MOD-RPT-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_REPORTING — Real-time P&L Dashboard (实时盈亏仪表盘)

盘中实时聚合 PnL/持仓/风控状态, 产出 DashboardSnapshot 供 D-FRONTEND 渲染。
本模块只产出数据, 不渲染 UI; 3s 刷新由消费者定时调用 refresh() 实现（不内置定时器,
解耦便于测试）。

直接消费 MOD-TRADING-002 PnL 计算器(CTR-TRD-01) + MOD-EX-002 PositionTracker,
闭环价值链: 成交→持仓→PnL→仪表盘。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.2 D-REPORTING-04, §2.4 Phase 1
蓝图: docs/03_modules/_domain_reporting/realtime_pnl_dashboard/blueprint.md

核心职责（阶段1）:
  - 已实现盈亏累计: record_fill 累加 net_pnl + fees
  - 未实现盈亏实时计算: refresh(market_prices) 用当前市价重算
  - 持仓明细: 每标的 quantity/avg_cost/price/market_value/unrealized_pnl
  - 风控状态: 可选注入 RiskDashboardSnapshot, 无则降级
  - 组合总盈亏: total_pnl = realized + unrealized

属 A 类基础设施（确定性数据聚合），纯消费层不发布领域事件(D-RPT-D01)。
纯基础设施: 不决定"买什么/何时买"，只负责"实时算出当前盈亏/持仓/风控状态"。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill + 买卖方向（CTR-005 契约）
#   fields: fill(symbol/price/quantity/fees) + side(BUY/SELL) + avg_cost(可选)
#   code: record_fill() 参数（zephyr.shared.contracts.fill.Fill）
# - id: I2
#   name: 当前市价字典
#   fields: market_prices {symbol: Decimal 当前市价}
#   code: refresh() 参数 market_prices
# - id: I3
#   name: PositionTracker 持仓状态（MOD-EX-002）
#   fields: holdings 持仓数量 + avg_costs 均价 + cash 现金
#   code: zephyr.ex_core.position_tracker.tracker.PositionTracker
# - id: I4
#   name: 风控状态快照（可选）
#   fields: RiskDashboardSnapshot（不注入则降级为 None）
#   code: update_risk() 参数 risk_snapshot
# 层: 算法
# - id: A1
#   name_zh: ① 已实现盈亏累计
#   name_en: RealtimePnlDashboard.record_fill
#   intro: 每笔成交算已实现盈亏：买入只计费用，卖出按价差乘数量计净盈亏并累加
#   desc: BUY: gross_pnl=0 仅累加 fees；SELL: gross=(fill_price-avg_cost)×qty，累加 net_pnl+fees；avg_cost=None 时从 tracker 读（须在 apply_fill 前调用）
#   inputs: I1 I3
#   outputs: RealizedPnl + 累计 realized_pnl_total/fees_total/fill_count
#   invariant: realized_pnl_total仅record_fill修改(refresh只读)
# - id: A2
#   name_zh: ② 市价校验
#   name_en: RealtimePnlDashboard.refresh 前置校验
#   intro: 拒绝负市价，市价缺失的标的回退用均价（浮盈按 0 算）
#   desc: price<0 抛 ZA-RPT-0001；market_prices.get(symbol, avg_cost) 回退
#   inputs: I2
#   outputs: 校验通过的市价表
# - id: A3
#   name_zh: ③ 未实现盈亏与持仓明细重算
#   name_en: refresh 持仓循环 + PnlCalculator.calculate_unrealized
#   intro: 用当前市价逐标的重算市值和浮动盈亏及浮盈百分比
#   desc: market_value=qty×current_price；upnl=calculate_unrealized(symbol,qty,avg_cost,price)；pct=(current-avg)/avg×100（avg=0 时为 0.0）
#   inputs: A2 I3
#   outputs: PositionPnlEntry 列表 + unrealized_total + total_market_value
#   invariant: Decimal-only金额计算(return_pct除外)
# - id: A4
#   name_zh: ④ 组合快照组装
#   name_en: refresh 快照构建（DashboardSnapshot）
#   intro: 汇总已实现+未实现得总盈亏，算总资产和收益率产出不可变快照
#   desc: total_pnl=realized+unrealized；total_assets=cash+total_market_value；return_pct=total_pnl/initial_capital×100；缓存为最近快照
#   inputs: A1 A3 I4
#   outputs: DashboardSnapshot
#   invariant: total_pnl=realized+unrealized恒成立；DashboardSnapshot/PositionPnlEntry frozen不可变；纯消费层不发布事件不改持仓
# 层: 输出
# - id: O1
#   name_zh: 实时盈亏仪表盘快照
#   name_en: DashboardSnapshot
#   intro: 某时刻完整组合盈亏/持仓明细/风控状态的不可变快照，供前端渲染（3s 刷新由消费者定时调 refresh）
#   invariant: total_pnl=realized+unrealized
#   downstream: zephyr.frontend（D-FRONTEND 渲染消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A1
# I3 --> A3
# I4 --> A4
# A1 --> A4
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from threading import Lock
from typing import Optional

from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.trading.pnl_calculator import PnlCalculator, RealizedPnl

_logger = logging.getLogger(__name__)


class InvalidDashboardInputError(ZephyrBaseError):
    """仪表盘输入非法——负市价/非正初始资金等。"""

    error_code = "ZA-RPT-0001"


# ── 数据模型（全部 frozen 不可变）──


@dataclass(frozen=True)
class PositionPnlEntry:
    """单标的持仓盈亏明细。不可变。"""

    symbol: str
    quantity: Decimal
    avg_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: float  # (current-avg)/avg × 100, avg=0时为0.0


@dataclass(frozen=True)
class DashboardSnapshot:
    """实时仪表盘快照。不可变。

    代表某一时刻的完整组合盈亏/持仓/风控状态, 供 D-FRONTEND 渲染。
    """

    timestamp: datetime
    portfolio_id: str
    total_pnl: Decimal  # realized + unrealized
    realized_pnl: Decimal  # 累计净已实现
    unrealized_pnl: Decimal  # 当前浮盈亏
    total_fees: Decimal  # 累计费用
    cash: Decimal
    total_market_value: Decimal
    total_assets: Decimal  # cash + market_value
    return_pct: float  # total_pnl / initial_capital × 100
    positions: list[PositionPnlEntry]
    risk_snapshot: RiskDashboardSnapshot | None
    fill_count: int
    schema_version: str = "1.0"


# ── 仪表盘主类 ──


class RealtimePnlDashboard:
    """实时盈亏仪表盘——PnL/持仓/风控状态聚合。

    纯消费层: 不修改持仓状态(由 PositionTracker 管理), 不发布事件。
    线程安全: 内部加 Lock 保护累计状态(record_fill 与 refresh 可能并发)。

    Usage:
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        dashboard = RealtimePnlDashboard(tracker)

        # 记录成交（已实现盈亏累计）
        dashboard.record_fill(fill, OrderSide.SELL)

        # 刷新（用当前市价重算未实现盈亏）
        snapshot = dashboard.refresh({"600000": Decimal("11.00")})
        print(snapshot.total_pnl, snapshot.return_pct)
    """

    def __init__(
        self,
        position_tracker: PositionTracker,
        pnl_calculator: PnlCalculator | None = None,
        portfolio_id: str = "realtime_dashboard",
        initial_capital: Decimal = Decimal("1000000"),
        recent_fills_limit: int = 20,
    ) -> None:
        if initial_capital <= 0:
            raise InvalidDashboardInputError(
                f"initial_capital 必须为正, 实际={initial_capital}",
                details={"initial_capital": str(initial_capital)},
            )
        self._tracker = position_tracker
        self._pnl_calc = pnl_calculator if pnl_calculator is not None else PnlCalculator()
        self._portfolio_id = portfolio_id
        self._initial_capital = initial_capital
        self._recent_fills_limit = recent_fills_limit

        # 累计状态（仅 record_fill 修改）
        self._realized_pnl_total: Decimal = Decimal("0")
        self._fees_total: Decimal = Decimal("0")
        self._fill_count: int = 0
        self._recent_fills: deque[tuple[Fill, OrderSide]] = deque(
            maxlen=recent_fills_limit
        )

        # 可选风控状态
        self._risk_snapshot: RiskDashboardSnapshot | None = None

        # 最近一次快照缓存
        self._last_snapshot: DashboardSnapshot | None = None

        self._lock = Lock()

    # ── 只读 properties ──

    @property
    def realized_pnl_total(self) -> Decimal:
        """累计已实现盈亏（净额）。"""
        with self._lock:
            return self._realized_pnl_total

    @property
    def total_fees(self) -> Decimal:
        """累计费用。"""
        with self._lock:
            return self._fees_total

    @property
    def fill_count(self) -> int:
        """累计成交笔数。"""
        with self._lock:
            return self._fill_count

    # ── 核心方法 ──

    def record_fill(
        self, fill: Fill, side: OrderSide, avg_cost: Decimal | None = None
    ) -> RealizedPnl:
        """记录成交——计算已实现盈亏并累加。

        Args:
            fill: 成交回报（CTR-005）。
            side: 买卖方向（Fill 契约无 side 字段, 需调用方传入）。
            avg_cost: 卖出前持仓均价。None 时从 PositionTracker 读取
                （卖出不改变 avg_cost, 可安全读取）。

        Returns:
            RealizedPnl: 本笔成交的已实现盈亏。

        Note:
            - 不修改持仓状态（持仓由 PositionTracker.apply_fill 管理, 调用方负责）
            - BUY: gross_pnl=0, 仅累加费用
            - SELL: gross_pnl=(fill_price-avg_cost)×qty, 累加 net_pnl
            - **调用顺序**: avg_cost=None 时从 tracker 读取, MUST 在 tracker.apply_fill
              之前调用本方法（读取卖出前的成本基础; 全部卖出后 tracker 会将 avg_cost
              重置为 0）。若在 apply_fill 之后调用, 需显式传入卖出前的 avg_cost。
        """
        with self._lock:
            if avg_cost is None:
                avg_cost = self._tracker.avg_costs.get(fill.symbol, Decimal("0"))

            realized = self._pnl_calc.calculate_realized(fill, side, avg_cost)

            self._realized_pnl_total += realized.net_pnl
            self._fees_total += realized.fees.total
            self._fill_count += 1
            self._recent_fills.append((fill, side))

            _logger.debug(
                "record_fill: symbol=%s side=%s net_pnl=%s realized_total=%s fill_count=%s",
                fill.symbol,
                side,
                realized.net_pnl,
                self._realized_pnl_total,
                self._fill_count,
            )
            return realized

    def update_risk(self, risk_snapshot: RiskDashboardSnapshot) -> None:
        """更新风控状态快照（可选, 降级模式: 不调用则 risk_snapshot=None）。"""
        with self._lock:
            self._risk_snapshot = risk_snapshot

    def refresh(self, market_prices: dict[str, Decimal]) -> DashboardSnapshot:
        """刷新仪表盘——用当前市价重算未实现盈亏, 产出快照。

        Args:
            market_prices: {symbol: current_price} 当前市价字典。
                缺失的标的回退到 avg_cost（market_value=qty×avg_cost, unrealized=0）。

        Returns:
            DashboardSnapshot: 含总盈亏/持仓明细/风控状态的不可变快照。

        Note:
            - 纯函数式: 输入 market_prices → 输出 DashboardSnapshot
            - 同时缓存为最近一次快照（get_snapshot 可读取）
            - 负市价拒绝（InvalidDashboardInputError）
        """
        # 校验市价
        for symbol, price in market_prices.items():
            if price < 0:
                raise InvalidDashboardInputError(
                    f"market_price 不能为负, symbol={symbol} price={price}",
                    details={"symbol": symbol, "price": str(price)},
                )

        with self._lock:
            pos_snapshot = self._tracker.get_positions()
            avg_costs = self._tracker.avg_costs

            positions: list[PositionPnlEntry] = []
            unrealized_total = Decimal("0")
            total_market_value = Decimal("0")

            for symbol, qty in pos_snapshot.holdings.items():
                avg_cost = avg_costs.get(symbol, Decimal("0"))
                # 市价缺失回退 avg_cost（unrealized=0）
                current_price = market_prices.get(symbol, avg_cost)
                market_value = qty * current_price
                upnl = self._pnl_calc.calculate_unrealized(
                    symbol, qty, avg_cost, current_price
                )
                unrealized_total += upnl.gross_pnl
                total_market_value += market_value

                # 浮盈百分比: (current-avg)/avg × 100, avg=0 时为 0.0
                if avg_cost > 0:
                    pnl_pct = float((current_price - avg_cost) / avg_cost * Decimal("100"))
                else:
                    pnl_pct = 0.0

                positions.append(
                    PositionPnlEntry(
                        symbol=symbol,
                        quantity=qty,
                        avg_cost=avg_cost,
                        current_price=current_price,
                        market_value=market_value,
                        unrealized_pnl=upnl.gross_pnl,
                        unrealized_pnl_pct=pnl_pct,
                    )
                )

            total_pnl = self._realized_pnl_total + unrealized_total
            total_assets = pos_snapshot.cash + total_market_value
            return_pct = (
                float(total_pnl / self._initial_capital * Decimal("100"))
                if self._initial_capital > 0
                else 0.0
            )

            snapshot = DashboardSnapshot(
                timestamp=datetime.now(UTC),
                portfolio_id=self._portfolio_id,
                total_pnl=total_pnl,
                realized_pnl=self._realized_pnl_total,
                unrealized_pnl=unrealized_total,
                total_fees=self._fees_total,
                cash=pos_snapshot.cash,
                total_market_value=total_market_value,
                total_assets=total_assets,
                return_pct=return_pct,
                positions=positions,
                risk_snapshot=self._risk_snapshot,
                fill_count=self._fill_count,
            )
            self._last_snapshot = snapshot

            _logger.debug(
                "refresh: total_pnl=%s realized=%s unrealized=%s assets=%s return_pct=%.2f%% "
                "positions=%d fill_count=%d",
                total_pnl,
                self._realized_pnl_total,
                unrealized_total,
                total_assets,
                return_pct,
                len(positions),
                self._fill_count,
            )
            return snapshot

    def get_snapshot(self) -> DashboardSnapshot | None:
        """获取最近一次 refresh 的快照（无则 None）。"""
        with self._lock:
            return self._last_snapshot


__all__ = [
    "DashboardSnapshot",
    "InvalidDashboardInputError",
    "PositionPnlEntry",
    "RealtimePnlDashboard",
]
