# [A_test] module_id: MOD-PLAN-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-001 | docs/03_modules/_domain_plan_engine/ | §
# [MODULE] tests.plan_engine.test_plan_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""plan_engine 施工验证测试。

覆盖：
- 3 dataclass：TomorrowBoundary / ConstraintState / BoundedActionAdvice
- 3 模块：TomorrowBoundaryPlanner / PremarketConstraintLoader / ClosingSessionDecision
"""

from __future__ import annotations

import pytest

from zephyr.plan_engine.closing_session_decision import (
    ADD_POSITION_THRESHOLD,
    REDUCE_POSITION_THRESHOLD,
    BoundedActionAdvice,
    ClosingSessionDecision,
)
from zephyr.plan_engine.premarket_constraint_loader import (
    SCENARIO_LIST,
    ConstraintState,
    PremarketConstraintLoader,
)
from zephyr.plan_engine.tomorrow_boundary_planner import (
    BREAKOUT_CONFIRM_CONDITION,
    DEFAULT_MAX_ADD_POSITION,
    TomorrowBoundary,
    TomorrowBoundaryPlanner,
)

# ══════════════════════════════════════════════════════════════
# TomorrowBoundary dataclass
# ══════════════════════════════════════════════════════════════


class TestTomorrowBoundary:
    """TomorrowBoundary 契约验证。"""

    def test_fields(self):
        """字段完整。"""
        b = TomorrowBoundary(
            symbol="600519",
            box_upper=11.0,
            box_lower=9.0,
            max_add_position=0.30,
            no_add_price=10.78,
            must_exit_price=11.0,
            breakout_confirm="放量站稳10分钟",
        )
        assert b.symbol == "600519"
        assert b.box_upper == 11.0
        assert b.box_lower == 9.0
        assert b.max_add_position == 0.30
        assert b.no_add_price == 10.78
        assert b.must_exit_price == 11.0
        assert b.breakout_confirm == "放量站稳10分钟"


# ══════════════════════════════════════════════════════════════
# ConstraintState dataclass
# ══════════════════════════════════════════════════════════════


class TestConstraintState:
    """ConstraintState 契约验证。"""

    def test_fields(self):
        """字段完整。"""
        b = TomorrowBoundary(
            symbol="600519", box_upper=11.0, box_lower=9.0,
            max_add_position=0.30, no_add_price=10.78,
            must_exit_price=11.0, breakout_confirm="放量站稳10分钟",
        )
        cs = ConstraintState(
            symbol="600519",
            boundary=b,
            scenario="FLAT_OPEN_WASH",
            initialized=True,
        )
        assert cs.symbol == "600519"
        assert cs.boundary is b
        assert cs.scenario == "FLAT_OPEN_WASH"
        assert cs.initialized is True


# ══════════════════════════════════════════════════════════════
# BoundedActionAdvice dataclass
# ══════════════════════════════════════════════════════════════


class TestBoundedActionAdvice:
    """BoundedActionAdvice 契约验证。"""

    def test_fields(self):
        """字段完整。"""
        advice = BoundedActionAdvice(
            symbol="600519",
            action="ADD",
            price_bound=(9.0, 11.0),
            max_weight=0.30,
            reason="高开概率75%>70%，加仓博高开",
        )
        assert advice.symbol == "600519"
        assert advice.action == "ADD"
        assert advice.price_bound == (9.0, 11.0)
        assert advice.max_weight == 0.30
        assert "加仓" in advice.reason


# ══════════════════════════════════════════════════════════════
# TomorrowBoundaryPlanner
# ══════════════════════════════════════════════════════════════


class TestTomorrowBoundaryPlanner:
    """明日预案引擎。"""

    def test_compute_boundary(self):
        """计算明日边界。"""
        planner = TomorrowBoundaryPlanner()
        market_state = {"close": 10.0, "amplitude": 0.03}
        b = planner.compute_boundary("600519", market_state)
        assert b.symbol == "600519"
        assert b.box_upper == pytest.approx(10.3)
        assert b.box_lower == pytest.approx(9.7)
        assert b.max_add_position == DEFAULT_MAX_ADD_POSITION
        assert b.breakout_confirm == BREAKOUT_CONFIRM_CONDITION

    def test_compute_boundary_zero_close_raises(self):
        """收盘价异常→ValueError。"""
        planner = TomorrowBoundaryPlanner()
        with pytest.raises(ValueError, match="收盘价异常"):
            planner.compute_boundary("600519", {"close": 0.0})

    def test_no_add_price_near_upper(self):
        """禁加仓价位接近上沿。"""
        planner = TomorrowBoundaryPlanner()
        b = planner.compute_boundary("600519", {"close": 10.0, "amplitude": 0.03})
        assert b.no_add_price == pytest.approx(b.box_upper * 0.98)


# ══════════════════════════════════════════════════════════════
# PremarketConstraintLoader
# ══════════════════════════════════════════════════════════════


class TestPremarketConstraintLoader:
    """盘前预案加载器。"""

    def _make_boundary(self) -> TomorrowBoundary:
        return TomorrowBoundary(
            symbol="600519", box_upper=11.0, box_lower=9.0,
            max_add_position=0.30, no_add_price=10.78,
            must_exit_price=11.0, breakout_confirm="放量站稳10分钟",
        )

    def test_load_constraint(self):
        """加载约束状态。"""
        loader = PremarketConstraintLoader()
        cs = loader.load_constraint("600519", self._make_boundary())
        assert cs.initialized is True
        assert cs.symbol == "600519"
        assert cs.scenario in SCENARIO_LIST

    def test_load_constraint_none_boundary_raises(self):
        """boundary=None→ValueError（致命）。"""
        loader = PremarketConstraintLoader()
        with pytest.raises(ValueError, match="未加载"):
            loader.load_constraint("600519", None)

    def test_scenario_match_high_open(self):
        """高开匹配。"""
        loader = PremarketConstraintLoader()
        auction = {"open_price": 10.5, "prev_close": 10.0}
        scenario = loader._match_scenario(auction)
        assert scenario == "HIGH_OPEN_REAL_UP"

    def test_scenario_match_low_open(self):
        """低开匹配。"""
        loader = PremarketConstraintLoader()
        auction = {"open_price": 9.5, "prev_close": 10.0}
        scenario = loader._match_scenario(auction)
        assert scenario == "LOW_OPEN_REAL_DOWN"

    def test_scenario_match_flat_open(self):
        """平开匹配。"""
        loader = PremarketConstraintLoader()
        auction = {"open_price": 10.05, "prev_close": 10.0}
        scenario = loader._match_scenario(auction)
        assert scenario == "FLAT_OPEN_WASH"

    def test_scenario_list_count(self):
        """9 种情景。"""
        assert len(SCENARIO_LIST) == 9


# ══════════════════════════════════════════════════════════════
# ClosingSessionDecision
# ══════════════════════════════════════════════════════════════


class TestClosingSessionDecision:
    """尾盘决策引擎。"""

    def test_add_on_high_open_prob(self):
        """高开概率>70%→ADD。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        position = {"weight": 0.10}
        advice = dec.decide("600519", inference, position, high_open_prob=0.75)
        assert advice.action == "ADD"
        assert advice.max_weight == 0.30

    def test_reduce_on_low_open_prob(self):
        """低开概率>60%→REDUCE。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        position = {"weight": 0.10}
        advice = dec.decide("600519", inference, position, low_open_prob=0.65)
        assert advice.action == "REDUCE"
        assert advice.max_weight == 0.10

    def test_hold_default(self):
        """概率未超阈值→HOLD。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        position = {"weight": 0.10}
        advice = dec.decide("600519", inference, position, high_open_prob=0.50, low_open_prob=0.40)
        assert advice.action == "HOLD"

    def test_add_threshold_boundary(self):
        """恰好等于阈值→不触发。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        position = {"weight": 0.10}
        advice = dec.decide("600519", inference, position, high_open_prob=ADD_POSITION_THRESHOLD)
        assert advice.action == "HOLD"  # 严格大于才触发

    def test_reduce_threshold_boundary(self):
        """恰好等于阈值→不触发。"""
        dec = ClosingSessionDecision()
        inference = {"box_upper": 11.0, "box_lower": 9.0}
        position = {"weight": 0.10}
        advice = dec.decide("600519", inference, position, low_open_prob=REDUCE_POSITION_THRESHOLD)
        assert advice.action == "HOLD"
