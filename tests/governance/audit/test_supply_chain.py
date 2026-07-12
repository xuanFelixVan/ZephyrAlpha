# [A_test] module_id: SRC-TST-1704 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_supply_chain
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

from unittest.mock import patch

import pytest

from zephyr.gov_audit.supply_chain import (
    AuditPackageResult,
    IntegrityVerifyResult,
    PackageRecord,
    SupplyChainAuditor,
)


@pytest.fixture
def auditor():
    return SupplyChainAuditor(verify_hashes=False)


@pytest.fixture
def auditor_with_hash():
    return SupplyChainAuditor(verify_hashes=True)


class TestPackageRecord:
    def test_default_values(self):
        rec = PackageRecord()
        assert rec.package_name == ""
        assert rec.integrity_verified is False
        assert rec.metadata == {}

    def test_custom_values(self):
        rec = PackageRecord(package_name="pkg", version="1.0", source="https://pypi.org", integrity_verified=True)
        assert rec.package_name == "pkg"
        assert rec.integrity_verified is True


class TestAuditPackageResult:
    def test_default_values(self):
        result = AuditPackageResult()
        assert result.is_safe is True
        assert result.integrity_ok is True
        assert result.issues == []
        assert result.risk_score == 0.0

    def test_unsafe_result(self):
        result = AuditPackageResult(is_safe=False, issues=["bad"], risk_score=0.8)
        assert result.is_safe is False
        assert len(result.issues) == 1


class TestIntegrityVerifyResult:
    def test_default_values(self):
        result = IntegrityVerifyResult()
        assert result.is_valid is False

    def test_valid_result(self):
        result = IntegrityVerifyResult(package_name="pkg", expected_hash="abc", actual_hash="abc", is_valid=True)
        assert result.is_valid is True


class TestSupplyChainAuditor:
    def test_instantiation(self, auditor):
        assert auditor._verify_hashes is False
        assert len(auditor._trusted_sources) > 0

    def test_audit_safe_package(self, auditor):
        result = auditor.audit_package(
            package_name="safe-pkg",
            version="1.0",
            source="https://pypi.org",
        )
        assert result.is_safe is True
        assert result.issues == []

    def test_audit_http_source(self, auditor):
        result = auditor.audit_package(
            package_name="http-pkg",
            version="1.0",
            source="http://pypi.org",
        )
        assert result.is_safe is False
        assert any("insecure HTTP" in i for i in result.issues)

    def test_audit_unknown_source(self, auditor):
        result = auditor.audit_package(
            package_name="unknown-pkg",
            version="1.0",
            source="unknown",
        )
        assert result.is_safe is False
        assert any("unknown source" in i for i in result.issues)

    def test_audit_suspicious_name(self, auditor):
        result = auditor.audit_package(
            package_name="pkg-dev",
            version="1.0",
            source="https://pypi.org",
        )
        assert result.is_safe is False
        assert any("suspicious pattern" in i for i in result.issues)

    def test_audit_no_source(self, auditor):
        result = auditor.audit_package(package_name="clean-pkg", version="1.0")
        assert result.is_safe is True

    def test_audit_records_package(self, auditor):
        auditor.audit_package(package_name="rec-pkg", version="2.0")
        packages = auditor.get_audited_packages()
        assert len(packages) == 1
        assert packages[0].package_name == "rec-pkg"

    @patch.object(SupplyChainAuditor, "_compute_package_hash", return_value="abc123")
    def test_verify_integrity_match(self, mock_hash, auditor_with_hash):
        result = auditor_with_hash.verify_integrity("test-pkg", "abc123")
        assert result.is_valid is True
        assert result.actual_hash == "abc123"

    @patch.object(SupplyChainAuditor, "_compute_package_hash", return_value="def456")
    def test_verify_integrity_mismatch(self, mock_hash, auditor_with_hash):
        result = auditor_with_hash.verify_integrity("test-pkg", "abc123")
        assert result.is_valid is False

    @patch.object(SupplyChainAuditor, "_compute_package_hash", return_value="")
    def test_verify_integrity_empty_hash(self, mock_hash, auditor_with_hash):
        result = auditor_with_hash.verify_integrity("test-pkg", "abc123")
        assert result.is_valid is False

    def test_risk_score_capped(self, auditor):
        result = auditor.audit_package(
            package_name="pkg-dev",
            version="1.0",
            source="http://pypi.org",
        )
        assert result.risk_score <= 1.0

    def test_audit_with_hash_verification(self, auditor_with_hash):
        with patch.object(SupplyChainAuditor, "_compute_package_hash", return_value="wrong"):
            result = auditor_with_hash.audit_package(
                package_name="hash-pkg",
                version="1.0",
                sha256="expected_hash",
            )
            assert result.integrity_ok is False
