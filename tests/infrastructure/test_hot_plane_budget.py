# [BLUEPRINT] MOD-INF-065 | docs/03_modules/_domain_infrastructure_runtime/hot_plane/blueprint.md | §test
# [MODULE] tests.infrastructure.test_hot_plane_budget
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.hot_plane_budget
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_hot_plane_budget.py
# [A_test] module_id: MOD-INF-065 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-INF-065 单元测试: Hot 平面（<10ms）时延预算与资源独占声明。

覆盖: 2/3/5ms 预算分解与累计 2/5/10ms 真源值、资源独占声明（核 8-11/P3 禁磁盘 IO/
miniQMT 连接独占/Redis 本地读路径）、check_budget 逐阶段与端到端判定、超限熔断
告警动作声明、畸形输入 Fail-Closed、核规格与 MOD-INF-064 对齐。
"""

from __future__ import annotations

import pytest

from zephyr.infrastructure.hot_plane_budget import (
    HOT_PLANE_BUDGET,
    HotPlaneBudgetError,
    check_budget,
    render_hot_plane_declaration,
)


class TestBudgetBreakdown:
    def test_stage_budgets_2_3_5(self):
        budgets = {stage.name: stage.budget_ms for stage in HOT_PLANE_BUDGET.stages}
        assert budgets["tick_to_risk"] == 2.0
        assert budgets["risk_eval"] == 3.0
        assert budgets["order_build_submit"] == 5.0

    def test_cumulative_budgets(self):
        cumulative = [stage.cumulative_budget_ms for stage in HOT_PLANE_BUDGET.stages]
        assert cumulative == [2.0, 5.0, 10.0]

    def test_total_budget_10ms(self):
        assert HOT_PLANE_BUDGET.total_budget_ms == 10.0


class TestResourceExclusivity:
    def test_resource_declarations(self):
        res = HOT_PLANE_BUDGET.resources
        assert res.p3_cpu_cores_exclusive == (8, 9, 10, 11)
        assert res.p3_disk_io_forbidden_except_logs is True
        assert res.miniqmt_connection_exclusive is True
        assert res.redis_local_read_path is True

    def test_cores_aligned_with_mod_inf_064(self):
        from zephyr.trading.trading_core_process_spec import TRADING_CORE_SPEC

        assert HOT_PLANE_BUDGET.resources.p3_cpu_cores_exclusive == TRADING_CORE_SPEC.cpu_cores


class TestCheckBudget:
    def test_within_budget(self):
        verdict = check_budget({"tick_to_risk": 1.0, "risk_eval": 3.0, "order_build_submit": 5.0})
        assert verdict.within_budget is True
        assert verdict.breached_stages == ()
        assert verdict.action == "none"
        assert verdict.total_ms == 9.0

    def test_exactly_at_budget_is_within(self):
        verdict = check_budget({"tick_to_risk": 2.0, "risk_eval": 3.0, "order_build_submit": 5.0})
        assert verdict.within_budget is True
        assert verdict.total_ms == 10.0

    def test_stage_breach_triggers_circuit_alert(self):
        verdict = check_budget({"tick_to_risk": 3.0, "risk_eval": 3.0, "order_build_submit": 5.0})
        assert verdict.within_budget is False
        assert verdict.breached_stages == ("tick_to_risk",)
        assert verdict.action == "circuit_alert"

    def test_total_breach_without_stage_breach_impossible_shape(self):
        # 每段恰好达标=总和 10ms 达标；总和超限必伴随至少一段超限（Fail-Closed 判定不缺项）
        verdict = check_budget({"tick_to_risk": 2.5, "risk_eval": 2.5, "order_build_submit": 5.5})
        assert verdict.within_budget is False
        assert set(verdict.breached_stages) == {"tick_to_risk", "order_build_submit"}
        assert verdict.total_ms == 10.5

    def test_unknown_stage_fail_closed(self):
        with pytest.raises(HotPlaneBudgetError):
            check_budget({"bogus_stage": 1.0})

    def test_missing_stage_fail_closed(self):
        with pytest.raises(HotPlaneBudgetError):
            check_budget({"tick_to_risk": 1.0, "risk_eval": 1.0})

    def test_negative_latency_fail_closed(self):
        with pytest.raises(HotPlaneBudgetError):
            check_budget({"tick_to_risk": -1.0, "risk_eval": 1.0, "order_build_submit": 1.0})


class TestConfigReadyDeclaration:
    def test_declaration_shape_and_owner_boundary(self):
        decl = render_hot_plane_declaration()
        assert decl["total_budget_ms"] == 10.0
        assert [s["budget_ms"] for s in decl["stages"]] == [2.0, 3.0, 5.0]
        assert decl["resources"]["p3_cpu_cores_exclusive"] == [8, 9, 10, 11]
        assert decl["resources"]["p3_disk_io_forbidden_except_logs"] is True
        assert decl["applied_by_ai"] is False
        assert "Owner" in decl["apply_boundary"]
