# [A_test] module_id: SRC-TST-0862 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-381 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_event_bus
# [INVARIANTS] EventBus subscribe+publish must deliver events to all matching subscribers
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.event_bus import DomainEvent, EventBus, EventType


class TestEventType:
    def test_enum_values_exist(self):
        assert EventType.TASK_CREATED.value == "task.created"
        assert EventType.TASK_COMPLETED.value == "task.completed"
        assert EventType.TASK_FAILED.value == "task.failed"
        assert EventType.SCOPE_DRIFT.value == "scope.drift"
        assert EventType.DEPENDENCY_RESOLVED.value == "dependency.resolved"

    def test_all_members_are_strings(self):
        for member in EventType:
            assert isinstance(member.value, str)


class TestDomainEvent:
    def test_instantiation(self):
        ev = DomainEvent(
            event_id="EV-001",
            event_type=EventType.TASK_CREATED,
            task_id="TASK-001",
            payload={"key": "val"},
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert ev.event_id == "EV-001"
        assert ev.event_type == EventType.TASK_CREATED
        assert ev.task_id == "TASK-001"
        assert ev.payload == {"key": "val"}

    def test_default_payload_empty(self):
        ev = DomainEvent(
            event_id="EV-002",
            event_type=EventType.TASK_STARTED,
            task_id="TASK-002",
            payload={},
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert ev.payload == {}


class TestEventBus:
    def test_instantiation(self):
        bus = EventBus()
        assert bus is not None
        assert bus._subscribers is not None
        assert bus._event_log is not None

    def test_publish_creates_domain_event(self):
        bus = EventBus()
        event = bus.publish(EventType.TASK_CREATED, "TASK-100")
        assert isinstance(event, DomainEvent)
        assert event.event_type == EventType.TASK_CREATED
        assert event.task_id == "TASK-100"
        assert event.payload == {}

    def test_publish_with_payload(self):
        bus = EventBus()
        event = bus.publish(EventType.TASK_COMPLETED, "TASK-200", {"result": "ok"})
        assert event.payload == {"result": "ok"}

    def test_publish_with_none_payload_defaults_empty(self):
        bus = EventBus()
        event = bus.publish(EventType.TASK_FAILED, "TASK-300", None)
        assert event.payload == {}

    def test_subscribe_and_receive(self):
        bus = EventBus()
        received: list[DomainEvent] = []

        def handler(event: DomainEvent) -> None:
            received.append(event)

        bus.subscribe(EventType.TASK_CREATED, handler)
        bus.publish(EventType.TASK_CREATED, "TASK-400")
        assert len(received) == 1
        assert received[0].task_id == "TASK-400"

    def test_multiple_subscribers_same_event_type(self):
        bus = EventBus()
        results_a: list[DomainEvent] = []
        results_b: list[DomainEvent] = []

        bus.subscribe(EventType.TASK_STARTED, lambda e: results_a.append(e))
        bus.subscribe(EventType.TASK_STARTED, lambda e: results_b.append(e))

        bus.publish(EventType.TASK_STARTED, "TASK-500")
        assert len(results_a) == 1
        assert len(results_b) == 1

    def test_subscriber_only_receives_matching_type(self):
        bus = EventBus()
        received: list[DomainEvent] = []

        bus.subscribe(EventType.TASK_COMPLETED, lambda e: received.append(e))
        bus.publish(EventType.TASK_FAILED, "TASK-600")
        bus.publish(EventType.TASK_COMPLETED, "TASK-601")

        assert len(received) == 1
        assert received[0].task_id == "TASK-601"

    def test_get_events_for_task(self):
        bus = EventBus()
        bus.publish(EventType.TASK_CREATED, "TASK-700")
        bus.publish(EventType.TASK_STARTED, "TASK-700")
        bus.publish(EventType.TASK_CREATED, "TASK-701")

        events = bus.get_events_for_task("TASK-700")
        assert len(events) == 2
        assert all(e.task_id == "TASK-700" for e in events)

    def test_get_events_for_task_empty(self):
        bus = EventBus()
        assert bus.get_events_for_task("NONEXISTENT") == []

    def test_get_recent_events(self):
        bus = EventBus()
        for i in range(10):
            bus.publish(EventType.TASK_CREATED, f"TASK-{i}")

        recent = bus.get_recent_events(limit=3)
        assert len(recent) == 3
        assert recent[-1].task_id == "TASK-9"

    def test_clear(self):
        bus = EventBus()
        bus.publish(EventType.TASK_CREATED, "TASK-800")
        bus.clear()
        assert bus.get_recent_events() == []

    def test_subscriber_exception_does_not_break_publish(self):
        bus = EventBus()
        received: list[DomainEvent] = []

        def bad_handler(event: DomainEvent) -> None:
            raise RuntimeError("boom")

        def good_handler(event: DomainEvent) -> None:
            received.append(event)

        bus.subscribe(EventType.TASK_FAILED, bad_handler)
        bus.subscribe(EventType.TASK_FAILED, good_handler)

        bus.publish(EventType.TASK_FAILED, "TASK-900")
        assert len(received) == 1

    def test_get_instance_returns_same_object(self):
        EventBus._instance = None
        a = EventBus.get_instance()
        b = EventBus.get_instance()
        assert a is b
        EventBus._instance = None
