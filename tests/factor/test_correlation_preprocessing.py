# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_test_correlation_preprocessing | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_preprocessing
# [TESTS] src/zephyr/factor/analysis/correlation_preprocessing.py
# [TTL] task_bound
"""23 号 memo §3.1① 数据预处理 pipeline 测试。

裁定真源：23_strategy_correlation_validation.md §3.1①——
  对数收益率统一 + ADF 平稳性（p<0.05 才算 Pearson）+ Modified Z-score 异常值
  标注（只标注不剔除）+ 交易日对齐（交集，禁前向填充）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis.correlation_preprocessing import (
    ADFSignificance,
    adf_test,
    align_trading_days,
    compute_strategy_correlation,
    modified_zscore_flags,
    preprocess_strategy_returns,
    to_log_returns,
)


class TestLogReturns:
    def test_known_values(self):
        prices = pd.Series([100.0, 110.0, 99.0], index=pd.date_range("2026-01-01", periods=3))
        lr = to_log_returns(prices)
        assert len(lr) == 2
        assert lr.iloc[0] == pytest.approx(np.log(1.1))
        assert lr.iloc[1] == pytest.approx(np.log(0.9))

    def test_empty_and_nonpositive_rejected(self):
        with pytest.raises(ValueError):
            to_log_returns(pd.Series(dtype=float))
        with pytest.raises(ValueError):
            to_log_returns(pd.Series([100.0, 0.0]))  # 非正值无法取对数


class TestADF:
    def test_white_noise_stationary(self):
        rng = np.random.default_rng(42)
        noise = pd.Series(rng.normal(0.0, 0.01, 500))
        res = adf_test(noise)
        assert res.is_stationary
        assert res.p_value < 0.05
        assert res.note == ADFSignificance.OK

    def test_random_walk_nonstationary(self):
        rng = np.random.default_rng(7)
        walk = pd.Series(np.cumsum(rng.normal(0.0, 0.01, 500)))
        res = adf_test(walk)
        assert not res.is_stationary
        assert res.p_value >= 0.05

    def test_constant_series_degraded(self):
        """常数序列：ADF 回归退化（零方差），保守标非平稳+constant_series 标记。"""
        res = adf_test(pd.Series([0.01] * 100))
        assert not res.is_stationary
        assert res.note == ADFSignificance.CONSTANT_SERIES
        assert np.isnan(res.adf_stat)

    def test_insufficient_sample(self):
        res = adf_test(pd.Series([0.01, -0.02, 0.03]))
        assert res.note == ADFSignificance.INSUFFICIENT_SAMPLE
        assert not res.is_stationary


class TestModifiedZscore:
    def test_spike_flagged_not_removed(self):
        rng = np.random.default_rng(1)
        values = rng.normal(0.0, 0.01, 200)
        values[100] = 0.30  # 连板日极端值
        flags = modified_zscore_flags(pd.Series(values))
        assert flags.iloc[100]
        assert flags.sum() == 1  # 只标注不剔除

    def test_constant_series_no_outliers(self):
        """MAD=0（常数序列）→ 无离群可判，全部 False。"""
        flags = modified_zscore_flags(pd.Series([0.01] * 50))
        assert not flags.any()


class TestAlignTradingDays:
    def test_intersection_only_no_forward_fill(self):
        idx_a = pd.date_range("2026-01-01", periods=5)
        idx_b = pd.date_range("2026-01-03", periods=5)  # 错位 2 天
        panel = align_trading_days({"a": pd.Series(range(5), index=idx_a), "b": pd.Series(range(5), index=idx_b)})
        assert len(panel) == 3  # 仅交集 01-03/04/05
        assert list(panel.columns) == ["a", "b"]
        assert not panel.isna().any().any()  # 禁前向填充

    def test_empty_intersection_rejected(self):
        with pytest.raises(ValueError):
            align_trading_days(
                {
                    "a": pd.Series([1.0], index=pd.date_range("2026-01-01", periods=1)),
                    "b": pd.Series([1.0], index=pd.date_range("2027-01-01", periods=1)),
                }
            )


class TestStrategyCorrelation:
    def test_identical_series_corr_one(self):
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0, 0.01, 100))
        panel = pd.DataFrame({"a": r, "b": r * 1.0})
        mats = compute_strategy_correlation(panel)
        assert mats["pearson"].loc["a", "b"] == pytest.approx(1.0)
        assert mats["spearman"].loc["a", "b"] == pytest.approx(1.0)
        assert mats["pearson"].loc["a", "a"] == pytest.approx(1.0)  # 对角线

    def test_unsupported_method_rejected(self):
        with pytest.raises(ValueError):
            compute_strategy_correlation(pd.DataFrame({"a": [0.1, 0.2]}), methods=("kendall",))


class TestPreprocessPipeline:
    def test_end_to_end(self):
        rng = np.random.default_rng(11)
        n = 300
        nav_a = pd.Series(np.exp(np.cumsum(rng.normal(0.0005, 0.01, n))))
        nav_b = pd.Series(np.exp(np.cumsum(rng.normal(0.0004, 0.012, n))))
        nav_flat = pd.Series([1.0] * n)  # 常数净值 → 对数收益常数 → ADF 退化
        result = preprocess_strategy_returns({"a": nav_a, "b": nav_b, "flat": nav_flat})
        assert len(result.aligned_log_returns) == n - 1
        assert "flat" in result.stationarity_warnings
        assert set(result.adf) == {"a", "b", "flat"}
        assert set(result.outliers) == {"a", "b", "flat"}

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            preprocess_strategy_returns({})
