# [A_test] module_id: SRC-TST-1705 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-436 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_supply_chain_security
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
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

    def test_enum_members_count(self):
        assert len(VendorRisk) == 3


class TestSupplyChainReport:
    def test_default_values(self):
        report = SupplyChainReport()
        assert report.total_deps == 0
        assert report.vulnerabilities == []
        assert report.blocked is False
        assert report.vendor_risk == VendorRisk.OK

    def test_custom_values(self):
        report = SupplyChainReport(
            total_deps=10,
            blocked=True,
            vendor_risk=VendorRisk.CRITICAL,
        )
        assert report.total_deps == 10
        assert report.blocked is True
        assert report.vendor_risk == VendorRisk.CRITICAL


class TestScanDependencies:
    def test_returns_report(self):
        report = scan_dependencies()
        assert isinstance(report, SupplyChainReport)
        assert report.scanned_at != ""
        assert report.total_deps >= 0

    def test_report_has_timestamp(self):
        report = scan_dependencies()
        assert len(report.scanned_at) > 0


class TestCheckVendorLockin:
    def test_recent_update_ok(self):
        recent = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        result = check_vendor_lockin(recent)
        assert result == VendorRisk.OK

    def test_old_update_critical(self):
        old = (datetime.now(UTC) - timedelta(days=400)).isoformat()
        result = check_vendor_lockin(old)
        assert result == VendorRisk.CRITICAL

    def test_approaching_threshold_warning(self):
        near = (datetime.now(UTC) - timedelta(days=280)).isoformat()
        result = check_vendor_lockin(near)
        assert result == VendorRisk.WARNING

    def test_invalid_date_returns_warning(self):
        result = check_vendor_lockin("not-a-date")
        assert result == VendorRisk.WARNING

    def test_none_returns_warning(self):
        with pytest.raises(AttributeError):
            check_vendor_lockin(None)

    def test_custom_threshold(self):
        recent = (datetime.now(UTC) - timedelta(days=200)).isoformat()
        result = check_vendor_lockin(recent, months_threshold=6)
        assert result == VendorRisk.CRITICAL


class TestGenerateSpdx:
    def test_basic_spdx(self):
        result = generate_spdx("test-project", [{"name": "pkg1", "version": "1.0"}])
        assert result["SPDXVersion"] == "SPDX-2.3"
        assert result["name"] == "test-project"
        assert len(result["packages"]) == 1

    def test_spdx_has_creation_info(self):
        result = generate_spdx("proj", [])
        assert "creationInfo" in result
        assert "created" in result["creationInfo"]

    def test_spdx_id_format(self):
        result = generate_spdx("my-proj", [])
        assert result["SPDXID"] == "SPDXRef-my-proj"

    def test_empty_packages(self):
        result = generate_spdx("proj", [])
        assert result["packages"] == []
