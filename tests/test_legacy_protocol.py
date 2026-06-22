# [A_test] module_id: SRC-TST-1222 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3
# [MODULE] tests.test_legacy_protocol
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self

from __future__ import annotations

import pytest

legacy_protocol = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.legacy_protocol",
    reason="legacy_protocol module not available",
)


class TestMessageType:
    def test_enum_values(self):
        assert legacy_protocol.MessageType.QUERY.value == "QUERY"
        assert legacy_protocol.MessageType.COMMAND.value == "COMMAND"
        assert legacy_protocol.MessageType.NOTIFY.value == "NOTIFY"
        assert legacy_protocol.MessageType.DELEGATE.value == "DELEGATE"
        assert legacy_protocol.MessageType.RESPONSE.value == "RESPONSE"

    def test_enum_count(self):
        assert len(legacy_protocol.MessageType) == 5


class TestA2ACommunication:
    def test_instantiation_with_required_fields(self):
        msg = legacy_protocol.A2ACommunication(
            a2a_id="id1",
            from_agent_id="agent_a",
            to_agent_id="agent_b",
        )
        assert msg.a2a_id == "id1"
        assert msg.from_agent_id == "agent_a"
        assert msg.to_agent_id == "agent_b"

    def test_default_values(self):
        msg = legacy_protocol.A2ACommunication(
            a2a_id="id2",
            from_agent_id="a",
            to_agent_id="b",
        )
        assert msg.message_type == legacy_protocol.MessageType.QUERY
        assert msg.payload_size == 0
        assert msg.transfer_token_count == 0
        assert msg.status == "PENDING"
        assert msg.timestamp != ""

    def test_custom_message_type(self):
        msg = legacy_protocol.A2ACommunication(
            a2a_id="id3",
            from_agent_id="a",
            to_agent_id="b",
            message_type=legacy_protocol.MessageType.COMMAND,
        )
        assert msg.message_type == legacy_protocol.MessageType.COMMAND

    def test_empty_agent_ids(self):
        msg = legacy_protocol.A2ACommunication(
            a2a_id="id4",
            from_agent_id="",
            to_agent_id="",
        )
        assert msg.from_agent_id == ""
        assert msg.to_agent_id == ""
