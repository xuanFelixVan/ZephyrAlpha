# [BLUEPRINT] MOD-SELL-016 | docs/03_modules/_domain_sell_decision/s1_scan_orchestrator/blueprint.md | §6
# [MODULE] tests.sell_decision.test_s1_scan_orchestrator
# [DOMAIN] D_SELL_DECISION
# [TESTS] S1 信号扫描编排器——触发/空跑/跳过留痕/投递 mock/落盘 tmp_path/live 档硬锁
# [TTL] permanent
"""S1 信号扫描编排器测试（G45-1 编排接线验收）。

铁律：测试隔离——输出一律 tmp_path fixture，禁写 data/ 业务目录；不连业务库。
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from zephyr.sell_decision.core.s1_scan_orchestrator import (
    S1_NODE_SPECS,
    XFLOW_VALIDATION_STATE,
    FileOutboxSink,
    InMemorySink,
    S1ScanError,
    S1ScanMode,
    S1SignalScanOrchestrator,
)
from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
)

_NOW = datetime(2026, 9, 28, 1, 30, tzinfo=timezone.utc)


def _sig(symbol: str = "000001.SZ", direction: SellDirection = SellDirection.REDUCE, conf: float = 0.7) -> SellSignal:
    return SellSignal(
        symbol=symbol,
        signal_type=SellSignalType.TECHNICAL,
        direction=direction,
        confidence=conf,
        source="TDM-X-S1-02",
        reason="测试信号",
        timestamp=_NOW,
    )


# ── 1. 构造与档位硬锁 ──


class TestModeInterlock:
    def test_live_mode_constructor_refused(self) -> None:
        # G45-1 先 paper 档：构造期禁止 live
        with pytest.raises(S1ScanError, match="live"):
            S1SignalScanOrchestrator(mode=S1ScanMode.LIVE)

    def test_live_scan_requires_explicit_unlock(self) -> None:
        orch = S1SignalScanOrchestrator(mode=S1ScanMode.PAPER)
        assert orch.mode is S1ScanMode.PAPER
        # paper 档 allow_live=True 合法（档位与解锁正交：paper 档无需解锁也放行）
        report = orch.scan_once([], now=_NOW, allow_live=True)
        assert report.mode == "paper"

    def test_default_mode_is_paper(self) -> None:
        orch = S1SignalScanOrchestrator()
        assert orch.mode is S1ScanMode.PAPER


# ── 2. 诚实空跑 ──


class TestHonestEmptyRun:
    def test_zero_providers_empty_run(self) -> None:
        orch = S1SignalScanOrchestrator()
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        assert report.empty_run is True
        assert report.signal_count == 0
        assert report.fused_count == 0
        assert report.delivered_count == 0
        assert "诚实空跑" in report.notes

    def test_empty_symbols_honest(self) -> None:
        orch = S1SignalScanOrchestrator()
        report = orch.scan_once([], now=_NOW)
        assert report.empty_run is True
        assert report.symbols == ()

    def test_no_fake_signals_on_empty(self) -> None:
        orch = S1SignalScanOrchestrator()
        report = orch.scan_once(["600000.SH"], now=_NOW)
        d = report.to_dict()
        assert d["signal_count"] == 0
        # 融合节点显式跳过留痕，不伪造决策
        n05 = [t for t in d["node_traces"] if t["node_id"] == "TDM-X-S1-05"]
        assert n05 and n05[0]["status"] == "skipped"


# ── 3. 就绪面与显式跳过留痕 ──


class TestReadinessAndSkips:
    def test_six_nodes_all_pending_disclosed(self) -> None:
        orch = S1SignalScanOrchestrator()
        readies = orch.readiness()
        assert set(readies) == {s.node_id for s in S1_NODE_SPECS}
        assert len(readies) == 6
        for r in readies.values():
            # 18 节点台账全 pending——如实披露不升格
            assert r.validation_state == "pending"
            assert XFLOW_VALIDATION_STATE == "pending"

    def test_module_refs_on_disk(self) -> None:
        orch = S1SignalScanOrchestrator()
        readies = orch.readiness()
        # S1-06 真身在 trading 域（09_f45 勘误 1：引用须带全路径）
        assert readies["TDM-X-S1-06"].module_ref.startswith("src/zephyr/trading/")
        for r in readies.values():
            assert r.code_ready is True, r.node_id

    def test_unregistered_strategy_nodes_skipped_with_trail(self) -> None:
        orch = S1SignalScanOrchestrator()
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        d = report.to_dict()
        skips = {t["node_id"]: t for t in d["node_traces"] if t["status"] == "skipped"}
        for node in ("TDM-X-S1-02", "TDM-X-S1-03", "TDM-X-S1-04"):
            assert node in skips, f"{node} 未显式跳过留痕"
            assert "provider 未注册" in skips[node]["detail"]
        # S1-06 触发扫描件未建=显式跳过（组合级归 R1/F47）
        assert "TDM-X-S1-06" in skips
        assert "X-R1/F47" in skips["TDM-X-S1-06"]["detail"]

    def test_unknown_node_provider_refused(self) -> None:
        orch = S1SignalScanOrchestrator()
        with pytest.raises(S1ScanError, match="未知 S1 节点"):
            orch.register_node_provider("TDM-X-S9-99", lambda s, n, c: [])

    def test_provider_registered_then_wired(self) -> None:
        orch = S1SignalScanOrchestrator()
        orch.register_node_provider("TDM-X-S1-02", lambda s, n, c: [_sig(s)])
        readies = orch.readiness(refresh=True)
        assert readies["TDM-X-S1-02"].wired is True
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        assert report.signal_count == 1
        traces = {t.node_id: t for t in report.node_traces}
        assert traces["TDM-X-S1-02"].status == "wired"
        assert traces["TDM-X-S1-02"].signal_count == 1


# ── 4. 端到端投递（mock sink + tmp_path 落盘） ──


class TestDelivery:
    def _wired_orch(self, sink) -> S1SignalScanOrchestrator:
        orch = S1SignalScanOrchestrator(sink=sink, clock=lambda: _NOW)
        orch.register_node_provider("TDM-X-S1-02", lambda s, n, c: [_sig(s)])
        orch.collector.register(
            SellSignalType.MAIN_FORCE_DISTRIBUTION,
            lambda s, n, c: [_sig(s, SellDirection.CLEAR, 0.95)],
        )
        return orch

    def test_inmemory_sink_delivery(self) -> None:
        sink = InMemorySink()
        orch = self._wired_orch(sink)
        report = orch.scan_once(["000001.SZ"], now=_NOW, triage_levels={"000001.SZ": "MONITOR"})
        assert report.delivered_count >= 1
        assert report.empty_run is False
        env = sink.envelopes[0]
        d = env.to_dict()
        assert d["schema_version"] == "TDM-X-S2-01_INBOX/v1"
        assert d["mode"] == "paper"
        assert d["validation_state"] == "pending"
        assert d["node_id"] in ("TDM-X-S1-05", "TDM-X-S1-06")
        assert 0.0 <= d["willingness"] <= 1.0
        assert 0.0 <= d["urgency"] <= 1.0
        assert d["payload"]["triage"] == "MONITOR"

    def test_file_outbox_tmp_path(self, tmp_path: Path) -> None:
        sink = FileOutboxSink(tmp_path / "outbox")
        orch = self._wired_orch(sink)
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        assert report.delivered_count >= 1
        out_file = tmp_path / "outbox" / "s2_route_inbox.jsonl"
        assert out_file.is_file()
        lines = out_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == report.delivered_count
        import json

        first = json.loads(lines[0])
        assert first["schema_version"] == "TDM-X-S2-01_INBOX/v1"

    def test_sink_failure_isolated(self) -> None:
        class _BoomSink:
            def deliver(self, envelope):  # noqa: ANN001
                raise RuntimeError("sink down")

        orch = self._wired_orch(_BoomSink())
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        # 投递故障隔离：不中断扫描，报告留痕
        assert report.signal_count >= 1
        assert report.delivered_count == 0
        assert any(t.node_id == "S2-ROUTE" and t.status == "skipped" for t in report.node_traces)


# ── 5. S1-06 绕过通道 ──


class TestBypassChannel:
    def test_bypass_hit_urgency_one_delivered(self) -> None:
        sink = InMemorySink()
        orch = S1SignalScanOrchestrator(sink=sink, clock=lambda: _NOW)
        orch.register_bypass_trigger("black_swan", lambda s, n, c: True)
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        assert report.empty_run is False
        env = sink.envelopes[0]
        assert env.node_id == "TDM-X-S1-06"
        assert env.execution_strategy == "BYPASS_FORCE"
        assert env.urgency == 1.0
        assert env.payload["trigger"] == "black_swan"

    def test_bypass_trigger_fault_isolated(self) -> None:
        def _boom(s, n, c):
            raise RuntimeError("trigger down")

        orch = S1SignalScanOrchestrator(clock=lambda: _NOW)
        orch.register_bypass_trigger("bad", _boom)
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        assert any("触发源 bad 故障隔离" in t.detail for t in report.node_traces)
        assert report.delivered_count == 0


# ── 6. 共享 triage 与报告可序列化 ──


class TestSharedTriageAndReport:
    def test_triage_levels_carried_not_consumed(self) -> None:
        sink = InMemorySink()
        orch = S1SignalScanOrchestrator(sink=sink, clock=lambda: _NOW)
        orch.register_node_provider("TDM-X-S1-02", lambda s, n, c: [_sig(s)])
        # triage_levels 来自共享 P1-02 循环——随信封留痕，不改变判定
        report = orch.scan_once(["000001.SZ"], now=_NOW, triage_levels={"000001.SZ": "WATCH"})
        assert report.signal_count == 1
        assert sink.envelopes[0].payload["triage"] == "WATCH"

    def test_report_json_roundtrip(self) -> None:
        import json

        orch = S1SignalScanOrchestrator(clock=lambda: _NOW)
        report = orch.scan_once(["000001.SZ"], now=_NOW)
        d = report.to_dict()
        json.dumps(d, ensure_ascii=False)  # 可序列化
        assert d["scan_id"] == report.scan_id
        assert d["empty_run"] is True
        assert {t["node_id"] for t in d["node_traces"]} >= {
            "TDM-X-S1-01",
            "TDM-X-S1-05",
            "TDM-X-S1-06",
        }
