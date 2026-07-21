# [A_test] module_id: MOD-GOV_a2a_failure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_a2a_failure
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_a2a_failure.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.agent_spec.a2a_failure import CommunicationFailureEvent, on_a2a_failure


class _StubCommunication:
    def __init__(self, a2a_id: str = "", from_agent_id: str = "", to_agent_id: str = ""):
        self.a2a_id = a2a_id
        self.from_agent_id = from_agent_id
        self.to_agent_id = to_agent_id


class TestCommunicationFailureEventProtocol:
    def test_stub_satisfies_protocol(self):
        stub = _StubCommunication("a2a-1", "agent-a", "agent-b")
        assert isinstance(stub, CommunicationFailureEvent)

    def test_stub_with_empty_fields_satisfies_protocol(self):
        stub = _StubCommunication()
        assert isinstance(stub, CommunicationFailureEvent)
        assert stub.a2a_id == ""
        assert stub.from_agent_id == ""
        assert stub.to_agent_id == ""


class TestOnA2AFailure:
    def test_returns_escalated_dict_with_all_fields(self):
        comm = _StubCommunication("a2a-42", "sender", "receiver")
        result = on_a2a_failure(comm, error="connection refused")
        assert result["escalated"] is True
        assert result["a2a_id"] == "a2a-42"
        assert result["from_agent"] == "sender"
        assert result["to_agent"] == "receiver"
        assert result["error"] == "connection refused"
        assert result["action"] == "retry_or_degrade"
        assert "ticket_id" in result

    def test_default_error_is_empty_string(self):
        comm = _StubCommunication("a2a-0", "x", "y")
        result = on_a2a_failure(comm)
        assert result["error"] == ""

    def test_empty_communication_fields(self):
        comm = _StubCommunication()
        result = on_a2a_failure(comm, error="timeout")
        assert result["escalated"] is True
        assert result["a2a_id"] == ""
        assert result["from_agent"] == ""
        assert result["to_agent"] == ""
        assert result["error"] == "timeout"

    def test_ticket_id_contains_a2a_id(self):
        comm = _StubCommunication("a2a-99", "a", "b")
        result = on_a2a_failure(comm)
        assert "a2a-99" in result["ticket_id"]

    def test_ticket_id_for_empty_a2a_id(self):
        comm = _StubCommunication("", "a", "b")
        result = on_a2a_failure(comm)
        assert "unknown" in result["ticket_id"] or "ESC-A2A-" in result["ticket_id"]


class TestOnA2AFailureBoundary:
    def test_unicode_error_message(self):
        comm = _StubCommunication("a2a-u", "α", "β")
        result = on_a2a_failure(comm, error="连接超时 🔥")
        assert result["error"] == "连接超时 🔥"
        assert result["from_agent"] == "α"

    def test_very_long_error_message(self):
        long_error = "x" * 10000
        comm = _StubCommunication("a2a-long", "a", "b")
        result = on_a2a_failure(comm, error=long_error)
        assert result["error"] == long_error

    def test_special_characters_in_ids(self):
        comm = _StubCommunication("a2a-<script>", "a&b", "c|d")
        result = on_a2a_failure(comm, error="fail")
        assert result["a2a_id"] == "a2a-<script>"
        assert result["from_agent"] == "a&b"
        assert result["to_agent"] == "c|d"
