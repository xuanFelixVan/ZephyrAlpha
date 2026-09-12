# [BLUEPRINT] MOD-SIG-040 | (auto-injected by S4 reconciler，gw-tdm-20260909 修正为模块级 ID) | §
# [TTL] permanent
# [DOMAIN] D_ASHARE_SIGNAL
# [TTL] permanent
"""调整周期追踪器 单元测试（市场级，复用 sector_adjustment 进度引擎，MOD-SIG-040）"""

import pytest

from zephyr.signal_ashare.adjustment_cycle_tracker import (
    AdjustmentCycleConfig,
    AdjustmentCycleDataError,
    AdjustmentCycleTracker,
    CyclePhase,
    DiffusionError,
    compute_diffusion_ratio,
    find_cycle_peak,
    track_adjustment_cycle,
    track_diffusion_progress,
)
from zephyr.signal_ashare.sector_adjustment import (
    ACTION_ACTIVATE_PARTIAL,
    ACTION_BLOCK_DIP,
)


def _steady_rise(n: int = 260) -> list[float]:
    """稳定慢涨（每日 +0.1%），无 ≥5% 回撤"""
    return [100.0 * 1.001**i for i in range(n)]


def _peak_then_decline(peak: float = 110.0, dd: float = 0.15, days: int = 20, base_days: int = 230) -> list[float]:
    """base_days 天 100 横盘 → 冲高至 peak → days 天线性回撤 dd"""
    closes = [100.0] * base_days + [peak]
    for i in range(1, days + 1):
        closes.append(peak * (1.0 - dd * i / days))
    return closes


class TestFindCyclePeak:
    def test_peak_inside_lookback(self):
        closes = [1.0, 2.0, 3.0, 2.0, 1.0]
        assert find_cycle_peak(closes, lookback=5) == 2

    def test_lookback_window_limits_search(self):
        closes = [1.0, 2.0, 3.0, 2.0, 1.0]
        # lookback=3 → 窗口 [3,2,1]（下标 2..4），峰值在下标 2
        assert find_cycle_peak(closes, lookback=3) == 2

    def test_new_high_at_tail(self):
        closes = _steady_rise(60)
        assert find_cycle_peak(closes, lookback=250) == 59


class TestTrackAdjustmentCycle:
    def test_no_adjustment_on_steady_rise(self):
        snap = track_adjustment_cycle(_steady_rise())
        assert snap.phase == CyclePhase.NO_ADJUSTMENT
        assert snap.progress == 0.0
        assert snap.action == "NONE"
        assert snap.drawdown_pct == 0.0
        assert 0.0 <= snap.confidence <= 1.0

    def test_complete_after_recovery_to_new_high(self):
        """深回撤（12% ≥ 5% 门槛）后创新高 → 调整完成 COMPLETE"""
        closes = [100.0] * 100
        for i in range(1, 11):  # 10 天回撤 12%
            closes.append(100.0 * (1.0 - 0.12 * i / 10))
        for i in range(1, 21):  # 20 天修复并创新高 101
            closes.append(88.0 + (101.0 - 88.0) * i / 20)
        snap = track_adjustment_cycle(closes)
        assert snap.phase == CyclePhase.COMPLETE
        assert snap.progress == 1.0
        assert snap.action == "NONE"

    def test_late_phase_with_breadth_recovery(self):
        """时间/回撤/扩散三维全恢复 → progress 1.0 → LATE + 激活分批"""
        closes = _peak_then_decline(dd=0.15, days=20)  # elapsed=20, dd=15%
        nh = [0.3] * 231 + [0.05] * 10 + [0.3] * 10  # 峰值 0.3 → 谷底 0.05 → 恢复 0.3
        snap = track_adjustment_cycle(closes, nh)
        assert snap.phase == CyclePhase.LATE
        assert snap.progress == pytest.approx(1.0)
        assert snap.action == ACTION_ACTIVATE_PARTIAL
        assert snap.days_elapsed == 20
        assert snap.drawdown_pct == pytest.approx(0.15)
        assert snap.peak_close == pytest.approx(110.0)

    def test_early_phase_blocks_dip_buying(self):
        """调整初期（elapsed=1, dd=8%）→ EARLY + 拦截低吸"""
        closes = [100.0] * 241 + [110.0, 101.2]  # 冲高后次日回撤 8%
        snap = track_adjustment_cycle(closes)
        assert snap.phase == CyclePhase.EARLY
        assert snap.progress < 0.4
        assert snap.action == ACTION_BLOCK_DIP
        assert snap.days_elapsed == 1

    def test_mid_phase_band(self):
        """中期带：elapsed=10, dd=12%（无扩散数据降级路径）→ 0.4 ≤ progress < 0.8"""
        closes = _peak_then_decline(dd=0.12, days=10, base_days=240)
        snap = track_adjustment_cycle(closes)
        # time_prog=0.5, dd_prog=0.8 → (0.4×0.5+0.3×0.8)/0.7 ≈ 0.6286
        assert snap.progress == pytest.approx((0.4 * 0.5 + 0.3 * 0.8) / 0.7)
        assert snap.phase == CyclePhase.MID

    def test_breadth_absent_renormalizes_weights(self):
        """无新高占比序列 → 广度维剔除，时间/回撤权重按 0.4:0.3 重归一"""
        closes = _peak_then_decline(dd=0.15, days=20)
        snap = track_adjustment_cycle(closes, None)
        assert snap.progress == pytest.approx(1.0)  # (0.4×1+0.3×1)/0.7
        assert snap.phase == CyclePhase.LATE

    def test_minor_pullback_not_adjustment(self):
        """回撤 <5% 门槛且未创新高 → NO_ADJUSTMENT（轻微回撤不算调整）"""
        closes = [100.0] * 100 + [110.0] + [107.0] * 5  # 回撤 2.7%
        snap = track_adjustment_cycle(closes)
        assert snap.phase == CyclePhase.NO_ADJUSTMENT

    def test_nh_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            track_adjustment_cycle(_steady_rise(60), [0.1] * 30)

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            track_adjustment_cycle([100.0] * 20)


class TestAdjustmentCycleTrackerLoader:
    def test_track_end_to_end_with_fake_query(self):
        closes = _peak_then_decline(dd=0.15, days=20)
        rows = "\n".join(f"2026-01-01\t{c:.4f}" for c in closes)
        tracker = AdjustmentCycleTracker(query_fn=lambda sql, timeout=30: rows)
        snap = tracker.track("000300", "2025-01-01", "2026-08-31")
        assert snap.phase == CyclePhase.LATE
        assert snap.action == ACTION_ACTIVATE_PARTIAL

    def test_empty_query_raises(self):
        tracker = AdjustmentCycleTracker(query_fn=lambda sql, timeout=30: "")
        with pytest.raises(AdjustmentCycleDataError):
            tracker.track("000300", "2025-01-01", "2026-08-31")

    def test_custom_config_passed_through(self):
        cfg = AdjustmentCycleConfig(min_drawdown=0.20)  # 门槛抬高 → 15% 回撤不算调整
        closes = _peak_then_decline(dd=0.15, days=20)
        rows = "\n".join(f"2026-01-01\t{c:.4f}" for c in closes)
        tracker = AdjustmentCycleTracker(query_fn=lambda sql, timeout=30: rows, config=cfg)
        snap = tracker.track("000300", "2025-01-01", "2026-08-31")
        assert snap.phase == CyclePhase.NO_ADJUSTMENT


# ── C6 扩散指标进度追踪（TDM-E-L2-03-1，2026-09-10 扩展）──


class TestDiffusionRatio:
    """compute_diffusion_ratio：占比计算与小样本 fail-closed。"""

    def test_basic_ratio(self):
        assert compute_diffusion_ratio(45, 80) == pytest.approx(0.5625)

    def test_zero_and_full(self):
        assert compute_diffusion_ratio(0, 50) == 0.0
        assert compute_diffusion_ratio(50, 50) == 1.0

    def test_small_panel_rejected(self):
        with pytest.raises(DiffusionError):
            compute_diffusion_ratio(3, 8)  # < min_members=10

    def test_count_exceeds_total_rejected(self):
        with pytest.raises(DiffusionError):
            compute_diffusion_ratio(11, 10)


class TestDiffusionProgress:
    """track_diffusion_progress：30/50/80 三线交叉语义。"""

    def test_low_trough_then_cross_50_confirms_end(self):
        v = track_diffusion_progress([0.25, 0.35, 0.52, 0.55])
        assert v.crossed_up_confirm is True
        assert v.ratio == 0.55

    def test_cross_50_without_low_band_no_signal(self):
        # 未经过 <30% 低谷，直接 45→55：不算"调整结束"确认
        v = track_diffusion_progress([0.45, 0.55])
        assert v.crossed_up_confirm is False

    def test_top_then_fall_below_80_confirms_top(self):
        v = track_diffusion_progress([0.85, 0.83, 0.78])
        assert v.crossed_down_top is True
        assert v.crossed_up_confirm is False

    def test_bands(self):
        v = track_diffusion_progress([0.25])
        assert v.in_low_band is True and v.in_top_band is False
        v2 = track_diffusion_progress([0.85])
        assert v2.in_top_band is True and v2.in_low_band is False

    def test_empty_rejected(self):
        with pytest.raises(DiffusionError):
            track_diffusion_progress([])

    def test_ratio_out_of_range_rejected(self):
        with pytest.raises(DiffusionError):
            track_diffusion_progress([0.5, 1.5])

    def test_boundary_50_is_inclusive_cross(self):
        # 恰好 0.50 视为上穿确认线（≥0.50）
        v = track_diffusion_progress([0.25, 0.50])
        assert v.crossed_up_confirm is True

    def test_boundary_80_stay_hot(self):
        # 恰好 0.80 不算掉头（严格 >0.80 才是峰顶带内）
        v = track_diffusion_progress([0.85, 0.80])
        assert v.crossed_down_top is True  # 0.80 ≤ top_band → 触发
        v2 = track_diffusion_progress([0.85, 0.81])
        assert v2.crossed_down_top is False  # 仍在峰顶带上方悬着
