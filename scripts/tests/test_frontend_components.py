# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] scripts.tests.test_frontend_components
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.dashboard.components.backtest_results; zephyr.frontend.dashboard.components.tick_replay; zephyr.frontend.dashboard.components.order_book; zephyr.frontend.dashboard.components.position_monitor; zephyr.frontend.dashboard.components.trade_panel
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] TTL=task_bound（施工完成后退役）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""5个前端组件综合验证脚本（TTL=task_bound，施工完成后退役）

验证组件:
  1. backtest_results: fetch 从 BacktestResult 派生 + 3阶段门控
  2. tick_replay: 分页 + 做T场景识别
  3. order_book: 5档盘口 + 压力比
  4. position_monitor: 持仓 + T+1标记
  5. trade_panel: 风控校验 + 紧急停止 + human_gated
"""
from datetime import datetime
from decimal import Decimal

from zephyr.frontend.dashboard.components.backtest_results import (
    BacktestGateStatus,
    BacktestMetrics,
    fetch_backtest_results,
    render_backtest_results,
)
from zephyr.frontend.dashboard.components.tick_replay import (
    ReplaySpeed,
    detect_t_scenarios,
    fetch_tick_replay,
    render_tick_replay,
)
from zephyr.frontend.dashboard.components.order_book import (
    fetch_order_book,
    render_order_book,
)
from zephyr.frontend.dashboard.components.position_monitor import (
    fetch_position_monitor,
    render_position_monitor,
)
from zephyr.frontend.dashboard.components.trade_panel import (
    DEFAULT_GREY_CAPITAL,
    DEFAULT_GREY_MAX_QTY,
    OrderItem,
    OrderSubmission,
    TradePanelData,
    build_risk_warning,
    emergency_stop,
    render_trade_panel,
    submit_order,
    validate_order_submission,
)


def _ok(name, cond, detail=""):
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))
    return cond


def test_backtest_results():
    print("=== Test 1: backtest_results ===")
    # Mock BacktestResult (CTR-P1-016, 11必填字段)
    class MockBR:
        annual_return = 0.18
        end_date = datetime(2024, 6, 30)
        idempotency_key = "bt-001"
        max_drawdown = -0.12
        sharpe_ratio = 1.85
        start_date = datetime(2024, 1, 1)
        strategy_id = "t_spike_30s"
        timestamp = datetime(2024, 7, 1)
        total_return = 0.09
        trades_count = 42
        win_rate = 0.55
        overfitting_flag = False

    br = MockBR()
    nav = [1.0, 1.01, 1.03, 1.02, 1.05, 1.04, 1.06]
    dd = [0.0, 0.0, 0.0, -0.0097, -0.0097, -0.0194, -0.0194]
    ts = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"]

    data = fetch_backtest_results(
        br,
        nav_series=nav,
        drawdown_series=dd,
        timestamps=ts,
        sortino=2.1,
        ic=0.08,
        ir=1.2,
    )
    ok1 = _ok("fetch 派生7个指标", data.metrics.sharpe == 1.85 and data.metrics.ic == 0.08 and data.metrics.ir == 1.2)
    ok2 = _ok("fetch 净值曲线7点", len(data.net_value_curve) == 7)

    # 3阶段门控
    gate = BacktestGateStatus(is_passed=True, wfa_passed=True, oos_passed=False)
    ok3 = _ok("3阶段门控 all_passed=False (OOS未通过)", gate.all_passed is False)
    gate2 = BacktestGateStatus(is_passed=True, wfa_passed=True, oos_passed=True)
    ok4 = _ok("3阶段门控 all_passed=True (全通过)", gate2.all_passed is True)

    data.gate_status = gate
    payload = render_backtest_results(data)
    ok5 = _ok("render 返回 dict 含7个指标", "metrics" in payload and payload["metrics"]["sharpe"] == 1.85)
    ok6 = _ok("render 含3阶段门控", payload["gate_status"]["all_passed"] is False)

    # 过拟合标记
    br.overfitting_flag = True
    data2 = fetch_backtest_results(br, nav_series=nav)
    payload2 = render_backtest_results(data2)
    ok7 = _ok("过拟合标记透传", payload2["overfitting_flag"] is True)

    return all([ok1, ok2, ok3, ok4, ok5, ok6, ok7])


def test_tick_replay():
    print("=== Test 2: tick_replay ===")
    # 构造冲高回落 Tick 序列（模拟30秒冲高回落）
    ticks = []
    base = datetime(2024, 1, 15, 9, 30, 0)
    for i in range(30):
        ts = base.replace(second=i)
        if i < 10:
            price = 10.0 + i * 0.05  # 冲高 10.0 → 10.45
        elif i < 20:
            price = 10.45 - (i - 10) * 0.03  # 回落 10.45 → 10.15
        else:
            price = 10.15 + (i - 20) * 0.01
        ticks.append({
            "timestamp": str(ts),
            "last_price": price,
            "ask_price": [price + 0.01 * j for j in range(1, 6)],
            "bid_price": [price - 0.01 * j for j in range(1, 6)],
            "ask_vol": [100 * j for j in range(1, 6)],
            "bid_vol": [100 * (6 - j) for j in range(1, 6)],
            "volume": 1000,
            "amount": 1000 * price,
        })

    # 分页：page=1, page_size=15 → 前15个 Tick
    data = fetch_tick_replay(ticks, symbol="600000.SH", page=1, page_size=15)
    ok1 = _ok("分页加载 visible=15", data.total_ticks == 30 and len(data.ticks) == 15)
    ok2 = _ok("归一化 last_price", abs(data.ticks[0].last_price - 10.0) < 0.001)

    # 做T场景识别
    marks = detect_t_scenarios(data.ticks)
    ok3 = _ok(f"做T场景识别 ({len(marks)} 个标记)", len(marks) > 0)

    payload = render_tick_replay(data)
    ok4 = _ok("render 返回 dict 含场景数", payload["t_scenario_count"] == len(marks))
    ok5 = _ok("render 含 symbol", payload["symbol"] == "600000.SH")

    # 空序列
    data_empty = fetch_tick_replay([], symbol="000001.SZ")
    ok6 = _ok("空 Tick 序列不报错", data_empty.total_ticks == 0 and len(data_empty.ticks) == 0)

    return all([ok1, ok2, ok3, ok4, ok5, ok6])


def test_order_book():
    print("=== Test 3: order_book ===")
    # Mock MiniQmtProvider
    class MockProvider:
        def get_order_book(self, symbol):
            return {
                "symbol": symbol,
                "ask_price": [Decimal("10.51"), Decimal("10.52"), Decimal("10.53"), Decimal("10.54"), Decimal("10.55")],
                "bid_price": [Decimal("10.50"), Decimal("10.49"), Decimal("10.48"), Decimal("10.47"), Decimal("10.46")],
                "ask_vol": [Decimal("100"), Decimal("200"), Decimal("300"), Decimal("400"), Decimal("500")],
                "bid_vol": [Decimal("150"), Decimal("250"), Decimal("350"), Decimal("450"), Decimal("550")],
                "last_price": Decimal("10.50"),
                "timestamp": datetime(2024, 1, 15, 9, 30, 0),
            }

    data = fetch_order_book(MockProvider(), "600000.SH")
    ok1 = _ok("fetch 5档 ask_price", len(data.ask_price) == 5 and abs(data.ask_price[0] - 10.51) < 0.001)
    ok2 = _ok("fetch 5档 bid_vol", len(data.bid_vol) == 5 and data.bid_vol[0] == 150)

    # 压力比 = bid_vol_total / ask_vol_total
    # bid_total = 150+250+350+450+550 = 1750
    # ask_total = 100+200+300+400+500 = 1500
    # pressure = 1750 / 1500 ≈ 1.1667
    ok3 = _ok(f"压力比计算 ({data.pressure_ratio:.4f})", abs(data.pressure_ratio - 1750/1500) < 0.001)

    payload = render_order_book(data)
    ok4 = _ok("render 返回 dict 含5档", len(payload["ask_price"]) == 5)
    ok5 = _ok("render 含压力比", "pressure_ratio" in payload)

    # Provider 为 None
    data_none = fetch_order_book(None, "000001.SZ")
    ok6 = _ok("Provider=None 返回空 OrderBookData", data_none.symbol == "000001.SZ" and not data_none.ask_price)

    # Provider 抛异常
    class BadProvider:
        def get_order_book(self, symbol):
            raise RuntimeError("连接失败")
    data_err = fetch_order_book(BadProvider(), "600000.SH")
    ok7 = _ok("Provider抛异常返回空 OrderBookData", not data_err.ask_price)

    return all([ok1, ok2, ok3, ok4, ok5, ok6, ok7])


def test_position_monitor():
    print("=== Test 4: position_monitor ===")
    # Mock PositionSnapshot
    class MockSnapshot:
        as_of_timestamp = datetime(2024, 1, 15, 14, 0, 0)
        idempotency_key = "pos-001"
        portfolio_id = "zephyr_session"
        cash = Decimal("50000")
        holdings = {"600000.SH": Decimal("1000"), "000001.SZ": Decimal("500")}
        market_values = {"600000.SH": Decimal("10500"), "000001.SZ": Decimal("6500")}
        total_market_value = Decimal("17000")

    class MockBroker:
        def get_positions(self):
            return MockSnapshot()

    today_bought = {"600000.SH": 200}  # 600000.SH 当日买入200股 → T+1锁定
    last_prices = {"600000.SH": 10.5, "000001.SZ": 13.0}
    cost_prices = {"600000.SH": 10.0, "000001.SZ": 13.0}

    data = fetch_position_monitor(
        MockBroker(),
        today_bought_map=today_bought,
        last_prices=last_prices,
        cost_prices=cost_prices,
    )
    ok1 = _ok("fetch 持仓2个标的", len(data.positions) == 2)
    ok2 = _ok("fetch 总资产 = 50000+17000 = 67000", abs(data.total_asset - 67000) < 0.01)

    # T+1 标记
    pos_600000 = next(p for p in data.positions if p.symbol == "600000.SH")
    ok3 = _ok("600000.SH T+1锁定标记", pos_600000.is_t_plus_1_locked is True)
    ok4 = _ok("600000.SH 可用 = 1000-200 = 800", pos_600000.available_quantity == 800)

    pos_000001 = next(p for p in data.positions if p.symbol == "000001.SZ")
    ok5 = _ok("000001.SZ 无T+1锁定", pos_000001.is_t_plus_1_locked is False)

    payload = render_position_monitor(data)
    ok6 = _ok("render 返回 dict 含持仓", payload["positions_count"] == 2)
    ok7 = _ok("render 含T+1标记", any(p["is_t_plus_1_locked"] for p in payload["positions"]))

    # Broker 为 None
    data_none = fetch_position_monitor(None)
    ok8 = _ok("Broker=None 返回空", data_none.total_asset == 0.0 and len(data_none.positions) == 0)

    return all([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8])


def test_trade_panel():
    print("=== Test 5: trade_panel (human_gated) ===")
    # 5.1 风控校验
    sub_ok = OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.50, order_type="limit")
    ok1, msg1 = validate_order_submission(sub_ok, available_cash=20000)
    ok_pass = _ok("风控校验通过 (100股@10.5 限价)", ok1 and msg1 == "校验通过")

    sub_qty = OrderSubmission(symbol="600000.SH", side="buy", quantity=50, price=10.50, order_type="limit")
    ok2, msg2 = validate_order_submission(sub_qty)
    ok_qty = _ok("50股被拒 (A股最小1手)", not ok2 and "100" in msg2)

    sub_step = OrderSubmission(symbol="600000.SH", side="buy", quantity=150, price=10.50, order_type="limit")
    ok3, msg3 = validate_order_submission(sub_step)
    ok_step = _ok("150股被拒 (非100整数倍)", not ok3 and "100" in msg3)

    sub_grey = OrderSubmission(symbol="600000.SH", side="buy", quantity=200, price=10.50, order_type="limit")
    ok4, msg4 = validate_order_submission(sub_grey, enable_grey=True)
    ok_grey = _ok("200股被拒 (灰度100股上限)", not ok4 and "灰度" in msg4)

    sub_cash = OrderSubmission(symbol="600000.SH", side="buy", quantity=100, price=10.50, order_type="limit")
    ok5, msg5 = validate_order_submission(sub_cash, available_cash=500)
    ok_cash = _ok("预估金额>可用资金被拒", not ok5 and "可用资金" in msg5)

    # 5.2 风控提示
    risk_text = build_risk_warning(sub_ok, available_cash=20000)
    ok_risk = _ok("风控提示含T+1", "T+1" in risk_text and "预估金额" in risk_text)

    # 5.3 下单：未确认被拒
    class MockEngine:
        def __init__(self):
            self.submitted = []
        def submit_order(self, order):
            self.submitted.append(order)
            return "broker-001"

    engine = MockEngine()
    ok6, msg6, _ = submit_order(engine, sub_ok, available_cash=20000, confirmed=False)
    ok_unconfirmed = _ok("未二次确认被拒", not ok6 and "二次确认" in msg6)

    # 5.4 下单：已确认成功
    ok7, msg7, _ = submit_order(engine, sub_ok, available_cash=20000, confirmed=True)
    ok_submit = _ok(f"已确认下单成功 ({msg7})", ok7 and msg7 == "broker-001" and len(engine.submitted) == 1)

    # 5.5 紧急停止
    orders = [
        OrderItem(order_id="o1", broker_order_id="b1", symbol="600000.SH", side="buy", quantity=100, price=10.5, status="SUBMITTED"),
        OrderItem(order_id="o2", broker_order_id="b2", symbol="600000.SH", side="buy", quantity=100, price=10.5, status="FILLED"),
        OrderItem(order_id="o3", broker_order_id="b3", symbol="600000.SH", side="buy", quantity=100, price=10.5, status="PARTIALLY_FILLED"),
        OrderItem(order_id="o4", broker_order_id="b4", symbol="600000.SH", side="buy", quantity=100, price=10.5, status="PENDING"),
    ]

    class MockEngineCancel:
        def cancel_order(self, broker_order_id):
            return True  # 全部撤单成功

    cancelled, errs = emergency_stop(MockEngineCancel(), orders)
    # SUBMITTED + PARTIALLY_FILLED + PENDING = 3 笔非终态
    ok_emergency = _ok(f"紧急停止撤单 {cancelled} 笔 (预期3)", cancelled == 3 and len(errs) == 0)

    # 5.6 render
    data = TradePanelData(orders=orders, available_cash=50000, total_asset=67000)
    payload = render_trade_panel(data)
    ok_render = _ok("render 返回 dict 含4个订单", payload["orders_count"] == 4)

    # 5.7 灰度常量
    ok_grey_const = _ok(
        f"灰度常量 1万元/{DEFAULT_GREY_MAX_QTY}股",
        DEFAULT_GREY_CAPITAL == 10000.0 and DEFAULT_GREY_MAX_QTY == 100,
    )

    return all([ok_pass, ok_qty, ok_step, ok_grey, ok_cash, ok_risk,
                ok_unconfirmed, ok_submit, ok_emergency, ok_render, ok_grey_const])


def main():
    print("=" * 60)
    print("5个前端组件综合验证")
    print("=" * 60)

    results = [
        ("backtest_results", test_backtest_results()),
        ("tick_replay", test_tick_replay()),
        ("order_book", test_order_book()),
        ("position_monitor", test_position_monitor()),
        ("trade_panel (human_gated)", test_trade_panel()),
    ]

    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    all_pass = True
    for name, ok in results:
        mark = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {mark}  {name}")
        if not ok:
            all_pass = False

    if all_pass:
        print("\nALL OK ✅ 5个前端组件全部验证通过")
    else:
        print("\n❌ 存在失败用例")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
