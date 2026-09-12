# [A_test] module_id: MOD-GOV_audit_financial_compliance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_financial_compliance
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

from zephyr.governance.financial_governance.financial_compliance import (
    FRAMEWORK_DIMENSIONS,
    PROTOCOL_DEFS,
    SAFEGUARD_LABELS,
    ComplianceLayer,
    Protocol,
    ProtocolDef,
    Safeguard,
    get_protocol,
    get_safeguard,
)


class TestComplianceLayer:
    def test_all_layers_exist(self):
        assert ComplianceLayer.L1_PREVENTATIVE.value == "L1_PREVENTATIVE"
        assert ComplianceLayer.L2_DETECTIVE.value == "L2_DETECTIVE"
        assert ComplianceLayer.L3_CORRECTIVE.value == "L3_CORRECTIVE"

    def test_layer_count(self):
        assert len(ComplianceLayer) == 3


class TestSafeguard:
    def test_all_safeguards_exist(self):
        expected = [
            "S1_ACCESS_CONTROL",
            "S2_DATA_PROTECTION",
            "S3_AUDIT_TRAIL",
            "S4_INCIDENT_RESPONSE",
            "S5_BUSINESS_CONTINUITY",
            "S6_MODEL_RISK",
            "S7_INSIDER_THREAT",
        ]
        for name in expected:
            assert hasattr(Safeguard, name)

    def test_safeguard_count(self):
        assert len(Safeguard) == 7

    def test_safeguard_labels_complete(self):
        for safeguard in Safeguard:
            assert safeguard in SAFEGUARD_LABELS
            assert isinstance(SAFEGUARD_LABELS[safeguard], str)
            assert len(SAFEGUARD_LABELS[safeguard]) > 0


class TestProtocol:
    def test_all_protocols_exist(self):
        assert Protocol.CLIENT_STATEMENT.value == "CLIENT_STATEMENT"
        assert Protocol.MRM.value == "MRM"
        assert Protocol.RECORD_KEEPING.value == "RECORD_KEEPING"
        assert Protocol.INCIDENT_NOTIFICATION.value == "INCIDENT_NOTIFICATION"

    def test_protocol_count(self):
        assert len(Protocol) == 4

    def test_protocol_defs_complete(self):
        for protocol in Protocol:
            assert protocol in PROTOCOL_DEFS
            assert isinstance(PROTOCOL_DEFS[protocol], ProtocolDef)
            assert PROTOCOL_DEFS[protocol].name == protocol


class TestGetProtocol:
    def test_returns_valid_protocol(self):
        result = get_protocol(Protocol.MRM)
        assert result is not None
        assert result.name == Protocol.MRM
        assert isinstance(result.description, str)

    def test_returns_none_for_missing(self):
        result = get_protocol("NONEXISTENT")
        assert result is None


class TestGetSafeguard:
    def test_returns_label(self):
        result = get_safeguard(Safeguard.S1_ACCESS_CONTROL)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_string_for_unknown(self):
        result = get_safeguard("unknown_value")
        assert isinstance(result, str)


class TestFrameworkDimensions:
    def test_dimensions_match_enums(self):
        assert FRAMEWORK_DIMENSIONS["compliance_layers"] == len(ComplianceLayer)
        assert FRAMEWORK_DIMENSIONS["safeguards"] == len(Safeguard)
        assert FRAMEWORK_DIMENSIONS["protocols"] == len(Protocol)
