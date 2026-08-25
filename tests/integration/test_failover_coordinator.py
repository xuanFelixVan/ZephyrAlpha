# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [TTL] permanent
"""FailoverCoordinator 测试（B1-00329 / CAND-BACL-002 / D-INT-26）。

测试内容（真实 CircuitBreakerRegistry + 假时钟，内存事件总线与审计 sink）：
- 三源优先级：初始选最高优先级健康源；主源熔断 → 按优先级切换
- 质量分动态切换：现役源质量分跌破阈值 → 切向健康高质源；恢复 → 自动回切
- 切换事件广播：EventBus 主题 data.failover.switch + 负载字段
- 全部源降级超阈值：联动 trading 熔断 hook（CIRCUIT_BREAKER 级，只读/禁开仓语义），
  锁存不重复触发，恢复后复位
- 切换与联动入审计；手动强制切换；breaker 状态机集成
"""

from __future__ import annotations

import pytest

from zephyr.data.source_circuit_breaker import CircuitBreakerRegistry, CircuitState
from zephyr.integration.failover_coordinator import FailoverCoordinator
from zephyr.trading.trading_contracts.risk.trading_kill_switch import KillSwitchLevel

_SOURCES = ("tushare", "akshare", "tiingo")  # 优先级 1>2>3


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class _FakeBus:
    """内存事件总线（对齐 EventBus.emit 签名）。"""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def emit(self, topic, payload, priority=None, **kwargs):
        self.events.append({"topic": topic, "payload": payload})
        return True


@pytest.fixture
def clock():
    return _Clock()


@pytest.fixture
def bus():
    return _FakeBus()


@pytest.fixture
def kill_calls():
    return []


@pytest.fixture
def audit_events():
    return []


@pytest.fixture
def coordinator(clock, bus, kill_calls, audit_events):
    registry = CircuitBreakerRegistry(failure_threshold=3, cooldown_seconds=600.0, clock=clock)
    return FailoverCoordinator(
        sources=_SOURCES,
        breaker_registry=registry,
        degraded_score_threshold=0.5,
        event_bus=bus,
        on_all_degraded=kill_calls.append,
        audit_sink=audit_events.append,
    )


def _degrade_source(coordinator, source: str, failures: int = 3) -> None:
    """把源打到熔断 OPEN（默认连续失败 3 次达阈值）。"""
    for _ in range(failures):
        coordinator.report_failure(source)


# ── 三源优先级 ────────────────────────────────────────────


def test_initial_selects_highest_priority(coordinator):
    event = coordinator.evaluate()
    assert coordinator.active_source() == "tushare"
    assert event is not None and event.reason == "initial"


def test_primary_tripped_switch_by_priority(coordinator, bus):
    coordinator.evaluate()
    _degrade_source(coordinator, "tushare")
    event = coordinator.evaluate()
    assert coordinator.active_source() == "akshare"
    assert event.from_source == "tushare" and event.to_source == "akshare"
    assert event.reason == "source_degraded"


def test_switch_event_broadcast_payload(coordinator, bus):
    coordinator.evaluate()
    _degrade_source(coordinator, "tushare")
    coordinator.evaluate()
    switch_events = [e for e in bus.events if e["topic"] == "data.failover.switch"]
    assert switch_events
    payload = switch_events[-1]["payload"]
    assert payload["from_source"] == "tushare"
    assert payload["to_source"] == "akshare"
    assert "quality_snapshot" in payload


# ── 质量分动态切换与回切 ───────────────────────────────────


def test_quality_drop_triggers_switch(coordinator):
    coordinator.evaluate()
    coordinator.update_quality("tushare", 0.2)  # 跌破 0.5 阈值
    event = coordinator.evaluate()
    assert coordinator.active_source() == "akshare"
    assert event.reason == "source_degraded"


def test_recovery_auto_failback(coordinator, clock):
    coordinator.evaluate()
    _degrade_source(coordinator, "tushare")
    coordinator.evaluate()
    assert coordinator.active_source() == "akshare"
    # 冷却到点 → 半开探针成功 → CLOSED，质量分恢复
    clock.advance(601)
    coordinator.report_success("tushare")  # HALF_OPEN 探针成功复位
    coordinator.update_quality("tushare", 1.0)
    event = coordinator.evaluate()
    assert coordinator.active_source() == "tushare"
    assert event.reason == "auto_failback"


def test_degraded_primary_healthy_lower_priority_wins(coordinator):
    coordinator.evaluate()
    coordinator.update_quality("tushare", 0.1)
    coordinator.update_quality("akshare", 0.9)
    coordinator.evaluate()
    assert coordinator.active_source() == "akshare"


# ── 全部源降级 → 联动 trading 熔断 ─────────────────────────


def test_all_degraded_triggers_kill_switch_hook(coordinator, bus, kill_calls):
    coordinator.evaluate()
    coordinator.update_quality("tushare", 0.1)
    coordinator.update_quality("akshare", 0.2)
    coordinator.update_quality("tiingo", 0.3)
    event = coordinator.evaluate()
    assert coordinator.all_degraded() is True
    assert event.reason == "all_degraded"
    assert len(kill_calls) == 1
    assert kill_calls[0]["kill_switch_level"] == KillSwitchLevel.CIRCUIT_BREAKER.value
    assert kill_calls[0]["action"] == "read_only_no_new_position"  # 只读/禁开仓
    assert any(e["topic"] == "data.failover.all_degraded" for e in bus.events)


def test_all_degraded_latched_until_recovery(coordinator, clock, kill_calls):
    coordinator.evaluate()
    for s in _SOURCES:
        coordinator.update_quality(s, 0.1)
    coordinator.evaluate()
    coordinator.evaluate()  # 锁存：不重复联动
    assert len(kill_calls) == 1
    # 恢复一源 → 联动复位并回切
    coordinator.update_quality("tushare", 1.0)
    coordinator.evaluate()
    assert coordinator.all_degraded() is False
    assert coordinator.active_source() == "tushare"
    # 再次全降级 → 可重新联动
    for s in _SOURCES:
        coordinator.update_quality(s, 0.1)
    coordinator.evaluate()
    assert len(kill_calls) == 2


def test_all_sources_tripped_by_breaker(coordinator, clock, kill_calls):
    coordinator.evaluate()
    for s in _SOURCES:
        _degrade_source(coordinator, s)
    coordinator.evaluate()
    assert coordinator.all_degraded() is True
    assert len(kill_calls) == 1


# ── 审计 / 手动切换 / breaker 集成 ─────────────────────────


def test_switch_and_linkage_audited(coordinator, audit_events):
    coordinator.evaluate()
    _degrade_source(coordinator, "tushare")
    coordinator.evaluate()
    kinds = [e["event"] for e in audit_events]
    assert "failover.switch" in kinds
    for s in _SOURCES:
        coordinator.update_quality(s, 0.1)
    coordinator.evaluate()
    assert "failover.all_degraded" in [e["event"] for e in audit_events]


def test_manual_force_switch(coordinator):
    coordinator.evaluate()
    event = coordinator.force_switch("tiingo", reason="ops_manual")
    assert coordinator.active_source() == "tiingo"
    assert event.reason == "ops_manual"


def test_update_quality_clamped(coordinator):
    coordinator.update_quality("tushare", 1.8)
    assert coordinator.quality_of("tushare") == 1.0
    coordinator.update_quality("tushare", -0.5)
    assert coordinator.quality_of("tushare") == 0.0


def test_breaker_state_integrated(coordinator):
    coordinator.evaluate()
    _degrade_source(coordinator, "tushare")
    assert coordinator.breaker_state("tushare") is CircuitState.OPEN
