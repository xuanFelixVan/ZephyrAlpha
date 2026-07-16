# [A_test] module_id: SRC-TST-1686 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_state_propagation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_state_propagation_root.py
# [TTL] task_bound


from zephyr.orchestrator.lifecycle.state_propagation import (
    PROPAGATION_RULES,
    PropagationTarget,
    StatePropagationEvent,
    StatePropagator,
)


class TestPropagationTargetEnum:
    def test_has_six_targets(self):
        assert len(PropagationTarget) == 6

    def test_target_values(self):
        assert PropagationTarget.GATES.value == "gates"
        assert PropagationTarget.VMS.value == "vector-memory"
        assert PropagationTarget.FLE.value == "feedback-loop"
        assert PropagationTarget.DB.value == "database"
        assert PropagationTarget.KB.value == "knowledge_base"
        assert PropagationTarget.ORCHESTRATOR.value == "orchestrator"


class TestPropagationRules:
    def test_pending_to_in_progress(self):
        rule = PROPAGATION_RULES.get("PENDING→IN_PROGRESS")
        assert rule is not None
        assert PropagationTarget.GATES in rule["notify"]
        assert PropagationTarget.FLE in rule["notify"]

    def test_in_progress_to_completed(self):
        rule = PROPAGATION_RULES.get("IN_PROGRESS→COMPLETED")
        assert rule is not None
        assert PropagationTarget.VMS in rule["notify"]
        assert PropagationTarget.DB in rule["notify"]

    def test_in_progress_to_blocked(self):
        rule = PROPAGATION_RULES.get("IN_PROGRESS→BLOCKED")
        assert rule is not None
        assert PropagationTarget.GATES in rule["notify"]

    def test_in_progress_to_failed(self):
        rule = PROPAGATION_RULES.get("IN_PROGRESS→FAILED")
        assert rule is not None
        assert PropagationTarget.FLE in rule["notify"]
        assert PropagationTarget.DB in rule["notify"]

    def test_unknown_transition_absent(self):
        rule = PROPAGATION_RULES.get("UNKNOWN→STATE")
        assert rule is None


class TestStatePropagationEventModel:
    def test_create_default(self):
        event = StatePropagationEvent(
            task_id="T-1",
            old_status="PENDING",
            new_status="IN_PROGRESS",
        )
        assert event.task_id == "T-1"
        assert event.old_status == "PENDING"
        assert event.new_status == "IN_PROGRESS"
        assert event.targets == []
        assert event.payload == {}
        assert event.timestamp is not None

    def test_create_with_all_fields(self):
        event = StatePropagationEvent(
            task_id="T-2",
            old_status="IN_PROGRESS",
            new_status="COMPLETED",
            transition_key="IN_PROGRESS→COMPLETED",
            targets=["vector-memory", "database"],
            payload={"reason": "done"},
        )
        assert event.transition_key == "IN_PROGRESS→COMPLETED"
        assert len(event.targets) == 2


class TestStatePropagatorInstantiation:
    def test_create_instance(self):
        prop = StatePropagator()
        assert prop is not None

    def test_has_propagate_method(self):
        prop = StatePropagator()
        assert callable(prop.propagate)

    def test_has_get_events_method(self):
        prop = StatePropagator()
        assert callable(prop.get_events)

    def test_has_get_events_for_task_method(self):
        prop = StatePropagator()
        assert callable(prop.get_events_for_task)

    def test_has_get_notifiable_targets_method(self):
        prop = StatePropagator()
        assert callable(prop.get_notifiable_targets)


class TestPropagate:
    def test_known_transition_returns_targets(self):
        prop = StatePropagator()
        targets = prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        assert len(targets) > 0
        assert PropagationTarget.GATES in targets
        assert PropagationTarget.FLE in targets

    def test_unknown_transition_returns_empty(self):
        prop = StatePropagator()
        targets = prop.propagate("T-1", "UNKNOWN", "STATE")
        assert targets == []

    def test_propagate_creates_event(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        events = prop.get_events()
        assert len(events) == 1
        assert events[0].task_id == "T-1"

    def test_propagate_stores_multiple_events(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        prop.propagate("T-2", "IN_PROGRESS", "COMPLETED")
        assert len(prop.get_events()) == 2

    def test_propagate_with_payload(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS", payload={"key": "val"})
        events = prop.get_events()
        assert events[0].payload == {"key": "val"}


class TestGetEvents:
    def test_empty_initially(self):
        prop = StatePropagator()
        assert prop.get_events() == []

    def test_returns_copy(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        events = prop.get_events()
        events.clear()
        assert len(prop.get_events()) == 1


class TestGetEventsForTask:
    def test_no_events_for_unknown_task(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        result = prop.get_events_for_task("T-999")
        assert result == []

    def test_returns_events_for_specific_task(self):
        prop = StatePropagator()
        prop.propagate("T-1", "PENDING", "IN_PROGRESS")
        prop.propagate("T-2", "IN_PROGRESS", "COMPLETED")
        prop.propagate("T-1", "IN_PROGRESS", "COMPLETED")
        result = prop.get_events_for_task("T-1")
        assert len(result) == 2


class TestGetNotifiableTargets:
    def test_known_transition(self):
        prop = StatePropagator()
        targets = prop.get_notifiable_targets("PENDING", "IN_PROGRESS")
        assert "gates" in targets
        assert "feedback-loop" in targets

    def test_unknown_transition(self):
        prop = StatePropagator()
        targets = prop.get_notifiable_targets("UNKNOWN", "STATE")
        assert targets == []

    def test_completed_transition(self):
        prop = StatePropagator()
        targets = prop.get_notifiable_targets("IN_PROGRESS", "COMPLETED")
        assert "vector-memory" in targets
        assert "database" in targets
