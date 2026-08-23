# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/MOD-SELL-017/
# [MODULE] zephyr.sell_decision.core.scaling_out_architect
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_scaling_out_architect.py
# [TTL] permanent
"""scaling_out_architect（分批卖出架构师）单元测试。

覆盖：
- 紧迫度→节奏映射（高→前重/中→均匀/低→后重）
- 批次分数和=1；首批即时执行；后续批次带触发条件
- T+1 内生：首批动作量≤可卖权重，超出顺延标注
- 非法输入 → InvalidScalingPlanInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.scaling_out_architect import (
    InvalidScalingPlanInputError,
    PacingStyle,
    TrancheTrigger,
    design_scaling_plan,
)


class TestPacing:
    def test_high_urgency_front_loaded(self) -> None:
        """紧迫 ≥0.8 → 前重后轻，首批分数最大。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.9)
        assert plan.pacing is PacingStyle.FRONT_LOADED
        fractions = [t.fraction for t in plan.tranches]
        assert fractions[0] == max(fractions)

    def test_mid_urgency_even(self) -> None:
        """紧迫 0.5~0.8 → 均匀分批。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.6)
        assert plan.pacing is PacingStyle.EVEN
        fractions = [t.fraction for t in plan.tranches]
        assert fractions[0] == pytest.approx(fractions[-1], abs=1e-9)

    def test_low_urgency_back_loaded(self) -> None:
        """紧迫 (0,0.5) → 前轻后重（保留反弹空间）。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.3)
        assert plan.pacing is PacingStyle.BACK_LOADED
        fractions = [t.fraction for t in plan.tranches]
        assert fractions[-1] == max(fractions)


class TestTrancheStructure:
    def test_fractions_sum_to_one(self) -> None:
        for urgency in (0.9, 0.6, 0.3):
            plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=urgency)
            assert sum(t.fraction for t in plan.tranches) == pytest.approx(1.0)

    def test_default_tranche_count_three(self) -> None:
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.6)
        assert len(plan.tranches) == 3

    def test_first_tranche_immediate_rest_triggered(self) -> None:
        """首批即时，后续批次带非即时触发条件。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.6)
        assert plan.tranches[0].trigger is TrancheTrigger.IMMEDIATE
        assert all(t.trigger is not TrancheTrigger.IMMEDIATE for t in plan.tranches[1:])

    def test_cumulative_fraction_monotonic(self) -> None:
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.9)
        cum = [t.cumulative_fraction for t in plan.tranches]
        assert cum == sorted(cum)
        assert cum[-1] == pytest.approx(1.0)

    def test_weights_match_fractions(self) -> None:
        """批次权重=总权重×分数。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.6)
        for t in plan.tranches:
            assert t.weight == pytest.approx(0.12 * t.fraction)


class TestT1Constraint:
    def test_first_tranche_capped_by_sellable(self) -> None:
        """首批动作量 ≤ T+1 可卖权重。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.05, urgency=0.9)
        assert plan.tranches[0].weight <= 0.05 + 1e-12

    def test_deferred_weight_recorded(self) -> None:
        """T+1 冻结顺延量留痕。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.05, urgency=0.9)
        assert plan.t1_deferred_weight > 0.0

    def test_no_deferral_when_sellable_covers_first(self) -> None:
        """可卖覆盖首批 → 无顺延。"""
        plan = design_scaling_plan(total_weight=0.12, sellable_weight=0.12, urgency=0.6)
        assert plan.t1_deferred_weight == pytest.approx(0.0)


class TestInvalidInput:
    def test_non_positive_total_weight(self) -> None:
        with pytest.raises(InvalidScalingPlanInputError):
            design_scaling_plan(total_weight=0.0, sellable_weight=0.0, urgency=0.5)

    def test_sellable_above_total(self) -> None:
        with pytest.raises(InvalidScalingPlanInputError):
            design_scaling_plan(total_weight=0.05, sellable_weight=0.10, urgency=0.5)

    def test_urgency_out_of_range(self) -> None:
        with pytest.raises(InvalidScalingPlanInputError):
            design_scaling_plan(total_weight=0.1, sellable_weight=0.1, urgency=1.2)

    def test_tranche_count_out_of_range(self) -> None:
        with pytest.raises(InvalidScalingPlanInputError):
            design_scaling_plan(total_weight=0.1, sellable_weight=0.1, urgency=0.5, tranche_count=1)
        with pytest.raises(InvalidScalingPlanInputError):
            design_scaling_plan(total_weight=0.1, sellable_weight=0.1, urgency=0.5, tranche_count=6)
