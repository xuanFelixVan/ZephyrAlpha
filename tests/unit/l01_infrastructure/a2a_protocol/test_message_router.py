# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_message_router
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Message Router"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, PartType
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.message_router import MessageRouter


class TestMessageRouter:
    def test_route_message(self):
        received = []
        def handler(content, metadata):
            received.append(content)
            return "ok"

        router = MessageRouter()
        router.register_handler(PartType.TEXT, handler)

        msg = A2AMessage(message_id="a2a-msg-r-001", from_agent="a", to_agent="b", task_id="a2a-task-x")
        msg.add_part(PartType.TEXT, "hello world")

        results = router.route(msg)
        assert received == ["hello world"]
