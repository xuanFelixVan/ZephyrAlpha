# [A_test] module_id: MOD-GOV_infra_observer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_observer

# [INVARIANTS] subscribe后emit必调用;once只调用一次;线程安全

# [MODIFY-GUARD] observer.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] frozen

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_infra_observer.py -q
# [TTL] task_bound

from zephyr.shared.infra.observer import (
    EventType,
    Observer,
)


class TestEventType:
    def test_members(self):
        assert EventType.FILE_EVENT.value == "file_event"
        assert EventType.TASK_EVENT.value == "task_event"
        assert EventType.TIME_EVENT.value == "time_event"
        assert EventType.MANUAL_EVENT.value == "manual_event"
        assert EventType.METRIC_EVENT.value == "metric_event"


class TestObserver:
    def test_subscribe_and_emit(self):
        bus = Observer()
        received = []
        bus.subscribe(EventType.FILE_EVENT, lambda et, p: received.append((et, p)))
        called = bus.emit(EventType.FILE_EVENT, {"path": "test.md"})
        assert called == 1
        assert len(received) == 1
        assert received[0][0] == EventType.FILE_EVENT
        assert received[0][1] == {"path": "test.md"}

    def test_emit_no_subscribers(self):
        bus = Observer()
        called = bus.emit(EventType.FILE_EVENT)
        assert called == 0

    def test_multiple_subscribers(self):
        bus = Observer()
        count = [0]

        def handler(et, p):
            count[0] += 1

        bus.subscribe(EventType.TASK_EVENT, handler)
        bus.subscribe(EventType.TASK_EVENT, handler)
        called = bus.emit(EventType.TASK_EVENT)
        assert called == 1
        assert count[0] == 1

    def test_unsubscribe(self):
        bus = Observer()
        received = []
        handler = lambda et, p: received.append(1)
        bus.subscribe(EventType.FILE_EVENT, handler)
        bus.unsubscribe(EventType.FILE_EVENT, handler)
        called = bus.emit(EventType.FILE_EVENT)
        assert called == 0
        assert len(received) == 0

    def test_unsubscribe_nonexistent(self):
        bus = Observer()
        bus.unsubscribe(EventType.FILE_EVENT, lambda et, p: None)

    def test_once_handler(self):
        bus = Observer()
        count = [0]
        handler = lambda et, p: count.__setitem__(0, count[0] + 1)
        bus.subscribe(EventType.TASK_EVENT, handler, once=True)
        bus.emit(EventType.TASK_EVENT)
        bus.emit(EventType.TASK_EVENT)
        assert count[0] == 1

    def test_subscriber_count(self):
        bus = Observer()
        handler = lambda et, p: None
        assert bus.subscriber_count(EventType.FILE_EVENT) == 0
        bus.subscribe(EventType.FILE_EVENT, handler)
        assert bus.subscriber_count(EventType.FILE_EVENT) == 1

    def test_has_subscriber(self):
        bus = Observer()
        handler = lambda et, p: None
        assert bus.has_subscriber(EventType.FILE_EVENT, handler) is False
        bus.subscribe(EventType.FILE_EVENT, handler)
        assert bus.has_subscriber(EventType.FILE_EVENT, handler) is True

    def test_clear_specific_event(self):
        bus = Observer()
        h1 = lambda et, p: None
        h2 = lambda et, p: None
        bus.subscribe(EventType.FILE_EVENT, h1)
        bus.subscribe(EventType.TASK_EVENT, h2)
        bus.clear(EventType.FILE_EVENT)
        assert bus.subscriber_count(EventType.FILE_EVENT) == 0
        assert bus.subscriber_count(EventType.TASK_EVENT) == 1

    def test_clear_all(self):
        bus = Observer()
        bus.subscribe(EventType.FILE_EVENT, lambda et, p: None)
        bus.subscribe(EventType.TASK_EVENT, lambda et, p: None)
        bus.clear()
        for et in EventType:
            assert bus.subscriber_count(et) == 0

    def test_event_types_with_subscribers(self):
        bus = Observer()
        bus.subscribe(EventType.FILE_EVENT, lambda et, p: None)
        bus.subscribe(EventType.TASK_EVENT, lambda et, p: None)
        active = bus.event_types_with_subscribers()
        assert EventType.FILE_EVENT in active
        assert EventType.TASK_EVENT in active
        assert EventType.TIME_EVENT not in active

    def test_handler_exception_does_not_stop_others(self):
        bus = Observer()
        results = []

        def bad_handler(et, p):
            raise RuntimeError("boom")

        def good_handler(et, p):
            results.append("good")

        bus.subscribe(EventType.FILE_EVENT, bad_handler)
        bus.subscribe(EventType.FILE_EVENT, good_handler)
        called = bus.emit(EventType.FILE_EVENT)
        assert called == 1
        assert "good" in results

    def test_emit_default_payload(self):
        bus = Observer()
        received = []
        bus.subscribe(EventType.FILE_EVENT, lambda et, p: received.append(p))
        bus.emit(EventType.FILE_EVENT)
        assert received[0] == {}
