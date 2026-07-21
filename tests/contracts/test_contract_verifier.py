# [A_test] module_id: MOD-GOV_contract_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.verifiers.contract_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.verifiers.contract_verifier import ContractStatus, ContractVerifier

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestContractStatus:
    def test_defaults(self):
        cs = ContractStatus(contract_id="G-CT-001")
        assert cs.compliant is False
        assert cs.detail == ""
        assert cs.checked_at == ""

    def test_with_values(self):
        cs = ContractStatus(contract_id="G-CT-004", compliant=True, detail="ok", checked_at="2026-01-01")
        assert cs.compliant is True
        assert cs.detail == "ok"


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestContractVerifier:
    def test_verify_gct001_compliant(self):
        cv = ContractVerifier()

        class FakeIdentity:
            agent_id = "a1"
            maturity = "L0"

        result = cv.verify_gct001(FakeIdentity())
        assert result.contract_id == "G-CT-001"
        assert result.compliant is True

    def test_verify_gct001_non_compliant(self):
        cv = ContractVerifier()

        class FakeIdentity:
            agent_id = "a1"

        result = cv.verify_gct001(FakeIdentity())
        assert result.compliant is False

    def test_verify_gct001_empty_object(self):
        cv = ContractVerifier()
        result = cv.verify_gct001(object())
        assert result.compliant is False

    def test_verify_gct004_compliant(self):
        cv = ContractVerifier()

        class FakeDecision:
            blocked_layer = "L1"
            rule_id = "R1"

        result = cv.verify_gct004(FakeDecision())
        assert result.compliant is True

    def test_verify_gct004_non_compliant(self):
        cv = ContractVerifier()
        result = cv.verify_gct004(object())
        assert result.compliant is False

    def test_verify_gct007_pass(self):
        cv = ContractVerifier()
        result = cv.verify_gct007(test_count=150)
        assert result.compliant is True

    def test_verify_gct007_fail(self):
        cv = ContractVerifier()
        result = cv.verify_gct007(test_count=50)
        assert result.compliant is False

    def test_verify_gct007_boundary(self):
        cv = ContractVerifier()
        result = cv.verify_gct007(test_count=120)
        assert result.compliant is True

    def test_verify_gct007_zero(self):
        cv = ContractVerifier()
        result = cv.verify_gct007(test_count=0)
        assert result.compliant is False

    def test_verify_gct008_compliant(self):
        cv = ContractVerifier()
        result = cv.verify_gct008(strategies=["A", "B", "C", "AUTO_GUARD"])
        assert result.compliant is True

    def test_verify_gct008_partial(self):
        cv = ContractVerifier()
        result = cv.verify_gct008(strategies=["A", "B"])
        assert result.compliant is False

    def test_verify_gct008_none(self):
        cv = ContractVerifier()
        result = cv.verify_gct008(strategies=None)
        assert result.compliant is False

    def test_verify_gct008_empty_list(self):
        cv = ContractVerifier()
        result = cv.verify_gct008(strategies=[])
        assert result.compliant is False

    def test_verify_all(self):
        cv = ContractVerifier()
        results = cv.verify_all()
        assert len(results) == 4
        for cid in ["G-CT-001", "G-CT-004", "G-CT-007", "G-CT-008"]:
            assert cid in results
            assert results[cid].compliant is True
