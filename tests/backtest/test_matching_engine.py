# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_matching_engine
# [DOMAIN] D_BACKTEST
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-BT-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""matching_engine + matching_logic + portfolio 正式测试（原 scripts/tests/ 临时验证脚本转正）"""

from decimal import Decimal

from zephyr.backtest.core.matching_engine import (
    MatchingConfig,
    MatchingEngine,
    MatchingError,
    MatchingFill,
    MatchOrderInput,
    OrderBookSnapshot,
    TickSnapshot,
)
from zephyr.backtest.core.matching_logic import MatchingLogic
from zephyr.backtest.core.portfolio import Portfolio


def test_backward_compatible_generate_fills():
    """向后兼容 - generate_fills with prices (日线回测模式)"""
    config = MatchingConfig(commission_rate=Decimal("0.0000854"), slippage_bps=Decimal("1"))
    engine = MatchingEngine(config=config)
    assert isinstance(engine.logic, MatchingLogic), "logic must be MatchingLogic instance"

    portfolio = Portfolio(initial_capital=Decimal("100000"))
    fills = engine.generate_fills(
        target_weights={"000001.SZ": 0.5},
        prices={"000001.SZ": Decimal("10.5")},
        portfolio=portfolio,
        date="2024-01-15",
    )
    assert len(fills) == 1, "日线兼容模式应生成1个fill"
    assert fills[0].side == "BUY"
    assert fills[0].symbol == "000001.SZ"


def test_generate_fills_with_order_book():
    """5档盘口撮合"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    portfolio = Portfolio(initial_capital=Decimal("100000"))
    ob = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(
            Decimal("10.50"),
            Decimal("10.51"),
            Decimal("10.52"),
            Decimal("10.53"),
            Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"),
            Decimal("10.48"),
            Decimal("10.47"),
            Decimal("10.46"),
            Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        last_price=Decimal("10.50"),
    )
    fills = engine.generate_fills_with_order_book(
        target_weights={"000001.SZ": 0.5},
        order_books={"000001.SZ": ob},
        portfolio=portfolio,
        date="2024-01-15",
    )
    assert len(fills) == 1
    assert fills[0].price > Decimal("10.50"), "BUY 价格应 >= ask1（含滑点）"


def test_match_tick_order_level_digestion():
    """Tick级5档撮合（做T专用）- 逐档消化"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    tick = TickSnapshot(
        symbol="000001.SZ",
        timestamp="2024-01-15 09:30:00",
        last_price=Decimal("10.50"),
        open=Decimal("10.4"),
        high=Decimal("10.6"),
        low=Decimal("10.3"),
        prev_close=Decimal("10.4"),
        amount=Decimal("1000000"),
        volume=Decimal("100000"),
        ask_price=(
            Decimal("10.50"),
            Decimal("10.51"),
            Decimal("10.52"),
            Decimal("10.53"),
            Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"),
            Decimal("10.48"),
            Decimal("10.47"),
            Decimal("10.46"),
            Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("100"),
            Decimal("200"),
            Decimal("300"),
            Decimal("400"),
            Decimal("500"),
        ),
        bid_vol=(
            Decimal("100"),
            Decimal("200"),
            Decimal("300"),
            Decimal("400"),
            Decimal("500"),
        ),
    )
    fill_tick = engine.match_tick_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("1000"),
            order_type="TICK",
        ),
        tick,
    )
    assert fill_tick.filled, "Tick级5档撮合应完全成交"
    assert fill_tick.quantity == Decimal("1000"), f"expected 1000, got {fill_tick.quantity}"
    assert Decimal("10.50") <= fill_tick.price <= Decimal("10.54"), f"加权均价应在5档区间内, got {fill_tick.price}"


def test_match_limit_order_not_filled():
    """限价单未成交场景"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    ob = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(
            Decimal("10.50"),
            Decimal("10.51"),
            Decimal("10.52"),
            Decimal("10.53"),
            Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"),
            Decimal("10.48"),
            Decimal("10.47"),
            Decimal("10.46"),
            Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        last_price=Decimal("10.50"),
    )
    fill = engine.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("10.40"),
        ),
        ob,
    )
    assert not fill.filled, "限价低于ask1应不成交"


def test_match_limit_order_filled():
    """限价单成交场景"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    ob = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(
            Decimal("10.50"),
            Decimal("10.51"),
            Decimal("10.52"),
            Decimal("10.53"),
            Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"),
            Decimal("10.48"),
            Decimal("10.47"),
            Decimal("10.46"),
            Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        last_price=Decimal("10.50"),
    )
    fill = engine.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("10.55"),
        ),
        ob,
    )
    assert fill.filled, "限价高于ask1应成交"


def test_shared_logic_reuse():
    """回测=实盘一致性 - logic 属性可直接给 MiniQmtBroker 复用"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    ob = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(
            Decimal("10.50"),
            Decimal("10.51"),
            Decimal("10.52"),
            Decimal("10.53"),
            Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"),
            Decimal("10.48"),
            Decimal("10.47"),
            Decimal("10.46"),
            Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"),
            Decimal("2000"),
            Decimal("3000"),
            Decimal("4000"),
            Decimal("5000"),
        ),
        last_price=Decimal("10.50"),
    )
    shared_logic = engine.logic
    fill_direct = shared_logic.match_market_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="MARKET",
        ),
        ob,
    )
    assert fill_direct.filled


def _make_ob(last: str = "10.00") -> OrderBookSnapshot:
    """构造对称 5 档盘口（测试辅助）"""
    return OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(Decimal("10.00"), Decimal("10.01"), Decimal("10.02"), Decimal("10.03"), Decimal("10.04")),
        bid_price=(Decimal("9.99"), Decimal("9.98"), Decimal("9.97"), Decimal("9.96"), Decimal("9.95")),
        ask_vol=(Decimal("10000"),) * 5,
        bid_vol=(Decimal("10000"),) * 5,
        last_price=Decimal(last),
    )


def test_total_cost_no_double_count_slippage():
    """total_cost 不得双重计入滑点（fill.price 已含滑点价）——AI-NIGHT-001 审查发现"""
    # 2026-08-21 费率口径统一（#233）：佣金万0.854 / 印花税万5卖出 / 过户费万0.1双向
    config = MatchingConfig(
        commission_rate=Decimal("0.0000854"),
        slippage_bps=Decimal("10"),  # 10bp 放大差异便于观测
        stamp_tax_rate=Decimal("0.0005"),
        min_commission=Decimal("5"),
    )
    logic = MatchingLogic(config)
    ob = _make_ob()

    # BUY: price = 10.00*(1+10/10000) = 10.01；佣金 = max(1000*10.01*0.0000854, 5) = max(0.855, 5) = 5；过户费 = gross*0.00001
    buy_fill = logic.match_market_order(
        MatchOrderInput(symbol="000001.SZ", side="BUY", quantity=Decimal("1000"), order_type="MARKET"), ob
    )
    assert buy_fill.price == Decimal("10.01")
    gross_buy = Decimal("1000") * Decimal("10.01")
    expected_buy = gross_buy + Decimal("5") + gross_buy * Decimal("0.00001")
    assert buy_fill.total_cost == expected_buy, (
        f"BUY total_cost 双计滑点: 期望 {expected_buy}（gross+commission+transfer），实际 {buy_fill.total_cost}"
    )

    # SELL: price = 9.99*(1-10/10000) = 9.98001；费用 = max(gross*0.0000854, 5) + 印花税 gross*0.0005 + 过户费 gross*0.00001
    sell_fill = logic.match_market_order(
        MatchOrderInput(symbol="000001.SZ", side="SELL", quantity=Decimal("1000"), order_type="MARKET"), ob
    )
    assert sell_fill.price == Decimal("9.98001")
    gross = Decimal("1000") * Decimal("9.98001")
    expected_sell = gross - (Decimal("5") + gross * Decimal("0.0005") + gross * Decimal("0.00001"))
    assert sell_fill.total_cost == expected_sell, (
        f"SELL total_cost 双计滑点: 期望 {expected_sell}（gross-commission-tax），实际 {sell_fill.total_cost}"
    )


def test_sell_realized_pnl_no_double_slippage():
    """卖出已实现盈亏不得再减 slippage_cost（成交价已含滑点）——AI-NIGHT-001 审查发现"""
    portfolio = Portfolio(initial_capital=Decimal("200000"))
    config = MatchingConfig(
        commission_rate=Decimal("0.0000854"), slippage_bps=Decimal("10"), stamp_tax_rate=Decimal("0.0005")
    )
    engine = MatchingEngine(config=config)
    ob = _make_ob()

    # d1 买入 1000 股 @10.00（ask1）
    buy_fills = engine.generate_fills_with_order_book(
        target_weights={"000001.SZ": 0.5}, order_books={"000001.SZ": ob}, portfolio=portfolio, date="2024-01-15"
    )
    for f in buy_fills:
        portfolio.apply_fill(f, allow_t_plus_1=False)
    pos = portfolio.get_position("000001.SZ")
    assert pos is not None and pos.quantity > 0
    qty_before = pos.quantity
    avg_cost = pos.avg_cost

    # d2 全部卖出 @bid1=9.99（T+1 后）
    sell_order = MatchOrderInput(symbol="000001.SZ", side="SELL", quantity=qty_before, order_type="MARKET")
    sell_fill = engine.logic.match_market_order(sell_order, ob)
    from zephyr.backtest.core.portfolio import BacktestFill

    portfolio.apply_fill(
        BacktestFill(
            date="2024-01-16",
            symbol=sell_fill.symbol,
            side="SELL",
            quantity=sell_fill.quantity,
            price=sell_fill.price,
            commission=sell_fill.commission,
            slippage_cost=sell_fill.slippage_cost,
        ),
        allow_t_plus_1=False,
    )
    # 期望 realized = (price - avg_cost) * qty - commission（不再 - slippage_cost）
    expected = (sell_fill.price - avg_cost) * qty_before - sell_fill.commission
    actual = portfolio.get_position("000001.SZ").realized_pnl
    assert abs(actual - expected) < Decimal("0.01"), f"realized_pnl 双计滑点: 期望 {expected}, 实际 {actual}"


def test_price_limit_board_inference():
    """涨跌停按板块幅度推断（AI-NIGHT-001 #211）：科创/创业 20%、北交所 30%、主板 10%"""
    engine = MatchingEngine(config=MatchingConfig())
    # 主板 60xxxx：±10%
    assert engine._is_price_limit("600001.SH", Decimal("11.00"), Decimal("10.00")) is True
    assert engine._is_price_limit("600001.SH", Decimal("10.50"), Decimal("10.00")) is False
    # 科创板 68xxxx：±20%——+15% 不应判涨停（旧统一 10% 会误判不成交）
    assert engine._is_price_limit("688001.SH", Decimal("11.50"), Decimal("10.00")) is False
    assert engine._is_price_limit("688001.SH", Decimal("12.00"), Decimal("10.00")) is True
    # 创业板 30xxxx：±20%
    assert engine._is_price_limit("300001.SZ", Decimal("11.50"), Decimal("10.00")) is False
    assert engine._is_price_limit("300001.SZ", Decimal("8.00"), Decimal("10.00")) is True
    # 北交所 8xxxxx：±30%
    assert engine._is_price_limit("830799.BJ", Decimal("12.50"), Decimal("10.00")) is False
    assert engine._is_price_limit("830799.BJ", Decimal("13.00"), Decimal("10.00")) is True
