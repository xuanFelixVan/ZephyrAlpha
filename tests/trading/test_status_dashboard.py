# [A_test] module_id: MOD-GOV_status_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
from __future__ import annotations

# [A_test] module_id=MOD-GOV_status_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_status_dashboard
# [INVARIANTS] StatusDashboard依赖多个runtime组件;测试使用mock
# [MODIFY-GUARD] src/zephyr/runtime/status_dashboard.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] render_tui返回str;render_json返回dict
# [TESTS] tests/test_status_dashboard.py
# [TTL] task_bound
from unittest.mock import MagicMock

from zephyr.trading.health_monitor import PressureLevel
from zephyr.trading.status_dashboard import StatusDashboard


def _make_registry(card_count: int = 3):
    registry = MagicMock()
    registry.list_all.return_value = [MagicMock() for _ in range(card_count)]
    return registry


def _make_health_monitor(level: PressureLevel = PressureLevel.NORMAL):
    hm = MagicMock()
    hm.pressure_level.return_value = level
    return hm


def _make_night_shift_queue(pending: int = 0, resolved: int = 0):
    nq = MagicMock()
    nq.stats.return_value = {"total": pending + resolved, "pending": pending, "resolved": resolved}
    return nq


def _make_work_orchestrator(dag_count: int = 0, pending: dict | None = None, running: dict | None = None):
    wo = MagicMock()
    wo.list_dags.return_value = [MagicMock() for _ in range(dag_count)]
    wo.pending_count.return_value = pending or {"trae": 0, "local": 0, "api": 0}
    wo.running_count.return_value = running or {"trae": 0, "local": 0, "api": 0}
    return wo


class TestStatusDashboardInit:
    def test_creation_with_all_deps(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        assert dash.registry is not None
        assert dash.uptime_start != ""

    def test_creation_with_custom_uptime(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
            uptime_start="2026-01-01T00:00:00",
        )
        assert dash.uptime_start == "2026-01-01T00:00:00"

    def test_creation_with_orphan_detector(self):
        od = MagicMock()
        od.compute_orphan_rate.return_value = 0.25
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
            orphan_detector=od,
        )
        assert dash.orphan is od


class TestRenderTui:
    def test_render_contains_header(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        output = dash.render_tui()
        assert "ZephyrAlpha AutoRuntime Core" in output
        assert "Phase:" in output
        assert "Pressure:" in output

    def test_render_shows_night_shift_stats(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(pending=2, resolved=5),
            work_orchestrator=_make_work_orchestrator(),
        )
        output = dash.render_tui()
        assert "2 pending" in output
        assert "5 resolved" in output

    def test_render_shows_orphan_rate_with_detector(self):
        od = MagicMock()
        od.compute_orphan_rate.return_value = 0.15
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
            orphan_detector=od,
        )
        output = dash.render_tui()
        assert "15.0%" in output

    def test_render_without_orphan_detector(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        output = dash.render_tui()
        assert "0.0%" in output


class TestRenderJson:
    def test_render_json_keys(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        data = dash.render_json()
        assert "phase" in data
        assert "pressure" in data
        assert "orphan_rate" in data
        assert "capabilities" in data
        assert "night_shift" in data
        assert "work_dags" in data
        assert "pending" in data
        assert "running" in data
        assert "uptime_start" in data

    def test_render_json_values(self):
        od = MagicMock()
        od.compute_orphan_rate.return_value = 0.3
        dash = StatusDashboard(
            registry=_make_registry(card_count=5),
            health_monitor=_make_health_monitor(level=PressureLevel.ELEVATED),
            night_shift_queue=_make_night_shift_queue(pending=1, resolved=3),
            work_orchestrator=_make_work_orchestrator(dag_count=2),
            orphan_detector=od,
        )
        data = dash.render_json(detail=True)  # ELEVATED 默认降采样，显式 detail=True 验证全量字段值
        assert data["phase"] in ("MORNING", "DAY", "EVENING", "NIGHT")
        assert data["pressure"] == "ELEVATED"
        assert data["orphan_rate"] == 0.3
        assert data["capabilities"] == 5
        assert data["night_shift"]["pending"] == 1
        assert data["night_shift"]["resolved"] == 3
        assert data["work_dags"] == 2

    def test_render_json_without_orphan_detector(self):
        dash = StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        data = dash.render_json()
        assert data["orphan_rate"] == 0.0


class TestDegradedDownsampling:
    """降级降采样（蓝图 §3.3 Lv1 动作「StatusDashboard 降采样」）。"""

    def _dash(self, level: PressureLevel):
        return StatusDashboard(
            registry=_make_registry(),
            health_monitor=_make_health_monitor(level=level),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )

    def test_normal_pressure_full_detail_unchanged(self):
        data = self._dash(PressureLevel.NORMAL).render_json()
        assert "orphan_rate" in data
        assert "night_shift" in data
        assert "pending" in data
        assert "running" in data
        assert "degraded" not in data

    def test_elevated_pressure_downsamples(self):
        data = self._dash(PressureLevel.ELEVATED).render_json()
        assert data["degraded"] is True
        assert "orphan_rate" not in data
        assert "night_shift" not in data
        assert "pending" not in data
        assert "running" not in data
        assert data["sampling_interval_s"] == 15.0
        assert "phase" in data
        assert "capabilities" in data
        assert "uptime_start" in data

    def test_critical_pressure_downsamples(self):
        data = self._dash(PressureLevel.CRITICAL).render_json()
        assert data["degraded"] is True
        assert data["sampling_interval_s"] == 60.0

    def test_explicit_detail_overrides_pressure(self):
        data = self._dash(PressureLevel.HIGH).render_json(detail=True)
        assert "orphan_rate" in data
        assert "degraded" not in data

    def test_sampling_interval_escalates_with_pressure(self):
        dash = self._dash(PressureLevel.NORMAL)
        assert dash.sampling_interval_seconds(PressureLevel.NORMAL) == 5.0
        assert dash.sampling_interval_seconds(PressureLevel.ELEVATED) == 15.0
        assert dash.sampling_interval_seconds(PressureLevel.HIGH) == 30.0
        assert dash.sampling_interval_seconds(PressureLevel.CRITICAL) == 60.0


class TestAggregateView:
    """聚合视图 + 下钻（蓝图 §16.3 步骤 1）。"""

    def test_aggregate_view_structure(self):
        dash = StatusDashboard(
            registry=_make_registry(card_count=3),
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(dag_count=2),
        )
        view = dash.aggregate_view()
        assert "summary" in view
        assert "drilldown" in view
        assert view["summary"]["capabilities"] == 3
        assert view["summary"]["work_dags"] == 2
        assert "capabilities_by_status" in view["drilldown"]
        assert "capabilities_by_category" in view["drilldown"]
        assert len(view["drilldown"]["dags"]) == 2

    def test_aggregate_view_status_grouping(self):
        card_a = MagicMock(status="ACTIVE", category="infra")
        card_b = MagicMock(status="ACTIVE", category="infra")
        card_c = MagicMock(status="INACTIVE", category="search")
        registry = MagicMock()
        registry.list_all.return_value = [card_a, card_b, card_c]
        dash = StatusDashboard(
            registry=registry,
            health_monitor=_make_health_monitor(),
            night_shift_queue=_make_night_shift_queue(),
            work_orchestrator=_make_work_orchestrator(),
        )
        view = dash.aggregate_view()
        assert view["drilldown"]["capabilities_by_status"] == {"ACTIVE": 2, "INACTIVE": 1}
        assert view["drilldown"]["capabilities_by_category"] == {"infra": 2, "search": 1}
