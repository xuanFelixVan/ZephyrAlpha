# [A_test] module_id: MOD-GOV_escalation_gov_a2a_failure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_gov_a2a_failure
# [INVARIANTS] none
# [MODIFY-GUARD] governance/a2a_failure.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_escalation_gov_a2a_failure.py -q
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass

from zephyr.governance.agent_spec.a2a_failure import (
    _A2ACommunicationLike,
    on_a2a_failure,
)


@dataclass
class StubCommunication:
    a2a_id: str = ""
    from_agent_id: str = ""
    to_agent_id: str = ""


class NotACommunication:
    other_field: str = "x"


class TestA2ACommunicationLikeProtocol:
    def test_stub_satisfies_protocol(self):
        comm = StubCommunication(a2a_id="A1", from_agent_id="FA", to_agent_id="TA")
        assert isinstance(comm, _A2ACommunicationLike)

    def test_non_conforming_does_not_satisfy(self):
        obj = NotACommunication()
        assert not isinstance(obj, _A2ACommunicationLike)


class TestOnA2AFailure:
    def test_basic_failure(self):
        comm = StubCommunication(a2a_id="A2A-001", from_agent_id="agent-A", to_agent_id="agent-B")
        result = on_a2a_failure(comm, error="timeout")
        assert result["escalated"] is True
        assert result["a2a_id"] == "A2A-001"
        assert result["from_agent"] == "agent-A"
        assert result["to_agent"] == "agent-B"
        assert result["action"] == "retry_or_degrade"
        assert result["ticket_id"] == "ESC-A2A-A2A-001"
        assert result["error"] == "timeout"

    def test_default_empty_error(self):
        comm = StubCommunication(a2a_id="A2A-002")
        result = on_a2a_failure(comm)
        assert result["error"] == ""

    def test_empty_ids(self):
        comm = StubCommunication()
        result = on_a2a_failure(comm, error="connection lost")
        assert result["a2a_id"] == ""
        assert result["from_agent"] == ""
        assert result["to_agent"] == ""
        assert result["ticket_id"] == "ESC-A2A-"
        assert result["error"] == "connection lost"

    def test_long_error_message(self):
        comm = StubCommunication(a2a_id="A2A-LONG")
        long_error = "e" * 5000
        result = on_a2a_failure(comm, error=long_error)
        assert result["error"] == long_error

    def test_result_contains_all_keys(self):
        comm = StubCommunication(a2a_id="A2A-K")
        result = on_a2a_failure(comm, error="test")
        expected_keys = {"escalated", "a2a_id", "from_agent", "to_agent", "action", "ticket_id", "error"}
        assert set(result.keys()) == expected_keys
