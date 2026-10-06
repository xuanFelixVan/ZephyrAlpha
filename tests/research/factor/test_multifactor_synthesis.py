# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-10 多因子合成测试——纯函数模块（无 IO 依赖）。

覆盖：
- synthesize_equal_weight: 空输入 / 等权=均值
- synthesize_ic_weighted: IC加权归一化 / 权重不匹配退化为等权
- synthesize_regression: 回归优化
- synthesize: 统一入口 dispatch / 未知方法退化
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

multifactor_synthesis = pytest.importorskip("zephyr.factor.analysis.multifactor_synthesis")

synthesize_equal_weight = multifactor_synthesis.synthesize_equal_weight
synthesize_ic_weighted = multifactor_synthesis.synthesize_ic_weighted
synthesize_regression = multifactor_synthesis.synthesize_regression
synthesize = multifactor_synthesis.synthesize


class TestSynthesizeEqualWeight:
    def test_empty_input(self):
        result = synthesize_equal_weight({})
        assert result.empty

    def test_equals_mean(self):
        f1 = pd.Series([1.0, 2.0, 3.0], index=list("ABC"))
        f2 = pd.Series([4.0, 5.0, 6.0], index=list("ABC"))
        result = synthesize_equal_weight({"f1": f1, "f2": f2})
        assert len(result) == 3
        # (1+4)/2=2.5, (2+5)/2=3.5, (3+6)/2=4.5
        assert abs(result.loc["A"] - 2.5) < 1e-10
        assert abs(result.loc["B"] - 3.5) < 1e-10
        assert abs(result.loc["C"] - 4.5) < 1e-10

    def test_single_factor(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        result = synthesize_equal_weight({"f1": f1})
        assert abs(result.loc["A"] - 1.0) < 1e-10
        assert abs(result.loc["B"] - 2.0) < 1e-10

    def test_three_factors(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([2.0, 4.0], index=list("AB"))
        f3 = pd.Series([3.0, 6.0], index=list("AB"))
        result = synthesize_equal_weight({"f1": f1, "f2": f2, "f3": f3})
        # (1+2+3)/3=2, (2+4+6)/3=4
        assert abs(result.loc["A"] - 2.0) < 1e-10
        assert abs(result.loc["B"] - 4.0) < 1e-10


class TestSynthesizeIcWeighted:
    def test_normalization(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        # ic_weights 总和 1+3=4, 归一化后 f1=0.25, f2=0.75
        ic_weights = {"f1": 1.0, "f2": 3.0}
        result = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        # A: 1*0.25 + 3*0.75 = 2.5; B: 2*0.25 + 4*0.75 = 3.5
        assert abs(result.loc["A"] - 2.5) < 1e-10
        assert abs(result.loc["B"] - 3.5) < 1e-10

    def test_empty_input(self):
        result = synthesize_ic_weighted({}, {"f1": 1.0})
        assert result.empty

    def test_weight_mismatch_degrades_to_equal_weight(self):
        # ic_weights 引用了不在 factor_values 中的因子 → 无有效权重 → 等权
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        ic_weights = {"f3": 1.0}  # f3 不在 factor_values
        result = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_all_zero_weights_degrades_to_equal_weight(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        ic_weights = {"f1": 0.0, "f2": 0.0}  # 全 0 → 归一化分母为 0 → 等权
        result = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_partial_weights(self):
        # 部分因子有权重，部分没有 → 只用有权重的因子
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        ic_weights = {"f1": 1.0, "f2": 0.0}  # f2 权重为 0 被剔除
        result = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        # 仅 f1 有效，归一化后 f1=1.0 → 结果 = f1
        assert abs(result.loc["A"] - 1.0) < 1e-10
        assert abs(result.loc["B"] - 2.0) < 1e-10

    def test_negative_weights_normalized(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        # 负权重按绝对值归一化：|−1|+|3|=4 → f1=0.25, f2=0.75
        ic_weights = {"f1": -1.0, "f2": 3.0}
        result = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        # f1*−0.25 + f2*0.75: A=−0.25+2.25=2.0, B=−0.5+3.0=2.5
        assert abs(result.loc["A"] - 2.0) < 1e-10
        assert abs(result.loc["B"] - 2.5) < 1e-10


class TestSynthesizeRegression:
    def test_regression_recovers_linear_combination(self):
        # 构造 fr = 2*f1 + 3*f2 的线性关系，OLS 应恢复系数
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0], index=list("ABCD"))
        f2 = pd.Series([2.0, 3.0, 4.0, 5.0], index=list("ABCD"))
        fr = pd.Series(
            [2 * 1 + 3 * 2, 2 * 2 + 3 * 3, 2 * 3 + 3 * 4, 2 * 4 + 3 * 5],
            index=list("ABCD"),
        )  # [8, 13, 18, 23]
        result = synthesize_regression({"f1": f1, "f2": f2}, fr)
        # 回归系数 ≈ [2, 3]，合成结果 ≈ fr
        assert len(result) == 4
        for sym in list("ABCD"):
            assert abs(result.loc[sym] - fr.loc[sym]) < 1e-6

    def test_empty_input(self):
        result = synthesize_regression({}, pd.Series([], dtype=float))
        assert result.empty

    def test_insufficient_data_degrades_to_equal_weight(self):
        # 数据点不足 (len(common) < len(columns)+1) → 等权兜底
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        fr = pd.Series([5.0, 6.0], index=list("AB"))
        # 2 个因子需 >= 3 个点，只有 2 个 → 等权
        result = synthesize_regression({"f1": f1, "f2": f2}, fr)
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)


class TestSynthesizeDispatch:
    def test_dispatch_equal_weight(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        result = synthesize({"f1": f1, "f2": f2}, method="equal_weight")
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_dispatch_ic_weighted(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        ic_weights = {"f1": 1.0, "f2": 3.0}
        result = synthesize(
            {"f1": f1, "f2": f2},
            method="ic_weighted",
            ic_weights=ic_weights,
        )
        expected = synthesize_ic_weighted({"f1": f1, "f2": f2}, ic_weights)
        pd.testing.assert_series_equal(result, expected)

    def test_dispatch_regression(self):
        f1 = pd.Series([1.0, 2.0, 3.0, 4.0], index=list("ABCD"))
        f2 = pd.Series([2.0, 3.0, 4.0, 5.0], index=list("ABCD"))
        fr = pd.Series([8.0, 13.0, 18.0, 23.0], index=list("ABCD"))
        result = synthesize(
            {"f1": f1, "f2": f2},
            method="regression",
            forward_returns=fr,
        )
        expected = synthesize_regression({"f1": f1, "f2": f2}, fr)
        pd.testing.assert_series_equal(result, expected)

    def test_dispatch_default_method_is_ic_weighted(self):
        # 默认 method="ic_weighted"
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        result = synthesize({"f1": f1, "f2": f2})  # 不传 method
        # 无 ic_weights → 等权兜底
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_unknown_method_degrades_to_equal_weight(self):
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        result = synthesize({"f1": f1, "f2": f2}, method="bogus_method")
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_regression_without_forward_returns_degrades(self):
        # regression 方法但未提供 forward_returns → 等权兜底
        f1 = pd.Series([1.0, 2.0], index=list("AB"))
        f2 = pd.Series([3.0, 4.0], index=list("AB"))
        result = synthesize({"f1": f1, "f2": f2}, method="regression")
        expected = synthesize_equal_weight({"f1": f1, "f2": f2})
        pd.testing.assert_series_equal(result, expected)

    def test_empty_input(self):
        result = synthesize({}, method="equal_weight")
        assert result.empty
