# [A_test] module_id: MOD-GOV_financial_compliance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-385 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_financial_compliance
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] FRAMEWORK_DIMENSIONS counts match enum sizes
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_financial_compliance.py
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
    def test_all_layers(self):
        expected = {"L1_PREVENTATIVE", "L2_DETECTIVE", "L3_CORRECTIVE"}
        actual = {l.value for l in ComplianceLayer}
        assert actual == expected


class TestSafeguard:
    def test_all_safeguards(self):
        assert len(Safeguard) == 7

    def test_safeguard_labels_complete(self):
        for s in Safeguard:
            assert s in SAFEGUARD_LABELS


class TestProtocol:
    def test_all_protocols(self):
        expected = {"CLIENT_STATEMENT", "MRM", "RECORD_KEEPING", "INCIDENT_NOTIFICATION"}
        actual = {p.value for p in Protocol}
        assert actual == expected


class TestProtocolDef:
    def test_creation_defaults(self):
        pd = ProtocolDef(name=Protocol.MRM, description="test")
        assert pd.owner == "Owner"
        assert pd.review_date is None


class TestGetProtocol:
    def test_known_protocol(self):
        result = get_protocol(Protocol.MRM)
        assert result is not None
        assert result.name == Protocol.MRM

    def test_all_protocols_retrievable(self):
        for p in Protocol:
            assert get_protocol(p) is not None


class TestGetSafeguard:
    def test_known_safeguard(self):
        result = get_safeguard(Safeguard.S1_ACCESS_CONTROL)
        assert "访问控制" in result

    def test_all_safeguards_retrievable(self):
        for s in Safeguard:
            label = get_safeguard(s)
            assert label != ""


class TestFrameworkDimensions:
    def test_compliance_layers_count(self):
        assert FRAMEWORK_DIMENSIONS["compliance_layers"] == len(ComplianceLayer)

    def test_safeguards_count(self):
        assert FRAMEWORK_DIMENSIONS["safeguards"] == len(Safeguard)

    def test_protocols_count(self):
        assert FRAMEWORK_DIMENSIONS["protocols"] == len(Protocol)


class TestBoundary:
    def test_protocol_defs_have_descriptions(self):
        for p, pd in PROTOCOL_DEFS.items():
            assert pd.description != ""

    def test_safeguard_labels_non_empty(self):
        for s, label in SAFEGUARD_LABELS.items():
            assert label != ""
