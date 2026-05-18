# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_a2a_schemas
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: A2A Message Schemas"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_schemas import (
    A2AMessage, A2AMessagePart, PartType,
)


class TestA2ASchemas:
    def test_create_message(self):
        msg = A2AMessage(message_id="a2a-msg-test-001", from_agent="agent-a", to_agent="agent-b", task_id="a2a-task-x")
        assert msg.from_agent == "agent-a"
        assert msg.to_agent == "agent-b"

    def test_add_text_part(self):
        msg = A2AMessage(message_id="a2a-msg-test-002", from_agent="agent-a", to_agent="agent-b", task_id="a2a-task-x")
        msg.add_part(PartType.TEXT, "Hello")
        assert len(msg.parts) == 1
        assert msg.parts[0].part_type == PartType.TEXT

    def test_add_code_part(self):
        msg = A2AMessage(message_id="a2a-msg-test-003", from_agent="agent-a", to_agent="agent-b", task_id="a2a-task-x")
        msg.add_part(PartType.CODE, "print('hi')", {"lang": "python"})
        assert msg.parts[0].part_type == PartType.CODE
