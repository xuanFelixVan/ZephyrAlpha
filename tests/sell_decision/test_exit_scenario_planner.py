# [BLUEPRINT] MOD-SELL-013 | docs/03_modules/MOD-SELL-013/
# [MODULE] zephyr.sell_decision.core.exit_scenario_planner
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_exit_scenario_planner.py
# [TTL] permanent
"""exit_scenario_planner（离场情景规划器）单元测试。

覆盖：
- 止损触发/高紧迫 → IMMEDIATE_EXIT 推荐
- 中紧迫 → SCALED_EXIT；低紧迫 → CONDITIONAL_HOLD；无风险 → HOLD
- T+1 内生：立即离场量受可卖权重约束（当日买入顺延提示）
- 情景排序确定性 + 理由留痕
- 非法输入 → InvalidExitPlanInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.exit_scenario_planner import (
    ExitPlanningInput,
    ExitScenario,
    InvalidExitPlanInputError,
    plan_exit_scenarios,
)


def _inp(**kw) -> ExitPlanningInput:
    base = {
        "symbol": "A",
        "weight": 0.10,
        "sellable_weight": 0.10,
        "pnl_pct": 0.0,
        "days_held": 5,
        "urgency": 0.0,
        "stop_triggered": False,
        "stop_reason": "",
    }
    base.update(kw)
    return ExitPlanningInput(**base)


class TestRecommendation:
    def test_stop_triggered_recommends_immediate(self) -> None:
        """止损触发 → 立即离场。"""
        plan = plan_exit_scenarios(_inp(stop_triggered=True, stop_reason="INITIAL_STOP"))
        assert plan.recommended is ExitScenario.IMMEDIATE_EXIT

    def test_high_urgency_recommends_immediate(self) -> None:
        """紧迫度 ≥0.8 → 立即离场。"""
        plan = plan_exit_scenarios(_inp(urgency=0.85))
        assert plan.recommended is ExitScenario.IMMEDIATE_EXIT

    def test_mid_urgency_recommends_scaled(self) -> None:
        """紧迫度 0.5~0.8 → 分批离场。"""
        plan = plan_exit_scenarios(_inp(urgency=0.6))
        assert plan.recommended is ExitScenario.SCALED_EXIT

    def test_low_urgency_recommends_conditional_hold(self) -> None:
        """低紧迫但有持仓 → 条件持有（守止损线）。"""
        plan = plan_exit_scenarios(_inp(urgency=0.3))
        assert plan.recommended is ExitScenario.CONDITIONAL_HOLD

    def test_zero_urgency_recommends_hold(self) -> None:
        """无紧迫 → 继续持有。"""
        plan = plan_exit_scenarios(_inp(urgency=0.0))
        assert plan.recommended is ExitScenario.HOLD


class TestT1Constraint:
    def test_immediate_limited_by_sellable(self) -> None:
        """立即离场动作量=T+1 可卖权重（非全仓）。"""
        plan = plan_exit_scenarios(_inp(urgency=0.9, weight=0.10, sellable_weight=0.06))
        immediate = next(s for s in plan.scenarios if s.scenario is ExitScenario.IMMEDIATE_EXIT)
        assert immediate.action_weight == pytest.approx(0.06)

    def test_t1_deferral_noted(self) -> None:
        """当日买入部分顺延提示（T+1 约束内生）。"""
        plan = plan_exit_scenarios(_inp(urgency=0.9, weight=0.10, sellable_weight=0.06))
        assert any("T+1" in c for c in plan.constraints)

    def test_no_deferral_note_when_fully_sellable(self) -> None:
        plan = plan_exit_scenarios(_inp(urgency=0.9, weight=0.10, sellable_weight=0.10))
        assert not any("顺延" in c for c in plan.constraints)


class TestScenarioStructure:
    def test_scenarios_sorted_by_priority(self) -> None:
        """情景按优先级升序（0=推荐）。"""
        plan = plan_exit_scenarios(_inp(urgency=0.6))
        priorities = [s.priority for s in plan.scenarios]
        assert priorities == sorted(priorities)
        assert plan.scenarios[0].scenario is plan.recommended

    def test_rationale_recorded(self) -> None:
        """每个情景有人类可读理由。"""
        plan = plan_exit_scenarios(_inp(urgency=0.6))
        assert all(s.rationale for s in plan.scenarios)

    def test_scaled_exit_action_is_partial(self) -> None:
        """分批离场首批动作量 < 可卖权重（不全清）。"""
        plan = plan_exit_scenarios(_inp(urgency=0.6, weight=0.10, sellable_weight=0.10))
        scaled = next(s for s in plan.scenarios if s.scenario is ExitScenario.SCALED_EXIT)
        assert 0.0 < scaled.action_weight < 0.10

    def test_hold_action_zero(self) -> None:
        plan = plan_exit_scenarios(_inp(urgency=0.0))
        hold = next(s for s in plan.scenarios if s.scenario is ExitScenario.HOLD)
        assert hold.action_weight == 0.0


class TestInvalidInput:
    def test_negative_weight(self) -> None:
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(weight=-0.1))

    def test_sellable_above_weight(self) -> None:
        """可卖>持仓（数据异常）→ 拒绝。"""
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(weight=0.05, sellable_weight=0.10))

    def test_urgency_out_of_range(self) -> None:
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(urgency=1.5))
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(urgency=-0.1))

    def test_empty_symbol(self) -> None:
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(symbol=""))

    def test_negative_days(self) -> None:
        with pytest.raises(InvalidExitPlanInputError):
            plan_exit_scenarios(_inp(days_held=-1))
