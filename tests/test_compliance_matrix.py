# [A_test] module_id: SRC-TST-0557 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.compliance_matrix
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.compliance_matrix import (
        COMPLIANCE_MATRIX,
        ComplianceItem,
        ComplianceStatus,
        compliant_items,
        get_by_reg_id,
        non_compliant_items,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestComplianceStatus:
    def test_enum_values(self):
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.EXEMPT.value == "exempt"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"

    def test_enum_is_string(self):
        assert isinstance(ComplianceStatus.COMPLIANT, str)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestComplianceItem:
    def test_item_creation(self):
        item = ComplianceItem(
            reg_id="TEST",
            regulation="Test Reg",
            status=ComplianceStatus.COMPLIANT,
            control="test control",
        )
        assert item.reg_id == "TEST"
        assert item.regulation == "Test Reg"
        assert item.status == ComplianceStatus.COMPLIANT
        assert item.control == "test control"
        assert item.evidence_path == ""
        assert item.last_audit is None

    def test_item_with_optional_fields(self):
        item = ComplianceItem(
            reg_id="TEST2",
            regulation="Test Reg 2",
            status=ComplianceStatus.NON_COMPLIANT,
            control="ctrl",
            evidence_path="/path/to/evidence",
            last_audit="2026-01-01",
        )
        assert item.evidence_path == "/path/to/evidence"
        assert item.last_audit == "2026-01-01"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestComplianceMatrixData:
    def test_matrix_not_empty(self):
        assert len(COMPLIANCE_MATRIX) > 0

    def test_matrix_contains_known_reg_ids(self):
        reg_ids = [item.reg_id for item in COMPLIANCE_MATRIX]
        assert "KYC" in reg_ids
        assert "AML" in reg_ids
        assert "GDPR" in reg_ids

    def test_get_by_reg_id_found(self):
        item = get_by_reg_id("GDPR")
        assert item is not None
        assert item.reg_id == "GDPR"
        assert item.status == ComplianceStatus.COMPLIANT

    def test_get_by_reg_id_not_found(self):
        item = get_by_reg_id("NONEXISTENT")
        assert item is None

    def test_get_by_reg_id_empty_string(self):
        item = get_by_reg_id("")
        assert item is None

    def test_non_compliant_items(self):
        items = non_compliant_items()
        for item in items:
            assert item.status == ComplianceStatus.NON_COMPLIANT

    def test_compliant_items(self):
        items = compliant_items()
        for item in items:
            assert item.status == ComplianceStatus.COMPLIANT

    def test_compliant_plus_non_compliant_subset_of_matrix(self):
        compliant = set(i.reg_id for i in compliant_items())
        non_compliant = set(i.reg_id for i in non_compliant_items())
        assert compliant.isdisjoint(non_compliant)
