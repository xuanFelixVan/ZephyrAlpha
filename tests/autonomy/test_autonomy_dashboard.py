# [A_test] module_id: MOD-GOV_autonomy_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_autonomy_dashboard
# [INVARIANTS] dashboard data isolated via tmp_path
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.governance.intelligence_governance.autonomy_dashboard import (
    EXIT_AUTONOMY_DOWNGRADED,
    AutonomyDashboard,
    AutonomyMetrics,
    DowngradeEvent,
    HealthGauge,
)


class TestAutonomyMetrics:
    def test_instantiation_defaults(self):
        m = AutonomyMetrics()
        assert m.total_rollbacks == 0
        assert m.successful_rollbacks == 0
        assert m.failed_rollbacks == 0

    def test_success_rate_no_rollbacks(self):
        m = AutonomyMetrics()
        assert m.success_rate == 1.0

    def test_success_rate_with_rollbacks(self):
        m = AutonomyMetrics(total_rollbacks=10, successful_rollbacks=8)
        assert m.success_rate == 0.8

    def test_intervention_rate_no_rollbacks(self):
        m = AutonomyMetrics()
        assert m.intervention_rate == 0.0

    def test_intervention_rate_with_data(self):
        m = AutonomyMetrics(total_rollbacks=10, human_interventions=3)
        assert m.intervention_rate == 0.3

    def test_false_positive_rate_no_rollbacks(self):
        m = AutonomyMetrics()
        assert m.false_positive_rate == 0.0

    def test_false_positive_rate_with_data(self):
        m = AutonomyMetrics(total_rollbacks=5, false_positives=1)
        assert m.false_positive_rate == 0.2

    def test_avg_rto_no_samples(self):
        m = AutonomyMetrics()
        assert m.avg_rto_ms == 0.0

    def test_avg_rto_with_samples(self):
        m = AutonomyMetrics(total_time_to_restore_ms=5000, samples_since_reset=5)
        assert m.avg_rto_ms == 1000.0


class TestHealthGauge:
    def test_instantiation(self):
        hg = HealthGauge(score=0.75)
        assert hg.score == 0.75
        assert hg.tier == 2

    def test_from_metrics_perfect(self):
        m = AutonomyMetrics(total_rollbacks=10, successful_rollbacks=10)
        hg = HealthGauge.from_metrics(m)
        assert hg.score > 0.8
        assert hg.tier == 2

    def test_from_metrics_poor(self):
        m = AutonomyMetrics(
            total_rollbacks=10,
            successful_rollbacks=1,
            human_interventions=9,
            false_positives=8,
        )
        hg = HealthGauge.from_metrics(m)
        assert hg.score < 0.5
        assert hg.tier == 0

    def test_from_metrics_medium(self):
        m = AutonomyMetrics(
            total_rollbacks=10,
            successful_rollbacks=6,
            human_interventions=2,
            false_positives=1,
        )
        hg = HealthGauge.from_metrics(m)
        assert 0.5 <= hg.score <= 0.8
        assert hg.tier == 1

    def test_from_metrics_zero_rollbacks(self):
        m = AutonomyMetrics()
        hg = HealthGauge.from_metrics(m)
        assert abs(hg.score - 1.0) < 1e-9
        assert hg.tier == 2

    def test_score_clamped_to_one(self):
        hg = HealthGauge(score=1.5)
        assert hg.score == 1.5
        result = HealthGauge.from_metrics(AutonomyMetrics())
        assert result.score <= 1.0


class TestDowngradeEvent:
    def test_instantiation(self):
        de = DowngradeEvent(
            timestamp_utc="2026-01-01T00:00:00+00:00",
            from_tier=2,
            to_tier=0,
            health_score=0.2,
            reason="Health < 0.3 for 300s",
        )
        assert de.from_tier == 2
        assert de.to_tier == 0
        assert de.health_score == 0.2


class TestAutonomyDashboardInstantiation:
    def test_with_data_dir(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        assert dash.data_dir == tmp_path

    def test_default_data_dir(self):
        dash = AutonomyDashboard()
        assert dash.data_dir == Path("data/rollback/autonomy")


class TestRecordRollback:
    def test_record_successful_rollback(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        metrics = dash.record_rollback(success=True, token_cost=100, rto_ms=500)
        assert metrics.total_rollbacks == 1
        assert metrics.successful_rollbacks == 1
        assert metrics.failed_rollbacks == 0
        assert metrics.total_token_cost == 100
        assert metrics.total_time_to_restore_ms == 500

    def test_record_failed_rollback(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        metrics = dash.record_rollback(success=False)
        assert metrics.total_rollbacks == 1
        assert metrics.failed_rollbacks == 1
        assert metrics.successful_rollbacks == 0

    def test_multiple_rollbacks_accumulate(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True, token_cost=50)
        dash.record_rollback(success=False, token_cost=30)
        metrics = dash.record_rollback(success=True, token_cost=20)
        assert metrics.total_rollbacks == 3
        assert metrics.successful_rollbacks == 2
        assert metrics.failed_rollbacks == 1
        assert metrics.total_token_cost == 100

    def test_persists_to_file(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        metrics_path = tmp_path / "autonomy_metrics.json"
        assert metrics_path.exists()
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        assert data["total_rollbacks"] == 1


class TestRecordIntervention:
    def test_record_intervention(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        metrics = dash.record_intervention(reason="manual override")
        assert metrics.human_interventions == 1

    def test_interventions_accumulate(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        dash.record_intervention()
        metrics = dash.record_intervention()
        assert metrics.human_interventions == 2


class TestRecordFalsePositive:
    def test_record_false_positive(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        metrics = dash.record_false_positive()
        assert metrics.false_positives == 1

    def test_false_positives_accumulate(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        dash.record_false_positive()
        metrics = dash.record_false_positive()
        assert metrics.false_positives == 2


class TestEvaluateHealth:
    def test_evaluate_health_good(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        for _ in range(10):
            dash.record_rollback(success=True)
        gauge = dash.evaluate_health()
        assert gauge.score > 0.5
        assert gauge.tier >= 1

    def test_evaluate_health_poor(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        for _ in range(10):
            dash.record_rollback(success=False)
        for _ in range(8):
            dash.record_intervention()
        gauge = dash.evaluate_health()
        assert gauge.score < 0.8

    def test_evaluate_health_empty(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        gauge = dash.evaluate_health()
        assert abs(gauge.score - 1.0) < 1e-9
        assert gauge.tier == 2


class TestGetDashboardReport:
    def test_report_structure(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        report = dash.get_dashboard_report()
        assert "timestamp_utc" in report
        assert "health_score" in report
        assert "autonomy_tier" in report
        assert "tier_description" in report
        assert "metrics" in report
        assert "downgrade_events_recent" in report
        assert "exit_code" in report

    def test_report_metrics_content(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True, token_cost=500, rto_ms=1000)
        report = dash.get_dashboard_report()
        m = report["metrics"]
        assert m["total_rollbacks"] == 1
        assert m["total_token_cost"] == 500
        assert m["avg_rto_ms"] == 1000.0

    def test_report_exit_code_healthy(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        report = dash.get_dashboard_report()
        assert report["exit_code"] == 0

    def test_report_exit_code_degraded(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        for _ in range(10):
            dash.record_rollback(success=False)
        for _ in range(9):
            dash.record_intervention()
        for _ in range(8):
            dash.record_false_positive()
        report = dash.get_dashboard_report()
        if report["autonomy_tier"] == 0:
            assert report["exit_code"] == EXIT_AUTONOMY_DOWNGRADED


class TestRenderDashboardMarkdown:
    def test_render_contains_header(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        md = dash.render_dashboard_markdown()
        assert "# Autonomy Dashboard" in md

    def test_render_contains_tier_map(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        md = dash.render_dashboard_markdown()
        assert "Tier Map" in md
        assert "Auto-revert" in md

    def test_render_contains_metrics(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        md = dash.render_dashboard_markdown()
        assert "Total Rollbacks" in md
        assert "Success Rate" in md


class TestResetMetrics:
    def test_reset_clears_all(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True, token_cost=500)
        dash.record_intervention()
        dash.reset_metrics()
        gauge = dash.evaluate_health()
        assert abs(gauge.score - 1.0) < 1e-9
        report = dash.get_dashboard_report()
        assert report["metrics"]["total_rollbacks"] == 0

    def test_reset_persists(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        dash.reset_metrics()
        dash2 = AutonomyDashboard(data_dir=tmp_path)
        report = dash2.get_dashboard_report()
        assert report["metrics"]["total_rollbacks"] == 0


class TestCorruptedMetricsFile:
    def test_load_with_corrupted_json(self, tmp_path):
        dash = AutonomyDashboard(data_dir=tmp_path)
        dash.record_rollback(success=True)
        metrics_path = tmp_path / "autonomy_metrics.json"
        metrics_path.write_text("{invalid json", encoding="utf-8")
        dash2 = AutonomyDashboard(data_dir=tmp_path)
        metrics = dash2.load_metrics()
        assert metrics.total_rollbacks == 0
