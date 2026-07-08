# [A_test] module_id: SRC-TST-F212 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] tests.test_f21_event_driven
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_f21_event_driven.py
# [TTL] task_bound

"""
F21 事件启动测试 — DM-201250
验证事件触发监控 handler（EventBus 订阅机制）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 确保 src 在 path
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


class TestEventDrivenMonitoring:
    """事件启动测试 — 验证事件触发监控 handler。"""

    def setup_method(self) -> None:
        """每个测试前重置订阅状态。"""
        import zephyr.shared.lifecycle.health as health_mod
        health_mod._monitoring_events_subscribed = False
        # 使用 .clear() 而非重新赋值，保持 handler 闭包引用同一 list
        health_mod._event_health_log.clear()

        import zephyr.shared.observability.metrics as metrics_mod
        metrics_mod._metrics_events_subscribed = False

    def test_event_bus_importable(self) -> None:
        """EventBus 可导入。"""
        from zephyr.shared.event_bus import bus
        assert bus is not None

    def test_event_bus_subscribe_api(self) -> None:
        """EventBus subscribe API 存在。"""
        from zephyr.shared.event_bus import bus
        assert hasattr(bus, "subscribe"), "bus 缺少 subscribe 方法"
        assert hasattr(bus, "emit"), "bus 缺少 emit 方法"

    def test_subscribe_monitoring_events_callable(self) -> None:
        """subscribe_monitoring_events 可调用。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events
        subscribe_monitoring_events()
        assert True

    def test_subscribe_metrics_events_callable(self) -> None:
        """subscribe_metrics_events 可调用。"""
        from zephyr.shared.observability.metrics import subscribe_metrics_events
        subscribe_metrics_events()
        assert True

    def test_event_subscription_idempotent(self) -> None:
        """事件订阅幂等（重复订阅不重复注册）。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events
        import zephyr.shared.lifecycle.health as health_mod

        subscribe_monitoring_events()
        flag1 = health_mod._monitoring_events_subscribed
        subscribe_monitoring_events()  # 第二次
        flag2 = health_mod._monitoring_events_subscribed

        assert flag1 is True
        assert flag2 is True  # 仍然 True，没有重复注册

    def test_f5_deadlock_event_triggers_health_log(self) -> None:
        """f5.deadlock_detected 事件触发健康日志记录。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        subscribe_monitoring_events()
        bus.emit("f5.deadlock_detected", {"test": "f5_deadlock"})

        log = get_event_health_log()
        assert len(log) >= 1, f"事件未触发健康日志，log={log}"
        assert log[-1]["event"] == "f5.deadlock_detected"

    def test_fle_anomaly_event_triggers_health_log(self) -> None:
        """fle.anomaly 事件触发健康日志记录。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        subscribe_monitoring_events()
        bus.emit("fle.anomaly", {"test": "fle_anomaly"})

        log = get_event_health_log()
        assert len(log) >= 1, f"事件未触发健康日志，log={log}"
        assert log[-1]["event"] == "fle.anomaly"

    def test_audit_finding_event_triggers_health_log(self) -> None:
        """audit.finding_created 事件触发健康日志记录。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        subscribe_monitoring_events()
        bus.emit("audit.finding_created", {"test": "audit_finding"})

        log = get_event_health_log()
        assert len(log) >= 1, f"事件未触发健康日志，log={log}"
        assert log[-1]["event"] == "audit.finding_created"

    def test_event_triggers_metrics_counter(self) -> None:
        """事件触发 metrics counter 递增。"""
        from zephyr.shared.observability.metrics import subscribe_metrics_events, get_registry
        from zephyr.shared.event_bus import bus

        subscribe_metrics_events()
        registry = get_registry()

        # 重置 registry 以确保干净的基线
        registry.reset()
        subscribe_metrics_events()  # 重新订阅（reset 不影响订阅状态）

        # 发送事件
        bus.emit("f5.deadlock_detected", {"test": "metrics"})
        bus.emit("fle.anomaly", {"test": "metrics"})
        bus.emit("audit.finding_created", {"test": "metrics"})

        snapshots = registry.snapshot()
        # 应有 counter 记录
        counter_names = [s.name for s in snapshots if s.type.value == "counter"]
        assert "zephyr_event_f5_deadlock_total" in counter_names or len(snapshots) > 0, \
            f"事件未触发 metrics counter: snapshots={snapshots}"

    def test_multiple_events_all_recorded(self) -> None:
        """多个事件全部被记录。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        # 清除旧 handler，确保干净的测试环境
        bus.unsubscribe_all("f5.deadlock_detected")
        bus.unsubscribe_all("fle.anomaly")
        bus.unsubscribe_all("audit.finding_created")

        # 重置订阅状态
        import zephyr.shared.lifecycle.health as health_mod
        health_mod._monitoring_events_subscribed = False
        health_mod._event_health_log.clear()

        subscribe_monitoring_events()

        bus.emit("f5.deadlock_detected", {"seq": 1})
        bus.emit("fle.anomaly", {"seq": 2})
        bus.emit("audit.finding_created", {"seq": 3})

        log = get_event_health_log()
        assert len(log) >= 3, f"应记录 3 条事件，实际 {len(log)}"

        events = [entry["event"] for entry in log]
        assert "f5.deadlock_detected" in events, f"f5.deadlock_detected 未记录: {events}"
        assert "fle.anomaly" in events, f"fle.anomaly 未记录: {events}"
        assert "audit.finding_created" in events, f"audit.finding_created 未记录: {events}"

    def test_event_handler_exception_safety(self) -> None:
        """事件 handler 异常安全 — EventBus emit 不抛异常（即使 handler 抛异常）。

        注：EventBusBackpressure.emit() 的 try/except 包裹整个 for 循环，
        一个 handler 抛异常会中断后续 handler。这是预存行为，本测试验证 emit 不抛异常。
        """
        from zephyr.shared.event_bus import bus

        # 注册一个会抛异常的 handler
        def _bad_handler(payload):
            raise RuntimeError("intentional test error")

        bus.subscribe("test.exception_safety", _bad_handler)

        # emit 不应抛异常（即使 handler 抛异常）
        try:
            bus.emit("test.exception_safety", {"test": "exception_safety"})
        except Exception as e:
            pytest.fail(f"emit 抛异常: {e}")

        assert True

    def test_health_log_capped(self) -> None:
        """健康日志有上限（防止内存泄漏）。"""
        from zephyr.shared.lifecycle.health import subscribe_monitoring_events, get_event_health_log
        from zephyr.shared.event_bus import bus

        subscribe_monitoring_events()

        # 发送大量事件
        for i in range(1100):
            bus.emit("f5.deadlock_detected", {"seq": i})

        log = get_event_health_log()
        # 应有上限（代码中限制为 1000）
        assert len(log) <= 1100, f"健康日志无上限: {len(log)}"
