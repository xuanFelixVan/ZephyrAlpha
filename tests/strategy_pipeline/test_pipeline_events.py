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
        lambda *a, **k: {"action": "skipped_test_isolation"},
    )
    monkeypatch.setattr(
        "zephyr.plan_engine.next_day_forecaster.maybe_emit_next_day_forecast",
        lambda *a, **k: {"action": "skipped_test_isolation"},
    )
    # BT-P1-031 编排器末棒挂点同款隔离（2026-09-17 st-orchp3 二次事故修复：wire 测试
    # 触发 maybe_run_daily_decision 走真库拍板写生产 decision_daily 8 行）——autouse 拦源头
    monkeypatch.setattr(
        "zephyr.strategy_pipeline.daily_decision_orchestrator.maybe_run_daily_decision",
        lambda *a, **k: {"action": "skipped_test_isolation"},
    )
    # L9 就绪度读数末棒挂点同款隔离（2026-09-27 st-ec2-p0：wire 测试触发
    # maybe_emit_l9_readiness 走真 CH 连接（ unclosed socket ResourceWarning 升级 ERROR+
    # 拖慢全文件 70s））——autouse 拦源头；读数件自身回归归 tests/data/test_l9_readiness_aggregator.py
    monkeypatch.setattr(
        "zephyr.data.l9_readiness_aggregator.maybe_emit_l9_readiness",
        lambda *a, **k: {"action": "skipped_test_isolation"},
    )


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

    def test_rewrite_unique_tmp_no_leftover(self, state):
        """P2a 回归（st-ffchief-20261001）：_rewrite 用 pid+uuid 唯一 tmp 且零残骸。

        病根：原固定 pending_events.jsonl.tmp 多进程共用 → WinError 5/32/2
        （当日 scheduler_run.log 三种错混发）。修后：成功路径 tmp 已被
        os.replace 消费、失败路径 finally 清理——盘上任何时刻不残留 *.tmp。
        """
        pe.record("c4_batch_completed", {"batch": "B1"})
        evts = pe.pending()
        for _ in range(3):  # 多轮重写（模拟多消费轮次）
            pe._rewrite([e for e in evts if e["kind"] != "c4_batch_completed"])
            assert pe.pending() == []
        leftovers = [p.name for p in state.glob("*.tmp")]
        assert leftovers == [], f"tmp 残骸: {leftovers}"
        assert (state / "pending_events.jsonl").read_text(encoding="utf-8") == ""

    def test_journal_lock_mutex_and_timeout(self, state):
        """P2a 回归：串化闸互斥（同进程第二句柄锁同区间必须等待/失败）。

        Windows 字节区间锁对不同句柄互斥（跨进程语义的进程内等价）：
        持闸期间第二 handle 对同一字节 LK_NBLCK 必 OSError；释放后
        pe._byte_lock 可正常获取（证明锁域无 stale）。
        """
        lock_path = state / "pending_events.jsonl.gate.lock"
        with pe._byte_lock(lock_path):
            import msvcrt

            with open(lock_path, "a+b") as probe:
                probe.seek(0)
                with pytest.raises(OSError):
                    msvcrt.locking(probe.fileno(), msvcrt.LK_NBLCK, 1)
        # 释放后可再获取（OS 自动释放，无 stale 锁）
        with pe._byte_lock(lock_path):
            pass

    def test_record_under_concurrent_drain_no_tmp_collision(self, state, monkeypatch):
        """P2a 回归：record（持闸 append）与 drain（持闸 rewrite）交错零 WinError。"""
        import threading

        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        pe.record("c4_batch_completed", {"batch": "B1"})
        errors: list[Exception] = []

        def recorder():
            for i in range(20):
                try:
                    pe.record("c2_screen_due", {"sig": i})
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        def drainer():
            for _ in range(20):
                try:
                    pe.drain(handler=lambda e: {"ok": True})
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        t1, t2 = threading.Thread(target=recorder), threading.Thread(target=drainer)
        t1.start(), t2.start()
        t1.join(), t2.join()
        assert errors == [], f"并发窗口异常: {errors[:3]}"
        # 全部 record 的行要么在盘、要么已被 drain 消费（零丢失由末态账目核对）
        r = pe.drain(handler=lambda e: {"ok": True})
        assert r["pending_left"] == 0

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

        monkeypatch.setattr(pe, "scan_translated_backlog", lambda: (_ for _ in ()).throw(RuntimeError("ch down")))
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
    合法日、执行体桩只回 rc——真 CH/真子进程都不得进测试。危机闸（TC-08 段1/裁定#392-D5
    接线后发射侧会真调 pf_alloc.crisis_gate.crisis_block_check）同款隔离：闸 helper 桩恒放行，
    危机两态定向用例见 TestCrisisBlockWiring（闸真件回归归 tests/pf_alloc/ 既有族）。
    归因日账（段2 接线后 SIM_DAILY_KINDS 末位会被 drain 真消费）：执行体桩只回 rc。
    regime 日序供给（挖矿 F3 起同一唤醒点先刷新 regime_snapshot_history）：整件打桩——
    真实现会查 CH 新鲜度并可能起分钟级全窗重印子进程（真件回归见
    tests/pf_alloc/test_pf_alloc_event_wiring.py ⑧ 族）。
    """
    monkeypatch.setattr(pe, "run_mount_audit", lambda: {"audit": "stub"})
    monkeypatch.setattr(pe, "run_sim_memo", lambda: {"memo": "stub"})
    monkeypatch.setattr(pe, "run_sim_ledger_daily", lambda p: {"rc": 0})
    monkeypatch.setattr(pe, "run_sim_journal_daily", lambda p: {"rc": 0})
    monkeypatch.setattr(pe, "run_attribution_daily", lambda p: {"rc": 0, "day": "2026-09-15"})
    monkeypatch.setattr(pe, "run_sim_deviation_monthly", lambda p: {"rc": 0, "month": "2026-08"})
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
    monkeypatch.setattr(pe, "_pf_alloc_crisis_gate_skip", lambda day: None)  # 危机闸隔离=恒放行
    monkeypatch.setattr(pe, "maybe_refresh_regime_snapshot", lambda **kw: {"action": "fresh"})
    monkeypatch.setattr(pe, "run_pf_alloc_daily", lambda p: {"rc": 0, "trade_date": "2026-09-15"})
    # F82 工单守护 spawn 同款隔离：wire 测试触发 hook 不得读生产 .runtime/ai_scheduling
    # （真件回归归本文件 TestOrderDaemonSpawn，journal 注入 tmp）
    monkeypatch.setattr(pe, "maybe_drain_order_daemon", lambda **kw: {"action": "skipped_test_isolation"})
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
        assert any(not e.get("poison") for e in pe.pending() if e["kind"] == "sim_memo_monthly")

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
        # 段2 接线（裁定#392-D5）+观察面日链（st-sim-launch-20260923）：
        # 账本→日刊→归因→观察面（判定/重放/日报/结算，输入依赖前三件）
        # L05-C10 D-1（2026-09-29）：做T条件包到期件挂链尾（FIFO=观察面后建次日包）
        assert r["emitted"] == [
            "sim_ledger_daily",
            "sim_journal_daily",
            "attribution_daily",
            "sim_observe_daily",
            "t0_condition_pack_due",
        ]
        r2 = pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=True)
        assert r2["emitted"] == []  # 非 poison 在队=去重

    def test_daily_wakes_on_index_kline_too(self, state, marker, monkeypatch):
        """指数日K（账本直读行情）同为唤醒源；非 kline 任务不唤醒。"""
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        r = pe.maybe_emit_sim_daily(task_id="kline_index_incremental", success=True)
        assert r["emitted"] == [
            "sim_ledger_daily",
            "sim_journal_daily",
            "attribution_daily",
            "sim_observe_daily",
            "t0_condition_pack_due",
        ]

    def test_daily_skips_non_kline_and_failed_tasks(self, state, marker):
        assert pe.maybe_emit_sim_daily(task_id="stock_list_daily", success=True)["emitted"] == []
        assert pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=False)["emitted"] == []
        assert pe.maybe_emit_sim_daily()["emitted"] == []

    def test_date_marker_blocks_reemission(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        pe._touch_marker("sim_ledger_daily")
        r = pe.maybe_emit_sim_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == [
            "sim_journal_daily",
            "attribution_daily",
            "sim_observe_daily",
            "t0_condition_pack_due",
        ]  # 只有未落 marker 的件入队

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

        def attribution_stub(p):
            order.append("attribution")
            return {"rc": 0, "day": "D"}

        def observe_stub(p):
            order.append("observe")
            return {"rc": 0, "day": "D"}

        monkeypatch.setattr(pe, "run_sim_ledger_daily", ledger_stub)
        monkeypatch.setattr(pe, "run_sim_journal_daily", journal_stub)
        monkeypatch.setattr(pe, "run_attribution_daily", attribution_stub)
        monkeypatch.setattr(pe, "run_sim_observe_daily", observe_stub)
        s = FakeScheduler()
        pe.wire_data_scheduler(s)
        s.h(task_id="kline_daily_incremental", success=True)
        assert order == ["ledger", "journal", "attribution", "observe"]  # FIFO 串行=账本→日刊→归因→观察面
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert (
            "sim_ledger_daily" in data
            and "sim_journal_daily" in data
            and "attribution_daily" in data
            and "sim_observe_daily" in data
        )  # 消费成功才落 marker
        # 全部轻 kind 消费完毕（月度件 marker 未到期不再发/或被 stub handler 消费）
        assert all(
            e["kind"] not in ("sim_ledger_daily", "sim_journal_daily", "attribution_daily", "sim_observe_daily")
            for e in pe.pending()
        )


class TestSimHandlers:
    """kind 派发 mock：开户/日件 handler 串联 + 预埋派发缺失跳过/交付即跑。"""

    def test_wallet_due_dispatch(self, state, monkeypatch):
        seen = {}

        def fake_run(p):
            seen["p"] = p
            return {"opened": ["S1"]}

        monkeypatch.setattr(pe, "run_sim_wallet_due", fake_run)
        out = pe._default_handler(
            {"id": "X", "kind": "sim_wallet_due", "payload": {"strategies": [{"strategy_id": "S1", "code_path": "a"}]}}
        )
        assert out == {"opened": ["S1"]} and seen["p"]["strategies"][0]["strategy_id"] == "S1"

    def test_daily_handlers_touch_date_markers_on_success(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "run_sim_ledger_daily", lambda p: {"rc": 0})
        monkeypatch.setattr(pe, "run_sim_journal_daily", lambda p: {"rc": 0})
        monkeypatch.setattr(pe, "run_attribution_daily", lambda p: {"rc": 0, "day": "D"})
        pe._default_handler({"id": "X", "kind": "sim_ledger_daily", "payload": {}})
        pe._default_handler({"id": "Y", "kind": "sim_journal_daily", "payload": {}})
        pe._default_handler({"id": "Z", "kind": "attribution_daily", "payload": {}})
        data = json.loads(marker.read_text(encoding="utf-8"))
        assert "sim_ledger_daily" in data and "sim_journal_daily" in data and "attribution_daily" in data

    def test_optional_due_missing_module_skips(self, state, marker, monkeypatch):
        """契约预埋：实现模块缺失=log-and-skip（不抛、可出队，不占 attempts）。

        S12 C4 交付后 promotion_advisory 模块已存在（真派发会读真仓写真盘）——本用例按原意
        改指缺失桩模块验证 skip 语义（适配留痕：Y1 st-fullauto-20260915）。
        """
        monkeypatch.setitem(
            pe.OPTIONAL_DUE_KINDS,
            "fw_backtest_due",
            ("zephyr.strategy_pipeline._definitely_missing_xyz", "run_fw_backtest_due"),
        )
        monkeypatch.setitem(
            pe.OPTIONAL_DUE_KINDS,
            "promotion_advisory_due",
            ("zephyr.strategy_pipeline._definitely_missing_xyz", "run_promotion_advisory_due"),
        )
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


# ---------- TC-08 段1/段2 接线定向验收（裁定#392-D5 批代落，2026-09-21）----------
class TestCrisisBlockWiring:
    """pf_alloc 危机短路（段1）：阻断=跳过+WARN/放行=正常/判读异常 fail-closed/不落 marker。

    闸注入=patch zephyr.pf_alloc.crisis_gate.crisis_block_check 源模块属性（生产侧函数级
    惰性 import，patch 生效）；真 crisis_gate 文件零触碰（R-072a 加固面维持不落）。
    """

    @staticmethod
    def _patch_gate(monkeypatch, *, skip=False, state="normal", reason="ok", exc=None):
        import zephyr.pf_alloc.crisis_gate as cg

        def fake_check(trade_date=None, **kw):
            if exc is not None:
                raise exc
            return cg.CrisisBlock(skip=skip, state=state, reason=reason)

        monkeypatch.setattr(cg, "crisis_block_check", fake_check)

    def test_emit_blocked_skips_enqueue_and_no_marker(self, state, marker, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
        self._patch_gate(monkeypatch, skip=True, state="crisis", reason="crisis_block：dominant=r10")
        r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == [] and r["skipped"] == "crisis_block"
        assert pe.pending() == []  # 阻断=跳过本轮 pf_alloc 入队
        assert not marker.exists()  # 不落 marker（解除后同日可重放=调用方条款）
        assert any(lv == "WARN" and "危机闸" in m for lv, m in alerts)  # WARN 留痕

    def test_emit_passes_on_normal(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
        self._patch_gate(monkeypatch, skip=False, state="normal", reason="normal")
        r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == ["pf_alloc_daily"] and r["trade_date"] == "2026-09-15"
        assert any(e["kind"] == "pf_alloc_daily" for e in pe.pending())

    def test_emit_fail_closed_on_check_error(self, state, marker, monkeypatch):
        """判读异常 fail-closed：视为阻断（裁定#392-D5 明示），同样不入队不落 marker。"""
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
        self._patch_gate(monkeypatch, exc=RuntimeError("snapshot unreadable"))
        r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=True)
        assert r["emitted"] == [] and r["skipped"] == "crisis_block"
        assert pe.pending() == [] and not marker.exists()
        assert any(lv == "WARN" and "fail-closed" in m for lv, m in alerts)

    def test_run_handler_blocks_subprocess(self, state, marker, monkeypatch):
        """执行侧兜底：人工 emit/已入队事件同过闸——阻断=子进程不执行+marker 不落。"""
        import subprocess as _sp

        called = []
        monkeypatch.setattr(_sp, "run", lambda *a, **k: called.append(1))
        self._patch_gate(monkeypatch, skip=True, state="crisis", reason="r")
        out = pe.run_pf_alloc_daily({"trade_date": "2026-09-15"})
        assert out["skipped"] == "crisis_block" and not called
        assert not marker.exists()

    def test_run_handler_fail_closed_no_subprocess(self, state, marker, monkeypatch):
        import subprocess as _sp

        called = []
        monkeypatch.setattr(_sp, "run", lambda *a, **k: called.append(1))
        self._patch_gate(monkeypatch, exc=RuntimeError("snapshot unreadable"))
        out = pe.run_pf_alloc_daily({"trade_date": "2026-09-15"})
        assert out["skipped"] == "crisis_block" and not called
        assert not marker.exists()


class TestAttributionDailyWiring:
    """归因日账（段2）：SIM_DAILY_KINDS FIFO 末位/--day 业务日 resolve/payload 覆盖/失败告警。"""

    def test_sim_daily_kinds_fifo_tail(self):
        # 末位追加铁律：归因 deps=账本当日行，FIFO 消费次序账本→日刊→归因→观察面由元组次序保证
        assert pe.SIM_DAILY_KINDS == (
            "sim_ledger_daily",
            "sim_journal_daily",
            "attribution_daily",
            "sim_observe_daily",
        )
        assert pe.SIM_DAILY_KINDS[-1] == "sim_observe_daily"
        assert "attribution_daily" in pe.LIGHT_KINDS  # 轻 kind=调度器唤醒自动可消费
        assert "sim_observe_daily" in pe.LIGHT_KINDS

    def test_handler_resolves_biz_day(self, monkeypatch):
        seen = {}
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-18")

        def fake_script(script, args, timeout_s):
            seen.update(script=script, args=args, timeout_s=timeout_s)
            return 0, ""

        monkeypatch.setattr(pe, "_run_sim_script", fake_script)
        out = pe.run_attribution_daily({})
        assert out == {"rc": 0, "day": "2026-09-18"}
        assert seen["script"] == "sim_attribution_report.py"
        assert seen["args"] == ["--day", "2026-09-18"]  # --day 业务日=resolve 真源，禁墙钟猜日

    def test_handler_payload_day_overrides_resolve(self, monkeypatch):
        monkeypatch.setattr(
            pe, "resolve_pf_alloc_trade_date", lambda: (_ for _ in ()).throw(AssertionError("payload 带日时禁 resolve"))
        )

        def fake_script(script, args, timeout_s):
            return 0, ""

        monkeypatch.setattr(pe, "_run_sim_script", fake_script)
        assert pe.run_attribution_daily({"trade_date": "2026-09-01"}) == {"rc": 0, "day": "2026-09-01"}
        assert pe.run_attribution_daily({"biz_date": "2026-09-02"}) == {"rc": 0, "day": "2026-09-02"}

    def test_handler_nonzero_rc_alerts(self, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-18")
        monkeypatch.setattr(pe, "_run_sim_script", lambda s, a, t: (3, "boom"))
        out = pe.run_attribution_daily({})
        assert out == {"rc": 3, "day": "2026-09-18"}
        assert any(lv == "ERROR" and "归因日账" in m for lv, m in alerts)

    def test_default_handler_touches_marker(self, state, marker, monkeypatch):
        monkeypatch.setattr(pe, "run_attribution_daily", lambda p: {"rc": 0, "day": "D"})
        pe._default_handler({"id": "X", "kind": "attribution_daily", "payload": {}})
        assert "attribution_daily" in json.loads(marker.read_text(encoding="utf-8"))

    def test_resolve_pf_alloc_trade_date_edges(self, monkeypatch):
        """业务日真源三态边界：正常日 / 空表哨兵 / 无行——宁可不发事件也不猜日。"""
        import zephyr.infrastructure.database_service as dbs

        class FakeConn:
            def __init__(self, rows):
                self._rows = rows

            def execute(self, sql):
                return self._rows

        class FakeSvc:
            def __init__(self, rows):
                self._rows = rows

            def get_clickhouse_conn(self, role="reader"):
                assert role == "reader"
                return FakeConn(self._rows)

        monkeypatch.setattr(dbs, "get_db_service", lambda: FakeSvc([("2026-09-18",)]))
        assert pe.resolve_pf_alloc_trade_date() == "2026-09-18"
        monkeypatch.setattr(dbs, "get_db_service", lambda: FakeSvc([("1970-01-01",)]))
        with pytest.raises(RuntimeError, match="无可用业务日"):
            pe.resolve_pf_alloc_trade_date()
        monkeypatch.setattr(dbs, "get_db_service", lambda: FakeSvc([]))
        with pytest.raises(RuntimeError, match="无可用业务日"):
            pe.resolve_pf_alloc_trade_date()


class TestCrisisGateShortCircuit:
    """段1 危机短路红证补齐（st-oddjobs-20260923 A-2 红证双向条件；两段本体=TC-08 段2/
    裁定#392 D5 批代落，本类只补红蓝证据不碰实现）。

    红向：crisis 态 / 判读异常 fail-closed → 发射侧零入队零 marker（重放契约）、
    执行侧零子进程；蓝向回归：解除后同日恢复发射。
    patch 面=crisis_gate.crisis_block_check 模块属性（本件惰性 import，patch 源头即生效）。
    """

    def _block_gate(self, monkeypatch, reason="红证：crisis 阻断"):
        import zephyr.pf_alloc.crisis_gate as cg

        monkeypatch.setattr(
            cg, "crisis_block_check", lambda *a, **k: cg.CrisisBlock(skip=True, state="crisis", reason=reason)
        )
        return cg

    def test_emission_side_crisis_blocks_enqueue(self, state, monkeypatch):
        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-23")
        monkeypatch.setattr(pe, "AUDIT_MARKER", state / "last_audit.json")
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        self._block_gate(monkeypatch)
        r = pe.maybe_emit_pf_alloc_daily(task_id="daily_kline", success=True)
        assert r == {"emitted": [], "skipped": "crisis_block", "trade_date": "2026-09-23"}
        assert pe.pending() == []  # 零入队
        assert not pe._marker_seen("pf_alloc_daily:2026-09-23")  # 零 marker（解除后可重放）

    def test_emission_side_gate_anomaly_fails_closed(self, state, monkeypatch):
        import zephyr.pf_alloc.crisis_gate as cg

        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-23")
        monkeypatch.setattr(pe, "AUDIT_MARKER", state / "last_audit.json")
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)

        def boom(*a, **k):
            raise RuntimeError("CH 不可达（红证：判读异常）")

        monkeypatch.setattr(cg, "crisis_block_check", boom)
        r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily", success=True)
        assert r["emitted"] == [] and r["skipped"] == "crisis_block"  # fail-closed=视为阻断
        assert pe.pending() == [] and not pe._marker_seen("pf_alloc_daily:2026-09-23")

    def test_execution_side_crisis_blocks_subprocess(self, state, monkeypatch):
        monkeypatch.setattr(pe, "AUDIT_MARKER", state / "last_audit.json")
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        self._block_gate(monkeypatch)
        import zephyr.shared.infra.process_pool as pp

        def _no_subprocess(*a, **k):
            raise AssertionError("危机阻断后子进程不得执行")

        monkeypatch.setattr(pp, "run_subprocess_hidden", _no_subprocess)
        r = pe.run_pf_alloc_daily({"trade_date": "2026-09-23"})
        assert r["skipped"] == "crisis_block"
        assert not pe._marker_seen("pf_alloc_daily:2026-09-23")

    def test_blue_gate_clear_same_day_reemits(self, state, monkeypatch):
        import zephyr.pf_alloc.crisis_gate as cg

        monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-23")
        monkeypatch.setattr(pe, "AUDIT_MARKER", state / "last_audit.json")
        monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
        self._block_gate(monkeypatch)
        assert pe.maybe_emit_pf_alloc_daily(task_id="daily_kline", success=True)["skipped"] == "crisis_block"
        # 危机解除（skip=False）→ 同日恢复发射（重放契约蓝向回归）
        monkeypatch.setattr(
            cg, "crisis_block_check", lambda *a, **k: cg.CrisisBlock(skip=False, state="normal", reason="解除")
        )
        r = pe.maybe_emit_pf_alloc_daily(task_id="daily_kline", success=True)
        assert r == {"emitted": [pe.PF_ALLOC_KIND], "trade_date": "2026-09-23"}
        assert len(pe.pending()) == 1 and pe.pending()[0]["payload"]["trade_date"] == "2026-09-23"


# ---------- E4 代码治本（st-lanech-20261001）：B1 tmp 唯一化 / B2 撕裂行容错 / B4 毒丸告警
# CRITICAL / B4' repair 处置正门 / B5 emit_sim_wallet_due 幂等闸（病根真源=e4_journal_surgery.md）----------
@pytest.fixture()
def _torn_alert_reset():
    """坏行告警进程级去重状态归零（测试互不遮蔽）。"""
    pe._TORN_LINE_ALERTED.clear()
    yield
    pe._TORN_LINE_ALERTED.clear()


class TestE4JournalTornLineTolerance:
    """B2：pending() 逐行 json.loads 零容错病根治本——坏行跳过+ERROR 出声，一行坏不再全队死。"""

    def test_pending_skips_torn_line_and_alerts(self, state, _torn_alert_reset, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        good1 = pe.record("c4_batch_completed", {"batch": "B1"})
        with pe.JOURNAL.open("a", encoding="utf-8") as f:
            f.write('{"id": "PIPE-TORN", "kind": "c4_ba\n')  # 撕裂半行（截断残骸，行尾留换行不吞后行）
        good2 = pe.record("sim_wallet_due", {"strategies": []})
        evts = pe.pending()  # 旧码此处抛 JSONDecodeError（一行坏全队死实证）
        assert [e["id"] for e in evts] == [good1["id"], good2["id"]]
        assert any(lv == "ERROR" and "坏行" in m for lv, m in alerts)

    def test_pending_torn_alert_deduped_within_process(self, state, _torn_alert_reset, monkeypatch):
        """drain/唤醒链每轮多次调 pending()——坏行告警进程级去重，不告警风暴。"""
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        with pe.JOURNAL.open("w", encoding="utf-8") as f:
            f.write("{bad torn line}\n")
        pe.pending()
        pe.pending()
        assert len([1 for lv, _ in alerts if lv == "ERROR"]) == 1

    def test_drain_consumes_rest_despite_torn_line(self, state, _torn_alert_reset, monkeypatch):
        """坏行不阻断消费；出队重写顺带剪除坏行（原件留备份/告警留痕）。"""
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
        pe.record("c4_batch_completed", {"batch": "B1"})
        with pe.JOURNAL.open("a", encoding="utf-8") as f:
            f.write('{"torn": tru\n')
        pe.record("c2_screen_due", {})
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        r = pe.drain(handler=lambda e: {"ok": True})
        assert len(r["processed"]) == 2 and r["pending_left"] == 0
        assert "torn" not in pe.JOURNAL.read_text(encoding="utf-8")  # 坏行被重写剪除

    def test_blank_lines_still_ignored(self, state):
        pe.record("c4_batch_completed", {"batch": "B1"})
        with pe.JOURNAL.open("a", encoding="utf-8") as f:
            f.write("\n   \n")
        assert len(pe.pending()) == 1  # 既有空行豁免语义不变


class TestE4TmpNameUniqueness:
    """B1：_rewrite 固定 tmp 名多进程互踩（撕裂行+WinError 32）治本——pid+uuid 唯一 tmp 名。"""

    def test_tmp_name_contains_pid_and_uuid(self, state, monkeypatch):
        monkeypatch.setattr(pe.os, "getpid", lambda: 424242)
        p1 = pe._journal_tmp_path()
        p2 = pe._journal_tmp_path()
        assert "424242" in p1.name and p1.name.endswith(".tmp")
        assert p1 != p2  # uuid 片段=同进程连续两次也不撞
        assert p1.parent == pe.JOURNAL.parent  # 同目录（os.replace 同盘原子性前提）

    def test_rewrite_leaves_no_tmp_on_success(self, state):
        pe.record("c4_batch_completed", {})
        pe._rewrite(pe.pending())
        assert list(state.glob("*.tmp")) == []

    def test_rewrite_cleans_tmp_on_replace_failure(self, state, monkeypatch):
        """replace 撞车（模拟 WinError 32）→ tmp 残留清理，防句柄/废件堆积。

        P2a 合并适配：dev 版 _rewrite 用 os.replace(tmp, JOURNAL)（非 Path.replace），
        monkeypatch 目标同步换 os.replace。
        """
        pe.record("c4_batch_completed", {})
        evts = pe.pending()

        def boom(src, dst):
            raise PermissionError(32, "simulated sharing violation")

        monkeypatch.setattr(pe.os, "replace", boom)
        with pytest.raises(PermissionError):
            pe._rewrite(evts)
        assert list(state.glob("*.tmp")) == []


class TestE4RepairCli:
    """B4'：毒丸处置正门——repair --list / --drop / --unpoison（落改前自动备份 .bak-repair-*）。"""

    @staticmethod
    def _make_poison(kind="c2_screen_due"):
        evt = pe.record(kind, {})
        evts = pe.pending()
        for e in evts:  # 按 id 定向（journal 可能已有他事件，record=追加不回头）
            if e["id"] == evt["id"]:
                e["poison"] = True
                e["attempts"] = pe.MAX_ATTEMPTS
                e["last_error"] = "RuntimeError: ch down"
        pe._rewrite(evts)
        return evt

    def test_repair_list_poison_only(self, state):
        healthy = pe.record("c4_batch_completed", {})
        poison = self._make_poison()
        out = pe.repair("list")
        assert out["n"] == 1 and [e["id"] for e in out["poison_events"]] == [poison["id"]]
        assert healthy["id"] not in [e["id"] for e in out["poison_events"]]

    def test_repair_drop_removes_single_event_with_backup(self, state):
        keep = pe.record("c4_batch_completed", {})
        poison = self._make_poison()
        out = pe.repair("drop", poison["id"])
        assert out["dropped"] is True and out["remaining"] == 1
        assert [e["id"] for e in pe.pending()] == [keep["id"]]
        baks = list(state.glob("*.bak-repair-*"))
        assert len(baks) == 1 and poison["id"] in baks[0].read_text(encoding="utf-8")  # 备份含被删原件

    def test_repair_drop_unknown_id_no_side_effect(self, state):
        pe.record("c4_batch_completed", {})
        out = pe.repair("drop", "PIPE-NONE")
        assert out == {"dropped": False, "why": "event_not_found", "event_id": "PIPE-NONE"}
        assert list(state.glob("*.bak-repair-*")) == []  # 无变更不备份

    def test_repair_unpoison_resets_and_replayable(self, state, monkeypatch):
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        poison = self._make_poison()
        out = pe.repair("unpoison", poison["id"])
        assert out["unpoisoned"] is True
        e = pe.pending()[0]
        assert "poison" not in e and e["attempts"] == 0  # 摘毒+attempts 归零（last_error 留档）
        assert e["last_error"] == "RuntimeError: ch down"
        r = pe.drain(handler=lambda ev: {"ok": True})  # 摘毒后重放正门打通
        assert r["processed"] and r["pending_left"] == 0

    def test_repair_cli_dispatch(self, state, capsys):
        poison = self._make_poison()
        assert pe.main(["repair", "--list"]) == 0
        out = json.loads(capsys.readouterr().out)
        assert [e["id"] for e in out["poison_events"]] == [poison["id"]]
        assert pe.main(["repair", "--drop", poison["id"]]) == 0
        capsys.readouterr()
        assert pe.pending() == []

    def test_repair_unknown_action_raises(self, state):
        with pytest.raises(ValueError, match="repair 动作"):
            pe.repair("rebuild")


class TestE4EmitSimWalletIdempotency:
    """B5：emit_sim_wallet_due 幂等闸——同 kind+同 strategies 集合未消费事件在队=跳过入队。"""

    def test_duplicate_emit_skipped(self, state, monkeypatch):
        monkeypatch.setattr(pe, "drain", lambda allow_heavy: {"processed": 1})
        r1 = pe.emit_sim_wallet_due([{"strategy_id": "S1", "code_path": "a.py"}])
        assert r1["drained"] is True
        r2 = pe.emit_sim_wallet_due([{"strategy_id": "S1", "code_path": "a.py"}])
        assert r2.get("already_pending") is True
        assert len([e for e in pe.pending() if e["kind"] == "sim_wallet_due"]) == 1  # 只记一条

    def test_same_strategy_set_different_order_deduped(self, state, monkeypatch):
        monkeypatch.setattr(pe, "drain", lambda allow_heavy: {"processed": 1})
        pe.emit_sim_wallet_due([{"strategy_id": "S1"}, {"strategy_id": "S2"}])
        r2 = pe.emit_sim_wallet_due([{"strategy_id": "S2"}, {"strategy_id": "S1"}])
        assert r2.get("already_pending") is True  # 集合比较与次序无关

    def test_different_strategies_still_emits(self, state, monkeypatch):
        monkeypatch.setattr(pe, "drain", lambda allow_heavy: {"processed": 1})
        pe.emit_sim_wallet_due([{"strategy_id": "S1"}])
        r2 = pe.emit_sim_wallet_due([{"strategy_id": "S1"}, {"strategy_id": "S2"}])
        assert r2.get("already_pending") is None and r2["drained"] is True
        assert len(pe.pending()) == 2

    def test_poison_does_not_block_reemission(self, state, monkeypatch):
        """毒丸不算"已入队"（月度档同款裁定）：开户卡死可由新事件重开正门。"""
        monkeypatch.setattr(pe, "drain", lambda allow_heavy: {"processed": 1})
        pe.emit_sim_wallet_due([{"strategy_id": "S1"}])
        evts = pe.pending()
        evts[0]["poison"] = True
        pe._rewrite(evts)
        r = pe.emit_sim_wallet_due([{"strategy_id": "S1"}])
        assert r["drained"] is True and r.get("already_pending") is None
        assert len([e for e in pe.pending() if e["kind"] == "sim_wallet_due"]) == 2


class TestE4PoisonAlertCritical:
    """B4：毒丸告警升级 CRITICAL——webhook 分发器只转发 CRITICAL（ERROR 级断链修复）。"""

    def test_poison_alert_level_is_critical(self, state, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        pe.record("c4_batch_completed", {})

        def boom(e):
            raise RuntimeError("ch down")

        for _ in range(pe.MAX_ATTEMPTS):
            pe.drain(handler=boom)
        poison_alerts = [(lv, m) for lv, m in alerts if "毒丸留档" in m]
        assert poison_alerts and poison_alerts[0][0] == "CRITICAL"  # 旧码=ERROR（webhook 不转发）


class TestOrderDaemonSpawn:
    """F82 P0（st-circ-a7）：工单守护 spawn——journal 空=零成本跳过；非空才起守护；
    守护异常 WARN 不反噬。SchedulingJournal/OrderDaemon/policy 全注入桩（零生产 IO）。"""

    @staticmethod
    def _fake_journal(monkeypatch, events):
        """把 hook 内惰性 import 的 SchedulingJournal 指向 tmp 桩（禁触生产 .runtime/ai_scheduling）。"""
        import zephyr.ai_layer.scheduling.scheduling_events as se

        class FakeJournal:
            def pending(self):
                return list(events)

        monkeypatch.setattr(se, "SchedulingJournal", lambda: FakeJournal())
        return se

    def test_empty_journal_skips_daemon(self, monkeypatch):
        self._fake_journal(monkeypatch, [])
        import zephyr.ai_layer.scheduling.order_daemon as od

        def _no_daemon(journal, policy, sink=None):
            raise AssertionError("空 journal 不得起守护")

        monkeypatch.setattr(od, "OrderDaemon", _no_daemon)
        r = pe.maybe_drain_order_daemon(task_id="daily_kline", success=True)
        assert r == {"action": "journal_empty"}

    def test_nonempty_journal_spawns_process_once(self, state, monkeypatch):
        import zephyr.ai_layer.scheduling.maturity as mat
        import zephyr.ai_layer.scheduling.order_daemon as od

        class FakeEvent:
            poison = False

        calls = {}

        class FakeDaemon:
            def __init__(self, journal, policy, sink=None):
                calls["policy"] = policy
                calls["sink"] = sink

            def process_once(self):
                calls["ran"] = True
                return {"processed": [{"id": "SCHED-1"}], "failed": [], "skipped": [], "pending_left": 0}

        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        self._fake_journal(monkeypatch, [FakeEvent()])
        monkeypatch.setattr(od, "OrderDaemon", FakeDaemon)
        monkeypatch.setattr(mat, "load_gate_policy", lambda: {"stub": True})
        r = pe.maybe_drain_order_daemon(task_id="kline_daily", success=True)
        assert r["action"] == "drained" and r["processed"] == 1 and calls["ran"]
        assert calls["sink"] is not None, "F82 lane-f82：spawn 必须挂落库 sink（dry-run=工单蒸发断链）"
        assert any(lv == "INFO" and "ORDER-DAEMON" in m for lv, m in alerts)

    def test_daemon_failure_alerts_and_never_raises(self, monkeypatch):
        import zephyr.ai_layer.scheduling.maturity as mat
        import zephyr.ai_layer.scheduling.order_daemon as od

        class FakeEvent:
            poison = False

        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        self._fake_journal(monkeypatch, [FakeEvent()])

        def boom(journal, policy, sink=None):
            raise RuntimeError("policy 缺节")

        monkeypatch.setattr(od, "OrderDaemon", boom)
        monkeypatch.setattr(mat, "load_gate_policy", lambda: {})
        r = pe.maybe_drain_order_daemon(task_id="daily_kline", success=True)
        assert r["action"] == "error" and r["error"] == "RuntimeError"
        assert any(lv == "WARN" and "ORDER-DAEMON" in m for lv, m in alerts)

    def test_failed_task_and_poison_only_journal_skip(self, monkeypatch):
        import zephyr.ai_layer.scheduling.order_daemon as od

        def _no_daemon(journal, policy, sink=None):
            raise AssertionError("毒丸 journal 不得起守护")

        monkeypatch.setattr(od, "OrderDaemon", _no_daemon)
        assert pe.maybe_drain_order_daemon(task_id="daily_kline", success=False)["action"] == "skipped_failed_task"
        self._fake_journal(monkeypatch, [type("E", (), {"poison": True})()])
        assert pe.maybe_drain_order_daemon(task_id="daily_kline", success=True)["action"] == "journal_empty"

    # ---- F82 lane-f82（2026-10-01）：sink 落库冒烟——journal 事件→守护→orders.jsonl ----
    # 模拟边界：工单=任务书文本对象（非交易订单），全 tmp 注入零生产路径零券商零下单。

    @staticmethod
    def _emit_winner(journal, experiment_id: str) -> None:
        from zephyr.ai_layer.scheduling.scheduling_events import KIND_EVOLUTION_WINNER_DUE

        journal.emit(
            KIND_EVOLUTION_WINNER_DUE,
            {
                "verdict": "win",
                "domain_id": "governance",
                "evidence_ref": f"{experiment_id}#verdict",
                "experiment_id": experiment_id,
                "criteria_hash": "a" * 64,
                "title": f"F82 冒烟工单 {experiment_id}",
                "compute_class": "local",
            },
        )

    def test_winner_event_lands_work_order_in_store(self, state, tmp_path, monkeypatch):
        """胜者事件→守护消费→工单落 orders.jsonl（sink 缺省 dry-run 的断链后半段治本回归）。"""
        import json

        import zephyr.ai_layer.scheduling.scheduling_events as se
        from zephyr.ai_layer.scheduling.scheduling_events import SchedulingJournal

        journal = SchedulingJournal(state_dir=tmp_path / "ai_scheduling")
        self._emit_winner(journal, "EX-F82-demo")
        monkeypatch.setattr(se, "SchedulingJournal", lambda: journal)
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))

        r = pe.maybe_drain_order_daemon(task_id="daily_kline", success=True)

        assert r["action"] == "drained" and r["processed"] == 1 and r["pending_left"] == 0
        orders_path = tmp_path / "ai_scheduling" / "orders.jsonl"
        assert orders_path.exists(), "工单必须落库（dry-run=断链后半段复发）"
        order = json.loads(orders_path.read_text(encoding="utf-8").splitlines()[0])
        assert order["order_id"].startswith("WO-") and order["state"] == "pending"
        assert order["domain_id"] == "governance" and order["experiment_id"] == "EX-F82-demo"

    def test_same_day_second_winner_gets_next_seq(self, state, tmp_path, monkeypatch):
        """同日第二胜者序号+1（handle_winner 硬编码 seq=1 的互踩丢单回归）。"""
        import zephyr.ai_layer.scheduling.scheduling_events as se
        from zephyr.ai_layer.scheduling.scheduling_events import SchedulingJournal

        journal = SchedulingJournal(state_dir=tmp_path / "ai_scheduling")
        self._emit_winner(journal, "EX-F82-1")
        self._emit_winner(journal, "EX-F82-2")
        monkeypatch.setattr(se, "SchedulingJournal", lambda: journal)
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)

        r = pe.maybe_drain_order_daemon(task_id="daily_kline", success=True)

        assert r["action"] == "drained" and r["processed"] == 2
        orders_path = tmp_path / "ai_scheduling" / "orders.jsonl"
        ids = [o.split('"order_id": "')[1].split('"')[0] for o in orders_path.read_text(encoding="utf-8").splitlines()]
        day = ids[0].split("-")[1]
        assert ids == [f"WO-{day}-001", f"WO-{day}-002"], f"同日序号必须递增不互踩：{ids}"


class TestTailFailIsolation:
    """F27 P0（st-circ-a7）：唤醒链尾段 fail-isolation——pf_alloc 发射炸了，
    sim 日件/monthly/drain 照跑且 ERROR 出声（09-30 08:39 型整段熄火根治回归）。"""

    def test_pf_alloc_emit_failure_does_not_kill_tail(self, state, marker, monkeypatch):
        alerts = []
        monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": alerts.append((level, msg)))
        monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
        monkeypatch.setattr(pe, "scan_translated_backlog", lambda: {"backlog": []})
        monkeypatch.setattr(pe, "scan_c1_c2_backlog", lambda: {})
        monkeypatch.setattr(pe, "maybe_drain_order_daemon", lambda **kw: {"action": "journal_empty"})
        monkeypatch.setattr(pe, "maybe_refresh_regime_snapshot", lambda **kw: {"action": "fresh"})
        monkeypatch.setattr(pe, "maybe_settle_judgment_ledger", lambda **kw: {"action": "settled"})
        monkeypatch.setattr(pe, "maybe_run_warroom_pipeline", lambda **kw: {"action": "run"})
        monkeypatch.setattr(pe, "maybe_record_auction_hit", lambda **kw: {"action": "run"})
        # Phase 2b 判定产出件（惰性 import）同款隔离（autouse 只盖 2a/编排器/L9）
        monkeypatch.setattr("zephyr.plan_engine.daily_plan.maybe_emit_daily_plan", lambda *a, **k: {"emitted": []})
        monkeypatch.setattr(
            "zephyr.plan_engine.scenario_classifier.maybe_classify_intraday_scenario",
            lambda *a, **k: {"action": "skipped"},
        )
        monkeypatch.setattr(
            "zephyr.plan_engine.close_verifier.maybe_verify_plan_close", lambda *a, **k: {"action": "skipped"}
        )
        monkeypatch.setattr(
            pe,
            "maybe_emit_pf_alloc_daily",
            lambda **kw: (_ for _ in ()).throw(RuntimeError("journal 并发读竞态（09-30 断因同型）")),
        )
        called = {"sim": False, "monthly": False, "drain": False}
        monkeypatch.setattr(pe, "maybe_emit_sim_daily", lambda **kw: called.__setitem__("sim", True))
        monkeypatch.setattr(pe, "maybe_emit_monthly", lambda: called.__setitem__("monthly", True))

        def fake_drain(allow_heavy=False, handler=None, max_events=20):
            called["drain"] = True
            return {"processed": [], "failed": [], "skipped": [], "stop_reason": None, "pending_left": 0}

        monkeypatch.setattr(pe, "drain", fake_drain)

        class S:
            def subscribe(self, event, handler):
                self.h = handler

        s = S()
        pe.wire_data_scheduler(s)
        s.h(task_id="daily_kline", success=True)
        assert called == {"sim": True, "monthly": True, "drain": True}  # 尾段不连坐
        assert any(lv == "ERROR" and "PF-ALLOC-EMIT" in m for lv, m in alerts)  # 且出声
