# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.test_matching_engine
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""matching_engine + matching_logic + portfolio 正式测试（原 scripts/tests/ 临时验证脚本转正）"""
from decimal import Decimal

from zephyr.backtest.core.matching_engine import (
    MatchingEngine,
    MatchingConfig,
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
    config = MatchingConfig(
        commission_rate=Decimal("0.0003"), slippage_bps=Decimal("1")
    )
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
            Decimal("10.50"), Decimal("10.51"), Decimal("10.52"),
            Decimal("10.53"), Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"), Decimal("10.48"), Decimal("10.47"),
            Decimal("10.46"), Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
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
            Decimal("10.50"), Decimal("10.51"), Decimal("10.52"),
            Decimal("10.53"), Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"), Decimal("10.48"), Decimal("10.47"),
            Decimal("10.46"), Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("100"), Decimal("200"), Decimal("300"),
            Decimal("400"), Decimal("500"),
        ),
        bid_vol=(
            Decimal("100"), Decimal("200"), Decimal("300"),
            Decimal("400"), Decimal("500"),
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
    assert Decimal("10.50") <= fill_tick.price <= Decimal("10.54"), (
        f"加权均价应在5档区间内, got {fill_tick.price}"
    )


def test_match_limit_order_not_filled():
    """限价单未成交场景"""
    config = MatchingConfig()
    engine = MatchingEngine(config=config)
    ob = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=(
            Decimal("10.50"), Decimal("10.51"), Decimal("10.52"),
            Decimal("10.53"), Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"), Decimal("10.48"), Decimal("10.47"),
            Decimal("10.46"), Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
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
            Decimal("10.50"), Decimal("10.51"), Decimal("10.52"),
            Decimal("10.53"), Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"), Decimal("10.48"), Decimal("10.47"),
            Decimal("10.46"), Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
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
            Decimal("10.50"), Decimal("10.51"), Decimal("10.52"),
            Decimal("10.53"), Decimal("10.54"),
        ),
        bid_price=(
            Decimal("10.49"), Decimal("10.48"), Decimal("10.47"),
            Decimal("10.46"), Decimal("10.45"),
        ),
        ask_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
        ),
        bid_vol=(
            Decimal("1000"), Decimal("2000"), Decimal("3000"),
            Decimal("4000"), Decimal("5000"),
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
