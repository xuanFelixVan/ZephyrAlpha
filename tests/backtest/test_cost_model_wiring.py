# [A_test] module_id: MOD-BT-COST-WIRING | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §test
# [MODULE] tests.backtest.test_cost_model_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.matching_logic; zephyr.backtest.core.matching_engine; zephyr.backtest.core.cost_model_calibration; zephyr.backtest.implementations.vectorized_engine
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_cost_model_wiring.py
# [TTL] task_bound
"""台账 #23 H2「标定真源 → 引擎接线」回归锁（车道 M）。

``test_cost_model_calibration.py`` 锁的是**标定件自身**（表自洽/有界/可复现）；
本件锁的是**接线**——标定值真的走进了成交价，而不是又一份躺在模块里的表。六件事：

(a) **滑点腿分层生效**：有当日成交额→落 ADV 五分位档；无流动性信息→全市场名义
    加权实证档（**不是**旧的 1bp）；显式钉住的平口径优先于二者。
(a′) **H2-A 病灶本体**：默认配置（``slippage_bps=None``）整链不再抛 TypeError；
    钉住口径与流动性无关；sizing 现金投影与实际成交共用同一档（两者一旦分裂，
    买入手数就会越过可负担前沿）。
(b) **地板佣金**：小额单咬合（¥1,000 与 ¥2,000 两档，有效费率高于万0.854，
    且惩罚量与 ``floor_drag_bps`` 闭式一致），超过
    ``commission_floor_nonbinding_notional`` 后不再咬合；
    全程万0.854 这个**费率本体零改动**（地板只是小额单上的额外约束）。
(c) **两腿不重复计费**：滑点腿与尺寸无关、冲击腿与尺寸相关，各自单独可归零；
    两腿同开时总成本 = 两笔相加（乘性口径下等于一次一腿），永久项 γ=0 恒零，
    绝不出现同一段位移计两次。
(d) **legacy 口径逐位复现**：``SLIPPAGE_TIERING_ENABLED=False`` 时四个黄金场景
    （含引擎级多日 NAV 轨迹）与接线前抓的数**逐字符相同**——A/B 取证的可信前提。
(e) **无第二真源**：引擎源码里不得出现任何档位 bps / η / σ / β 字面量。

费率字面量真源在 ``matching_logic``；本件只引用不复制（RULE-SSOT）。
"""

from __future__ import annotations

import inspect
import re
from decimal import ROUND_FLOOR, Decimal

import pandas as pd
import pytest

from zephyr.backtest.core import cost_model_calibration as cal
from zephyr.backtest.core import matching_engine as me
from zephyr.backtest.core import matching_logic as ml
from zephyr.backtest.core.matching_engine import LiquidityGuardConfig, MatchingEngine
from zephyr.backtest.core.matching_logic import (
    COMMISSION_RATE,
    MIN_COMMISSION,
    TRANSFER_FEE_RATE,
    MatchingConfig,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.backtest.core.portfolio import Portfolio
from zephyr.backtest.implementations.vectorized_engine import BacktestConfig, DefaultBacktestEngine

_DATE = "2026-08-03"
_PRICE = Decimal("10.00")
#: ¥3,000万 日成交额 → Q1_illiquid（低于最低层上界 ADV_QUINTILE_BOUNDS_YUAN[0]）
_ILLIQUID_NOTIONAL = Decimal("30000000")
#: ¥9亿 日成交额 → Q5_liquid（高于最高层上界）
_LIQUID_NOTIONAL = Decimal("900000000")


def _book(price: Decimal = _PRICE, symbol: str = "600000") -> OrderBookSnapshot:
    """合成1档盘口（ask1==bid1==last，零价差）——与 MatchingEngine 日线路径同构。"""
    return OrderBookSnapshot(
        symbol=symbol,
        ask_price=tuple([price] * 5),
        bid_price=tuple([price] * 5),
        ask_vol=tuple([Decimal("1000000")] * 5),
        bid_vol=tuple([Decimal("1000000")] * 5),
        last_price=price,
        timestamp=None,
    )


def _gross_only_book_logic(
    qty: Decimal,
    *,
    notional: Decimal | None = None,
    side: str = "BUY",
    slippage: Decimal | None = None,
) -> ml.MatchingFill:
    """单笔市价撮合（可钉滑点口径），用于隔离出「一条腿」的成本。"""
    logic = MatchingLogic(MatchingConfig(slippage_bps=slippage))
    return logic.match_market_order(
        MatchOrderInput(
            symbol="600000",
            side=side,
            quantity=qty,
            order_type="MARKET",
            daily_notional_yuan=notional,
        ),
        _book(),
    )


# ---------------------------------------------------------------------------
# (a) 滑点腿：分层标定值真的进入成交价
# ---------------------------------------------------------------------------


def test_illiquid_notional_fill_carries_calibrated_tier_bps() -> None:
    """有当日成交额→滑点按 ADV 五分位档（Q1 最不流动层），非常数。"""
    bps = cal.SLIPPAGE_TIER_BPS[cal.liquidity_tier(float(_ILLIQUID_NOTIONAL))]
    fill = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL)
    assert bps == cal.SLIPPAGE_TIER_BPS[0]  # 前提：确为最不流动层
    assert fill.price == _PRICE * (Decimal("1") + bps / Decimal("10000"))
    assert fill.slippage_cost == (fill.price - _PRICE) * fill.quantity


def test_liquid_notional_is_cheaper_than_illiquid() -> None:
    """同一把尺子：更流动的标的滑点更低（分层单调，不是一口价）。"""
    illiquid = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL)
    liquid = _gross_only_book_logic(Decimal("1000"), notional=_LIQUID_NOTIONAL)
    assert liquid.price < illiquid.price
    assert cal.slippage_bps_for_notional(float(_LIQUID_NOTIONAL)) < cal.slippage_bps_for_notional(
        float(_ILLIQUID_NOTIONAL)
    )


def test_fill_without_liquidity_info_uses_universal_not_legacy_flat() -> None:
    """无流动性信息→全市场名义加权**实证**档；显式区别于 legacy 1bp（H2-A 病灶）。"""
    fill = _gross_only_book_logic(Decimal("1000"), notional=None)
    assert fill.price == _PRICE * (Decimal("1") + cal.SLIPPAGE_BPS_UNIVERSAL / Decimal("10000"))
    assert fill.price != _PRICE * (Decimal("1") + cal.LEGACY_FLAT_SLIPPAGE_BPS / Decimal("10000"))


def test_pinned_flat_bps_overrides_tiering_and_accepts_zero() -> None:
    """钉住口径优先于分层；0=毛口径对照（成本敏感性扫描用），不是非法值。"""
    pinned = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL, slippage=Decimal("10"))
    assert pinned.price == _PRICE * Decimal("1.001")
    gross_ref = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL, slippage=Decimal("0"))
    assert gross_ref.price == _PRICE
    assert gross_ref.slippage_cost == Decimal("0")


@pytest.mark.parametrize(
    ("notional", "expected"),
    [
        (None, cal.SLIPPAGE_BPS_UNIVERSAL),
        (_ILLIQUID_NOTIONAL, cal.SLIPPAGE_TIER_BPS[0]),
        (_LIQUID_NOTIONAL, cal.SLIPPAGE_TIER_BPS[-1]),
    ],
)
def test_resolve_slippage_precedence_is_single_source(notional, expected) -> None:
    """四级优先序在真源一处实现；引擎/Logic 都只是它的调用方。"""
    assert MatchingLogic().slippage_bps_for(notional) == expected
    assert cal.resolve_slippage_bps(None if notional is None else float(notional)) == expected


def test_engine_threads_daily_turnover_into_every_fill() -> None:
    """引擎级：volumes→当日成交额→逐笔档位（不是只在 Logic 里对，引擎不传也白搭）。"""
    vol_illiquid = _ILLIQUID_NOTIONAL / _PRICE  # 300 万股
    vol_liquid = _LIQUID_NOTIONAL / _PRICE
    engine = MatchingEngine(config=MatchingConfig(), liquidity_config=LiquidityGuardConfig(impact_enabled=False))
    fills = engine.generate_fills(
        target_weights={"ILLIQ": 0.1, "LIQ": 0.1},
        prices={"ILLIQ": _PRICE, "LIQ": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"ILLIQ": vol_illiquid, "LIQ": vol_liquid},
    )
    by_symbol = {f.symbol: f for f in fills}
    assert set(by_symbol) == {"ILLIQ", "LIQ"}
    for symbol, notional in (("ILLIQ", _ILLIQUID_NOTIONAL), ("LIQ", _LIQUID_NOTIONAL)):
        bps = cal.slippage_bps_for_notional(float(notional))
        assert by_symbol[symbol].price == _PRICE * (Decimal("1") + bps / Decimal("10000")), symbol


def test_engine_without_volume_falls_back_to_universal_caliber() -> None:
    """不传 volumes（无流动性信息）→逐笔落无信息档，而非 legacy 1bp。"""
    engine = MatchingEngine()
    fills = engine.generate_fills(
        target_weights={"600000": 0.1},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
    )
    assert fills[0].price == _PRICE * (Decimal("1") + cal.SLIPPAGE_BPS_UNIVERSAL / Decimal("10000"))


# ---------------------------------------------------------------------------
# (a′) H2-A 病灶本体：崩溃回归 / 钉住口径与流动性无关 / 投影与成交同一把尺
# ---------------------------------------------------------------------------


def test_default_config_generate_fills_no_longer_raises_and_fills_at_calibrated_bps() -> None:
    """H2-A 崩溃回归：``slippage_bps=None`` 的默认路曾经 TypeError，现在必须出成交。

    病灶是 ``_clamp_buys_to_projected_cash`` 直接对**原始字段**做 ``/ 10000`` 算术，
    而 ``generate_fills`` 无条件调用它 → 默认配置（None=逐笔解析）必然抛
    ``TypeError: unsupported operand type(s) for /: 'NoneType' and 'Decimal'``。
    本用例即当年那段最小复现，逐字照抄（半仓、无 volumes）。
    """
    engine = MatchingEngine()
    assert engine.config.slippage_bps is None  # 崩溃前提：默认值确实是 None 而非 1bp

    fills = engine.generate_fills(
        target_weights={"600000": 0.5},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date="2026-09-16",
    )
    assert len(fills) == 1
    assert fills[0].quantity == Decimal("50000")  # 未误收缩
    assert fills[0].price == _PRICE * (Decimal("1") + cal.SLIPPAGE_BPS_UNIVERSAL / Decimal("10000"))

    # 结构锁：引擎侧不得再碰原始字段，只能经 Logic 的单点解析（防同类病灶复发）
    assert "config.slippage_bps" not in inspect.getsource(me)


@pytest.mark.parametrize("notional", [None, _ILLIQUID_NOTIONAL, _LIQUID_NOTIONAL])
def test_pinned_bps_is_independent_of_liquidity(notional: Decimal) -> None:
    """钉住 2bp 就是 2bp：三档流动性输入下价格逐位相同（显式口径优先，不分层）。"""
    pinned = _gross_only_book_logic(Decimal("1000"), notional=notional, slippage=Decimal("2"))
    assert pinned.price == _PRICE * (Decimal("1") + Decimal("2") / Decimal("10000"))
    # 同花输入不钉住时三档价格互不相同 → 证明上面的一致来自钉住，而非分层恒真
    unpinned = _gross_only_book_logic(Decimal("1000"), notional=notional)
    assert unpinned.price != pinned.price
    assert MatchingLogic().slippage_bps_for(notional) != Decimal("2")

    # 引擎级同口径：ILLIQ/LIQ 两腿在钉住下必须同价（分层失效才是对的）
    fills = MatchingEngine(
        config=MatchingConfig(slippage_bps=Decimal("2")),
        liquidity_config=LiquidityGuardConfig(impact_enabled=False),
    ).generate_fills(
        target_weights={"ILLIQ": 0.1, "LIQ": 0.1},
        prices={"ILLIQ": _PRICE, "LIQ": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"ILLIQ": _ILLIQUID_NOTIONAL / _PRICE, "LIQ": _LIQUID_NOTIONAL / _PRICE},
    )
    assert {f.price for f in fills} == {_PRICE * Decimal("1.0002")}


def test_cash_projection_and_fill_share_the_same_slippage_tier() -> None:
    """sizing 投影与实际成交不得分裂（#23 H2-A 的「同一条腿用两次」锁）。

    构造现金恰好咬合的满仓单：可负担最大整手由**投影用的滑点**决定。若投影仍按
    legacy 1bp 而成交按标定 7.24bp，买单会多出一手、_apply_buy 的现金非负防线
    兜底 → 本用例的第一条不等式即失败。断言全部从**成交单自身的价格**反推，
    不复述任何档位字面量。
    """
    cash = Decimal("999500")  # 落在 7.24bp 与 1bp 两条可负担前沿之间（见下方闭合验证）
    vol = _ILLIQUID_NOTIONAL / _PRICE  # 300 万股 → Q1 最不流动档
    engine = MatchingEngine(
        config=MatchingConfig(), liquidity_config=LiquidityGuardConfig(impact_enabled=False)
    )
    fills = engine.generate_fills(
        target_weights={"600000": 1.0},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=cash),
        date=_DATE,
        volumes={"600000": vol},
    )
    fill = fills[0]

    # ① 成交腿的档 = 真源对该标当日成交额解析出的档
    assert (fill.price / _PRICE - Decimal("1")) * Decimal("10000") == cal.slippage_bps_for_notional(
        float(_ILLIQUID_NOTIONAL)
    )
    # ② 投影腿按**同一个档**给出的前沿：该手数是买得起的最大整手
    lot = Decimal("100")

    def _cost(q: Decimal) -> Decimal:
        g = q * fill.price
        return g + max(g * COMMISSION_RATE, MIN_COMMISSION) + g * TRANSFER_FEE_RATE

    assert _cost(fill.quantity) <= cash < _cost(fill.quantity + lot)
    # ③ 反证：按 legacy 一口价投影会多买一手 → 两口径可区分，②不是恒真式
    legacy_exec = _PRICE * (Decimal("1") + cal.LEGACY_FLAT_SLIPPAGE_BPS / Decimal("10000"))

    def _legacy_cost(q: Decimal) -> Decimal:
        g = q * legacy_exec
        return g + max(g * COMMISSION_RATE, MIN_COMMISSION) + g * TRANSFER_FEE_RATE

    assert _legacy_cost(fill.quantity + lot) <= cash


# ---------------------------------------------------------------------------
# (b) 地板佣金：小额单咬合、大额单不咬合、费率本体零改动
# ---------------------------------------------------------------------------


def _broker_part(fill: ml.MatchingFill, gross: Decimal) -> Decimal:
    """从总手续费里剥出「券商佣金」一项（扣掉双向过户费）以便与地板比对。"""
    return fill.commission - gross * TRANSFER_FEE_RATE


def test_commission_floor_binds_on_small_order() -> None:
    """¥1,000 小额单：比例佣金 0.0854 元 < ¥5 下限 → 地板咬合，惩罚量等于闭式。"""
    qty = Decimal("100")
    fill = _gross_only_book_logic(qty, slippage=Decimal("0"))  # 毛口径：成交价=基准价
    gross = qty * _PRICE
    broker = _broker_part(fill, gross)
    assert broker == MIN_COMMISSION
    drag = cal.floor_drag_bps(float(gross), commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    assert float((broker / gross - COMMISSION_RATE) * Decimal("10000")) == pytest.approx(drag, rel=1e-9)


def test_commission_floor_binds_at_two_thousand_yuan_notional() -> None:
    """¥2,000 名义单：比例佣金 0.1708 元 → 地板把券商佣金抬到整 ¥5，总成本随之前移。

    CRITICAL 约束的反面证据：地板咬合改变的是**该笔单的有效费率**，不是
    ``COMMISSION_RATE`` 这个常量本身——末行逐字复比，确认费率未被就地改动。
    """
    qty = Decimal("200")
    fill = _gross_only_book_logic(qty, slippage=Decimal("0"))  # 毛口径：成交价=基准价
    gross = qty * _PRICE
    assert gross == Decimal("2000.00")
    assert gross * COMMISSION_RATE < MIN_COMMISSION  # 0.1708 < 5 → 必然咬合

    assert _broker_part(fill, gross) == MIN_COMMISSION
    assert fill.commission == MIN_COMMISSION + gross * TRANSFER_FEE_RATE
    assert fill.total_cost == gross + MIN_COMMISSION + gross * TRANSFER_FEE_RATE
    # 有效费率被地板抬到 25bp，惩罚量与闭式一致；费率常量本体逐字未动
    broker_rate = _broker_part(fill, gross) / gross
    assert broker_rate == Decimal("0.0025")
    drag = cal.floor_drag_bps(float(gross), commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION)
    assert float((broker_rate - COMMISSION_RATE) * Decimal("10000")) == pytest.approx(drag, rel=1e-9)
    assert COMMISSION_RATE == Decimal("0.0000854")


def test_commission_floor_does_not_bind_above_nonbinding_notional() -> None:
    """过 ``commission_floor_nonbinding_notional`` 后地板不再咬合：有效费率=万0.854 逐位。"""
    threshold = cal.commission_floor_nonbinding_notional(
        commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION
    )
    # 边界成对：下界（1 手）咬合、上界（1 手）不咬合——地板阈值本身被钉住
    below = (threshold / _PRICE).to_integral_value(rounding="ROUND_FLOOR") * _PRICE - Decimal("10")
    above = (threshold / _PRICE).to_integral_value(rounding="ROUND_FLOOR") * _PRICE + Decimal("10")
    assert below < threshold < above

    small = _gross_only_book_logic(below / _PRICE, slippage=Decimal("0"))
    large = _gross_only_book_logic(above / _PRICE, slippage=Decimal("0"))
    assert _broker_part(small, below) == MIN_COMMISSION  # 咬合
    assert _broker_part(large, above) > MIN_COMMISSION  # 不咬合
    assert _broker_part(large, above) == above * COMMISSION_RATE  # 纯比例，费率未被改动


def test_floor_treatment_never_mutates_the_negligible_rate() -> None:
    """CRITICAL 锁：万0.854 是 Owner 确认的券商合作费率，地板处理只加约束、不改费率。"""
    assert COMMISSION_RATE == Decimal("0.0000854")
    assert MatchingConfig().commission_rate == COMMISSION_RATE
    assert BacktestConfig().commission_rate == COMMISSION_RATE
    assert MIN_COMMISSION == Decimal("5")
    # 大单上「佣金/名义」逐位等于费率本体（地板未渗入率值）
    qty = Decimal("200000")
    fill = _gross_only_book_logic(qty, slippage=Decimal("0"))
    gross = qty * _PRICE
    assert _broker_part(fill, gross) / gross == COMMISSION_RATE


# ---------------------------------------------------------------------------
# (c) 两腿互斥可加：不重复计费
# ---------------------------------------------------------------------------


def _engine(impact: bool) -> MatchingEngine:
    return MatchingEngine(config=MatchingConfig(), liquidity_config=LiquidityGuardConfig(impact_enabled=impact))


def test_impact_leg_uses_calibrated_tier_params_not_default_params() -> None:
    """冲击腿参数档=该流动性层标定值（H2-C）；默认档被消费的旧路径不再是主通路。"""
    vol = _ILLIQUID_NOTIONAL / _PRICE
    qty = Decimal("20000")
    p = float(qty) / float(vol)
    lvl = cal.impact_level_for_notional(float(_ILLIQUID_NOTIONAL))
    engine = _engine(impact=True)
    adjusted = engine._apply_impact_to_books(
        [{"side": "BUY", "symbol": "600000", "quantity": qty}], {"600000": _book()}, {"600000": vol}
    )
    shocked = adjusted["600000"].ask_price[0]
    # 冲击恰好是一次表内位移（临时项），永久项 γ=0 ⇒ 不再另计一次
    expected = _PRICE * (Decimal("1") + Decimal(str(lvl.cost_bps_at(p))) / Decimal("10000"))
    assert shocked == expected
    assert lvl.gamma == 0.0
    assert shocked > _PRICE * (Decimal("1") + Decimal("0.0001"))  # 已脱离 DEFAULT_PARAMS 量级


def test_slippage_leg_is_size_independent_and_impact_leg_is_size_dependent() -> None:
    """两腿正交：滑点只随流动性变、冲击只随尺寸变——这正是「可加不重叠」的前提。"""
    vol = _ILLIQUID_NOTIONAL / _PRICE
    bps = cal.slippage_bps_for_notional(float(_ILLIQUID_NOTIONAL))
    small = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL)
    large = _gross_only_book_logic(Decimal("50000"), notional=_ILLIQUID_NOTIONAL)
    assert small.price == large.price == _PRICE * (Decimal("1") + bps / Decimal("10000"))

    engine = _engine(impact=True)
    shocks = []
    for qty in (Decimal("20000"), Decimal("150000")):
        adjusted = engine._apply_impact_to_books(
            [{"side": "BUY", "symbol": "600000", "quantity": qty}], {"600000": _book()}, {"600000": vol}
        )
        shocks.append(adjusted["600000"].ask_price[0])
    assert shocks[1] > shocks[0]  # 参与率越大越贵（滑点腿给不出这个单调性）


def test_two_legs_add_up_without_double_charging() -> None:
    """两腿同开=一次滑点 + 一次冲击，总溢价等于两笔之和（不含任何第三笔）。"""
    vol = _ILLIQUID_NOTIONAL / _PRICE
    qty = Decimal("20000")
    p = float(qty) / float(vol)
    bps = cal.slippage_bps_for_notional(float(_ILLIQUID_NOTIONAL))
    lvl = cal.impact_level_for_notional(float(_ILLIQUID_NOTIONAL))

    fills = _engine(impact=True).generate_fills(
        target_weights={"600000": 0.2},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"600000": vol},
    )
    fill = fills[0]
    assert fill.quantity == qty  # 未触发收缩，参与率可比

    impact_bps = lvl.cost_bps_at(p)
    slip_bps = float(bps)
    # 成交价 = 基准价 ×(1+冲击)×(1+滑点)：一条腿各计一次，次序与引擎一致
    expected_price = _PRICE * (Decimal("1") + Decimal(str(impact_bps)) / Decimal("10000"))
    expected_price = expected_price + expected_price * bps / Decimal("10000")
    assert fill.price == expected_price

    total_premium_bps = float((fill.price / _PRICE - Decimal("1")) * Decimal("10000"))
    excess_bps = total_premium_bps - (impact_bps + slip_bps)
    # 超出"两笔相加"的部分只能是乘性二阶交叉项，不可能再藏着第三条腿
    assert excess_bps == pytest.approx(impact_bps * slip_bps / 1e4, rel=1e-9)
    assert abs(excess_bps) < 0.01 * min(impact_bps, slip_bps)

    # 分腿可归零：滑点钉 0 时只剩冲击；冲击关时只剩滑点
    zero_slip = MatchingEngine(
        config=MatchingConfig(slippage_bps=Decimal("0")), liquidity_config=LiquidityGuardConfig()
    ).generate_fills(
        target_weights={"600000": 0.2},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"600000": vol},
    )[0]
    assert float((zero_slip.price / _PRICE - Decimal("1")) * Decimal("10000")) == pytest.approx(impact_bps, rel=1e-9)

    no_impact = _engine(impact=False).generate_fills(
        target_weights={"600000": 0.2},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"600000": vol},
    )[0]
    assert float((no_impact.price / _PRICE - Decimal("1")) * Decimal("10000")) == pytest.approx(float(bps), rel=1e-9)


# ---------------------------------------------------------------------------
# (d) legacy 口径逐位复现（A/B 取证前提）
# ---------------------------------------------------------------------------

# 接线前（未接线代码 + 无开关）在 .runtime/tmp/m2_capture_legacy_goldens.py 抓的数。
# 逐字符比对：这些字面量是**历史事实**，不是档位表，不构成第二真源。
_LEGACY_GOLDENS = {
    "case1_no_volume": {
        "qty": "99900",
        "price": "10.001",
        "commission": "95.3141304600",
        "slippage_cost": "99.900",
        "total_cost": "999195.2141304600",
    },
    "case2_illiquid_impact_on": {
        "qty": "20000",
        "price": "10.00194992489725248550594",
        "commission": "19.08372045670395774234533352",
        "slippage_cost": "20.00189965982852211880000",
        "total_cost": "200058.0822184017536678611453",
    },
    "case3_logic": {
        "buy_price": "10.001",
        "buy_commission": "5.10001000",
        "buy_total": "10006.10001000",
        "sell_price": "9.989001",
        "sell_commission": "594.7451195400000",
        "sell_total": "998305.3548804600000",
    },
    "case4_engine_run": {
        "total_return": "0.0037088481300052954",
        "trades": 2,
        "cash": "1713.8681550200560588361560",
        "commission_total": "95.22741228287930",
        "slippage_total": "99.809109532316474",
    },
}


def _capture() -> dict:
    """重跑四个黄金场景（口径由当前 ``SLIPPAGE_TIERING_ENABLED`` 决定）。"""
    out: dict = {}

    engine = MatchingEngine()
    fills = engine.generate_fills(
        target_weights={"600000": 1.0},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
    )
    f = fills[0]
    out["case1_no_volume"] = {
        "qty": str(f.quantity),
        "price": str(f.price),
        "commission": str(f.commission),
        "slippage_cost": str(f.slippage_cost),
        "total_cost": str(f.total_cost),
    }

    eng2 = MatchingEngine(config=MatchingConfig(), liquidity_config=LiquidityGuardConfig())
    f2 = eng2.generate_fills(
        target_weights={"600000": 0.2},
        prices={"600000": _PRICE},
        portfolio=Portfolio(initial_capital=Decimal("1000000")),
        date=_DATE,
        volumes={"600000": Decimal("3000000")},
    )[0]
    out["case2_illiquid_impact_on"] = {
        "qty": str(f2.quantity),
        "price": str(f2.price),
        "commission": str(f2.commission),
        "slippage_cost": str(f2.slippage_cost),
        "total_cost": str(f2.total_cost),
    }

    logic = MatchingLogic()
    book = OrderBookSnapshot(
        symbol="000001.SZ",
        ask_price=tuple(Decimal("10.00") + Decimal("0.01") * i for i in range(5)),
        bid_price=tuple(Decimal("9.99") - Decimal("0.01") * i for i in range(5)),
        ask_vol=tuple(Decimal("100") for _ in range(5)),
        bid_vol=tuple(Decimal("100") for _ in range(5)),
        last_price=Decimal("10.00"),
    )
    buy = logic.match_market_order(
        MatchOrderInput(symbol="000001.SZ", side="BUY", quantity=Decimal("1000"), order_type="MARKET"), book
    )
    sell = logic.match_market_order(
        MatchOrderInput(symbol="000001.SZ", side="SELL", quantity=Decimal("100000"), order_type="MARKET"), book
    )
    out["case3_logic"] = {
        "buy_price": str(buy.price),
        "buy_commission": str(buy.commission),
        "buy_total": str(buy.total_cost),
        "sell_price": str(sell.price),
        "sell_commission": str(sell.commission),
        "sell_total": str(sell.total_cost),
    }

    dates = pd.bdate_range("2026-08-03", periods=6)
    rows = []
    for j, d in enumerate(dates):
        for sym, base in (("600000", 10.0), ("600002", 20.0)):
            rows.append(
                {
                    "symbol": sym,
                    "date": d,
                    "close": base * (1.001**j),
                    "open": base * (1.001**j),
                    "volume": 3_000_000 if sym == "600000" else 40_000_000,
                }
            )
    data = pd.DataFrame(rows).set_index(["symbol", "date"])
    signals = pd.DataFrame({"600000": [0.5] * 6, "600002": [0.5] * 6}, index=dates)
    eng4 = DefaultBacktestEngine(
        config=BacktestConfig(enable_pit_universe_filter=False),
        enable_stk_limit_provider=False,
    )
    res4 = eng4.run(data=data, signals=signals, strategy_name="legacy-golden")
    pf = eng4.last_portfolio
    out["case4_engine_run"] = {
        "total_return": repr(res4.total_return),
        "trades": res4.trades_count,
        "cash": str(pf.cash),
        "commission_total": str(sum((Decimal(str(t["commission"])) for t in pf.trades_log), Decimal("0"))),
        "slippage_total": str(sum((Decimal(str(t["slippage_cost"])) for t in pf.trades_log), Decimal("0"))),
    }
    return out


def test_legacy_caliber_reproduces_bit_for_bit_when_switch_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """开关关 → 整链逐位回到接线前（每个字段逐字符比对，A/B 取证的可信根）。"""
    monkeypatch.setattr(cal, "SLIPPAGE_TIERING_ENABLED", False)
    assert cal.calibration_enabled() is False
    got = _capture()
    for case, gold in _LEGACY_GOLDENS.items():
        for key, want in gold.items():
            assert str(got[case][key]) == str(want), f"{case}.{key}: legacy={got[case][key]!r} != {want!r}"


def test_calibrated_caliber_is_strictly_more_expensive_than_legacy() -> None:
    """反向锁：接线后的同一路径必须比 legacy 一口价贵——否则「接线」是假绿。"""
    fill = _gross_only_book_logic(Decimal("1000"), notional=_ILLIQUID_NOTIONAL)
    legacy_ref = _PRICE * (Decimal("1") + cal.LEGACY_FLAT_SLIPPAGE_BPS / Decimal("10000"))
    assert fill.price > legacy_ref
    assert (fill.price - _PRICE) / _PRICE * Decimal("10000") == cal.slippage_bps_for_notional(
        float(_ILLIQUID_NOTIONAL)
    )


# ---------------------------------------------------------------------------
# (e) 默认口径与「无第二真源」
# ---------------------------------------------------------------------------


def test_engines_default_to_calibrated_per_fill_caliber() -> None:
    """两套引擎配置的默认都是「逐笔解析」，不再钉住 legacy 一口价。"""
    assert BacktestConfig().slippage_bps is None
    assert MatchingConfig().slippage_bps is None
    assert MatchingEngine().config.slippage_bps is None
    # 兼容别名仍在，但值本体归标定件（避免两处各写一份 1bp）
    assert ml.SLIPPAGE_BPS is cal.LEGACY_FLAT_SLIPPAGE_BPS


def test_matching_engine_source_holds_no_second_cost_table() -> None:
    """引擎侧零档位字面量：滑点 bps / η / β / σ 只能来自标定件（CloneGuard 前置锁）。"""
    body = inspect.getsource(me)
    body = re.sub(r'"""[\s\S]*?"""', "", body)  # 去 docstring
    body = re.sub(r"#.*", "", body)  # 去注释
    banned = ("3.79", "7.24", "5.69", "4.67", "2.34", "0.9776", "0.7295", "0.4205", "0.020428", "0.03904")
    hits = sorted(v for v in banned if re.search(rf"(?<![\d.]){re.escape(v)}(?![\d.])", body))
    assert not hits, f"matching_engine 出现标定档位字面量（第二真源）: {hits}"


def test_calibration_header_declares_live_consumers() -> None:
    """接线即披露：标定件 [CONSUMERS] 头必须点名两个撮合侧消费方（防"表在、线没接"）。"""
    declared = next(
        (ln for ln in inspect.getsource(cal).splitlines() if ln.startswith("# [CONSUMERS]")),
        "",
    )
    assert declared, "标定件缺 [CONSUMERS] 头"
    for consumer in ("matching_logic", "matching_engine", "vectorized_engine", "cost_attribution"):
        assert consumer in declared, f"{consumer} 未记入标定件 [CONSUMERS]: {declared}"
