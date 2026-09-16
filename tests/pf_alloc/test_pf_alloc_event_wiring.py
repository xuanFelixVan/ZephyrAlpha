# [A_test] module_id: MOD-PFALLOC-ALLOC-DAILY | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md | §test
# [MODULE] tests.pf_alloc.test_pf_alloc_event_wiring
# [DOMAIN] D_PF_ALLOC
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_alloc/test_pf_alloc_event_wiring.py
# [TTL] task_bound
"""pf_alloc_daily 事件接线回归锁（车道 D 接线②③：产出者→派发→分配链装配体）。

锁的是"事件正门通到装配体 + 装配体有人按电铃"这条链的五个不变量
（宪法 §9.3：触发面=事件，禁 cron/Timer/sleep）：
1. kind 归轻 kind（调度器唤醒钩子可消费）且非重 kind；派发分支把事件路由到 run_pf_alloc_daily；
2. 执行体=subprocess 隔离 `python -m zephyr.pf_alloc.allocation_orchestrator --date <D>`，
   超时有界（PF_ALLOC_TIMEOUT_S），业务日只认 payload（缺 trade_date 即抛，禁墙钟猜日）；
3. 同日幂等：同一 trade_date 已成功落地后再派发=零子进程调用（alloc 三表只增不改，
   无此闸=同日双写快照）；失败/超时不落 marker（重试路径不被自己的守卫堵死）；
4. 失败进既有重试语义：抛错 → drain 计 attempts，MAX_ATTEMPTS=3 后毒丸留档不再自动消费；
5. **产出者存在且给得出日**（清单 #15 治本，此前 1-4 全绿却恒 0 行=有消费端无发射方）：
   daily_kline SUCCESS 唤醒即入队、业务日=行情最新入库日（解析不出即不发事件+告警，
   绝不墙钟猜）、入队先于 sim_ledger_daily（分配先落，账本同日开户才拿到真实额度）、
   落地结果一行摘要进告警面（"产而不消"的反面=算了没人知道）。

全程 tmp_path（JOURNAL/RECEIPT/AUDIT_MARKER 重定向）+ subprocess.run 打桩，零生产 IO、零真实等待。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from zephyr.strategy_pipeline import pipeline_events as pe  # noqa: E402

DAY = "2026-09-15"
MARKER_KEY = f"pf_alloc_daily:{DAY}"


@pytest.fixture()
def state(tmp_path, monkeypatch):
    """journal/marker 全部指 tmp（禁写生产 .runtime/strategy_pipeline）。"""
    monkeypatch.setattr(pe, "STATE_DIR", tmp_path)
    monkeypatch.setattr(pe, "JOURNAL", tmp_path / "pending_events.jsonl")
    monkeypatch.setattr(pe, "RECEIPT", tmp_path / "last_receipt.json")
    monkeypatch.setattr(pe, "AUDIT_MARKER", tmp_path / "last_audit.json")
    return tmp_path


@pytest.fixture()
def alerts(monkeypatch):
    seen: list[tuple[str, str]] = []
    monkeypatch.setattr(pe, "alert",
                        lambda msg, level="WARN": seen.append((str(msg), level)))
    return seen


class _FakeProc:
    def __init__(self, returncode=0, stdout="ok", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


class _Spied:
    """子进程桩的调用记录 + 可配返回（calls 空=一次都没起子进程）。"""

    def __init__(self):
        self.calls: list[dict] = []
        self.box: dict = {"proc": _FakeProc(), "raise": None}


@pytest.fixture()
def spied(monkeypatch):
    """subprocess.run 打桩：记录调用、可配返回/抛错（绝不真起子进程、绝不 sleep）。"""
    holder = _Spied()

    def fake_run(cmd, **kwargs):
        holder.calls.append({"cmd": list(cmd), **kwargs})
        if holder.box["raise"]:
            raise holder.box["raise"]
        return holder.box["proc"]

    monkeypatch.setattr(subprocess, "run", fake_run)
    return holder


def _markers(state: Path) -> dict:
    f = state / "last_audit.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


# ── ① kind 注册 + 派发 ────────────────────────────────────────────────
def test_pf_alloc_daily_is_light_kind():
    assert "pf_alloc_daily" in pe.LIGHT_KINDS
    assert "pf_alloc_daily" not in pe.HEAVY_KINDS


def test_dispatcher_routes_pf_alloc_daily_to_handler(state, monkeypatch):
    seen: list[dict] = []
    monkeypatch.setattr(pe, "run_pf_alloc_daily",
                        lambda p: seen.append(p) or {"rc": 0, "trade_date": p["trade_date"]})
    out = pe._default_handler({"id": "X", "kind": "pf_alloc_daily",
                               "payload": {"trade_date": DAY}})

    assert seen == [{"trade_date": DAY}]  # 事件 payload 原样交给执行体
    assert out["trade_date"] == DAY
    assert "pf_alloc_daily" in _markers(state)  # 消费成功才落 kind 级日号（与 sim_ledger_daily 同族）


def test_unknown_kind_still_rejected_at_dispatch():
    with pytest.raises(ValueError):
        pe._default_handler({"id": "X", "kind": "pf_alloc_dailyy", "payload": {}})


# ── ② 执行体：子进程隔离 + 有界超时 + 业务日只认 payload ───────────────
def test_handler_invokes_orchestrator_cli_with_bounded_timeout(state, spied):
    spied.box["raise"] = None
    out = pe.run_pf_alloc_daily({"trade_date": DAY, "strategy_ids": ["STR-A", "STR-B"]})

    call = spied.calls[0]
    assert call["cmd"][:4] == [sys.executable, "-m", pe.PF_ALLOC_MODULE, "--date"]
    assert call["cmd"][4] == DAY and call["cmd"][5:7] == ["--strategy-id", "STR-A"]
    assert call["timeout"] == pe.PF_ALLOC_TIMEOUT_S  # 运行时界（非无界）
    assert call["cwd"] == str(pe.ROOT) and call["capture_output"] is True
    assert out["rc"] == 0 and out["trade_date"] == DAY
    assert _markers(state)[MARKER_KEY]  # 成功才落 trade_date 级号


def test_handler_payload_timeout_overrides_default(state, spied):
    pe.run_pf_alloc_daily({"biz_date": DAY, "timeout_s": 42})
    assert spied.calls[0]["timeout"] == 42


def test_handler_refuses_to_guess_trade_date_from_wall_clock(state, spied, alerts):
    with pytest.raises(RuntimeError, match="trade_date"):
        pe.run_pf_alloc_daily({})
    assert spied.calls == []  # 缺业务日=连子进程都不起（分配链 handle_pf_alloc_daily_event 同口径）


# ── ③ 同日幂等（防双写分配快照） ──────────────────────────────────────
def test_same_trade_date_second_run_writes_nothing(state, spied):
    assert pe.run_pf_alloc_daily({"trade_date": DAY})["rc"] == 0
    assert len(spied.calls) == 1
    assert pe.run_pf_alloc_daily({"trade_date": DAY})["skipped"] == "already_persisted"
    assert len(spied.calls) == 1  # 重放零副作用（三表只增不改，双写=同日两份快照）


def test_different_trade_date_is_not_blocked_by_marker(state, spied):
    pe.run_pf_alloc_daily({"trade_date": DAY})
    assert pe.run_pf_alloc_daily({"trade_date": "2026-09-16"})["rc"] == 0
    assert len(spied.calls) == 2  # 闸按业务日计，不按 kind 全局堵死回填


# ── ④ 失败/超时 → 抛错进既有重试语义（MAX_ATTEMPTS=3） ─────────────────
def test_nonzero_rc_raises_and_leaves_marker_unset_for_retry(state, spied, alerts):
    spied.box["proc"] = _FakeProc(returncode=1, stderr="AllocationInputError: 表未建")
    with pytest.raises(RuntimeError, match="rc=1"):
        pe.run_pf_alloc_daily({"trade_date": DAY})
    assert MARKER_KEY not in _markers(state)  # 失败不落号（否则重试被自己的守卫永久堵死）
    assert alerts and alerts[0][1] == "ERROR"


def test_timeout_raises_bounded_error(state, spied, alerts):
    spied.box["raise"] = subprocess.TimeoutExpired(cmd=["python"], timeout=5)
    with pytest.raises(RuntimeError, match="超时"):
        pe.run_pf_alloc_daily({"trade_date": DAY, "timeout_s": 5})
    assert MARKER_KEY not in _markers(state)
    assert alerts and "超时" in alerts[0][0]


def test_drain_retries_then_poisons_pf_alloc_event(state, monkeypatch, alerts):
    """真 drain + 真派发（执行体打桩抛错）：attempts 计数与毒丸留档对新 kind 同样生效。"""
    monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))

    def boom(payload):
        raise RuntimeError("alloc chain down")

    monkeypatch.setattr(pe, "run_pf_alloc_daily", boom)
    pe.record("pf_alloc_daily", {"trade_date": DAY})
    for expected in (1, 2, 3):
        r = pe.drain(allow_heavy=False)
        assert r["failed"], "轻 drain 必须消费 pf_alloc_daily（它是轻 kind）"
        assert pe.pending()[0]["attempts"] == expected
    assert pe.pending()[0].get("poison") is True
    r4 = pe.drain(allow_heavy=False)
    assert r4["pending_left"] == 1 and any(s.get("why") == "poison_held" for s in r4["skipped"])
    assert any("毒丸" in m for m, _ in alerts)


# ── ⑤ 每日产出者（清单 #15 治本：kind 有消费端无发射方=alloc 三表恒 0 行的真断点）──
class _FakeChConn:
    """只读连接桩：按预置行回答业务日查询（零生产 IO，禁真连 CH）。"""

    def __init__(self, rows):
        self.rows, self.sqls = rows, []

    def execute(self, sql):
        self.sqls.append(sql)
        return self.rows


def _patch_ch(monkeypatch, rows):
    import zephyr.infrastructure.database_service as dbs

    conn = _FakeChConn(rows)
    monkeypatch.setattr(
        dbs, "get_db_service",
        lambda: type("_S", (), {"get_clickhouse_conn": staticmethod(lambda role=None: conn)})())
    return conn


def test_producer_emits_on_kline_success_with_data_derived_day(state, monkeypatch, alerts):
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: DAY)
    r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=True)

    assert r["emitted"] == [pe.PF_ALLOC_KIND] and r["trade_date"] == DAY
    evt = pe.pending()[0]
    assert evt["kind"] == "pf_alloc_daily" and evt["payload"]["trade_date"] == DAY
    # 入队即出声（静默的产出者等于没有产出者——PFA-1 的教训就是"没人知道该生效"）
    assert any("已入队" in m and lv == "INFO" for m, lv in alerts)


def test_producer_silent_on_non_kline_or_failed_task(state, monkeypatch, alerts):
    def boom():
        raise AssertionError("非唤醒点不得触库解析业务日")

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", boom)
    assert pe.maybe_emit_pf_alloc_daily(task_id="stock_list_daily", success=True) == {"emitted": []}
    assert pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=False) == {"emitted": []}
    assert pe.maybe_emit_pf_alloc_daily() == {"emitted": []}
    assert pe.pending() == []


def test_producer_refuses_wall_clock_when_business_day_unresolvable(state, monkeypatch, alerts):
    """行情日不可解析=宁可不发事件，也不按墙钟猜一个业务日写进只增不改的分配快照。"""
    def down():
        raise RuntimeError("CH 不可达")

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", down)
    r = pe.maybe_emit_pf_alloc_daily(task_id="daily_kline", success=True)

    assert r["emitted"] == [] and "业务日不可解析" in r["error"]
    assert pe.pending() == []  # 零事件（下游因此走显式回退，不是假额度）
    assert alerts and alerts[0][1] == "WARN"


def test_producer_dedupes_same_business_day_via_pending_then_marker(state, monkeypatch, alerts):
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: DAY)
    assert pe.maybe_emit_pf_alloc_daily(task_id="daily_kline")["emitted"] == [pe.PF_ALLOC_KIND]
    # 闸 1：同业务日非 poison 事件在队=不重复入队
    assert pe.maybe_emit_pf_alloc_daily(task_id="kline_index_incremental")["emitted"] == []
    assert len(pe.pending()) == 1
    # 闸 2：事件已消费成功（trade_date 级 marker 落地）后再次唤醒仍零副作用
    for e in pe.pending():
        e["attempts"] = 3
        e["poison"] = True
    pe._rewrite(pe.pending())
    pe._touch_marker(f"{pe.PF_ALLOC_KIND}:{DAY}")
    r = pe.maybe_emit_pf_alloc_daily(task_id="daily_kline")
    assert r["emitted"] == [] and r.get("skipped") == "already_queued_or_done"


def test_producer_gate_is_business_day_scoped_not_utc_day(state, monkeypatch, alerts):
    """行情停更/周末唤醒：UTC 日已翻篇但业务日仍是已分配过的 D=不得再发（只增表拒绝重复快照）。

    此闸若按"当日"口径（_date_marker_done）写就会漏——记号时间戳一旦不是今天，同一业务日
    会被再次自动分配，alloc_budget_daily 里多出一份新 run_id 的重复快照。
    """
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: DAY)
    (state / "last_audit.json").write_text(
        json.dumps({MARKER_KEY: "2020-01-01T00:00:00"}), encoding="utf-8")

    r = pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental", success=True)
    assert r["emitted"] == [] and r.get("skipped") == "already_queued_or_done"
    assert pe.pending() == []
    # 永久闸只挡"已分配过的业务日"，不是把链一劳永逸关掉：新业务日照样发
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-16")
    assert pe.maybe_emit_pf_alloc_daily(task_id="kline_daily_incremental")["emitted"] == [
        pe.PF_ALLOC_KIND]


def test_producer_poison_does_not_block_retry(state, monkeypatch, alerts):
    """毒丸不算"已入队"（与 C2/X2 同族病根：否则一次失败永久堵死该链）。"""
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: DAY)
    pe.record(pe.PF_ALLOC_KIND, {"trade_date": DAY})
    evts = pe.pending()
    evts[0]["poison"] = True
    pe._rewrite(evts)
    # 判毒 + trade_date marker 未落 = 同业务日下次唤醒必须重发（留档行不堵重试行）
    assert pe.maybe_emit_pf_alloc_daily(task_id="daily_kline")["emitted"] == [pe.PF_ALLOC_KIND]
    queued = pe.pending()
    assert [e["kind"] for e in queued] == [pe.PF_ALLOC_KIND, pe.PF_ALLOC_KIND]
    assert sum(1 for e in queued if e.get("poison")) == 1

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-16")
    r = pe.maybe_emit_pf_alloc_daily(task_id="daily_kline")
    assert r["emitted"] == [pe.PF_ALLOC_KIND] and r["trade_date"] == "2026-09-16"


def test_wake_hook_orders_alloc_before_ledger_and_journal(state, monkeypatch, alerts):
    """端到端（全执行体打桩）：一次行情唤醒 → journal FIFO 顺序 alloc→ledger→journal。

    次序即接通：账本 ensure_wallet 读 alloc_budget_daily 当日行取钱包额度，分配若后排
    就永远读到空表 → 恒回退 flat 100 万（PFA-2 原状）。
    """
    class FakeScheduler:
        def subscribe(self, event, handler):
            self.h = handler

    order = []
    monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
    monkeypatch.setattr(pe, "scan_translated_backlog", lambda: {"backlog": []})
    monkeypatch.setattr(pe, "scan_c1_c2_backlog", lambda: {})
    monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
    monkeypatch.setattr(pe, "run_mount_audit", lambda: {"audit": "stub"})
    monkeypatch.setattr(pe, "run_sim_memo", lambda: {"memo": "stub"})
    monkeypatch.setattr(pe, "run_sim_deviation_monthly", lambda p: {"rc": 0, "month": "2026-09"})
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: DAY)
    monkeypatch.setattr(pe, "run_pf_alloc_daily",
                        lambda p: order.append("alloc") or {"rc": 0, "trade_date": p["trade_date"],
                                                            "alloc_brief": "run=alloc-x 落地=ch_committed"})
    monkeypatch.setattr(pe, "run_sim_ledger_daily", lambda p: order.append("ledger") or {"rc": 0})
    monkeypatch.setattr(pe, "run_sim_journal_daily", lambda p: order.append("journal") or {"rc": 0})

    s = FakeScheduler()
    pe.wire_data_scheduler(s)
    s.h(task_id="kline_index_incremental", success=True)

    assert order == ["alloc", "ledger", "journal"]
    assert [e["kind"] for e in pe.pending()] == []  # 全部轻 kind 消费完毕
    data = _markers(state)
    # 派发落 kind 级日号（唤醒侧去重）；trade_date 级双写闸号在真 handler 内落（见 ⑦）
    assert data[pe.PF_ALLOC_KIND]
    # 分配结果一行摘要进 drain 回执（持久人查面）——只进子进程 stdout=无人知晓=又变纸面链
    receipt = json.loads((state / "last_receipt.json").read_text(encoding="utf-8"))
    assert any(e.get("result", {}).get("alloc_brief") == "run=alloc-x 落地=ch_committed"
               for e in receipt["processed"] if e["kind"] == pe.PF_ALLOC_KIND)


def test_wake_hook_non_kline_task_emits_no_daily_events(state, monkeypatch, alerts):
    """非行情任务完成=不唤醒任何日频产出者（禁把分配链挂成"每次唤醒都跑"）。"""
    class FakeScheduler:
        def subscribe(self, event, handler):
            self.h = handler

    def boom():
        raise AssertionError("非行情唤醒点不得解析业务日")

    monkeypatch.setattr(pe, "kill_switch_clear", lambda: (True, "normal"))
    monkeypatch.setattr(pe, "scan_translated_backlog", lambda: {"backlog": []})
    monkeypatch.setattr(pe, "scan_c1_c2_backlog", lambda: {})
    monkeypatch.setattr(pe, "alert", lambda msg, level="WARN": None)
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", boom)
    s = FakeScheduler()
    pe.wire_data_scheduler(s)
    s.h(task_id="news_ingest", success=True)
    assert pe.pending() == []


# ── ⑥ 业务日解析：数据驱动 + 空表哨兵 fail-closed ──────────────────────
def test_business_day_resolves_from_latest_market_data(state, monkeypatch):
    import datetime as dt

    conn = _patch_ch(monkeypatch, [(dt.date(2026, 9, 15),)])
    assert pe.resolve_pf_alloc_trade_date() == DAY
    assert pe.PF_ALLOC_BIZ_DATE_SQL in conn.sqls[0]  # 单条只读模板，禁散落拼串


def test_business_day_rejects_empty_table_sentinel_and_null(state, monkeypatch):
    """CH 空表 max(Date) 回 1970-01-01 哨兵——按其分配=给 1970 年写只增不改的快照，必须拒。"""
    import datetime as dt

    for rows in ([(dt.date(1970, 1, 1),)], [(None,)], []):
        _patch_ch(monkeypatch, rows)
        with pytest.raises(RuntimeError, match="业务日"):
            pe.resolve_pf_alloc_trade_date()


# ── ⑦ 出声：落地结果进告警面与回执（不只在子进程 stdout）───────────────
def test_success_broadcasts_one_line_alloc_brief(state, spied, alerts, monkeypatch):
    import json as _json

    summary = {"run_id": f"alloc-{DAY}-abc123", "trade_date": DAY, "enabled": True,
               "portfolio_total_capital": 2000000.0, "global_shrinkage": 0.939332,
               "sum_effective_budget": 0.511328, "unallocated_cash": 977343.0,
               "cash_drag_capital": 1022657.0,
               "wallet_capital": {"STR-VREV-025": 655796.73, "STR-E-TIMING-001": 366860.27},
               "excluded_members": [], "cash_seats": [], "regime": {
                   "dominant": "r3", "source_date": "2026-09-11", "lag_days": 4},
               "warnings": ["cash_drag: 1"],
               "persisted": {"budget_daily": "ch_committed", "shrinkage_daily": "ch_committed"}}
    spied.box["proc"] = _FakeProc(stdout=_json.dumps(summary, ensure_ascii=False))

    out = pe.run_pf_alloc_daily({"trade_date": DAY})

    brief = out["alloc_brief"]
    assert summary["run_id"] in brief and "655796.73" in brief and "ch_committed" in brief
    assert "r3" in brief and "滞后4日" in brief  # 教材滞后是分配口径的一部分，须可见
    assert alerts and alerts[-1][1] == "INFO" and "已落地" in alerts[-1][0]


def test_brief_degrades_on_non_json_stdout_without_failing(state, spied, alerts):
    """stdout 非 JSON（CLI 版本漂移/额外打印）→ 退回首文本，绝不因摘要格式失败误判分配失败。"""
    spied.box["proc"] = _FakeProc(returncode=0, stdout="分配完成 {...truncated")
    out = pe.run_pf_alloc_daily({"trade_date": DAY})
    assert out["rc"] == 0 and "分配完成" in out["alloc_brief"]
    assert _markers(state)[f"{pe.PF_ALLOC_KIND}:{DAY}"]
