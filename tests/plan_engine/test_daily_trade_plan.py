# [A_test] module_id: MOD-PLAN-011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-011 | 待统筹登记 | 缺口总账 GAP-F-09 + 45号 §4 W2
# [MODULE] tests.plan_engine.test_daily_trade_plan
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""DailyTradePlan (MOD-PLAN-011) 施工验证测试。

覆盖：
- 拟买清单：数量=min(boundary.max_add_position×档位缩放, firm 8% 硬顶)×总资金/
  计划买入点位（箱体下沿）折算整手；firm 硬顶与缩放各自的约束路径；参考价=
  箱体下沿；一句话逻辑模板含角色/档位/箱体/禁加价/必出价；不足一手跳过+note。
- 拟卖清单：每持仓两条规则（冲上沿必出全出/破下沿按比例减仓），触发价与
  数量折算；零股跳过。
- resolve_stance：final_scenario 前缀→激活三情景条目（stance+SHIFT_STANCE 缩放）；
  空三情景降级 NORMAL×1.0。
- 契约：DailyTradePlan.to_dict JSON 可序列化；非法输入 fail-closed。
纯内存构造（TomorrowBoundary/ScenarioPlan 直接 new），无 DB 无 CH。
"""

from __future__ import annotations

import json

import pytest

from zephyr.plan_engine.daily_trade_plan import (
    DailyTradePlan,
    DailyTradePlanConfig,
    TradePlanCandidate,
    TradePlanHolding,
    generate_daily_trade_plan,
    resolve_stance,
)
from zephyr.plan_engine.scenario_planner import ScenarioActionPlan, ScenarioPlan
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary

TRADE_DATE = "2026-08-24"


def _boundary(
    symbol: str = "600000.SH",
    box_upper: float = 10.0,
    box_lower: float = 9.5,
    max_add: float = 0.30,
) -> TomorrowBoundary:
    return TomorrowBoundary(
        symbol=symbol,
        box_upper=box_upper,
        box_lower=box_lower,
        max_add_position=max_add,
        no_add_price=box_upper * 0.98,
        must_exit_price=box_upper,
        breakout_confirm="放量站稳10分钟",
        computed_at=None,
    )


def _candidate(
    symbol: str = "600000.SH",
    role: str = "龙头",
    max_add: float = 0.30,
    box_lower: float = 9.5,
) -> TradePlanCandidate:
    return TradePlanCandidate(
        symbol=symbol,
        boundary=_boundary(symbol, box_lower=box_lower, max_add=max_add),
        role=role,
    )


# ══════════════════════════════════════════════════════════════
# 拟买清单
# ══════════════════════════════════════════════════════════════


class TestBuyList:
    def test_firm_cap_binding(self) -> None:
        # max_add 0.30×1.0=0.30 > firm 8% → cap=0.08；80000/9.5=8421 股→整手 8400
        plan = generate_daily_trade_plan(
            TRADE_DATE, [_candidate()], [], config=DailyTradePlanConfig(total_capital=1_000_000.0),
        )
        assert len(plan.buy_list) == 1
        item = plan.buy_list[0]
        assert item.direction == "BUY"
        assert item.symbol == "600000.SH"
        assert item.cap_weight == pytest.approx(0.08)
        assert item.reference_price == pytest.approx(9.5)
        assert item.quantity == 8400
        assert "龙头" in item.logic
        assert "NORMAL" in item.logic
        assert "9.50" in item.logic  # 箱体下沿
        assert "禁加价" in item.logic and "必出" in item.logic

    def test_scale_binding_below_firm_cap(self) -> None:
        # 保守档 ×0.5：0.30×0.5=0.15 > 0.08 仍 firm 截断；自定义 max_add 0.05×1.0=0.05 < 0.08 → cap=0.05
        plan = generate_daily_trade_plan(
            TRADE_DATE, [_candidate(max_add=0.05)], [],
            config=DailyTradePlanConfig(total_capital=1_000_000.0),
        )
        assert plan.buy_list[0].cap_weight == pytest.approx(0.05)
        # 50000/9.5=5263 股 → 5200
        assert plan.buy_list[0].quantity == 5200

    def test_conservative_scale_halves_quantity(self) -> None:
        plan_normal = generate_daily_trade_plan(
            TRADE_DATE, [_candidate(max_add=0.10)], [], stance="NORMAL", position_scale=1.0,
        )
        plan_cons = generate_daily_trade_plan(
            TRADE_DATE, [_candidate(max_add=0.10)], [], stance="CONSERVATIVE", position_scale=0.5,
        )
        assert plan_normal.buy_list[0].cap_weight == pytest.approx(0.08)  # firm 截断
        assert plan_cons.buy_list[0].cap_weight == pytest.approx(0.05)  # 0.10×0.5，低于 firm
        assert plan_cons.buy_list[0].quantity < plan_normal.buy_list[0].quantity

    def test_zero_quantity_skipped_with_note(self) -> None:
        # 高价小资金：cap 0.05×1000=50 元 < 一手 9500 元 → 跳过
        plan = generate_daily_trade_plan(
            TRADE_DATE, [_candidate(max_add=0.05)], [],
            config=DailyTradePlanConfig(total_capital=1_000.0),
        )
        assert plan.buy_list == ()
        assert any("不足一手" in n or "跳过" in n for n in plan.notes)

    def test_multiple_candidates(self) -> None:
        plan = generate_daily_trade_plan(
            TRADE_DATE,
            [_candidate("600000.SH", "龙头"), _candidate("000001.SZ", "中军")],
            [],
        )
        assert [i.symbol for i in plan.buy_list] == ["600000.SH", "000001.SZ"]


# ══════════════════════════════════════════════════════════════
# 拟卖清单
# ══════════════════════════════════════════════════════════════


class TestSellList:
    def test_exit_and_reduce_entries(self) -> None:
        holding = TradePlanHolding(
            symbol="600000.SH",
            weight=0.06,
            boundary=_boundary(),
            reference_price=9.8,
            reduce_fraction=0.5,
        )
        plan = generate_daily_trade_plan(
            TRADE_DATE, [], [holding], config=DailyTradePlanConfig(total_capital=1_000_000.0),
        )
        assert len(plan.sell_list) == 2
        by_trigger = {item.trigger_price: item for item in plan.sell_list}
        exit_item = by_trigger[10.0]  # 必出止盈=box_upper
        reduce_item = by_trigger[9.5]  # 破下沿减仓
        assert exit_item.direction == "SELL"
        # 持仓股数=0.06×1e6/9.8=6122 股→整手 6100；止盈全出
        assert exit_item.quantity == 6100
        # 减仓 50%：3050→整手 3000
        assert reduce_item.quantity == 3000
        assert "必出" in exit_item.logic
        assert "减仓" in reduce_item.logic

    def test_zero_position_skipped(self) -> None:
        holding = TradePlanHolding(
            symbol="600000.SH", weight=0.0, boundary=_boundary(), reference_price=9.8,
        )
        plan = generate_daily_trade_plan(TRADE_DATE, [], [holding])
        assert plan.sell_list == ()
        assert any("600000.SH" in n for n in plan.notes)


# ══════════════════════════════════════════════════════════════
# resolve_stance（ScenarioPlan → 档位/缩放）
# ══════════════════════════════════════════════════════════════


def _scenario_entry(name: str, shift: float) -> ScenarioActionPlan:
    return ScenarioActionPlan(
        name=name,
        open_pct_min=None,
        open_pct_max=None,
        stance={-1.0: "CONSERVATIVE", 0.0: "NORMAL", 1.0: "AGGRESSIVE"}[shift],
        final_shift=shift,
        max_add_position=0.30,
        no_add_price=None,
        reduce_trigger_price=None,
        must_exit_price=None,
        actions=[],
    )


class TestResolveStance:
    def test_high_open_activated(self) -> None:
        plan = ScenarioPlan(
            date=TRADE_DATE,
            three_scenarios=[
                _scenario_entry("HIGH_OPEN", 1.0),
                _scenario_entry("FLAT_OPEN", 0.0),
                _scenario_entry("LOW_OPEN", -1.0),
            ],
            auction_verification=None,
            final_scenario="HIGH_OPEN_REAL_UP",
            confidence_scale=1.0,
            degraded=False,
            reasons=[],
            trace={},
        )
        stance, scale = resolve_stance(plan)
        assert stance == "AGGRESSIVE"
        assert scale == pytest.approx(1.2)

    def test_flat_wash_selects_flat_entry(self) -> None:
        plan = ScenarioPlan(
            date=TRADE_DATE,
            three_scenarios=[
                _scenario_entry("HIGH_OPEN", 1.0),
                _scenario_entry("FLAT_OPEN", 0.0),
                _scenario_entry("LOW_OPEN", -1.0),
            ],
            auction_verification=None,
            final_scenario="FLAT_OPEN_WASH",
            confidence_scale=1.0,
            degraded=False,
            reasons=[],
            trace={},
        )
        stance, scale = resolve_stance(plan)
        assert stance == "NORMAL"
        assert scale == pytest.approx(1.0)

    def test_empty_scenarios_fallback(self) -> None:
        plan = ScenarioPlan(
            date=TRADE_DATE,
            three_scenarios=[],
            auction_verification=None,
            final_scenario="FLAT_OPEN_WASH",
            confidence_scale=1.0,
            degraded=True,
            reasons=[],
            trace={},
        )
        stance, scale = resolve_stance(plan)
        assert (stance, scale) == ("NORMAL", 1.0)


# ══════════════════════════════════════════════════════════════
# 契约与校验
# ══════════════════════════════════════════════════════════════


class TestContract:
    def test_to_dict_jsonable(self) -> None:
        plan = generate_daily_trade_plan(
            TRADE_DATE, [_candidate()], [
                TradePlanHolding(symbol="000001.SZ", weight=0.05, boundary=_boundary("000001.SZ"), reference_price=9.8),
            ],
        )
        assert isinstance(plan, DailyTradePlan)
        d = plan.to_dict()
        assert d["date"] == TRADE_DATE
        assert d["stance"] == "NORMAL"
        assert len(d["buy_list"]) == 1
        assert len(d["sell_list"]) == 2
        json.dumps(d, ensure_ascii=False)

    def test_invalid_input_fail_closed(self) -> None:
        with pytest.raises(ValueError):
            generate_daily_trade_plan("2026-13-99", [], [])  # 非法日期
        with pytest.raises(ValueError):
            generate_daily_trade_plan(TRADE_DATE, [{"not": "candidate"}], [])  # type: ignore[list-item]
        with pytest.raises(ValueError):
            generate_daily_trade_plan(TRADE_DATE, [], [], position_scale=0.0)
        with pytest.raises(ValueError):
            generate_daily_trade_plan(TRADE_DATE, [], [], stance="")
        with pytest.raises(ValueError):
            DailyTradePlanConfig(total_capital=0.0)
        with pytest.raises(ValueError):
            DailyTradePlanConfig(firm_single_cap=1.5)
        with pytest.raises(ValueError):
            TradePlanHolding(
                symbol="X", weight=1.5, boundary=_boundary("X"), reference_price=9.8,
            )
        with pytest.raises(ValueError):
            TradePlanCandidate(symbol="", boundary=_boundary())
