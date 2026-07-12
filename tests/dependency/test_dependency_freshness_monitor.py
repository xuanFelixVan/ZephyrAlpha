# [A_test] module_id: SRC-TST-0735 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_dependency_freshness_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_dependency_freshness_monitor.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.detectors.dependency_freshness_monitor import (
    DependencyFreshnessMonitor,
    FreshnessStatus,
)


class TestFreshnessStatus:
    def test_enum_values(self):
        assert FreshnessStatus.FRESH.value == "FRESH"
        assert FreshnessStatus.AGING.value == "AGING"
        assert FreshnessStatus.STALE.value == "STALE"
        assert FreshnessStatus.CRITICAL.value == "CRITICAL"


class TestDependencyFreshnessMonitorInstantiation:
    def test_default_instantiation(self):
        monitor = DependencyFreshnessMonitor()
        assert monitor.max_age_days == 180
        assert monitor.max_major_version_lag == 2
        assert monitor.cve_severity_threshold == "HIGH"
        assert monitor.dependencies == {}
        assert monitor.freshness_alerts == []

    def test_custom_parameters(self):
        monitor = DependencyFreshnessMonitor(max_age_days=90, max_major_version_lag=1)
        assert monitor.max_age_days == 90
        assert monitor.max_major_version_lag == 1


class TestRegister:
    def test_register_dependency(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("numpy", "1.20.0", "1.26.0", time.time())
        assert "numpy" in monitor.dependencies

    def test_register_with_cves(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("openssl", "1.1.1", "3.1.0", time.time(), known_cves=["CVE-2024-0001"])
        assert len(monitor.dependencies["openssl"]["cves"]) == 1

    def test_register_without_cves(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("requests", "2.28.0", "2.31.0", time.time())
        assert monitor.dependencies["requests"]["cves"] == []

    def test_register_overwrites_existing(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("numpy", "1.20.0", "1.26.0", time.time())
        monitor.register("numpy", "1.25.0", "1.26.0", time.time())
        assert monitor.dependencies["numpy"]["current"] == "1.25.0"


class TestCheckFreshness:
    def test_fresh_dependency_no_alerts(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("fresh_pkg", "1.0.0", "1.0.0", time.time())
        alerts = monitor.check_freshness()
        assert len(alerts) == 0

    def test_aging_dependency(self):
        monitor = DependencyFreshnessMonitor(max_age_days=180)
        old_ts = time.time() - 100 * 86400
        monitor.register("aging_pkg", "1.0.0", "1.0.0", old_ts)
        alerts = monitor.check_freshness()
        assert any(a["status"] == FreshnessStatus.AGING.value for a in alerts)

    def test_stale_dependency_by_age(self):
        monitor = DependencyFreshnessMonitor(max_age_days=180)
        old_ts = time.time() - 200 * 86400
        monitor.register("stale_pkg", "1.0.0", "1.0.0", old_ts)
        alerts = monitor.check_freshness()
        assert any(a["status"] == FreshnessStatus.STALE.value for a in alerts)

    def test_critical_dependency_by_extreme_age(self):
        monitor = DependencyFreshnessMonitor(max_age_days=180)
        very_old_ts = time.time() - 400 * 86400
        monitor.register("critical_pkg", "1.0.0", "1.0.0", very_old_ts)
        alerts = monitor.check_freshness()
        assert any(a["status"] == FreshnessStatus.CRITICAL.value for a in alerts)

    def test_critical_dependency_by_cve(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("vuln_pkg", "1.0.0", "1.0.0", time.time(), known_cves=["CVE-2024-0001"])
        alerts = monitor.check_freshness()
        assert any(a["status"] == FreshnessStatus.CRITICAL.value for a in alerts)

    def test_stale_by_version_lag(self):
        monitor = DependencyFreshnessMonitor(max_major_version_lag=2)
        monitor.register("old_ver", "1.0.0", "4.0.0", time.time())
        alerts = monitor.check_freshness()
        assert any(a["status"] == FreshnessStatus.STALE.value for a in alerts)

    def test_empty_dependencies(self):
        monitor = DependencyFreshnessMonitor()
        alerts = monitor.check_freshness()
        assert alerts == []

    def test_alerts_populate_freshness_alerts(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("vuln_pkg", "1.0.0", "1.0.0", time.time(), known_cves=["CVE-2024-0001"])
        monitor.check_freshness()
        assert len(monitor.freshness_alerts) >= 1


class TestGetStalest:
    def test_empty_dependencies(self):
        monitor = DependencyFreshnessMonitor()
        result = monitor.get_stalest()
        assert result == []

    def test_returns_top_n(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("pkg_a", "1.0.0", "1.0.0", time.time() - 100 * 86400)
        monitor.register("pkg_b", "1.0.0", "1.0.0", time.time() - 200 * 86400)
        result = monitor.get_stalest(top_n=1)
        assert len(result) == 1

    def test_sorts_by_cves_then_age(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("pkg_no_cve", "1.0.0", "1.0.0", time.time() - 300 * 86400)
        monitor.register("pkg_with_cve", "1.0.0", "1.0.0", time.time() - 10 * 86400, known_cves=["CVE-1"])
        result = monitor.get_stalest(top_n=2)
        assert result[0]["package"] == "pkg_with_cve"


class TestOverallHealthScore:
    def test_empty_dependencies_returns_one(self):
        monitor = DependencyFreshnessMonitor()
        assert monitor.overall_health_score() == 1.0

    def test_fresh_dependencies_high_score(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("fresh", "1.0.0", "1.0.0", time.time())
        score = monitor.overall_health_score()
        assert score > 0.9

    def test_cve_reduces_score(self):
        monitor = DependencyFreshnessMonitor()
        monitor.register("no_cve", "1.0.0", "1.0.0", time.time())
        monitor.register("with_cve", "1.0.0", "1.0.0", time.time(), known_cves=["CVE-1"])
        score = monitor.overall_health_score()
        assert score < 1.0

    def test_old_dependencies_lower_score(self):
        monitor = DependencyFreshnessMonitor(max_age_days=180)
        monitor.register("old", "1.0.0", "1.0.0", time.time() - 300 * 86400)
        score = monitor.overall_health_score()
        assert score < 0.5
