# [A_test] module_id: SRC-TST-1094 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_health_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_health_monitor.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.health_monitor import (
    HealthDimension,
    HealthMonitor,
    HealthReport,
)


class TestHealthDimension:
    def test_default_values(self):
        hd = HealthDimension(name="test", score=80.0)
        assert hd.name == "test"
        assert hd.score == 80.0
        assert hd.weight == 1.0
        assert hd.status == "ok"

    def test_custom_values(self):
        hd = HealthDimension(name="dup_rate", score=30.0, weight=1.5, status="critical")
        assert hd.weight == 1.5
        assert hd.status == "critical"


class TestHealthReport:
    def test_default_values(self):
        hr = HealthReport(overall=75, trend="flat", grade="C")
        assert hr.overall == 75
        assert hr.trend == "flat"
        assert hr.grade == "C"
        assert hr.dimensions == []
        assert hr.hotspots == []


class TestHealthMonitor:
    def test_instantiation(self):
        hm = HealthMonitor()
        assert hm is not None

    def test_compute_all_perfect(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 100.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics)
        assert report.overall == 100
        assert report.grade == "A"
        assert report.trend == "flat"

    def test_compute_all_zero(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 0.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics)
        assert report.overall == 0
        assert report.grade == "F"

    def test_compute_partial_metrics(self):
        hm = HealthMonitor()
        metrics = {"duplication_rate": 50.0}
        report = hm.compute(metrics)
        assert 0 <= report.overall <= 100

    def test_compute_empty_metrics(self):
        hm = HealthMonitor()
        report = hm.compute({})
        assert report.overall == 100
        assert report.grade == "A"

    def test_compute_trend_up(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 80.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics, previous_overall=70)
        assert report.trend == "up"

    def test_compute_trend_down(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 50.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics, previous_overall=80)
        assert report.trend == "down"

    def test_compute_trend_flat(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 75.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics, previous_overall=76)
        assert report.trend == "flat"

    def test_compute_trend_no_previous(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 75.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics, previous_overall=None)
        assert report.trend == "flat"

    def test_compute_with_hotspots(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 80.0 for dim in hm._DIMENSIONS}
        hotspots = [{"category": "shared"}, {"category": "core"}, {"category": "tests"}]
        report = hm.compute(metrics, hotspots=hotspots)
        assert len(report.hotspots) <= 3

    def test_compute_dimensions_count(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 80.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics)
        assert len(report.dimensions) == len(hm._DIMENSIONS)

    def test_classify_dimension_excellent(self):
        assert HealthMonitor._classify_dimension(95) == "excellent"

    def test_classify_dimension_good(self):
        assert HealthMonitor._classify_dimension(75) == "good"

    def test_classify_dimension_warning(self):
        assert HealthMonitor._classify_dimension(55) == "warning"

    def test_classify_dimension_critical(self):
        assert HealthMonitor._classify_dimension(30) == "critical"

    def test_compute_grade_boundaries(self):
        assert HealthMonitor._compute_grade(90) == "A"
        assert HealthMonitor._compute_grade(89) == "B"
        assert HealthMonitor._compute_grade(80) == "B"
        assert HealthMonitor._compute_grade(79) == "C"
        assert HealthMonitor._compute_grade(70) == "C"
        assert HealthMonitor._compute_grade(69) == "D"
        assert HealthMonitor._compute_grade(59) == "F"

    def test_compute_session_summary(self):
        hm = HealthMonitor()
        metrics = {dim["name"]: 80.0 for dim in hm._DIMENSIONS}
        report = hm.compute(metrics)
        assert "Dedup Health" in report.session_summary

    def test_compute_score_clamped(self):
        hm = HealthMonitor()
        metrics = {"duplication_rate": 150.0}
        report = hm.compute(metrics)
        dim = [d for d in report.dimensions if d.name == "duplication_rate"][0]
        assert dim.score == 100.0
