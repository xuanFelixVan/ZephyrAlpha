# [A_test] module_id: MOD-GOV_e_gov_a2a_failure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gov_a2a_failure
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.agent_spec.a2a_failure import (
    CommunicationFailureEvent,
    on_a2a_failure,
)


class StubA2ACommunication:
    def __init__(self, a2a_id="", from_agent_id="", to_agent_id=""):
        self.a2a_id = a2a_id
        self.from_agent_id = from_agent_id
        self.to_agent_id = to_agent_id


class TestA2ACommunicationLikeProtocol:
    def test_stub_satisfies_protocol(self):
        stub = StubA2ACommunication("a2a-1", "a", "b")
        assert isinstance(stub, CommunicationFailureEvent)


class TestOnA2AFailure:
    def test_returns_escalated_dict(self):
        comm = StubA2ACommunication("a2a-1", "agent-a", "agent-b")
        result = on_a2a_failure(comm, error="connection timeout")
        assert result["escalated"] is True
        assert result["a2a_id"] == "a2a-1"
        assert result["from_agent"] == "agent-a"
        assert result["to_agent"] == "agent-b"
        assert result["error"] == "connection timeout"
        assert result["action"] == "retry_or_degrade"

    def test_empty_communication(self):
        comm = StubA2ACommunication()
        result = on_a2a_failure(comm)
        assert result["escalated"] is True
        assert result["error"] == ""

    def test_no_error_provided(self):
        comm = StubA2ACommunication("a2a-2", "x", "y")
        result = on_a2a_failure(comm)
        assert result["error"] == ""
