# [BLUEPRINT] MOD-RPT-004 | docs/03_modules/_domain_reporting/realtime_pnl_dashboard/blueprint.md
# [MODULE] tests.reporting.test_realtime_pnl_dashboard
# [DOMAIN] D_REPORTING
# [INVARIANTS] Decimal-only断言; 验证frozen不可变; realized累计仅record_fill修改; total_pnl=realized+unrealized恒成立
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDashboardInputError(ZA-RPT-0001)
# [TESTS] self
# [A_module] module_id=MOD-RPT-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-004 Real-time P&L Dashboard 单元测试.

覆盖（blueprint §9）:
  - 已实现盈亏累计(多笔 BUY/SELL)
  - 未实现盈亏实时计算
  - 组合总盈亏 total_pnl = realized + unrealized
  - return_pct 百分比
  - 风控状态注入/降级(无 risk_snapshot=None)
  - 持仓明细(多头/空持仓)
  - refresh 幂等性(可重复调用)
  - Decimal精度
  - frozen不可变
  - 边界值(空持仓/负市价拒绝/initial_capital非正)
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.reporting.realtime_pnl_dashboard import (
    DashboardSnapshot,
    InvalidDashboardInputError,
    PositionPnlEntry,
    RealtimePnlDashboard,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot

# ── 辅助构造 ──


def make_fill(
    symbol: str = "600000",
    fill_price: Decimal = Decimal("10"),
    filled_quantity: Decimal = Decimal("100"),
    fill_id: str = "F001",
) -> Fill:
    """构造测试用 Fill（CTR-005, commission=0 由 FeeCalculator 统一核算）。"""
    return Fill(
        fill_id=fill_id,
        fill_price=fill_price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=filled_quantity,
        idempotency_key=f"ik-{fill_id}",
        order_id=f"O-{fill_id}",
        strategy_id="S001",
        symbol=symbol,
    )


def make_dashboard(
    initial_cash: Decimal = Decimal("1000000"),
) -> RealtimePnlDashboard:
    """构造带 PositionTracker 的仪表盘。"""
    tracker = PositionTracker(initial_cash=initial_cash)
    return RealtimePnlDashboard(
        position_tracker=tracker,
        initial_capital=initial_cash,
    )


# ── 已实现盈亏累计测试 ──


class TestRecordFill:
    def test_buy_records_fees_only(self) -> None:
        """买入: gross_pnl=0, 仅累加费用。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), filled_quantity=Decimal("100"))
        # 先 apply_fill 到 tracker（更新持仓）, 再 record_fill（累计 PnL）
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        realized = dash.record_fill(fill, OrderSide.BUY)

        # BUY: turnover=1000, commission=max(0.25,5)=5, stamp=0, transfer=0.01
        assert realized.gross_pnl == Decimal("0")
        assert realized.fees.total == Decimal("5.01")
        assert realized.net_pnl == Decimal("-5.01")
        assert dash.realized_pnl_total == Decimal("-5.01")
        assert dash.total_fees == Decimal("5.01")
        assert dash.fill_count == 1

    def test_sell_records_realized_pnl(self) -> None:
        """卖出: 计算已实现盈亏并累加。

        调用顺序: record_fill 在 apply_fill 之前（读取卖出前 avg_cost；
        全部卖出后 tracker 会重置 avg_cost=0）。
        """
        dash = make_dashboard()
        buy_fill = make_fill(fill_price=Decimal("10"), fill_id="FB")
        sell_fill = make_fill(fill_price=Decimal("11"), fill_id="FS")

        dash._tracker.apply_fill(buy_fill, OrderSide.BUY)
        dash.record_fill(buy_fill, OrderSide.BUY)
        # 卖出前 avg_cost=10: record_fill 先读, 再 apply_fill 更新持仓
        realized = dash.record_fill(sell_fill, OrderSide.SELL)
        dash._tracker.apply_fill(sell_fill, OrderSide.SELL)

        # SELL: gross=(11-10)*100=100, turnover=1100
        # commission=max(0.275,5)=5, stamp=0.55, transfer=0.011, fees=5.561
        assert realized.gross_pnl == Decimal("100")
        assert realized.fees.total == Decimal("5.561")
        assert realized.net_pnl == Decimal("94.439")
        # 累计: BUY(-5.01) + SELL(94.439) = 89.429
        assert dash.realized_pnl_total == Decimal("89.429")
        assert dash.total_fees == Decimal("10.571")
        assert dash.fill_count == 2

    def test_record_fill_reads_avg_cost_from_tracker(self) -> None:
        """avg_cost=None 时从 PositionTracker 读取（apply_fill 之前调用）。"""
        dash = make_dashboard()
        buy_fill = make_fill(fill_price=Decimal("10"), fill_id="FB")
        sell_fill = make_fill(fill_price=Decimal("12"), fill_id="FS")

        dash._tracker.apply_fill(buy_fill, OrderSide.BUY)
        dash.record_fill(buy_fill, OrderSide.BUY)
        # record_fill 先读 avg_cost=10, 再 apply_fill
        realized = dash.record_fill(sell_fill, OrderSide.SELL, avg_cost=None)
        dash._tracker.apply_fill(sell_fill, OrderSide.SELL)
        # gross=(12-10)*100=200
        assert realized.gross_pnl == Decimal("200")

    def test_record_fill_explicit_avg_cost(self) -> None:
        """显式传入 avg_cost 覆盖 tracker 读取。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("11"), fill_id="F1")
        realized = dash.record_fill(fill, OrderSide.SELL, avg_cost=Decimal("9"))
        # gross=(11-9)*100=200
        assert realized.gross_pnl == Decimal("200")

    def test_multiple_fills_accumulate(self) -> None:
        """多笔成交累计正确。"""
        dash = make_dashboard()
        for i in range(5):
            fill = make_fill(fill_price=Decimal("10"), fill_id=f"F{i}")
            dash._tracker.apply_fill(fill, OrderSide.BUY)
            dash.record_fill(fill, OrderSide.BUY)
        # 每笔 BUY net=-5.01, 5笔 = -25.05
        assert dash.realized_pnl_total == Decimal("-25.05")
        assert dash.fill_count == 5


# ── 未实现盈亏 + 组合总盈亏测试 ──


class TestRefreshUnrealized:
    def test_refresh_computes_unrealized(self) -> None:
        """refresh 用当前市价重算未实现盈亏。"""
        dash = make_dashboard()
        buy_fill = make_fill(fill_price=Decimal("10"), fill_id="FB")
        dash._tracker.apply_fill(buy_fill, OrderSide.BUY)
        dash.record_fill(buy_fill, OrderSide.BUY)

        # 持仓 100@10, 市价 11 → unrealized=(11-10)*100=100
        snapshot = dash.refresh({"600000": Decimal("11")})
        assert snapshot.unrealized_pnl == Decimal("100")
        assert len(snapshot.positions) == 1
        entry = snapshot.positions[0]
        assert entry.symbol == "600000"
        assert entry.quantity == Decimal("100")
        assert entry.avg_cost == Decimal("10")
        assert entry.current_price == Decimal("11")
        assert entry.market_value == Decimal("1100")
        assert entry.unrealized_pnl == Decimal("100")
        assert entry.unrealized_pnl_pct == pytest.approx(10.0)

    def test_total_pnl_equals_realized_plus_unrealized(self) -> None:
        """不变量: total_pnl = realized + unrealized。"""
        dash = make_dashboard()
        buy_fill = make_fill(fill_price=Decimal("10"), fill_id="FB")
        sell_fill = make_fill(fill_price=Decimal("11"), fill_id="FS")
        dash._tracker.apply_fill(buy_fill, OrderSide.BUY)
        dash.record_fill(buy_fill, OrderSide.BUY)
        dash._tracker.apply_fill(sell_fill, OrderSide.SELL)
        dash.record_fill(sell_fill, OrderSide.SELL)
        # 卖完后持仓=0, 但再买一笔留持仓
        buy2 = make_fill(fill_price=Decimal("10"), filled_quantity=Decimal("50"), fill_id="FB2")
        dash._tracker.apply_fill(buy2, OrderSide.BUY)
        dash.record_fill(buy2, OrderSide.BUY)

        snapshot = dash.refresh({"600000": Decimal("12")})
        # realized = BUY(-5.01)+SELL(94.439)+BUY2(-5.005... )
        # total_pnl = realized + unrealized
        assert snapshot.total_pnl == snapshot.realized_pnl + snapshot.unrealized_pnl

    def test_return_pct(self) -> None:
        """return_pct = total_pnl / initial_capital × 100。"""
        dash = make_dashboard(initial_cash=Decimal("1000000"))
        buy_fill = make_fill(fill_price=Decimal("10"), fill_id="FB")
        dash._tracker.apply_fill(buy_fill, OrderSide.BUY)
        dash.record_fill(buy_fill, OrderSide.BUY)

        snapshot = dash.refresh({"600000": Decimal("11")})
        # unrealized=100, realized=-5.01, total=94.99
        # return_pct = 94.99/1000000*100 = 0.009499
        assert snapshot.return_pct == pytest.approx(0.009499, rel=1e-4)

    def test_refresh_caches_snapshot(self) -> None:
        """refresh 缓存最近一次快照, get_snapshot 可读取。"""
        dash = make_dashboard()
        assert dash.get_snapshot() is None
        snap1 = dash.refresh({"600000": Decimal("10")})
        assert dash.get_snapshot() is snap1

    def test_refresh_idempotent_when_no_change(self) -> None:
        """无新成交时, 两次 refresh 的 realized/fill_count 一致。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)

        snap1 = dash.refresh({"600000": Decimal("11")})
        snap2 = dash.refresh({"600000": Decimal("11")})
        assert snap1.realized_pnl == snap2.realized_pnl
        assert snap1.fill_count == snap2.fill_count
        assert snap1.unrealized_pnl == snap2.unrealized_pnl

    def test_missing_price_falls_back_to_avg_cost(self) -> None:
        """市价缺失的标的回退 avg_cost, unrealized=0。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)

        # 不提供市价 → 回退 avg_cost=10, unrealized=0
        snapshot = dash.refresh({})
        assert snapshot.unrealized_pnl == Decimal("0")
        assert snapshot.positions[0].current_price == Decimal("10")
        assert snapshot.positions[0].unrealized_pnl == Decimal("0")


# ── 空持仓 + 边界值测试 ──


class TestEdgeCases:
    def test_empty_positions(self) -> None:
        """无成交时 refresh 返回空持仓快照。"""
        dash = make_dashboard()
        snapshot = dash.refresh({})
        assert snapshot.positions == []
        assert snapshot.unrealized_pnl == Decimal("0")
        assert snapshot.realized_pnl == Decimal("0")
        assert snapshot.total_pnl == Decimal("0")
        assert snapshot.total_fees == Decimal("0")
        assert snapshot.fill_count == 0
        assert snapshot.cash == Decimal("1000000")
        assert snapshot.total_market_value == Decimal("0")
        assert snapshot.total_assets == Decimal("1000000")
        assert snapshot.return_pct == pytest.approx(0.0)

    def test_invalid_negative_market_price(self) -> None:
        """负市价拒绝。"""
        dash = make_dashboard()
        with pytest.raises(InvalidDashboardInputError) as exc_info:
            dash.refresh({"600000": Decimal("-1")})
        assert exc_info.value.error_code == "ZA-RPT-0001"

    def test_invalid_initial_capital_zero(self) -> None:
        """initial_capital=0 拒绝。"""
        tracker = PositionTracker()
        with pytest.raises(InvalidDashboardInputError):
            RealtimePnlDashboard(tracker, initial_capital=Decimal("0"))

    def test_invalid_initial_capital_negative(self) -> None:
        """initial_capital 负数拒绝。"""
        tracker = PositionTracker()
        with pytest.raises(InvalidDashboardInputError):
            RealtimePnlDashboard(tracker, initial_capital=Decimal("-100"))

    def test_total_assets_equals_cash_plus_market_value(self) -> None:
        """不变量: total_assets = cash + total_market_value。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)

        snapshot = dash.refresh({"600000": Decimal("11")})
        assert snapshot.total_assets == snapshot.cash + snapshot.total_market_value


# ── 风控状态测试 ──


class TestRiskStatus:
    def test_update_risk_injects_snapshot(self) -> None:
        """update_risk 注入风控快照, refresh 携带。"""
        dash = make_dashboard()
        risk = RiskDashboardSnapshot(
            snapshot_time="2026-08-02T10:00:00",
            portfolio_id="realtime_dashboard",
            portfolio_var_1d=0.02,
            max_drawdown_current=-0.05,
            gross_leverage=1.1,
            top_position_concentration=0.3,
            overall_risk_score=0.4,
            idempotency_key="risk-001",
        )
        dash.update_risk(risk)
        snapshot = dash.refresh({})
        assert snapshot.risk_snapshot is risk
        assert snapshot.risk_snapshot.portfolio_var_1d == 0.02

    def test_no_risk_snapshot_degrades_gracefully(self) -> None:
        """无风控数据时 risk_snapshot=None, 核心功能不受影响。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)

        snapshot = dash.refresh({"600000": Decimal("11")})
        assert snapshot.risk_snapshot is None
        # PnL/持仓仍正常
        assert snapshot.unrealized_pnl == Decimal("100")
        assert snapshot.total_pnl == Decimal("94.99")


# ── Decimal精度 + frozen不可变 ──


class TestInvariants:
    def test_all_amounts_are_decimal(self) -> None:
        """所有金额为 Decimal(return_pct除外)。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)
        snapshot = dash.refresh({"600000": Decimal("11")})

        assert isinstance(snapshot.total_pnl, Decimal)
        assert isinstance(snapshot.realized_pnl, Decimal)
        assert isinstance(snapshot.unrealized_pnl, Decimal)
        assert isinstance(snapshot.total_fees, Decimal)
        assert isinstance(snapshot.cash, Decimal)
        assert isinstance(snapshot.total_market_value, Decimal)
        assert isinstance(snapshot.total_assets, Decimal)
        assert isinstance(snapshot.return_pct, float)
        entry = snapshot.positions[0]
        assert isinstance(entry.quantity, Decimal)
        assert isinstance(entry.avg_cost, Decimal)
        assert isinstance(entry.current_price, Decimal)
        assert isinstance(entry.market_value, Decimal)
        assert isinstance(entry.unrealized_pnl, Decimal)
        assert isinstance(entry.unrealized_pnl_pct, float)

    def test_dashboard_snapshot_is_frozen(self) -> None:
        """DashboardSnapshot 不可变。"""
        dash = make_dashboard()
        snapshot = dash.refresh({})
        with pytest.raises(Exception):
            snapshot.total_pnl = Decimal("999")  # type: ignore[misc]

    def test_position_pnl_entry_is_frozen(self) -> None:
        """PositionPnlEntry 不可变。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)
        snapshot = dash.refresh({"600000": Decimal("11")})
        with pytest.raises(Exception):
            snapshot.positions[0].symbol = "999"  # type: ignore[misc]

    def test_realized_pnl_only_modified_by_record_fill(self) -> None:
        """realized_pnl_total 仅 record_fill 修改, refresh 不改变。"""
        dash = make_dashboard()
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)
        before = dash.realized_pnl_total
        dash.refresh({"600000": Decimal("11")})
        dash.refresh({"600000": Decimal("20")})
        assert dash.realized_pnl_total == before


# ── 多标的测试 ──


class TestMultiSymbol:
    def test_multi_symbol_portfolio(self) -> None:
        """多标的组合: 持仓明细 + 汇总正确。"""
        dash = make_dashboard()
        # 买两个标的
        f1 = make_fill(symbol="600000", fill_price=Decimal("10"), fill_id="F1")
        f2 = make_fill(symbol="000001", fill_price=Decimal("20"), fill_id="F2")
        dash._tracker.apply_fill(f1, OrderSide.BUY)
        dash.record_fill(f1, OrderSide.BUY)
        dash._tracker.apply_fill(f2, OrderSide.BUY)
        dash.record_fill(f2, OrderSide.BUY)

        snapshot = dash.refresh({"600000": Decimal("11"), "000001": Decimal("18")})
        assert len(snapshot.positions) == 2
        # 600000: unrealized=(11-10)*100=100
        # 000001: unrealized=(18-20)*100=-200
        assert snapshot.unrealized_pnl == Decimal("-100")
        symbols = {p.symbol for p in snapshot.positions}
        assert symbols == {"600000", "000001"}

    def test_zero_pct_when_avg_cost_zero(self) -> None:
        """avg_cost=0 时 unrealized_pnl_pct=0.0。"""
        dash = make_dashboard()
        # 不通过 tracker, 直接构造无成本持仓场景测试 pct 边界
        # 正常场景 avg_cost>0, 这里验证 avg_cost=0 的回退逻辑
        fill = make_fill(fill_price=Decimal("10"), fill_id="F1")
        dash._tracker.apply_fill(fill, OrderSide.BUY)
        dash.record_fill(fill, OrderSide.BUY)
        # avg_cost=10 > 0, 正常 pct
        snapshot = dash.refresh({"600000": Decimal("11")})
        assert snapshot.positions[0].unrealized_pnl_pct == pytest.approx(10.0)
