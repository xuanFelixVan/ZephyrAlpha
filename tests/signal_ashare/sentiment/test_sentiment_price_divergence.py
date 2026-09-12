# [A_test] module_id: MOD-SIG-101 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-101 | docs/03_modules/_domain_signal/sentiment_price_divergence/blueprint.md
# [MODULE] tests.signal_ashare.test_sentiment_price_divergence
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""情绪-价格背离指数模型（MOD-SIG-101，B10-01371）施工验证测试。

覆盖：
- z 分差：滚动窗 z 计算、零方差窗 z=0+notes 降级；
- SDI=ΔSentiment_z−ΔPrice_z：情绪急涨价格横盘 → bullish；镜像 → bearish；
  同向同步 → none；
- 置信度=min(|SDI|/scale,1) 钳制；direction=none 时 divergence=False；
- scan：逐根前视，仅收背离事件且 bar_index 正确；
- fail-closed：不等长/短历史/非有限/非正价格/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.sentiment_price_divergence import (
    SentimentPriceDivergence,
    SentimentPriceDivergenceConfig,
)

N = 70


def _engine() -> SentimentPriceDivergence:
    return SentimentPriceDivergence(SentimentPriceDivergenceConfig())


def _flat_prices() -> list[float]:
    return [100.0] * N


def _bullish_sentiment() -> list[float]:
    """尾段 5 根急涨的情绪序列（z 分差显著为正）。"""
    return [50.0] * (N - 5) + [60.0, 62.0, 64.0, 66.0, 68.0]


def _bearish_sentiment() -> list[float]:
    """尾段 5 根急跌的情绪序列（z 分差显著为负）。"""
    return [60.0] * (N - 5) + [50.0, 48.0, 46.0, 44.0, 42.0]


class TestConfigValidation:
    def test_default_config_ok(self) -> None:
        SentimentPriceDivergenceConfig()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("z_window", 9),
            ("delta_lag", 0),
            ("divergence_threshold", 0.0),
            ("confidence_scale", 0.0),
        ],
    )
    def test_invalid_config_raises(self, field: str, value: float) -> None:
        with pytest.raises(ValueError):
            SentimentPriceDivergenceConfig(**{field: value})


class TestCompute:
    def test_bullish_divergence(self) -> None:
        r = _engine().compute(_bullish_sentiment(), _flat_prices())
        assert r.direction == "bullish"
        assert r.divergence is True
        assert r.sdi > 1.0
        assert r.delta_sentiment_z > 0.0
        assert r.delta_price_z == pytest.approx(0.0)  # 恒定价格 → z=0
        assert r.confidence == pytest.approx(1.0)  # 钳制上限
        assert any("零方差" in n for n in r.notes)

    def test_bearish_divergence(self) -> None:
        r = _engine().compute(_bearish_sentiment(), _flat_prices())
        assert r.direction == "bearish"
        assert r.divergence is True
        assert r.sdi < -1.0
        assert r.delta_sentiment_z < 0.0
        assert r.confidence == pytest.approx(1.0)

    def test_synchronized_no_divergence(self) -> None:
        # 情绪与价格完全同形 → 两侧 z 相等 → SDI=0
        series = [50.0 + 0.3 * i for i in range(N)]
        r = _engine().compute(series, series)
        assert r.direction == "none"
        assert r.divergence is False
        assert r.sdi == pytest.approx(0.0, abs=1e-9)
        assert r.confidence == pytest.approx(0.0, abs=1e-9)

    def test_confidence_formula(self) -> None:
        # 大 scale 下置信度不触钳制 → confidence=|SDI|/scale 精确成立
        eng = SentimentPriceDivergence(SentimentPriceDivergenceConfig(confidence_scale=100.0))
        r = eng.compute(_bullish_sentiment(), _flat_prices())
        assert r.confidence == pytest.approx(abs(r.sdi) / 100.0)
        assert r.confidence < 1.0

    def test_unequal_length_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().compute([1.0] * N, [1.0] * (N + 1))

    def test_short_history_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().compute([1.0] * 30, [1.0] * 30)

    def test_non_finite_raises(self) -> None:
        bad = [1.0] * (N - 1) + [float("nan")]
        with pytest.raises(ValueError):
            _engine().compute(bad, _flat_prices())

    def test_non_positive_price_raises(self) -> None:
        prices = _flat_prices()
        prices[-1] = 0.0
        with pytest.raises(ValueError):
            _engine().compute(_bullish_sentiment(), prices)


class TestScan:
    def test_scan_collects_events_with_bar_index(self) -> None:
        events = _engine().scan(_bullish_sentiment(), _flat_prices())
        assert len(events) > 0
        assert all(e.direction != "none" for e in events)
        # 情绪尾段急涨 → 背离事件应出现在尾段
        assert max(e.bar_index for e in events) >= N - 5
        assert all(0 <= e.bar_index < N for e in events)

    def test_scan_synchronized_empty(self) -> None:
        series = [50.0 + 0.3 * i for i in range(N)]
        assert _engine().scan(series, series) == []

    def test_scan_validation(self) -> None:
        with pytest.raises(ValueError):
            _engine().scan([1.0] * 10, [1.0] * 10)


class TestContract:
    def test_frozen_and_json_serializable(self) -> None:
        r = _engine().compute(_bullish_sentiment(), _flat_prices())
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.sdi = 0.0  # type: ignore[misc]
        json.dumps(r.to_dict())
