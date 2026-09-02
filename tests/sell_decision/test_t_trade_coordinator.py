# [BLUEPRINT] MOD-SELL-018 | docs/03_modules/MOD-SELL-018/
# [MODULE] zephyr.sell_decision.core.t_trade_coordinator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_t_trade_coordinator.py
# [TTL] permanent
"""t_trade_coordinator（做T 协调器，T+1 规则内）单元测试。

覆盖：
- 卖出量≤T+1可卖量（当日买入不可卖的硬约束内生）
- 日终仓位复原（买回量=卖出量）
- 净价差=预期价差−往返成本；净价差>最小边际才 viable
- 成本含做T额外成本（宪章§3约束一）
- 非法输入 → InvalidTTradeInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.t_trade_coordinator import (
    InvalidTTradeInputError,
    TTradeDirection,
    TTradeInput,
    plan_t_trade,
)


def _inp(**kw) -> TTradeInput:
    base = {
        "symbol": "A",
        "direction": TTradeDirection.REVERSE_T,
        "sellable_weight": 0.10,
        "planned_weight": 0.05,
        "expected_spread_pct": 0.012,
        "round_trip_cost_pct": 0.002,
        "min_edge_pct": 0.003,
    }
    base.update(kw)
    return TTradeInput(**base)


class TestViability:
    def test_viable_when_edge_above_min(self) -> None:
        """净价差 0.010 > 最小边际 0.003 → viable。"""
        plan = plan_t_trade(_inp())
        assert plan.viable is True
        assert plan.net_edge_pct == pytest.approx(0.012 - 0.002)

    def test_not_viable_when_edge_below_min(self) -> None:
        """价差 0.0025 − 成本 0.002 = 0.0005 < 0.003 → 不做。"""
        plan = plan_t_trade(_inp(expected_spread_pct=0.0025))
        assert plan.viable is False

    def test_negative_spread_not_viable(self) -> None:
        """预期价差为负 → 不做。"""
        plan = plan_t_trade(_inp(expected_spread_pct=-0.005))
        assert plan.viable is False


class TestT1Rules:
    def test_planned_capped_by_sellable(self) -> None:
        """计划量超可卖 → 截断到可卖（T+1 内生）。"""
        plan = plan_t_trade(_inp(sellable_weight=0.03, planned_weight=0.05))
        assert plan.sell_weight == pytest.approx(0.03)

    def test_zero_sellable_no_trade(self) -> None:
        """可卖=0（全仓当日买入）→ 不可做T。"""
        plan = plan_t_trade(_inp(sellable_weight=0.0))
        assert plan.viable is False
        assert plan.sell_weight == 0.0

    def test_buyback_equals_sell(self) -> None:
        """买回量=卖出量（日终仓位复原）。"""
        plan = plan_t_trade(_inp())
        assert plan.buyback_weight == pytest.approx(plan.sell_weight)

    def test_t1_constraint_note_on_cap(self) -> None:
        """截断时 constraints 留痕 T+1。"""
        plan = plan_t_trade(_inp(sellable_weight=0.03, planned_weight=0.05))
        assert any("T+1" in c for c in plan.constraints)


class TestDirections:
    def test_reverse_t_sell_first(self) -> None:
        """倒T=先卖后买（高位卖出低位买回）。"""
        plan = plan_t_trade(_inp(direction=TTradeDirection.REVERSE_T))
        assert plan.direction is TTradeDirection.REVERSE_T

    def test_positive_t_buy_first(self) -> None:
        """正T=先买后卖（低位买入，卖出用原底仓）。"""
        plan = plan_t_trade(_inp(direction=TTradeDirection.POSITIVE_T))
        assert plan.direction is TTradeDirection.POSITIVE_T

    def test_positive_t_sell_also_capped(self) -> None:
        """正T的卖出腿同样只能用可卖底仓。"""
        plan = plan_t_trade(_inp(direction=TTradeDirection.POSITIVE_T, sellable_weight=0.02, planned_weight=0.05))
        assert plan.sell_weight == pytest.approx(0.02)


class TestInvalidInput:
    def test_empty_symbol(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(symbol=""))

    def test_negative_sellable(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(sellable_weight=-0.01))

    def test_negative_planned(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(planned_weight=-0.01))

    def test_negative_cost(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(round_trip_cost_pct=-0.001))

    def test_negative_min_edge(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(min_edge_pct=-0.001))

    def test_non_finite_spread(self) -> None:
        with pytest.raises(InvalidTTradeInputError):
            plan_t_trade(_inp(expected_spread_pct=float("nan")))
