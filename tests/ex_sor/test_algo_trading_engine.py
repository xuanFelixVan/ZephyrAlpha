# [BLUEPRINT] MOD-XS-005 | docs/03_modules/_domain-ex_sor/algo_trading_engine/blueprint.md | §
# [TTL] permanent
"""AlgoTradingEngine 单元测试 (MOD-XS-005)。6 种算法 + 注册表 + 参数优化器。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.core.algo_trading_engine import (
    LOT_SIZE,
    MAX_ADV_FRACTION,
    MAX_PARTICIPATION_RATE,
    AggressiveLiquidityTakingStrategy,
    AlgoError,
    AlgoExecutionPlan,
    AlgoParamOptimizer,
    AlgoParams,
    AlgoSlice,
    AlgoTradingEngine,
    AlgoType,
    IcebergStrategy,
    ImplementationShortfallStrategy,
    InvalidAlgoParamsError,
    MarketContext,
    OrderTooLargeError,
    PovStrategy,
    PriceStrategy,
    TwapStrategy,
    UnknownAlgoError,
    VwapStrategy,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_order(
    qty: Decimal = Decimal("1000"),
    order_id: str = "ORD-001",
    side: OrderSide = OrderSide.BUY,
) -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"IDEMP-{order_id}",
        order_type=OrderType.LIMIT,
        quantity=qty,
        side=side,
        strategy_id="STRAT-1",
        symbol="000001.SZ",
        limit_price=Decimal("10.50"),
    )


def make_ctx(
    adv: Decimal = Decimal("1000000"),
    bid: Decimal | None = Decimal("10.49"),
    ask: Decimal | None = Decimal("10.51"),
) -> MarketContext:
    return MarketContext(
        symbol="000001.SZ",
        last_price=Decimal("10.50"),
        adv=adv,
        bid_price=bid,
        ask_price=ask,
    )


def make_params(
    algo: AlgoType = AlgoType.TWAP,
    **kw,
) -> AlgoParams:
    defaults = dict(
        participation_rate=Decimal("0.05"),
        time_horizon_minutes=30,
        max_slice_count=10,
        min_slice_quantity=LOT_SIZE,
        urgency=Decimal("0.5"),
    )
    if algo == AlgoType.ICEBERG and "display_quantity" not in kw:
        defaults["display_quantity"] = Decimal("200")
    defaults.update(kw)
    return AlgoParams(algo_type=algo, **defaults)


# ── AlgoType / PriceStrategy 枚举 ────────────────────────────────────────────


def test_algo_type_values():
    assert AlgoType.TWAP.value == "TWAP"
    assert AlgoType.VWAP.value == "VWAP"
    assert AlgoType.ICEBERG.value == "ICEBERG"
    assert AlgoType.POV.value == "POV"
    assert AlgoType.IS.value == "IS"
    assert AlgoType.ALT.value == "ALT"
    assert str(AlgoType.TWAP) == "TWAP"


def test_price_strategy_values():
    assert PriceStrategy.MARKET.value == "MARKET"
    assert PriceStrategy.AGGRESSIVE.value == "AGGRESSIVE"
    assert len(PriceStrategy) == 5


# ── MarketContext 校验 ───────────────────────────────────────────────────────


def test_market_context_valid():
    ctx = make_ctx()
    assert ctx.symbol == "000001.SZ"
    assert ctx.last_price == Decimal("10.50")


def test_market_context_empty_symbol():
    with pytest.raises(AlgoError, match="symbol"):
        MarketContext(symbol="", last_price=Decimal("10"), adv=Decimal("1000"))


def test_market_context_zero_price():
    with pytest.raises(AlgoError, match="last_price"):
        MarketContext(symbol="X", last_price=Decimal("0"), adv=Decimal("1000"))


def test_market_context_zero_adv():
    with pytest.raises(AlgoError, match="adv"):
        MarketContext(symbol="X", last_price=Decimal("10"), adv=Decimal("0"))


def test_market_context_bad_volume_profile():
    with pytest.raises(AlgoError, match="volume_profile"):
        MarketContext(
            symbol="X",
            last_price=Decimal("10"),
            adv=Decimal("1000"),
            volume_profile={1: 0.5, 2: 0.3},  # sum=0.8
        )


def test_market_context_default_volume_profile():
    ctx = make_ctx()
    assert sum(ctx.volume_profile.values()) == pytest.approx(1.0)


# ── AlgoParams 校验 ─────────────────────────────────────────────────────────


def test_params_valid():
    p = make_params()
    assert p.algo_type == AlgoType.TWAP
    assert p.participation_rate == Decimal("0.05")


def test_params_participation_zero():
    with pytest.raises(InvalidAlgoParamsError, match="participation_rate"):
        AlgoParams(algo_type=AlgoType.POV, participation_rate=Decimal("0"))


def test_params_participation_over_limit():
    with pytest.raises(InvalidAlgoParamsError, match="participation_rate"):
        AlgoParams(algo_type=AlgoType.POV, participation_rate=Decimal("0.10"))


def test_params_participation_exact_limit_ok():
    # 恰好 5% 应允许
    p = AlgoParams(algo_type=AlgoType.POV, participation_rate=MAX_PARTICIPATION_RATE)
    assert p.participation_rate == MAX_PARTICIPATION_RATE


def test_params_zero_horizon():
    with pytest.raises(InvalidAlgoParamsError, match="time_horizon"):
        AlgoParams(algo_type=AlgoType.TWAP, time_horizon_minutes=0)


def test_params_zero_slice_count():
    with pytest.raises(InvalidAlgoParamsError, match="max_slice"):
        AlgoParams(algo_type=AlgoType.TWAP, max_slice_count=0)


def test_params_urgency_out_of_range():
    with pytest.raises(InvalidAlgoParamsError, match="urgency"):
        AlgoParams(algo_type=AlgoType.IS, urgency=Decimal("1.5"))


def test_params_iceberg_requires_display():
    with pytest.raises(InvalidAlgoParamsError, match="display_quantity"):
        AlgoParams(algo_type=AlgoType.ICEBERG, display_quantity=None)


def test_params_iceberg_zero_display():
    with pytest.raises(InvalidAlgoParamsError, match="display_quantity"):
        AlgoParams(algo_type=AlgoType.ICEBERG, display_quantity=Decimal("0"))


def test_params_min_slice_zero():
    with pytest.raises(InvalidAlgoParamsError, match="min_slice"):
        AlgoParams(algo_type=AlgoType.TWAP, min_slice_quantity=Decimal("0"))


# ── 注册表 ──────────────────────────────────────────────────────────────────


def test_engine_default_registry():
    eng = AlgoTradingEngine()
    types = eng.get_algo_types()
    assert set(types) == {
        AlgoType.TWAP,
        AlgoType.VWAP,
        AlgoType.ICEBERG,
        AlgoType.POV,
        AlgoType.IS,
        AlgoType.ALT,
    }


def test_engine_is_registered():
    eng = AlgoTradingEngine()
    assert eng.is_registered(AlgoType.TWAP) is True
    eng.unregister(AlgoType.TWAP)
    assert eng.is_registered(AlgoType.TWAP) is False


def test_engine_get_strategy():
    eng = AlgoTradingEngine()
    s = eng.get_strategy(AlgoType.TWAP)
    assert isinstance(s, TwapStrategy)


def test_engine_get_unknown_strategy():
    eng = AlgoTradingEngine()
    # 所有 AlgoType 都已注册, 无法直接构造未知 → 用 unregister 后查询
    eng.unregister(AlgoType.ALT)
    with pytest.raises(UnknownAlgoError, match="未知算法"):
        eng.get_strategy(AlgoType.ALT)


def test_engine_unregister_unknown():
    eng = AlgoTradingEngine()
    eng.unregister(AlgoType.ALT)
    with pytest.raises(UnknownAlgoError):
        eng.unregister(AlgoType.ALT)


def test_engine_register_custom():
    eng = AlgoTradingEngine()
    eng.unregister(AlgoType.TWAP)
    eng.register(TwapStrategy())
    assert eng.is_registered(AlgoType.TWAP)


def test_engine_describe_algo():
    eng = AlgoTradingEngine()
    desc = eng.describe_algo(AlgoType.IS)
    assert "Implementation Shortfall" in desc


def test_engine_describe_unknown():
    eng = AlgoTradingEngine()
    eng.unregister(AlgoType.ALT)
    with pytest.raises(UnknownAlgoError):
        eng.describe_algo(AlgoType.ALT)


# ── 守恒不变量 (核心) ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "algo",
    [
        AlgoType.TWAP,
        AlgoType.VWAP,
        AlgoType.ICEBERG,
        AlgoType.POV,
        AlgoType.IS,
        AlgoType.ALT,
    ],
)
def test_generate_plan_conservation(algo):
    """所有算法: 切片数量和 == 订单总量 (Decimal 守恒)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("1000"))
    ctx = make_ctx()
    params = make_params(algo)
    plan = eng.generate_plan(order, params, ctx, now=NOW)
    sliced = sum((s.quantity for s in plan.slices), Decimal("0"))
    assert sliced == order.quantity
    assert plan.total_quantity == order.quantity


@pytest.mark.parametrize(
    "qty",
    [
        Decimal("100"),
        Decimal("500"),
        Decimal("1234"),
        Decimal("10000"),
    ],
)
def test_twap_conservation_various_qty(qty):
    eng = AlgoTradingEngine()
    order = make_order(qty)
    plan = eng.generate_plan(order, make_params(AlgoType.TWAP), make_ctx(), now=NOW)
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == qty


# ── TWAP 策略 ───────────────────────────────────────────────────────────────


def test_twap_even_split():
    eng = AlgoTradingEngine()
    order = make_order(Decimal("1000"))
    plan = eng.generate_plan(order, make_params(AlgoType.TWAP, max_slice_count=5), make_ctx(), now=NOW)
    assert len(plan.slices) == 5
    # 1000/5 = 200 each
    for s in plan.slices:
        assert s.quantity == Decimal("200")
    assert all(s.price_strategy == PriceStrategy.PASSIVE for s in plan.slices)


def test_twap_reference_price_mid():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(make_order(), make_params(AlgoType.TWAP), make_ctx(), now=NOW)
    # mid = (10.49+10.51)/2 = 10.50
    assert plan.slices[0].reference_price == Decimal("10.50")


def test_twap_no_bid_ask_uses_last():
    eng = AlgoTradingEngine()
    ctx = MarketContext(symbol="X", last_price=Decimal("10.50"), adv=Decimal("1e6"))
    plan = eng.generate_plan(make_order(), make_params(AlgoType.TWAP), ctx, now=NOW)
    assert plan.slices[0].reference_price == Decimal("10.50")


def test_twap_lot_alignment():
    """非整除 lot 时, 余数补到末片, 守恒保持 (末片可能携带亚 lot 余数)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("350"))  # /3 = 116.67 → 100 + 100 + 150
    plan = eng.generate_plan(order, make_params(AlgoType.TWAP, max_slice_count=3), make_ctx(), now=NOW)
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == Decimal("350")
    # 前 n-1 片对齐 100 lot (末片携带余数, 保持守恒)
    for s in plan.slices[:-1]:
        assert s.quantity % LOT_SIZE == 0


# ── VWAP 策略 ───────────────────────────────────────────────────────────────


def test_vwap_slice_count_equals_periods():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(make_order(), make_params(AlgoType.VWAP), make_ctx(), now=NOW)
    # 默认 4 时段 → 4 切片
    assert len(plan.slices) == 4


def test_vwap_weights_by_profile():
    """VWAP 切片按占比降序排列 (最大占比时段为首片)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("10000"))
    plan = eng.generate_plan(order, make_params(AlgoType.VWAP), make_ctx(), now=NOW)
    # 按占比降序: 尾盘 45% 为首片, 午盘 10% 为末片
    assert plan.slices[0].quantity > plan.slices[-1].quantity
    # 首片 = 45% × 10000 = 4500
    assert plan.slices[0].quantity == Decimal("4500")


def test_vwap_conservation_with_odd_qty():
    eng = AlgoTradingEngine()
    order = make_order(Decimal("333"))
    plan = eng.generate_plan(order, make_params(AlgoType.VWAP), make_ctx(), now=NOW)
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == Decimal("333")


# ── ICEBERG 策略 ────────────────────────────────────────────────────────────


def test_iceberg_display_quantity_slices():
    eng = AlgoTradingEngine()
    order = make_order(Decimal("1000"))
    plan = eng.generate_plan(
        order,
        make_params(AlgoType.ICEBERG, display_quantity=Decimal("200")),
        make_ctx(),
        now=NOW,
    )
    # 1000/200 = 5 片, 每片 200
    assert len(plan.slices) == 5
    for s in plan.slices[:-1]:
        assert s.quantity == Decimal("200")


def test_iceberg_last_slice_remainder():
    eng = AlgoTradingEngine()
    order = make_order(Decimal("750"))
    plan = eng.generate_plan(
        order,
        make_params(AlgoType.ICEBERG, display_quantity=Decimal("200")),
        make_ctx(),
        now=NOW,
    )
    # 200,200,200,150
    assert plan.slices[-1].quantity == Decimal("150")
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == Decimal("750")


def test_iceberg_max_slice_capped():
    """max_slice_count 用尽后余量补末片 (守恒)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("1000"))
    plan = eng.generate_plan(
        order,
        make_params(AlgoType.ICEBERG, display_quantity=Decimal("100"), max_slice_count=3),
        make_ctx(),
        now=NOW,
    )
    assert len(plan.slices) == 3
    # 100+100+800 (末片补余)
    assert plan.slices[-1].quantity == Decimal("800")
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == Decimal("1000")


# ── POV 策略 ────────────────────────────────────────────────────────────────


def test_pov_generates_slices():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(
        make_order(Decimal("500")),
        make_params(AlgoType.POV, participation_rate=Decimal("0.05")),
        make_ctx(),
        now=NOW,
    )
    assert len(plan.slices) >= 1
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == Decimal("500")


def test_pov_participation_in_rationale():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(
        make_order(Decimal("500")),
        make_params(AlgoType.POV),
        make_ctx(),
        now=NOW,
    )
    assert "POV" in plan.slices[0].rationale


# ── IS 策略 ─────────────────────────────────────────────────────────────────


def test_is_zero_urgency_is_twap_like():
    """urgency=0 → 均匀 (类似 TWAP)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("1000"))
    plan = eng.generate_plan(
        order,
        make_params(AlgoType.IS, urgency=Decimal("0"), max_slice_count=5),
        make_ctx(),
        now=NOW,
    )
    quantities = [s.quantity for s in plan.slices]
    # 均匀: 极差应很小
    assert max(quantities) - min(quantities) <= Decimal("1")


def test_is_high_urgency_front_loaded():
    """urgency→1 → 前置加载 (首片最大)。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("10000"))
    plan = eng.generate_plan(
        order,
        make_params(AlgoType.IS, urgency=Decimal("0.95"), max_slice_count=5),
        make_ctx(),
        now=NOW,
    )
    # 首片应明显大于末片
    assert plan.slices[0].quantity > plan.slices[-1].quantity


def test_is_mid_price_strategy():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(
        make_order(),
        make_params(AlgoType.IS),
        make_ctx(),
        now=NOW,
    )
    assert all(s.price_strategy == PriceStrategy.MID for s in plan.slices)


# ── ALT 策略 ────────────────────────────────────────────────────────────────


def test_alt_few_slices():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(
        make_order(Decimal("1000")),
        make_params(AlgoType.ALT, max_slice_count=5),
        make_ctx(),
        now=NOW,
    )
    # ALT 上限 3 片
    assert len(plan.slices) <= 3


def test_alt_aggressive_price_buy_uses_ask():
    eng = AlgoTradingEngine()
    order = make_order(side=OrderSide.BUY)
    plan = eng.generate_plan(order, make_params(AlgoType.ALT), make_ctx(), now=NOW)
    # BUY → ask = 10.51
    assert plan.slices[0].reference_price == Decimal("10.51")
    assert plan.slices[0].price_strategy == PriceStrategy.AGGRESSIVE


def test_alt_aggressive_price_sell_uses_bid():
    eng = AlgoTradingEngine()
    order = make_order(side=OrderSide.SELL)
    plan = eng.generate_plan(order, make_params(AlgoType.ALT), make_ctx(), now=NOW)
    # SELL → bid = 10.49
    assert plan.slices[0].reference_price == Decimal("10.49")


def test_alt_no_bid_ask_uses_last():
    eng = AlgoTradingEngine()
    ctx = MarketContext(symbol="X", last_price=Decimal("10.50"), adv=Decimal("1e6"))
    plan = eng.generate_plan(make_order(), make_params(AlgoType.ALT), ctx, now=NOW)
    assert plan.slices[0].reference_price == Decimal("10.50")


# ── ADV 上限 (§13.1) ────────────────────────────────────────────────────────


def test_order_too_large_raises():
    """订单 > 15% ADV → OrderTooLargeError (§13.1)。"""
    eng = AlgoTradingEngine()
    # adv=1000, order=200 → 20% > 15%
    order = make_order(Decimal("200"))
    ctx = make_ctx(adv=Decimal("1000"))
    with pytest.raises(OrderTooLargeError, match="15% ADV"):
        eng.generate_plan(order, make_params(AlgoType.TWAP), ctx, now=NOW)


def test_order_at_adv_limit_ok():
    """恰好 15% ADV 应允许。"""
    eng = AlgoTradingEngine()
    order = make_order(Decimal("150"))
    ctx = make_ctx(adv=Decimal("1000"))
    plan = eng.generate_plan(order, make_params(AlgoType.TWAP), ctx, now=NOW)
    assert plan.total_quantity == Decimal("150")


# ── 执行计划 ────────────────────────────────────────────────────────────────


def test_plan_empty_slices_raises():
    with pytest.raises(AlgoError, match="切片不能为空"):
        AlgoExecutionPlan(
            order_id="X",
            algo_type=AlgoType.TWAP,
            params=make_params(),
            slices=[],
            total_quantity=Decimal("100"),
            created_at=NOW,
            estimated_participation=Decimal("0"),
        )


def test_plan_conservation_violation_raises():
    with pytest.raises(AlgoError, match="守恒"):
        AlgoExecutionPlan(
            order_id="X",
            algo_type=AlgoType.TWAP,
            params=make_params(),
            slices=[AlgoSlice(0, Decimal("50"), PriceStrategy.MARKET, None, "x")],
            total_quantity=Decimal("100"),  # 不等于 50
            created_at=NOW,
            estimated_participation=Decimal("0"),
        )


def test_plan_to_dict():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(make_order(), make_params(AlgoType.TWAP, max_slice_count=2), make_ctx(), now=NOW)
    d = plan.to_dict()
    assert d["order_id"] == "ORD-001"
    assert d["algo_type"] == "TWAP"
    assert d["slice_count"] == 2
    assert len(d["slices"]) == 2


def test_plan_estimated_participation():
    eng = AlgoTradingEngine()
    plan = eng.generate_plan(
        make_order(Decimal("1000")),
        make_params(AlgoType.TWAP, max_slice_count=5),
        make_ctx(adv=Decimal("100000")),
        now=NOW,
    )
    # max slice = 200, adv=100000 → 0.002
    assert plan.estimated_participation == pytest.approx(Decimal("0.002"))


# ── 参数校验 ────────────────────────────────────────────────────────────────


def test_validate_params_unknown_algo():
    eng = AlgoTradingEngine()
    eng.unregister(AlgoType.ALT)
    p = AlgoParams(algo_type=AlgoType.ALT, display_quantity=None)
    with pytest.raises(UnknownAlgoError):
        eng.validate_params(p)


def test_generate_plan_unknown_algo():
    eng = AlgoTradingEngine()
    eng.unregister(AlgoType.ALT)
    with pytest.raises(UnknownAlgoError):
        eng.generate_plan(make_order(), make_params(AlgoType.ALT), make_ctx(), now=NOW)


# ── 参数优化器 ──────────────────────────────────────────────────────────────


def test_optimizer_large_order_long_horizon():
    opt = AlgoParamOptimizer()
    order = make_order(Decimal("60000"))  # 6% ADV
    params = opt.optimize(order, AlgoType.VWAP, make_ctx())
    assert params.time_horizon_minutes == 60
    assert params.max_slice_count <= 20


def test_optimizer_small_order_short_horizon():
    opt = AlgoParamOptimizer()
    order = make_order(Decimal("100"))  # 0.01% ADV
    params = opt.optimize(order, AlgoType.TWAP, make_ctx())
    assert params.time_horizon_minutes == 15


def test_optimizer_medium_order():
    opt = AlgoParamOptimizer()
    order = make_order(Decimal("20000"))  # 2% ADV
    params = opt.optimize(order, AlgoType.IS, make_ctx())
    assert params.time_horizon_minutes == 30


def test_optimizer_participation_within_limit():
    opt = AlgoParamOptimizer()
    params = opt.optimize(make_order(Decimal("1000")), AlgoType.POV, make_ctx())
    assert params.participation_rate <= MAX_PARTICIPATION_RATE


def test_optimizer_iceberg_display_quantity():
    opt = AlgoParamOptimizer()
    order = make_order(Decimal("10000"))
    params = opt.optimize(order, AlgoType.ICEBERG, make_ctx())
    assert params.display_quantity is not None
    assert params.display_quantity > 0
    assert params.display_quantity % LOT_SIZE == 0


def test_optimizer_sets_price_limit_from_order():
    opt = AlgoParamOptimizer()
    order = make_order()
    params = opt.optimize(order, AlgoType.TWAP, make_ctx())
    assert params.price_limit == Decimal("10.50")


# ── 策略类 algo_type 属性 ────────────────────────────────────────────────────


def test_strategy_algo_type_attributes():
    assert TwapStrategy().algo_type == AlgoType.TWAP
    assert VwapStrategy().algo_type == AlgoType.VWAP
    assert IcebergStrategy().algo_type == AlgoType.ICEBERG
    assert PovStrategy().algo_type == AlgoType.POV
    assert ImplementationShortfallStrategy().algo_type == AlgoType.IS
    assert AggressiveLiquidityTakingStrategy().algo_type == AlgoType.ALT


# ── MAX 常量 ────────────────────────────────────────────────────────────────


def test_constants():
    assert Decimal("0.05") == MAX_PARTICIPATION_RATE
    assert Decimal("0.15") == MAX_ADV_FRACTION
    assert Decimal("100") == LOT_SIZE
