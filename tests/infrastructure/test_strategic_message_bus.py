# [BLUEPRINT] MOD-INF-090 | docs/03_modules/_domain_infrastructure_operations/strategic_message_bus/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-090 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_strategic_message_bus
# [TESTS] src/zephyr/infrastructure/a2a_protocol/strategic_message_bus.py
"""MOD-INF-090 单元测试：strategic_message_bus 战略层三层逻辑消息总线。

蓝图验收（B11-02493/CAND-INFRAA2A-002，A7-Agent架构）：
strategic.*/tactical.*/execution.* 三层 topic 命名空间校验 + 发布订阅权限
按 Agent 层级校验（层级表注入）+ 跨层消息强制 A2A 检查网关（未注入
Fail-Closed）+ 层内直连层间留痕审计。网关/审计/时钟全注入内存替身，不
触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.strategic_message_bus",
    reason="strategic_message_bus not importable",
)

from zephyr.infrastructure.a2a_protocol.strategic_message_bus import (  # noqa: E402
    BusAudit,
    BusLayer,
    StrategicBusError,
    StrategicMessageBus,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_AGENTS = {
    "risk_manager": BusLayer.STRATEGIC,
    "signal_analyst": BusLayer.TACTICAL,
    "t0_trader": BusLayer.EXECUTION,
}


def _bus(
    gateway="default",
    audits: list | None = None,
    layer: BusLayer = BusLayer.STRATEGIC,
) -> StrategicMessageBus:
    return StrategicMessageBus(
        layer=layer,
        agent_layers=_AGENTS,
        a2a_gateway=(lambda a, t, p: True) if gateway == "default" else gateway,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruct:
    def test_invalid_layer_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            StrategicMessageBus(layer="strategic", agent_layers=_AGENTS)

    def test_empty_agents_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            StrategicMessageBus(layer=BusLayer.STRATEGIC, agent_layers={})

    def test_invalid_agent_layer_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            StrategicMessageBus(layer=BusLayer.STRATEGIC, agent_layers={"a": "strategic"})

    def test_layer_property(self) -> None:
        assert _bus(layer=BusLayer.TACTICAL).layer is BusLayer.TACTICAL


# ──────────────────────────────────────────────────────────────────────────────
# topic 命名空间校验
# ──────────────────────────────────────────────────────────────────────────────


class TestTopicNamespace:
    def test_empty_topic_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().publish("risk_manager", "", {})

    def test_unknown_prefix_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().publish("risk_manager", "ops.metrics", {})

    def test_no_separator_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().publish("risk_manager", "strategic", {})

    def test_all_legal_prefixes(self) -> None:
        bus = _bus()
        for topic, path in [
            ("strategic.risk", "intra_layer"),     # 战略 Agent 发战略 topic → 层内
            ("tactical.signal", "cross_layer"),    # 跨层 → 网关
            ("execution.order", "cross_layer"),
        ]:
            assert bus.publish("risk_manager", topic, {}) == path


# ──────────────────────────────────────────────────────────────────────────────
# 订阅权限
# ──────────────────────────────────────────────────────────────────────────────


class TestSubscribe:
    def test_subscribe_ok(self) -> None:
        bus = _bus()
        bus.subscribe("risk_manager", "strategic.risk", lambda p: None)
        assert bus.subscriber_count("strategic.risk") == 1

    def test_unknown_agent_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().subscribe("ghost", "strategic.risk", lambda p: None)

    def test_cross_layer_subscribe_rejected(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().subscribe("t0_trader", "strategic.risk", lambda p: None)

    def test_subscribe_same_layer_other_bus_topic_ok(self) -> None:
        bus = _bus(layer=BusLayer.TACTICAL)
        bus.subscribe("signal_analyst", "tactical.signal", lambda p: None)
        assert bus.subscriber_count("tactical.signal") == 1


# ──────────────────────────────────────────────────────────────────────────────
# 发布：层内直连
# ──────────────────────────────────────────────────────────────────────────────


class TestPublishIntra:
    def test_delivered_to_handlers(self) -> None:
        got: list = []
        bus = _bus()
        bus.subscribe("risk_manager", "strategic.risk", lambda p: got.append(p))
        assert bus.publish("risk_manager", "strategic.risk", {"cap": 0.05}) == "intra_layer"
        assert got == [{"cap": 0.05}]

    def test_intra_audit_trail(self) -> None:
        audits: list[BusAudit] = []
        bus = _bus(audits=audits)
        bus.publish("risk_manager", "strategic.risk", {})
        assert len(audits) == 1
        assert audits[0].path == "intra_layer"
        assert audits[0].topic == "strategic.risk"
        assert audits[0].at == _T0

    def test_no_subscribers_still_intra(self) -> None:
        assert _bus().publish("risk_manager", "strategic.idle", {}) == "intra_layer"

    def test_unknown_agent_publish_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().publish("ghost", "strategic.risk", {})

    def test_none_payload_raises(self) -> None:
        with pytest.raises(StrategicBusError):
            _bus().publish("risk_manager", "strategic.risk", None)


# ──────────────────────────────────────────────────────────────────────────────
# 发布：跨层强制 A2A 网关
# ──────────────────────────────────────────────────────────────────────────────


class TestPublishCross:
    def test_gateway_missing_fail_closed(self) -> None:
        bus = _bus(gateway=None)
        with pytest.raises(StrategicBusError):
            bus.publish("risk_manager", "tactical.signal", {})

    def test_cross_routed_via_gateway_with_audit(self) -> None:
        seen: list = []
        audits: list[BusAudit] = []
        bus = _bus(gateway=lambda a, t, p: seen.append((a, t, p)) or True, audits=audits)
        assert bus.publish("risk_manager", "execution.order", {"qty": 100}) == "cross_layer"
        assert seen == [("risk_manager", "execution.order", {"qty": 100})]
        assert audits[-1].path == "cross_layer"

    def test_gateway_reject_raises(self) -> None:
        bus = _bus(gateway=lambda a, t, p: False)
        with pytest.raises(StrategicBusError):
            bus.publish("risk_manager", "tactical.signal", {})

    def test_gateway_exception_raises(self) -> None:
        def _boom(a: str, t: str, p: dict) -> bool:
            raise RuntimeError("net")

        with pytest.raises(StrategicBusError):
            _bus(gateway=_boom).publish("risk_manager", "tactical.signal", {})

    def test_tactical_instance_intra(self) -> None:
        got: list = []
        bus = _bus(layer=BusLayer.TACTICAL)
        bus.subscribe("signal_analyst", "tactical.signal", lambda p: got.append(p))
        assert bus.publish("signal_analyst", "tactical.signal", {"s": 1}) == "intra_layer"
        assert got == [{"s": 1}]
