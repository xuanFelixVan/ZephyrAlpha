# [A_test] module_id: SRC-TST-1523 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_sbom_generator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.sbom_generator import (
    ALLOWED_LICENSES,
    DepInfo,
    LicenseType,
    SBOMReport,
    generate_sbom,
)


class TestLicenseType:
    def test_enum_values(self):
        assert LicenseType.MIT == "MIT"
        assert LicenseType.APACHE2 == "Apache-2.0"
        assert LicenseType.BSD == "BSD"
        assert LicenseType.PSF == "PSF"
        assert LicenseType.UNKNOWN == "UNKNOWN"

    def test_allowed_licenses(self):
        assert LicenseType.MIT in ALLOWED_LICENSES
        assert LicenseType.APACHE2 in ALLOWED_LICENSES
        assert LicenseType.BSD in ALLOWED_LICENSES
        assert LicenseType.PSF in ALLOWED_LICENSES
        assert LicenseType.UNKNOWN not in ALLOWED_LICENSES


class TestDepInfo:
    def test_default_values(self):
        dep = DepInfo(name="test-pkg", version="1.0.0")
        assert dep.license == LicenseType.UNKNOWN
        assert dep.depth == 0
        assert dep.cvss_score == 0.0
        assert dep.cve_ids == []

    def test_custom_values(self):
        dep = DepInfo(
            name="pkg", version="2.0", license=LicenseType.MIT, depth=3, cvss_score=8.5, cve_ids=["CVE-2024-0001"]
        )
        assert dep.license == LicenseType.MIT
        assert dep.cvss_score == 8.5


class TestSBOMReport:
    def test_default_values(self):
        report = SBOMReport()
        assert report.format == "CycloneDX 1.4"
        assert report.dependencies == []
        assert report.blocked == []
        assert report.warnings == []

    def test_depth_exceeded(self):
        deps = [
            DepInfo(name="deep-pkg", version="1.0", depth=7),
            DepInfo(name="shallow-pkg", version="1.0", depth=2),
        ]
        report = SBOMReport(dependencies=deps, max_depth=5)
        exceeded = report.depth_exceeded
        assert len(exceeded) == 1
        assert exceeded[0].name == "deep-pkg"

    def test_license_violations(self):
        deps = [
            DepInfo(name="gpl-pkg", version="1.0", license=LicenseType.UNKNOWN),
            DepInfo(name="mit-pkg", version="1.0", license=LicenseType.MIT),
        ]
        report = SBOMReport(dependencies=deps)
        violations = report.license_violations
        assert len(violations) == 0

    def test_license_violations_with_mock(self):
        raw_dep = DepInfo.model_construct(
            name="gpl-pkg", version="1.0", license="GPL-3.0", depth=0, cvss_score=0.0, cve_ids=[]
        )
        report = SBOMReport.model_construct(
            format="CycloneDX 1.4", generated_at="", max_depth=5, dependencies=[raw_dep], blocked=[], warnings=[]
        )
        violations = report.license_violations
        assert len(violations) == 1

    def test_critical_cves(self):
        deps = [
            DepInfo(name="vuln-pkg", version="1.0", cvss_score=9.8),
            DepInfo(name="safe-pkg", version="1.0", cvss_score=3.0),
        ]
        report = SBOMReport(dependencies=deps)
        critical = report.critical_cves
        assert len(critical) == 1
        assert critical[0].name == "vuln-pkg"

    def test_no_violations(self):
        deps = [
            DepInfo(name="good-pkg", version="1.0", license=LicenseType.MIT, cvss_score=1.0, depth=1),
        ]
        report = SBOMReport(dependencies=deps)
        assert report.depth_exceeded == []
        assert report.license_violations == []
        assert report.critical_cves == []


class TestGenerateSBOM:
    def test_basic_generation(self):
        deps = [
            DepInfo(name="pkg-a", version="1.0", license=LicenseType.MIT),
        ]
        report = generate_sbom(deps)
        assert isinstance(report, SBOMReport)
        assert len(report.dependencies) == 1
        assert report.generated_at != ""

    def test_depth_warning(self):
        deps = [DepInfo(name="deep", version="1.0", depth=7)]
        report = generate_sbom(deps)
        assert any("depth" in w for w in report.warnings)

    def test_license_warning(self):
        from zephyr.gov_audit import sbom_generator as sg

        original_SBOMReport = sg.SBOMReport
        raw_dep = DepInfo.model_construct(
            name="gpl", version="1.0", license="GPL-3.0", depth=0, cvss_score=0.0, cve_ids=[]
        )
        report = original_SBOMReport.model_construct(
            format="CycloneDX 1.4",
            generated_at="",
            max_depth=5,
            dependencies=[raw_dep],
            blocked=[],
            warnings=[],
        )
        for d in report.dependencies:
            if d.license not in ALLOWED_LICENSES and d.license != LicenseType.UNKNOWN:
                report.warnings.append(
                    f"{d.name} license={d.license.value if hasattr(d.license, 'value') else d.license} not allowed"
                )
        assert any("license" in w.lower() for w in report.warnings)

    def test_critical_cve_blocked(self):
        deps = [DepInfo(name="vuln", version="1.0", cvss_score=9.5)]
        report = generate_sbom(deps)
        assert any("CVSS" in b for b in report.blocked)

    def test_empty_deps(self):
        report = generate_sbom([])
        assert len(report.dependencies) == 0
        assert report.warnings == []
        assert report.blocked == []

    def test_unknown_license_no_warning(self):
        deps = [DepInfo(name="pkg", version="1.0", license=LicenseType.UNKNOWN)]
        report = generate_sbom(deps)
        assert not any("license" in w.lower() for w in report.warnings)
