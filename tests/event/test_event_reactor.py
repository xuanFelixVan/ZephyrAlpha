# [A_test] module_id: SRC-TST-0866 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-382 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_event_reactor
# [INVARIANTS] EventReactor must log a Reaction for each subscribed event type
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.events.event_reactor import EventReactor, Reaction
from zephyr.shared.event_bus import EventBus, EventType


class TestReaction:
    def test_instantiation_defaults(self):
        r = Reaction(
            reaction_id="REACT-001",
            trigger_event=EventType.TASK_FAILED,
            action="Notify owner",
        )
        assert r.reaction_id == "REACT-001"
        assert r.trigger_event == EventType.TASK_FAILED
        assert r.action == "Notify owner"
        assert r.executed is False
        assert r.timestamp_utc == ""

    def test_instantiation_with_all_fields(self):
        r = Reaction(
            reaction_id="REACT-002",
            trigger_event=EventType.TASK_COMPLETED,
            action="Update journal",
            executed=True,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert r.executed is True
        assert r.timestamp_utc == "2026-01-01T00:00:00+00:00"


class TestEventReactor:
    def test_instantiation_with_explicit_bus(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        assert reactor._bus is bus
        assert reactor.get_reactions() == []

    def test_instantiation_with_default_bus(self):
        EventBus._instance = None
        reactor = EventReactor()
        assert reactor._bus is not None
        EventBus._instance = None

    def test_task_failed_triggers_reaction(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_FAILED, "TASK-FAIL-001")
        reactions = reactor.get_reactions()
        assert len(reactions) == 1
        assert reactions[0].trigger_event == EventType.TASK_FAILED
        assert "TASK-FAIL-001" in reactions[0].action
        assert reactions[0].executed is True

    def test_task_completed_triggers_reaction(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_COMPLETED, "TASK-DONE-001")
        reactions = reactor.get_reactions()
        assert len(reactions) == 1
        assert reactions[0].trigger_event == EventType.TASK_COMPLETED
        assert "TASK-DONE-001" in reactions[0].action

    def test_scope_drift_triggers_reaction(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(
            EventType.SCOPE_DRIFT,
            "TASK-DRIFT-001",
            {"extra_touch": ["file_a.py", "file_b.py"]},
        )
        reactions = reactor.get_reactions()
        assert len(reactions) == 1
        assert reactions[0].trigger_event == EventType.SCOPE_DRIFT
        assert "file_a.py" in reactions[0].action

    def test_scope_drift_with_empty_payload(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.SCOPE_DRIFT, "TASK-DRIFT-002", {})
        reactions = reactor.get_reactions()
        assert len(reactions) == 1
        assert "TASK-DRIFT-002" in reactions[0].action

    def test_dependency_resolved_triggers_reaction(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.DEPENDENCY_RESOLVED, "TASK-DEP-001")
        reactions = reactor.get_reactions()
        assert len(reactions) == 1
        assert reactions[0].trigger_event == EventType.DEPENDENCY_RESOLVED
        assert "TASK-DEP-001" in reactions[0].action

    def test_multiple_events_produce_multiple_reactions(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_FAILED, "TASK-001")
        bus.publish(EventType.TASK_COMPLETED, "TASK-002")
        bus.publish(EventType.SCOPE_DRIFT, "TASK-003")
        reactions = reactor.get_reactions()
        assert len(reactions) == 3

    def test_unsubscribed_event_type_no_reaction(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_CREATED, "TASK-NOPE")
        bus.publish(EventType.GATE_PASSED, "TASK-NOPE2")
        assert reactor.get_reactions() == []

    def test_get_reactions_returns_copy(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_FAILED, "TASK-001")
        r1 = reactor.get_reactions()
        r2 = reactor.get_reactions()
        assert r1 is not r2
        assert r1 == r2

    def test_reaction_has_timestamp(self):
        bus = EventBus()
        reactor = EventReactor(event_bus=bus)
        bus.publish(EventType.TASK_FAILED, "TASK-TS")
        reactions = reactor.get_reactions()
        assert reactions[0].timestamp_utc != ""
        assert "T" in reactions[0].timestamp_utc
