# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_pricing_policy.py
# [TTL] task_bound
# 对应: src/zephyr/ex_core/pricing_policy.py
# 覆盖: gap 9 挂单价算法（被动档/主动档/涨停跌停/提1tick/盘口回退）
"""PricingPolicy 单元测试（40_execution_broker §决策⑭ gap 9）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.pricing_policy import (
    PricingContext,
    PricingPolicy,
    PricingPolicyError,
    PricingTier,
    compute_quote_price,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

# ───────────────────────── 被动档 PASSIVE ─────────────────────────


class TestPassiveTier:
    """被动档挂单（默认档位）。"""

    def test_buy_uses_bid1(self):
        """被动买单 → 买一价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.PASSIVE)

        assert decision.price == Decimal("10.04")
        assert decision.tier is PricingTier.PASSIVE
        assert decision.fallback_used is False

    def test_sell_uses_ask1(self):
        """被动卖单 → 卖一价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.PASSIVE)

        assert decision.price == Decimal("10.05")
        assert decision.tier is PricingTier.PASSIVE
        assert decision.fallback_used is False

    def test_buy_no_bid1_fallback_last(self):
        """买单无买一价 → 回退最新成交价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=None,
            last_price=Decimal("10.045"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.PASSIVE)

        # Decimal quantize 默认 ROUND_HALF_EVEN，10.045→10.04（4是偶数）
        assert decision.price == Decimal("10.04")
        assert decision.fallback_used is True

    def test_buy_no_bid1_no_last_fallback_prev_close(self):
        """买单无买一价无最新价 → 回退前收盘价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=None,
            last_price=None,
            prev_close=Decimal("10.00"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.PASSIVE)

        assert decision.price == Decimal("10.00")
        assert decision.fallback_used is True

    def test_no_any_price_raises(self):
        """无任何可用价格 → 抛 PricingPolicyError。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=None,
            bid1=None,
            last_price=None,
            prev_close=None,
        )
        with pytest.raises(PricingPolicyError):
            PricingPolicy().decide(ctx, PricingTier.PASSIVE)

    def test_default_tier_is_passive(self):
        """默认 tier 参数 = PASSIVE。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx)  # 不传 tier

        assert decision.tier is PricingTier.PASSIVE
        assert decision.price == Decimal("10.04")


# ───────────────────────── 主动档 ACTIVE ─────────────────────────


class TestActiveTier:
    """主动档挂单（Make-or-Take 兜底）。"""

    def test_buy_uses_ask1(self):
        """主动买单 → 卖一价（跨价吃单）。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ACTIVE)

        assert decision.price == Decimal("10.05")
        assert decision.tier is PricingTier.ACTIVE
        assert decision.fallback_used is False

    def test_sell_uses_bid1(self):
        """主动卖单 → 买一价（跨价吃单）。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ACTIVE)

        assert decision.price == Decimal("10.04")
        assert decision.tier is PricingTier.ACTIVE

    def test_buy_no_ask1_fallback_last(self):
        """主动买单无卖一 → 回退最新价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=None,
            bid1=Decimal("10.04"),
            last_price=Decimal("10.045"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ACTIVE)

        assert decision.fallback_used is True

    def test_buy_no_ask1_no_last_no_prev_uses_own_plus_tick(self):
        """主动买单无对手价无 last 无 prev → 用己方价+1tick 兜底。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=None,
            bid1=Decimal("10.04"),
            last_price=None,
            prev_close=None,
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ACTIVE)

        # 己方 bid1 + 1tick = 10.04 + 0.01 = 10.05
        assert decision.price == Decimal("10.05")
        assert decision.fallback_used is True

    def test_sell_no_bid1_no_last_no_prev_uses_own_minus_tick(self):
        """主动卖单无对手价无 last 无 prev → 用己方价-1tick 兜底。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            ask1=Decimal("10.05"),
            bid1=None,
            last_price=None,
            prev_close=None,
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ACTIVE)

        # 己方 ask1 - 1tick = 10.05 - 0.01 = 10.04
        assert decision.price == Decimal("10.04")
        assert decision.fallback_used is True


# ───────────────────────── 涨停跌停 ─────────────────────────


class TestLimitUpLimitDown:
    """涨停板卖单 / 跌停板买单。"""

    def test_limit_up_sell_uses_provided_price(self):
        """涨停板卖单用传入的涨停价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            prev_close=Decimal("10.00"),
            limit_up_price=Decimal("11.00"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.LIMIT_UP_SELL)

        assert decision.price == Decimal("11.00")
        assert decision.tier is PricingTier.LIMIT_UP_SELL
        assert decision.fallback_used is False

    def test_limit_up_sell_estimate_from_prev_close(self):
        """涨停板卖单无涨停价 → 用 prev_close×1.1 估算。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            prev_close=Decimal("10.00"),
            limit_up_price=None,
        )
        decision = PricingPolicy().decide(ctx, PricingTier.LIMIT_UP_SELL)

        assert decision.price == Decimal("11.00")
        assert decision.fallback_used is True

    def test_limit_up_sell_no_data_raises(self):
        """涨停板卖单无涨停价无前收盘 → 抛错。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            prev_close=None,
            limit_up_price=None,
        )
        with pytest.raises(PricingPolicyError):
            PricingPolicy().decide(ctx, PricingTier.LIMIT_UP_SELL)

    def test_limit_down_buy_uses_provided_price(self):
        """跌停板买单用传入的跌停价。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            prev_close=Decimal("10.00"),
            limit_down_price=Decimal("9.00"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.LIMIT_DOWN_BUY)

        assert decision.price == Decimal("9.00")
        assert decision.tier is PricingTier.LIMIT_DOWN_BUY
        assert decision.fallback_used is False

    def test_limit_down_buy_estimate_from_prev_close(self):
        """跌停板买单无跌停价 → 用 prev_close×0.9 估算。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            prev_close=Decimal("10.00"),
            limit_down_price=None,
        )
        decision = PricingPolicy().decide(ctx, PricingTier.LIMIT_DOWN_BUY)

        assert decision.price == Decimal("9.00")
        assert decision.fallback_used is True


# ───────────────────────── 提1tick中间档 ─────────────────────────


class TestOneTickInside:
    """提1tick中间档（Phase 1.5 候选）。"""

    def test_buy_one_tick_above_bid1(self):
        """买单提1tick → 买一+1tick。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ONE_TICK_INSIDE)

        assert decision.price == Decimal("10.05")  # 10.04 + 0.01
        assert decision.tier is PricingTier.ONE_TICK_INSIDE

    def test_sell_one_tick_below_ask1(self):
        """卖单提1tick → 卖一-1tick。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.SELL,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ONE_TICK_INSIDE)

        assert decision.price == Decimal("10.04")  # 10.05 - 0.01
        assert decision.tier is PricingTier.ONE_TICK_INSIDE

    def test_no_own_price_fallback(self):
        """无己方盘口 → 回退到被动档逻辑。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=None,
            last_price=Decimal("10.045"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.ONE_TICK_INSIDE)

        assert decision.tier is PricingTier.ONE_TICK_INSIDE
        assert decision.fallback_used is True


# ───────────────────────── 函数式入口 ─────────────────────────


class TestComputeQuotePrice:
    """compute_quote_price 函数式入口。"""

    def test_function_interface(self):
        """函数式入口与类方法一致。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        d1 = PricingPolicy().decide(ctx, PricingTier.PASSIVE)
        d2 = compute_quote_price(ctx, PricingTier.PASSIVE)

        assert d1.price == d2.price
        assert d1.tier == d2.tier

    def test_default_tier_passive(self):
        """默认 PASSIVE 档。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.05"),
            bid1=Decimal("10.04"),
        )
        d = compute_quote_price(ctx)  # 不传 tier

        assert d.tier is PricingTier.PASSIVE
        assert d.price == Decimal("10.04")


# ───────────────────────── 价格量化 ─────────────────────────


class TestPriceQuantization:
    """挂单价量化到 0.01 tick。"""

    def test_price_rounded_to_tick(self):
        """传入非 tick 整数倍的价格 → 量化到 tick。"""
        ctx = PricingContext(
            symbol="600000.SH",
            side=OrderSide.BUY,
            ask1=Decimal("10.055"),  # 非法价格
            bid1=Decimal("10.045"),
        )
        decision = PricingPolicy().decide(ctx, PricingTier.PASSIVE)

        # 10.045 quantize 到 0.01 = 10.04（ROUND_HALF_EVEN）
        assert decision.price == Decimal("10.04")
