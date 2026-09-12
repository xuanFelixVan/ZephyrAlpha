"""调整周期进度追踪 单元测试（22 号 spec §3.1③，MOD-SIG-040）"""

import pytest

from zephyr.signal_ashare.sector_adjustment import (
    ACTION_ACTIVATE_PARTIAL,
    ACTION_BLOCK_DIP,
    ACTION_OBSERVE,
    adjustment_action,
    compute_adjustment_progress,
)


class TestComputeAdjustmentProgress:
    def test_fully_digested_returns_one(self):
        """时间窗满 + 回撤达标 + 扩散指标完全恢复 → 进度 1.0"""
        progress = compute_adjustment_progress(
            elapsed_days=20,
            drawdown_pct=0.15,
            nh_ratio_current=0.30,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(1.0)

    def test_adjustment_start_returns_zero(self):
        """调整第 0 天 + 零回撤 + 扩散指标在谷底 → 进度 0.0"""
        progress = compute_adjustment_progress(
            elapsed_days=0,
            drawdown_pct=0.0,
            nh_ratio_current=0.05,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.0)

    def test_dimension_weights(self):
        """三维权重 0.4/0.3/0.3：时间满 + 回撤满 + 扩散未恢复 → 0.7"""
        progress = compute_adjustment_progress(
            elapsed_days=20,
            drawdown_pct=0.15,
            nh_ratio_current=0.05,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.7)

    def test_time_progress_capped_at_one(self):
        """超窗交易日不溢出（elapsed=30 > expected=20 → time_prog=1）"""
        progress = compute_adjustment_progress(
            elapsed_days=30,
            drawdown_pct=0.0,
            nh_ratio_current=0.05,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.4)

    def test_drawdown_progress_partial(self):
        """回撤 7.5% / 目标 15% → dd_prog=0.5 → 0.3×0.5=0.15"""
        progress = compute_adjustment_progress(
            elapsed_days=0,
            drawdown_pct=0.075,
            nh_ratio_current=0.05,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.15)

    def test_breadth_recovery_partial(self):
        """扩散恢复 50%：(0.175-0.05)/(0.30-0.05)=0.5 → 0.3×0.5=0.15"""
        progress = compute_adjustment_progress(
            elapsed_days=0,
            drawdown_pct=0.0,
            nh_ratio_current=0.175,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.15)

    def test_breadth_recovery_clipped(self):
        """当前新高占比超峰值 → 恢复度 clip 到 1"""
        progress = compute_adjustment_progress(
            elapsed_days=0,
            drawdown_pct=0.0,
            nh_ratio_current=0.50,
            nh_ratio_trough=0.05,
            nh_ratio_peak=0.30,
        )
        assert progress == pytest.approx(0.3)

    def test_degenerate_peak_span_gives_zero_breadth(self):
        """peak ≤ trough 无法定义恢复 → 扩散维退化 0"""
        progress = compute_adjustment_progress(
            elapsed_days=10,
            drawdown_pct=0.075,
            nh_ratio_current=0.10,
            nh_ratio_trough=0.10,
            nh_ratio_peak=0.10,
        )
        assert progress == pytest.approx(0.4 * 0.5 + 0.3 * 0.5)

    def test_result_always_in_unit_interval(self):
        for elapsed in (0, 5, 20, 100):
            progress = compute_adjustment_progress(
                elapsed_days=elapsed,
                drawdown_pct=0.99,
                nh_ratio_current=0.9,
                nh_ratio_trough=0.01,
                nh_ratio_peak=0.3,
            )
            assert 0.0 <= progress <= 1.0


class TestAdjustmentAction:
    @pytest.mark.parametrize(
        ("progress", "expected"),
        [
            (1.0, ACTION_ACTIVATE_PARTIAL),
            (0.80, ACTION_ACTIVATE_PARTIAL),  # 边界：≥80% 激活
            (0.79, ACTION_OBSERVE),
            (0.40, ACTION_OBSERVE),  # 边界：<40% 才拦截
            (0.39, ACTION_BLOCK_DIP),
            (0.0, ACTION_BLOCK_DIP),
        ],
    )
    def test_action_thresholds(self, progress, expected):
        assert adjustment_action(progress) == expected
