# [A_test] module_id: MOD-GOV_push_notifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_push_notifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_push_notifier.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer2_communication.push_notifier import PushNotifier


class TestPushNotifier:
    def test_create(self):
        pn = PushNotifier()
        assert pn.subscribers == {}

    def test_subscribe_and_notify(self):
        pn = PushNotifier()
        received = []
        pn.subscribe("agent-a", lambda event, data: received.append((event, data)))
        count = pn.notify("agent-a", "task_done", {"task_id": "t1"})
        assert count == 1
        assert len(received) == 1
        assert received[0] == ("task_done", {"task_id": "t1"})

    def test_notify_no_subscribers(self):
        pn = PushNotifier()
        count = pn.notify("agent-x", "event", {})
        assert count == 0

    def test_unsubscribe(self):
        pn = PushNotifier()
        cb = lambda e, d: None
        pn.subscribe("agent-a", cb)
        pn.unsubscribe("agent-a", cb)
        count = pn.notify("agent-a", "event")
        assert count == 0

    def test_multiple_subscribers(self):
        pn = PushNotifier()
        r1, r2 = [], []
        pn.subscribe("agent-a", lambda e, d: r1.append(e))
        pn.subscribe("agent-a", lambda e, d: r2.append(e))
        count = pn.notify("agent-a", "evt")
        assert count == 2
        assert r1 == ["evt"]
        assert r2 == ["evt"]

    def test_notify_default_data(self):
        pn = PushNotifier()
        received = []
        pn.subscribe("agent-a", lambda e, d: received.append(d))
        pn.notify("agent-a", "evt")
        assert received == [{}]

    def test_unsubscribe_nonexistent(self):
        pn = PushNotifier()
        pn.unsubscribe("agent-x", lambda e, d: None)
