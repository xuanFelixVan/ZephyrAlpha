# [BLUEPRINT] MOD-SIG-052 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §2
# [MODULE] tests.signal_ashare.test_adaptive_conformal_tcp_rm_ddci
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/signal_ashare/test_adaptive_conformal_tcp_rm_ddci.py -q
# [TTL] permanent

"""自适应保形 TCP-RM/DDCI（MOD-SIG-052）单元测试——加权分位数/未校准 fail-closed。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.adaptive_conformal_tcp_rm_ddci import (
    AdaptiveConformalTcpRmDdci,
)


class TestFailClosed:
    def test_interval_before_calibrate_raises(self):
        m = AdaptiveConformalTcpRmDdci()
        with pytest.raises(ValueError, match="未校准"):
            m.predict_interval(1.0)


class TestCalibrateValidation:
    def test_empty_residuals_rejected(self):
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci().calibrate(np.array([]))

    def test_alpha_bounds(self):
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci(alpha=0.0)
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci(alpha=1.0)

    def test_weight_length_mismatch_rejected(self):
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci().calibrate(np.abs(np.arange(5.0)), weights=np.ones(3))

    def test_negative_weights_rejected(self):
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci().calibrate(np.abs(np.arange(5.0)), weights=-np.ones(5))

    def test_all_zero_weights_rejected(self):
        with pytest.raises(ValueError):
            AdaptiveConformalTcpRmDdci().calibrate(np.abs(np.arange(5.0)), weights=np.zeros(5))


class TestWeightedQuantile:
    def test_unweighted_matches_split_conformal_scale(self):
        m = AdaptiveConformalTcpRmDdci(alpha=0.05)
        m.calibrate(np.abs(np.arange(1.0, 21.0)))
        interval = m.predict_interval(0.0)
        # k=⌈(n+1)(1−α)⌉=20 → 第 20 小值（与 SIG-044 split-conformal 同口径）
        assert interval.margin == pytest.approx(20.0)
        assert interval.lower == pytest.approx(-20.0)
        assert interval.upper == pytest.approx(20.0)

    def test_recent_heavy_weights_shrink_margin(self):
        residuals = np.concatenate([np.full(18, 10.0), np.full(2, 1.0)])
        uniform = AdaptiveConformalTcpRmDdci(alpha=0.2).calibrate(residuals)
        weighted = AdaptiveConformalTcpRmDdci(alpha=0.2).calibrate(
            residuals, weights=np.concatenate([np.full(18, 0.01), np.full(2, 1.0)])
        )
        assert weighted.margin < uniform.margin

    def test_interval_metadata(self):
        m = AdaptiveConformalTcpRmDdci(alpha=0.1)
        m.calibrate(np.abs(np.arange(1.0, 11.0)))
        interval = m.predict_interval(5.0)
        assert interval.point == 5.0
        assert interval.alpha == pytest.approx(0.1)
        assert interval.weighted is True
