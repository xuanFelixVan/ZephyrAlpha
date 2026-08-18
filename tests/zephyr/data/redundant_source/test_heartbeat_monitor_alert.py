# [TESTS] zephyr.data.redundant_source.heartbeat_monitor
# [TTL] permanent
"""HeartbeatMonitor 告警集成测试（R4a，#ARCH-DR-CH-RESTART-001）。

验证 CH 状态变化时触发告警：
- ALIVE→DEAD：CRITICAL 告警
- DEAD→ALIVE：INFO 恢复通知
- 无 alerter 时静默（向后兼容）
- 持续 DEAD 不重复告警（仅状态变化时触发）
"""
from __future__ import annotations

from typing import List, Tuple

import pytest

from zephyr.data.redundant_source.heartbeat_monitor import (
    HeartbeatMonitor,
    SourceState,
)


class FakeAlerter:
    """记录所有 notify 调用的假告警器。"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str, str | None]] = []

    def notify(
        self,
        task_id: str,
        error: str,
        level: str = "ERROR",
        source: str | None = None,
        extra: dict | None = None,
    ) -> bool:
        self.calls.append((task_id, error, level, source))
        return True


def _make_monitor(ping_results, alerter=None, fail_threshold=3):
    """构造一个 HeartbeatMonitor，ping 依次返回 ping_results 中的值。"""
    it = iter(ping_results)

    def fake_ping() -> bool:
        try:
            return next(it)
        except StopIteration:
            return True  # 耗尽后默认成功

    mon = HeartbeatMonitor(
        ch_ping_interval=0.001,  # 极短间隔加速测试
        ch_fail_threshold=fail_threshold,
        ch_ping_fn=fake_ping,
        alerter=alerter,
    )
    return mon


def _run_pings(monitor, n: int) -> None:
    """手动调用 n 次 _ping_once（_ch_ping_loop 的可测单轮），模拟状态变化触发的告警。"""
    prev = SourceState.UNKNOWN
    for _ in range(n):
        state_changed_to = monitor._ping_once(prev)
        prev = monitor._status.ch_state
        if state_changed_to is not None and monitor._alerter is not None:
            monitor._fire_ch_state_alert(state_changed_to)


class TestHeartbeatAlertIntegration:
    """R4a: CH 状态变化触发告警。"""

    def test_alive_to_dead_triggers_critical_alert(self):
        """CH 连续失败达阈值 → CRITICAL 告警。"""
        alerter = FakeAlerter()
        # 阈值=3：前 2 次失败不告警，第 3 次失败触发 DEAD→CRITICAL
        # 注意：prev_ch_state 初始 UNKNOWN，第 1 次设为 DEAD 后不触发（UNKNOWN 跳过）
        # 需要 ALIVE→DEAD 的真实转换。先成功 1 次（ALIVE），再失败 3 次（DEAD）
        monitor = _make_monitor(
            [True, False, False, False],
            alerter=alerter,
            fail_threshold=3,
        )
        _run_pings(monitor, 4)

        critical_calls = [c for c in alerter.calls if c[2] == "CRITICAL"]
        assert len(critical_calls) == 1, f"期望 1 次 CRITICAL，实际 {len(critical_calls)}: {alerter.calls}"
        assert critical_calls[0][0] == "ch_heartbeat"
        assert critical_calls[0][3] == "clickhouse"

    def test_dead_to_alive_triggers_info_recovery(self):
        """CH 恢复 → INFO 恢复通知。"""
        alerter = FakeAlerter()
        # ALIVE(1) → DEAD(3次失败) → ALIVE(1)
        monitor = _make_monitor(
            [True, False, False, False, True],
            alerter=alerter,
            fail_threshold=3,
        )
        _run_pings(monitor, 5)

        info_calls = [c for c in alerter.calls if c[2] == "INFO"]
        assert len(info_calls) == 1, f"期望 1 次 INFO 恢复，实际 {len(info_calls)}: {alerter.calls}"
        assert "恢复" in info_calls[0][1]

    def test_no_alert_when_alerter_none(self):
        """无 alerter 时不报错（向后兼容）。"""
        monitor = _make_monitor(
            [True, False, False, False],
            alerter=None,
            fail_threshold=3,
        )
        # 不应抛异常
        _run_pings(monitor, 4)
        assert monitor.get_status().ch_state == SourceState.DEAD

    def test_sustained_dead_no_repeat_alert(self):
        """持续 DEAD 不重复告警（仅状态变化时触发）。"""
        alerter = FakeAlerter()
        # ALIVE(1) → DEAD(连续 5 次失败)，阈值=3
        monitor = _make_monitor(
            [True, False, False, False, False, False],
            alerter=alerter,
            fail_threshold=3,
        )
        _run_pings(monitor, 6)

        critical_calls = [c for c in alerter.calls if c[2] == "CRITICAL"]
        assert len(critical_calls) == 1, f"持续 DEAD 应只告警 1 次，实际 {len(critical_calls)}"

    def test_flapping_triggers_each_transition(self):
        """CH 反复抖动 → 每次转换都告警（DEAD→ALIVE→DEAD→ALIVE）。"""
        alerter = FakeAlerter()
        # ALIVE → DEAD(3) → ALIVE → DEAD(3) → ALIVE
        monitor = _make_monitor(
            [True, False, False, False, True, False, False, False, True],
            alerter=alerter,
            fail_threshold=3,
        )
        _run_pings(monitor, 9)

        critical_calls = [c for c in alerter.calls if c[2] == "CRITICAL"]
        info_calls = [c for c in alerter.calls if c[2] == "INFO"]
        assert len(critical_calls) == 2, f"期望 2 次 CRITICAL，实际 {len(critical_calls)}"
        assert len(info_calls) == 2, f"期望 2 次 INFO，实际 {len(info_calls)}"
