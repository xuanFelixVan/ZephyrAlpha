# [A_test] module_id: SRC-TST-1468 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_risk_registry
# [INVARIANTS] RISKS has 34 entries; get returns None for unknown; mitigate/accept return bool
# [MODIFY-GUARD] src/zephyr/orchestrator/risk_registry.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get/list_all/list_open/mitigate/accept never raise
# [TESTS] tests/test_risk_registry_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

from zephyr.orchestrator.governance.risk_registry import (
    RISKS,
    ConflictResolution,
    Risk,
    RiskRegistry,
    RiskSeverity,
    RiskStatus,
)


class TestRiskStatusEnum:
    def test_values(self):
        assert RiskStatus.OPEN == "open"
        assert RiskStatus.MITIGATED == "mitigated"
        assert RiskStatus.ACCEPTED == "accepted"
        assert RiskStatus.CLOSED == "closed"


class TestRiskSeverityEnum:
    def test_values(self):
        assert RiskSeverity.LOW == "LOW"
        assert RiskSeverity.MEDIUM == "MEDIUM"
        assert RiskSeverity.HIGH == "HIGH"
        assert RiskSeverity.CRITICAL == "CRITICAL"


class TestRiskModel:
    def test_creation_with_required_fields(self):
        risk = Risk(risk_id="R-TEST", severity=RiskSeverity.HIGH)
        assert risk.risk_id == "R-TEST"
        assert risk.severity == RiskSeverity.HIGH

    def test_default_values(self):
        risk = Risk(risk_id="R-X", severity=RiskSeverity.LOW)
        assert risk.status == RiskStatus.OPEN
        assert risk.description == ""
        assert risk.mitigation_plan == ""
        assert risk.affected_contracts == []
        assert isinstance(risk.created_at, datetime)
        assert isinstance(risk.updated_at, datetime)


class TestConflictResolutionModel:
    def test_creation(self):
        cr = ConflictResolution(
            conflict_id="C-1",
            contract_a="CT-A",
            contract_b="CT-B",
            resolution="A wins",
        )
        assert cr.conflict_id == "C-1"
        assert cr.contract_a == "CT-A"
        assert cr.contract_b == "CT-B"
        assert cr.resolution == "A wins"

    def test_optional_fields(self):
        cr = ConflictResolution(
            conflict_id="C-2",
            contract_a="CT-A",
            contract_b="CT-B",
            resolution="merge",
        )
        assert cr.rationale == ""
        assert cr.resolved_by == ""


class TestRiskRegistryInstantiation:
    def test_create_instance(self):
        reg = RiskRegistry()
        assert reg is not None


class TestGet:
    def test_known_risk(self):
        reg = RiskRegistry()
        risk = reg.get("R-MOD-1")
        assert risk is not None
        assert risk.risk_id == "R-MOD-1"

    def test_unknown_risk(self):
        reg = RiskRegistry()
        assert reg.get("R-MOD-999") is None

    def test_empty_string(self):
        reg = RiskRegistry()
        assert reg.get("") is None


class TestListAll:
    def test_returns_list(self):
        reg = RiskRegistry()
        result = reg.list_all()
        assert isinstance(result, list)

    def test_returns_all_risks(self):
        reg = RiskRegistry()
        result = reg.list_all()
        assert len(result) == len(RISKS)


class TestListOpen:
    def test_returns_only_open(self):
        reg = RiskRegistry()
        result = reg.list_open()
        for risk in result:
            assert risk.status == RiskStatus.OPEN

    def test_all_default_open(self):
        reg = RiskRegistry()
        result = reg.list_open()
        assert len(result) == len(RISKS)


class TestMitigate:
    def test_mitigate_known_risk(self):
        reg = RiskRegistry()
        result = reg.mitigate("R-MOD-1")
        assert result is True
        risk = reg.get("R-MOD-1")
        assert risk.status == RiskStatus.MITIGATED

    def test_mitigate_unknown_risk(self):
        reg = RiskRegistry()
        result = reg.mitigate("R-MOD-999")
        assert result is False

    def test_mitigate_updates_timestamp(self):
        reg = RiskRegistry()
        risk_before = reg.get("R-MOD-2")
        ts_before = risk_before.updated_at
        reg.mitigate("R-MOD-2")
        risk_after = reg.get("R-MOD-2")
        assert risk_after.updated_at >= ts_before


class TestAccept:
    def test_accept_known_risk(self):
        reg = RiskRegistry()
        result = reg.accept("R-MOD-3")
        assert result is True
        risk = reg.get("R-MOD-3")
        assert risk.status == RiskStatus.ACCEPTED

    def test_accept_unknown_risk(self):
        reg = RiskRegistry()
        result = reg.accept("R-MOD-999")
        assert result is False

    def test_accept_updates_timestamp(self):
        reg = RiskRegistry()
        risk_before = reg.get("R-MOD-4")
        ts_before = risk_before.updated_at
        reg.accept("R-MOD-4")
        risk_after = reg.get("R-MOD-4")
        assert risk_after.updated_at >= ts_before


class TestRisksData:
    def test_has_34_entries(self):
        assert len(RISKS) == 34

    def test_keys_match_risk_ids(self):
        for key, risk in RISKS.items():
            assert risk.risk_id == key

    def test_all_default_medium_severity(self):
        for risk in RISKS.values():
            assert risk.severity == RiskSeverity.MEDIUM


class TestBoundary:
    def test_mitigate_then_accept(self):
        reg = RiskRegistry()
        reg.mitigate("R-MOD-5")
        reg.accept("R-MOD-5")
        risk = reg.get("R-MOD-5")
        assert risk.status == RiskStatus.ACCEPTED

    def test_list_open_after_mitigate(self):
        reg = RiskRegistry()
        reg.mitigate("R-MOD-6")
        open_risks = reg.list_open()
        for risk in open_risks:
            assert risk.risk_id != "R-MOD-6"

    def test_list_all_returns_new_list(self):
        reg = RiskRegistry()
        a = reg.list_all()
        b = reg.list_all()
        assert a is not b
