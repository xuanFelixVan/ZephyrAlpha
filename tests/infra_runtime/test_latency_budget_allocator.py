# [BLUEPRINT] MOD-INF-080 | docs/03_modules/_domain_infrastructure_runtime/latency_budget_allocator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-080 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_latency_budget_allocator
# [TESTS] src/zephyr/infra_runtime/latency_budget_allocator.py
"""MOD-INF-080 单元测试：latency_budget_allocator 延迟预算分配器。

蓝图验收（B14-04701/CAND-H1FS-013，A9 运维架构 §8.3.10）：
Hot<10ms/Warm<1s 端到端预算常量 + 阶段预算分解登记（总和校验超预算拒绝，
预算表版本递增）+ 实际耗时上报 + 超预算阶段判定+告警回调 + 预算消耗率报表。
时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.latency_budget_allocator",
    reason="latency_budget_allocator not importable",
)

from zephyr.infra_runtime.latency_budget_allocator import (  # noqa: E402
    PLANE_BUDGET_MS,
    BudgetViolation,
    LatencyBudgetAllocator,
    LatencyBudgetError,
    Plane,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _alloc(alerts: list | None = None) -> LatencyBudgetAllocator:
    return LatencyBudgetAllocator(
        clock=lambda: _T0,
        alert_sink=(lambda v: alerts.append(v)) if alerts is not None else None,
    )


_HOT_STAGES = {"tick_ingest": 2.0, "signal": 5.0, "order_route": 3.0}


# ──────────────────────────────────────────────────────────────────────────────
# 预算分解登记（总和校验 + 版本化）
# ──────────────────────────────────────────────────────────────────────────────


class TestAllocate:
    def test_plane_budget_constants(self) -> None:
        assert PLANE_BUDGET_MS[Plane.HOT] == 10.0
        assert PLANE_BUDGET_MS[Plane.WARM] == 1000.0

    def test_allocate_ok_returns_version_1(self) -> None:
        alloc = _alloc()
        assert alloc.allocate(Plane.HOT, dict(_HOT_STAGES)) == 1
        table = alloc.table(Plane.HOT)
        assert table.version == 1
        assert [s.stage for s in table.stages] == ["order_route", "signal", "tick_ingest"]

    def test_allocate_exact_cap_boundary_ok(self) -> None:
        assert _alloc().allocate(Plane.HOT, {"only": 10.0}) == 1

    def test_allocate_over_budget_rejected(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate(Plane.HOT, {"a": 6.0, "b": 5.0})  # 11 > 10

    def test_allocate_empty_stages_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate(Plane.WARM, {})

    def test_allocate_empty_stage_name_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate(Plane.HOT, {"": 1.0})

    def test_allocate_non_positive_budget_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate(Plane.HOT, {"a": 0.0})
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate(Plane.HOT, {"a": -1.0})

    def test_allocate_invalid_plane_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().allocate("hot", dict(_HOT_STAGES))  # type: ignore[arg-type]

    def test_reallocate_increments_version(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        assert alloc.allocate(Plane.HOT, {"signal": 8.0}) == 2
        assert alloc.table(Plane.HOT).version == 2

    def test_table_unknown_plane_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().table(Plane.WARM)


# ──────────────────────────────────────────────────────────────────────────────
# 实际耗时上报（超预算判定 + 告警）
# ──────────────────────────────────────────────────────────────────────────────


class TestRecord:
    def test_record_within_budget_no_alert(self) -> None:
        alerts: list[BudgetViolation] = []
        alloc = _alloc(alerts)
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        assert alloc.record(Plane.HOT, "signal", 4.5) is False
        assert alerts == []

    def test_record_over_budget_alerts(self) -> None:
        alerts: list[BudgetViolation] = []
        alloc = _alloc(alerts)
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        assert alloc.record(Plane.HOT, "signal", 7.5) is True
        assert len(alerts) == 1
        assert alerts[0].stage == "signal"
        assert alerts[0].budget_ms == 5.0
        assert alerts[0].actual_ms == 7.5

    def test_record_exact_budget_boundary_not_over(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        assert alloc.record(Plane.HOT, "signal", 5.0) is False

    def test_record_unknown_plane_raises(self) -> None:
        with pytest.raises(LatencyBudgetError):
            _alloc().record(Plane.HOT, "signal", 1.0)

    def test_record_unknown_stage_raises(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        with pytest.raises(LatencyBudgetError):
            alloc.record(Plane.HOT, "ghost", 1.0)

    def test_record_negative_actual_raises(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        with pytest.raises(LatencyBudgetError):
            alloc.record(Plane.HOT, "signal", -0.1)

    def test_record_stale_stage_after_reallocate_raises(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        alloc.allocate(Plane.HOT, {"signal": 8.0})  # 新表仅 signal
        with pytest.raises(LatencyBudgetError):
            alloc.record(Plane.HOT, "tick_ingest", 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# 预算消耗率报表（确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestReport:
    def test_report_structure_and_ratios(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        alloc.record(Plane.HOT, "signal", 4.0)
        alloc.record(Plane.HOT, "signal", 6.0)  # 1 次超支
        rep = alloc.report()
        hot = rep["hot"]
        assert hot["version"] == 1
        assert hot["plane_budget_ms"] == 10.0
        assert hot["allocated_ms"] == 10.0
        sig = hot["stages"]["signal"]
        assert sig["count"] == 2
        assert sig["avg_actual_ms"] == 5.0
        assert sig["max_actual_ms"] == 6.0
        assert sig["consumption_ratio"] == 1.0
        assert sig["over_count"] == 1
        idle = hot["stages"]["tick_ingest"]
        assert idle["count"] == 0
        assert idle["consumption_ratio"] == 0.0

    def test_report_multi_plane_sorted(self) -> None:
        alloc = _alloc()
        alloc.allocate(Plane.WARM, {"batch": 900.0})
        alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
        assert list(alloc.report()) == ["hot", "warm"]

    def test_report_empty_allocator(self) -> None:
        assert _alloc().report() == {}

    def test_report_deterministic_replay(self) -> None:
        def build() -> dict:
            alloc = _alloc()
            alloc.allocate(Plane.HOT, dict(_HOT_STAGES))
            alloc.record(Plane.HOT, "signal", 3.0)
            alloc.record(Plane.HOT, "order_route", 3.0)
            return alloc.report()

        assert build() == build()  # 同输入必同输出
