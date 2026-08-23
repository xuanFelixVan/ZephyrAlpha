# [BLUEPRINT] MOD-SELL-012 | docs/03_modules/MOD-SELL-012/
# [MODULE] zephyr.sell_decision.core.sell_execution_quality_tracker
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_sell_execution_quality_tracker.py
# [TTL] permanent
"""sell_execution_quality_tracker（卖出执行质量追踪）单元测试。

覆盖：
- 滑点口径：卖出滑点=(决策价−成交价)/决策价（正=卖亏）
- 加权平均滑点、最差滑点、质量分级（GOOD/ACCEPTABLE/DEGRADED）
- 超阈值成交明细留痕
- 非法输入 → InvalidFillRecordError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.sell_execution_quality_tracker import (
    ExecutionQualityGrade,
    InvalidFillRecordError,
    SellFillRecord,
    evaluate_execution_quality,
)


def _fill(symbol: str = "A", decision: float = 10.0, executed: float = 9.98, weight: float = 0.05) -> SellFillRecord:
    return SellFillRecord(
        symbol=symbol,
        decision_price=decision,
        executed_price=executed,
        weight=weight,
    )


class TestSlippage:
    def test_slippage_sign_sell(self) -> None:
        """卖出 10.0→9.98：滑点 +0.2%（卖亏为正）。"""
        report = evaluate_execution_quality([_fill()])
        assert report.fills[0].slippage_pct == pytest.approx(0.002)

    def test_negative_slippage_better_execution(self) -> None:
        """卖出 10.0→10.02：滑点 −0.2%（卖得更好）。"""
        report = evaluate_execution_quality([_fill(executed=10.02)])
        assert report.fills[0].slippage_pct == pytest.approx(-0.002)

    def test_weighted_average(self) -> None:
        """加权平均滑点按权重加权。"""
        report = evaluate_execution_quality(
            [
                _fill(symbol="A", executed=9.96, weight=0.06),  # +0.4%
                _fill(symbol="B", executed=10.00, weight=0.02),  # 0%
            ]
        )
        # (0.004*0.06 + 0*0.02)/0.08 = 0.003
        assert report.avg_slippage_pct == pytest.approx(0.003)

    def test_worst_slippage_tracked(self) -> None:
        report = evaluate_execution_quality(
            [
                _fill(symbol="A", executed=9.98),  # +0.2%
                _fill(symbol="B", executed=9.90),  # +1.0%
            ]
        )
        assert report.max_slippage_pct == pytest.approx(0.01)
        assert report.worst_symbol == "B"


class TestGrading:
    def test_good_grade(self) -> None:
        """平均滑点 ≤0.1% → GOOD。"""
        report = evaluate_execution_quality([_fill(executed=9.995)])
        assert report.grade is ExecutionQualityGrade.GOOD

    def test_acceptable_grade(self) -> None:
        """平均滑点 0.1%~0.3% → ACCEPTABLE。"""
        report = evaluate_execution_quality([_fill(executed=9.98)])
        assert report.grade is ExecutionQualityGrade.ACCEPTABLE

    def test_degraded_grade_and_warning(self) -> None:
        """平均滑点 >0.3% → DEGRADED + 预警。"""
        report = evaluate_execution_quality([_fill(executed=9.95)])
        assert report.grade is ExecutionQualityGrade.DEGRADED
        assert report.warnings

    def test_custom_thresholds(self) -> None:
        """阈值可覆写。"""
        report = evaluate_execution_quality(
            [_fill(executed=9.98)], good_threshold_pct=0.001
        )
        assert report.grade is not ExecutionQualityGrade.GOOD

    def test_outlier_fills_listed(self) -> None:
        """超阈值的单笔成交留痕。"""
        report = evaluate_execution_quality(
            [
                _fill(symbol="A", executed=9.99, weight=0.04),  # 0.1%
                _fill(symbol="B", executed=9.90, weight=0.01),  # 1.0% 超阈
            ]
        )
        assert "B" in report.outlier_symbols

    def test_empty_fills(self) -> None:
        report = evaluate_execution_quality([])
        assert report.fills == ()
        assert report.avg_slippage_pct == 0.0


class TestInvalidInput:
    def test_non_positive_decision_price(self) -> None:
        with pytest.raises(InvalidFillRecordError):
            evaluate_execution_quality([_fill(decision=0.0)])

    def test_non_positive_executed_price(self) -> None:
        with pytest.raises(InvalidFillRecordError):
            evaluate_execution_quality([_fill(executed=-1.0)])

    def test_negative_weight(self) -> None:
        with pytest.raises(InvalidFillRecordError):
            evaluate_execution_quality([_fill(weight=-0.01)])

    def test_empty_symbol(self) -> None:
        with pytest.raises(InvalidFillRecordError):
            evaluate_execution_quality([_fill(symbol="")])

    def test_threshold_out_of_range(self) -> None:
        with pytest.raises(InvalidFillRecordError):
            evaluate_execution_quality([_fill()], good_threshold_pct=-0.1)
