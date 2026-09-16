# [A_test] module_id: MOD-DATA-BREADTHALERT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.data.implementations.test_breadth_freshness_alerts
# [TESTS] src/zephyr/data/implementations/breadth_freshness_alerts.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""车道 G 广度断供哨兵单测：零值/缺行判据 → OpsAlertFeed 唯一出口（promotion 页）落板/解除。

CH 读与告警板全注入（reader 替身 + tmp_path 板目录），禁触网、禁写生产 .runtime。
锚定不变式：
  1. 断供必可见——尾部连续缺位达阈值即落板，零值与整行缺失同判；
  2. 消息必须报"缺位天数"（补位不得永久遮蔽真源缺失的外显证据）；
  3. 缺口填平 → resolve（灰显解除）；
  4. 扫描自身失败 → selfcheck critical（哨兵失能=断供重新隐身）；
  5. 未达阈值不刷板（容忍盘后任务单日晚到）。
"""

from __future__ import annotations

import datetime
import json

import pytest

from zephyr.data.implementations.breadth_freshness_alerts import (
    INDEX_UNIVERSE,
    BreadthFreshnessAlerts,
    run_check,
)

_DAYS = [f"2026-09-{d:02d}" for d in range(1, 11)]  # 10 个"交易日"


def _reader(state_by_symbol: dict[str, dict[str, int]], days: list[str] | None = None):
    """CH 只读替身：state_by_symbol[sym][date] = ok 家数（缺键=整行缺失）。"""
    if days is None:  # 显式传 [] 表示「日历查不到行」，不能被 or 吞回默认值
        days = _DAYS
    calls: list[str] = []

    def _query(sql: str, timeout: int = 30) -> str:
        calls.append(sql)
        if "SELECT cal_date" in sql:
            return "".join(d + "\n" for d in days)
        if "countIf(advance_count > 0 OR decline_count > 0)" in sql:
            lines = []
            for sym, per_day in state_by_symbol.items():
                for d in days:
                    if d in per_day:
                        lines.append(f"{sym}\t{d}\t{per_day[d]}\t1")
            return "".join(x + "\n" for x in lines)
        raise AssertionError(f"未预期 SQL: {sql[:160]}")

    _query.calls = calls  # type: ignore[attr-defined]
    return _query


def _board(tmp_path):
    return tmp_path / "ops_board"


def _entries(tmp_path):
    f = _board(tmp_path) / "notifications.jsonl"
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def _one(tmp_path, key):
    hits = [e for e in _entries(tmp_path) if e["key"] == key]
    assert hits, f"{key} 未落板: {[e['key'] for e in _entries(tmp_path)]}"
    return hits[-1]


def _zero_tail(n: int, days: list[str] | None = None) -> dict[str, int]:
    """末 n 日宽度双零、其余正常的单标的状态。"""
    days = days or _DAYS
    bad = set(days[-n:])
    return {d: (0 if d in bad else 500) for d in days}


# ── 检测 ────────────────────────────────────────────────────────────────


def test_scan_detects_trailing_zero_breadth():
    r = _reader({"399106": _zero_tail(3)})
    items = BreadthFreshnessAlerts(reader=r).scan(today=datetime.date(2026, 9, 11))
    hit = next(i for i in items if i["symbol"] == "399106")
    assert hit["trailing_bad"] == 3 and hit["total_bad"] == 3
    assert hit["gap_start"] == _DAYS[-3] and hit["gap_end"] == _DAYS[-1]
    assert hit["universe"] == "SZ"


def test_scan_treats_missing_row_as_bad_and_counts_it():
    per_day = {d: 500 for d in _DAYS[:-2]}  # 末 2 日整行缺失
    items = BreadthFreshnessAlerts(reader=_reader({"399106": per_day})).scan(
        today=datetime.date(2026, 9, 11)
    )
    hit = next(i for i in items if i["symbol"] == "399106")
    assert hit["missing_rows"] == 2 and hit["trailing_bad"] == 2


def test_scan_ignores_single_day_lag_below_threshold():
    """尾部仅 1 日缺位=可能任务晚到，不刷板（防 23:00 巡检边界抖动）。"""
    items = BreadthFreshnessAlerts(reader=_reader({"399106": _zero_tail(1)})).scan(
        today=datetime.date(2026, 9, 11)
    )
    assert not [i for i in items if i["symbol"] == "399106"]


def test_scan_no_items_when_all_days_ok():
    all_ok = {sym: {d: 500 for d in _DAYS} for sym in INDEX_UNIVERSE}
    items = BreadthFreshnessAlerts(reader=_reader(all_ok)).scan(
        today=datetime.date(2026, 9, 11)
    )
    assert items == []


def test_scan_requires_trading_calendar(tmp_path):
    """日历空=失去判据，必须以异常上抛（由 run_check 转 selfcheck 告警）。"""
    with pytest.raises(RuntimeError, match="交易日"):
        BreadthFreshnessAlerts(reader=_reader({}, days=[])).scan(today=datetime.date(2026, 9, 11))


# ── 发布/解除（唯一出口） ──────────────────────────────────────────────


def test_run_check_publishes_warning_with_gap_days(tmp_path):
    res = run_check(
        today=datetime.date(2026, 9, 11),
        board_dir=str(_board(tmp_path)),
        reader=_reader({"399106": _zero_tail(3)}),
    )
    assert res["triggered"] >= 1 and res["scan_error"] is None
    e = _one(tmp_path, "breadth_gap:399106")
    assert e["severity"] == "warning"
    assert e["module_id"] == "breadth-freshness-sentinel"
    assert "连续 3 个交易日无值" in e["message"]
    assert "EQW_ALLA" in e["message"]  # 补位遮蔽真源缺失的外显提示
    assert e["labels"]["trailing_bad"] == 3
    assert e["labels"]["feed_task"] == "kline_index_breadth_refresh"


def test_run_check_escalates_to_critical_at_five_days(tmp_path):
    run_check(
        today=datetime.date(2026, 9, 11),
        board_dir=str(_board(tmp_path)),
        reader=_reader({"399106": _zero_tail(6)}),
    )
    assert _one(tmp_path, "breadth_gap:399106")["severity"] == "critical"


def test_run_check_resolves_when_gap_healed(tmp_path):
    all_bad = {sym: _zero_tail(4) for sym in INDEX_UNIVERSE}
    run_check(
        today=datetime.date(2026, 9, 11),
        board_dir=str(_board(tmp_path)),
        reader=_reader(all_bad),
    )
    assert _one(tmp_path, "breadth_gap:399106")["resolved_at"] is None
    all_ok = {sym: {d: 500 for d in _DAYS} for sym in INDEX_UNIVERSE}
    res = run_check(
        today=datetime.date(2026, 9, 11),
        board_dir=str(_board(tmp_path)),
        reader=_reader(all_ok),
    )
    assert any(o.get("op") == "resolved" for o in res["ops"])
    assert _one(tmp_path, "breadth_gap:399106")["resolved_at"] is not None


def test_scan_failure_publishes_selfcheck_critical(tmp_path):
    def _boom(sql: str, timeout: int = 30) -> str:
        raise RuntimeError("CH 不可达")

    res = run_check(
        today=datetime.date(2026, 9, 11), board_dir=str(_board(tmp_path)), reader=_boom
    )
    assert "CH 不可达" in (res["scan_error"] or "")
    e = _one(tmp_path, "breadth_scan_failed")
    assert e["severity"] == "critical"


def test_selfcheck_resolves_once_scanner_recovers(tmp_path):
    def _boom(sql: str, timeout: int = 30) -> str:
        raise RuntimeError("CH 不可达")

    run_check(today=datetime.date(2026, 9, 11), board_dir=str(_board(tmp_path)), reader=_boom)
    assert _one(tmp_path, "breadth_scan_failed")["resolved_at"] is None
    all_ok = {sym: {d: 500 for d in _DAYS} for sym in INDEX_UNIVERSE}
    run_check(
        today=datetime.date(2026, 9, 11),
        board_dir=str(_board(tmp_path)),
        reader=_reader(all_ok),
    )
    assert _one(tmp_path, "breadth_scan_failed")["resolved_at"] is not None


def test_publish_never_raises_on_board_failure(tmp_path, monkeypatch):
    """告警线自身不得成为故障源：落板异常只记日志。"""
    alerts = BreadthFreshnessAlerts(board_dir=str(_board(tmp_path)), reader=_reader({}))

    class _Broken:
        def publish(self, **kw):
            raise OSError("disk full")

        def list_active(self):
            raise OSError("board unreadable")

        def resolve(self, key):
            raise OSError("board unwritable")

    monkeypatch.setattr(alerts, "_feed", lambda: _Broken())
    out = alerts.publish([{"symbol": "399106", "universe": "SZ", "trailing_bad": 9, "total_bad": 9, "gap_start": "x", "gap_end": "y", "missing_rows": 0}])
    assert any(o.get("op") == "failed" for o in out["ops"])
