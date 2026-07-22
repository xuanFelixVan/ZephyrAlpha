# [A_test] module_id: MOD-GOV_incident_response | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-396 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_incident_response
# [INVARIANTS] INCIDENT_PROTOCOLS covers all IncidentLevel values; escalate returns ordered list
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_incident_response.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.incident_response import (
    INCIDENT_PROTOCOLS,
    IncidentLevel,
    IncidentProtocol,
    escalate,
    get_protocol,
)


class TestIncidentLevel:
    def test_all_levels(self):
        expected = {"L1_INSTANT", "L2_DEGRADED", "L3_PARTIAL", "L4_TOTAL", "L5_CATASTROPHIC"}
        actual = {l.value for l in IncidentLevel}
        assert actual == expected


class TestIncidentProtocol:
    def test_creation_defaults(self):
        ip = IncidentProtocol(
            level=IncidentLevel.L1_INSTANT,
            label="test",
            response_time_minutes=5,
        )
        assert ip.escalation_chain == []
        assert ip.notification_channel == "log"
        assert ip.postmortem_required is False


class TestIncidentProtocols:
    def test_all_levels_have_protocols(self):
        for level in IncidentLevel:
            assert level in INCIDENT_PROTOCOLS

    def test_l5_catastrophic_requires_postmortem(self):
        assert INCIDENT_PROTOCOLS[IncidentLevel.L5_CATASTROPHIC].postmortem_required is True

    def test_l1_does_not_require_postmortem(self):
        assert INCIDENT_PROTOCOLS[IncidentLevel.L1_INSTANT].postmortem_required is False

    def test_escalation_chain_grows(self):
        l1 = INCIDENT_PROTOCOLS[IncidentLevel.L1_INSTANT]
        l5 = INCIDENT_PROTOCOLS[IncidentLevel.L5_CATASTROPHIC]
        assert len(l5.escalation_chain) > len(l1.escalation_chain)


class TestGetProtocol:
    def test_known_level(self):
        result = get_protocol(IncidentLevel.L1_INSTANT)
        assert result is not None
        assert result.level == IncidentLevel.L1_INSTANT

    def test_all_levels_retrievable(self):
        for level in IncidentLevel:
            assert get_protocol(level) is not None


class TestEscalate:
    def test_escalate_from_l1(self):
        result = escalate(IncidentLevel.L1_INSTANT)
        assert IncidentLevel.L1_INSTANT in result
        assert IncidentLevel.L5_CATASTROPHIC in result
        assert len(result) == 5

    def test_escalate_from_l5(self):
        result = escalate(IncidentLevel.L5_CATASTROPHIC)
        assert result == [IncidentLevel.L5_CATASTROPHIC]

    def test_escalate_from_l3(self):
        result = escalate(IncidentLevel.L3_PARTIAL)
        assert result[0] == IncidentLevel.L3_PARTIAL
        assert result[-1] == IncidentLevel.L5_CATASTROPHIC


class TestBoundary:
    def test_response_times_increase(self):
        times = [INCIDENT_PROTOCOLS[l].response_time_minutes for l in IncidentLevel]
        for i in range(len(times) - 1):
            assert times[i] <= times[i + 1]

    def test_all_protocols_have_labels(self):
        for level, proto in INCIDENT_PROTOCOLS.items():
            assert proto.label != ""
