# [BLUEPRINT] MOD-EX-049 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""PositionTracker (MOD-EX-002 / D-EX-CORE-04) 单元测试。

覆盖: 买入/卖出持仓更新、平均成本计算、现金跟踪、PositionSnapshot产出、
零持仓清理、并发安全、与SimulationBroker逻辑等价性。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.position_tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.fill import Fill

# ── 辅助函数 ──


def make_fill(
    symbol: str = "600000.SH",
    fill_price: Decimal = Decimal("10.00"),
    filled_quantity: Decimal = Decimal("100"),
    commission: Decimal = Decimal("3.00"),
    order_id: str = "ord-001",
    strategy_id: str = "test",
) -> Fill:
    """构造测试用 Fill。"""
    return Fill(
        fill_id=f"fill-{order_id}",
        fill_price=fill_price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=filled_quantity,
        idempotency_key=f"idem-{order_id}",
        order_id=order_id,
        strategy_id=strategy_id,
        symbol=symbol,
        commission=commission,
    )


# ── 买入测试 ──


class TestBuy:
    def test_buy_updates_quantity(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        fill = make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10"))
        tracker.apply_fill(fill, OrderSide.BUY)
        assert tracker.holdings["600000.SH"] == Decimal("100")

    def test_buy_updates_avg_cost(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        fill = make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10"))
        tracker.apply_fill(fill, OrderSide.BUY)
        assert tracker.avg_costs["600000.SH"] == Decimal("10")

    def test_buy_deducts_cash(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        fill = make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10"), commission=Decimal("3"))
        tracker.apply_fill(fill, OrderSide.BUY)
        # cash = 1000000 - 100*10 - 3 = 998997
        assert tracker.cash == Decimal("998997")

    def test_multiple_buys_weighted_avg(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        # 第一次买入: 100股 @ 10
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        # 第二次买入: 100股 @ 12
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("100"), fill_price=Decimal("12")), OrderSide.BUY
        )
        # avg = (10*100 + 12*100) / 200 = 11
        assert tracker.holdings["600000.SH"] == Decimal("200")
        assert tracker.avg_costs["600000.SH"] == Decimal("11")

    def test_multiple_buys_different_quantities(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("200"), fill_price=Decimal("13")), OrderSide.BUY
        )
        # avg = (10*100 + 13*200) / 300 = 3600/300 = 12
        assert tracker.holdings["600000.SH"] == Decimal("300")
        assert tracker.avg_costs["600000.SH"] == Decimal("12")


# ── 卖出测试 ──


class TestSell:
    def test_sell_reduces_quantity(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("50"), fill_price=Decimal("11")), OrderSide.SELL
        )
        assert tracker.holdings["600000.SH"] == Decimal("50")

    def test_sell_preserves_avg_cost(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("50"), fill_price=Decimal("11")), OrderSide.SELL
        )
        # 卖出后 avg_cost 不变 = 10
        assert tracker.avg_costs["600000.SH"] == Decimal("10")

    def test_sell_adds_cash(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10"), commission=Decimal("3")),
            OrderSide.BUY,
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("50"), fill_price=Decimal("11"), commission=Decimal("2")),
            OrderSide.SELL,
        )
        # buy: cash = 1000000 - 1000 - 3 = 998997
        # sell: cash = 998997 + 50*11 - 2 = 998997 + 550 - 2 = 999545
        assert tracker.cash == Decimal("999545")

    def test_sell_to_zero_clears_avg_cost(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("100"), fill_price=Decimal("11")), OrderSide.SELL
        )
        assert tracker.holdings["600000.SH"] == Decimal("0")
        assert tracker.avg_costs["600000.SH"] == Decimal("0")

    def test_sell_to_zero_realizes_pnl_in_cash(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", filled_quantity=Decimal("100"), fill_price=Decimal("10"), commission=Decimal("0")),
            OrderSide.BUY,
        )
        tracker.apply_fill(
            make_fill(order_id="o2", filled_quantity=Decimal("100"), fill_price=Decimal("12"), commission=Decimal("0")),
            OrderSide.SELL,
        )
        # buy: cash = 1000000 - 1000 = 999000
        # sell: cash = 999000 + 1200 = 1000200
        # profit = 200
        assert tracker.cash == Decimal("1000200")


# ── PositionSnapshot 测试 ──


class TestPositionSnapshot:
    def test_snapshot_is_frozen(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY)
        snap = tracker.get_positions()
        with pytest.raises(AttributeError):
            snap.cash = Decimal("999")  # type: ignore[misc]

    def test_snapshot_holdings_match_tracker(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(symbol="600000.SH", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        tracker.apply_fill(
            make_fill(symbol="000001.SZ", filled_quantity=Decimal("200"), fill_price=Decimal("15")), OrderSide.BUY
        )
        snap = tracker.get_positions()
        assert snap.holdings["600000.SH"] == Decimal("100")
        assert snap.holdings["000001.SZ"] == Decimal("200")

    def test_snapshot_market_values(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(symbol="600000.SH", filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY
        )
        snap = tracker.get_positions()
        # market_value = 100 * 10 = 1000
        assert snap.market_values["600000.SH"] == Decimal("1000")
        assert snap.total_market_value == Decimal("1000")

    def test_snapshot_cash(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10"), commission=Decimal("3")), OrderSide.BUY
        )
        snap = tracker.get_positions()
        assert snap.cash == Decimal("998997")

    def test_snapshot_excludes_zero_holdings(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(
            make_fill(order_id="o1", symbol="600000.SH", filled_quantity=Decimal("100"), fill_price=Decimal("10")),
            OrderSide.BUY,
        )
        tracker.apply_fill(
            make_fill(order_id="o2", symbol="600000.SH", filled_quantity=Decimal("100"), fill_price=Decimal("11")),
            OrderSide.SELL,
        )
        snap = tracker.get_positions()
        # 600000.SH 持仓=0，不应出现在 holdings 中
        assert "600000.SH" not in snap.holdings

    def test_snapshot_portfolio_id(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"), portfolio_id="simulation")
        snap = tracker.get_positions()
        assert snap.portfolio_id == "simulation"

    def test_snapshot_gross_leverage(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY)
        snap = tracker.get_positions()
        # total_mv = 1000, initial_cash = 1000000, leverage = 0.001
        assert snap.gross_leverage == pytest.approx(0.001, rel=1e-6)


# ── 并发安全测试 ──


class TestConcurrency:
    def test_thread_safe_apply_fill(self):
        """多线程并发 apply_fill 不丢数据。"""
        import threading

        tracker = PositionTracker(initial_cash=Decimal("100000000"))
        errors: list[Exception] = []

        def buy_batch(start: int) -> None:
            try:
                for i in range(start, start + 50):
                    fill = make_fill(order_id=f"o{i}", filled_quantity=Decimal("1"), fill_price=Decimal("10"))
                    tracker.apply_fill(fill, OrderSide.BUY)
            except Exception as e:  # noqa: BLE001 — test: collect thread errors
                errors.append(e)

        threads = [threading.Thread(target=buy_batch, args=(i * 50,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # 4 threads × 50 buys × 1 share = 200 shares
        assert tracker.holdings["600000.SH"] == Decimal("200")


# ── SimulationBroker 等价性测试 ──


class TestSimulationBrokerEquivalence:
    """验证 PositionTracker 的逻辑与 SimulationBroker 的 _update_positions 等价。"""

    def test_same_buy_result_as_simulation_broker(self):
        from zephyr.governance.adapters.simulation_broker import SimulationBroker
        from zephyr.shared.contracts.order import Order

        # SimulationBroker
        broker = SimulationBroker(initial_cash=Decimal("1000000"))
        broker.connect()
        order = Order(
            order_id="ord-1",
            idempotency_key="idem-1",
            symbol="600000.SH",
            strategy_id="test",
            side=OrderSide.BUY,
            order_type=__import__("zephyr.shared.contracts.enums.order_enums", fromlist=["OrderType"]).OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            created_at=datetime.now(UTC),
        )
        broker.submit_order(order)
        broker_snap = broker.get_positions()

        # PositionTracker (commission=0 to match — SimulationBroker applies commission internally)
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        # SimulationBroker commission_rate=0.0000854（#233）, slippage_bps=1
        # fill_price = 10 * (1 + 1/10000) = 10.001
        # commission = 100 * 10.001 * 0.0000854 = 0.08540854
        fill = Fill(
            fill_id="fill-1",
            fill_price=Decimal("10.001"),
            fill_timestamp=datetime.now(UTC),
            filled_quantity=Decimal("100"),
            idempotency_key="idem-1",
            order_id="ord-1",
            strategy_id="test",
            symbol="600000.SH",
            commission=Decimal("100") * Decimal("10.001") * Decimal("0.0000854"),
        )
        tracker.apply_fill(fill, OrderSide.BUY)
        tracker_snap = tracker.get_positions()

        # 持仓数量一致
        assert tracker_snap.holdings["600000.SH"] == broker_snap.holdings["600000.SH"]
        # 现金一致
        assert tracker_snap.cash == broker_snap.cash


# ── reset 测试 ──


class TestReset:
    def test_reset_clears_state(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        tracker.apply_fill(make_fill(filled_quantity=Decimal("100"), fill_price=Decimal("10")), OrderSide.BUY)
        tracker.reset()
        assert tracker.cash == Decimal("1000000")
        assert tracker.holdings == {}
        assert tracker.avg_costs == {}
