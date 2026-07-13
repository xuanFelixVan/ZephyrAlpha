# [A_test] module_id: SRC-TST-0321 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_api_dependency_metrics
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.api_dependency_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_api_dependency_metrics.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.reliability.api_dependency_metrics import (
    APIDependencyMetrics,
    DependencyStatusRecord,
)


class TestDependencyStatusRecord:
    def test_default_construction(self):
        rec = DependencyStatusRecord(service="svc-a", version="1.0")
        assert rec.service == "svc-a"
        assert rec.version == "1.0"
        assert rec.cve_count == 0
        assert rec.license_copyleft is False
        assert rec.sunset_overdue is False

    def test_risk_level_low(self):
        rec = DependencyStatusRecord(service="svc", version="1.0")
        assert rec.risk_level == "LOW"

    def test_risk_level_high_cve(self):
        rec = DependencyStatusRecord(service="svc", version="1.0", cve_count=2)
        assert rec.risk_level == "HIGH"

    def test_risk_level_medium_copyleft(self):
        rec = DependencyStatusRecord(service="svc", version="1.0", license_copyleft=True)
        assert rec.risk_level == "MEDIUM"

    def test_risk_level_high_sunset_overdue(self):
        rec = DependencyStatusRecord(service="svc", version="1.0", sunset_overdue=True)
        assert rec.risk_level == "HIGH"

    def test_risk_level_cve_takes_precedence_over_copyleft(self):
        rec = DependencyStatusRecord(service="svc", version="1.0", cve_count=1, license_copyleft=True)
        assert rec.risk_level == "HIGH"

    def test_risk_level_cve_takes_precedence_over_sunset(self):
        rec = DependencyStatusRecord(service="svc", version="1.0", cve_count=1, sunset_overdue=True)
        assert rec.risk_level == "HIGH"


class TestAPIDependencyMetrics:
    def test_instantiation_default(self):
        metrics = APIDependencyMetrics()
        assert metrics.dependencies == {}
        assert len(metrics.history) == 0

    def test_register_creates_dependency(self):
        metrics = APIDependencyMetrics()
        dep = metrics.register("svc-a", "2.0")
        assert isinstance(dep, DependencyStatusRecord)
        assert dep.service == "svc-a"
        assert dep.version == "2.0"
        assert "svc-a" in metrics.dependencies

    def test_register_overwrites_existing(self):
        metrics = APIDependencyMetrics()
        metrics.register("svc-a", "1.0")
        dep = metrics.register("svc-a", "2.0")
        assert dep.version == "2.0"
        assert len(metrics.dependencies) == 1

    def test_scan_empty(self):
        metrics = APIDependencyMetrics()
        result = metrics.scan()
        assert result == {"total": 0, "cve_active": 0, "copyleft": 0, "sunset_overdue": 0}

    def test_scan_with_deps(self):
        metrics = APIDependencyMetrics()
        metrics.register("svc-a", "1.0")
        metrics.register("svc-b", "2.0")
        result = metrics.scan()
        assert result["total"] == 2
        assert result["cve_active"] == 0

    def test_scan_counts_cve(self):
        metrics = APIDependencyMetrics()
        dep = metrics.register("svc-a", "1.0")
        dep.cve_count = 3
        metrics.register("svc-b", "2.0")
        result = metrics.scan()
        assert result["cve_active"] == 1

    def test_scan_counts_copyleft(self):
        metrics = APIDependencyMetrics()
        dep = metrics.register("svc-a", "1.0")
        dep.license_copyleft = True
        result = metrics.scan()
        assert result["copyleft"] == 1

    def test_scan_counts_sunset_overdue(self):
        metrics = APIDependencyMetrics()
        dep = metrics.register("svc-a", "1.0")
        dep.sunset_overdue = True
        result = metrics.scan()
        assert result["sunset_overdue"] == 1

    def test_snapshot_appends_history(self):
        metrics = APIDependencyMetrics()
        metrics.register("svc-a", "1.0")
        metrics.snapshot()
        assert len(metrics.history) == 1
        assert metrics.history[0]["total"] == 1

    def test_snapshot_multiple(self):
        metrics = APIDependencyMetrics()
        metrics.register("svc-a", "1.0")
        metrics.snapshot()
        metrics.register("svc-b", "2.0")
        metrics.snapshot()
        assert len(metrics.history) == 2
        assert metrics.history[0]["total"] == 1
        assert metrics.history[1]["total"] == 2

    def test_history_maxlen(self):
        metrics = APIDependencyMetrics()
        metrics.register("svc-a", "1.0")
        for _ in range(600):
            metrics.snapshot()
        assert len(metrics.history) <= 500

    def test_register_returns_record_with_defaults(self):
        metrics = APIDependencyMetrics()
        dep = metrics.register("svc-x", "3.0")
        assert dep.cve_count == 0
        assert dep.license_copyleft is False
        assert dep.sunset_overdue is False
