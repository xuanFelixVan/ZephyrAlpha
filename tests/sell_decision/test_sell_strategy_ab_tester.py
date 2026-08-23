# [BLUEPRINT] MOD-SELL-011 | docs/03_modules/MOD-SELL-011/
# [MODULE] zephyr.sell_decision.core.sell_strategy_ab_tester
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_sell_strategy_ab_tester.py
# [TTL] permanent
"""sell_strategy_ab_tester（卖出策略 AB 测试）单元测试。

覆盖：
- B 显著优于 A → ADOPT_B；A 显著优 → KEEP_A；差异不显著 → INCONCLUSIVE
- 样本不足 → INCONCLUSIVE + 预警（防小样本过拟合决策）
- 双样本 z 检验（正态近似）方向正确
- 非法输入 → InvalidABTestInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.sell_strategy_ab_tester import (
    ABDecision,
    InvalidABTestInputError,
    evaluate_ab_test,
)


def _outcomes(mean: float, n: int, spread: float = 0.01) -> list[float]:
    """确定性伪样本：围绕 mean 对称分布。"""
    half = spread * (n - 1) / 2.0
    return [mean - half + spread * i for i in range(n)]


class TestDecision:
    def test_adopt_b_when_significantly_better(self) -> None:
        """B 均值显著高于 A → ADOPT_B。"""
        a = _outcomes(0.010, 50, spread=0.001)
        b = _outcomes(0.030, 50, spread=0.001)
        report = evaluate_ab_test(a, b, min_samples=20)
        assert report.decision is ABDecision.ADOPT_B
        assert report.significant is True

    def test_keep_a_when_b_significantly_worse(self) -> None:
        """B 均值显著低于 A → KEEP_A。"""
        a = _outcomes(0.030, 50, spread=0.001)
        b = _outcomes(0.010, 50, spread=0.001)
        report = evaluate_ab_test(a, b, min_samples=20)
        assert report.decision is ABDecision.KEEP_A
        assert report.significant is True

    def test_inconclusive_when_no_difference(self) -> None:
        """两组同分布 → 不显著 → INCONCLUSIVE。"""
        a = _outcomes(0.020, 50)
        b = _outcomes(0.020, 50)
        report = evaluate_ab_test(a, b, min_samples=20)
        assert report.decision is ABDecision.INCONCLUSIVE
        assert report.significant is False

    def test_inconclusive_when_insufficient_samples(self) -> None:
        """样本 < min_samples → INCONCLUSIVE + 预警。"""
        a = _outcomes(0.010, 5)
        b = _outcomes(0.050, 5)
        report = evaluate_ab_test(a, b, min_samples=30)
        assert report.decision is ABDecision.INCONCLUSIVE
        assert any("样本" in w for w in report.warnings)


class TestStatistics:
    def test_means_computed(self) -> None:
        a = _outcomes(0.010, 40)
        b = _outcomes(0.020, 40)
        report = evaluate_ab_test(a, b, min_samples=20)
        assert report.mean_a == pytest.approx(0.010)
        assert report.mean_b == pytest.approx(0.020)
        assert report.diff == pytest.approx(0.010)

    def test_z_statistic_direction(self) -> None:
        """B 更好 → z > 0。"""
        report = evaluate_ab_test(_outcomes(0.0, 50), _outcomes(0.02, 50), min_samples=20)
        assert report.z_statistic > 0.0

    def test_z_statistic_zero_for_identical(self) -> None:
        report = evaluate_ab_test(_outcomes(0.02, 50), _outcomes(0.02, 50), min_samples=20)
        assert report.z_statistic == pytest.approx(0.0)

    def test_sample_sizes_recorded(self) -> None:
        report = evaluate_ab_test(_outcomes(0.01, 30), _outcomes(0.02, 40), min_samples=20)
        assert report.n_a == 30
        assert report.n_b == 40


class TestInvalidInput:
    def test_empty_groups(self) -> None:
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([], [0.01, 0.02])
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01], [])

    def test_non_finite_outcomes(self) -> None:
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01, float("nan")], [0.01, 0.02])
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01], [float("inf"), 0.02])

    def test_min_samples_below_two(self) -> None:
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01, 0.02], [0.01, 0.02], min_samples=1)

    def test_alpha_out_of_range(self) -> None:
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01, 0.02], [0.01, 0.02], alpha=0.0)
        with pytest.raises(InvalidABTestInputError):
            evaluate_ab_test([0.01, 0.02], [0.01, 0.02], alpha=1.0)
