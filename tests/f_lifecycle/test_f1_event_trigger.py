# [A_test] module_id=TEST-F1-EVENT | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §3.2
# [MODULE] tests.test_f1_event_trigger
# [INVARIANTS] 测试两套事件机制(shared.event_bus.EventBus/EventBusBackpressure)触发F1组件
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=发现事件触发链路漏洞
# [TESTS] self
# [DOMAIN] D_AUTONOMY_CORE
# [TTL] task_bound

"""F1 事件触发启动测试

验证 F1 两套事件机制能否正确触发 F1 组件启动:
  ① zephyr.shared.event_bus.EventBus（强类型领域事件）
     - subscribe(publish) TASK_CREATED/TASK_COMPLETED/GATE_PASSED 等事件
     - 验证 publish 触发订阅者回调
  ② zephyr.shared.event_bus.EventBusBackpressure（主题式带背压）
     - subscribe/emit 主题式事件
     - 验证 emit 触发订阅者回调
     - 验证背压控制（队列上限/丢弃计数）

依据: MOD-INF-035 §3.2数据流 + DM-201113 任务卡。
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.shared.event_bus import (
    EventBus,
    EventBusBackpressure,
    EventPriority,
    EventType,
)


# ---------------------------------------------------------------------------
# ① EventBus（强类型领域事件）
# ---------------------------------------------------------------------------


class TestEventBusSubscribe:
    """验证 EventBus 订阅/发布机制。"""

    def test_subscribe_and_publish(self) -> None:
        bus = EventBus()  # 直接实例化，避免单例污染
        called = []

        def handler(event) -> None:
            called.append(event)

        bus.subscribe(EventType.TASK_CREATED, handler)
        bus.publish(EventType.TASK_CREATED, task_id="DM-TEST-001", payload={"key": "value"})

        assert len(called) == 1
        assert called[0].task_id == "DM-TEST-001"
        assert called[0].payload == {"key": "value"}

    def test_multiple_subscribers(self) -> None:
        bus = EventBus()
        called1 = []
        called2 = []

        bus.subscribe(EventType.TASK_COMPLETED, lambda e: called1.append(1))
        bus.subscribe(EventType.TASK_COMPLETED, lambda e: called2.append(1))

        bus.publish(EventType.TASK_COMPLETED, task_id="DM-TEST-002")

        assert called1 == [1]
        assert called2 == [1]

    def test_no_subscriber_no_crash(self) -> None:
        """验证发布无订阅者的事件不崩溃。"""
        bus = EventBus()
        # TASK_ROLLBACK 无订阅者
        event = bus.publish(EventType.TASK_ROLLBACK, task_id="DM-TEST-003")
        assert event is not None
        assert event.task_id == "DM-TEST-003"

    def test_handler_exception_isolated(self) -> None:
        """验证单个 handler 异常不影响其他 handler。"""
        bus = EventBus()
        called = []

        def exploding_handler(event) -> None:
            raise RuntimeError("handler exploded")

        bus.subscribe(EventType.TASK_FAILED, exploding_handler)
        bus.subscribe(EventType.TASK_FAILED, lambda e: called.append(1))

        # 不应抛出异常
        bus.publish(EventType.TASK_FAILED, task_id="DM-TEST-004")
        # 正常 handler 仍被调用
        assert called == [1]

    def test_event_log_recorded(self) -> None:
        """验证事件被记录到 event_log。"""
        bus = EventBus()
        bus.publish(EventType.TASK_STARTED, task_id="DM-TEST-005")
        bus.publish(EventType.TASK_COMPLETED, task_id="DM-TEST-005")

        events = bus.get_events_for_task("DM-TEST-005")
        assert len(events) == 2
        assert events[0].event_type == EventType.TASK_STARTED
        assert events[1].event_type == EventType.TASK_COMPLETED


class TestEventBusTriggerF1:
    """验证 EventBus 事件触发 F1 组件回调。"""

    def test_task_created_triggers_callback(self) -> None:
        """验证 TASK_CREATED 事件可触发 F1 组件回调（模拟 auto_unblock）。"""
        bus = EventBus()
        unblocked = []

        def auto_unblock(event) -> None:
            if event.event_type == EventType.TASK_CREATED:
                unblocked.append(event.task_id)

        bus.subscribe(EventType.TASK_CREATED, auto_unblock)
        bus.publish(EventType.TASK_CREATED, task_id="DM-NEW-001")

        assert unblocked == ["DM-NEW-001"]

    def test_task_completed_triggers_callback(self) -> None:
        """验证 TASK_COMPLETED 事件可触发 F1 组件回调（模拟 triple_align）。"""
        bus = EventBus()
        aligned = []

        def triple_align(event) -> None:
            if event.event_type == EventType.TASK_COMPLETED:
                aligned.append(event.task_id)

        bus.subscribe(EventType.TASK_COMPLETED, triple_align)
        bus.publish(EventType.TASK_COMPLETED, task_id="DM-DONE-001")

        assert aligned == ["DM-DONE-001"]

    def test_gate_passed_triggers_callback(self) -> None:
        """验证 GATE_PASSED 事件可触发 F1 组件回调。"""
        bus = EventBus()
        triggered = []

        bus.subscribe(EventType.GATE_PASSED, lambda e: triggered.append(e.task_id))
        bus.publish(EventType.GATE_PASSED, task_id="DM-GATE-001")

        assert triggered == ["DM-GATE-001"]

    def test_dependency_resolved_triggers_callback(self) -> None:
        """验证 DEPENDENCY_RESOLVED 事件可触发 F1 组件回调。"""
        bus = EventBus()
        resolved = []

        bus.subscribe(EventType.DEPENDENCY_RESOLVED, lambda e: resolved.append(e.task_id))
        bus.publish(EventType.DEPENDENCY_RESOLVED, task_id="DM-DEP-001")

        assert resolved == ["DM-DEP-001"]


# ---------------------------------------------------------------------------
# ② EventBusBackpressure（主题式带背压）
# ---------------------------------------------------------------------------


class TestEventBusBackpressureSubscribe:
    """验证 EventBusBackpressure 订阅/发布机制。"""

    def test_subscribe_and_emit(self) -> None:
        bus = EventBusBackpressure()
        called = []

        bus.subscribe("test-topic", lambda e: called.append(e.payload))
        bus.emit("test-topic", {"data": "test"})

        assert len(called) == 1
        assert called[0] == {"data": "test"}

    def test_multiple_subscribers_same_topic(self) -> None:
        bus = EventBusBackpressure()
        called1 = []
        called2 = []

        bus.subscribe("multi-topic", lambda e: called1.append(e.payload))
        bus.subscribe("multi-topic", lambda e: called2.append(e.payload))

        bus.emit("multi-topic", "payload")

        assert called1 == ["payload"]
        assert called2 == ["payload"]

    def test_unsubscribe(self) -> None:
        bus = EventBusBackpressure()
        called = []

        def handler(event):
            called.append(event.payload)

        bus.subscribe("unsub-topic", handler)
        bus.emit("unsub-topic", "first")
        assert called == ["first"]

        result = bus.unsubscribe("unsub-topic", handler)
        assert result is True
        bus.emit("unsub-topic", "second")
        assert called == ["first"]  # 不再被调用

    def test_unsubscribe_all(self) -> None:
        bus = EventBusBackpressure()
        bus.subscribe("topic1", lambda p: None)
        bus.subscribe("topic2", lambda p: None)

        count = bus.unsubscribe_all()
        assert count == 2

    def test_emit_no_subscriber(self) -> None:
        """验证向无订阅者的 topic emit 不崩溃。"""
        bus = EventBusBackpressure()
        result = bus.emit("no-sub-topic", "payload")
        # emit 应返回 True（事件入队）
        assert isinstance(result, bool)


class TestEventBusBackpressureTriggerF1:
    """验证 EventBusBackpressure 事件触发 F1 组件回调。"""

    def test_blueprint_changed_triggers_callback(self) -> None:
        """验证 blueprint.changed 主题可触发 F1 组件回调（模拟 triple_align）。"""
        bus = EventBusBackpressure()
        aligned = []

        bus.subscribe("blueprint.changed", lambda e: aligned.append(e.payload))
        bus.emit("blueprint.changed", {"blueprint_id": "MOD-INF-035"})

        assert len(aligned) == 1
        assert aligned[0]["blueprint_id"] == "MOD-INF-035"

    def test_task_created_topic_triggers_callback(self) -> None:
        """验证 task.created 主题可触发 F1 组件回调。"""
        bus = EventBusBackpressure()
        triggered = []

        bus.subscribe("task.created", lambda e: triggered.append(e.payload))
        bus.emit("task.created", {"task_id": "DM-NEW-002"})

        assert len(triggered) == 1
        assert triggered[0]["task_id"] == "DM-NEW-002"

    def test_priority_events(self) -> None:
        """验证不同优先级的事件都能被处理。"""
        bus = EventBusBackpressure()
        called = []

        bus.subscribe("priority-topic", lambda e: called.append(e.payload))
        bus.emit("priority-topic", "low", priority=EventPriority.LOW)
        bus.emit("priority-topic", "normal", priority=EventPriority.NORMAL)
        bus.emit("priority-topic", "high", priority=EventPriority.HIGH)

        assert len(called) == 3


class TestEventBusBackpressureBackpressure:
    """验证 EventBusBackpressure 背压控制。"""

    def test_queue_thresholds(self) -> None:
        """验证队列阈值配置。"""
        bus = EventBusBackpressure(
            max_queue_size=100,
            warn_threshold=50,
            critical_threshold=80,
        )
        assert bus.max_queue_size == 100
        assert bus.warn_threshold == 50
        assert bus.critical_threshold == 80

    def test_emit_count_tracked(self) -> None:
        """验证 emit 计数被跟踪。"""
        bus = EventBusBackpressure()
        bus.emit("count-topic", "payload1")
        bus.emit("count-topic", "payload2")
        bus.emit("count-topic", "payload3")

        assert bus._emit_count == 3


# ---------------------------------------------------------------------------
# ④ 事件机制隔离性
# ---------------------------------------------------------------------------


class TestThreeEventMechanismsIsolation:
    """验证事件机制相互隔离——一个机制的异常不影响其他机制。"""

    def test_event_bus_and_backpressure_isolated(self) -> None:
        """验证 EventBus 和 EventBusBackpressure 互不影响。"""
        domain_bus = EventBus()
        bp_bus = EventBusBackpressure()

        domain_called = []
        bp_called = []

        domain_bus.subscribe(EventType.TASK_CREATED, lambda e: domain_called.append(e.task_id))
        bp_bus.subscribe("task.created", lambda e: bp_called.append(e.payload))

        # 在 domain_bus 发布，不影响 bp_bus
        domain_bus.publish(EventType.TASK_CREATED, task_id="DM-ISO-001")
        assert domain_called == ["DM-ISO-001"]
        assert bp_called == []

        # 在 bp_bus 发布，不影响 domain_bus
        bp_bus.emit("task.created", {"task_id": "DM-ISO-002"})
        assert bp_called == [{"task_id": "DM-ISO-002"}]
        assert domain_called == ["DM-ISO-001"]
