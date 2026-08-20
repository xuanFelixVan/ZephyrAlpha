# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""correlation_dedup 模块测试——因子相关性去重。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis import correlation_dedup


class TestFindRedundantPairs:
    def test_empty_input(self) -> None:
        assert correlation_dedup.find_redundant_pairs({}) == []

    def test_single_factor(self) -> None:
        factor_values = {"f1": pd.Series([1.0, 2.0, 3.0])}
        assert correlation_dedup.find_redundant_pairs(factor_values) == []

    def test_no_redundant_pairs(self) -> None:
        np.random.seed(42)
        factor_values = {
            "f1": pd.Series(np.random.randn(100)),
            "f2": pd.Series(np.random.randn(100)),
        }
        # 不相关因子，默认阈值 0.7，应无冗余对
        pairs = correlation_dedup.find_redundant_pairs(factor_values, threshold=0.7)
        assert pairs == []

    def test_identical_factors_redundant(self) -> None:
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        factor_values = {"f1": values, "f2": values}
        pairs = correlation_dedup.find_redundant_pairs(factor_values)
        assert len(pairs) == 1
        f1, f2, corr = pairs[0]
        assert {f1, f2} == {"f1", "f2"}
        assert corr == pytest.approx(1.0)

    def test_sorted_by_abs_correlation_desc(self) -> None:
        # f1/f2 完全相关（1.0），f1/f3 较高相关但 < 1.0
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        f2 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])  # corr=1.0
        f3 = pd.Series([1.0, 2.0, 2.0, 4.0, 5.0])  # corr<1.0
        factor_values = {"f1": f1, "f2": f2, "f3": f3}
        pairs = correlation_dedup.find_redundant_pairs(factor_values, threshold=0.5)
        # 按绝对相关性降序排列
        assert len(pairs) >= 1
        corrs = [abs(p[2]) for p in pairs]
        assert corrs == sorted(corrs, reverse=True)

    def test_custom_threshold(self) -> None:
        np.random.seed(42)
        f1 = pd.Series(np.random.randn(100))
        f2 = pd.Series(np.random.randn(100))
        factor_values = {"f1": f1, "f2": f2}
        # 低阈值时可能有冗余对
        pairs_low = correlation_dedup.find_redundant_pairs(factor_values, threshold=0.0)
        # 阈值=0，所有非 NaN 对都算冗余
        assert len(pairs_low) >= 1
        # 高阈值时无冗余对
        pairs_high = correlation_dedup.find_redundant_pairs(factor_values, threshold=0.99)
        assert pairs_high == []

    def test_return_format(self) -> None:
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        factor_values = {"f1": values, "f2": values}
        pairs = correlation_dedup.find_redundant_pairs(factor_values)
        assert isinstance(pairs, list)
        assert isinstance(pairs[0], tuple)
        assert len(pairs[0]) == 3


class TestDedupFactors:
    def test_empty_input(self) -> None:
        assert correlation_dedup.dedup_factors({}) == []

    def test_single_factor(self) -> None:
        factor_values = {"f1": pd.Series([1.0, 2.0, 3.0])}
        result = correlation_dedup.dedup_factors(factor_values)
        assert result == ["f1"]

    def test_identical_factors_keeps_first(self) -> None:
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        factor_values = {"f1": values, "f2": values}
        result = correlation_dedup.dedup_factors(factor_values, threshold=0.7)
        # f1 先出现，f2 与 f1 完全相关被丢弃
        assert result == ["f1"]

    def test_uncorrelated_all_kept(self) -> None:
        np.random.seed(42)
        factor_values = {
            "f1": pd.Series(np.random.randn(100)),
            "f2": pd.Series(np.random.randn(100)),
            "f3": pd.Series(np.random.randn(100)),
        }
        result = correlation_dedup.dedup_factors(factor_values, threshold=0.7)
        assert len(result) == 3
        assert set(result) == {"f1", "f2", "f3"}

    def test_preserves_insertion_order(self) -> None:
        np.random.seed(42)
        f1 = pd.Series(np.random.randn(50))
        f2 = pd.Series(np.random.randn(50))
        f3 = pd.Series(np.random.randn(50))
        factor_values = {"zzz": f1, "aaa": f2, "mmm": f3}
        result = correlation_dedup.dedup_factors(factor_values, threshold=0.7)
        # 应保持插入顺序
        assert result == list(factor_values.keys())

    def test_partial_redundancy(self) -> None:
        # f1/f2 完全相关，f3 独立
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        np.random.seed(42)
        f3 = pd.Series(np.random.randn(5))
        factor_values = {"f1": values, "f2": values, "f3": f3}
        result = correlation_dedup.dedup_factors(factor_values, threshold=0.7)
        assert "f1" in result
        assert "f2" not in result
        assert "f3" in result

    def test_threshold_boundary(self) -> None:
        # 相关性正好等于阈值
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        f2 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        factor_values = {"f1": f1, "f2": f2}
        # corr=1.0 >= threshold=1.0，应去重
        result = correlation_dedup.dedup_factors(factor_values, threshold=1.0)
        assert result == ["f1"]
        # corr=1.0 < threshold=1.1（超过 1.0 不合法但函数不报错），保留两个
        # 注意：阈值 > 1.0 时无任何对满足 >=，故都保留
        result2 = correlation_dedup.dedup_factors(factor_values, threshold=1.5)
        assert len(result2) == 2

    def test_negative_correlation_redundant(self) -> None:
        # 负相关也应被去重（用绝对值判断）
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        f2 = pd.Series([-1.0, -2.0, -3.0, -4.0, -5.0])  # corr=-1.0
        factor_values = {"f1": f1, "f2": f2}
        result = correlation_dedup.dedup_factors(factor_values, threshold=0.7)
        assert result == ["f1"]
