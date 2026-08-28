# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_matching_logic
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_matching_logic.py
# [TTL] permanent
"""matching_logic 单元测试（52号 四核心模块零单测清偿，AI-WAVE2C-001）。

覆盖: 三模式撮合（市价/限价/Tick逐档）黄金数、滑点与费用边界（最低佣金/
印花税卖出单边/过户费双向）、未成交路径、异常输入（数量/side/类型/盘口）、
纯函数式语义（同输入同输出、frozen 值对象）。
黄金数口径: 费率 #233 裁定（万0.854/滑点1bps/印花万5卖出/过户万0.1/最低5元不免五）。
纯内存合成盘口夹具，不触网不触库。
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingFill,
    MatchingLogic,
    MatchingLogicError,
    MatchOrderInput,
    OrderBookSnapshot,
    TickSnapshot,
)

SYM = "000001.SZ"


def _book(
    ask1: str = "10.00",
    bid1: str = "9.99",
    ask_vols: tuple[str, ...] = ("100", "200", "300", "400", "500"),
    bid_vols: tuple[str, ...] = ("100", "200", "300", "400", "500"),
) -> OrderBookSnapshot:
    """构造5档盘口合成夹具（默认 ask 升序 10.00~10.04 / bid 降序 9.99~9.95）。"""
    a1 = Decimal(ask1)
    b1 = Decimal(bid1)
    return OrderBookSnapshot(
        symbol=SYM,
        ask_price=tuple(a1 + Decimal("0.01") * i for i in range(5)),
        bid_price=tuple(b1 - Decimal("0.01") * i for i in range(5)),
        ask_vol=tuple(Decimal(v) for v in ask_vols),
        bid_vol=tuple(Decimal(v) for v in bid_vols),
        last_price=a1,
    )


def _tick(book: OrderBookSnapshot) -> TickSnapshot:
    """由盘口构造 Tick 快照合成夹具。"""
    return TickSnapshot(
        symbol=book.symbol,
        timestamp=None,
        last_price=book.last_price,
        open=book.last_price,
        high=book.last_price,
        low=book.last_price,
        prev_close=book.last_price,
        amount=Decimal("0"),
        volume=Decimal("0"),
        ask_price=book.ask_price,
        bid_price=book.bid_price,
        ask_vol=book.ask_vol,
        bid_vol=book.bid_vol,
    )


def _order(
    side: str = "BUY",
    qty: str = "100",
    order_type: str = "MARKET",
    limit_price: str | None = None,
) -> MatchOrderInput:
    return MatchOrderInput(
        symbol=SYM,
        side=side,
        quantity=Decimal(qty),
        order_type=order_type,
        limit_price=Decimal(limit_price) if limit_price is not None else None,
    )


class TestMatchingConfig:
    """撮合配置契约（frozen + 费率口径 #233 裁定黄金值）。"""

    def test_default_golden_values(self):
        c = MatchingConfig()
        assert c.commission_rate == Decimal("0.0000854")
        assert c.slippage_bps == Decimal("1")
        assert c.stamp_tax_rate == Decimal("0.0005")
        assert c.transfer_fee_rate == Decimal("0.00001")
        assert c.min_commission == Decimal("5")
        assert c.lot_size == 100
        assert c.price_limit_pct == Decimal("0.10")

    def test_frozen_immutable(self):
        c = MatchingConfig()
        with pytest.raises(FrozenInstanceError):
            c.commission_rate = Decimal("0.001")  # type: ignore[misc]

    def test_logic_default_config(self):
        logic = MatchingLogic()
        assert logic.config == MatchingConfig()


class TestMatchMarketOrder:
    """市价单撮合（盘口最优价 + 滑点 + 费用黄金数）。"""

    def test_buy_golden(self):
        """BUY 100股@ask1=10.00: 滑点后10.001, 佣金=max(0.085,5)+过户0.010001。"""
        logic = MatchingLogic()
        fill = logic.match_market_order(_order("BUY", "100"), _book(ask1="10.00"))
        assert fill.filled is True
        assert fill.symbol == SYM
        assert fill.side == "BUY"
        assert fill.quantity == Decimal("100")
        assert fill.filled_quantity == Decimal("100")
        assert fill.price == Decimal("10.001")
        assert fill.commission == Decimal("5.010001")
        assert fill.slippage_cost == Decimal("0.100")
        assert fill.total_cost == Decimal("1005.110001")

    def test_sell_golden(self):
        """SELL 100股@bid1=9.99: 滑点后9.989001, 佣金+印花(卖出单边)。"""
        logic = MatchingLogic()
        fill = logic.match_market_order(_order("SELL", "100"), _book(bid1="9.99"))
        assert fill.filled is True
        assert fill.price == Decimal("9.989001")
        assert fill.commission == Decimal("5.509439051")
        assert fill.slippage_cost == Decimal("0.0999")
        assert fill.total_cost == Decimal("993.390660949")

    def test_buy_large_order_commission_above_min(self):
        """大额单佣金超过最低5元: 100000股@10.001 成交额1000100, 佣金85.40854+过户10.001。"""
        logic = MatchingLogic()
        fill = logic.match_market_order(_order("BUY", "100000"), _book(ask1="10.00"))
        assert fill.price == Decimal("10.001")
        assert fill.commission == Decimal("95.40954")

    def test_sell_no_stamp_tax_on_buy(self):
        """印花税卖出单边: BUY 佣金=佣金+过户费, 不含印花税。"""
        logic = MatchingLogic()
        fill = logic.match_market_order(_order("BUY", "100000"), _book(ask1="10.00"))
        gross = fill.quantity * fill.price
        expected = gross * Decimal("0.0000854") + gross * Decimal("0.00001")
        assert fill.commission == expected

    def test_buy_empty_ask_raises(self):
        logic = MatchingLogic()
        book = _book()
        empty_ask = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(),
            bid_price=book.bid_price,
            ask_vol=(),
            bid_vol=book.bid_vol,
            last_price=Decimal("10.00"),
        )
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("BUY", "100"), empty_ask)

    def test_sell_empty_bid_raises(self):
        logic = MatchingLogic()
        book = _book()
        empty_bid = OrderBookSnapshot(
            symbol=SYM,
            ask_price=book.ask_price,
            bid_price=(),
            ask_vol=book.ask_vol,
            bid_vol=(),
            last_price=Decimal("10.00"),
        )
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("SELL", "100"), empty_bid)

    def test_buy_zero_ask_price_raises(self):
        logic = MatchingLogic()
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("0"),) * 5,
            bid_price=_book().bid_price,
            ask_vol=(Decimal("100"),) * 5,
            bid_vol=(Decimal("100"),) * 5,
            last_price=Decimal("10.00"),
        )
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("BUY", "100"), book)

    def test_zero_quantity_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("BUY", "0"), _book())

    def test_negative_quantity_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("BUY", "-100"), _book())

    def test_invalid_side_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("HOLD", "100"), _book())

    def test_order_type_mismatch_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_market_order(_order("BUY", "100", order_type="LIMIT", limit_price="10.00"), _book())

    def test_error_code(self):
        err = MatchingLogicError("boom")
        assert err.error_code == "ZA-BT-0007"
        err2 = MatchingLogicError("boom", error_code="ZA-CUSTOM-1")
        assert err2.error_code == "ZA-CUSTOM-1"


class TestMatchLimitOrder:
    """限价单撮合（限价内成交，否则不成交）。"""

    def test_buy_limit_reaches_ask_fills_at_ask(self):
        """BUY 限价10.05 >= ask1=10.00 → 以 ask1 成交(优于限价) + 滑点。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("BUY", "100", order_type="LIMIT", limit_price="10.05"),
            _book(ask1="10.00"),
        )
        assert fill.filled is True
        assert fill.price == Decimal("10.001")
        assert fill.commission == Decimal("5.010001")

    def test_buy_limit_below_ask_unfilled(self):
        """BUY 限价9.99 < ask1=10.00 → 不成交。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("BUY", "100", order_type="LIMIT", limit_price="9.99"),
            _book(ask1="10.00"),
        )
        assert fill.filled is False
        assert fill.quantity == Decimal("0")
        assert fill.filled_quantity == Decimal("0")
        assert fill.price == Decimal("0")
        assert fill.commission == Decimal("0")
        assert fill.slippage_cost == Decimal("0")

    def test_buy_limit_equal_ask_boundary(self):
        """边界: BUY 限价 == ask1 → 成交(>= 语义)。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("BUY", "100", order_type="LIMIT", limit_price="10.00"),
            _book(ask1="10.00"),
        )
        assert fill.filled is True

    def test_sell_limit_reaches_bid_fills_at_bid(self):
        """SELL 限价9.98 <= bid1=9.99 → 以 bid1 成交 + 滑点。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("SELL", "100", order_type="LIMIT", limit_price="9.98"),
            _book(bid1="9.99"),
        )
        assert fill.filled is True
        assert fill.price == Decimal("9.989001")

    def test_sell_limit_above_bid_unfilled(self):
        """SELL 限价10.00 > bid1=9.99 → 不成交。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("SELL", "100", order_type="LIMIT", limit_price="10.00"),
            _book(bid1="9.99"),
        )
        assert fill.filled is False

    def test_sell_limit_equal_bid_boundary(self):
        """边界: SELL 限价 == bid1 → 成交(<= 语义)。"""
        logic = MatchingLogic()
        fill = logic.match_limit_order(
            _order("SELL", "100", order_type="LIMIT", limit_price="9.99"),
            _book(bid1="9.99"),
        )
        assert fill.filled is True

    def test_limit_price_none_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_limit_order(_order("BUY", "100", order_type="LIMIT"), _book())

    def test_limit_price_nonpositive_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_limit_order(
                _order("BUY", "100", order_type="LIMIT", limit_price="0"), _book()
            )

    def test_buy_empty_ask_unfilled_not_error(self):
        """限价单盘口无卖价 → 不成交(非异常)。"""
        logic = MatchingLogic()
        book = _book()
        empty_ask = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(),
            bid_price=book.bid_price,
            ask_vol=(),
            bid_vol=book.bid_vol,
            last_price=Decimal("10.00"),
        )
        fill = logic.match_limit_order(
            _order("BUY", "100", order_type="LIMIT", limit_price="10.05"), empty_ask
        )
        assert fill.filled is False

    def test_order_type_mismatch_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_limit_order(_order("BUY", "100", order_type="MARKET"), _book())


class TestMatchTickOrder:
    """Tick级5档撮合（逐档消化，流动性约束，加权均价）。"""

    def test_buy_two_levels_weighted_average_golden(self):
        """BUY 200股: 消化 ask1(10.00×100)+ask2(10.20×100) → 均价10.10 + 滑点。"""
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("10.00"), Decimal("10.20"), Decimal("10.30"), Decimal("10.40"), Decimal("10.50")),
            bid_price=(Decimal("9.90"),) * 5,
            ask_vol=(Decimal("100"), Decimal("100"), Decimal("300"), Decimal("400"), Decimal("500")),
            bid_vol=(Decimal("100"),) * 5,
            last_price=Decimal("10.00"),
        )
        logic = MatchingLogic()
        fill = logic.match_tick_order(_order("BUY", "200", order_type="TICK"), _tick(book))
        assert fill.filled is True
        assert fill.quantity == Decimal("200")
        assert fill.filled_quantity == Decimal("200")
        assert fill.price == Decimal("10.10101")
        assert fill.slippage_cost == Decimal("0.20200")
        assert fill.commission == Decimal("5.02020202")

    def test_sell_two_levels_weighted_average_golden(self):
        """SELL 200股: 消化 bid1(10.00×100)+bid2(9.90×100) → 均价9.95 - 滑点。"""
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("10.10"),) * 5,
            bid_price=(Decimal("10.00"), Decimal("9.90"), Decimal("9.80"), Decimal("9.70"), Decimal("9.60")),
            ask_vol=(Decimal("100"),) * 5,
            bid_vol=(Decimal("100"), Decimal("100"), Decimal("300"), Decimal("400"), Decimal("500")),
            last_price=Decimal("10.00"),
        )
        logic = MatchingLogic()
        fill = logic.match_tick_order(_order("SELL", "200", order_type="TICK"), _tick(book))
        assert fill.filled is True
        assert fill.price == Decimal("9.949005")
        assert fill.commission == Decimal("6.01479851")

    def test_partial_fill_when_exceeding_liquidity(self):
        """流动性约束: 订单10000股 > 5档总卖量1500 → 部分成交1500, filled=False。"""
        logic = MatchingLogic()
        fill = logic.match_tick_order(_order("BUY", "10000", order_type="TICK"), _tick(_book()))
        assert fill.filled is False
        assert fill.quantity == Decimal("1500")
        assert fill.filled_quantity == Decimal("1500")
        assert fill.price > Decimal("10.00")

    def test_zero_liquidity_unfilled(self):
        """全档零量 → 不成交。"""
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("10.00"),) * 5,
            bid_price=(Decimal("9.90"),) * 5,
            ask_vol=(Decimal("0"),) * 5,
            bid_vol=(Decimal("0"),) * 5,
            last_price=Decimal("10.00"),
        )
        logic = MatchingLogic()
        fill = logic.match_tick_order(_order("BUY", "100", order_type="TICK"), _tick(book))
        assert fill.filled is False
        assert fill.quantity == Decimal("0")

    def test_skip_zero_price_levels(self):
        """逐档消化跳过 price<=0 或 vol<=0 的档位。"""
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("0"), Decimal("10.00"), Decimal("10.10"), Decimal("10.20"), Decimal("10.30")),
            bid_price=(Decimal("9.90"),) * 5,
            ask_vol=(Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100")),
            bid_vol=(Decimal("100"),) * 5,
            last_price=Decimal("10.00"),
        )
        logic = MatchingLogic()
        fill = logic.match_tick_order(_order("BUY", "100", order_type="TICK"), _tick(book))
        assert fill.filled is True
        assert fill.quantity == Decimal("100")
        # 第一档 price=0 被跳过, 从 10.00 档成交
        assert fill.price == Decimal("10.001")

    def test_limit_tick_delegates_to_limit_matching(self):
        """限价Tick单 → 委托限价单规则撮合。"""
        logic = MatchingLogic()
        fill = logic.match_tick_order(
            _order("BUY", "100", order_type="TICK", limit_price="10.05"),
            _tick(_book(ask1="10.00")),
        )
        assert fill.filled is True
        assert fill.price == Decimal("10.001")

    def test_limit_tick_unfilled(self):
        logic = MatchingLogic()
        fill = logic.match_tick_order(
            _order("BUY", "100", order_type="TICK", limit_price="9.90"),
            _tick(_book(ask1="10.00")),
        )
        assert fill.filled is False

    def test_incomplete_order_book_raises(self):
        """5档不完整(3档) → MatchingLogicError。"""
        book = OrderBookSnapshot(
            symbol=SYM,
            ask_price=(Decimal("10.00"),) * 3,
            bid_price=(Decimal("9.90"),) * 3,
            ask_vol=(Decimal("100"),) * 3,
            bid_vol=(Decimal("100"),) * 3,
            last_price=Decimal("10.00"),
        )
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_tick_order(_order("BUY", "100", order_type="TICK"), _tick(book))

    def test_invalid_side_raises(self):
        logic = MatchingLogic()
        with pytest.raises(MatchingLogicError):
            logic.match_tick_order(_order("HOLD", "100", order_type="TICK"), _tick(_book()))


class TestPureFunctionSemantics:
    """纯函数式语义（回测=实盘一致性根基）。"""

    def test_same_input_same_output(self):
        logic = MatchingLogic()
        order = _order("BUY", "100")
        book = _book()
        fill1 = logic.match_market_order(order, book)
        fill2 = logic.match_market_order(order, book)
        assert fill1 == fill2

    def test_no_mutation_of_inputs(self):
        logic = MatchingLogic()
        order = _order("BUY", "100")
        book = _book()
        ask_before = book.ask_price
        logic.match_market_order(order, book)
        assert book.ask_price == ask_before
        assert order.quantity == Decimal("100")

    def test_value_objects_frozen(self):
        order = _order("BUY", "100")
        with pytest.raises(FrozenInstanceError):
            order.quantity = Decimal("200")  # type: ignore[misc]
        fill = MatchingFill(
            symbol=SYM,
            side="BUY",
            quantity=Decimal("100"),
            price=Decimal("10.00"),
            commission=Decimal("5"),
            slippage_cost=Decimal("0.1"),
        )
        with pytest.raises(FrozenInstanceError):
            fill.price = Decimal("11.00")  # type: ignore[misc]

    def test_config_not_shared_between_instances(self):
        custom = MatchingConfig(slippage_bps=Decimal("10"))
        logic_custom = MatchingLogic(custom)
        logic_default = MatchingLogic()
        fill_c = logic_custom.match_market_order(_order("BUY", "100"), _book(ask1="10.00"))
        fill_d = logic_default.match_market_order(_order("BUY", "100"), _book(ask1="10.00"))
        assert fill_c.price == Decimal("10.01")
        assert fill_d.price == Decimal("10.001")


class TestMatchingFillTotalCost:
    """MatchingFill.total_cost 口径（price 已含滑点，不得双计）。"""

    def test_buy_total_cost(self):
        fill = MatchingFill(
            symbol=SYM,
            side="BUY",
            quantity=Decimal("100"),
            price=Decimal("10.001"),
            commission=Decimal("5.010001"),
            slippage_cost=Decimal("0.1"),
        )
        assert fill.total_cost == Decimal("1005.110001")

    def test_sell_total_cost(self):
        fill = MatchingFill(
            symbol=SYM,
            side="SELL",
            quantity=Decimal("100"),
            price=Decimal("9.989001"),
            commission=Decimal("5.509439051"),
            slippage_cost=Decimal("0.0999"),
        )
        assert fill.total_cost == Decimal("993.390660949")


class TestTickSnapshotConversion:
    """TickSnapshot.to_order_book 转换。"""

    def test_to_order_book_fields(self):
        book = _book()
        tick = _tick(book)
        converted = tick.to_order_book()
        assert converted.symbol == tick.symbol
        assert converted.ask_price == tick.ask_price
        assert converted.bid_price == tick.bid_price
        assert converted.ask_vol == tick.ask_vol
        assert converted.bid_vol == tick.bid_vol
        assert converted.last_price == tick.last_price
