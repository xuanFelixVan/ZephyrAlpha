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
"""pf_alloc_daily 事件接线回归锁（车道 D 接线②：pipeline_events 轻 kind 派发 → 分配链装配体）。

锁的是"事件正门通到装配体"这条链的四个不变量（宪法 §9.3：触发面=事件，禁 cron/Timer/sleep）：
1. kind 归轻 kind（调度器唤醒钩子可消费）且非重 kind；派发分支把事件路由到 run_pf_alloc_daily；
2. 执行体=subprocess 隔离 `python -m zephyr.pf_alloc.allocation_orchestrator --date <D>`，
   超时有界（PF_ALLOC_TIMEOUT_S），业务日只认 payload（缺 trade_date 即抛，禁墙钟猜日）；
3. 同日幂等：同一 trade_date 已成功落地后再派发=零子进程调用（alloc 三表只增不改，
   无此闸=同日双写快照）；失败/超时不落 marker（重试路径不被自己的守卫堵死）；
4. 失败进既有重试语义：抛错 → drain 计 attempts，MAX_ATTEMPTS=3 后毒丸留档不再自动消费。

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
