# [BLUEPRINT] MOD-XS-011 | docs/03_modules/_domain-ex_sor/algo_execution_selector/blueprint.md | §
# [TTL] permanent
"""AlgoExecutionSelector 单元测试 (MOD-XS-011)。订单特征→评分→选算法 + 效果评估。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.core.algo_execution_selector import (
    AlgoEvaluationResult,
    AlgoExecutionSelector,
    AlgoScoreBreakdown,
    AlgoSelection,
    DefaultAlgoEvaluator,
    ExecutionOutcome,
    InvalidFeaturesError,
    NoAlgoAvailableError,
    OrderFeatures,
    SelectorError,
)
from zephyr.ex_sor.core.algo_trading_engine import AlgoTradingEngine, AlgoType, MarketContext
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_order(
    qty: Decimal = Decimal("1000"),
    side: OrderSide = OrderSide.BUY,
    order_id: str = "ORD-001",
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
    bid: Decimal = Decimal("10.49"),
    ask: Decimal = Decimal("10.51"),
    last: Decimal = Decimal("10.50"),
) -> MarketContext:
    return MarketContext(
        symbol="000001.SZ",
        last_price=last,
        adv=adv,
        bid_price=bid,
        ask_price=ask,
    )


def make_selector() -> AlgoExecutionSelector:
    return AlgoExecutionSelector(AlgoTradingEngine())


# ── OrderFeatures ────────────────────────────────────────────────────────────


def test_features_from_order():
    ctx = make_ctx()
    f = OrderFeatures.from_order(make_order(Decimal("5000")), ctx, Decimal("0.3"))
    assert f.order_id == "ORD-001"
    assert f.adv_fraction == Decimal("0.005")
    assert f.urgency == Decimal("0.3")
    assert f.side == OrderSide.BUY
    # spread = (10.51-10.49)/10.50 * 10000 = 1.9047...
    assert f.spread_bps > 0


def test_features_spread_unknown_when_no_bid_ask():
    ctx = MarketContext(symbol="X", last_price=Decimal("10"), adv=Decimal("1e6"))
    f = OrderFeatures.from_order(make_order(), ctx)
    assert f.spread_bps < 0  # 未知


def test_features_invalid_urgency():
    with pytest.raises(InvalidFeaturesError, match="urgency"):
        OrderFeatures(
            order_id="X",
            symbol="S",
            side=OrderSide.BUY,
            quantity=Decimal("100"),
            adv_fraction=Decimal("0.01"),
            urgency=Decimal("1.5"),
        )


def test_features_invalid_adv_fraction():
    with pytest.raises(InvalidFeaturesError, match="adv_fraction"):
        OrderFeatures(
            order_id="X",
            symbol="S",
            side=OrderSide.BUY,
            quantity=Decimal("100"),
            adv_fraction=Decimal("-0.1"),
            urgency=Decimal("0.5"),
        )


def test_features_invalid_quantity():
    with pytest.raises(InvalidFeaturesError, match="quantity"):
        OrderFeatures(
            order_id="X",
            symbol="S",
            side=OrderSide.BUY,
            quantity=Decimal("0"),
            adv_fraction=Decimal("0.01"),
            urgency=Decimal("0.5"),
        )


def test_features_empty_order_id():
    with pytest.raises(InvalidFeaturesError, match="order_id"):
        OrderFeatures(
            order_id="",
            symbol="S",
            side=OrderSide.BUY,
            quantity=Decimal("100"),
            adv_fraction=Decimal("0.01"),
            urgency=Decimal("0.5"),
        )


def test_features_zero_adv_unreachable():
    """MarketContext 自身已强制 adv>0, from_order 的 adv<=0 防御检查不可达 (验证守卫存在)。"""
    # MarketContext 构造即拒绝 adv=0
    with pytest.raises(Exception):
        MarketContext(symbol="X", last_price=Decimal("10"), adv=Decimal("0"))


# ── 选择 (核心场景) ──────────────────────────────────────────────────────────


def test_select_tiny_urgent_picks_alt():
    """小单 + 高紧急度 → ALT (激进吃单)。"""
    sel = make_selector()
    # 500 / 1e6 = 0.05% ADV (tiny), urgency 0.9
    s = sel.select(make_order(Decimal("500")), make_ctx(), urgency=Decimal("0.9"), now=NOW)
    assert s.selected_algo == AlgoType.ALT


def test_select_large_passive_picks_iceberg():
    """大单 (>5% ADV) + 低紧急度 → ICEBERG (隐藏意图)。"""
    sel = make_selector()
    # 60000 / 1e6 = 6% ADV (large)
    s = sel.select(make_order(Decimal("60000")), make_ctx(), urgency=Decimal("0.2"), now=NOW)
    assert s.selected_algo == AlgoType.ICEBERG


def test_select_medium_mid_picks_is_or_vwap():
    """中单 + 中紧急度 → IS 或 VWAP (风险均衡/跟随量)。"""
    sel = make_selector()
    # 20000 / 1e6 = 2% ADV (medium)
    s = sel.select(make_order(Decimal("20000")), make_ctx(), urgency=Decimal("0.5"), now=NOW)
    assert s.selected_algo in (AlgoType.IS, AlgoType.VWAP)


def test_select_tiny_passive_picks_twap():
    """小单 + 低紧急度 → TWAP (被动均匀)。"""
    sel = make_selector()
    # 500 / 1e6 = 0.05% ADV (tiny), urgency 0.1
    s = sel.select(make_order(Decimal("500")), make_ctx(), urgency=Decimal("0.1"), now=NOW)
    assert s.selected_algo == AlgoType.TWAP


def test_select_returns_selection_with_breakdowns():
    sel = make_selector()
    s = sel.select(make_order(), make_ctx(), now=NOW)
    assert isinstance(s, AlgoSelection)
    assert len(s.breakdowns) == 6  # 全部 6 算法评分
    assert s.selected_algo in s.scores


def test_select_scores_in_range():
    sel = make_selector()
    s = sel.select(make_order(), make_ctx(), now=NOW)
    for b in s.breakdowns:
        assert 0.0 <= b.size_score <= 1.0
        assert 0.0 <= b.urgency_score <= 1.0
        assert 0.0 <= b.liquidity_score <= 1.0
        assert 0.0 <= b.total <= 1.0


def test_select_picks_highest_score():
    sel = make_selector()
    s = sel.select(make_order(), make_ctx(), now=NOW)
    expected = max(s.scores.items(), key=lambda kv: kv[1])[0]
    assert s.selected_algo == expected


def test_select_records_audit_history():
    sel = make_selector()
    sel.select(make_order(order_id="O1"), make_ctx(), now=NOW)
    sel.select(make_order(order_id="O2"), make_ctx(), now=NOW)
    assert len(sel.selections) == 2
    history = sel.get_history("O1")
    assert len(history) == 1
    assert history[0].order_id == "O1"


def test_select_history_limit():
    sel = make_selector()
    for i in range(5):
        sel.select(make_order(order_id=f"O{i}"), make_ctx(), now=NOW)
    assert len(sel.get_history(limit=2)) == 2


def test_select_clear_history():
    sel = make_selector()
    sel.select(make_order(), make_ctx(), now=NOW)
    sel.clear_history()
    assert len(sel.selections) == 0


def test_select_to_dict():
    sel = make_selector()
    s = sel.select(make_order(), make_ctx(), now=NOW)
    d = s.to_dict()
    assert d["selected_algo"] == s.selected_algo.value
    assert "breakdowns" in d
    assert "features" in d
    assert d["features"]["symbol"] == "000001.SZ"


def test_select_reason_includes_scores():
    sel = make_selector()
    s = sel.select(make_order(), make_ctx(), now=NOW)
    assert "总分" in s.reason
    assert s.selected_algo.value in s.reason


# ── 无可用算法 ──────────────────────────────────────────────────────────────


def test_select_no_algos_available():
    eng = AlgoTradingEngine()
    # 注销全部
    for at in list(eng.get_algo_types()):
        eng.unregister(at)
    sel = AlgoExecutionSelector(eng)
    with pytest.raises(NoAlgoAvailableError, match="注册表为空"):
        sel.select(make_order(), make_ctx(), now=NOW)


# ── 评分权重 ────────────────────────────────────────────────────────────────


def test_custom_weights_valid():
    sel = AlgoExecutionSelector(AlgoTradingEngine(), weights=(0.5, 0.3, 0.2))
    s = sel.select(make_order(), make_ctx(), now=NOW)
    assert s.selected_algo is not None


def test_custom_weights_negative_rejected():
    with pytest.raises(SelectorError, match="不能为负"):
        AlgoExecutionSelector(AlgoTradingEngine(), weights=(-0.1, 0.6, 0.5))


def test_custom_weights_sum_not_one_rejected():
    with pytest.raises(SelectorError, match="权重和"):
        AlgoExecutionSelector(AlgoTradingEngine(), weights=(0.5, 0.3, 0.1))


# ── recommend (无副作用) ────────────────────────────────────────────────────


def test_recommend_returns_algo():
    sel = make_selector()
    f = OrderFeatures.from_order(make_order(Decimal("60000")), make_ctx(), Decimal("0.2"))
    algo = sel.recommend(f)
    assert algo == AlgoType.ICEBERG


def test_recommend_no_audit():
    sel = make_selector()
    f = OrderFeatures.from_order(make_order(), make_ctx())
    sel.recommend(f)
    assert len(sel.selections) == 0  # recommend 不记审计


# ── 评分明细 ────────────────────────────────────────────────────────────────


def test_score_breakdown_to_dict():
    b = AlgoScoreBreakdown(
        algo=AlgoType.TWAP,
        size_score=0.8,
        urgency_score=0.7,
        liquidity_score=0.6,
        total=0.71,
    )
    d = b.to_dict()
    assert d["algo"] == "TWAP"
    assert d["total"] == 0.71


# ── 大小评分维度 ────────────────────────────────────────────────────────────


def test_size_score_twap_decreases_with_size():
    sel = make_selector()
    tiny = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.0001"), Decimal("0.5"))
    large = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.06"), Decimal("0.5"))
    tw_tiny = sel._size_score(AlgoType.TWAP, tiny)
    tw_large = sel._size_score(AlgoType.TWAP, large)
    assert tw_tiny > tw_large


def test_size_score_iceberg_increases_with_size():
    sel = make_selector()
    small = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.005"), Decimal("0.5"))
    large = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.06"), Decimal("0.5"))
    ib_small = sel._size_score(AlgoType.ICEBERG, small)
    ib_large = sel._size_score(AlgoType.ICEBERG, large)
    assert ib_large > ib_small


# ── 紧急度评分维度 ──────────────────────────────────────────────────────────


def test_urgency_score_alt_increases_with_urgency():
    sel = make_selector()
    low = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.1"))
    high = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.9"))
    assert sel._urgency_score(AlgoType.ALT, high) > sel._urgency_score(AlgoType.ALT, low)


def test_urgency_score_twap_decreases_with_urgency():
    sel = make_selector()
    low = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.1"))
    high = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.9"))
    assert sel._urgency_score(AlgoType.TWAP, low) > sel._urgency_score(AlgoType.TWAP, high)


def test_urgency_score_is_peaks_at_mid():
    sel = make_selector()
    mid = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"))
    extreme = OrderFeatures("X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.99"))
    assert sel._urgency_score(AlgoType.IS, mid) > sel._urgency_score(AlgoType.IS, extreme)


# ── 流动性评分维度 ──────────────────────────────────────────────────────────


def test_liquidity_score_unknown_spread_neutral():
    sel = make_selector()
    f = OrderFeatures(
        "X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"), spread_bps=Decimal("-1")
    )
    assert sel._liquidity_score(AlgoType.TWAP, f) == 0.5


def test_liquidity_score_alt_prefers_narrow_spread():
    sel = make_selector()
    narrow = OrderFeatures(
        "X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"), spread_bps=Decimal("3")
    )
    wide = OrderFeatures(
        "X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"), spread_bps=Decimal("25")
    )
    assert sel._liquidity_score(AlgoType.ALT, narrow) > sel._liquidity_score(AlgoType.ALT, wide)


def test_liquidity_score_twap_prefers_wide_spread():
    sel = make_selector()
    narrow = OrderFeatures(
        "X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"), spread_bps=Decimal("3")
    )
    wide = OrderFeatures(
        "X", "S", OrderSide.BUY, Decimal("100"), Decimal("0.01"), Decimal("0.5"), spread_bps=Decimal("25")
    )
    assert sel._liquidity_score(AlgoType.TWAP, wide) > sel._liquidity_score(AlgoType.TWAP, narrow)


# ── 效果评估器 ──────────────────────────────────────────────────────────────


def test_evaluator_good_verdict():
    ev = DefaultAlgoEvaluator()
    # IS = 1bp (avg 10.501 vs decision 10.50)
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.TWAP,
            Decimal("10.50"),
            Decimal("10.501"),
            Decimal("1000"),
        )
    )
    assert r.verdict == "good"
    assert float(r.implementation_shortfall_bps) == pytest.approx(0.952, rel=1e-2)
    assert r.efficiency_score > 0.9


def test_evaluator_acceptable_verdict():
    ev = DefaultAlgoEvaluator()
    # IS = 10bp
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.VWAP,
            Decimal("10.00"),
            Decimal("10.01"),
            Decimal("1000"),
        )
    )
    assert r.verdict == "acceptable"
    assert 0.6 < r.efficiency_score < 0.9


def test_evaluator_poor_verdict():
    ev = DefaultAlgoEvaluator()
    # IS = 30bp
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.ALT,
            Decimal("10.00"),
            Decimal("10.03"),
            Decimal("1000"),
        )
    )
    assert r.verdict == "poor"
    assert r.efficiency_score < 0.6


def test_evaluator_zero_fill():
    ev = DefaultAlgoEvaluator()
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.TWAP,
            Decimal("10.00"),
            Decimal("10.00"),
            Decimal("0"),
        )
    )
    assert r.fill_rate == Decimal("0")


def test_evaluator_full_fill():
    ev = DefaultAlgoEvaluator()
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.TWAP,
            Decimal("10.00"),
            Decimal("10.00"),
            Decimal("1000"),
        )
    )
    assert r.fill_rate == Decimal("1.0")


def test_evaluator_zero_decision_price_raises():
    ev = DefaultAlgoEvaluator()
    with pytest.raises(SelectorError, match="decision_price"):
        ev.evaluate(
            ExecutionOutcome(
                "O1",
                AlgoType.TWAP,
                Decimal("0"),
                Decimal("10.00"),
                Decimal("1000"),
            )
        )


def test_evaluator_negative_is_takes_abs():
    """SELL 方向 avg < decision → IS 为负, 评估取绝对值 (1bp→good)。"""
    ev = DefaultAlgoEvaluator()
    r = ev.evaluate(
        ExecutionOutcome(
            "O1",
            AlgoType.TWAP,
            Decimal("10.00"),
            Decimal("9.999"),
            Decimal("1000"),
        )
    )
    # |(-1bp)| = 1bp → good
    assert r.verdict == "good"


def test_evaluation_result_dataclass():
    r = AlgoEvaluationResult(
        order_id="O1",
        algo_type=AlgoType.TWAP,
        implementation_shortfall_bps=Decimal("5"),
        fill_rate=Decimal("1.0"),
        efficiency_score=0.9,
        verdict="good",
    )
    assert r.algo_type == AlgoType.TWAP
    assert r.verdict == "good"


# ── 集成: 选择→生成计划 ──────────────────────────────────────────────────────


def test_integration_select_then_generate_plan():
    """端到端: 选择器选算法 → 引擎用该算法生成计划。"""
    eng = AlgoTradingEngine()
    sel = AlgoExecutionSelector(eng)
    order = make_order(Decimal("60000"))
    ctx = make_ctx()
    selection = sel.select(order, ctx, urgency=Decimal("0.2"), now=NOW)
    # 用选择的算法生成计划 (ICEBERG 需 display_quantity)
    from zephyr.ex_sor.core.algo_trading_engine import LOT_SIZE, AlgoParams

    kwargs = {}
    if selection.selected_algo == AlgoType.ICEBERG:
        kwargs["display_quantity"] = Decimal("5000")
    params = AlgoParams(algo_type=selection.selected_algo, **kwargs)
    plan = eng.generate_plan(order, params, ctx, now=NOW)
    assert plan.algo_type == selection.selected_algo
    assert sum((s.quantity for s in plan.slices), Decimal("0")) == order.quantity
