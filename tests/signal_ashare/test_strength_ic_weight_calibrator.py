# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.4
# [TTL] permanent
"""6 维权重 IC 加权校准（路径 A）单元测试——含退化/边界用例。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.strength_ic_weight_calibrator import (
    EMPIRICAL_WEIGHTS,
    STRENGTH_DIMENSIONS,
    calibrate_dimension_weights_ic,
    compute_rank_ic,
    compute_rolling_ic_weights,
    should_recalibrate_cusum,
)


class TestComputeRankIC:
    def test_perfect_positive(self):
        ic = compute_rank_ic([1.0, 2.0, 3.0, 4.0, 5.0], [0.01, 0.02, 0.03, 0.04, 0.05])
        assert ic == pytest.approx(1.0)

    def test_perfect_negative(self):
        ic = compute_rank_ic([1.0, 2.0, 3.0, 4.0, 5.0], [0.05, 0.04, 0.03, 0.02, 0.01])
        assert ic == pytest.approx(-1.0)

    def test_ties_average_rank(self):
        # 并列值不崩、IC ∈ [-1,1]
        ic = compute_rank_ic([1.0, 1.0, 2.0, 2.0, 3.0], [1.0, 1.0, 2.0, 2.0, 3.0])
        assert ic == pytest.approx(1.0)

    def test_zero_variance_returns_zero(self):
        assert compute_rank_ic([5.0, 5.0, 5.0, 5.0], [1.0, 2.0, 3.0, 4.0]) == 0.0
        assert compute_rank_ic([1.0, 2.0, 3.0, 4.0], [2.0, 2.0, 2.0, 2.0]) == 0.0

    def test_too_few_samples_returns_zero(self):
        assert compute_rank_ic([1.0, 2.0], [1.0, 2.0]) == 0.0
        assert compute_rank_ic([], []) == 0.0

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            compute_rank_ic([1.0, 2.0, 3.0], [1.0, 2.0])


class TestCalibrateWeights:
    def test_proportional_to_positive_ic(self):
        w = calibrate_dimension_weights_ic({"price_momentum": 0.06, "technical": 0.03})
        assert w["price_momentum"] == pytest.approx(2.0 / 3.0)
        assert w["technical"] == pytest.approx(1.0 / 3.0)
        assert w["risk"] == 0.0
        assert sum(w.values()) == pytest.approx(1.0)
        assert set(w) == set(STRENGTH_DIMENSIONS)

    def test_negative_ic_clipped_to_zero(self):
        w = calibrate_dimension_weights_ic({"price_momentum": -0.05, "capital": 0.04})
        assert w["price_momentum"] == 0.0
        assert w["capital"] == pytest.approx(1.0)

    def test_all_nonpositive_falls_back_empirical(self):
        w = calibrate_dimension_weights_ic({d: -0.01 for d in STRENGTH_DIMENSIONS})
        assert w == EMPIRICAL_WEIGHTS
        assert w is not EMPIRICAL_WEIGHTS  # 副本，防外部篡改

    def test_empty_ic_falls_back(self):
        assert calibrate_dimension_weights_ic({}) == EMPIRICAL_WEIGHTS

    def test_empirical_weights_sum_one(self):
        assert sum(EMPIRICAL_WEIGHTS.values()) == pytest.approx(1.0)


class TestRollingICWeights:
    def test_window_alignment_uses_tail(self):
        # 前 60 日无相关，末 60 日强正相关 → 尾部窗口 IC 生效
        dim = list(range(120))
        rets = [0.0] * 60 + [float(i) * 0.001 for i in range(60)]
        w = compute_rolling_ic_weights(
            {"price_momentum": dim},
            rets,
            window=60,
        )
        assert w["price_momentum"] == pytest.approx(1.0)

    def test_short_window_raises(self):
        with pytest.raises(ValueError):
            compute_rolling_ic_weights({}, [1.0, 2.0], window=2)

    def test_all_missing_dims_falls_back(self):
        w = compute_rolling_ic_weights({}, [0.01] * 60, window=60)
        assert w == EMPIRICAL_WEIGHTS


class TestCusumRecalibrate:
    def test_stable_series_no_trigger(self):
        assert should_recalibrate_cusum([0.03] * 30) is False

    def test_level_shift_triggers(self):
        series = [0.05] * 30 + [-0.05] * 30
        assert should_recalibrate_cusum(series) is True

    def test_short_series_no_trigger(self):
        assert should_recalibrate_cusum([0.05]) is False
        assert should_recalibrate_cusum([]) is False
