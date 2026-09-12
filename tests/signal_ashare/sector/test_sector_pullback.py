"""回踩质量 A/B/C 判定 单元测试（22 号 spec §3.1②）"""

import pytest

from zephyr.signal_ashare.sector_pullback import (
    VOLUME_EXPANDING,
    VOLUME_MIXED,
    VOLUME_SHRINKING,
    classify_volume_pattern,
    fib_retrace_ratio,
    grade_pullback,
    pullback_action,
)


class TestFibRetraceRatio:
    def test_half_retrace(self):
        # high=110, low=100, current=105 → (110-105)/(110-100) = 0.5
        assert fib_retrace_ratio(110.0, 100.0, 105.0) == pytest.approx(0.5)

    def test_deep_retrace_618(self):
        assert fib_retrace_ratio(110.0, 100.0, 103.82) == pytest.approx(0.618, abs=1e-3)

    def test_no_pullback_when_price_above_high(self):
        assert fib_retrace_ratio(110.0, 100.0, 112.0) == 0.0

    def test_full_retrace_at_swing_low(self):
        assert fib_retrace_ratio(110.0, 100.0, 100.0) == pytest.approx(1.0)

    def test_invalid_swing_raises(self):
        with pytest.raises(ValueError, match="swing_high"):
            fib_retrace_ratio(100.0, 100.0, 99.0)
        with pytest.raises(ValueError, match="swing_high"):
            fib_retrace_ratio(99.0, 100.0, 98.0)


class TestClassifyVolumePattern:
    def test_shrinking_sequence_to_35_50_pct(self):
        """spec 量能衰减范式：Day6:80%→Day9:35% 逐日递减至 50 日均量 35-50%"""
        assert classify_volume_pattern([0.80, 0.60, 0.45, 0.35]) == VOLUME_SHRINKING

    def test_shrinking_boundary_at_50_pct(self):
        assert classify_volume_pattern([0.7, 0.5]) == VOLUME_SHRINKING

    def test_decreasing_but_not_below_50_is_mixed(self):
        """递减但末段未降至 50% 以下 → 混合"""
        assert classify_volume_pattern([0.9, 0.7, 0.6]) == VOLUME_MIXED

    def test_expanding_latest_above_ma(self):
        """回踩放量（最新量 >50 日均量）= 派发"""
        assert classify_volume_pattern([0.6, 0.8, 1.2]) == VOLUME_EXPANDING

    def test_strictly_increasing_is_expanding(self):
        assert classify_volume_pattern([0.3, 0.5, 0.7]) == VOLUME_EXPANDING

    def test_mixed_pattern(self):
        """部分日放量但不破支撑 → 混合"""
        assert classify_volume_pattern([0.6, 0.4, 0.55]) == VOLUME_MIXED

    def test_empty_is_mixed(self):
        assert classify_volume_pattern([]) == VOLUME_MIXED

    def test_single_low_volume_is_mixed_conservative(self):
        """单日数据不足以判序列，保守按混合"""
        assert classify_volume_pattern([0.4]) == VOLUME_MIXED


class TestGradePullback:
    def test_grade_a_all_dimensions_aligned(self):
        """A：Fib≤50% + 缩量序列 + 板块强度≥70 + 健康时间窗"""
        assert grade_pullback(0.45, VOLUME_SHRINKING, 75.0, 5) == "A"

    def test_grade_b_aligned(self):
        """B：Fib 50-61.8% + 混合量能 + 板块强度 40-70"""
        assert grade_pullback(0.55, VOLUME_MIXED, 50.0, 5) == "B"

    def test_grade_c_deep_fib(self):
        """C：Fib >61.8%（即使量能与强度都好也降级）"""
        assert grade_pullback(0.65, VOLUME_SHRINKING, 80.0, 5) == "C"

    def test_grade_c_structure_break_786(self):
        """>78.6% 趋势结构破坏"""
        assert grade_pullback(0.80, VOLUME_SHRINKING, 80.0, 5) == "C"

    def test_grade_c_expanding_volume(self):
        """回踩放量 = 机构派发 → C"""
        assert grade_pullback(0.40, VOLUME_EXPANDING, 80.0, 5) == "C"

    def test_grade_c_weak_sector_strength(self):
        """板块强度 <40 → C（三维取最弱档）"""
        assert grade_pullback(0.40, VOLUME_SHRINKING, 30.0, 5) == "C"

    def test_grade_c_rotation_warning(self):
        """轮动预警触发 → 强度维直接 C"""
        assert grade_pullback(0.40, VOLUME_SHRINKING, 80.0, 5, rotation_warning=True) == "C"

    def test_worst_dimension_decides(self):
        """三维错位取最弱档：A 深度 + A 量能 + B 强度 → B"""
        assert grade_pullback(0.45, VOLUME_SHRINKING, 50.0, 5) == "B"

    def test_time_window_too_short_not_graded(self):
        """<2 交易日属盘中洗盘非真回踩"""
        assert grade_pullback(0.45, VOLUME_SHRINKING, 80.0, 1) is None
        assert grade_pullback(0.45, VOLUME_SHRINKING, 80.0, 0) is None

    def test_time_window_stale_not_graded(self):
        """>15 交易日转横盘整理，回踩失效"""
        assert grade_pullback(0.45, VOLUME_SHRINKING, 80.0, 16) is None

    def test_time_window_boundaries(self):
        """2 与 15 交易日边界可评级"""
        assert grade_pullback(0.45, VOLUME_SHRINKING, 80.0, 2) == "A"
        assert grade_pullback(0.45, VOLUME_SHRINKING, 80.0, 15) == "A"

    def test_strength_boundary_70(self):
        assert grade_pullback(0.45, VOLUME_SHRINKING, 70.0, 5) == "A"
        assert grade_pullback(0.45, VOLUME_SHRINKING, 69.9, 5) == "B"


class TestPullbackAction:
    @pytest.mark.parametrize(
        ("grade", "expected"),
        [
            ("A", "FULL_POSITION_PRIORITY"),
            ("B", "HALF_POSITION_STAGED"),
            ("C", "WATCH_OR_DOWNGRADE"),
            (None, "WATCH_OR_DOWNGRADE"),
        ],
    )
    def test_action_mapping(self, grade, expected):
        assert pullback_action(grade) == expected
