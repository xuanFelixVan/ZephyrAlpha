# [A_test] module_id: SRC-TST-0640 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_cross_blueprint_contract_drift
# [INVARIANTS] max_staleness_days=30; drift_alert_threshold=3
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cross_blueprint_contract_drift.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.cross_blueprint_contract_drift import (
    ContractStatus,
    CrossBlueprintContractDrift,
)


class TestCrossBlueprintContractDriftInstantiation:
    def test_default_construction(self):
        cbd = CrossBlueprintContractDrift()
        assert cbd.max_staleness_days == pytest.approx(30.0)
        assert cbd.drift_alert_threshold == 3
        assert cbd.contracts == {}

    def test_custom_params(self):
        cbd = CrossBlueprintContractDrift(max_staleness_days=7.0, drift_alert_threshold=5)
        assert cbd.max_staleness_days == pytest.approx(7.0)
        assert cbd.drift_alert_threshold == 5


class TestRegisterContract:
    def test_register_new(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig-v1", "/path/mod")
        assert "CT-001" in cbd.contracts
        assert cbd.contracts["CT-001"]["source"] == "BP-A"
        assert cbd.contracts["CT-001"]["status"] == ContractStatus.UNMONITORED

    def test_register_overwrite(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig-v1", "/a")
        cbd.register_contract("CT-001", "BP-C", "BP-D", "sig-v2", "/b")
        assert cbd.contracts["CT-001"]["source"] == "BP-C"


class TestRecordActualSignature:
    def test_matching_signature(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig-v1", "/path")
        result = cbd.record_actual_signature("CT-001", "sig-v1")
        assert result["status"] == ContractStatus.COMPLIANT.value
        assert result["match"] is True

    def test_drifted_signature(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig-v1", "/path")
        result = cbd.record_actual_signature("CT-001", "sig-v2")
        assert result["status"] == ContractStatus.DRIFTED.value
        assert result["match"] is False

    def test_unknown_contract(self):
        cbd = CrossBlueprintContractDrift()
        result = cbd.record_actual_signature("CT-999", "sig-v1")
        assert result["error"] == "unknown_contract"

    def test_empty_signature(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "", "/path")
        result = cbd.record_actual_signature("CT-001", "")
        assert result["match"] is True


class TestCheckStaleness:
    def test_no_contracts(self):
        cbd = CrossBlueprintContractDrift()
        stale = cbd.check_staleness()
        assert stale == []

    def test_recently_validated_not_stale(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig", "/p")
        stale = cbd.check_staleness()
        assert stale == []


class TestGetDriftedContracts:
    def test_no_drift(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig", "/p")
        cbd.record_actual_signature("CT-001", "sig")
        assert cbd.get_drifted_contracts() == []

    def test_with_drift(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "BP-A", "BP-B", "sig-v1", "/p")
        cbd.record_actual_signature("CT-001", "sig-v2")
        drifted = cbd.get_drifted_contracts()
        assert len(drifted) == 1
        assert drifted[0]["contract_id"] == "CT-001"


class TestGetContractHealthSummary:
    def test_empty(self):
        cbd = CrossBlueprintContractDrift()
        summary = cbd.get_contract_health_summary()
        assert summary["health"] == pytest.approx(1.0)
        assert summary["total"] == 0

    def test_all_compliant(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "A", "B", "sig", "/p")
        cbd.record_actual_signature("CT-001", "sig")
        summary = cbd.get_contract_health_summary()
        assert summary["health"] == pytest.approx(1.0)
        assert summary["compliant"] == 1

    def test_drift_alert(self):
        cbd = CrossBlueprintContractDrift(drift_alert_threshold=2)
        cbd.register_contract("CT-001", "A", "B", "sig1", "/p1")
        cbd.register_contract("CT-002", "A", "C", "sig2", "/p2")
        cbd.register_contract("CT-003", "A", "D", "sig3", "/p3")
        cbd.record_actual_signature("CT-001", "wrong1")
        cbd.record_actual_signature("CT-002", "wrong2")
        summary = cbd.get_contract_health_summary()
        assert summary["alert"] is True


class TestForceRevalidateAll:
    def test_revalidate(self):
        cbd = CrossBlueprintContractDrift()
        cbd.register_contract("CT-001", "A", "B", "sig", "/p")
        cbd.record_actual_signature("CT-001", "sig")
        cbd.force_revalidate_all()
        assert cbd.contracts["CT-001"]["status"] == ContractStatus.UNMONITORED
