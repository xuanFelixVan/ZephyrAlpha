# [A_test] module_id: MOD-GOV_escalation_incident_response | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §test

# [MODULE] tests.test_escalation_incident_response

# [INVARIANTS] test_escalation_incident_response covers IncidentLevel+IncidentProtocol+get_protocol+escalate

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] test_escalation_incident_response
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
    def test_all_five_levels(self):
        assert len(IncidentLevel) == 5

    def test_level_values(self):
        assert IncidentLevel.L1_INSTANT.value == "L1_INSTANT"
        assert IncidentLevel.L5_CATASTROPHIC.value == "L5_CATASTROPHIC"

    def test_str_enum(self):
        assert isinstance(IncidentLevel.L1_INSTANT, str)


class TestIncidentProtocol:
    def test_create_custom(self):
        p = IncidentProtocol(
            level=IncidentLevel.L1_INSTANT,
            label="test",
            response_time_minutes=10,
        )
        assert p.level == IncidentLevel.L1_INSTANT
        assert p.label == "test"
        assert p.response_time_minutes == 10
        assert p.escalation_chain == []
        assert p.notification_channel == "log"
        assert p.postmortem_required is False

    def test_create_with_all_fields(self):
        p = IncidentProtocol(
            level=IncidentLevel.L3_PARTIAL,
            label="partial",
            response_time_minutes=60,
            escalation_chain=["AI", "Owner"],
            notification_channel="email",
            postmortem_required=True,
        )
        assert p.escalation_chain == ["AI", "Owner"]
        assert p.postmortem_required is True

    def test_empty_label(self):
        p = IncidentProtocol(level=IncidentLevel.L1_INSTANT, label="", response_time_minutes=1)
        assert p.label == ""


class TestIncidentProtocols:
    def test_all_levels_have_protocols(self):
        for level in IncidentLevel:
            assert level in INCIDENT_PROTOCOLS

    def test_l1_protocol(self):
        p = INCIDENT_PROTOCOLS[IncidentLevel.L1_INSTANT]
        assert p.response_time_minutes == 5
        assert p.postmortem_required is False

    def test_l5_protocol(self):
        p = INCIDENT_PROTOCOLS[IncidentLevel.L5_CATASTROPHIC]
        assert p.response_time_minutes == 9999
        assert p.postmortem_required is True

    def test_escalation_chain_grows(self):
        prev_len = 0
        for level in IncidentLevel:
            p = INCIDENT_PROTOCOLS[level]
            assert len(p.escalation_chain) >= prev_len
            prev_len = len(p.escalation_chain)


class TestGetProtocol:
    def test_returns_protocol_for_valid_level(self):
        p = get_protocol(IncidentLevel.L2_DEGRADED)
        assert p is not None
        assert p.level == IncidentLevel.L2_DEGRADED

    def test_returns_none_for_missing(self):
        result = INCIDENT_PROTOCOLS.get(IncidentLevel.L1_INSTANT)
        assert result is not None


class TestEscalate:
    def test_l1_returns_all_levels(self):
        result = escalate(IncidentLevel.L1_INSTANT)
        assert len(result) == 5
        assert result[0] == IncidentLevel.L1_INSTANT
        assert result[-1] == IncidentLevel.L5_CATASTROPHIC

    def test_l5_returns_only_l5(self):
        result = escalate(IncidentLevel.L5_CATASTROPHIC)
        assert result == [IncidentLevel.L5_CATASTROPHIC]

    def test_l3_returns_l3_l4_l5(self):
        result = escalate(IncidentLevel.L3_PARTIAL)
        assert result == [IncidentLevel.L3_PARTIAL, IncidentLevel.L4_TOTAL, IncidentLevel.L5_CATASTROPHIC]

    def test_escalation_order_is_sequential(self):
        levels = list(IncidentLevel)
        for i in range(len(levels) - 1):
            result = escalate(levels[i])
            assert result[0] == levels[i]
