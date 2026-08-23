# [BLUEPRINT] MOD-ML-008 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] tests.ml_train.test_meta_learning_rsi
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/ml_train/test_meta_learning_rsi.py -q
# [TTL] permanent

"""元学习 RSI（MOD-ML-008）单元测试——RSI 计算/按 regime 元学习推荐周期。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.meta_learning_rsi import (
    MetaLearningRsi,
    MetaLearningRsiError,
    compute_rsi,
)


class TestComputeRsi:
    def test_all_gains_rsi_100(self):
        rsi = compute_rsi(np.arange(1.0, 30.0), period=14)
        assert rsi[-1] == pytest.approx(100.0)

    def test_all_losses_rsi_0(self):
        rsi = compute_rsi(np.arange(30.0, 1.0, -1.0), period=14)
        assert rsi[-1] == pytest.approx(0.0)

    def test_flat_series_rsi_neutral(self):
        rsi = compute_rsi(np.full(30, 10.0), period=14)
        assert rsi[-1] == pytest.approx(50.0)

    def test_output_length_and_warmup_nan(self):
        rsi = compute_rsi(np.arange(1.0, 20.0), period=5)
        assert len(rsi) == 18  # len(prices)-1
        assert np.all(np.isnan(rsi[:4]))
        assert np.all(np.isfinite(rsi[4:]))

    def test_rsi_bounds(self):
        rng = np.random.default_rng(0)
        prices = 10 * np.exp(np.cumsum(rng.normal(0, 0.02, 100)))
        rsi = compute_rsi(prices, period=14)
        valid = rsi[np.isfinite(rsi)]
        assert np.all((valid >= 0.0) & (valid <= 100.0))

    def test_invalid_period_rejected(self):
        with pytest.raises(MetaLearningRsiError):
            compute_rsi(np.arange(10.0), period=0)

    def test_short_series_rejected(self):
        with pytest.raises(MetaLearningRsiError):
            compute_rsi(np.arange(3.0), period=14)


class TestMetaLearning:
    def test_recommend_default_when_no_records(self):
        m = MetaLearningRsi(default_period=14)
        rec = m.recommend_period("震荡")
        assert rec["period"] == 14
        assert rec["source"] == "default"

    def test_record_and_recommend_best_period(self):
        m = MetaLearningRsi(candidate_periods=(7, 14, 21))
        m.record_performance(period=7, regime="趋势", score=0.4)
        m.record_performance(period=14, regime="趋势", score=0.8)
        m.record_performance(period=21, regime="趋势", score=0.6)
        rec = m.recommend_period("趋势")
        assert rec["period"] == 14
        assert rec["source"] == "meta_learning"
        assert rec["score"] == pytest.approx(0.8)

    def test_regime_isolation(self):
        m = MetaLearningRsi(candidate_periods=(7, 14))
        m.record_performance(period=7, regime="趋势", score=0.9)
        rec = m.recommend_period("震荡")
        assert rec["source"] == "default"

    def test_score_average_over_records(self):
        m = MetaLearningRsi(candidate_periods=(7,))
        m.record_performance(period=7, regime="趋势", score=0.6)
        m.record_performance(period=7, regime="趋势", score=0.8)
        rec = m.recommend_period("趋势")
        assert rec["score"] == pytest.approx(0.7)

    def test_invalid_record_rejected(self):
        m = MetaLearningRsi(candidate_periods=(7, 14))
        with pytest.raises(MetaLearningRsiError):
            m.record_performance(period=9, regime="趋势", score=0.5)
        with pytest.raises(MetaLearningRsiError):
            m.record_performance(period=7, regime="", score=0.5)
        with pytest.raises(MetaLearningRsiError):
            m.record_performance(period=7, regime="趋势", score=float("nan"))

    def test_candidate_periods_validated(self):
        with pytest.raises(MetaLearningRsiError):
            MetaLearningRsi(candidate_periods=(0,))

    def test_error_code(self):
        assert MetaLearningRsiError.error_code == "ZA-MLT-0011"
