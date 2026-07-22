# [A_test] module_id: MOD-GOV_health_aggregator_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_health_aggregator
# [INVARIANTS] 12-system probe contract; snapshot capped at MAX_SNAPSHOTS
# [MODIFY-GUARD] health_aggregator.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError→fail; RuntimeError→fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

ha = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.health_aggregator",
    reason="health_aggregator import failed",
)


class TestSystemHealthSnapshot:
    def test_creation(self):
        s = ha.SystemHealthSnapshot(system="orchestrator")
        assert s.system == "orchestrator"
        assert s.liveness == "alive"
        assert s.readiness == "ready"
        assert s.degraded is False

    def test_degraded_snapshot(self):
        s = ha.SystemHealthSnapshot(system="database", liveness="alive", readiness="ready", degraded=True)
        assert s.degraded is True


class TestAnnualHealthReport:
    def test_creation(self):
        r = ha.AnnualHealthReport(year=2026)
        assert r.year == 2026
        assert isinstance(r.uptime_ratio, dict)
        assert isinstance(r.mttr_s, dict)

    def test_with_data(self):
        r = ha.AnnualHealthReport(
            year=2026,
            uptime_ratio={"orchestrator": 0.999},
            mttr_s={"orchestrator": 30.0},
            degradation_ratio={"orchestrator": 0.01},
        )
        assert r.uptime_ratio["orchestrator"] == 0.999


class TestHealthAggregator:
    def test_instantiation(self):
        agg = ha.HealthAggregator()
        assert agg is not None

    def test_poll_all(self):
        agg = ha.HealthAggregator()
        results = agg.poll_all()
        assert isinstance(results, list)
        assert len(results) > 0
        for snap in results:
            assert isinstance(snap, ha.SystemHealthSnapshot)
            assert snap.system != ""

    def test_poll_all_populates_snapshots(self):
        agg = ha.HealthAggregator()
        agg.poll_all()
        assert len(agg._snapshots) > 0

    def test_latest_snapshots_empty(self):
        agg = ha.HealthAggregator()
        result = agg.latest_snapshots()
        assert result == []

    def test_latest_snapshots_after_poll(self):
        agg = ha.HealthAggregator()
        agg.poll_all()
        latest = agg.latest_snapshots()
        assert len(latest) > 0

    def test_annual_report(self):
        agg = ha.HealthAggregator()
        report = agg.annual_report(
            year=2026,
            uptimes={"orchestrator": 0.999},
            mttr={"orchestrator": 30.0},
            degradations={"orchestrator": 0.01},
        )
        assert isinstance(report, ha.AnnualHealthReport)
        assert report.year == 2026

    def test_snapshot_cap(self):
        agg = ha.HealthAggregator()
        for _ in range(100):
            agg.poll_all()
        assert len(agg._snapshots) <= agg._MAX_SNAPSHOTS


class TestBoundary:
    def test_poll_all_with_custom_probe_manager(self):
        hp = pytest.importorskip(
            "zephyr.infrastructure.system_telemetry.health_probes",
            reason="health_probes import failed",
        )
        pm = hp.HealthProbeManager()
        agg = ha.HealthAggregator(probe_manager=pm)
        results = agg.poll_all()
        assert len(results) > 0

    def test_annual_report_empty_data(self):
        agg = ha.HealthAggregator()
        report = agg.annual_report(year=2026, uptimes={}, mttr={}, degradations={})
        assert report.uptime_ratio == {}
