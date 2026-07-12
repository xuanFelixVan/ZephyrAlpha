# [A_test] module_id: SRC-TST-1224 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_license_compliance
# [INVARIANTS] License classification must follow SPDX rules deterministically
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.license_compliance import (
    DependencyLicense,
    LicenseCompliance,
    LicenseRisk,
)


class TestLicenseRisk:
    def test_enum_values(self):
        assert LicenseRisk.PERMISSIVE == "PERMISSIVE"
        assert LicenseRisk.COPYLEFT == "COPYLEFT"
        assert LicenseRisk.UNKNOWN == "UNKNOWN"
        assert LicenseRisk.FORBIDDEN == "FORBIDDEN"


class TestDependencyLicense:
    def test_creation(self):
        dl = DependencyLicense(package="foo", version="1.0", license_spdx="MIT", risk=LicenseRisk.PERMISSIVE)
        assert dl.package == "foo"
        assert dl.version == "1.0"
        assert dl.license_spdx == "MIT"
        assert dl.risk == LicenseRisk.PERMISSIVE


class TestLicenseComplianceInstantiation:
    def test_default_values(self):
        lc = LicenseCompliance()
        assert lc.dependencies == []
        assert "AGPL-3.0" in lc.forbidden_licenses
        assert "GPL-3.0" in lc.forbidden_licenses

    def test_custom_forbidden_licenses(self):
        lc = LicenseCompliance(forbidden_licenses={"CUSTOM-FORBIDDEN"})
        assert "CUSTOM-FORBIDDEN" in lc.forbidden_licenses


class TestRegister:
    def test_permissive_license(self):
        lc = LicenseCompliance()
        risk = lc.register("requests", "2.28", "MIT")
        assert risk == LicenseRisk.PERMISSIVE
        assert len(lc.dependencies) == 1

    def test_apache_permissive(self):
        lc = LicenseCompliance()
        risk = lc.register("lib", "1.0", "Apache-2.0")
        assert risk == LicenseRisk.PERMISSIVE

    def test_bsd_permissive(self):
        lc = LicenseCompliance()
        risk = lc.register("lib", "1.0", "BSD-3-Clause")
        assert risk == LicenseRisk.PERMISSIVE

    def test_copyleft_license(self):
        lc = LicenseCompliance()
        risk = lc.register("gpl-lib", "1.0", "GPL-2.0")
        assert risk == LicenseRisk.COPYLEFT

    def test_lgpl_copyleft(self):
        lc = LicenseCompliance()
        risk = lc.register("lgpl-lib", "1.0", "LGPL-3.0")
        assert risk == LicenseRisk.COPYLEFT

    def test_forbidden_license(self):
        lc = LicenseCompliance()
        risk = lc.register("agpl-lib", "1.0", "AGPL-3.0")
        assert risk == LicenseRisk.FORBIDDEN

    def test_gpl3_forbidden(self):
        lc = LicenseCompliance()
        risk = lc.register("gpl3-lib", "1.0", "GPL-3.0")
        assert risk == LicenseRisk.FORBIDDEN

    def test_unknown_license(self):
        lc = LicenseCompliance()
        risk = lc.register("weird-lib", "1.0", "CUSTOM-LICENSE")
        assert risk == LicenseRisk.UNKNOWN

    def test_multiple_registrations(self):
        lc = LicenseCompliance()
        lc.register("lib1", "1.0", "MIT")
        lc.register("lib2", "2.0", "GPL-3.0")
        assert len(lc.dependencies) == 2


class TestCopyleftAlerts:
    def test_no_alerts_when_all_permissive(self):
        lc = LicenseCompliance()
        lc.register("lib1", "1.0", "MIT")
        lc.register("lib2", "1.0", "Apache-2.0")
        assert lc.copyleft_alerts() == []

    def test_alerts_for_copyleft(self):
        lc = LicenseCompliance()
        lc.register("lib1", "1.0", "MIT")
        lc.register("lib2", "1.0", "GPL-2.0")
        alerts = lc.copyleft_alerts()
        assert len(alerts) == 1
        assert alerts[0].package == "lib2"

    def test_alerts_for_forbidden(self):
        lc = LicenseCompliance()
        lc.register("lib1", "1.0", "AGPL-3.0")
        alerts = lc.copyleft_alerts()
        assert len(alerts) == 1
        assert alerts[0].risk == LicenseRisk.FORBIDDEN

    def test_alerts_empty_when_no_deps(self):
        lc = LicenseCompliance()
        assert lc.copyleft_alerts() == []
