# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_pipeline_events
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.pipeline_events
# [CONSUMERS] MOD-BT-190 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（monkeypatch JOURNAL/RECEIPT 到 tmp_path）；KillSwitch 探针可注入
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/pipeline_events.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-190 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pipeline_events 测试——事件不丢/KillSwitch 停留/毒丸/重 kind 延迟/扫描幂等（交接清单①⑬验收）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import pipeline_events as pe  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_phase2a_judgment_hooks(monkeypatch):
    """判定台账 Phase 2a 挂点测试隔离（2026-09-17 三连发事故修复）。

    wire_data_scheduler 的 _on_task_completed 会惰性 import 并执行
    plan_engine 的两个判定产出钩子——本文件的 wire 测试触发该回调时，
    钩子若未隔离会走真库（读 kline_index→查重→emit_judgment 真实发射，
    synthetic=0 生产行）。autouse patch 拦在源头：判定发射是生产副作用，
    测试进程零豁免。
    """
    monkeypatch.setattr(
        "zephyr.plan_engine.intraday_l1_tracker.maybe_track_intraday_state",
        lambda *a, **k: {"action": "skipped_test_isolation"})
    monkeypatch.setattr(
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast",
        lambda *a, **k: {"action": "skipped_test_isolation"})


@pytest.fixture()
def state(tmp_path, monkeypatch):
    monkeypatch.setattr(pe, "STATE_DIR", tmp_path)
    monkeypatch.setattr(pe, "JOURNAL", tmp_path / "pending_events.jsonl")
    monkeypatch.setattr(pe, "RECEIPT", tmp_path / "last_receipt.json")
    return tmp_path


class TestJournal:
    def test_record_and_pending_roundtrip(self, state):
        evt = pe.record("c4_batch_completed", {"batch": "B1", "inserted": 3})
        assert evt["id"].startswith("PIPE-")
        evts = pe.pending()
        assert len(evts) == 1 and evts[0]["payload"]["batch"] == "B1"

    def test_drain_success_dequeues(self, state, monkeypatch):
        pe.record("c4_batch_completed", {"batch": "B1"})
        seen = []
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        r = pe.drain(handler=lambda e: seen.append(e["id"]) or {"ok": True})
        assert seen and r["processed"] and r["pending_left"] == 0
        assert json.loads((state / "last_receipt.json").read_text(encoding="utf-8"))["processed"]

    def test_killswitch_retains_event(self, state, monkeypatch):
        # 红蓝：KillSwitch 中途触发→事件零丢失，恢复后重放
        pe.record("c4_batch_completed", {"batch": "B1"})
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (False, "tripped"))
        r = pe.drain(handler=lambda e: (_ for _ in ()).throw(AssertionError("不应消费")))
        assert r["stop_reason"] == "tripped" and r["pending_left"] == 1
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        r2 = pe.drain(handler=lambda e: {"ok": True})
        assert r2["processed"] and r2["pending_left"] == 0

    def test_failure_keeps_and_counts_attempts(self, state, monkeypatch):
        pe.record("c4_batch_completed", {"batch": "B1"})
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        calls = []

        def boom(e):
            calls.append(1)
            raise RuntimeError("ch down")

        r = pe.drain(handler=boom)
        assert r["failed"] and r["pending_left"] == 1 and len(calls) == 1  # 一次 drain 只试一次
        r2 = pe.drain(handler=boom)
        evts = pe.pending()
        assert evts[0]["attempts"] == 2
        r3 = pe.drain(handler=boom)
        evts = pe.pending()
        assert evts[0]["attempts"] == 3 and evts[0].get("poison") is True  # 毒丸留档
        # 毒丸不再自动消费
        r4 = pe.drain(handler=lambda e: {"ok": True})
        assert r4["pending_left"] == 1 and any(s.get("why") == "poison_held" for s in r4["skipped"])

    def test_heavy_kind_deferred_on_light_drain(self, state, monkeypatch):
        # 调度器唤醒（allow_heavy=False）不消费重 kind；显式 drain 消费
        pe.record("c4_batch_due", {"files": ["c4_x.py"]})
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        r = pe.drain(handler=lambda e: {"ok": True})
        assert r["pending_left"] == 1
        r2 = pe.drain(allow_heavy=True, handler=lambda e: {"ran": True})
        assert r2["processed"] and r2["pending_left"] == 0


class TestWiring:
    def test_wire_data_scheduler_subscribes(self, state, marker, monkeypatch):
        class FakeScheduler:
            def __init__(self):
                self.handlers = {}

            def subscribe(self, event, handler):
                self.handlers[event] = handler

        s = FakeScheduler()
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "scan_translated_backlog", lambda: {"backlog": []})
        monkeypatch.setattr(pe, "scan_c1_c2_backlog", lambda: {})
        _stub_executors(monkeypatch)
        pe.wire_data_scheduler(s)
        assert "task_completed" in s.handlers
        s.handlers["task_completed"](task_id="x", success=True)  # 永不抛
        assert (state / "last_receipt.json").exists()

    def test_hook_never_raises(self, state, marker, monkeypatch):
        class FakeScheduler:
            def subscribe(self, event, handler):
                self.h = handler

        monkeypatch.setattr(pe, "scan_translated_backlog",
                            lambda: (_ for _ in ()).throw(RuntimeError("ch down")))
        s = FakeScheduler()
        pe.wire_data_scheduler(s)
        s.h()  # 扫描炸了也不反噬调度器


class TestScanBacklog:
    def test_backlog_detected_and_deduped(self, state, monkeypatch):
        root = state / "repo"
        (root / "scripts/backtest/translated").mkdir(parents=True)
        (root / "scripts/backtest/translated/c4_newone.py").write_text("# new", encoding="utf-8")
        monkeypatch.setattr(pe, "ROOT", root)
        monkeypatch.setattr(pe, "STATE_DIR", state)
        monkeypatch.setattr(pe, "JOURNAL", state / "pending_events.jsonl")

        class FakeClient:
            def execute(self, sql):
                return [("scripts/backtest/translated/c4_known.py",)]

        import zephyr.data.ch_writer as cw
        monkeypatch.setattr(cw, "get_client_strict", lambda: FakeClient())
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        r1 = pe.scan_translated_backlog()
        assert r1["backlog"] == ["c4_newone.py"]
        r2 = pe.scan_translated_backlog()
        assert r2.get("already_recorded") is True  # 幂等：同集合不重复入队
        kinds = [e["kind"] for e in pe.pending()]
        assert kinds == ["c4_batch_due"]


# ---------- S08/S09/S10 C1+C2：模拟盘开户/日件/月度件（全部 tmp_path+mock，零生产 IO） ----------
@pytest.fixture()
def marker(tmp_path, monkeypatch):
    """AUDIT_MARKER 指 tmp（state fixture 不覆盖它，防写生产 last_audit.json）。"""
    m = tmp_path / "last_audit.json"
    monkeypatch.setattr(pe, "AUDIT_MARKER", m)
    return m


def _stub_executors(monkeypatch):
    """钩子内 drain 用真 _default_handler——所有可达执行体必须 stub（测试零生产 IO 铁律）。

    pf_alloc 两件套（清单 #15 起唤醒钩子会解析业务日并入队分配件）：业务日桩固定回一个
    合法日、执行体桩只回 rc——真 CH/真子进程都不得进测试。
    regime 日序供给（挖矿 F3 起同一唤醒点先刷新 regime_snapshot_history）：整件打桩——
    真实现会查 CH 新鲜度并可能起分钟级全窗重印子进程（真件回归见
    tests/pf_alloc/test_pf_alloc_event_wiring.py ⑧ 族）。
    """
    monkeypatch.setattr(pe, "run_mount_audit", lambda: {"audit": "stub"})
    monkeypatch.setattr(pe, "run_sim_memo", lambda: {"memo": "stub"})
    monkeypatch.setattr(pe, "run_sim_ledger_daily", lambda p: {"rc": 0})
    monkeypatch.setattr(pe, "run_sim_journal_daily", lambda p: {"rc": 0})
    monkeypatch.setattr(pe, "run_sim_deviation_monthly", lambda p: {"rc": 0, "month": "2026-08"})
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
    monkeypatch.setattr(pe, "maybe_refresh_regime_snapshot", lambda **kw: {"action": "fresh"})
    monkeypatch.setattr(pe, "run_pf_alloc_daily", lambda p: {"rc": 0, "trade_date": "2026-09-15"})
    monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)


class TestMonthlyMarker:
    """月度档病根修复验收：marker 触发一次/重跑不重触发/毒丸不堵队/sim_memo handler 落 marker。"""

    def test_monthly_emits_once_then_pending_dedup(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        r1 = pe.maybe_emit_monthly()
        assert {"mount_audit_monthly", "sim_memo_monthly", "sim_deviation_monthly"} <= set(r1["emitted"])
        r2 = pe.maybe_emit_monthly()  # 同月非 poison 在队=去重
        assert r2["emitted"] == []

    def test_marker_blocks_reemission_after_success(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        pe._touch_marker("sim_memo")  # 模拟消费成功（handler 现在会落 marker——病根修复）
        pe._touch_marker("sim_deviation")
        r = pe.maybe_emit_monthly()
        assert "sim_memo_monthly" not in r["emitted"]
        assert "sim_deviation_monthly" not in r["emitted"]
        assert "mount_audit_monthly" in r["emitted"]  # mount 无 marker 仍到期

    def test_poison_does_not_block_monthly_forever(self, state, marker, monkeypatch):
        """毒丸不算"已入队"（否则毒丸行永久堵死月度档——sim_memo 病根之二）。"""
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        evt = pe.record("sim_memo_monthly", {})
        evts = pe.pending()
        evts[0]["poison"] = True
        pe._rewrite(evts)
        r = pe.maybe_emit_monthly()
        assert "sim_memo_monthly" in r["emitted"]  # 毒丸堵不死，重发可消费
        assert any(not e.get("poison") for e in pe.pending()
                   if e["kind"] == "sim_memo_monthly")

    def test_sim_memo_handler_touches_marker(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "run_sim_memo", lambda: {"ok": True})
        pe._default_handler({"id": "X", "kind": "sim_memo_monthly", "payload": {}})
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert "sim_memo" in data  # 病根主因：此前 handler 从不落 marker


class TestSimDailyWiring:
    """日件：daily_kline SUCCESS 唤醒入队/双闸幂等/FIFO 顺序/wire 钩子串联。"""

    def test_daily_emits_on_kline_success_in_order(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        r = pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == ["sim_ledger_daily", "sim_journal_daily"]  # 账本先行
        r2 = pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=True)
        assert r2["emitted"] == []  # 非 poison 在队=去重

    def test_daily_wakes_on_index_kline_too(self, state, marker, monkeypatch):
        """指数日K（账本直读行情）同为唤醒源；非 kline 任务不唤醒。"""
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        r = pe.maybe_emit_sim_daily(task_id="kline_index_incremental", success=True)
        assert r["emitted"] == ["sim_ledger_daily", "sim_journal_daily"]

    def test_daily_skips_non_kline_and_failed_tasks(self, state, marker):
        assert pe.maybe_emit_sim_daily(task_id="stock_list_daily", success=True)["emitted"] == []
        assert pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=False)["emitted"] == []
        assert pe.maybe_emit_sim_daily()["emitted"] == []

    def test_date_marker_blocks_reemission(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        pe._touch_marker("sim_ledger_daily")
        r = pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == ["sim_journal_daily"]  # 只有未落 marker 的 journal 件入队

    def test_wire_hook_enqueues_daily_and_drains(self, state, marker, monkeypatch):
        """端到端（执行体全 stub）：唤醒→入队 FIFO→drain 串行消费→date-marker 落盘。"""
        class FakeScheduler:
            def subscribe(self, event, handler):
                self.h = handler

        order = []
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "scan_translated_backlog", lambda: {"backlog": []})
        monkeypatch.setattr(pe, "scan_c1_c2_backlog", lambda: {})
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        _stub_executors(monkeypatch)

        def ledger_stub(p):
            order.append("ledger")
            return {"rc": 0}

        def journal_stub(p):
            order.append("journal")
            return {"rc": 0}

        monkeypatch.setattr(pe, "run_sim_ledger_daily", ledger_stub)
        monkeypatch.setattr(pe, "run_sim_journal_daily", journal_stub)
        s = FakeScheduler()
        pe.wire_data_scheduler(s)
        s.h(task_id="kline_daily_incremental", success=True)
        assert order == ["ledger", "journal"]  # FIFO 串行=日刊必见当日账本
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert "sim_ledger_daily" in data and "sim_journal_daily" in data  # 消费成功才落 marker
        # 全部轻 kind 消费完毕（月度件 marker 未到期不再发/或被 stub handler 消费）
        assert all(e["kind"] not in ("sim_ledger_daily", "sim_journal_daily")
                   for e in pe.pending())


class TestSimHandlers:
    """kind 派发 mock：开户/日件 handler 串联 + 预埋派发缺失跳过/交付即跑。"""

    def test_wallet_due_dispatch(self, state, monkeypatch):
        seen = {}

        def fake_run(p):
            seen["p"] = p
            return {"opened": ["S1"]}

        monkeypatch.setattr(pe, "run_sim_wallet_due", fake_run)
        out = pe._default_handler({"id": "X", "kind": "sim_wallet_due",
                                   "payload": {"strategies": [{"strategy_id": "S1", "code_path": "a"}]}})
        assert out == {"opened": ["S1"]} and seen["p"]["strategies"][0]["strategy_id"] == "S1"

    def test_daily_handlers_touch_date_markers_on_success(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "run_sim_ledger_daily", lambda p: {"rc": 0})
        monkeypatch.setattr(pe, "run_sim_journal_daily", lambda p: {"rc": 0})
        pe._default_handler({"id": "X", "kind": "sim_ledger_daily", "payload": {}})
        pe._default_handler({"id": "Y", "kind": "sim_journal_daily", "payload": {}})
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert "sim_ledger_daily" in data and "sim_journal_daily" in data

    def test_optional_due_missing_module_skips(self, state, marker, monkeypatch):
        """契约预埋：实现模块缺失=log-and-skip（不抛、可出队，不占 attempts）。

        S12 C4 交付后 promotion_advisory 模块已存在（真派发会读真仓写真盘）——本用例按原意
        改指缺失桩模块验证 skip 语义（适配留痕：Y1 st-fullauto-20260915）。
        """
        monkeypatch.setitem(pe.OPTIONAL_DUE_KINDS, "fw_backtest_due",
                            ("zephyr.strategy_pipeline._definitely_missing_xyz", "run_fw_backtest_due"))
        monkeypatch.setitem(pe.OPTIONAL_DUE_KINDS, "promotion_advisory_due",
                            ("zephyr.strategy_pipeline._definitely_missing_xyz", "run_promotion_advisory_due"))
        out = pe._default_handler({"id": "X", "kind": "fw_backtest_due", "payload": {}})
        assert out["skipped"] == "module_not_ready"
        out2 = pe._default_handler({"id": "Y", "kind": "promotion_advisory_due", "payload": {}})
        assert out2["skipped"] == "module_not_ready"

    def test_optional_due_delivered_module_runs(self, state, marker, monkeypatch):
        """实现交付后：同契约直接执行（模块路径+run_xxx_due(event)->dict）。"""
        import types

        fake = types.ModuleType("zephyr.strategy_pipeline.fw_backtest")
        fake.run_fw_backtest_due = lambda event: {"ran": event["id"]}
        monkeypatch.setitem(sys.modules, "zephyr.strategy_pipeline.fw_backtest", fake)
        out = pe._default_handler({"id": "E1", "kind": "fw_backtest_due", "payload": {}})
        assert out == {"ran": "E1"}


class TestEmitSimWalletDue:
    """intake 开户钩子（c4 同款 record+立即轻消费）：失败留 journal 不反噬。"""

    def test_emit_and_drain(self, state, monkeypatch):
        monkeypatch.setattr(pe, "drain", lambda allow_heavy: {"processed": 1})
        out = pe.emit_sim_wallet_due([{"strategy_id": "S1", "code_path": "a.py"}])
        assert out["drained"] is True
        evts = pe.pending()
        assert evts[0]["kind"] == "sim_wallet_due"
        assert evts[0]["payload"]["strategies"] == [{"strategy_id": "S1", "code_path": "a.py"}]

    def test_emit_drain_failure_keeps_event(self, state, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append(msg))
        def boom(allow_heavy):
            raise RuntimeError("ch down")
        monkeypatch.setattr(pe, "drain", boom)
        out = pe.emit_sim_wallet_due([{"strategy_id": "S1"}])
        assert out["drained"] is False and pe.pending()
        assert alerts and "sim_wallet_due" in alerts[0]
