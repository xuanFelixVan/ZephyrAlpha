# [A_test] module_id: MOD-SIG-099 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-099 | docs/03_modules/_domain_signal/extreme_sentiment_reversal_detector/blueprint.md
# [MODULE] tests.signal_ashare.test_extreme_sentiment_reversal_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""极端情绪反转与恐慌底部检测模型（MOD-SIG-099，B10-01369）施工验证测试。

覆盖：
- 双冰点：情绪冰点（≤22% 分位）×指数冰点（RSI14<30）配对、≤2 日滞后配对、
  修复概率查表门槛、无冰点后未确认；
- Capitulation 打分卡：跌幅/量能/广度三维查表与边界、总分；
- Shakeout vs 真破位：收回比例 >0.5/<0.2/其间/未破位四态；
- 综合 detect：反转成立（双冰点+打分卡≥70+非真破位）、真破位阻断、降级注解；
- fail-closed：不等长/短历史/非有限/非法价格量广度/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.extreme_sentiment_reversal_detector import (
    ExtremeSentimentReversalDetector,
    SentimentReversalConfig,
)

N = 60


def _engine() -> ExtremeSentimentReversalDetector:
    return ExtremeSentimentReversalDetector(SentimentReversalConfig())


def _sentiment_normal() -> list[float]:
    """缓升情绪序列（无冰点）。"""
    return [50.0 + 0.5 * i for i in range(N)]


def _sentiment_ice_now() -> list[float]:
    """末日极端低情绪（冰点）。"""
    s = _sentiment_normal()
    s[-1] = 5.0
    return s


def _closes_declining(final_drop: float = 0.03) -> list[float]:
    """稳降收盘序列（RSI 深度超卖），末日放大跌幅 final_drop。"""
    closes = [200.0 - i for i in range(N - 1)]
    closes.append(closes[-1] * (1.0 - final_drop))
    return closes


class TestConfigValidation:
    def test_default_config_ok(self) -> None:
        SentimentReversalConfig()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("sentiment_ice_percentile", 0.0),
            ("sentiment_ice_percentile", 0.5),
            ("min_history", 29),
            ("rsi_period", 1),
            ("rsi_ice_threshold", 0.0),
            ("rsi_ice_threshold", 55.0),
            ("double_ice_max_lag_days", -1),
            ("repair_prob_threshold", 0.0),
            ("repair_prob_threshold", 1.0),
            ("capitulation_threshold", 0.0),
            ("capitulation_threshold", 100.1),
            ("volume_avg_window", 4),
            ("shakeout_recovery_ratio", 0.2),
            ("true_breakdown_ratio", 0.5),
        ],
    )
    def test_invalid_config_raises(self, field: str, value: float) -> None:
        with pytest.raises(ValueError):
            SentimentReversalConfig(**{field: value})

    def test_repair_table_key_gap_raises(self) -> None:
        with pytest.raises(ValueError):
            SentimentReversalConfig(repair_prob_by_lag={0: 0.72, 2: 0.71})

    def test_repair_table_value_range_raises(self) -> None:
        with pytest.raises(ValueError):
            SentimentReversalConfig(repair_prob_by_lag={0: 1.2, 1: 0.74, 2: 0.71})


class TestDoubleIce:
    def test_both_ice_now_confirmed_lag0(self) -> None:
        st = _engine().detect_double_ice(_sentiment_ice_now(), _closes_declining())
        assert st.sentiment_ice_now is True
        assert st.index_ice_now is True
        assert st.paired is True
        assert st.lag_days == 0
        assert st.repair_probability == pytest.approx(0.72)
        assert st.confirmed is True

    def test_lag2_pairing_confirmed(self) -> None:
        # 指数冰点在倒数第 3 根（13 连阴 RSI≈17），随后 2 根强反弹 RSI 回到 30 上方；
        # 情绪冰点在末日 → 滞后 2 日配对
        closes = [100.0 + 0.5 * i for i in range(45)]
        closes += [closes[-1] - 1.5 * k for k in range(1, 14)]  # 45..57 连阴
        closes += [closes[-1] + 6.0, closes[-1] + 12.0]  # 58/59 强反弹
        st = _engine().detect_double_ice(_sentiment_ice_now(), closes)
        assert st.sentiment_ice_now is True
        assert st.index_ice_now is False
        assert st.paired is True
        assert st.lag_days == 2
        assert st.repair_probability == pytest.approx(0.71)
        assert st.confirmed is True

    def test_no_ice_not_confirmed(self) -> None:
        s = _sentiment_normal()
        closes = [100.0 + 0.5 * i for i in range(N)]  # 稳涨 → RSI 高位
        st = _engine().detect_double_ice(s, closes)
        assert st.sentiment_ice_now is False
        assert st.index_ice_now is False
        assert st.paired is False
        assert st.confirmed is False
        assert st.repair_probability is None

    def test_repair_prob_below_threshold_not_confirmed(self) -> None:
        cfg = SentimentReversalConfig(repair_prob_by_lag={0: 0.65, 1: 0.74, 2: 0.71})
        st = ExtremeSentimentReversalDetector(cfg).detect_double_ice(_sentiment_ice_now(), _closes_declining())
        assert st.paired is True
        assert st.confirmed is False

    def test_unequal_length_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().detect_double_ice([1.0] * N, [1.0] * (N + 1))

    def test_short_history_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().detect_double_ice([1.0] * 20, [1.0] * 20)


class TestCapitulationScorecard:
    def test_full_panic_scores_100(self) -> None:
        card = _engine().capitulation_score(-0.06, 3.0, 0.05)
        assert card.drop_points == 40.0
        assert card.volume_points == 30.0
        assert card.breadth_points == 30.0
        assert card.total == pytest.approx(100.0)
        assert card.is_capitulation is True

    def test_mid_tier_scores(self) -> None:
        card = _engine().capitulation_score(-0.03, 2.0, 0.20)
        assert card.drop_points == 32.0
        assert card.volume_points == 26.0
        assert card.breadth_points == 22.0
        assert card.total == pytest.approx(80.0)
        assert card.is_capitulation is True

    def test_calm_day_zero(self) -> None:
        card = _engine().capitulation_score(-0.005, 1.0, 0.55)
        assert card.total == pytest.approx(0.0)
        assert card.is_capitulation is False

    def test_boundary_drop_1pct(self) -> None:
        card = _engine().capitulation_score(-0.01, 1.19, 0.31)
        assert card.drop_points == 10.0
        assert card.volume_points == 0.0
        assert card.breadth_points == 0.0

    @pytest.mark.parametrize(
        "drop,vol,adv",
        [(-0.02, 0.0, 0.5), (-0.02, 1.0, 1.2), (-0.02, 1.0, -0.1), (float("nan"), 1.0, 0.5)],
    )
    def test_invalid_inputs_raise(self, drop: float, vol: float, adv: float) -> None:
        with pytest.raises(ValueError):
            _engine().capitulation_score(drop, vol, adv)


class TestBreakdownVerdict:
    def test_shakeout(self) -> None:
        v = _engine().classify_breakdown(level=100.0, day_low=90.0, close=97.0)
        assert v.kind == "shakeout"
        assert v.recovery_ratio == pytest.approx(0.7)

    def test_true_breakdown(self) -> None:
        v = _engine().classify_breakdown(level=100.0, day_low=90.0, close=91.0)
        assert v.kind == "true_breakdown"
        assert v.recovery_ratio == pytest.approx(0.1)

    def test_undetermined(self) -> None:
        v = _engine().classify_breakdown(level=100.0, day_low=90.0, close=94.0)
        assert v.kind == "undetermined"
        assert v.recovery_ratio == pytest.approx(0.4)

    def test_no_breakdown(self) -> None:
        v = _engine().classify_breakdown(level=100.0, day_low=101.0, close=102.0)
        assert v.kind == "none"
        assert v.recovery_ratio is None

    def test_close_above_level_full_recovery(self) -> None:
        v = _engine().classify_breakdown(level=100.0, day_low=95.0, close=101.0)
        assert v.kind == "shakeout"
        assert v.recovery_ratio == pytest.approx(1.2)

    @pytest.mark.parametrize(
        "level,low,close",
        [(0.0, 90.0, 95.0), (100.0, 0.0, 95.0), (100.0, 90.0, 0.0), (100.0, 95.0, 90.0)],
    )
    def test_invalid_raises(self, level: float, low: float, close: float) -> None:
        with pytest.raises(ValueError):
            _engine().classify_breakdown(level, low, close)


class TestDetect:
    def _series(self, final_drop: float = 0.03) -> tuple:
        closes = _closes_declining(final_drop)
        lows = [c * 0.995 for c in closes]
        volumes = [1000.0] * (N - 1) + [3000.0]
        advances = [0.5] * (N - 1) + [0.05]
        return closes, lows, volumes, advances

    def test_reversal_detected_with_shakeout(self) -> None:
        closes, lows, volumes, advances = self._series(0.031)  # 末日跌幅 −3.1% → 32 分档
        prev_close = closes[-2]
        lows[-1] = prev_close * 0.90  # 破位 10%，收回 (0.969-0.90)/0.10≈0.69 → shakeout
        rep = _engine().detect(
            _sentiment_ice_now(),
            closes,
            lows,
            volumes,
            advances,
            support_level=prev_close,
        )
        assert rep.double_ice.confirmed is True
        assert rep.capitulation.is_capitulation is True
        assert rep.verdict is not None and rep.verdict.kind == "shakeout"
        assert rep.reversal_detected is True
        # confidence = (32+30+30)/100 × 0.72
        assert rep.confidence == pytest.approx(0.92 * 0.72)

    def test_true_breakdown_blocks_reversal(self) -> None:
        closes, lows, volumes, advances = self._series(0.077)
        prev_close = closes[-2]
        lows[-1] = prev_close * 0.90
        closes[-1] = prev_close * 0.908  # 收回 (0.908-0.90)/0.10=0.08 → 真破位
        rep = _engine().detect(
            _sentiment_ice_now(),
            closes,
            lows,
            volumes,
            advances,
            support_level=prev_close,
        )
        assert rep.verdict is not None and rep.verdict.kind == "true_breakdown"
        assert rep.reversal_detected is False
        assert rep.confidence == pytest.approx(0.0)

    def test_no_double_ice_no_reversal(self) -> None:
        closes, lows, volumes, advances = self._series(0.03)
        rep = _engine().detect(
            _sentiment_normal(),
            closes,
            lows,
            volumes,
            advances,
        )
        assert rep.reversal_detected is False
        assert rep.verdict is None  # 未注入 support_level → 腿降级
        assert any("support_level" in n for n in rep.notes)

    def test_unequal_series_raises(self) -> None:
        closes, lows, volumes, advances = self._series()
        with pytest.raises(ValueError):
            _engine().detect(_sentiment_ice_now(), closes, lows[:-1], volumes, advances)


class TestContract:
    def test_frozen_and_json_serializable(self) -> None:
        card = _engine().capitulation_score(-0.06, 3.0, 0.05)
        with pytest.raises(dataclasses.FrozenInstanceError):
            card.total = 0.0  # type: ignore[misc]
        json.dumps(card.to_dict())
        st = _engine().detect_double_ice(_sentiment_ice_now(), _closes_declining())
        json.dumps(st.to_dict())
        v = _engine().classify_breakdown(100.0, 90.0, 97.0)
        json.dumps(v.to_dict())
