# [A_test] module_id: SRC-TST-0367 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_supply_chain_security
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

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_audit.supply_chain_security import (
    SupplyChainReport,
    VendorRisk,
    check_vendor_lockin,
    generate_spdx,
    scan_dependencies,
)


class TestVendorRisk:
    def test_enum_values(self):
        assert VendorRisk.OK == "OK"
        assert VendorRisk.WARNING == "WARNING"
        assert VendorRisk.CRITICAL == "CRITICAL"


class TestSupplyChainReport:
    def test_default_values(self):
        report = SupplyChainReport()
        assert report.total_deps == 0
        assert report.vulnerabilities == []
        assert report.blocked is False
        assert report.vendor_risk == VendorRisk.OK
        assert report.last_vendor_update is None

    def test_custom_values(self):
        report = SupplyChainReport(total_deps=10, blocked=True, vendor_risk=VendorRisk.CRITICAL)
        assert report.total_deps == 10
        assert report.blocked is True


class TestScanDependencies:
    def test_default_scan(self):
        report = scan_dependencies()
        assert isinstance(report, SupplyChainReport)
        assert report.scanned_at != ""
        assert report.total_deps == 0

    def test_scan_nonexistent_lock_file(self):
        report = scan_dependencies("nonexistent.lock")
        assert isinstance(report, SupplyChainReport)


class TestCheckVendorLockin:
    def test_recent_update_ok(self):
        recent = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        result = check_vendor_lockin(recent)
        assert result == VendorRisk.OK

    def test_old_update_critical(self):
        old = (datetime.now(UTC) - timedelta(days=400)).isoformat()
        result = check_vendor_lockin(old)
        assert result == VendorRisk.CRITICAL

    def test_medium_age_warning(self):
        medium = (datetime.now(UTC) - timedelta(days=280)).isoformat()
        result = check_vendor_lockin(medium)
        assert result == VendorRisk.WARNING

    def test_invalid_date_returns_warning(self):
        result = check_vendor_lockin("not-a-date")
        assert result == VendorRisk.WARNING

    def test_none_returns_warning(self):
        with pytest.raises((AttributeError, TypeError)):
            check_vendor_lockin(None)

    def test_custom_threshold(self):
        recent = (datetime.now(UTC) - timedelta(days=200)).isoformat()
        result = check_vendor_lockin(recent, months_threshold=24)
        assert result == VendorRisk.OK


class TestGenerateSPDX:
    def test_basic_generation(self):
        packages = [{"name": "pkg-a", "version": "1.0"}]
        result = generate_spdx("TestProject", packages)
        assert result["SPDXVersion"] == "SPDX-2.3"
        assert result["DataLicense"] == "CC0-1.0"
        assert result["name"] == "TestProject"
        assert result["SPDXID"] == "SPDXRef-TestProject"
        assert len(result["packages"]) == 1
        assert "created" in result["creationInfo"]

    def test_empty_packages(self):
        result = generate_spdx("EmptyProject", [])
        assert result["packages"] == []

    def test_creation_info_tool(self):
        result = generate_spdx("Proj", [])
        assert any("ZephyrAlpha" in c for c in result["creationInfo"]["creators"])
