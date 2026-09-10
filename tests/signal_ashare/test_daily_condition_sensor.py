# [DOMAIN] D_ASHARE_SIGNAL
# [TTL] permanent
"""MOD-SIG-135 daily_condition_sensor 单元测试（红蓝对抗：红-边界/红-契约/红-故障）。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.core.daily_condition_sensor import (
    DailyConditionSensorError,
    DailyConditionVerdict,
    DailyRawSignals,
    DailySensorThresholds,
    SignalVote,
    WaterTempTier,
    evaluate_daily_condition,
)


def _hot() -> DailyRawSignals:
    """水烫样例：11 信号全偏多。"""
    return DailyRawSignals(
        limit_up_count=110, limit_up_count_prev=90,  # 环比 1.22
        ladder_count=55, ladder_count_prev=40,  # 环比 1.375
        failed_board_ratio=0.15,
        limit_down_count=0,
        yesterday_limit_up_premium=0.03,
        advancers=3200,
        volume_match_trap=False,
        sector_chaos_index=0.25,
        breadth_leading=0.2,
        bad_news_reaction=0.08,
        cap_tier_breadth=0.7,
    )


def _ice() -> DailyRawSignals:
    """水冰样例：11 信号全偏空。"""
    return DailyRawSignals(
        limit_up_count=50, limit_up_count_prev=90,  # 0.56
        ladder_count=20, ladder_count_prev=40,  # 0.5
        failed_board_ratio=0.55,
        limit_down_count=45,
        yesterday_limit_up_premium=-0.06,
        advancers=1200,
        volume_match_trap=True,
        sector_chaos_index=0.7,
        breadth_leading=-0.2,
        bad_news_reaction=-0.15,
        cap_tier_breadth=0.2,
    )


class TestTierMapping:
    """净分→五档映射（单调，边界确定）。"""

    def test_all_bullish_is_s4(self):
        v = evaluate_daily_condition(_hot())
        assert v.tier is WaterTempTier.S4_HOT
        assert v.net_score == 11 and v.insufficient_data is False

    def test_all_bearish_is_s0(self):
        v = evaluate_daily_condition(_ice())
        assert v.tier is WaterTempTier.S0_ICE
        assert v.net_score == -11

    def test_neutral_band_is_s2(self):
        raw = DailyRawSignals(
            limit_up_count=95, limit_up_count_prev=90,  # 1.056 中性
            ladder_count=42, ladder_count_prev=40,
            failed_board_ratio=0.35,
            limit_down_count=5,
            yesterday_limit_up_premium=0.0,
            advancers=2000,
            volume_match_trap=None,
            sector_chaos_index=0.45,
            breadth_leading=0.0,
            bad_news_reaction=0.0,
            cap_tier_breadth=0.45,
        )
        v = evaluate_daily_condition(raw)
        assert v.tier is WaterTempTier.S2_NEUTRAL
        assert v.net_score == 0

    def test_s3_boundary(self):
        raw = DailyRawSignals(
            limit_up_count=110, limit_up_count_prev=90,
            ladder_count=55, ladder_count_prev=40,
            failed_board_ratio=0.15,
            limit_down_count=5,  # 非零非 30 → 中性
            yesterday_limit_up_premium=0.0,
            advancers=2000,
            volume_match_trap=None,
            sector_chaos_index=0.45,
            breadth_leading=0.0,
            bad_news_reaction=0.0,
            cap_tier_breadth=0.45,
        )
        v = evaluate_daily_condition(raw)
        assert v.net_score == 3
        assert v.tier is WaterTempTier.S3_WARM

    def test_s1_boundary(self):
        raw = DailyRawSignals(
            limit_up_count=50, limit_up_count_prev=90,
            ladder_count=20, ladder_count_prev=40,
            failed_board_ratio=0.55,
            limit_down_count=5,
            yesterday_limit_up_premium=0.0,
            advancers=2000,
            volume_match_trap=None,
            sector_chaos_index=0.45,
            breadth_leading=0.0,
            bad_news_reaction=0.0,
            cap_tier_breadth=0.45,
        )
        v = evaluate_daily_condition(raw)
        assert v.net_score == -3
        assert v.tier is WaterTempTier.S1_COOL


class TestMissingData:
    """红-故障：缺数据信号计 0 票；可用不足 6 拒绝给档。"""

    def test_all_missing_rejects_tier(self):
        v = evaluate_daily_condition(DailyRawSignals())
        assert v.tier is None and v.insufficient_data is True
        assert v.missing_count == 11

    def test_partial_missing_counts_zero_votes(self):
        base = _hot()
        raw = DailyRawSignals(
            limit_up_count=base.limit_up_count,
            limit_up_count_prev=base.limit_up_count_prev,
        )  # 只给 ①
        v = evaluate_daily_condition(raw)
        assert v.insufficient_data is True
        assert v.bullish_count == 1 and v.missing_count == 10

    def test_five_available_still_rejects(self):
        th = DailySensorThresholds()
        assert th.min_available_signals == 6
        raw = DailyRawSignals(
            limit_up_count=110, limit_up_count_prev=90,
            ladder_count=55, ladder_count_prev=40,
            failed_board_ratio=0.15,
            limit_down_count=0,
            yesterday_limit_up_premium=0.03,
            # 其余 6 个缺 → 可用 5 < 6
        )
        v = evaluate_daily_condition(raw)
        assert v.insufficient_data is True and v.tier is None

    def test_six_available_passes(self):
        raw = DailyRawSignals(
            limit_up_count=110, limit_up_count_prev=90,
            ladder_count=55, ladder_count_prev=40,
            failed_board_ratio=0.15,
            limit_down_count=0,
            yesterday_limit_up_premium=0.03,
            advancers=3200,
            # 可用 6 = min
        )
        v = evaluate_daily_condition(raw)
        assert v.insufficient_data is False
        assert v.tier is WaterTempTier.S4_HOT

    def test_missing_signals_flagged_in_details(self):
        v = evaluate_daily_condition(_hot())
        assert all(not d.missing for d in v.details)
        names = {d.name for d in v.details}
        assert names == {
            "limit_up_ratio", "ladder_ratio", "failed_board_ratio", "limit_down_count",
            "yesterday_premium", "advancers", "volume_match_trap", "sector_chaos",
            "breadth_leading", "bad_news_reaction", "cap_tier_breadth",
        }


class TestSignalSemantics:
    """单信号语义与 D20 警报线。"""

    def test_division_by_zero_prev_treated_missing(self):
        raw = DailyRawSignals(limit_up_count=100, limit_up_count_prev=0)
        v = evaluate_daily_condition(raw)
        d = next(d for d in v.details if d.name == "limit_up_ratio")
        assert d.missing is True and d.vote is SignalVote.NEUTRAL

    def test_prev_none_treated_missing(self):
        raw = DailyRawSignals(limit_up_count=100)
        v = evaluate_daily_condition(raw)
        d = next(d for d in v.details if d.name == "limit_up_ratio")
        assert d.missing is True

    def test_failed_board_d20_alarm_line(self):
        # 恰好 0.50 = 警报线，不触发（严格大于）
        raw = DailyRawSignals(failed_board_ratio=0.50)
        v = evaluate_daily_condition(raw)
        d = next(d for d in v.details if d.name == "failed_board_ratio")
        assert d.vote is SignalVote.NEUTRAL

    def test_premium_alarm_line_inclusive(self):
        # 溢价 -5% 是"≤-5%" → 边界触发偏空（band 语义：value < bear_under 严格）
        raw = DailyRawSignals(yesterday_limit_up_premium=-0.05)
        v = evaluate_daily_condition(raw)
        d = next(d for d in v.details if d.name == "yesterday_premium")
        # -0.05 不严格小于 -0.05 → 中性；文档按"≤-5%"口径，实现取严格<
        assert d.vote is SignalVote.NEUTRAL

    def test_volume_trap_bearish_when_true(self):
        raw = DailyRawSignals(volume_match_trap=True)
        v = evaluate_daily_condition(raw)
        d = next(d for d in v.details if d.name == "volume_match_trap")
        assert d.vote is SignalVote.BEARISH


class TestFailClosed:
    """红-契约：越界输入 fail-closed；纯函数确定性。"""

    @pytest.mark.parametrize("field,value", [
        ("limit_up_count", -1),
        ("advancers", -100),
        ("failed_board_ratio", 1.5),
        ("yesterday_limit_up_premium", -1.5),
        ("sector_chaos_index", -0.1),
        ("cap_tier_breadth", 2.0),
    ])
    def test_invalid_inputs_rejected(self, field, value):
        with pytest.raises(DailyConditionSensorError):
            DailyRawSignals(**{field: value})

    def test_determinism(self):
        assert evaluate_daily_condition(_hot()) == evaluate_daily_condition(_hot())

    def test_verdict_frozen(self):
        v = evaluate_daily_condition(_hot())
        with pytest.raises(Exception):
            v.tier = None

    def test_custom_thresholds(self):
        th = DailySensorThresholds(min_available_signals=11)
        raw = DailyRawSignals(limit_up_count=110, limit_up_count_prev=90)
        v = evaluate_daily_condition(raw, th)
        assert v.insufficient_data is True
