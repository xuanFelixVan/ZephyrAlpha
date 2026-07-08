# [A_test] module_id: SRC-TST-F5-EVT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §3
# [MODULE] tests.test_f5_event_startup
# [INVARIANTS] subscribe_all is idempotent; handle_* never raises; unsubscribe_all restores clean state
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit codes: 0=all tests pass
# [TESTS] tests/test_f5_event_startup.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.governance.resilience_governance.f5_event_subscriber import (
    DEFAULT_RULE_BINDINGS,
    F5_EVENT_TOPICS,
    TOPIC_CONFLICT_DETECTED,
    TOPIC_DEADLOCK_DETECTED,
    TOPIC_ESCALATION_NEEDED,
    EventHandlerResult,
    F5EventSubscriber,
    RuleBinding,
    SubscriptionResult,
    create_f5_event_subscriber,
)
from zephyr.shared.event_bus import EventBusBackpressure, EventPriority


@pytest.fixture
def isolated_bus() -> EventBusBackpressure:
    """每个测试用例使用独立的 EventBus 实例, 避免全局 bus 污染。"""
    return EventBusBackpressure()


@pytest.fixture
def subscriber(isolated_bus: EventBusBackpressure) -> F5EventSubscriber:
    """已绑定独立 bus 的订阅器 (未绑定 F5 组件)。"""
    return F5EventSubscriber(event_bus=isolated_bus)


@pytest.fixture
def full_subscriber(isolated_bus: EventBusBackpressure) -> F5EventSubscriber:
    """绑定真实 F5 组件的订阅器 (通过 F5BootIntegration 启动)。

    注: escalation_engine 用 mock 替换, 因为真实 EscalationEngine.evaluate()
    会触发 LSG 扫描, 而项目中 SupplyChainGuard 存在签名不匹配的预存问题
    (见 test_f5_auto_startup.py 中的注释)。
    """
    from zephyr.governance.resilience_governance.f5_boot_integration import F5BootIntegration
    from zephyr.governance.escalation.escalation_models import EscalationEvent, RuleCategory
    integration = F5BootIntegration()
    boot = integration.on_startup()
    assert boot.success is True, f"F5 boot failed: {boot.errors}"
    sub = F5EventSubscriber(event_bus=isolated_bus)
    # 用 mock 替换 escalation_engine, 避免 SupplyChainGuard 签名问题
    mock_esc = MagicMock()
    mock_event = EscalationEvent(
        category=RuleCategory.CUSTOM,
        description="mocked escalation",
        owner_id="test",
    )
    mock_esc.evaluate.return_value = mock_event
    sub.bind_components(
        escalation_engine=mock_esc,
        delegation_engine=integration.delegation_engine,
        deadlock_detector=integration.deadlock_detector,
        arbitrator=integration.arbitrator,
    )
    return sub


class TestSubscriptionResult:
    def test_default_factory_values(self):
        r = SubscriptionResult(success=True, topic="t", handler_name="h")
        assert r.success is True
        assert r.topic == "t"
        assert r.handler_name == "h"
        assert r.error == ""

    def test_with_error(self):
        r = SubscriptionResult(success=False, topic="t", handler_name="h", error="boom")
        assert r.success is False
        assert r.error == "boom"


class TestEventHandlerResult:
    def test_default_factory_values(self):
        r = EventHandlerResult(handled=True, topic="t", action="a", success=True)
        assert r.handled is True
        assert r.details == {}
        assert r.error == ""


class TestRuleBinding:
    def test_default_priority_is_high(self):
        b = RuleBinding(category="c", topic="t", handler_name="h")
        assert b.priority == EventPriority.HIGH

    def test_custom_priority(self):
        b = RuleBinding(category="c", topic="t", handler_name="h", priority=EventPriority.LOW)
        assert b.priority == EventPriority.LOW


class TestF5EventTopics:
    def test_topic_constants(self):
        assert TOPIC_DEADLOCK_DETECTED == "f5.deadlock_detected"
        assert TOPIC_ESCALATION_NEEDED == "f5.escalation_needed"
        assert TOPIC_CONFLICT_DETECTED == "f5.conflict_detected"

    def test_f5_event_topics_tuple(self):
        assert len(F5_EVENT_TOPICS) == 3
        assert TOPIC_DEADLOCK_DETECTED in F5_EVENT_TOPICS
        assert TOPIC_ESCALATION_NEEDED in F5_EVENT_TOPICS
        assert TOPIC_CONFLICT_DETECTED in F5_EVENT_TOPICS

    def test_default_rule_bindings_cover_all_topics(self):
        topics = {b.topic for b in DEFAULT_RULE_BINDINGS}
        assert topics == set(F5_EVENT_TOPICS)

    def test_default_rule_bindings_handler_names(self):
        bindings = {b.topic: b.handler_name for b in DEFAULT_RULE_BINDINGS}
        assert bindings[TOPIC_DEADLOCK_DETECTED] == "handle_deadlock"
        assert bindings[TOPIC_ESCALATION_NEEDED] == "handle_escalation"
        assert bindings[TOPIC_CONFLICT_DETECTED] == "handle_conflict"


class TestConstruction:
    def test_default_construction_uses_global_bus(self):
        from zephyr.governance.resilience_governance.f5_event_subscriber import default_bus
        sub = F5EventSubscriber()
        assert sub._bus is default_bus

    def test_custom_bus(self, isolated_bus: EventBusBackpressure):
        sub = F5EventSubscriber(event_bus=isolated_bus)
        assert sub._bus is isolated_bus

    def test_custom_rule_bindings(self, isolated_bus: EventBusBackpressure):
        custom = [RuleBinding(category="x", topic="x.topic", handler_name="h")]
        sub = F5EventSubscriber(event_bus=isolated_bus, rule_bindings=custom)
        assert len(sub.rule_bindings) == 1
        assert sub.rule_bindings[0].topic == "x.topic"

    def test_default_rule_bindings_used_when_none(self, isolated_bus: EventBusBackpressure):
        sub = F5EventSubscriber(event_bus=isolated_bus)
        assert len(sub.rule_bindings) == len(DEFAULT_RULE_BINDINGS)

    def test_initial_state_no_subscriptions(self, subscriber: F5EventSubscriber):
        assert subscriber.subscribed_topics == set()
        assert subscriber.is_subscribed(TOPIC_DEADLOCK_DETECTED) is False

    def test_initial_components_none(self, subscriber: F5EventSubscriber):
        assert subscriber.escalation_engine is None
        assert subscriber.delegation_engine is None
        assert subscriber.deadlock_detector is None
        assert subscriber.arbitrator is None
        assert subscriber.feedback_loop is None

    def test_handler_registry_populated(self, subscriber: F5EventSubscriber):
        assert TOPIC_DEADLOCK_DETECTED in subscriber._handler_registry
        assert TOPIC_ESCALATION_NEEDED in subscriber._handler_registry
        assert TOPIC_CONFLICT_DETECTED in subscriber._handler_registry


class TestBindComponents:
    def test_bind_individual_components(self, subscriber: F5EventSubscriber):
        esc = MagicMock()
        ddl = MagicMock()
        subscriber.bind_components(escalation_engine=esc, deadlock_detector=ddl)
        assert subscriber.escalation_engine is esc
        assert subscriber.deadlock_detector is ddl
        assert subscriber.delegation_engine is None
        assert subscriber.arbitrator is None

    def test_bind_all_components(self, subscriber: F5EventSubscriber):
        esc, dele, ddl, arb = MagicMock(), MagicMock(), MagicMock(), MagicMock()
        subscriber.bind_components(esc, dele, ddl, arb)
        assert subscriber.escalation_engine is esc
        assert subscriber.delegation_engine is dele
        assert subscriber.deadlock_detector is ddl
        assert subscriber.arbitrator is arb

    def test_bind_feedback_loop(self, subscriber: F5EventSubscriber):
        fl = MagicMock()
        subscriber.bind_feedback_loop(fl)
        assert subscriber.feedback_loop is fl

    def test_bind_components_idempotent(self, subscriber: F5EventSubscriber):
        esc1 = MagicMock()
        esc2 = MagicMock()
        subscriber.bind_components(escalation_engine=esc1)
        subscriber.bind_components(escalation_engine=esc2)
        assert subscriber.escalation_engine is esc2


class TestSubscribeAll:
    def test_subscribes_to_all_f5_topics(self, subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        results = subscriber.subscribe_all()
        assert len(results) == 3
        assert all(r.success for r in results)
        assert subscriber.is_subscribed(TOPIC_DEADLOCK_DETECTED)
        assert subscriber.is_subscribed(TOPIC_ESCALATION_NEEDED)
        assert subscriber.is_subscribed(TOPIC_CONFLICT_DETECTED)
        assert len(subscriber.subscribed_topics) == 3

    def test_subscribe_all_idempotent(self, subscriber: F5EventSubscriber):
        first = subscriber.subscribe_all()
        second = subscriber.subscribe_all()
        assert len(first) == 3
        assert len(second) == 3
        assert all(r.error == "already_subscribed" for r in second)
        assert len(subscriber.subscribed_topics) == 3

    def test_subscription_result_fields(self, subscriber: F5EventSubscriber):
        results = subscriber.subscribe_all()
        for r in results:
            assert isinstance(r, SubscriptionResult)
            assert r.success is True
            assert r.topic in F5_EVENT_TOPICS
            assert r.handler_name in ("handle_deadlock", "handle_escalation", "handle_conflict")

    def test_subscribe_registers_handler_in_bus(self, subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        subscriber.subscribe_all()
        assert TOPIC_DEADLOCK_DETECTED in isolated_bus._handlers
        assert TOPIC_ESCALATION_NEEDED in isolated_bus._handlers
        assert TOPIC_CONFLICT_DETECTED in isolated_bus._handlers


class TestUnsubscribeAll:
    def test_unsubscribes_all_topics(self, subscriber: F5EventSubscriber):
        subscriber.subscribe_all()
        count = subscriber.unsubscribe_all()
        assert count == 3
        assert subscriber.subscribed_topics == set()

    def test_unsubscribe_when_not_subscribed(self, subscriber: F5EventSubscriber):
        count = subscriber.unsubscribe_all()
        assert count == 0

    def test_resubscribe_after_unsubscribe(self, subscriber: F5EventSubscriber):
        subscriber.subscribe_all()
        subscriber.unsubscribe_all()
        results = subscriber.subscribe_all()
        assert all(r.success for r in results)
        assert len(subscriber.subscribed_topics) == 3


class TestHandleDeadlock:
    def test_handles_deadlock_with_node(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "agent-1", "cycle": ["a", "b", "a"]}
        result = subscriber.handle_deadlock(event)
        assert result.handled is True
        assert result.success is True
        assert result.action == "break_deadlock"
        assert result.details["node"] == "agent-1"
        assert result.details["broken"] is True
        ddl.break_deadlock.assert_called_once_with("agent-1")

    def test_handles_deadlock_without_node_uses_preempt(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.preempt_lowest.return_value = "victim-agent"
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {}
        result = subscriber.handle_deadlock(event)
        assert result.handled is True
        assert result.success is True
        assert result.details["victim"] == "victim-agent"
        ddl.preempt_lowest.assert_called_once()

    def test_deadlock_without_detector_returns_error(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"node": "x"}
        result = subscriber.handle_deadlock(event)
        assert result.handled is False
        assert result.success is False
        assert "not bound" in result.error

    def test_deadlock_handles_detector_exception(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.break_deadlock.side_effect = RuntimeError("boom")
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        result = subscriber.handle_deadlock(event)
        assert result.handled is True
        assert result.success is False
        assert "boom" in result.error

    def test_deadlock_with_dict_payload(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        result = subscriber.handle_deadlock({"node": "agent-x"})
        assert result.handled is True
        assert result.success is True

    def test_deadlock_never_raises(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = MagicMock(side_effect=RuntimeError("bad payload"))
        result = subscriber.handle_deadlock(event)
        assert isinstance(result, EventHandlerResult)


class TestHandleEscalation:
    def test_handles_escalation_with_valid_category(self, full_subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {
            "category": "deadlock",
            "description": "test escalation",
            "owner_id": "owner-1",
        }
        result = full_subscriber.handle_escalation(event)
        assert result.handled is True
        assert result.success is True
        assert result.action == "evaluate"
        assert "event_id" in result.details

    def test_escalation_with_invalid_category_falls_back_to_custom(self, full_subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"category": "nonexistent", "description": "test"}
        result = full_subscriber.handle_escalation(event)
        assert result.handled is True
        assert result.success is True

    def test_escalation_without_engine_returns_error(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"description": "test"}
        result = subscriber.handle_escalation(event)
        assert result.handled is False
        assert "not bound" in result.error

    def test_escalation_handles_engine_exception(self, subscriber: F5EventSubscriber):
        esc = MagicMock()
        esc.evaluate.side_effect = RuntimeError("engine broken")
        subscriber.bind_components(escalation_engine=esc)
        event = MagicMock()
        event.payload = {"description": "test"}
        result = subscriber.handle_escalation(event)
        assert result.handled is True
        assert result.success is False
        assert "engine broken" in result.error

    def test_escalation_default_category_is_custom(self, full_subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"description": "no category"}
        result = full_subscriber.handle_escalation(event)
        assert result.handled is True
        assert result.success is True


class TestHandleConflict:
    def test_handles_conflict_with_agent_meta(self, full_subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {
            "agent_a": {"agent_id": "agent-1", "role": "builder", "tasks_completed": 5},
            "agent_b": {"agent_id": "agent-2", "role": "governance", "tasks_completed": 10},
            "conflicted_files": ["src/foo.py", "src/bar.py"],
        }
        result = full_subscriber.handle_conflict(event)
        assert result.handled is True
        assert result.success is True
        assert result.action == "arbitrate"
        assert "winner" in result.details
        assert "tier" in result.details

    def test_conflict_without_arbitrator_returns_error(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"agent_a": {}, "agent_b": {}}
        result = subscriber.handle_conflict(event)
        assert result.handled is False
        assert "not bound" in result.error

    def test_conflict_handles_arbitrator_exception(self, subscriber: F5EventSubscriber):
        arb = MagicMock()
        arb.arbitrate.side_effect = RuntimeError("arb broken")
        subscriber.bind_components(arbitrator=arb)
        event = MagicMock()
        event.payload = {"agent_a": {"agent_id": "a"}, "agent_b": {"agent_id": "b"}}
        result = subscriber.handle_conflict(event)
        assert result.handled is True
        assert result.success is False
        assert "arb broken" in result.error

    def test_conflict_with_empty_files(self, full_subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {
            "agent_a": {"agent_id": "a"},
            "agent_b": {"agent_id": "b"},
            "conflicted_files": [],
        }
        result = full_subscriber.handle_conflict(event)
        assert result.handled is True
        assert result.success is True


class TestFeedbackLoopIntegration:
    def test_feedback_loop_notified_on_deadlock(self, subscriber: F5EventSubscriber):
        fl = MagicMock()
        fl.generate_proposals.return_value = [MagicMock()]
        subscriber.bind_feedback_loop(fl)
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        subscriber.handle_deadlock(event)
        fl.generate_proposals.assert_called_once()
        fl.apply_proposal.assert_called_once()

    def test_feedback_loop_notified_on_escalation(self, full_subscriber: F5EventSubscriber):
        fl = MagicMock()
        fl.generate_proposals.return_value = []
        full_subscriber.bind_feedback_loop(fl)
        event = MagicMock()
        event.payload = {"description": "test"}
        full_subscriber.handle_escalation(event)
        fl.generate_proposals.assert_called_once()

    def test_feedback_loop_notified_on_conflict(self, full_subscriber: F5EventSubscriber):
        fl = MagicMock()
        fl.generate_proposals.return_value = []
        full_subscriber.bind_feedback_loop(fl)
        event = MagicMock()
        event.payload = {
            "agent_a": {"agent_id": "a"},
            "agent_b": {"agent_id": "b"},
        }
        full_subscriber.handle_conflict(event)
        fl.generate_proposals.assert_called_once()

    def test_feedback_loop_failure_does_not_break_handler(self, subscriber: F5EventSubscriber):
        fl = MagicMock()
        fl.generate_proposals.side_effect = RuntimeError("fl broken")
        subscriber.bind_feedback_loop(fl)
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        result = subscriber.handle_deadlock(event)
        assert result.handled is True
        assert result.success is True

    def test_no_feedback_loop_does_not_raise(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        result = subscriber.handle_deadlock(event)
        assert result.handled is True


class TestEventDispatchLog:
    def test_dispatch_log_records_results(self, subscriber: F5EventSubscriber):
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        subscriber.handle_deadlock(event)
        log = subscriber.dispatch_log
        assert len(log) == 1
        assert log[0].action == "break_deadlock"

    def test_dispatch_log_capped_at_max(self, subscriber: F5EventSubscriber):
        subscriber._max_log_entries = 5
        ddl = MagicMock()
        ddl.break_deadlock.return_value = True
        subscriber.bind_components(deadlock_detector=ddl)
        event = MagicMock()
        event.payload = {"node": "x"}
        for _ in range(10):
            subscriber.handle_deadlock(event)
        assert len(subscriber.dispatch_log) == 5


class TestEmitHelpers:
    def test_emit_deadlock_event(self, subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        ok = subscriber.emit_deadlock_event(node="agent-1", cycle=["a", "b"])
        assert ok is True
        assert isolated_bus._emit_count == 1

    def test_emit_escalation_event(self, subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        ok = subscriber.emit_escalation_event(category="deadlock", description="test", owner_id="o1")
        assert ok is True
        assert isolated_bus._emit_count == 1

    def test_emit_conflict_event(self, subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        ok = subscriber.emit_conflict_event(
            agent_a={"agent_id": "a"},
            agent_b={"agent_id": "b"},
            conflicted_files=["f.py"],
        )
        assert ok is True
        assert isolated_bus._emit_count == 1


class TestGetStats:
    def test_stats_initial_state(self, subscriber: F5EventSubscriber):
        stats = subscriber.get_stats()
        assert stats["subscribed_topics"] == []
        assert stats["rule_bindings_count"] == 3
        assert stats["dispatch_log_count"] == 0
        components = stats["components_bound"]
        assert components["escalation_engine"] is False
        assert components["arbitrator"] is False

    def test_stats_after_subscribe_and_bind(self, subscriber: F5EventSubscriber):
        subscriber.bind_components(escalation_engine=MagicMock())
        subscriber.subscribe_all()
        stats = subscriber.get_stats()
        assert len(stats["subscribed_topics"]) == 3
        assert stats["components_bound"]["escalation_engine"] is True


class TestCreateF5EventSubscriber:
    def test_creates_with_components(self, isolated_bus: EventBusBackpressure):
        esc, dele, ddl, arb = MagicMock(), MagicMock(), MagicMock(), MagicMock()
        sub = create_f5_event_subscriber(
            escalation_engine=esc,
            delegation_engine=dele,
            deadlock_detector=ddl,
            arbitrator=arb,
            event_bus=isolated_bus,
        )
        assert sub.escalation_engine is esc
        assert sub.delegation_engine is dele
        assert sub.deadlock_detector is ddl
        assert sub.arbitrator is arb
        assert sub._bus is isolated_bus

    def test_creates_with_feedback_loop(self, isolated_bus: EventBusBackpressure):
        fl = MagicMock()
        sub = create_f5_event_subscriber(feedback_loop=fl, event_bus=isolated_bus)
        assert sub.feedback_loop is fl

    def test_creates_without_components(self, isolated_bus: EventBusBackpressure):
        sub = create_f5_event_subscriber(event_bus=isolated_bus)
        assert sub.escalation_engine is None
        assert sub._bus is isolated_bus


class TestEndToEndEventFlow:
    def test_deadlock_event_triggers_break_deadlock(self, full_subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        full_subscriber.subscribe_all()
        ddl = full_subscriber.deadlock_detector
        ddl.add_edge("a", "b")
        ddl.add_edge("b", "a")
        ok = full_subscriber.emit_deadlock_event(node="a", cycle=["a", "b", "a"])
        assert ok is True
        log = full_subscriber.dispatch_log
        assert len(log) == 1
        assert log[0].topic == TOPIC_DEADLOCK_DETECTED
        assert log[0].handled is True

    def test_escalation_event_triggers_evaluate(self, full_subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        full_subscriber.subscribe_all()
        ok = full_subscriber.emit_escalation_event(
            category="deadlock",
            description="e2e escalation test",
            owner_id="e2e-owner",
        )
        assert ok is True
        log = full_subscriber.dispatch_log
        assert len(log) == 1
        assert log[0].topic == TOPIC_ESCALATION_NEEDED
        assert log[0].success is True

    def test_conflict_event_triggers_arbitrate(self, full_subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        full_subscriber.subscribe_all()
        ok = full_subscriber.emit_conflict_event(
            agent_a={"agent_id": "agent-a", "role": "builder", "tasks_completed": 3},
            agent_b={"agent_id": "agent-b", "role": "governance", "tasks_completed": 8},
            conflicted_files=["src/x.py"],
        )
        assert ok is True
        log = full_subscriber.dispatch_log
        assert len(log) == 1
        assert log[0].topic == TOPIC_CONFLICT_DETECTED
        assert log[0].success is True

    def test_unsubscribe_stops_dispatch(self, full_subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        full_subscriber.subscribe_all()
        full_subscriber.emit_deadlock_event(node="x")
        assert len(full_subscriber.dispatch_log) == 1
        full_subscriber.unsubscribe_all()
        full_subscriber.emit_deadlock_event(node="y")
        assert len(full_subscriber.dispatch_log) == 1

    def test_full_lifecycle(self, full_subscriber: F5EventSubscriber, isolated_bus: EventBusBackpressure):
        full_subscriber.subscribe_all()
        full_subscriber.emit_deadlock_event(node="a")
        full_subscriber.emit_escalation_event(description="lifecycle test")
        full_subscriber.emit_conflict_event(
            agent_a={"agent_id": "a"},
            agent_b={"agent_id": "b"},
        )
        assert len(full_subscriber.dispatch_log) == 3
        topics = {r.topic for r in full_subscriber.dispatch_log}
        assert topics == set(F5_EVENT_TOPICS)
        count = full_subscriber.unsubscribe_all()
        assert count == 3


class TestExtractPayload:
    def test_extract_from_dict(self, subscriber: F5EventSubscriber):
        payload = F5EventSubscriber._extract_payload({"key": "value"})
        assert payload == {"key": "value"}

    def test_extract_from_none(self, subscriber: F5EventSubscriber):
        payload = F5EventSubscriber._extract_payload(None)
        assert payload == {}

    def test_extract_from_event_with_dict_payload(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = {"key": "value"}
        payload = F5EventSubscriber._extract_payload(event)
        assert payload == {"key": "value"}

    def test_extract_from_event_with_none_payload(self, subscriber: F5EventSubscriber):
        event = MagicMock()
        event.payload = None
        payload = F5EventSubscriber._extract_payload(event)
        assert payload == {}
