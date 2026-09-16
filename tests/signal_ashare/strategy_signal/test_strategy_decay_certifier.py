# [BLUEPRINT] MOD-SIG-150 | tests/signal_ashare/strategy_signal/test_strategy_decay_certifier.py
# [TTL] permanent
"""strategy_decay_certifier 单测（SDC-1 施工后 2026-09-17）。

两极覆盖：
  判据可达 —— 真衰减证据（oos_years_decay）能产出 failed → 连周 → retired 建议，
              且建议**真的落到通知板**（既有出口 OpsAlertFeed，前端 promotion 页消费）；
  数据缺席 —— 零行输入=闸门失明：不判、不覆写台账、必落 critical + ERROR 出声，
              绝不静默当健康；注入合成 rows 时出口整条关闭（禁误碰生产板）。
台账/通知板一律 tmp_path，零生产 IO、零网络。
"""

from __future__ import annotations

import json
import logging

import pytest

import zephyr.signal_ashare.strategy_signal.strategy_decay_certifier as sdc
from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed
from zephyr.signal_ashare.strategy_signal.strategy_decay_certifier import (
    FAILED_WINDOWS,
    LEDGER_PATH,
    load_latest_metrics,
    run_strategy_decay_certify,
)

_BLIND_KEY = "strategy_decay_gate_blind"
_STATES = ("certified", "probation", "failed", "retired", "resurrected")


def _row(sid: str, ds: float | None, decay: float | None = 0.0) -> dict:
    """load_latest_metrics 产物形状（5 键；decay=None 即该列 NULL）。"""
    return {"strategy_id": sid, "deflated_sharpe": ds, "is_sharpe": 1.0,
            "max_drawdown": 0.1, "oos_years_decay": decay}


class _FakeClient:
    """假 CH client：按注入顺序回放裸行，last-wins 去重交给被测函数本体。"""

    def __init__(self, rows):
        self._rows = rows
        self.sql: list[str] = []

    def execute(self, sql, params=None):
        self.sql.append(sql)
        return self._rows


def _unresolved(feed: OpsAlertFeed) -> dict[str, dict]:
    return {e["key"]: e for e in feed.list_active()
            if e.get("module_id") == "strategy-decay-gate" and not e.get("resolved_at")}


# ── ① 判定：三态 + 证据缺席 + 越域 ────────────────────────────────────────────


def test_decay_evidence_drives_all_three_live_states(tmp_path):
    """DS 达线但衰减越线=failed（旧死分支的现实替身）；证据双缺=probation 封顶。"""
    ledger = tmp_path / "led.json"
    r = run_strategy_decay_certify(
        ledger_path=ledger, today="D1",
        rows=[_row("S-cert", 0.8, 0.1), _row("S-fail", 0.9, 0.6),
              _row("S-low", 0.2, 0.1), _row("S-none", None, None)],
    )
    assert r["counts"] == {"certified": 1, "probation": 2, "failed": 1,
                           "retired": 0, "resurrected": 0}
    assert r["no_evidence"] == 1 and r["blind_scan"] is False
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["S-fail"]["reason"].startswith("按年外样本衰减 0.6")
    assert doc["strategies"]["S-none"]["reason"].startswith("证据双缺")
    assert doc["strategies"]["S-cert"]["oos_years_decay"] == 0.1


def test_ds_out_of_domain_is_upstream_incident_not_a_verdict(tmp_path):
    """DS 越出 [0,1]（生产 1205 行实测负值 0 行）=上游口径事故：封顶不判死、不续连周。"""
    ledger = tmp_path / "led.json"
    r = run_strategy_decay_certify(
        ledger_path=ledger, today="D1", rows=[_row("S-BAD", -0.2, None)],
    )
    assert r["counts"] == {"certified": 0, "probation": 1, "failed": 0,
                           "retired": 0, "resurrected": 0}
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert "上游口径事故" in doc["strategies"]["S-BAD"]["reason"]
    assert doc["strategies"]["S-BAD"]["failed_streak"] == 0


def test_counts_always_expose_every_state(tmp_path):
    """counts 恒含全部五键（SDC-1「失败模式不可见」治本：0 也必须显式在场）。"""
    r = run_strategy_decay_certify(
        ledger_path=tmp_path / "led.json", today="D1", rows=[_row("S1", 0.8, 0.1)])
    assert set(r["counts"]) == set(_STATES)


# ── ② 退役链：连周 failed → retired → 通知板真的收到 ─────────────────────────


def test_failed_streak_retires_and_lands_on_notification_board(tmp_path):
    """连周判死→retired 建议，且建议真的被既有出口收下（不是产而不消）。"""
    ledger, board = tmp_path / "led.json", tmp_path / "board"
    feed = OpsAlertFeed(board_dir=board, module_id="strategy-decay-gate")
    for w in range(FAILED_WINDOWS - 1):
        r = run_strategy_decay_certify(ledger_path=ledger, today=f"W{w}",
                                       rows=[_row("STR-C", 0.2, 0.8)], alert_feed=feed)
        assert r["counts"]["retired"] == 0 and _unresolved(feed) == {}
    r = run_strategy_decay_certify(ledger_path=ledger, today=f"W{FAILED_WINDOWS}",
                                   rows=[_row("STR-C", 0.2, 0.8)], alert_feed=feed)
    assert r["counts"]["retired"] == 1
    key = "strategy_retirement_advice:STR-C"
    entry = _unresolved(feed)[key]
    assert entry["severity"] == "critical"
    assert entry["labels"]["failed_streak"] == FAILED_WINDOWS
    assert entry["labels"]["ledger"] == LEDGER_PATH
    assert "退役**建议**" in entry["message"] and "oos_years_decay" in entry["message"]
    assert r["alerts"]["outlet"] == "injected" and r["alerts"]["retired"] == 1
    assert any(op.get("op") == "created" for op in r["alerts"]["ops"])


def test_retirement_advice_resolves_when_decay_clears(tmp_path):
    """不再 retired=板上那条必须被解除（出口不是只写不销的单向道）。"""
    ledger, board = tmp_path / "led.json", tmp_path / "board"
    feed = OpsAlertFeed(board_dir=board, module_id="strategy-decay-gate")
    for w in range(FAILED_WINDOWS):
        run_strategy_decay_certify(ledger_path=ledger, today=f"W{w}",
                                   rows=[_row("STR-C", 0.2, 0.8)], alert_feed=feed)
    assert _unresolved(feed)
    r = run_strategy_decay_certify(ledger_path=ledger, today="CLEAN",
                                   rows=[_row("STR-C", 0.9, 0.1)], alert_feed=feed)
    assert r["counts"]["resurrected"] == 1
    assert _unresolved(feed) == {}
    assert any(op.get("op") == "resolved" for op in r["alerts"]["ops"])


def test_resurrection_needs_double_evidence(tmp_path):
    """退役后单证（DS 达线但衰减 NULL）不许悄悄复活——复活是再准入，缺证维持退役。"""
    ledger = tmp_path / "led.json"
    for w in range(FAILED_WINDOWS):
        run_strategy_decay_certify(ledger_path=ledger, today=f"W{w}",
                                   rows=[_row("STR-C", 0.2, 0.8)])
    keep = run_strategy_decay_certify(ledger_path=ledger, today="R1",
                                      rows=[_row("STR-C", 0.9, None)])
    assert keep["counts"]["retired"] == 1
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert "复活需双证" in doc["strategies"]["STR-C"]["reason"]
    back = run_strategy_decay_certify(ledger_path=ledger, today="R2",
                                      rows=[_row("STR-C", 0.9, 0.2)])
    assert back["counts"]["resurrected"] == 1
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-C"]["resurrected_at"] == "R2"


def test_resurrected_is_not_a_permanent_exemption(tmp_path):
    """复活态回落常规判定：下轮衰减再越线重新计连周（一次复活≠永久豁免衰减闸）。"""
    ledger = tmp_path / "led.json"
    for w in range(FAILED_WINDOWS):
        run_strategy_decay_certify(ledger_path=ledger, today=f"W{w}",
                                   rows=[_row("STR-C", 0.2, 0.8)])
    run_strategy_decay_certify(ledger_path=ledger, today="R1", rows=[_row("STR-C", 0.9, 0.2)])
    for w in range(FAILED_WINDOWS):
        r = run_strategy_decay_certify(ledger_path=ledger, today=f"S{w}",
                                       rows=[_row("STR-C", 0.2, 0.8)])
    assert r["counts"]["retired"] == 1


# ── ③ 失明：零行输入绝不静默当健康 ───────────────────────────────────────────


def test_zero_rows_is_blind_scan_and_preserves_ledger(tmp_path, caplog):
    """零行=不判、不覆写台账、ERROR 出声（旧行为会把 8 周连周计数整本抹掉）。"""
    ledger = tmp_path / "led.json"
    seed = {"schema": "strategy_decay/2", "updated_at": "D0",
            "strategies": {"STR-C": {"state": "failed", "failed_streak": 7}}}
    ledger.write_text(json.dumps(seed), encoding="utf-8")
    before = ledger.read_text(encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        r = run_strategy_decay_certify(ledger_path=ledger, today="D1", rows=[])
    assert r["blind_scan"] is True and r["total"] == 0
    assert set(r["counts"]) == set(_STATES) and sum(r["counts"].values()) == 0
    assert ledger.read_text(encoding="utf-8") == before          # 台账一字未动
    assert any("失明" in rec.message for rec in caplog.records if rec.levelno >= logging.ERROR)
    assert r["alerts"]["ops"][0]["op"] == "skipped"               # 离线模式不外呼


def test_blind_scan_publishes_critical_and_next_round_resolves(tmp_path):
    """失明告警真落板，且恢复读数后自动解除（不留僵尸横幅）。"""
    ledger, board = tmp_path / "led.json", tmp_path / "board"
    feed = OpsAlertFeed(board_dir=board, module_id="strategy-decay-gate")
    run_strategy_decay_certify(ledger_path=ledger, today="D1", rows=[], alert_feed=feed)
    entry = _unresolved(feed)[_BLIND_KEY]
    assert entry["severity"] == "critical" and "不得把 counts 全零读成" in entry["message"]
    run_strategy_decay_certify(ledger_path=ledger, today="D2", rows=[_row("S1", 0.8, 0.1)],
                               alert_feed=feed)
    assert _unresolved(feed) == {}


def test_injected_rows_never_construct_production_board(tmp_path, monkeypatch):
    """合成宇宙不做 resolve 联动：rows 注入而未给 feed=整条出口关闭（零板 IO）。"""
    def _boom(*a, **k):  # pragma: no cover - 命中即红
        raise AssertionError("离线判定不得构造生产通知板")

    monkeypatch.setattr(sdc, "_feed", _boom)
    r = run_strategy_decay_certify(ledger_path=tmp_path / "led.json", today="D1",
                                   rows=[_row("S1", 0.2, 0.9)])
    assert r["alerts"] == {"retired": 0, "ops": [], "outlet": "off"}


def test_broken_alert_outlet_does_not_break_ledger(tmp_path, monkeypatch):
    """告警通道任何故障不反噬台账产出（INVARIANTS）：出口 unavailable，台账照落。"""
    monkeypatch.setattr(sdc, "_feed", lambda *a, **k: None)
    ledger = tmp_path / "led.json"
    client = _FakeClient([("S1", 0.8, 1.2, 0.1, 0.1)])
    r = run_strategy_decay_certify(client=client, ledger_path=ledger, today="D1", rows=None)
    assert r["counts"]["certified"] == 1 and r["alerts"]["outlet"] == "unavailable"
    assert json.loads(ledger.read_text(encoding="utf-8"))["strategies"]["S1"]["state"] == "certified"


# ── ④ 读数：平序键显式化 + 台账容错 ─────────────────────────────────────────


def test_load_latest_metrics_last_wins_and_carries_decay_column():
    """同策略多行按给定序 last-wins（表非 Replacing，去重在内存做）。"""
    client = _FakeClient([
        ("S1", 0.1, 1.0, 0.4, 0.9), ("S1", 0.8, 1.1, 0.1, 0.0), ("S2", None, None, None, None),
    ])
    out = load_latest_metrics(client)
    assert {r["strategy_id"]: r for r in out}["S1"]["deflated_sharpe"] == 0.8
    assert set(out[0]) == {"strategy_id", "deflated_sharpe", "is_sharpe", "max_drawdown",
                           "oos_years_decay"}
    sql = client.sql[0]
    assert "c1_backtest.strategy_screen" in sql
    for tie in ("screen_batch", "strategy_id", "run_id", "ingest_ts"):
        assert tie in sql.split("ORDER BY", 1)[1], f"平序键 {tie} 未显式给出（SDC-5）"


def test_corrupt_ledger_restarts_streak_with_warning(tmp_path, caplog):
    """台账解析失败=按无历史重起并 WARNING 出声，不猜状态也不抛。"""
    ledger = tmp_path / "led.json"
    ledger.write_text("{not json", encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        r = run_strategy_decay_certify(ledger_path=ledger, today="D1",
                                       rows=[_row("S1", 0.2, 0.8)])
    assert r["counts"]["failed"] == 1
    doc = json.loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["S1"]["failed_streak"] == 1
    assert any("衰减台账解析失败" in rec.message for rec in caplog.records)


def test_full_scan_round_trip_through_fake_client(tmp_path):
    """rows=None 真读路径也走同一判定链（fake client 注入，不触库）。"""
    ledger = tmp_path / "led.json"
    r = run_strategy_decay_certify(
        client=_FakeClient([("S1", 0.9, 1.3, 0.1, 0.7), ("S2", 0.9, 1.3, 0.1, 0.0)]),
        ledger_path=ledger, today="D1", rows=None)
    assert r["counts"]["failed"] == 1 and r["counts"]["certified"] == 1
    assert r["alerts"]["retired"] == 0
