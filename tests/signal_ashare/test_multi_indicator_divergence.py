# [A_test] module_id: MOD-SIG-095 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-095 | docs/03_modules/_domain_signal/multi_indicator_divergence/blueprint.md
# [MODULE] tests.signal_ashare.test_multi_indicator_divergence
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""多指标背离检测（MOD-SIG-095，B10-01363）施工验证测试。

覆盖：
- 指标核：RSI 全涨=100/全跌=0；MACD DIF 趋势方向性；
- 峰谷对位：价新高+RSI 走弱→bearish、价新低+DIF 抬升→bullish、确认时零背离、
  magnitude>0、CVD 腿接入；
- 背离化解：背离后指标反超前峰→resolved=True；
- 次数→反转概率查表（3 次顶背离≥70%）+ 越界钳制；
- 多级别级联：对齐级别数→级联概率（满级≥60%）、异向不计；
- fail-closed：短序列/NaN/非法方向/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.multi_indicator_divergence import (
    DivergenceConfig,
    MultiIndicatorDivergenceDetector,
)


def _detector(**kw) -> MultiIndicatorDivergenceDetector:
    return MultiIndicatorDivergenceDetector(DivergenceConfig(**kw))


def _two_peak_bearish_prices() -> list[float]:
    """强拉到 P1→回落→混合爬行出更高 P2（动量显著走弱）→尾部确认。"""
    up = [100.0 + 0.5 * i for i in range(20)]  # →109.5 强拉（P1，RSI≈100）
    down = [up[-1] - 0.5 * i for i in range(1, 11)]  # →104.5 回落
    creep: list[float] = []
    v = down[-1]
    for i in range(24):  # 混合爬行 →112.1（P2 价更高）
        v += 0.55 if i % 3 != 2 else -0.15
        creep.append(v)
    tail = [creep[-1] - 0.4 * i for i in range(1, 6)]  # 尾部回落确认 P2
    return up + down + creep + tail


class TestIndicatorCore:
    def test_rsi_bounds(self) -> None:
        d = _detector()
        up = pd.Series([float(i) for i in range(1, 40)])
        down = pd.Series([float(40 - i) for i in range(39)])
        assert d.rsi(up).iloc[-1] == pytest.approx(100.0)
        assert d.rsi(down).iloc[-1] == pytest.approx(0.0)

    def test_macd_dif_trend_direction(self) -> None:
        d = _detector()
        up = pd.Series([100.0 + 0.3 * i for i in range(60)])
        down = pd.Series([120.0 - 0.3 * i for i in range(60)])
        dif_up, _, _ = d.macd(up)
        dif_down, _, _ = d.macd(down)
        assert dif_up.iloc[-1] > 0.0
        assert dif_down.iloc[-1] < 0.0


class TestPeakTroughDivergence:
    def test_bearish_rsi_divergence(self) -> None:
        d = _detector()
        close = pd.Series(_two_peak_bearish_prices())
        events = d.detect(close, d.rsi(close), indicator="rsi")
        bearish = [e for e in events if e.direction == "bearish"]
        assert bearish, f"应检出 RSI 顶背离: {events}"
        assert all(e.magnitude > 0.0 for e in bearish)
        assert all(e.indicator == "rsi" for e in bearish)

    def test_bullish_macd_divergence(self) -> None:
        d = _detector()
        down1 = [100.0 - 0.5 * i for i in range(20)]  # →90.5 急跌（T1）
        upr = [down1[-1] + 0.4 * i for i in range(1, 11)]
        creep: list[float] = []
        v = upr[-1]
        for i in range(24):  # 混合阴跌 →86.9（T2 价更低）
            v += -0.55 if i % 3 != 2 else 0.15
            creep.append(v)
        tail = [creep[-1] + 0.4 * i for i in range(1, 6)]
        close = pd.Series(down1 + upr + creep + tail)
        dif, _, _ = d.macd(close)
        events = d.detect(close, dif, indicator="macd")
        bullish = [e for e in events if e.direction == "bullish"]
        assert bullish, f"应检出 MACD 底背离: {events}"

    def test_no_divergence_when_confirmed(self) -> None:
        d = _detector()
        close = pd.Series([100.0 + 0.4 * i for i in range(50)])  # 单边强趋势
        events = d.detect(close, d.rsi(close), indicator="rsi")
        assert events == []

    def test_cvd_leg_supported(self) -> None:
        d = _detector()
        close = pd.Series(_two_peak_bearish_prices())
        cvd = pd.Series(np.linspace(1000.0, 100.0, len(close)))  # 量差一路走弱
        events = d.detect(close, cvd, indicator="cvd")
        assert any(e.direction == "bearish" and e.indicator == "cvd" for e in events)

    def test_divergence_resolution(self) -> None:
        # 第一次温和拉升（RSI≈70）→背离→随后强劲单边拉（RSI→100 反超）→化解
        up1: list[float] = []
        v = 100.0
        for i in range(20):
            v += 0.5 if i % 3 != 2 else -0.1
            up1.append(v)
        down = [up1[-1] - 0.4 * i for i in range(1, 11)]
        creep: list[float] = []
        v = down[-1]
        for i in range(24):
            v += 0.45 if i % 3 != 2 else -0.15
            creep.append(v)
        dip = [creep[-1] - 0.3 * i for i in range(1, 6)]
        rally = [dip[-1] + 0.8 * i for i in range(1, 31)]  # 持续强势反超（RSI→99）→ 化解
        close = pd.Series(up1 + down + creep + dip + rally)
        d = _detector()
        events = d.detect(close, d.rsi(close), indicator="rsi")
        bearish = [e for e in events if e.direction == "bearish"]
        assert bearish
        assert any(e.resolved for e in bearish)


class TestProbabilityTables:
    def test_reversal_probability_table(self) -> None:
        d = _detector()
        assert d.reversal_probability(1) == pytest.approx(0.35)
        assert d.reversal_probability(2) == pytest.approx(0.55)
        assert d.reversal_probability(3) == pytest.approx(0.72)
        assert d.reversal_probability(9) == pytest.approx(0.72)  # 钳制到表尾

    def test_cascade_probability(self) -> None:
        d = _detector()
        full = d.cascade_probability(
            {"5min": "bearish", "30min": "bearish", "60min": "bearish", "daily": "bearish"},
            direction="bearish",
        )
        assert full.aligned_levels == 4
        assert full.probability >= 0.60
        partial = d.cascade_probability({"5min": "bearish", "30min": "bullish", "daily": None}, direction="bearish")
        assert partial.aligned_levels == 1
        assert partial.probability < full.probability

    def test_scan_counts_and_probability(self) -> None:
        d = _detector()
        close = pd.Series(_two_peak_bearish_prices())
        result = d.scan(close)
        assert result.top_divergence_count >= 1
        assert 0.0 < result.top_reversal_probability <= 1.0


class TestFailClosed:
    def test_short_series(self) -> None:
        d = _detector()
        with pytest.raises(ValueError):
            d.detect(pd.Series([1.0, 2.0, 3.0]), pd.Series([1.0, 2.0, 3.0]), indicator="rsi")

    def test_nan_rejected(self) -> None:
        d = _detector()
        close = pd.Series([float(i) for i in range(30)])
        ind = close.copy()
        ind.iloc[10] = float("nan")
        with pytest.raises(ValueError):
            d.detect(close, ind, indicator="rsi")

    def test_unknown_indicator_and_bad_direction(self) -> None:
        d = _detector()
        close = pd.Series([float(i) for i in range(30)])
        with pytest.raises(ValueError):
            d.detect(close, close, indicator="boll")
        with pytest.raises(ValueError):
            d.cascade_probability({"5min": "up"}, direction="up")

    def test_config_validation(self) -> None:
        with pytest.raises(ValueError):
            DivergenceConfig(rsi_period=0)
        with pytest.raises(ValueError):
            DivergenceConfig(macd_fast=26, macd_slow=12)
        with pytest.raises(ValueError):
            DivergenceConfig(reversal_probability_table={1: 1.5})
        with pytest.raises(ValueError):
            DivergenceConfig(cascade_probability_table={1: 0.5, 2: 0.3})  # 须非递减


class TestContract:
    def test_results_frozen_and_json_serializable(self) -> None:
        d = _detector()
        close = pd.Series(_two_peak_bearish_prices())
        result = d.scan(close)
        assert dataclasses.is_dataclass(result)
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.top_divergence_count = 0  # type: ignore[misc]
        json.dumps(result.to_dict())
        casc = d.cascade_probability({"5min": "bullish"}, direction="bullish")
        json.dumps(casc.to_dict())
