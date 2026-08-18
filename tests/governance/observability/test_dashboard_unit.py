# [A_test] module_id: MOD-GOV_dashboard_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-622 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_dashboard
# [DOMAIN] D_FRONTEND
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-622 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for Streamlit Dashboard components (T-4-07)
=======================================================
覆盖：5 个组件的数据获取与渲染逻辑。

最少测试：5 条（组件级）。
"""


import pytest

# 治本：zephyr.ops 已迁移到 zephyr.feedback_loop（ARCH-032，ops/ 74 文件迁移到 trading/feedback_loop/）。
from zephyr.feedback_loop.fitness_functions import FitnessInputs
from zephyr.frontend.dashboard.app import create_app
from zephyr.frontend.dashboard.components.fitness_functions import (
    FitnessDashboardData,
    fetch_fitness_data,
    render_fitness_dashboard,
)
from zephyr.frontend.dashboard.components.gate_statistics import (
    GateStat,
    GateStatisticsData,
    fetch_gate_statistics,
    render_gate_statistics,
)
from zephyr.frontend.dashboard.components.knowledge_overview import (
    KnowledgeOverviewData,
    fetch_knowledge_overview,
    render_knowledge_overview,
)
from zephyr.frontend.dashboard.components.olap_trend import (
    OLAPTrendData,
    fetch_olap_trends,
    render_olap_trends,
)
from zephyr.frontend.dashboard.components.task_progress import (
    PhaseProgress,
    TaskProgressData,
    fetch_task_progress,
    render_task_progress,
)


class TestTaskProgressComponent:
    def test_phase_progress_completion_rate(self) -> None:
        pp = PhaseProgress(phase=0, total_tasks=10, completed_tasks=7)
        assert pp.completion_rate == pytest.approx(0.7)

    def test_phase_progress_zero_tasks(self) -> None:
        pp = PhaseProgress(phase=1)
        assert pp.completion_rate == 0.0

    def test_fetch_without_repo(self) -> None:
        data = fetch_task_progress(task_repo=None)
        assert data.total_tasks == 0
        assert len(data.phases) == 5

    def test_render_task_progress(self) -> None:
        data = TaskProgressData(
            phases=[PhaseProgress(phase=0, total_tasks=5, completed_tasks=3)],
            total_tasks=5,
            total_completed=3,
        )
        rendered = render_task_progress(data)
        assert rendered["overall_rate"] == pytest.approx(0.6)
        assert len(rendered["phases"]) == 1


class TestKnowledgeOverviewComponent:
    def test_fetch_without_repo(self) -> None:
        data = fetch_knowledge_overview()
        assert data.total_entries == 0
        assert data.activation_rate == 0.0

    def test_render_knowledge_overview(self) -> None:
        data = KnowledgeOverviewData(
            total_entries=50,
            activated_entries=20,
            activation_rate=0.4,
        )
        rendered = render_knowledge_overview(data)
        assert rendered["total_entries"] == 50
        assert rendered["activation_rate"] == pytest.approx(0.4)


class TestGateStatisticsComponent:
    def test_gate_stat_rates(self) -> None:
        gs = GateStat(gate_id="G1", total_runs=100, passed_runs=90, failed_runs=10)
        assert gs.pass_rate == pytest.approx(0.9)
        assert gs.block_rate == pytest.approx(0.1)

    def test_fetch_without_engine(self) -> None:
        data = fetch_gate_statistics(olap_engine=None)
        assert data.total_runs == 0

    def test_render_gate_statistics(self) -> None:
        data = GateStatisticsData(
            total_runs=100,
            total_passed=95,
            total_failed=5,
            overall_pass_rate=0.95,
            overall_block_rate=0.05,
        )
        rendered = render_gate_statistics(data)
        assert rendered["overall_pass_rate"] == pytest.approx(0.95)


class TestFitnessFunctionsComponent:
    def test_fetch_fitness_data(self) -> None:
        inputs = FitnessInputs(
            coverage_pct=72.0,
            gate_total=100,
            gate_passed=95,
            ke_total=50,
            ke_activated=20,
            hallucination_total=30,
            hallucination_intercepted=25,
        )
        data = fetch_fitness_data(inputs=inputs)
        assert data.overall_status in ("PASS", "WARN", "FAIL")
        assert len(data.metrics) == 5

    def test_render_fitness_dashboard(self) -> None:
        data = FitnessDashboardData(
            overall_status="PASS",
            metrics=[{"metric_name": "test_coverage", "value": 72.0, "status": "PASS"}],
        )
        rendered = render_fitness_dashboard(data)
        assert rendered["overall_status"] == "PASS"
        assert len(rendered["metrics"]) == 1


class TestOLAPTrendComponent:
    def test_fetch_without_engine(self) -> None:
        data = fetch_olap_trends(olap_engine=None)
        assert data.task_progress == []
        assert data.compliance_rate == []

    def test_render_olap_trends(self) -> None:
        data = OLAPTrendData(
            task_progress=[{"period": "2026-04-24", "total": 10}],
            compliance_rate=[],
            knowledge_activation=[],
        )
        rendered = render_olap_trends(data)
        assert len(rendered["task_progress"]) == 1


class TestDashboardApp:
    def test_create_app(self) -> None:
        app = create_app()
        assert app is not None

    def test_render_page_task_progress(self) -> None:
        app = create_app()
        result = app.render_page("task_progress")
        assert "overall_rate" in result

    def test_render_page_knowledge_overview(self) -> None:
        app = create_app()
        result = app.render_page("knowledge_overview")
        assert "total_entries" in result

    def test_render_page_gate_statistics(self) -> None:
        app = create_app()
        result = app.render_page("gate_statistics")
        assert "overall_pass_rate" in result

    def test_render_page_fitness_functions(self) -> None:
        app = create_app()
        result = app.render_page("fitness_functions")
        assert "overall_status" in result

    def test_render_page_olap_trend(self) -> None:
        app = create_app()
        result = app.render_page("olap_trend")
        assert "task_progress" in result

    def test_render_page_unknown(self) -> None:
        app = create_app()
        result = app.render_page("unknown")
        assert "error" in result
