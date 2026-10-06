# [A_test] module_id: MOD-LLM_SECURITY_l5_perf_guard | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §40.4
# [MODULE] tests.llm_security.test_l5_performance_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""L5 LSGPerformanceGuard 测试（蓝图 §40.4 / 09 号文 §4.3 P1-3）。

验收：延迟埋点 → check_budget 三态；人为制造延迟超预算 → 按 §40.4 降级
顺序自动降级；永不可降级项（L1A/L3B/L4/L5 成本熔断）不被降级（不变量测试）。
"""

from __future__ import annotations

import pytest

from zephyr.security.llm_defense.llm_security.layers.l5_resource_protection import (
    BudgetStatus,
    DegradationPlan,
    LSGPerformanceGuard,
)


def _feed(guard: LSGPerformanceGuard, latencies: list[float], layer: str = "l1_input") -> None:
    for v in latencies:
        guard.track_latency(layer, v)


class TestLatencyTrackingAndBudget:
    def test_insufficient_samples_stays_within_budget(self) -> None:
        guard = LSGPerformanceGuard()
        _feed(guard, [999.0, 999.0])  # 高延迟但样本不足 → 不误降
        assert guard.check_budget() is BudgetStatus.WITHIN_BUDGET

    def test_normal_latency_within_budget(self) -> None:
        guard = LSGPerformanceGuard()
        _feed(guard, [5.0] * 100)
        assert guard.check_budget() is BudgetStatus.WITHIN_BUDGET
        assert guard.stats()["p95"] == 5.0

    def test_approaching_budget(self) -> None:
        guard = LSGPerformanceGuard(p95_budget_ms=50.0, p99_budget_ms=1000.0)
        _feed(guard, [42.0] * 100)  # p95=42 ≥ 50*0.8=40，未达 50 → APPROACHING
        assert guard.check_budget() is BudgetStatus.APPROACHING

    def test_exceeded_p95_triggers(self) -> None:
        guard = LSGPerformanceGuard(p95_budget_ms=50.0)
        _feed(guard, [80.0] * 100)  # p95=80 ≥ 50 → EXCEEDED
        assert guard.check_budget() is BudgetStatus.EXCEEDED

    def test_exceeded_p99_triggers(self) -> None:
        guard = LSGPerformanceGuard(p95_budget_ms=1000.0, p99_budget_ms=100.0)
        _feed(guard, [10.0] * 98 + [150.0, 150.0])  # p99 ≥ 100 → EXCEEDED
        assert guard.check_budget() is BudgetStatus.EXCEEDED


class TestEnactDegradation:
    def test_exceeded_produces_full_ordered_plan(self) -> None:
        guard = LSGPerformanceGuard()
        plan = guard.enact_degradation(BudgetStatus.EXCEEDED)
        assert plan.alert is True
        assert plan.degraded_layers == ("L1C", "L3D", "L6", "L8", "L7"), "降级顺序必须符合蓝图 §40.4"
        modes = {s.layer: (s.from_mode, s.to_mode) for s in plan.steps}
        assert modes["L1C"] == ("越狱LLM辅助检测", "纯pattern match")
        assert modes["L3D"] == ("幻觉LLM辅助检测", "纯启发式")
        assert modes["L6"] == ("详细审计日志", "摘要日志")
        assert modes["L8"] == ("Agent间行为分析", "纯身份验证")
        assert modes["L7"] == ("实时验证", "定期批量验证")

    def test_approaching_alerts_without_steps(self) -> None:
        guard = LSGPerformanceGuard()
        plan = guard.enact_degradation(BudgetStatus.APPROACHING)
        assert plan.alert is True
        assert plan.steps == ()

    def test_within_budget_noop(self) -> None:
        guard = LSGPerformanceGuard()
        plan = guard.enact_degradation(BudgetStatus.WITHIN_BUDGET)
        assert plan.alert is False
        assert plan.steps == ()

    def test_end_to_end_overbudget_latency_produces_plan(self) -> None:
        """人为制造延迟超预算 → check_budget=EXCEEDED → 计划按序产出。"""
        guard = LSGPerformanceGuard(p95_budget_ms=50.0)
        _feed(guard, [200.0] * 50, layer="l1_input")
        status = guard.check_budget()
        assert status is BudgetStatus.EXCEEDED
        plan = guard.enact_degradation(status)
        assert plan.degraded_layers[:2] == ("L1C", "L3D")


class TestNeverDegradableInvariant:
    """不变量：L1A/L3B/L4/L5 成本熔断永不可降级。"""

    @pytest.mark.parametrize("status", list(BudgetStatus))
    def test_never_degradable_layers_absent_from_any_plan(self, status: BudgetStatus) -> None:
        guard = LSGPerformanceGuard()
        plan = guard.enact_degradation(status)
        assert not (set(plan.degraded_layers) & LSGPerformanceGuard.NEVER_DEGRADABLE)

    @pytest.mark.parametrize("layer", ["L1A", "L3B", "L4", "L5_COST_BREAKER"])
    def test_is_degradable_false_for_protected_layers(self, layer: str) -> None:
        assert LSGPerformanceGuard.is_degradable(layer) is False

    @pytest.mark.parametrize("layer", ["L1C", "L3D", "L6", "L7", "L8"])
    def test_is_degradable_true_for_listed_layers(self, layer: str) -> None:
        assert LSGPerformanceGuard.is_degradable(layer) is True

    def test_degradation_order_contains_no_protected_layer(self) -> None:
        for layer, _from, _to in LSGPerformanceGuard.DEGRADATION_ORDER:
            assert layer not in LSGPerformanceGuard.NEVER_DEGRADABLE

    def test_tampered_degradation_order_rejected_at_construction(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """故障注入：若降级清单被篡改含永不可降级层，构造期必须拒绝。"""
        tampered = (("L3B", "沙箱执行", "无沙箱"),)
        monkeypatch.setattr(LSGPerformanceGuard, "DEGRADATION_ORDER", tampered)
        with pytest.raises(ValueError, match="永不可降级"):
            LSGPerformanceGuard()
