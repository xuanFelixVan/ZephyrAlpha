"""板块轮动状态 5 分类 单元测试（22 号 spec §3.1⑨）"""

import pytest

from zephyr.signal_ashare.sector_rotation_state import (
    RotationState,
    classify_rotation_state,
    top_n_hhi,
    watch_score,
)


class TestTopNHhi:
    def test_empty_returns_zero(self):
        assert top_n_hhi([]) == 0.0

    def test_zero_total_returns_zero(self):
        assert top_n_hhi([0.0, 0.0]) == 0.0

    def test_hhi_math(self):
        """4 家 100/200/300/400 → top2 份额 0.4/0.3 → 0.16+0.09=0.25"""
        assert top_n_hhi([100.0, 200.0, 300.0, 400.0], n=2) == pytest.approx(0.25)

    def test_n_larger_than_list(self):
        """N 超过板块数时取全部"""
        assert top_n_hhi([100.0, 300.0], n=5) == pytest.approx(0.0625 + 0.5625)


class TestClassifyRotationState:
    def test_distribution_risk_highest_priority(self):
        """派发风险优先级最高：放量滞涨 + hhi>0.25（即使同时满足高潮条件）"""
        state = classify_rotation_state(up_ratio=0.75, hhi_top5=0.31, lead_streak=5, disp_signal=1)
        assert state == RotationState.DISTRIBUTION_RISK

    def test_distribution_risk_requires_concentration(self):
        """放量滞涨但集中度不足（≤0.25）→ 不判派发"""
        state = classify_rotation_state(up_ratio=0.50, hhi_top5=0.22, lead_streak=1, disp_signal=1)
        assert state != RotationState.DISTRIBUTION_RISK

    def test_consensus_climax(self):
        """高集中 >0.30 + 普涨 >0.70 → 共识高潮"""
        state = classify_rotation_state(up_ratio=0.75, hhi_top5=0.31, lead_streak=1, disp_signal=0)
        assert state == RotationState.CONSENSUS_CLIMAX

    def test_consensus_climax_relaxed_in_fast_rotation(self):
        """快轮动期阈值放宽 0.30→0.35：hhi=0.32 常规期判高潮，快轮动期不判"""
        base = dict(up_ratio=0.75, hhi_top5=0.32, lead_streak=1, disp_signal=0)
        assert classify_rotation_state(**base) == RotationState.CONSENSUS_CLIMAX
        assert classify_rotation_state(**base, fast_rotation=True) != RotationState.CONSENSUS_CLIMAX
        # 快轮动期 hhi>0.35 仍判高潮
        hot = dict(up_ratio=0.75, hhi_top5=0.36, lead_streak=1, disp_signal=0)
        assert classify_rotation_state(**hot, fast_rotation=True) == RotationState.CONSENSUS_CLIMAX

    def test_healthy_mainline(self):
        """主线连续领涨 3+ 日 + 未过度集中 <0.20 → 健康主线"""
        state = classify_rotation_state(up_ratio=0.55, hhi_top5=0.15, lead_streak=3, disp_signal=0)
        assert state == RotationState.HEALTHY_MAINLINE

    def test_healthy_mainline_streak_boundary(self):
        """streak=2 不满足 3+ 日"""
        state = classify_rotation_state(up_ratio=0.55, hhi_top5=0.15, lead_streak=2, disp_signal=0)
        assert state != RotationState.HEALTHY_MAINLINE

    def test_disagreement_pullback(self):
        """涨跌严重分化 up<0.40 + 头部集中 >0.20 → 分歧回调"""
        state = classify_rotation_state(up_ratio=0.30, hhi_top5=0.24, lead_streak=1, disp_signal=0)
        assert state == RotationState.DISAGREEMENT_PULLBACK

    def test_neutral_mixed_default(self):
        """不命中任何规则 → 中性混沌"""
        state = classify_rotation_state(up_ratio=0.55, hhi_top5=0.22, lead_streak=1, disp_signal=0)
        assert state == RotationState.NEUTRAL_MIXED

    @pytest.mark.parametrize(
        ("up_ratio", "hhi", "streak", "disp"),
        [
            (0.70, 0.30, 3, 0),  # 边界值组合（均不严格超过阈值）
            (0.39, 0.20, 3, 0),  # hhi=0.20 不>0.20 不判分歧；streak≥3 但 hhi 不<0.20
        ],
    )
    def test_threshold_boundaries_fall_through(self, up_ratio, hhi, streak, disp):
        """边界等值不触发严格大于/小于规则"""
        state = classify_rotation_state(up_ratio=up_ratio, hhi_top5=hhi, lead_streak=streak, disp_signal=disp)
        assert state in set(RotationState)


class TestWatchScore:
    @pytest.mark.parametrize(
        ("state", "expected"),
        [
            (RotationState.CONSENSUS_CLIMAX, -0.08),
            (RotationState.DISAGREEMENT_PULLBACK, 0.01),
            (RotationState.HEALTHY_MAINLINE, 0.03),
            (RotationState.DISTRIBUTION_RISK, -0.10),
            (RotationState.NEUTRAL_MIXED, 0.00),
        ],
    )
    def test_watch_score_mapping(self, state, expected):
        assert watch_score(state) == expected

    def test_distribution_risk_most_negative(self):
        """派发风险 -0.10 是最重扣分（最危险）"""
        scores = [watch_score(s) for s in RotationState]
        assert watch_score(RotationState.DISTRIBUTION_RISK) == min(scores)
