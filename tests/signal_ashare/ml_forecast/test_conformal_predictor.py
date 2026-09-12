# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [TTL] permanent
"""共形预测器（BM-SEL-14，MOD-SIG-044）单元测试——split-conformal 标准算法/rolling 基线/覆盖率。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.conformal_predictor import (
    RollingConformalCalibrator,
    SplitConformalPredictor,
    conformal_band_around_quantiles,
    empirical_coverage,
)


class TestSplitConformal:
    def test_margin_is_kth_score(self):
        """n=19, α=0.05 → k=⌈20×0.95⌉=19 → margin=最大残差。"""
        preds = [0.0] * 19
        actuals = list(np.linspace(-1.0, 1.0, 19))  # 残差 max=1.0
        m = SplitConformalPredictor(alpha=0.05).fit(preds, actuals)
        assert m.margin == pytest.approx(1.0)

    def test_interval(self):
        m = SplitConformalPredictor(alpha=0.05).fit([0.0] * 50, np.random.default_rng(1).normal(0, 0.01, 50))
        iv = m.predict_interval(0.5)
        assert iv.lower < iv.point < iv.upper
        assert iv.margin == pytest.approx((iv.upper - iv.lower) / 2)
        assert iv.n_calibration == 50
        assert iv.alpha == pytest.approx(0.05)

    def test_marginal_coverage_guarantee(self):
        """标准性质：可交换数据上经验覆盖率 ≥ 1−α（大样本口径）。"""
        rng = np.random.default_rng(23)
        n_cal, n_test = 500, 2000
        cal = rng.normal(0.0, 1.0, n_cal)
        test = rng.normal(0.0, 1.0, n_test)
        m = SplitConformalPredictor(alpha=0.05).fit(np.zeros(n_cal), cal)
        iv = m.predict_interval(0.0)
        cov = empirical_coverage([iv.lower] * n_test, [iv.upper] * n_test, test)
        assert cov >= 0.93  # 名义 0.95，抽样噪声容差

    def test_unfitted_raises(self):
        with pytest.raises(ValueError):
            SplitConformalPredictor().predict_interval(0.0)

    def test_invalid_alpha_and_empty(self):
        with pytest.raises(ValueError):
            SplitConformalPredictor(alpha=1.5)
        with pytest.raises(ValueError):
            SplitConformalPredictor().fit([], [])
        with pytest.raises(ValueError):
            SplitConformalPredictor().fit([0.0] * 5, [0.0] * 3)


class TestRollingConformal:
    def test_not_ready_returns_none(self):
        cal = RollingConformalCalibrator(window=100, min_samples=10)
        for i in range(5):
            cal.update(0.0, 0.01)
        assert cal.margin() is None
        assert cal.predict_interval(0.0) is None

    def test_margin_after_ready(self):
        cal = RollingConformalCalibrator(window=100, min_samples=10, alpha=0.10)
        for i in range(30):
            cal.update(0.0, 0.01 * (1 if i % 2 == 0 else -1))
        m = cal.margin()
        assert m == pytest.approx(0.01)
        iv = cal.predict_interval(0.2)
        assert iv is not None
        assert iv.lower == pytest.approx(0.19)

    def test_window_evicts_old(self):
        cal = RollingConformalCalibrator(window=5, min_samples=2, alpha=0.5)
        for v in [1.0, 1.0, 1.0, 1.0, 1.0]:
            cal.update(0.0, v)
        for v in [0.1, 0.1, 0.1, 0.1, 0.1]:
            cal.update(0.0, v)
        assert cal.sample_count == 5  # maxlen 驱逐
        assert cal.margin() == pytest.approx(0.1)  # 旧大残差已驱逐

    def test_invalid_params(self):
        with pytest.raises(ValueError):
            RollingConformalCalibrator(window=0)
        with pytest.raises(ValueError):
            RollingConformalCalibrator(min_samples=0)


class TestBandAndCoverage:
    def test_band_widens(self):
        lo, hi = conformal_band_around_quantiles(-0.02, 0.025, 0.01)
        assert lo == pytest.approx(-0.03)
        assert hi == pytest.approx(0.035)

    def test_band_inverted_raises(self):
        with pytest.raises(ValueError):
            conformal_band_around_quantiles(0.03, -0.03, 0.01)

    def test_empirical_coverage(self):
        assert empirical_coverage([0, 0], [1, 2], [0.5, 3.0]) == pytest.approx(0.5)

    def test_coverage_input_errors(self):
        with pytest.raises(ValueError):
            empirical_coverage([], [], [])
        with pytest.raises(ValueError):
            empirical_coverage([0.0], [1.0, 2.0], [0.5])
