# [A_test] module_id: MOD-GOV_a2a_governance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §governance
# [MODULE] tests.test_a2a_governance
# [INVARIANTS] GovernanceAdapter.verify_pair必须返回A2AGovernanceRecord; Phase4Hold.can_proceed仅Phase4为True
# [MODIFY-GUARD] 仅当a2a governance公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_a2a_governance.py -q
# [TTL] task_bound


from zephyr.infrastructure.a2a_protocol.governance.governance_adapter import (
    A2AGovernanceRecord,
    GovernanceAdapter,
)
from zephyr.infrastructure.a2a_protocol.governance.phase_hold import (
    Phase4Hold,
)
from zephyr.infrastructure.a2a_protocol.governance.protocol import (
    A2ACommunication,
    MessageType,
)


class TestA2AGovernanceRecord:
    def test_default_construction(self):
        record = A2AGovernanceRecord(
            agent_pair=("a", "b"),
            action="verify",
        )
        assert record.agent_pair == ("a", "b")
        assert record.action == "verify"
        assert record.granted is False
        assert record.escalation_level == ""
        assert record.audit_id == ""
        assert record.metadata == {}


class TestGovernanceAdapter:
    def test_instantiation(self):
        adapter = GovernanceAdapter()
        assert adapter is not None

    def test_verify_pair_allowed(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair("orchestrator", "worker")
        assert record.granted is True

    def test_verify_pair_allowed_reverse(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair("worker", "orchestrator")
        assert record.granted is True

    def test_verify_pair_denied(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair("unknown", "stranger")
        assert record.granted is False

    def test_verify_pair_auditor_any(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair("auditor", "any")
        assert record.granted is True

    def test_escalate_if_needed_granted(self):
        adapter = GovernanceAdapter()
        record = A2AGovernanceRecord(
            agent_pair=("orchestrator", "worker"),
            action="verify",
            granted=True,
        )
        result = adapter.escalate_if_needed(record)
        assert result.escalation_level == ""

    def test_escalate_if_needed_denied(self):
        adapter = GovernanceAdapter()
        record = A2AGovernanceRecord(
            agent_pair=("unknown", "stranger"),
            action="verify",
            granted=False,
        )
        result = adapter.escalate_if_needed(record, severity="CRITICAL")
        assert result.escalation_level == "CRITICAL"

    def test_audit_communication(self):
        adapter = GovernanceAdapter()
        record = A2AGovernanceRecord(
            agent_pair=("a", "b"),
            action="test",
        )
        result = adapter.audit_communication(record, session_id="sess-123")
        assert result.audit_id.startswith("a2a-")
        assert "sess-123" in result.audit_id


class TestPhase4Hold:
    def test_instantiation(self):
        hold = Phase4Hold()
        assert hold.hold_active is True
        assert hold.hold_since != ""

    def test_check(self):
        hold = Phase4Hold()
        result = hold.check()
        assert result["hold_active"] is True
        assert "reason" in result
        assert "hold_since" in result

    def test_can_proceed_phase4(self):
        hold = Phase4Hold()
        assert hold.can_proceed("Phase4") is True
        assert hold.can_proceed("phase4") is True
        assert hold.can_proceed("4") is True

    def test_cannot_proceed_other_phases(self):
        hold = Phase4Hold()
        assert hold.can_proceed("Phase3") is False
        assert hold.can_proceed("phase2") is False
        assert hold.can_proceed("1") is False


class TestMessageType:
    def test_values(self):
        assert MessageType.QUERY.value == "QUERY"
        assert MessageType.COMMAND.value == "COMMAND"
        assert MessageType.NOTIFY.value == "NOTIFY"
        assert MessageType.DELEGATE.value == "DELEGATE"
        assert MessageType.RESPONSE.value == "RESPONSE"


class TestA2ACommunication:
    def test_construction(self):
        comm = A2ACommunication(
            a2a_id="a2a-001",
            from_agent_id="agent-1",
            to_agent_id="agent-2",
        )
        assert comm.a2a_id == "a2a-001"
        assert comm.message_type == MessageType.QUERY
        assert comm.status == "PENDING"

    def test_custom_values(self):
        comm = A2ACommunication(
            a2a_id="a2a-002",
            from_agent_id="agent-1",
            to_agent_id="agent-2",
            message_type=MessageType.COMMAND,
            payload_size=1024,
        )
        assert comm.message_type == MessageType.COMMAND
        assert comm.payload_size == 1024
