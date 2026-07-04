# [A_test] module_id: SRC-TST-P1-COMP | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §16.7.1-§16.7.5
# [MODULE] tests.governance.observability.test_p1_components_unit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_p1_components_unit · 5 个 P1 交易/回测组件单元测试（v3.0.0, #ARCH-047）

覆盖组件（蓝图 §16.7.1-§16.7.5）:
  1. backtest_results — 回测结果可视化
  2. tick_replay — Tick 回放可视化
  3. order_book — 5 档盘口实时展示
  4. position_monitor — 实盘持仓监控
  5. trade_panel — 实盘交易面板（human_gated）

测试策略:
  - dataclass: 实例化 + 默认值 + property
  - fetch_*: None 输入 / mock 对象 / 空数据
  - render_*: dict payload 路径（pn=None 时返回 dict，可断言）
  - trade_panel 额外: validate_order_submission / build_risk_warning / submit_order / emergency_stop

组件在 pn=None 时 render 返回 dict payload（无 panel 依赖），测试主要走此路径。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest


# =========================================================================
# 1. backtest_results 单元测试
# =========================================================================

class TestBacktestResults:
    """backtest_results.py 组件测试（蓝图 §16.7.1）"""

    def test_backtest_metrics_defaults(self) -> None:
        from zephyr.frontend.dashboard.components.backtest_results import BacktestMetrics
        m = BacktestMetrics()
        assert m.sharpe == 0.0
        assert m.sortino == 0.0
        assert m.max_drawdown == 0.0
        assert m.ic == 0.0
        assert m.ir == 0.0
        assert m.win_rate == 0.0
        assert m.annual_return == 0.0

    def test_gate_status_all_passed(self) -> None:
        from zephyr.frontend.dashboard.components.backtest_results import BacktestGateStatus
        gs = BacktestGateStatus()
        assert not gs.all_passed
        gs.is_passed = True
        gs.wfa_passed = True
        gs.oos_passed = True
        assert gs.all_passed

    def test_fetch_with_none(self) -> None:
        from zephyr.frontend.dashboard.components.backtest_results import (
            fetch_backtest_results,
        )
        data = fetch_backtest_results(backtest_result=None)
        assert data.backtest_id == ""
        assert data.strategy_id == ""
        assert data.net_value_curve == []

    def test_fetch_from_mock_backtest_result(self) -> None:
        @dataclass
        class MockBR:
            idempotency_key: str = "bt-001"
            strategy_id: str = "strat-A"
            sharpe_ratio: float = 1.5
            max_drawdown: float = -0.12
            win_rate: float = 0.55
            annual_return: float = 0.25
            overfitting_flag: bool = False

        from zephyr.frontend.dashboard.components.backtest_results import (
            fetch_backtest_results,
        )
        data = fetch_backtest_results(
            backtest_result=MockBR(),
            nav_series=[1.0, 1.02, 1.01, 1.03],
            drawdown_series=[0.0, -0.01, -0.02, -0.005],
            timestamps=["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
            sortino=2.0,
            ic=0.05,
            ir=0.8,
        )
        assert data.backtest_id == "bt-001"
        assert data.strategy_id == "strat-A"
        assert len(data.net_value_curve) == 4
        assert data.metrics.sharpe == 1.5
        assert data.metrics.sortino == 2.0
        assert data.metrics.ic == 0.05
        assert data.metrics.ir == 0.8

    def test_render_returns_payload(self, monkeypatch) -> None:
        import zephyr.frontend.dashboard.components.backtest_results as mod
        monkeypatch.setattr(mod, "pn", None)
        from zephyr.frontend.dashboard.components.backtest_results import (
            BacktestGateStatus,
            BacktestMetrics,
            BacktestResultData,
            render_backtest_results,
        )
        data = BacktestResultData(
            backtest_id="bt-test",
            strategy_id="strat-X",
            net_value_curve=[1.0, 1.05, 1.10],
            drawdown_curve=[0.0, -0.02, -0.01],
            timestamps=["t1", "t2", "t3"],
            metrics=BacktestMetrics(sharpe=1.2, sortino=1.8, max_drawdown=-0.15),
            gate_status=BacktestGateStatus(is_passed=True, wfa_passed=True, oos_passed=False),
        )
        payload = render_backtest_results(data)
        assert payload["backtest_id"] == "bt-test"
        assert payload["strategy_id"] == "strat-X"
        assert payload["net_value_points"] == 3
        assert payload["metrics"]["sharpe"] == 1.2
        assert payload["gate_status"]["is_passed"] is True
        assert payload["gate_status"]["oos_passed"] is False
        assert payload["gate_status"]["all_passed"] is False


# =========================================================================
# 2. tick_replay 单元测试
# =========================================================================

class TestTickReplay:
    """tick_replay.py 组件测试（蓝图 §16.7.2）"""

    def test_replay_speed_enum(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import ReplaySpeed
        assert ReplaySpeed.REAL_TIME.value == "real_time"
        assert ReplaySpeed.FAST_FORWARD.value == "fast_forward"
        assert ReplaySpeed.MAX_SPEED.value == "max_speed"

    def test_tick_snapshot_view_defaults(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import TickSnapshotView
        t = TickSnapshotView()
        assert t.timestamp == ""
        assert t.last_price == 0.0
        assert t.ask_price == []
        assert t.bid_price == []

    def test_fetch_empty(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import fetch_tick_replay
        data = fetch_tick_replay(tick_data=[], symbol="600000.SH")
        assert data.symbol == "600000.SH"
        assert data.ticks == []
        assert data.total_ticks == 0

    def test_fetch_with_pagination(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import (
            TickSnapshotView,
            fetch_tick_replay,
        )
        raw_ticks = [
            {"timestamp": f"t{i}", "last_price": 10.0 + i * 0.01, "volume": 100 + i}
            for i in range(2500)
        ]
        data = fetch_tick_replay(raw_ticks, symbol="000001.SZ", page=1, page_size=1000)
        assert data.total_ticks == 2500
        assert len(data.ticks) == 1000
        assert data.ticks[0].last_price == 10.0
        assert data.ticks[999].last_price == pytest.approx(19.99, abs=1e-6)

        data_p2 = fetch_tick_replay(raw_ticks, symbol="000001.SZ", page=2, page_size=1000)
        assert len(data_p2.ticks) == 1000
        assert data_p2.ticks[0].last_price == pytest.approx(20.0, abs=1e-6)

    def test_detect_t_scenarios_empty(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import detect_t_scenarios
        assert detect_t_scenarios([]) == []

    def test_detect_t_scenarios_spike(self) -> None:
        from zephyr.frontend.dashboard.components.tick_replay import (
            TickSnapshotView,
            detect_t_scenarios,
        )
        ticks = [
            TickSnapshotView(timestamp=f"t{i}", last_price=p)
            for i, p in enumerate([10.0, 10.5, 11.0, 10.2, 9.8, 10.0, 10.1, 10.2])
        ]
        marks = detect_t_scenarios(ticks, spike_drop_window=4, spike_threshold_pct=0.005)
        assert len(marks) >= 1
        assert marks[0].scenario_type == "30s_spike_drop"

    def test_render_returns_payload(self, monkeypatch) -> None:
        import zephyr.frontend.dashboard.components.tick_replay as mod
        monkeypatch.setattr(mod, "pn", None)
        from zephyr.frontend.dashboard.components.tick_replay import (
            ReplaySpeed,
            TickSnapshotView,
            TickReplayData,
            render_tick_replay,
        )
        data = TickReplayData(
            symbol="600000.SH",
            ticks=[TickSnapshotView(timestamp="t1", last_price=10.0, volume=100)],
            replay_speed=ReplaySpeed.MAX_SPEED,
            total_ticks=1,
        )
        payload = render_tick_replay(data)
        assert payload["symbol"] == "600000.SH"
        assert payload["total_ticks"] == 1
        assert payload["visible_ticks"] == 1
        assert payload["replay_speed"] == "max_speed"


# =========================================================================
# 3. order_book 单元测试
# =========================================================================

class TestOrderBook:
    """order_book.py 组件测试（蓝图 §16.7.3）"""

    def test_order_book_data_defaults(self) -> None:
        from zephyr.frontend.dashboard.components.order_book import OrderBookData
        ob = OrderBookData()
        assert ob.symbol == ""
        assert ob.ask_price == []
        assert ob.bid_price == []
        assert ob.ask_vol_total == 0
        assert ob.bid_vol_total == 0
        assert ob.pressure_ratio == 0.0

    def test_order_book_pressure_ratio(self) -> None:
        from zephyr.frontend.dashboard.components.order_book import OrderBookData
        # pressure_ratio 是 plain field（非 property），需显式设值
        # ask_vol_total/bid_vol_total 是 @property，自动计算
        ob = OrderBookData(
            ask_vol=[100, 200, 300, 400, 500],
            bid_vol=[500, 400, 300, 200, 100],
            pressure_ratio=1.0,
        )
        assert ob.ask_vol_total == 1500
        assert ob.bid_vol_total == 1500
        assert ob.pressure_ratio == 1.0

    def test_fetch_with_none(self) -> None:
        from zephyr.frontend.dashboard.components.order_book import fetch_order_book
        data = fetch_order_book(miniqmt_provider=None, symbol="600000.SH")
        assert data.symbol == "600000.SH"
        assert data.ask_price == []

    def test_fetch_from_mock_provider(self) -> None:
        class MockProvider:
            def get_order_book(self, symbol: str) -> dict:
                return {
                    "ask_price": [10.05, 10.06, 10.07, 10.08, 10.09],
                    "bid_price": [10.04, 10.03, 10.02, 10.01, 10.00],
                    "ask_vol": [100, 200, 300, 400, 500],
                    "bid_vol": [500, 400, 300, 200, 100],
                    "last_price": 10.045,
                    "timestamp": "2026-07-05 10:00:00",
                }

        from zephyr.frontend.dashboard.components.order_book import fetch_order_book
        data = fetch_order_book(MockProvider(), "600000.SH")
        assert len(data.ask_price) == 5
        assert len(data.bid_price) == 5
        assert data.last_price == 10.045
        assert data.pressure_ratio == 1.0

    def test_render_returns_payload(self) -> None:
        from zephyr.frontend.dashboard.components.order_book import (
            OrderBookData,
            render_order_book,
        )
        data = OrderBookData(
            symbol="600000.SH",
            ask_price=[10.05, 10.06],
            bid_price=[10.04, 10.03],
            ask_vol=[100, 200],
            bid_vol=[200, 100],
            last_price=10.045,
            pressure_ratio=1.0,
        )
        payload = render_order_book(data)
        assert payload["symbol"] == "600000.SH"
        assert payload["last_price"] == 10.045
        assert payload["ask_vol_total"] == 300
        assert payload["bid_vol_total"] == 300


# =========================================================================
# 4. position_monitor 单元测试
# =========================================================================

class TestPositionMonitor:
    """position_monitor.py 组件测试（蓝图 §16.7.4）"""

    def test_position_item_defaults(self) -> None:
        from zephyr.frontend.dashboard.components.position_monitor import PositionItem
        p = PositionItem()
        assert p.symbol == ""
        assert p.quantity == 0
        assert p.is_t_plus_1_locked is False

    def test_position_item_market_value(self) -> None:
        from zephyr.frontend.dashboard.components.position_monitor import PositionItem
        p = PositionItem(quantity=100, last_price=10.5)
        assert p.market_value == 1050.0

    def test_fetch_with_none(self) -> None:
        from zephyr.frontend.dashboard.components.position_monitor import (
            fetch_position_monitor,
        )
        data = fetch_position_monitor(miniqmt_broker=None)
        assert data.positions == []
        assert data.total_asset == 0.0

    def test_fetch_from_mock_broker(self) -> None:
        @dataclass
        class MockSnapshot:
            cash: float = 50000.0
            holdings: dict = None
            market_values: dict = None
            total_market_value: float = 0.0
            portfolio_id: str = "acc-001"
            as_of_timestamp: Any = None

        snapshot = MockSnapshot(
            cash=50000.0,
            holdings={"600000.SH": 200, "000001.SZ": 100},
            market_values={"600000.SH": 2100.0, "000001.SZ": 1300.0},
            total_market_value=3400.0,
        )

        class MockBroker:
            def get_positions(self) -> Any:
                return snapshot

        from zephyr.frontend.dashboard.components.position_monitor import (
            fetch_position_monitor,
        )
        data = fetch_position_monitor(
            MockBroker(),
            today_bought_map={"600000.SH": 100},
            last_prices={"600000.SH": 10.5, "000001.SZ": 13.0},
            cost_prices={"600000.SH": 10.0, "000001.SZ": 12.5},
        )
        assert len(data.positions) == 2
        pos_600 = [p for p in data.positions if p.symbol == "600000.SH"][0]
        assert pos_600.quantity == 200
        assert pos_600.today_bought == 100
        assert pos_600.is_t_plus_1_locked is True
        assert pos_600.available_quantity == 100
        assert pos_600.frozen_quantity == 100

    def test_render_returns_payload(self) -> None:
        from zephyr.frontend.dashboard.components.position_monitor import (
            PositionItem,
            PositionMonitorData,
            render_position_monitor,
        )
        data = PositionMonitorData(
            account_id="acc-001",
            total_asset=100000.0,
            available_cash=50000.0,
            market_value_total=50000.0,
            today_pnl=1200.0,
            positions=[
                PositionItem(symbol="600000.SH", quantity=100, last_price=10.5, is_t_plus_1_locked=True),
            ],
        )
        payload = render_position_monitor(data)
        assert payload["account_id"] == "acc-001"
        assert payload["total_asset"] == 100000.0
        assert payload["positions_count"] == 1
        assert payload["positions"][0]["symbol"] == "600000.SH"
        assert payload["positions"][0]["is_t_plus_1_locked"] is True


# =========================================================================
# 5. trade_panel 单元测试
# =========================================================================

class TestTradePanelValidation:
    """trade_panel.py 风控校验测试（蓝图 §16.7.5 D）"""

    def test_validate_empty_symbol(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(OrderSubmission(symbol=""))
        assert not ok
        assert "空" in msg

    def test_validate_invalid_side(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(OrderSubmission(symbol="600000.SH", side="invalid"))
        assert not ok
        assert "方向" in msg

    def test_validate_qty_below_min(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(
            OrderSubmission(symbol="600000.SH", side="buy", quantity=50)
        )
        assert not ok
        assert "100" in msg

    def test_validate_qty_not_multiple(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(
            OrderSubmission(symbol="600000.SH", side="buy", quantity=150)
        )
        assert not ok
        assert "整数倍" in msg

    def test_validate_limit_no_price(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(
            OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=0.0, order_type="limit")
        )
        assert not ok
        assert "价格" in msg

    def test_validate_grey_qty_exceeds(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(
            OrderSubmission(symbol="600000.SH", side="buy", quantity=200, price=10.0),
            enable_grey=True,
        )
        assert not ok
        assert "灰度" in msg

    def test_validate_pass(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            validate_order_submission,
        )
        ok, msg = validate_order_submission(
            OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.0),
            available_cash=10000.0,
        )
        assert ok
        assert "通过" in msg


class TestTradePanelRiskWarning:
    """trade_panel.py 风控提示测试"""

    def test_build_risk_warning_buy(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            build_risk_warning,
        )
        sub = OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.0)
        text = build_risk_warning(sub, available_cash=50000.0)
        assert "600000.SH" in text
        assert "BUY" in text
        assert "100" in text
        assert "T+1" in text

    def test_build_risk_warning_sell_no_t1(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            build_risk_warning,
        )
        sub = OrderSubmission(symbol="600000.SH", side="sell", quantity=100, price=10.0)
        text = build_risk_warning(sub, available_cash=50000.0, is_t_plus_1_relevant=True)
        assert "SELL" in text
        assert "T+1" not in text


class TestTradePanelSubmitOrder:
    """trade_panel.py 下单/撤单/紧急停止测试"""

    def test_submit_no_confirmation(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            submit_order,
        )
        ok, msg, risk = submit_order(
            execution_engine=None,
            order_submission=OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.0),
            confirmed=False,
        )
        assert not ok
        assert "确认" in msg

    def test_submit_no_engine(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            submit_order,
        )
        ok, msg, risk = submit_order(
            execution_engine=None,
            order_submission=OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.0),
            confirmed=True,
        )
        assert not ok
        assert "未注入" in msg

    def test_submit_invalid_order(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderSubmission,
            submit_order,
        )
        ok, msg, risk = submit_order(
            execution_engine=object(),
            order_submission=OrderSubmission(symbol="", side="buy", quantity=100, price=10.0),
            confirmed=True,
        )
        assert not ok

    def test_emergency_stop(self) -> None:
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderItem,
            emergency_stop,
        )

        class MockEngine:
            def __init__(self) -> None:
                self.cancelled: list[str] = []

            def cancel_order(self, broker_order_id: str) -> bool:
                self.cancelled.append(broker_order_id)
                return True

        engine = MockEngine()
        orders = [
            OrderItem(broker_order_id="ord-1", status="SUBMITTED"),
            OrderItem(broker_order_id="ord-2", status="FILLED"),
            OrderItem(broker_order_id="ord-3", status="PARTIALLY_FILLED"),
            OrderItem(broker_order_id="ord-4", status="CANCELLED"),
        ]
        cancelled, errors = emergency_stop(engine, orders)
        assert cancelled == 2
        assert errors == []
        assert set(engine.cancelled) == {"ord-1", "ord-3"}


class TestTradePanelRender:
    """trade_panel.py 渲染测试"""

    def test_render_returns_payload(self, monkeypatch) -> None:
        import zephyr.frontend.dashboard.components.trade_panel as mod
        monkeypatch.setattr(mod, "pn", None)
        from zephyr.frontend.dashboard.components.trade_panel import (
            OrderItem,
            TradePanelData,
            render_trade_panel,
        )
        data = TradePanelData(
            orders=[
                OrderItem(order_id="o1", symbol="600000.SH", side="buy", quantity=100, price=10.0, status="FILLED"),
            ],
            available_cash=50000.0,
            total_asset=100000.0,
        )
        payload = render_trade_panel(data)
        assert payload["orders_count"] == 1
        assert payload["available_cash"] == 50000.0
        assert payload["orders"][0]["symbol"] == "600000.SH"
        assert payload["orders"][0]["status"] == "FILLED"
