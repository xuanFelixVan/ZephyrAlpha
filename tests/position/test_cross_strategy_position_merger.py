# [BLUEPRINT] MOD-POS-005 | docs/03_modules/MOD-POS-005/
# [MODULE] zephyr.position.core.cross_strategy_position_merger
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_cross_strategy_position_merger.py
# [TTL] permanent
"""cross_strategy_position_merger（跨策略仓位合并器）单元测试。

覆盖：
- 组合权重 = Σ 子策略资金占比 × 子策略账本权重
- 同标的多策略净额合并（netting）与毛额保留两种口径
- 资金占比缺省=等分；占比和<1 留现金余量；>1 拒绝
- 非法输入（空簿/占比不齐/非有限值）→ InvalidMergerInputError
"""

from __future__ import annotations

import pytest

from zephyr.position.core.cross_strategy_position_merger import (
    InvalidMergerInputError,
    merge_strategy_books,
)


class TestMerge:
    def test_single_book_passthrough(self) -> None:
        """单策略满仓 → 组合=账本原样。"""
        result = merge_strategy_books({"S1": {"A": 0.6, "B": 0.4}})
        assert result.weights["A"] == pytest.approx(0.6)
        assert result.weights["B"] == pytest.approx(0.4)

    def test_capital_weighted_merge(self) -> None:
        """两策略等资（各 0.5）→ 组合权重=均值。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.8}, "S2": {"A": 0.4, "B": 0.6}},
            allocations={"S1": 0.5, "S2": 0.5},
        )
        assert result.weights["A"] == pytest.approx(0.6)
        assert result.weights["B"] == pytest.approx(0.3)

    def test_netting_opposite_signs(self) -> None:
        """同标的一多一空 → 净额抵消（等资 0.5×(0.5−0.2)=0.15）。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.5}, "S2": {"A": -0.2}},
            allocations={"S1": 0.5, "S2": 0.5},
        )
        assert result.weights["A"] == pytest.approx(0.15)

    def test_full_netting_to_zero_drops_symbol(self) -> None:
        """完全抵消 → 标的不出现在净结果（净额 0 不留占位）。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.5}, "S2": {"A": -0.5}},
        )
        assert "A" not in result.weights

    def test_gross_exposure_sums_absolute(self) -> None:
        """gross=Σ|权重|（含抵消前的毛口径）。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.5}, "S2": {"A": -0.2, "B": 0.1}},
        )
        # 合并后: A=0.15(等资0.5·(0.5-0.2)), B=0.05 → net_gross=0.2
        assert result.gross_exposure == pytest.approx(abs(0.15) + abs(0.05))

    def test_net_exposure_signed_sum(self) -> None:
        """net=Σ权重（带符号）。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.5}, "S2": {"A": -0.2, "B": 0.1}},
        )
        assert result.net_exposure == pytest.approx(0.15 + 0.05)

    def test_default_allocations_equal_split(self) -> None:
        """缺省占比=等分 1/N。"""
        result = merge_strategy_books({"S1": {"A": 1.0}, "S2": {"B": 1.0}})
        assert result.weights["A"] == pytest.approx(0.5)
        assert result.weights["B"] == pytest.approx(0.5)

    def test_allocations_below_one_leaves_cash(self) -> None:
        """占比和 0.8 → 组合总净敞口 0.8（余 0.2 现金）。"""
        result = merge_strategy_books({"S1": {"A": 1.0}}, allocations={"S1": 0.8})
        assert result.weights["A"] == pytest.approx(0.8)
        assert result.cash_fraction == pytest.approx(0.2)

    def test_contributors_recorded(self) -> None:
        """contributors 记录每个标的的来源策略。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.8}, "S2": {"A": 0.4, "B": 0.6}},
        )
        assert set(result.contributors["A"]) == {"S1", "S2"}
        assert result.contributors["B"] == ("S2",)

    def test_netting_warning_on_offset(self) -> None:
        """同标的多空抵消 → warnings 留痕。"""
        result = merge_strategy_books(
            {"S1": {"A": 0.5}, "S2": {"A": -0.3}},
        )
        assert any("A" in w for w in result.warnings)


class TestInvalidInput:
    def test_empty_books(self) -> None:
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({})

    def test_allocation_strategy_mismatch(self) -> None:
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({"S1": {"A": 0.5}}, allocations={"S2": 1.0})

    def test_allocation_sum_above_one(self) -> None:
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books(
                {"S1": {"A": 0.5}, "S2": {"A": 0.5}},
                allocations={"S1": 0.7, "S2": 0.7},
            )

    def test_negative_allocation(self) -> None:
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({"S1": {"A": 0.5}}, allocations={"S1": -0.1})

    def test_non_finite_weight(self) -> None:
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({"S1": {"A": float("nan")}})
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({"S1": {"A": float("inf")}})

    def test_empty_book_rejected(self) -> None:
        """某策略空账本（无持仓意图也要显式给 0 权重，不接受空 dict）。"""
        with pytest.raises(InvalidMergerInputError):
            merge_strategy_books({"S1": {}})
