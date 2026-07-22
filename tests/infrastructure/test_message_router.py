# [A_test] module_id: MOD-GOV_message_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_message_router
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_message_router.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas import (
    A2AMessage,
    A2AMessagePart,
    PartType,
)
from zephyr.infrastructure.a2a_protocol.layer2_communication.message_router import MessageRouter


def _make_message(*part_specs):
    parts = [A2AMessagePart(part_type=pt, content=content, metadata=meta) for pt, content, meta in part_specs]
    return A2AMessage(
        message_id="a2a-msg-router-1",
        from_agent="agent-a",
        to_agent="agent-b",
        task_id="task-r1",
        parts=parts,
    )


class TestMessageRouter:
    def test_create(self):
        router = MessageRouter()
        assert router._handlers == {}

    def test_register_and_route(self):
        router = MessageRouter()
        collected = []
        router.register_handler(PartType.TEXT, lambda content, meta: collected.append(content))
        msg = _make_message((PartType.TEXT, "hello", {}))
        results = router.route(msg)
        assert "text" in results
        assert len(results["text"]) == 1
        assert collected == ["hello"]

    def test_route_with_message_param(self):
        router = MessageRouter()
        router.register_handler(PartType.TEXT, lambda msg: msg.message_id)
        msg = _make_message((PartType.TEXT, "hello", {}))
        results = router.route(msg)
        assert results["text"] == ["a2a-msg-router-1"]

    def test_route_no_handlers(self):
        router = MessageRouter()
        msg = _make_message((PartType.CODE, "x=1", {}))
        results = router.route(msg)
        assert results["code"] == []

    def test_route_handler_exception(self):
        router = MessageRouter()

        def bad_handler(content, meta):
            raise ValueError("boom")

        router.register_handler(PartType.TEXT, bad_handler)
        msg = _make_message((PartType.TEXT, "hello", {}))
        results = router.route(msg)
        assert len(results["text"]) == 1
        assert "error" in results["text"][0]

    def test_multiple_handlers_same_type(self):
        router = MessageRouter()
        router.register_handler(PartType.TEXT, lambda c, m: "h1")
        router.register_handler(PartType.TEXT, lambda c, m: "h2")
        msg = _make_message((PartType.TEXT, "hello", {}))
        results = router.route(msg)
        assert len(results["text"]) == 2

    def test_route_empty_parts(self):
        router = MessageRouter()
        msg = A2AMessage(
            message_id="a2a-msg-router-2",
            from_agent="a",
            to_agent="b",
            task_id="t",
        )
        results = router.route(msg)
        assert results == {}
