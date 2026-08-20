# [BLUEPRINT] MOD-L06-002 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_post_close_pricing
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 窗口硬校验; 价格规则(买≥收盘/卖≤收盘); 不可撤单+15:30作废; 北交所拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PostClosePricingError
# [TESTS] self
# [TTL] permanent
"""盘后固定价格交易通道测试（40 号 §6.1 gap 16，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from datetime import UTC, datetime, time
from decimal import Decimal

import pytest

from zephyr.ex_core.post_close_pricing import (
    PostClosePricingError,
    convert_to_post_close_order,
    is_in_post_close_window,
    is_post_close_eligible,
    validate_post_close_price,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order


def _order(
    side: OrderSide = OrderSide.BUY,
    limit: str | None = None,
    symbol: str = "600000",
    qty: str = "100",
) -> Order:
    return Order(
        idempotency_key="idem-pc",
        order_id="o-pc",
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
        side=side,
        strategy_id="S1",
        symbol=symbol,
        limit_price=Decimal(limit) if limit is not None else None,
        created_at=datetime(2026, 8, 20, 14, 55, tzinfo=UTC),
    )


class TestWindow:
    def test_window_boundaries(self):
        assert is_in_post_close_window(time(15, 4, 59)) is False
        assert is_in_post_close_window(time(15, 5, 0)) is True
        assert is_in_post_close_window(time(15, 30, 0)) is True
        assert is_in_post_close_window(time(15, 30, 1)) is False

    def test_outside_window_rejected(self):
        with pytest.raises(PostClosePricingError):
            convert_to_post_close_order(_order(), Decimal("10.00"), time(15, 0))


class TestEligibility:
    @pytest.mark.parametrize("symbol", ["600000", "000001", "300750", "688981", "510300", "159915"])
    def test_ashare_etf_eligible(self, symbol: str):
        assert is_post_close_eligible(symbol) is True

    @pytest.mark.parametrize("symbol", ["430047", "830799", "920001"])
    def test_bse_not_eligible(self, symbol: str):
        assert is_post_close_eligible(symbol) is False

    def test_bse_order_rejected(self):
        with pytest.raises(PostClosePricingError):
            convert_to_post_close_order(_order(symbol="830799"), Decimal("10.00"), time(15, 10))


class TestPriceRules:
    def test_buy_limit_below_close_rejected(self):
        with pytest.raises(PostClosePricingError):
            validate_post_close_price(OrderSide.BUY, Decimal("9.99"), Decimal("10.00"))

    def test_buy_limit_at_close_ok(self):
        validate_post_close_price(OrderSide.BUY, Decimal("10.00"), Decimal("10.00"))

    def test_sell_limit_above_close_rejected(self):
        with pytest.raises(PostClosePricingError):
            validate_post_close_price(OrderSide.SELL, Decimal("10.01"), Decimal("10.00"))

    def test_sell_limit_at_close_ok(self):
        validate_post_close_price(OrderSide.SELL, Decimal("10.00"), Decimal("10.00"))

    def test_non_positive_prices_rejected(self):
        with pytest.raises(PostClosePricingError):
            validate_post_close_price(OrderSide.BUY, Decimal("10.00"), Decimal("0"))
        with pytest.raises(PostClosePricingError):
            validate_post_close_price(OrderSide.BUY, Decimal("-1"), Decimal("10.00"))


class TestConversion:
    def test_default_limit_equals_close(self):
        spec = convert_to_post_close_order(_order(limit=None), Decimal("10.00"), time(15, 10))
        assert spec.limit_price == Decimal("10.00")
        assert spec.close_price == Decimal("10.00")

    def test_spec_invariants(self):
        spec = convert_to_post_close_order(_order(), Decimal("10.00"), time(15, 20))
        assert spec.channel == "post_close_fixed_price"
        assert spec.cancellable is False  # 15:05 后不可撤单
        assert spec.auto_expire_at == time(15, 30)  # 未成交自动作废
        assert spec.order_id == "o-pc"
        assert spec.side == "BUY"

    def test_sell_spec(self):
        spec = convert_to_post_close_order(_order(side=OrderSide.SELL), Decimal("10.00"), time(15, 10))
        assert spec.side == "SELL"

    def test_zero_quantity_rejected(self):
        with pytest.raises(PostClosePricingError):
            convert_to_post_close_order(_order(qty="0"), Decimal("10.00"), time(15, 10))

    def test_missing_order_rejected(self):
        with pytest.raises(PostClosePricingError):
            convert_to_post_close_order(None, Decimal("10.00"), time(15, 10))  # type: ignore[arg-type]
