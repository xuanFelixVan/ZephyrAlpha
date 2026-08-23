# [BLUEPRINT] MOD-EX-058 | docs/03_modules/MOD-EX-058/ | §test
# [MODULE] tests.reporting.test_miniqmt_order_link_probe
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.miniqmt_order_link_probe
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;全程假通道零真实 QMT 连接
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] test_miniqmt_order_link_probe.py
# [A_test] module_id: MOD-EX-058_probe | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-EX-058_probe 单元测试: miniQMT 下单链路探针（source_health 族口径）。

覆盖：
- 状态映射：ready+无心跳失败=healthy；ready+心跳失败=degraded；
  交易时段未就绪=down（告警态）；非交易时段未就绪=closed（正常态不误报）；
- 判定降级：交易时段判定未注入/异常 → 保守按交易时段口径（down）+notes 留痕；
- 延迟探针注入位：注入产出透传 / 未注入 notes / 异常不炸探针；
- 通道读取异常 → status=error 不抛；仅有 is_ready 的瘦鸭型兼容；
- 契约：clock 注入确定性、to_dict JSON 可序列化、source_health 族字段对齐
  （source/status/timestamp）。
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from zephyr.reporting.miniqmt_order_link_probe import (
    STATUS_CLOSED,
    STATUS_DEGRADED,
    STATUS_DOWN,
    STATUS_ERROR,
    STATUS_HEALTHY,
    OrderLinkHealth,
    probe_order_link,
)

_FIXED_NOW = dt.datetime(2026, 8,24, 15, 0, tzinfo=dt.timezone.utc)


def _clock() -> dt.datetime:
    return _FIXED_NOW


class _FakeStatus:
    """ChannelStatus 鸭型（state/ready/consecutive_heartbeat_failures/reconnect_attempts）。"""

    def __init__(self, state: str, ready: bool, hb: int = 0, ra: int = 0) -> None:
        self.state = state
        self.ready = ready
        self.consecutive_heartbeat_failures = hb
        self.reconnect_attempts = ra


class _FakeManager:
    """MiniQmtChannelManager 鸭型（is_ready + status()）。"""

    def __init__(
        self,
        ready: bool,
        state: str = "connected",
        hb: int = 0,
        ra: int = 0,
        *,
        status_raises: bool = False,
        with_status: bool = True,
    ) -> None:
        self._ready = ready
        self._state = state if ready else state if state != "connected" else "down"
        self._hb = hb
        self._ra = ra
        self._status_raises = status_raises
        self._with_status = with_status

    @property
    def is_ready(self) -> bool:
        return self._ready

    def status(self) -> _FakeStatus:
        if self._status_raises:
            raise RuntimeError("channel read boom")
        return _FakeStatus(self._state, self._ready, self._hb, self._ra)


class _LeanManager:
    """瘦鸭型：仅 is_ready（无 status() 快照）。"""

    def __init__(self, ready: bool) -> None:
        self._ready = ready

    @property
    def is_ready(self) -> bool:
        return self._ready


# ----------------------------------------------------------------------
# 状态映射
# ----------------------------------------------------------------------


class TestStatusMapping:
    def test_ready_no_failures_is_healthy(self) -> None:
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: True, clock=_clock)
        assert h.status == STATUS_HEALTHY
        assert h.ready is True
        assert h.channel_state == "connected"

    def test_ready_with_heartbeat_failures_is_degraded(self) -> None:
        h = probe_order_link(_FakeManager(True, hb=2), is_trading_time=lambda: True, clock=_clock)
        assert h.status == STATUS_DEGRADED
        assert h.consecutive_heartbeat_failures == 2
        assert any("心跳" in n for n in h.notes)

    def test_not_ready_trading_time_is_down(self) -> None:
        h = probe_order_link(
            _FakeManager(False, state="reconnecting", ra=2),
            is_trading_time=lambda: True,
            clock=_clock,
        )
        assert h.status == STATUS_DOWN
        assert h.trading_time is True
        assert h.reconnect_attempts == 2

    def test_not_ready_non_trading_is_closed_no_false_alarm(self) -> None:
        h = probe_order_link(
            _FakeManager(False, state="disconnected"),
            is_trading_time=lambda: False,
            clock=_clock,
        )
        assert h.status == STATUS_CLOSED
        assert h.trading_time is False
        assert any("非交易时段" in n for n in h.notes)

    def test_not_ready_without_trading_checker_conservative_down(self) -> None:
        h = probe_order_link(_FakeManager(False, state="down"), clock=_clock)
        assert h.status == STATUS_DOWN
        assert h.trading_time is None
        assert any("未注入" in n for n in h.notes)

    def test_trading_checker_exception_conservative_down(self) -> None:
        def boom() -> bool:
            raise RuntimeError("calendar down")

        h = probe_order_link(_FakeManager(False, state="down"), is_trading_time=boom, clock=_clock)
        assert h.status == STATUS_DOWN
        assert h.trading_time is None
        assert any("异常" in n for n in h.notes)

    def test_ready_ignores_trading_checker(self) -> None:
        # 通道就绪时不依赖交易时段判定（非交易时段 CONNECTED 同样 healthy）
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: False, clock=_clock)
        assert h.status == STATUS_HEALTHY


# ----------------------------------------------------------------------
# 延迟探针注入位
# ----------------------------------------------------------------------


class TestLatencyProbe:
    def test_latency_passthrough(self) -> None:
        h = probe_order_link(
            _FakeManager(True),
            is_trading_time=lambda: True,
            latency_probe=lambda: {"order_ms": 12.5, "report_ms": 30},
            clock=_clock,
        )
        assert h.latency_ms == {"order_ms": 12.5, "report_ms": 30.0}

    def test_latency_not_injected_noted(self) -> None:
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: True, clock=_clock)
        assert h.latency_ms == {}
        assert any("延迟" in n for n in h.notes)

    def test_latency_exception_does_not_break_probe(self) -> None:
        def boom() -> dict:
            raise RuntimeError("latency probe down")

        h = probe_order_link(
            _FakeManager(True),
            is_trading_time=lambda: True,
            latency_probe=boom,
            clock=_clock,
        )
        assert h.status == STATUS_HEALTHY
        assert h.latency_ms == {}
        assert any("延迟探针异常" in n for n in h.notes)


# ----------------------------------------------------------------------
# 通道读取异常与瘦鸭型
# ----------------------------------------------------------------------


class TestReadFailures:
    def test_status_read_exception_is_error_not_raise(self) -> None:
        h = probe_order_link(
            _FakeManager(True, status_raises=True),
            is_trading_time=lambda: True,
            clock=_clock,
        )
        assert h.status == STATUS_ERROR
        assert any("读取异常" in n for n in h.notes)

    def test_lean_manager_without_status_snapshot(self) -> None:
        h = probe_order_link(_LeanManager(False), is_trading_time=lambda: False, clock=_clock)
        assert h.status == STATUS_CLOSED
        assert h.channel_state == "unknown"
        assert any("status()" in n for n in h.notes)


# ----------------------------------------------------------------------
# 契约
# ----------------------------------------------------------------------


class TestContract:
    def test_source_health_family_fields(self) -> None:
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: True, clock=_clock)
        assert h.source == "miniqmt_order_link"
        assert h.timestamp == _FIXED_NOW.isoformat()
        d = h.to_dict()
        assert {"source", "status", "timestamp"} <= set(d)

    def test_to_dict_json_serializable(self) -> None:
        h = probe_order_link(
            _FakeManager(False, state="down", hb=3, ra=3),
            is_trading_time=lambda: True,
            latency_probe=lambda: {"order_ms": 9.9},
            clock=_clock,
        )
        json.dumps(h.to_dict(), ensure_ascii=False)

    def test_health_frozen(self) -> None:
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: True, clock=_clock)
        with pytest.raises(Exception):
            h.status = STATUS_DOWN  # type: ignore[misc]

    def test_custom_source_name(self) -> None:
        h = probe_order_link(
            _FakeManager(True),
            is_trading_time=lambda: True,
            clock=_clock,
            source="miniqmt_order_link_paper",
        )
        assert h.source == "miniqmt_order_link_paper"

    def test_return_type(self) -> None:
        h = probe_order_link(_FakeManager(True), is_trading_time=lambda: True, clock=_clock)
        assert isinstance(h, OrderLinkHealth)
        assert h.status in {STATUS_HEALTHY, STATUS_DEGRADED, STATUS_CLOSED, STATUS_DOWN, STATUS_ERROR}
