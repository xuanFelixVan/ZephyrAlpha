# [A_test] module_id: SRC-TST-0732 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_dep_cve_correlator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.security.dep_cve_correlator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_dep_cve_correlator.py
# [TTL] task_bound


from zephyr.feedback_loop.security.dep_cve_correlator import (
    CVEAlert,
    CVESeverity,
    DepCVECorrelator,
)


class TestDepCVECorrelatorInstantiation:
    def test_default_instantiation(self):
        corr = DepCVECorrelator()
        assert corr.alerts == []
        assert corr.dependencies == []
        assert "nvd.nist.gov" in corr.nvd_api_url

    def test_custom_instantiation(self):
        corr = DepCVECorrelator(nvd_api_url="https://internal-nvd.local/api")
        assert corr.nvd_api_url == "https://internal-nvd.local/api"


class TestRegisterDependency:
    def test_register_single(self):
        corr = DepCVECorrelator()
        corr.register_dependency("requests", "2.28.0")
        assert ("requests", "2.28.0") in corr.dependencies

    def test_register_multiple(self):
        corr = DepCVECorrelator()
        corr.register_dependency("requests", "2.28.0")
        corr.register_dependency("flask", "2.2.0")
        assert len(corr.dependencies) == 2


class TestCheckCritical:
    def test_no_critical_alerts(self):
        corr = DepCVECorrelator()
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-0001",
                dependency="lib",
                severity=CVESeverity.LOW,
                cvss_score=2.0,
                description="low issue",
                affected_version="1.0",
            )
        )
        assert corr.check_critical() == []

    def test_critical_alerts_found(self):
        corr = DepCVECorrelator()
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-0002",
                dependency="lib",
                severity=CVESeverity.CRITICAL,
                cvss_score=9.8,
                description="critical issue",
                affected_version="1.0",
            )
        )
        critical = corr.check_critical()
        assert len(critical) == 1
        assert critical[0].cve_id == "CVE-2024-0002"

    def test_mixed_severity_alerts(self):
        corr = DepCVECorrelator()
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-L",
                dependency="a",
                severity=CVESeverity.LOW,
                cvss_score=2.0,
                description="low",
                affected_version="1.0",
            )
        )
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-C",
                dependency="b",
                severity=CVESeverity.CRITICAL,
                cvss_score=9.8,
                description="critical",
                affected_version="1.0",
            )
        )
        assert len(corr.check_critical()) == 1


class TestAutoFixAvailable:
    def test_no_fix_available(self):
        corr = DepCVECorrelator()
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-0003",
                dependency="lib",
                severity=CVESeverity.HIGH,
                cvss_score=7.5,
                description="no fix",
                affected_version="1.0",
                fixed_version="",
            )
        )
        assert corr.auto_fix_available() == {}

    def test_fix_available(self):
        corr = DepCVECorrelator()
        corr.alerts.append(
            CVEAlert(
                cve_id="CVE-2024-0004",
                dependency="lib",
                severity=CVESeverity.HIGH,
                cvss_score=7.5,
                description="fix available",
                affected_version="1.0",
                fixed_version="1.1",
            )
        )
        fixes = corr.auto_fix_available()
        assert fixes["CVE-2024-0004"] == "1.1"


class TestCVEAlert:
    def test_alert_defaults(self):
        alert = CVEAlert(
            cve_id="CVE-2024-0005",
            dependency="x",
            severity=CVESeverity.MEDIUM,
            cvss_score=5.0,
            description="test",
            affected_version="2.0",
        )
        assert alert.fixed_version == ""
