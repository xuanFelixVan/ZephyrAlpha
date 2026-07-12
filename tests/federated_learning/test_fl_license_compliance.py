# [A_test] module_id: SRC-TST-0970 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_license_compliance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.license_compliance
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_license_compliance.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.license_compliance import LicenseCompliance, LicenseRisk


class TestLicenseComplianceInstantiation:
    def test_default_construction(self):
        lc = LicenseCompliance()
        assert lc.dependencies == []
        assert "AGPL-3.0" in lc.forbidden_licenses


class TestRegister:
    def test_register_permissive(self):
        lc = LicenseCompliance()
        risk = lc.register("requests", "2.31.0", "Apache-2.0")
        assert risk == LicenseRisk.PERMISSIVE

    def test_register_copyleft(self):
        lc = LicenseCompliance()
        risk = lc.register("gpl-lib", "1.0.0", "GPL-2.0")
        assert risk == LicenseRisk.COPYLEFT

    def test_register_forbidden(self):
        lc = LicenseCompliance()
        risk = lc.register("agpl-lib", "1.0.0", "AGPL-3.0")
        assert risk == LicenseRisk.FORBIDDEN

    def test_register_unknown(self):
        lc = LicenseCompliance()
        risk = lc.register("weird-lib", "1.0.0", "CustomLicense")
        assert risk == LicenseRisk.UNKNOWN

    def test_register_appends_dependency(self):
        lc = LicenseCompliance()
        lc.register("pkg-a", "1.0", "MIT")
        lc.register("pkg-b", "2.0", "GPL-3.0")
        assert len(lc.dependencies) == 2


class TestCopyleftAlerts:
    def test_no_alerts_when_all_permissive(self):
        lc = LicenseCompliance()
        lc.register("pkg-a", "1.0", "MIT")
        assert lc.copyleft_alerts() == []

    def test_alerts_for_copyleft(self):
        lc = LicenseCompliance()
        lc.register("pkg-a", "1.0", "LGPL-3.0")
        alerts = lc.copyleft_alerts()
        assert len(alerts) == 1
        assert alerts[0].risk == LicenseRisk.COPYLEFT

    def test_alerts_for_forbidden(self):
        lc = LicenseCompliance()
        lc.register("pkg-a", "1.0", "AGPL-3.0")
        alerts = lc.copyleft_alerts()
        assert len(alerts) == 1
        assert alerts[0].risk == LicenseRisk.FORBIDDEN


class TestBoundaries:
    def test_register_empty_spdx(self):
        lc = LicenseCompliance()
        risk = lc.register("pkg", "1.0", "")
        assert risk == LicenseRisk.UNKNOWN

    def test_register_mit_license(self):
        lc = LicenseCompliance()
        risk = lc.register("pkg", "1.0", "MIT")
        assert risk == LicenseRisk.PERMISSIVE
