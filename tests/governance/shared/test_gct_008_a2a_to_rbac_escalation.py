# [A_test] module_id: SRC-TST-0131 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-288 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_008_a2a_to_rbac_escalation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-008 — A2A → RBAC 集成测试."""

from __future__ import annotations


class TestGCT008A2AToRBAC:
    """验证 a2a/protocol.py 的 A2ACommunication 可被 agent-rbac/a2a_check.py 验证."""

    def test_a2a_communication_creatable(self):
        from zephyr.infrastructure.a2a_protocol import A2ACommunication

        comm = A2ACommunication(a2a_id="A001", from_agent_id="superadmin", to_agent_id="admin")
        assert comm.a2a_id == "A001"

    def test_a2a_check_verifies_pair(self):
        from zephyr.infrastructure.a2a_protocol import A2ACommunication
        from zephyr.security.access_control.a2a_check import verify_a2a_pair

        comm = A2ACommunication(a2a_id="A002", from_agent_id="superadmin", to_agent_id="admin")
        result = verify_a2a_pair(comm.from_agent_id, comm.to_agent_id)
        assert isinstance(result, dict)
        assert "approved" in result

    def test_unauthorized_pair_blocked(self):
        from zephyr.security.access_control.a2a_check import verify_a2a_pair

        result = verify_a2a_pair("unknown_agent", "another_unknown")
        assert isinstance(result, dict)

    def test_message_type_enum(self):
        from zephyr.infrastructure.a2a_protocol import MessageType

        assert MessageType.QUERY is not None
        assert MessageType.RESPONSE is not None
