# [BLUEPRINT] MOD-ORCH-001 | docs/03_modules/_domain_orchestrator/layered_command_chain/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ORCH-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.orchestrator.test_layered_command_chain
# [TESTS] src/zephyr/orchestrator/layered_command_chain.py
"""MOD-ORCH-001 单元测试：layered_command_chain Agent 分层指挥链。

蓝图验收（B11-02451/CAND-ORCH-001，A7 §0边界声明/§1）：
战略→战术→执行三层委托协议（TaskPacket/ResultReport Schema）+
指挥链注册（越层注册拒绝+告警）+ 层间通信强制 A2A 网关（未注入 Fail-Closed）+
越层/未注册直连拒绝并告警 + packet 状态机 + 查询确定性排序。
网关/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.orchestrator.layered_command_chain",
    reason="layered_command_chain not importable",
)

from zephyr.orchestrator.layered_command_chain import (  # noqa: E402
    ChainLayer,
    ChainViolation,
    CommandChainError,
    LayeredCommandChain,
    PacketStatus,
    ReportStatus,
    ResultReport,
    TaskPacket,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_LAYERS = {
    "risk_manager": ChainLayer.STRATEGIC,
    "signal_analyst": ChainLayer.TACTICAL,
    "timing_analyst": ChainLayer.TACTICAL,
    "t0_trader": ChainLayer.EXECUTION,
}


def _chain(
    alerts: list | None = None,
    gateway=None,
    gateway_ok: bool = True,
) -> LayeredCommandChain:
    return LayeredCommandChain(
        agent_layers=_LAYERS,
        clock=lambda: _T0,
        a2a_gateway=gateway if gateway is not None else (lambda p: gateway_ok),
        alert_sink=(lambda v: alerts.append(v)) if alerts is not None else None,
    )


def _packet(
    parent: str = "risk_manager",
    child: str = "signal_analyst",
    packet_id: str = "pkt-1",
) -> TaskPacket:
    return TaskPacket(
        packet_id=packet_id,
        parent_agent=parent,
        child_agent=child,
        objective="回撤≤5%约束下产出明日信号目标",
        constraints={"max_drawdown": 0.05},
        deadline_ts=None,
        issued_at=_T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 指挥链注册（越层拒绝+告警）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterLink:
    def test_legal_links(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")      # 战略→战术
        chain.register_link("signal_analyst", "t0_trader")         # 战术→执行
        links = chain.chain_of("signal_analyst")
        assert links.parents == ("risk_manager",)
        assert links.children == ("t0_trader",)

    def test_skip_layer_rejected_with_alert(self) -> None:
        alerts: list[ChainViolation] = []
        chain = _chain(alerts)
        with pytest.raises(CommandChainError):
            chain.register_link("risk_manager", "t0_trader")  # 战略→执行 越层
        assert len(alerts) == 1
        assert alerts[0].parent_agent == "risk_manager"
        assert alerts[0].child_agent == "t0_trader"
        assert "越层" in alerts[0].reason or "skip" in alerts[0].reason.lower()

    def test_upward_link_rejected(self) -> None:
        alerts: list[ChainViolation] = []
        chain = _chain(alerts)
        with pytest.raises(CommandChainError):
            chain.register_link("t0_trader", "signal_analyst")  # 执行→战术 逆向
        assert len(alerts) == 1

    def test_unknown_agent_raises(self) -> None:
        chain = _chain()
        with pytest.raises(CommandChainError):
            chain.register_link("ghost", "signal_analyst")
        with pytest.raises(CommandChainError):
            chain.register_link("risk_manager", "ghost")

    def test_duplicate_link_idempotent(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        chain.register_link("risk_manager", "signal_analyst")  # 幂等不抛
        assert chain.chain_of("signal_analyst").parents == ("risk_manager",)


# ──────────────────────────────────────────────────────────────────────────────
# 委托协议（强制 A2A 网关）
# ──────────────────────────────────────────────────────────────────────────────


class TestDelegate:
    def test_delegate_ok(self) -> None:
        sent: list[TaskPacket] = []
        chain = _chain(gateway=lambda p: sent.append(p) or True)
        chain.register_link("risk_manager", "signal_analyst")
        status = chain.delegate(_packet())
        assert status is PacketStatus.ACCEPTED
        assert sent == [_packet()]  # 经 A2A 网关传递

    def test_delegate_unregistered_link_rejected_with_alert(self) -> None:
        alerts: list[ChainViolation] = []
        chain = _chain(alerts)
        status = chain.delegate(_packet())  # 未注册链路
        assert status is PacketStatus.REJECTED
        assert len(alerts) == 1
        assert alerts[0].reason  # 留痕原因

    def test_delegate_skip_layer_rejected_with_alert(self) -> None:
        alerts: list[ChainViolation] = []
        chain = _chain(alerts)
        chain.register_link("risk_manager", "signal_analyst")
        status = chain.delegate(_packet(child="t0_trader"))  # 越层直连
        assert status is PacketStatus.REJECTED
        assert len(alerts) == 1

    def test_gateway_not_injected_fail_closed(self) -> None:
        chain = LayeredCommandChain(agent_layers=_LAYERS, clock=lambda: _T0)
        chain.register_link("risk_manager", "signal_analyst")
        with pytest.raises(CommandChainError):
            chain.delegate(_packet())

    def test_gateway_nack_rejected(self) -> None:
        chain = _chain(gateway_ok=False)
        chain.register_link("risk_manager", "signal_analyst")
        assert chain.delegate(_packet()) is PacketStatus.REJECTED

    def test_invalid_packet_raises(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        with pytest.raises(CommandChainError):
            chain.delegate(_packet(packet_id=""))


# ──────────────────────────────────────────────────────────────────────────────
# 上报协议（状态机）
# ──────────────────────────────────────────────────────────────────────────────


class TestReport:
    def _accepted(self, chain: LayeredCommandChain) -> TaskPacket:
        chain.register_link("risk_manager", "signal_analyst")
        pkt = _packet()
        assert chain.delegate(pkt) is PacketStatus.ACCEPTED
        return pkt

    def test_report_ok(self) -> None:
        chain = _chain()
        pkt = self._accepted(chain)
        chain.report(ResultReport(
            packet_id=pkt.packet_id,
            child_agent="signal_analyst",
            status=ReportStatus.COMPLETED,
            metrics={"signals": 3},
            reported_at=_T0,
        ))
        assert chain.packet_status(pkt.packet_id) is PacketStatus.REPORTED

    def test_report_unknown_packet_raises(self) -> None:
        chain = _chain()
        with pytest.raises(CommandChainError):
            chain.report(ResultReport(
                packet_id="ghost",
                child_agent="signal_analyst",
                status=ReportStatus.COMPLETED,
                metrics={},
                reported_at=_T0,
            ))

    def test_report_before_accept_raises(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        pkt = _packet()
        with pytest.raises(CommandChainError):
            chain.report(ResultReport(
                packet_id=pkt.packet_id,
                child_agent="signal_analyst",
                status=ReportStatus.COMPLETED,
                metrics={},
                reported_at=_T0,
            ))

    def test_report_child_mismatch_raises(self) -> None:
        chain = _chain()
        pkt = self._accepted(chain)
        with pytest.raises(CommandChainError):
            chain.report(ResultReport(
                packet_id=pkt.packet_id,
                child_agent="timing_analyst",  # 非受托方
                status=ReportStatus.COMPLETED,
                metrics={},
                reported_at=_T0,
            ))


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_pending_packets_order(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        p2 = _packet(packet_id="pkt-2")
        p1 = _packet(packet_id="pkt-1")
        chain.delegate(p2)
        chain.delegate(p1)
        pending = chain.pending_packets("signal_analyst")
        assert [p.packet_id for p in pending] == ["pkt-1", "pkt-2"]  # 同刻按 id 排序

    def test_pending_excludes_reported(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        pkt = _packet()
        chain.delegate(pkt)
        chain.report(ResultReport(
            packet_id=pkt.packet_id,
            child_agent="signal_analyst",
            status=ReportStatus.COMPLETED,
            metrics={},
            reported_at=_T0,
        ))
        assert chain.pending_packets("signal_analyst") == []

    def test_chain_of_full(self) -> None:
        chain = _chain()
        chain.register_link("risk_manager", "signal_analyst")
        chain.register_link("risk_manager", "timing_analyst")
        chain.register_link("signal_analyst", "t0_trader")
        links = chain.chain_of("risk_manager")
        assert links.parents == ()
        assert links.children == ("signal_analyst", "timing_analyst")  # 确定性排序
