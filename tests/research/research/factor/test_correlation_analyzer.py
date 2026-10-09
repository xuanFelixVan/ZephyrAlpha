# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""correlation_analyzer 模块测试——因子相关性分析。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis import correlation_analyzer


class TestComputeFactorCorrelation:
    def test_empty_input(self) -> None:
        result = correlation_analyzer.compute_factor_correlation({})
        assert result.empty

    def test_single_factor(self) -> None:
        factor_values = {"f1": pd.Series([1.0, 2.0, 3.0, 4.0])}
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        assert not result.empty
        assert result.shape == (1, 1)
        # 自相关 = 1.0
        assert result.loc["f1", "f1"] == pytest.approx(1.0)

    def test_identical_factors(self) -> None:
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        factor_values = {"f1": values, "f2": values}
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        assert result.loc["f1", "f2"] == pytest.approx(1.0)

    def test_negatively_correlated(self) -> None:
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        f2 = pd.Series([5.0, 4.0, 3.0, 2.0, 1.0])
        factor_values = {"f1": f1, "f2": f2}
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        assert result.loc["f1", "f2"] == pytest.approx(-1.0)

    def test_uncorrelated_factors(self) -> None:
        np.random.seed(42)
        f1 = pd.Series(np.random.randn(100))
        f2 = pd.Series(np.random.randn(100))
        factor_values = {"f1": f1, "f2": f2}
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        # 不相关因子的相关性应接近 0
        assert abs(result.loc["f1", "f2"]) < 0.3

    def test_matrix_symmetric(self) -> None:
        np.random.seed(123)
        factor_values = {
            "f1": pd.Series(np.random.randn(50)),
            "f2": pd.Series(np.random.randn(50)),
            "f3": pd.Series(np.random.randn(50)),
        }
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        # 对称矩阵
        for i in result.index:
            for j in result.columns:
                assert result.loc[i, j] == pytest.approx(result.loc[j, i], abs=1e-10)

    def test_index_alignment(self) -> None:
        # 不同 index 的因子值应自动对齐
        f1 = pd.Series([1.0, 2.0, 3.0], index=[0, 1, 2])
        f2 = pd.Series([2.0, 3.0, 4.0], index=[1, 2, 3])
        factor_values = {"f1": f1, "f2": f2}
        result = correlation_analyzer.compute_factor_correlation(factor_values)
        assert not result.empty
        assert result.shape == (2, 2)


class TestComputeRollingCorrelation:
    def test_empty_input(self) -> None:
        result = correlation_analyzer.compute_rolling_correlation({})
        assert result.empty

    def test_single_factor(self) -> None:
        # 单因子无法计算两两相关性
        factor_values = {"f1": pd.Series([1.0, 2.0, 3.0])}
        result = correlation_analyzer.compute_rolling_correlation(factor_values)
        assert result.empty

    def test_two_factors(self) -> None:
        np.random.seed(42)
        f1 = pd.Series(np.random.randn(100))
        f2 = pd.Series(np.random.randn(100))
        factor_values = {"f1": f1, "f2": f2}
        result = correlation_analyzer.compute_rolling_correlation(factor_values, window=20)
        assert not result.empty
        assert "f1_f2" in result.columns
        # 前 window-1 个值为 NaN
        assert result["f1_f2"].iloc[:18].isna().all()
        # window 之后应有非 NaN 值
        assert result["f1_f2"].iloc[20:].notna().any()

    def test_three_factors_three_pairs(self) -> None:
        np.random.seed(42)
        factor_values = {
            "f1": pd.Series(np.random.randn(80)),
            "f2": pd.Series(np.random.randn(80)),
            "f3": pd.Series(np.random.randn(80)),
        }
        result = correlation_analyzer.compute_rolling_correlation(factor_values, window=30)
        # C(3,2) = 3 对
        assert len(result.columns) == 3
        assert "f1_f2" in result.columns
        assert "f1_f3" in result.columns
        assert "f2_f3" in result.columns

    def test_custom_window(self) -> None:
        np.random.seed(42)
        factor_values = {
            "f1": pd.Series(np.random.randn(50)),
            "f2": pd.Series(np.random.randn(50)),
        }
        result = correlation_analyzer.compute_rolling_correlation(factor_values, window=10)
        # window=10，前 9 个值为 NaN
        assert result["f1_f2"].iloc[:8].isna().all()
        assert result["f1_f2"].iloc[10:].notna().any()

    def test_identical_factors_rolling_one(self) -> None:
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        factor_values = {"f1": values, "f2": values}
        result = correlation_analyzer.compute_rolling_correlation(factor_values, window=5)
        # 相同因子的滚动相关性应全为 1.0（非 NaN 部分）
        non_na = result["f1_f2"].dropna()
        assert np.allclose(non_na.to_numpy(), 1.0)
