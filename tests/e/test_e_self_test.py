# [A_test] module_id: MOD-GOV_e_self_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_self_test
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.self_test import (
    CheckResult,
    HealthLevel,
    SelfTestReport,
)


class TestHealthLevel:
    def test_three_members(self):
        assert len(HealthLevel) == 3

    def test_values(self):
        assert HealthLevel.HEALTHY.value == "healthy"
        assert HealthLevel.DEGRADED.value == "degraded"
        assert HealthLevel.CRITICAL.value == "critical"


class TestCheckResult:
    def test_default_instantiation(self):
        cr = CheckResult(name="test_check", passed=True)
        assert cr.name == "test_check"
        assert cr.passed is True
        assert cr.level == HealthLevel.HEALTHY
        assert cr.detail == ""
        assert cr.latency_ms == 0.0

    def test_failed_check(self):
        cr = CheckResult(name="bad", passed=False, level=HealthLevel.CRITICAL, detail="error")
        assert cr.passed is False
        assert cr.level == HealthLevel.CRITICAL
        assert cr.detail == "error"


class TestSelfTestReport:
    def test_default_instantiation(self):
        rpt = SelfTestReport()
        assert rpt.checks == []
        assert rpt.total_passed == 0
        assert rpt.total_failed == 0
        assert rpt.overall == HealthLevel.HEALTHY
        assert rpt.duration_ms == 0.0

    def test_with_checks(self):
        checks = [
            CheckResult("c1", True),
            CheckResult("c2", False, HealthLevel.DEGRADED),
        ]
        rpt = SelfTestReport(checks=checks, total_passed=1, total_failed=1, overall=HealthLevel.DEGRADED)
        assert len(rpt.checks) == 2
        assert rpt.total_passed == 1
        assert rpt.total_failed == 1
        assert rpt.overall == HealthLevel.DEGRADED
