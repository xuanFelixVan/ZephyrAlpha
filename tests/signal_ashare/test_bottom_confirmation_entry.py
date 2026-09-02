# [A_test] module_id: MOD-SIG-103 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-103 | docs/03_modules/_domain_signal/bottom_confirmation_entry/blueprint.md
# [MODULE] tests.signal_ashare.test_bottom_confirmation_entry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""多维度底部确认与右侧入场模型（MOD-SIG-103，B10-01414）施工验证测试。

覆盖：
- 五维封闭集：价格超卖（RSI14<30 或触布林下轨）/量能萎缩+放量反弹/
  Smart Money 资金流/情绪≤22%分位/Wyckoff Spring；
- ≥3 维确认才 bottom_confirmed；置信度=加权命中占比（权重可注入）；
- 右侧入场=确认∧收盘>前日高；止损=底部最低价−1×ATR14（Wilder 自算）；
- 数据缺失维降级（hit=False+notes）不阻断其余维；
- fail-closed：不等长/短历史/非有限/非正价/负量/对齐注入序列长度不符/
  未知维度权重/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.bottom_confirmation_entry import (
    BOTTOM_DIM_NAMES,
    BottomConfirmationConfig,
    BottomConfirmationEntry,
)

N = 60


def _flat_bars() -> tuple[list[float], list[float], list[float], list[float], list[float]]:
    """60 根平稳 K：开=收=100、高=100.5、低=99.5、量=1000。"""
    opens = [100.0] * N
    closes = [100.0] * N
    highs = [100.5] * N
    lows = [99.5] * N
    vols = [1000.0] * N
    return opens, highs, lows, closes, vols


def _engine(**kwargs) -> BottomConfirmationEntry:
    return BottomConfirmationEntry(BottomConfirmationConfig(**kwargs))


class TestConfigValidation:
    def test_rsi_oversold_out_of_range(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(rsi_oversold=0.0)
        with pytest.raises(ValueError):
            BottomConfirmationConfig(rsi_oversold=100.0)

    def test_min_confirmations_out_of_range(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(min_confirmations=0)
        with pytest.raises(ValueError):
            BottomConfirmationConfig(min_confirmations=6)

    def test_negative_ratio(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(shrink_ratio=0.0)
        with pytest.raises(ValueError):
            BottomConfirmationConfig(rebound_vol_ratio=0.5)

    def test_min_history_too_small(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(min_history=20)

    def test_unknown_dim_weight(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(dim_weights={"mystery": 1.0})

    def test_negative_dim_weight(self):
        with pytest.raises(ValueError):
            BottomConfirmationConfig(dim_weights={"price_oversold": -1.0})


class TestInputFailClosed:
    def test_unequal_ohlcv(self):
        o, h, l, c, v = _flat_bars()
        with pytest.raises(ValueError):
            _engine().evaluate("600000", o, h, l, c[:-1], v)

    def test_short_history(self):
        o, h, l, c, v = _flat_bars()
        with pytest.raises(ValueError):
            _engine().evaluate("600000", o[:25], h[:25], l[:25], c[:25], v[:25])

    def test_non_positive_price(self):
        o, h, l, c, v = _flat_bars()
        c[30] = 0.0
        with pytest.raises(ValueError):
            _engine().evaluate("600000", o, h, l, c, v)

    def test_negative_volume(self):
        o, h, l, c, v = _flat_bars()
        v[30] = -1.0
        with pytest.raises(ValueError):
            _engine().evaluate("600000", o, h, l, c, v)

    def test_empty_symbol(self):
        o, h, l, c, v = _flat_bars()
        with pytest.raises(ValueError):
            _engine().evaluate("", o, h, l, c, v)

    def test_misaligned_injected_series(self):
        o, h, l, c, v = _flat_bars()
        with pytest.raises(ValueError):
            _engine().evaluate("600000", o, h, l, c, v, sentiment_scores=[50.0] * 10)


class TestDimensions:
    def test_price_oversold_via_rsi(self):
        """末段 15 根连阴 → Wilder RSI14→0 <30 → price_oversold 命中。"""
        o, h, l, c, v = _flat_bars()
        for i in range(N - 15, N):
            c[i] = c[i - 1] - 2.0
            o[i] = c[i - 1]
            h[i] = o[i] + 0.5
            l[i] = c[i] - 0.5
        report = _engine().evaluate("600000", o, h, l, c, v)
        dims = {d.name: d for d in report.dims}
        assert dims["price_oversold"].hit is True

    def test_flat_market_no_oversold(self):
        o, h, l, c, v = _flat_bars()
        report = _engine().evaluate("600000", o, h, l, c, v)
        dims = {d.name: d for d in report.dims}
        assert dims["price_oversold"].hit is False

    def test_volume_shrink_then_rebound(self):
        """前 20 根均量 2000 → 近 10 根（除今）800 萎缩 → 今日 3500 放量阳线。"""
        o, h, l, c, v = _flat_bars()
        for i in range(N - 31, N - 11):
            v[i] = 2000.0
        for i in range(N - 11, N - 1):
            v[i] = 800.0
        v[N - 1] = 3500.0
        o[N - 1] = 99.0
        c[N - 1] = 100.0  # 阳线
        report = _engine().evaluate("600000", o, h, l, c, v)
        dims = {d.name: d for d in report.dims}
        assert dims["volume_rebound"].hit is True

    def test_volume_no_shrink_no_hit(self):
        o, h, l, c, v = _flat_bars()
        v[N - 1] = 3500.0
        o[N - 1] = 99.0
        c[N - 1] = 100.0
        report = _engine().evaluate("600000", o, h, l, c, v)
        dims = {d.name: d for d in report.dims}
        assert dims["volume_rebound"].hit is False

    def test_smart_money_flow_hit_and_missing(self):
        o, h, l, c, v = _flat_bars()
        flows = [0.0] * (N - 5) + [100.0, 200.0, 150.0, 50.0, 80.0]
        report = _engine().evaluate("600000", o, h, l, c, v, smart_money_flows=flows)
        dims = {d.name: d for d in report.dims}
        assert dims["smart_money_flow"].hit is True
        report2 = _engine().evaluate("600000", o, h, l, c, v)
        dims2 = {d.name: d for d in report2.dims}
        assert dims2["smart_money_flow"].hit is False
        assert any("缺失" in n for n in report2.notes)

    def test_sentiment_extreme_hit_and_missing(self):
        o, h, l, c, v = _flat_bars()
        sentiment = [50.0] * (N - 1) + [5.0]
        report = _engine().evaluate("600000", o, h, l, c, v, sentiment_scores=sentiment)
        dims = {d.name: d for d in report.dims}
        assert dims["sentiment_extreme"].hit is True
        report2 = _engine().evaluate("600000", o, h, l, c, v)
        dims2 = {d.name: d for d in report2.dims}
        assert dims2["sentiment_extreme"].hit is False

    def test_wyckoff_spring_hit_and_missing(self):
        o, h, l, c, v = _flat_bars()
        springs = [False] * N
        springs[N - 3] = True
        report = _engine().evaluate("600000", o, h, l, c, v, wyckoff_springs=springs)
        dims = {d.name: d for d in report.dims}
        assert dims["wyckoff_spring"].hit is True
        report2 = _engine().evaluate("600000", o, h, l, c, v)
        dims2 = {d.name: d for d in report2.dims}
        assert dims2["wyckoff_spring"].hit is False


def _confirmed_fixture() -> tuple[
    list[float], list[float], list[float], list[float], list[float], list[float], list[float], list[bool]
]:
    """三维命中（量能+资金流+情绪）+ 今日收盘>前日高的夹具。"""
    o, h, l, c, v = _flat_bars()
    for i in range(N - 31, N - 11):
        v[i] = 2000.0
    for i in range(N - 11, N - 1):
        v[i] = 800.0
    v[N - 1] = 3500.0
    o[N - 1] = 100.0
    c[N - 1] = 101.0
    h[N - 1] = 101.5  # 前日高=100.5，今日收盘 101.0 > 100.5 → 右侧触发
    flows = [0.0] * (N - 5) + [100.0, 200.0, 150.0, 50.0, 80.0]
    sentiment = [50.0] * (N - 1) + [5.0]
    springs = [False] * N
    return o, h, l, c, v, flows, sentiment, springs


class TestConfirmationAndEntry:
    def test_three_dims_confirmed_and_entry(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        report = _engine().evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        assert report.confirmed_count == 3
        assert report.bottom_confirmed is True
        assert report.entry_triggered is True
        assert report.entry_price == pytest.approx(101.0)

    def test_two_dims_not_confirmed(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        sentiment = [50.0] * N  # 情绪不极端 → 仅 2 维
        report = _engine().evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        assert report.confirmed_count == 2
        assert report.bottom_confirmed is False
        assert report.entry_triggered is False
        assert report.stop_price is None

    def test_confirmed_but_no_breakout_no_entry(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        c[N - 1] = 100.2  # 收盘≤前日高 100.5
        h[N - 1] = 100.4
        report = _engine().evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        assert report.bottom_confirmed is True
        assert report.entry_triggered is False
        assert report.stop_price is None

    def test_stop_is_bottom_low_minus_atr(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        report = _engine().evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        assert report.stop_price == pytest.approx(report.bottom_low - report.atr)
        assert report.atr > 0.0
        assert report.bottom_low == pytest.approx(min(l[-20:]))

    def test_confidence_weighted(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        weights = {"volume_rebound": 2.0, "smart_money_flow": 1.0, "sentiment_extreme": 1.0}
        report = _engine(dim_weights=weights).evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        # 三维命中、两维缺失（价格/spring 权重默认 1）
        assert report.bottom_confirmed is True
        assert 0.0 < report.confidence <= 1.0
        dims = {d.name: d for d in report.dims}
        assert dims["volume_rebound"].weight == pytest.approx(2.0)


class TestContract:
    def test_frozen_and_json_serializable(self):
        o, h, l, c, v, flows, sentiment, springs = _confirmed_fixture()
        report = _engine().evaluate(
            "600000",
            o,
            h,
            l,
            c,
            v,
            smart_money_flows=flows,
            sentiment_scores=sentiment,
            wyckoff_springs=springs,
        )
        assert dataclasses.is_dataclass(report)
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.bottom_confirmed = False  # type: ignore[misc]
        json.dumps(report.to_dict(), ensure_ascii=False)

    def test_dim_names_closed_set(self):
        assert len(BOTTOM_DIM_NAMES) == 5
        assert "wyckoff_spring" in BOTTOM_DIM_NAMES
