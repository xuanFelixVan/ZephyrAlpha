# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.tests.test_matching_engine_v1_1_0
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.matching_engine; zephyr.backtest.core.matching_logic
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
# [TTL] task_bound
"""matching_engine v1.1.0 重构验证脚本（TTL=task_bound，施工完成后退役）"""
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


def main() -> None:
    # Test 1: 向后兼容 - generate_fills with prices (日线回测模式)
    config = MatchingConfig(
        commission_rate=Decimal("0.0003"), slippage_bps=Decimal("1")
    )
    engine = MatchingEngine(config=config)
    print("config:", engine.config)
    print("logic:", type(engine.logic).__name__)

    # 验证 logic 就是 MatchingLogic（回测=实盘一致性核心）
    assert isinstance(engine.logic, MatchingLogic), "logic must be MatchingLogic instance"

    portfolio = Portfolio(initial_capital=Decimal("100000"))
    fills = engine.generate_fills(
        target_weights={"000001.SZ": 0.5},
        prices={"000001.SZ": Decimal("10.5")},
        portfolio=portfolio,
        date="2024-01-15",
    )
    print(f"generate_fills (日线兼容): {len(fills)} fills")
    for f in fills:
        print(
            f"  {f.side} {f.symbol} qty={f.quantity} price={f.price} commission={f.commission}"
        )
    assert len(fills) == 1, "日线兼容模式应生成1个fill"
    assert fills[0].side == "BUY"
    assert fills[0].symbol == "000001.SZ"

    # Test 2: 5档盘口撮合
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
    fills2 = engine.generate_fills_with_order_book(
        target_weights={"000001.SZ": 0.5},
        order_books={"000001.SZ": ob},
        portfolio=portfolio,
        date="2024-01-15",
    )
    print(f"generate_fills_with_order_book (5档盘口): {len(fills2)} fills")
    for f in fills2:
        print(
            f"  {f.side} {f.symbol} qty={f.quantity} price={f.price} commission={f.commission}"
        )
    # BUY 应按 ask1=10.50 成交（应用滑点后）
    assert len(fills2) == 1
    assert fills2[0].price > Decimal("10.50"), "BUY 价格应 >= ask1（含滑点）"

    # Test 3: Tick级5档撮合（做T专用）- 逐档消化
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
    # 大单1000股超过单档100股，应逐档消化
    fill_tick = engine.match_tick_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("1000"),
            order_type="TICK",
        ),
        tick,
    )
    print(
        f"match_tick_order (逐档消化): filled={fill_tick.filled} qty={fill_tick.quantity} price={fill_tick.price}"
    )
    # 5档总卖量=100+200+300+400+500=1500 > 1000，应完全成交
    assert fill_tick.filled, "Tick级5档撮合应完全成交"
    assert fill_tick.quantity == Decimal("1000"), f"expected 1000, got {fill_tick.quantity}"
    # 加权均价应在 10.50~10.54 之间
    assert Decimal("10.50") <= fill_tick.price <= Decimal("10.54"), (
        f"加权均价应在5档区间内, got {fill_tick.price}"
    )

    # Test 4: 限价单未成交场景
    fill_limit = engine.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("10.40"),  # 低于 ask1=10.50，不成交
        ),
        ob,
    )
    print(f"match_limit_order (未成交): filled={fill_limit.filled}")
    assert not fill_limit.filled, "限价低于ask1应不成交"

    # Test 5: 限价单成交场景
    fill_limit2 = engine.match_limit_order(
        MatchOrderInput(
            symbol="000001.SZ",
            side="BUY",
            quantity=Decimal("100"),
            order_type="LIMIT",
            limit_price=Decimal("10.55"),  # 高于 ask1=10.50，成交
        ),
        ob,
    )
    print(
        f"match_limit_order (成交): filled={fill_limit2.filled} price={fill_limit2.price}"
    )
    assert fill_limit2.filled, "限价高于ask1应成交"

    # Test 6: 回测=实盘一致性 - logic 属性可直接给 MiniQmtBroker 复用
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
    print(
        f"shared_logic.match_market_order: filled={fill_direct.filled} price={fill_direct.price}"
    )
    assert fill_direct.filled

    print("ALL OK")


if __name__ == "__main__":
    main()
