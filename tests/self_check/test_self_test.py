# [A_test] module_id: MOD-GOV_self_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_self_test
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_self_test.py
# [TTL] task_bound

from zephyr.governance.intelligence_governance.self_test import (
    CheckResult,
    HealthLevel,
    SelfTestReport,
    main,
    run_self_test,
)


class TestHealthLevel:
    def test_values(self):
        assert HealthLevel.HEALTHY.value == "healthy"
        assert HealthLevel.DEGRADED.value == "degraded"
        assert HealthLevel.CRITICAL.value == "critical"

    def test_is_str_enum(self):
        assert isinstance(HealthLevel.HEALTHY, str)


class TestCheckResult:
    def test_default_values(self):
        cr = CheckResult(name="test_check", passed=True)
        assert cr.name == "test_check"
        assert cr.passed is True
        assert cr.level == HealthLevel.HEALTHY
        assert cr.detail == ""
        assert cr.latency_ms == 0.0

    def test_custom_values(self):
        cr = CheckResult(name="fail_check", passed=False, level=HealthLevel.CRITICAL, detail="boom", latency_ms=5.0)
        assert cr.passed is False
        assert cr.level == HealthLevel.CRITICAL
        assert cr.detail == "boom"
        assert cr.latency_ms == 5.0


class TestSelfTestReport:
    def test_default_values(self):
        r = SelfTestReport()
        assert r.checks == []
        assert r.total_passed == 0
        assert r.total_failed == 0
        assert r.overall == HealthLevel.HEALTHY
        assert r.duration_ms == 0.0

    def test_with_checks(self):
        checks = [
            CheckResult(name="a", passed=True),
            CheckResult(name="b", passed=False, level=HealthLevel.DEGRADED),
        ]
        r = SelfTestReport(checks=checks, total_passed=1, total_failed=1, overall=HealthLevel.DEGRADED)
        assert len(r.checks) == 2
        assert r.total_passed == 1
        assert r.total_failed == 1


class TestRunSelfTest:
    def test_returns_self_test_report(self):
        report = run_self_test()
        assert isinstance(report, SelfTestReport)

    def test_has_checks(self):
        report = run_self_test()
        assert len(report.checks) > 0

    def test_overall_is_valid_health_level(self):
        report = run_self_test()
        assert report.overall in (HealthLevel.HEALTHY, HealthLevel.DEGRADED, HealthLevel.CRITICAL)

    def test_total_passed_plus_failed_equals_checks(self):
        report = run_self_test()
        assert report.total_passed + report.total_failed == len(report.checks)

    def test_duration_positive(self):
        report = run_self_test()
        assert report.duration_ms > 0

    def test_check_names_present(self):
        report = run_self_test()
        names = [c.name for c in report.checks]
        assert "import_chain" in names
        assert "engine_init" in names

    def test_each_check_has_name_and_result(self):
        report = run_self_test()
        for c in report.checks:
            assert isinstance(c.name, str)
            assert len(c.name) > 0
            assert isinstance(c.passed, bool)


class TestMain:
    def test_main_returns_zero_on_healthy(self):
        report = run_self_test()
        if report.overall == HealthLevel.HEALTHY:
            assert main() == 0

    def test_main_json_output(self, capsys):
        import sys

        old_argv = sys.argv
        sys.argv = ["self_test", "--json"]
        try:
            main()
            captured = capsys.readouterr()
            import json

            data = json.loads(captured.out)
            assert "overall" in data
            assert "checks" in data
            assert "total_passed" in data
            assert "total_failed" in data
        finally:
            sys.argv = old_argv
