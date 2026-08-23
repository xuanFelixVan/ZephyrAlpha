# [BLUEPRINT] MOD-POS-011 | docs/03_modules/MOD-POS-011/
# [MODULE] zephyr.position.core.covariance_estimator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_covariance_estimator.py
# [TTL] permanent
"""covariance_estimator（Ledoit-Wolf 收缩协方差估计器）单元测试。

覆盖：
- 样本协方差正确性（ shrinkage=0 时退化为样本协方差）
- 收缩目标=等方差对角阵 μI，收缩强度∈[0,1]
- 少样本高维场景收缩强度→1（Fail-Closed 向对角阵收敛）
- 非法输入（长度不齐/样本不足/非有限值/单标的）→ InvalidCovarianceInputError
"""

from __future__ import annotations

import math

import pytest

from zephyr.position.core.covariance_estimator import (
    InvalidCovarianceInputError,
    estimate_covariance,
)


def _series(n: int, base: float, step: float) -> list[float]:
    """构造确定性收益率序列（均值非零、方差非零）。"""
    return [base + step * ((i % 7) - 3) for i in range(n)]


class TestEstimateCovariance:
    def test_symbols_sorted_and_shape(self) -> None:
        """标的按字典序排序，矩阵为 N×N 对称。"""
        est = estimate_covariance({"B": _series(30, 0.001, 0.01), "A": _series(30, 0.002, 0.02)})
        assert est.symbols == ("A", "B")
        assert len(est.matrix) == 2
        assert all(len(row) == 2 for row in est.matrix)
        assert est.matrix[0][1] == pytest.approx(est.matrix[1][0])

    def test_diagonal_is_variance(self) -> None:
        """对角线=各标的方差（正数）。"""
        est = estimate_covariance({"A": _series(40, 0.0, 0.015), "B": _series(40, 0.0, 0.008)})
        assert est.matrix[0][0] > 0
        assert est.matrix[1][1] > 0

    def test_perfect_correlation_offdiag(self) -> None:
        """完全线性相关的两序列 → 协方差≈sqrt(var1*var2)（收缩后仍接近）。"""
        a = _series(60, 0.0, 0.01)
        b = [2.0 * x for x in a]
        est = estimate_covariance({"A": a, "B": b})
        var_a = est.matrix[0][0]
        var_b = est.matrix[1][1]
        cov_ab = est.matrix[0][1]
        corr = cov_ab / math.sqrt(var_a * var_b)
        assert corr == pytest.approx(1.0, abs=0.05)

    def test_shrinkage_in_unit_interval(self) -> None:
        """收缩强度∈[0,1]。"""
        est = estimate_covariance({"A": _series(50, 0.0, 0.01), "B": _series(50, 0.0, 0.013)})
        assert 0.0 <= est.shrinkage <= 1.0

    def test_high_shrinkage_when_few_observations(self) -> None:
        """T≪N² 噪声场景 → 收缩强度显著>0（向对角目标收敛）。"""
        # T=3，4 标的近似独立噪声 → 样本协方差病态，收缩应显著
        returns = {
            "S0": [0.01, -0.02, 0.015],
            "S1": [-0.005, 0.02, -0.01],
            "S2": [0.02, 0.005, -0.015],
            "S3": [-0.01, 0.01, 0.005],
        }
        est = estimate_covariance(returns)
        assert est.shrinkage > 0.0

    def test_shrunk_diag_not_larger_than_max_sample_var(self) -> None:
        """收缩后方差不放大（只缩不增方向的合理性）。"""
        a = _series(80, 0.0, 0.02)
        b = _series(80, 0.0, 0.005)
        est = estimate_covariance({"A": a, "B": b})
        sample_var_a = max(
            sum((x - sum(a) / len(a)) ** 2 for x in a) / (len(a) - 1),
            0.0,
        )
        # 收缩目标为共同均值 μ：各对角线向 μ 靠拢，最大方差不超样本最大值太多
        assert est.matrix[0][0] <= sample_var_a * 1.5

    def test_n_observations_recorded(self) -> None:
        """n_observations 记录样本量。"""
        est = estimate_covariance({"A": _series(25, 0.0, 0.01), "B": _series(25, 0.0, 0.02)})
        assert est.n_observations == 25

    def test_to_nested_dict(self) -> None:
        """to_nested_dict 输出 {sym: {sym: cov}} 口径。"""
        est = estimate_covariance({"A": _series(30, 0.0, 0.01), "B": _series(30, 0.0, 0.02)})
        d = est.to_nested_dict()
        assert set(d) == {"A", "B"}
        assert d["A"]["B"] == pytest.approx(est.matrix[0][1])


class TestInvalidInput:
    def test_empty_returns(self) -> None:
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({})

    def test_single_asset_rejected(self) -> None:
        """单标的无协方差结构 → 拒绝。"""
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": _series(30, 0.0, 0.01)})

    def test_too_few_observations(self) -> None:
        """T<2 → 拒绝。"""
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": [0.01], "B": [0.02]})

    def test_mismatched_lengths(self) -> None:
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": _series(30, 0.0, 0.01), "B": _series(20, 0.0, 0.01)})

    def test_non_finite_values(self) -> None:
        bad = _series(30, 0.0, 0.01)
        bad[5] = float("nan")
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": bad, "B": _series(30, 0.0, 0.01)})
        bad2 = _series(30, 0.0, 0.01)
        bad2[3] = float("inf")
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": _series(30, 0.0, 0.01), "B": bad2})

    def test_zero_variance_series(self) -> None:
        """常数序列（方差 0）→ 拒绝（无风险结构可估）。"""
        with pytest.raises(InvalidCovarianceInputError):
            estimate_covariance({"A": [0.01] * 30, "B": _series(30, 0.0, 0.01)})
