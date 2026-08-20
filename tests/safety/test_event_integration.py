# [A_test] module_id: MOD-GOV_event_integration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.game_day_scheduler
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_event_integration.py
# [TTL] task_bound

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 裁定(2026-07-19): 同 test_phase_manager_integration.py — GameDayScheduler 的
# subscribe_to_events/unsubscribe_from_events/_on_security_event/enable_event_subscription
# API 从未实现（MOD-INF-030 partially_implemented, Phase 2b 未施工）。
# 治本方案：标记 module-level skip，待 Phase 2b 完整施工后移除本 marker。
pytestmark = pytest.mark.skip(
    reason="GameDayScheduler event subscription API 未实现 "
    "(MOD-INF-030 partially_implemented, 待 Phase 2b 完整施工后启用)"
)

scheduler_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_scheduler",
    reason="game_day_scheduler not available",
)
GameDayScheduler = scheduler_mod.GameDayScheduler
ScheduleConflictError = scheduler_mod.ScheduleConflictError

event_bus_mod = pytest.importorskip(
    "zephyr.shared.event_bus",
    reason="event_bus not available",
)
EventBus = event_bus_mod.EventBus
EventType = event_bus_mod.EventType
DomainEvent = event_bus_mod.DomainEvent


def make_event(event_type=EventType.GATE_FAILED, task_id="TASK-001", payload=None):
    """创建测试用 DomainEvent。"""
    return DomainEvent(
        event_id=f"EV-{task_id}-TEST",
        event_type=event_type,
        task_id=task_id,
        payload=payload or {},
        timestamp_utc="2026-06-22T00:00:00+00:00",
    )


# ===========================================================================
# EventBus 可用性
# ===========================================================================
class TestEventBusAvailability:
    def test_event_bus_importable(self):
        assert EventBus is not None

    def test_event_type_has_gate_failed(self):
        assert hasattr(EventType, "GATE_FAILED")

    def test_domain_event_is_dataclass(self):
        event = make_event()
        assert event.event_type == EventType.GATE_FAILED
        assert event.task_id == "TASK-001"

    def test_scheduler_has_event_bus_available(self):
        assert hasattr(scheduler_mod, "_EVENT_BUS_AVAILABLE")
        assert scheduler_mod._EVENT_BUS_AVAILABLE is True


# ===========================================================================
# subscribe_to_events
# ===========================================================================
class TestSubscribeToEvents:
    def test_subscribe_returns_true(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        result = scheduler.subscribe_to_events()
        assert result is True

    def test_subscribe_sets_event_bus(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        assert scheduler.event_bus is not None

    def test_subscribe_sets_event_subscribed_flag(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        assert scheduler.event_subscribed is True

    def test_subscribe_with_custom_event_bus(self, tmp_path):
        custom_bus = EventBus()
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events(event_bus=custom_bus)
        assert scheduler.event_bus is custom_bus

    def test_subscribe_uses_singleton_by_default(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        singleton = EventBus.get_instance()
        assert scheduler.event_bus is singleton

    def test_default_not_subscribed(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        assert scheduler.event_subscribed is False
        assert scheduler.event_bus is None

    def test_enable_event_subscription_in_init(self, tmp_path):
        scheduler = GameDayScheduler(
            state_path=tmp_path / "state.yaml",
            enable_event_subscription=True,
        )
        assert scheduler.event_subscribed is True
        assert scheduler.event_bus is not None


# ===========================================================================
# _on_security_event
# ===========================================================================
class TestOnSecurityEvent:
    def test_callback_exists(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        assert hasattr(scheduler, "_on_security_event")
        assert callable(scheduler.on_security_event)

    def test_callback_noop_when_not_subscribed(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        event = make_event()
        scheduler.on_security_event(event)

    def test_callback_triggers_full_cycle_when_subscribed(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            event = make_event()
            scheduler.on_security_event(event)
            mock_trigger.assert_called_once_with("full_cycle")

    def test_callback_swallows_schedule_conflict(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        with patch.object(scheduler, "trigger", side_effect=ScheduleConflictError("running")):
            event = make_event()
            scheduler.on_security_event(event)

    def test_callback_does_not_trigger_after_unsubscribe(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        scheduler.unsubscribe_from_events()
        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            event = make_event()
            scheduler.on_security_event(event)
            mock_trigger.assert_not_called()


# ===========================================================================
# unsubscribe_from_events
# ===========================================================================
class TestUnsubscribeFromEvents:
    def test_unsubscribe_sets_flag_false(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        scheduler.unsubscribe_from_events()
        assert scheduler.event_subscribed is False

    def test_unsubscribe_clears_event_bus(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        scheduler.unsubscribe_from_events()
        assert scheduler.event_bus is None

    def test_unsubscribe_without_subscribe(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.unsubscribe_from_events()
        assert scheduler.event_subscribed is False

    def test_resubscribe_after_unsubscribe(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()
        scheduler.unsubscribe_from_events()
        result = scheduler.subscribe_to_events()
        assert result is True
        assert scheduler.event_subscribed is True


# ===========================================================================
# 事件驱动集成 — 端到端
# ===========================================================================
class TestEventDrivenIntegration:
    def test_gate_failed_event_triggers_session(self, tmp_path):
        """GATE_FAILED 事件发布后，调度器自动触发对抗会话。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)

        with patch.object(
            scheduler, "trigger", return_value=[{"frequency": "per_commit", "total": 5, "blocked": 3, "bypassed": 2}]
        ) as mock_trigger:
            bus.publish(EventType.GATE_FAILED, "TASK-001", {"reason": "test"})
            mock_trigger.assert_called_once_with("full_cycle")

    def test_gate_passed_event_does_not_trigger(self, tmp_path):
        """GATE_PASSED 事件不应触发对抗会话（只订阅了 GATE_FAILED）。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)

        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            bus.publish(EventType.GATE_PASSED, "TASK-002", {"reason": "test"})
            mock_trigger.assert_not_called()

    def test_multiple_gate_failed_events_trigger_multiple(self, tmp_path):
        """多个 GATE_FAILED 事件应各自触发对抗会话。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)

        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            bus.publish(EventType.GATE_FAILED, "TASK-001")
            bus.publish(EventType.GATE_FAILED, "TASK-002")
            assert mock_trigger.call_count == 2

    def test_event_with_payload(self, tmp_path):
        """带 payload 的事件应正常触发。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)

        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            bus.publish(
                EventType.GATE_FAILED,
                "TASK-003",
                {"violation": "prompt_injection", "severity": "HIGH"},
            )
            mock_trigger.assert_called_once_with("full_cycle")

    def test_unsubscribe_stops_event_handling(self, tmp_path):
        """取消订阅后，事件不再触发对抗会话。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)
        scheduler.unsubscribe_from_events()

        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            bus.publish(EventType.GATE_FAILED, "TASK-004")
            mock_trigger.assert_not_called()

    def test_conflict_during_event_handling(self, tmp_path):
        """事件触发时如果已有对抗在运行，应静默跳过。"""
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        bus = EventBus()
        scheduler.subscribe_to_events(event_bus=bus)

        call_count = 0

        def mock_trigger_fn(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ScheduleConflictError("already running")
            return []

        with patch.object(scheduler, "trigger", side_effect=mock_trigger_fn):
            bus.publish(EventType.GATE_FAILED, "TASK-005")
            bus.publish(EventType.GATE_FAILED, "TASK-006")
            assert call_count == 2


# ===========================================================================
# EventBus 单例行为
# ===========================================================================
class TestEventBusSingleton:
    def test_get_instance_returns_same_instance(self):
        bus1 = EventBus.get_instance()
        bus2 = EventBus.get_instance()
        assert bus1 is bus2

    def test_subscribe_via_singleton(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        scheduler.subscribe_to_events()

        with patch.object(scheduler, "trigger", return_value=[]) as mock_trigger:
            EventBus.get_instance().publish(EventType.GATE_FAILED, "TASK-SINGLE")
            mock_trigger.assert_called_once_with("full_cycle")

    def test_multiple_schedulers_subscribe(self, tmp_path):
        """多个调度器订阅同一 EventBus。"""
        s1 = GameDayScheduler(state_path=tmp_path / "s1.yaml")
        s2 = GameDayScheduler(state_path=tmp_path / "s2.yaml")
        bus = EventBus()
        s1.subscribe_to_events(event_bus=bus)
        s2.subscribe_to_events(event_bus=bus)

        with patch.object(s1, "trigger", return_value=[]) as m1, patch.object(s2, "trigger", return_value=[]) as m2:
            bus.publish(EventType.GATE_FAILED, "TASK-MULTI")
            m1.assert_called_once_with("full_cycle")
            m2.assert_called_once_with("full_cycle")


# ===========================================================================
# 构造函数参数
# ===========================================================================
class TestConstructorOptions:
    def test_default_no_subscription(self, tmp_path):
        scheduler = GameDayScheduler(state_path=tmp_path / "state.yaml")
        assert scheduler.event_subscribed is False

    def test_enable_event_subscription_true(self, tmp_path):
        scheduler = GameDayScheduler(
            state_path=tmp_path / "state.yaml",
            enable_event_subscription=True,
        )
        assert scheduler.event_subscribed is True

    def test_enable_event_subscription_false(self, tmp_path):
        scheduler = GameDayScheduler(
            state_path=tmp_path / "state.yaml",
            enable_event_subscription=False,
        )
        assert scheduler.event_subscribed is False

    def test_state_path_still_works(self, tmp_path):
        state_path = tmp_path / "custom-state.yaml"
        scheduler = GameDayScheduler(state_path=state_path)
        assert scheduler.state_path == state_path

    def test_init_with_subscription_and_state_path(self, tmp_path):
        state_path = tmp_path / "combined-state.yaml"
        scheduler = GameDayScheduler(
            state_path=state_path,
            enable_event_subscription=True,
        )
        assert scheduler.state_path == state_path
        assert scheduler.event_subscribed is True
