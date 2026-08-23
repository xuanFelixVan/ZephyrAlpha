# [BLUEPRINT] MOD-POS-012 | docs/03_modules/MOD-POS-012/
# [MODULE] zephyr.position.core.correlation_regime_monitor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_correlation_regime_monitor.py
# [TTL] permanent
"""correlation_regime_monitor（相关性 regime 监控）单元测试。

覆盖：
- 相关矩阵由 MOD-POS-011 协方差标准化而来，对角=1，值域[-1,1]
- 平均成对相关→三档 regime（LOW/NORMAL/HIGH）分类正确
- 高相关 regime → 分散失效预警（Fail-Closed 方向）
- 阈值参数非法 → InvalidCorrelationRegimeInputError
"""

from __future__ import annotations

import pytest

from zephyr.position.core.correlation_regime_monitor import (
    CorrelationRegime,
    InvalidCorrelationRegimeInputError,
    assess_correlation_regime,
)


def _independent(n: int, seed: int) -> list[float]:
    """伪独立噪声序列（确定性）。"""
    return [0.01 * (((i * 7 + seed * 13) % 11) - 5) / 5.0 for i in range(n)]


def _common_factor(n: int, beta: float, idio: float, seed: int) -> list[float]:
    """含公共因子的序列：beta*factor + idio*noise（可造高相关）。"""
    factor = [0.02 * (((i * 5) % 9) - 4) / 4.0 for i in range(n)]
    noise = [idio * (((i * 3 + seed) % 7) - 3) / 3.0 for i in range(n)]
    return [beta * f + e for f, e in zip(factor, noise)]


def _orthogonal_patterns(n: int) -> tuple[list[float], list[float], list[float]]:
    """三个两两样本正交、等方差的确定性模式（周期 4），用于解析式造相关系数。"""
    f = [0.01 * (1.0 if i % 2 == 0 else -1.0) for i in range(n)]
    g = [0.01 * (1.0 if i % 4 < 2 else -1.0) for i in range(n)]
    h = [0.01 * (1.0 if i % 4 in (0, 3) else -1.0) for i in range(n)]
    return f, g, h


def _mid_correlation_returns(n: int = 80) -> dict[str, list[float]]:
    """解析式构造 avg 成对相关 ≈0.49 的三标的组合（NORMAL 区间）。

    y1=f；y2=a·f+b·g；y3=a·f+b·h（f/g/h 两两正交等方差）→
    corr(y1,y2)=corr(y1,y3)=a/√(a²+b²)=0.573，corr(y2,y3)=a²/(a²+b²)=0.329。
    """
    a, b = 0.7, 1.0
    f, g, h = _orthogonal_patterns(n)
    return {
        "S0": list(f),
        "S1": [a * x + b * y for x, y in zip(f, g)],
        "S2": [a * x + b * y for x, y in zip(f, h)],
    }


class TestAssessCorrelationRegime:
    def test_low_regime_for_independent_series(self) -> None:
        """近似独立序列 → LOW regime，分散有效。"""
        returns = {f"S{k}": _independent(60, k + 1) for k in range(4)}
        report = assess_correlation_regime(returns)
        assert report.regime is CorrelationRegime.LOW
        assert report.diversification_effective is True
        assert -1.0 <= report.avg_pairwise_correlation <= 1.0

    def test_high_regime_for_common_factor_series(self) -> None:
        """强公共因子主导 → HIGH regime + 分散失效预警。"""
        returns = {f"S{k}": _common_factor(60, 1.0, 0.0001, k) for k in range(4)}
        report = assess_correlation_regime(returns)
        assert report.regime is CorrelationRegime.HIGH
        assert report.diversification_effective is False
        assert any("分散" in w for w in report.warnings)

    def test_normal_regime_between_thresholds(self) -> None:
        """中等相关（解析构造 avg≈0.49）→ NORMAL regime。"""
        report = assess_correlation_regime(_mid_correlation_returns())
        assert report.regime is CorrelationRegime.NORMAL
        assert report.diversification_effective is True

    def test_custom_thresholds_respected(self) -> None:
        """自定义阈值生效（high 压低 → 同数据升级 HIGH）。"""
        report = assess_correlation_regime(
            _mid_correlation_returns(), low_threshold=0.01, high_threshold=0.05
        )
        assert report.regime is CorrelationRegime.HIGH

    def test_correlation_matrix_properties(self) -> None:
        """相关矩阵对角=1，对称，值域[-1,1]。"""
        returns = {f"S{k}": _independent(50, k + 2) for k in range(3)}
        report = assess_correlation_regime(returns)
        n = len(report.symbols)
        for i in range(n):
            assert report.correlation_matrix[i][i] == pytest.approx(1.0)
            for j in range(n):
                assert -1.0 <= report.correlation_matrix[i][j] <= 1.0
                assert report.correlation_matrix[i][j] == pytest.approx(
                    report.correlation_matrix[j][i]
                )

    def test_max_pair_reported(self) -> None:
        """max_pair 记录最高相关标的对。"""
        returns = {f"S{k}": _common_factor(60, 1.0, 0.001, k) for k in range(3)}
        report = assess_correlation_regime(returns)
        assert len(report.max_pair) == 2
        assert report.max_pair[0] in report.symbols
        assert report.max_pair[1] in report.symbols
        assert report.max_pair[0] != report.max_pair[1]

    def test_avg_pairwise_excludes_diagonal(self) -> None:
        """平均成对相关不含对角（单对完全相关→avg≈1，收缩致轻微<1）。"""
        a = _independent(60, 1)
        b = [2.0 * x for x in a]
        report = assess_correlation_regime({"A": a, "B": b})
        assert report.avg_pairwise_correlation == pytest.approx(1.0, abs=0.05)

    def test_symbols_sorted(self) -> None:
        returns = {"B": _independent(40, 1), "A": _independent(40, 2)}
        report = assess_correlation_regime(returns)
        assert report.symbols == ("A", "B")


class TestInvalidThresholds:
    def test_negative_low_threshold(self) -> None:
        returns = {"A": _independent(30, 1), "B": _independent(30, 2)}
        with pytest.raises(InvalidCorrelationRegimeInputError):
            assess_correlation_regime(returns, low_threshold=-0.1)

    def test_low_not_less_than_high(self) -> None:
        returns = {"A": _independent(30, 1), "B": _independent(30, 2)}
        with pytest.raises(InvalidCorrelationRegimeInputError):
            assess_correlation_regime(returns, low_threshold=0.6, high_threshold=0.6)

    def test_high_above_one(self) -> None:
        returns = {"A": _independent(30, 1), "B": _independent(30, 2)}
        with pytest.raises(InvalidCorrelationRegimeInputError):
            assess_correlation_regime(returns, high_threshold=1.5)

    def test_non_finite_threshold(self) -> None:
        returns = {"A": _independent(30, 1), "B": _independent(30, 2)}
        with pytest.raises(InvalidCorrelationRegimeInputError):
            assess_correlation_regime(returns, high_threshold=float("nan"))
