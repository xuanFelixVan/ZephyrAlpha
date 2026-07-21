# [A_test] module_id: MOD-GOV_a2a_schemas | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_a2a_schemas
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_a2a_schemas.py
# [TTL] task_bound

import pytest

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas import (
    A2AMessage,
    A2AMessagePart,
    PartType,
)


class TestPartType:
    def test_enum_values(self):
        assert PartType.TEXT == "text"
        assert PartType.CODE == "code"
        assert PartType.FILE == "file"
        assert PartType.BLUEPRINT_REF == "blueprint_ref"
        assert PartType.GATE_RESULT == "gate_result"
        assert PartType.ERROR == "error"

    def test_enum_from_value(self):
        assert PartType("text") is PartType.TEXT
        assert PartType("error") is PartType.ERROR


class TestA2AMessagePart:
    def test_create_with_defaults(self):
        part = A2AMessagePart(part_type=PartType.TEXT, content="hello")
        assert part.part_type == PartType.TEXT
        assert part.content == "hello"
        assert part.metadata == {}

    def test_create_with_metadata(self):
        meta = {"lang": "python"}
        part = A2AMessagePart(part_type=PartType.CODE, content="print(1)", metadata=meta)
        assert part.metadata == meta

    def test_empty_content(self):
        part = A2AMessagePart(part_type=PartType.TEXT, content="")
        assert part.content == ""


class TestA2AMessage:
    def test_create_valid_message(self):
        msg = A2AMessage(
            message_id="a2a-msg-001",
            from_agent="agent-a",
            to_agent="agent-b",
            task_id="task-1",
        )
        assert msg.message_id == "a2a-msg-001"
        assert msg.from_agent == "agent-a"
        assert msg.to_agent == "agent-b"
        assert msg.parts == []
        assert msg.context_ref is None

    def test_add_part(self):
        msg = A2AMessage(
            message_id="a2a-msg-002",
            from_agent="agent-a",
            to_agent="agent-b",
            task_id="task-2",
        )
        part = msg.add_part(PartType.TEXT, "body text", {"key": "val"})
        assert len(msg.parts) == 1
        assert part.part_type == PartType.TEXT
        assert part.content == "body text"
        assert part.metadata == {"key": "val"}

    def test_add_multiple_parts(self):
        msg = A2AMessage(
            message_id="a2a-msg-003",
            from_agent="agent-a",
            to_agent="agent-b",
            task_id="task-3",
        )
        msg.add_part(PartType.TEXT, "hello")
        msg.add_part(PartType.CODE, "x=1")
        assert len(msg.parts) == 2

    def test_invalid_message_id_pattern(self):
        with pytest.raises(Exception):
            A2AMessage(
                message_id="invalid-id",
                from_agent="a",
                to_agent="b",
                task_id="t",
            )

    def test_context_ref(self):
        msg = A2AMessage(
            message_id="a2a-msg-004",
            from_agent="a",
            to_agent="b",
            task_id="t",
            context_ref="ctx-123",
        )
        assert msg.context_ref == "ctx-123"
