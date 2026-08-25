# [BLUEPRINT] MOD-INF-071 | docs/03_modules/_domain_infrastructure_runtime/warm_plane/blueprint.md | §test
# [MODULE] tests.infrastructure.test_warm_plane_budget
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.warm_plane_budget
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_warm_plane_budget.py
# [A_test] module_id: MOD-INF-071 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-071 单元测试: Warm 平面（10ms~1s）时延预算与 11 态路由表 SSOT。

覆盖: 200/300/500ms 预算分解与累计 200/500/1000ms 真源值、check_budget 逐阶段
与端到端判定、超 1s 过期信号动作声明（P3 用缓存信号）、11 态路由表（7 行）
真源值与权重 Σ=1、状态码全覆盖唯一映射、未知阶段/未知状态码 Fail-Closed、
单向通道声明（signal:*+market:state，仅声明不执行）。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.warm_plane_budget import (
    MARKET_STATE_ROUTING,
    WARM_PLANE_BUDGET,
    WarmPlaneBudgetError,
    WarmPlaneRoutingError,
    check_budget,
    get_routing,
    render_warm_plane_declaration,
)


class TestBudgetBreakdown:
    def test_stage_budgets_200_300_500(self):
        budgets = {stage.name: stage.budget_ms for stage in WARM_PLANE_BUDGET.stages}
        assert budgets["incremental_factor_compute"] == 200.0
        assert budgets["signal_gen_aggregate"] == 300.0
        assert budgets["strategy_route_position"] == 500.0

    def test_cumulative_budgets(self):
        cumulative = [stage.cumulative_budget_ms for stage in WARM_PLANE_BUDGET.stages]
        assert cumulative == [200.0, 500.0, 1000.0]

    def test_total_budget_1s(self):
        assert WARM_PLANE_BUDGET.total_budget_ms == 1000.0


class TestCheckBudget:
    def test_within_budget(self):
        verdict = check_budget(
            {
                "incremental_factor_compute": 150.0,
                "signal_gen_aggregate": 250.0,
                "strategy_route_position": 400.0,
            }
        )
        assert verdict.within_budget is True
        assert verdict.overrun_stages == ()
        assert verdict.action == "none"

    def test_stage_overrun(self):
        verdict = check_budget(
            {
                "incremental_factor_compute": 250.0,
                "signal_gen_aggregate": 250.0,
                "strategy_route_position": 400.0,
            }
        )
        assert verdict.within_budget is False
        assert verdict.overrun_stages == ("incremental_factor_compute",)
        assert verdict.action == "stale_signal_use_cache"

    def test_total_overrun_without_stage_overrun(self):
        verdict = check_budget(
            {
                "incremental_factor_compute": 200.0,
                "signal_gen_aggregate": 300.0,
                "strategy_route_position": 500.5,
            }
        )
        assert verdict.within_budget is False
        assert verdict.action == "stale_signal_use_cache"

    def test_unknown_stage_fail_closed(self):
        with pytest.raises(WarmPlaneBudgetError):
            check_budget({"incremental_factor_compute": 1.0, "mystery": 1.0})

    def test_missing_stage_fail_closed(self):
        with pytest.raises(WarmPlaneBudgetError):
            check_budget({"incremental_factor_compute": 1.0})

    def test_negative_latency_fail_closed(self):
        with pytest.raises(WarmPlaneBudgetError):
            check_budget(
                {
                    "incremental_factor_compute": -1.0,
                    "signal_gen_aggregate": 1.0,
                    "strategy_route_position": 1.0,
                }
            )


class TestRoutingTable:
    def test_seven_rows_cover_eleven_states(self):
        codes = [code for row in MARKET_STATE_ROUTING for code in row.state_codes]
        assert len(MARKET_STATE_ROUTING) == 7
        assert len(codes) == 11
        assert len(set(codes)) == 11

    def test_weights_sum_to_one(self):
        for row in MARKET_STATE_ROUTING:
            assert sum(row.signal_weights.values()) == pytest.approx(1.0)

    def test_trend_up(self):
        row = get_routing("①")
        assert row is get_routing("②")
        assert row.route_strategy == "momentum_first"
        assert row.signal_weights == {"momentum": 0.6, "value": 0.2, "defense": 0.2}
        assert row.position_cap_range == (0.80, 0.80)

    def test_high_volatility(self):
        row = get_routing("③")
        assert row.route_strategy == "t0_activate"
        assert row.signal_weights == {"momentum": 0.3, "t0": 0.4, "defense": 0.3}
        assert row.position_cap_range == (0.60, 0.60)

    def test_range_bound(self):
        row = get_routing("④")
        assert row is get_routing("⑤")
        assert row.route_strategy == "mean_reversion_first"
        assert row.position_cap_range == (0.50, 0.50)

    def test_squeeze_breakout_cap_band(self):
        row = get_routing("⑥")
        assert row.route_strategy == "breakout_standby"
        assert row.position_cap_range == (0.40, 0.70)

    def test_trend_down_cap_band(self):
        row = get_routing("⑦")
        assert row is get_routing("⑧") is get_routing("⑨")
        assert row.route_strategy == "defense_dominant"
        assert row.signal_weights == {"defense": 0.6, "value": 0.3, "momentum": 0.1}
        assert row.position_cap_range == (0.10, 0.30)

    def test_event_driven_cap_none(self):
        row = get_routing("⑩")
        assert row.route_strategy == "event_activate"
        assert row.position_cap_range is None

    def test_sector_rotation(self):
        row = get_routing("⑪")
        assert row.route_strategy == "rotation_activate"
        assert row.position_cap_range == (0.70, 0.70)

    def test_unknown_state_fail_closed(self):
        with pytest.raises(WarmPlaneRoutingError):
            get_routing("⑫")


class TestDeclaration:
    def test_render_declaration_shape(self):
        decl = render_warm_plane_declaration()
        assert decl["plane"] == "warm"
        assert decl["latency_band"] == "10ms~1s"
        assert decl["total_budget_ms"] == 1000.0
        assert decl["stale_signal_action"] == "stale_signal_use_cache"
        assert decl["egress"]["signal_pubsub"] == "signal:*"
        assert decl["egress"]["market_state"] == "market:state:current"
        assert decl["egress"]["direction"] == "warm_to_hot_one_way"
        assert len(decl["routing_table"]) == 7

    def test_declaration_is_declaration_only(self):
        decl = render_warm_plane_declaration()
        assert decl["execution_boundary"] == "declaration_only_owner_window"
