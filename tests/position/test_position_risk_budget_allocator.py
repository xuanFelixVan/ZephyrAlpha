# [BLUEPRINT] MOD-POS-013 | docs/03_modules/MOD-POS-013/
# [MODULE] zephyr.position.core.position_risk_budget_allocator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_position_risk_budget_allocator.py
# [TTL] permanent
"""position_risk_budget_allocator（风险预算分配器）单元测试。

覆盖：
- 等预算 ERC：等波动不相关标的 → 等权；波动 2:1 → 权重 1:2 反比
- 自定义预算 → 相对风险贡献按预算比例
- 权重和=1；相对风险贡献和=1
- max_weight 上限投影生效
- 非法输入（预算标的不齐/负预算/全零预算/上限不可行）→ InvalidRiskBudgetInputError
"""

from __future__ import annotations

import pytest

from zephyr.position.core.covariance_estimator import estimate_covariance
from zephyr.position.core.position_risk_budget_allocator import (
    InvalidRiskBudgetInputError,
    allocate_risk_budget,
)


def _orthogonal(n: int) -> tuple[list[float], list[float]]:
    """两个样本正交、等方差确定性模式。"""
    f = [0.01 * (1.0 if i % 2 == 0 else -1.0) for i in range(n)]
    g = [0.01 * (1.0 if i % 4 < 2 else -1.0) for i in range(n)]
    return f, g


class TestEqualRiskContribution:
    def test_equal_vol_uncorrelated_gives_equal_weights(self) -> None:
        """等波动+不相关 → ERC 退化为等权。"""
        f, g = _orthogonal(80)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov)
        assert alloc.weights["A"] == pytest.approx(0.5, abs=0.02)
        assert alloc.weights["B"] == pytest.approx(0.5, abs=0.02)
        assert alloc.converged is True

    def test_vol_ratio_inverse_weights(self) -> None:
        """不相关标的波动 2:1 → ERC 权重 1:2（风险贡献相等）。"""
        f, g = _orthogonal(80)
        cov = estimate_covariance({"A": [2.0 * x for x in f], "B": list(g)})
        alloc = allocate_risk_budget(cov)
        assert alloc.weights["A"] == pytest.approx(1.0 / 3.0, abs=0.02)
        assert alloc.weights["B"] == pytest.approx(2.0 / 3.0, abs=0.02)

    def test_relative_risk_contributions_match_equal_budget(self) -> None:
        """等预算 → 相对风险贡献各 50%。"""
        f, g = _orthogonal(80)
        cov = estimate_covariance({"A": [1.5 * x for x in f], "B": list(g)})
        alloc = allocate_risk_budget(cov)
        assert alloc.relative_risk_contributions["A"] == pytest.approx(0.5, abs=0.02)
        assert alloc.relative_risk_contributions["B"] == pytest.approx(0.5, abs=0.02)

    def test_weights_sum_to_one(self) -> None:
        f, g = _orthogonal(60)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov)
        assert sum(alloc.weights.values()) == pytest.approx(1.0)

    def test_relative_rc_sums_to_one(self) -> None:
        f, g = _orthogonal(60)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov)
        assert sum(alloc.relative_risk_contributions.values()) == pytest.approx(1.0)

    def test_portfolio_volatility_positive(self) -> None:
        f, g = _orthogonal(60)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov)
        assert alloc.portfolio_volatility > 0.0

    def test_diversification_reduces_volatility(self) -> None:
        """组合波动 < 单一高波资产波动（分散效果）。"""
        f, g = _orthogonal(80)
        cov = estimate_covariance({"A": [2.0 * x for x in f], "B": list(g)})
        alloc = allocate_risk_budget(cov)
        import math

        var_a = cov.matrix[0][0]
        assert alloc.portfolio_volatility < math.sqrt(var_a)


class TestCustomBudget:
    def test_custom_budget_risk_contributions(self) -> None:
        """自定义预算 0.7/0.3 → 相对风险贡献按预算。"""
        f, g = _orthogonal(100)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov, budget={"A": 0.7, "B": 0.3})
        assert alloc.relative_risk_contributions["A"] == pytest.approx(0.7, abs=0.03)
        assert alloc.relative_risk_contributions["B"] == pytest.approx(0.3, abs=0.03)

    def test_unnormalized_budget_accepted(self) -> None:
        """预算未归一化（如 7:3）→ 内部归一。"""
        f, g = _orthogonal(100)
        cov = estimate_covariance({"A": f, "B": g})
        alloc = allocate_risk_budget(cov, budget={"A": 7.0, "B": 3.0})
        assert alloc.relative_risk_contributions["A"] == pytest.approx(0.7, abs=0.03)


class TestMaxWeightCap:
    def test_max_weight_cap_respected(self) -> None:
        """三标的 + 上限 0.4（≥1/3 可行）→ 任何权重不超上限（容差 1e-9）。"""
        f, g = _orthogonal(90)
        h = [0.01 * (1.0 if i % 4 in (0, 3) else -1.0) for i in range(90)]
        cov = estimate_covariance({"A": f, "B": g, "C": h})
        alloc = allocate_risk_budget(cov, max_weight=0.4)
        assert all(w <= 0.4 + 1e-9 for w in alloc.weights.values())

    def test_infeasible_max_weight_rejected(self) -> None:
        """max_weight < 1/N 不可行 → 拒绝。"""
        f, g = _orthogonal(60)
        cov = estimate_covariance({"A": f, "B": g})
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(cov, max_weight=0.4)


class TestInvalidInput:
    def _cov(self) -> "object":
        f, g = _orthogonal(60)
        return estimate_covariance({"A": f, "B": g})

    def test_budget_symbol_mismatch(self) -> None:
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), budget={"A": 0.5, "C": 0.5})

    def test_negative_budget(self) -> None:
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), budget={"A": 1.5, "B": -0.5})

    def test_all_zero_budget(self) -> None:
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), budget={"A": 0.0, "B": 0.0})

    def test_non_finite_budget(self) -> None:
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), budget={"A": float("nan"), "B": 1.0})

    def test_invalid_max_weight(self) -> None:
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), max_weight=0.0)
        with pytest.raises(InvalidRiskBudgetInputError):
            allocate_risk_budget(self._cov(), max_weight=1.5)
