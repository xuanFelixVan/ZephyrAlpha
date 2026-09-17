# [A_test] module_id: MOD-PLAN-027 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-027 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §四
# [MODULE] tests.plan_engine.test_judgment_settler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""judgment_settler 共享结算器施工验证测试（判定台账标准 v0.1 §四）。

覆盖：
- diebold_mariano 纯函数：同分布→0；完美 vs 差预测→大统计量；参数 fail-closed。
- 单行结算纯逻辑（行情以映射注入）：next_day（brier/log_loss/label 手算对账/
  未到期/行情断供 gap/坏 payload/subject 未映射）；intraday（p_bull/当日未收盘/
  隔日无行情）；daily_plan（verification 联结/当日宽限/隔日无验证=unresolvable）。
- 回填 SQL：evaluated_at IS NULL 双闸在 WHERE（重复回填防御——红蓝项）；结算
  列组白名单；mutations_sync 同步等待；判定列组永不出现在 SET（铁律）。
- settle_table 组合：canned 通道注入 → 报告计数/单行回填失败计 failed 不中断。
- aggregate_report：SQL 组装（synthetic 过滤/窗口）；结果行解析。
- 事件挂点 maybe_settle_judgment_ledger：非 daily_kline 唤醒点跳过；marker 幂等；
  settle_all 异常不反噬（error 返回）；成功出 brief。
全 monkeypatch 隔离，不触真 ClickHouse（真库冒烟走 synthetic 标注+清理通道）。
"""

from __future__ import annotations

import json
import math
from typing import Any

import pytest

from zephyr.plan_engine import judgment_settler as js
from zephyr.plan_engine.brier_calibration import brier_score, brier_score_multiclass
from zephyr.strategy_pipeline import pipeline_events as pe


# ── DM 纯函数 ──


def test_dm_identical_losses_zero() -> None:
    assert js.diebold_mariano([0.5] * 20, [0.5] * 20) == 0.0
    # 恒定非零差分（零方差）=差异确定性存在 → 无穷大统计量（带符号）


def test_dm_perfect_beats_poor() -> None:
    a = [0.01] * 30  # 预测者 A 损失近零
    b = [0.5] * 30  # 预测者 B 一半错
    stat = js.diebold_mariano(a, b)
    assert stat == -math.inf  # 恒定差分零方差 → -inf（负=A 显著占优，见 docstring 惯例）


def test_dm_noisy_losses_positive() -> None:
    a = [0.2, 0.3, 0.1, 0.25, 0.15] * 6
    b = [0.6, 0.5, 0.7, 0.55, 0.65] * 6
    assert js.diebold_mariano(a, b) < -1.96  # 噪声差分仍显著负=A 更优


def test_dm_validation() -> None:
    with pytest.raises(ValueError):
        js.diebold_mariano([], [])
    with pytest.raises(ValueError):
        js.diebold_mariano([1.0], [1.0, 2.0])
    with pytest.raises(ValueError):
        js.diebold_mariano([1.0], [1.0], h=0)


# ── next_day 单行结算 ──


def _row(jid: str, payload: dict[str, Any] | str, subject: str = "index:000300.SH",
         asof: str = "2026-09-15 08:00:00.000") -> dict[str, Any]:
    return {
        "judgment_id": jid,
        "module_id": "MOD-TEST",
        "model_version": "v1",
        "asof_ts": asof,
        "subject": subject,
        "payload": payload if isinstance(payload, str) else json.dumps(payload),
        "confidence": 0.6,
    }


_CAL = {"2026-09-15": 4000.0, "2026-09-16": 4040.0}  # T→T+1 收盘（+1.0%）


def test_settle_next_day_happy_path() -> None:
    payload = {"p_up": 0.5, "p_flat": 0.3, "p_down": 0.2}
    backfill, res, _ = js._settle_next_day(_row("J1", payload), _CAL)
    assert res.action == "settled" and backfill is not None
    # 手算对账：ret=+1% → label=up（±0.1% 带宽）；brier=Σ(p_k-o_k)²
    assert backfill["realized_return"] == pytest.approx(0.01)
    assert backfill["realized_label"] == "up"
    expected_brier = brier_score_multiclass([([0.5, 0.3, 0.2], 0)])
    assert backfill["brier_score"] == pytest.approx(expected_brier)
    assert backfill["eval_score"] == pytest.approx(expected_brier)
    assert backfill["log_loss"] == pytest.approx(-math.log(0.5))
    assert backfill["calibration_bucket"] == "0.5-0.6"
    assert json.loads(backfill["outcome_value"])["hit"] is True  # argmax=up 且实际 up


def test_settle_next_day_wrong_prediction_hit_false() -> None:
    payload = {"p_up": 0.1, "p_flat": 0.2, "p_down": 0.7}
    backfill, res, _ = js._settle_next_day(_row("J2", payload), _CAL)
    assert res.action == "settled"
    assert backfill["realized_label"] == "up"
    assert json.loads(backfill["outcome_value"])["hit"] is False  # argmax=down 实际 up
    assert backfill["log_loss"] == pytest.approx(-math.log(0.1))  # 实际格概率=0.1


def test_settle_next_day_not_matured_when_no_future_kline() -> None:
    cal = {"2026-09-10": 4000.0}
    _, res, permanent = js._settle_next_day(_row("J3", {"p_up": 0.3, "p_flat": 0.3, "p_down": 0.4},
                                                asof="2026-09-10 08:00:00.000"), cal)
    assert res.action == "not_matured" and not permanent


def test_settle_next_day_gap_unresolvable() -> None:
    """行情断供：asof→target 间隔超限=unresolvable 留痕（禁跳过式静默）。"""
    cal = {"2026-09-01": 4000.0, "2026-10-01": 4040.0}
    _, res, permanent = js._settle_next_day(
        _row("J4", {"p_up": 0.3, "p_flat": 0.3, "p_down": 0.4}, asof="2026-09-01 08:00:00.000"), cal)
    assert res.action == "unresolvable" and permanent
    assert "gap" in res.reason


def test_settle_next_day_bad_payload_and_subject() -> None:
    _, res, _ = js._settle_next_day(_row("J5", "{bad json"), _CAL)
    assert res.action == "unresolvable" and "bad_json" in res.reason
    _, res2, _ = js._settle_next_day(_row("J6", {"p_up": 0.3, "p_flat": 0.3, "p_down": 0.4},
                                          subject="sector:880-001"), _CAL)
    assert res2.action == "unresolvable" and res2.reason == "subject_unmapped"
    _, res3, _ = js._settle_next_day(_row("J7", {"foo": 1}), _CAL)
    assert res3.action == "unresolvable" and res3.reason == "payload_missing_probs"
    _, res4, _ = js._settle_next_day(_row("J8", {"p_up": 0.3, "p_flat": 0.3, "p_down": 0.4},
                                          asof="2026-09-14 08:00:00.000"),
                                     {"2026-09-16": 4040.0})  # asof 当日无 K 线
    assert res4.action == "unresolvable" and res4.reason == "asof_date_no_kline"


# ── intraday 单行结算 ──

_OHLC = {"2026-09-15": (4000.0, 4060.0)}  # 当日 +1.5%


def _irow(jid: str, payload: dict[str, Any], asof: str = "2026-09-15 06:00:00.000",
          subject: str = "index:000300.SH") -> dict[str, Any]:
    return {"judgment_id": jid, "module_id": "MOD-TEST", "model_version": "v1",
            "asof_ts": asof, "subject": subject, "payload": json.dumps(payload),
            "confidence": 0.7}


def test_settle_intraday_happy_path() -> None:
    payload = {"state_label": "进攻",
               "state_probs": {"低迷": 0.05, "防御": 0.05, "震荡": 0.15, "进攻": 0.6, "亢奋": 0.15}}
    backfill, res, _ = js._settle_intraday(_irow("I1", payload), _OHLC)
    assert res.action == "settled"
    assert backfill["realized_close_vs_open"] == pytest.approx(0.015)
    assert backfill["state_realized"] == "up"  # +1.5% > ±0.3% 带宽
    assert backfill["brier_contrib"] == pytest.approx(brier_score([(0.75, 1.0)]))  # p_bull=0.75
    assert "pending_minute_source" in backfill["outcome_value"]  # 尾盘列不伪造
    assert json.loads(backfill["outcome_value"])["hit"] is True  # p_bull>=0.5 判对


def test_settle_intraday_same_day_not_matured() -> None:
    payload = {"state_label": "进攻", "state_probs": {"进攻": 0.6, "亢奋": 0.4}}
    # 16 日判定但 16 日 K 线未入库（最新=15）→ not_matured（当日未收盘）
    _, res3, permanent = js._settle_intraday(
        _irow("I3", payload, asof="2026-09-16 06:00:00.000"), dict(_OHLC))
    assert res3.action == "not_matured" and not permanent
    # 14 日判定但 14 日 K 线缺失（15 已在=已过）→ unresolvable
    _, res4, permanent4 = js._settle_intraday(
        _irow("I4", payload, asof="2026-09-14 06:00:00.000"), dict(_OHLC))
    assert res4.action == "unresolvable" and permanent4


# ── daily_plan 单行结算 ──

_PLAN = {"scenarios": [
    {"scenario_id": "S1", "trigger": "gap>0.5", "action": "wait", "path_prior": 0.5},
    {"scenario_id": "S2", "trigger": "ratio<0.8", "action": "stand", "path_prior": 0.5}]}
_VER = {"P1": {"actual_scenario_id": "S1", "plan_followed": 1,
               "scenario_hits": json.dumps([{"scenario_id": "S1", "trigger_ts": "t", "trigger_price": 1.0}]),
               "verified_at": "2026-09-15 07:00:00.000"}}


def test_settle_daily_plan_with_verification() -> None:
    backfill, res, _ = js._settle_daily_plan(
        _row("P1", _PLAN, asof="2026-09-15 01:00:00.000"), _VER, latest_day="2026-09-15")
    assert res.action == "settled"
    assert backfill["actual_scenario_id"] == "S1"
    assert backfill["scenario_brier"] == pytest.approx(brier_score_multiclass([([0.5, 0.5], 0)]))
    ov = json.loads(backfill["outcome_value"])
    assert ov["hit"] is True and ov["plan_followed"] is True and ov["n_hits"] == 1


def test_settle_daily_plan_grace_and_missing() -> None:
    _, res, permanent = js._settle_daily_plan(
        _row("P2", _PLAN, asof="2026-09-15 01:00:00.000"), {}, latest_day="2026-09-15")
    assert res.action == "not_matured" and not permanent  # 当日宽限
    _, res2, permanent2 = js._settle_daily_plan(
        _row("P3", _PLAN, asof="2026-09-14 01:00:00.000"), {}, latest_day="2026-09-15")
    assert res2.action == "unresolvable" and permanent2
    assert res2.reason == "verification_missing"


def test_settle_daily_plan_unknown_actual() -> None:
    ver = {"P4": {"actual_scenario_id": "S9", "plan_followed": 0, "scenario_hits": "[]",
                  "verified_at": "2026-09-15 07:00:00.000"}}
    _, res, _ = js._settle_daily_plan(
        _row("P4", _PLAN, asof="2026-09-14 01:00:00.000"), ver, latest_day="2026-09-15")
    assert res.action == "unresolvable" and res.reason == "actual_scenario_unknown"


# ── 回填 SQL（双闸/白名单）──


def test_backfill_sql_double_guard_and_whitelist(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    def fake_writer(sql: str) -> None:
        captured.append(sql)

    monkeypatch.setattr(js, "_writer_execute", fake_writer)
    settled_at = "2026-09-16 08:00:00.000"
    js._backfill_row("c1_market.judgment_next_day_forecast", "next_day_forecast", "J1",
                     {"realized_return": 0.01, "realized_label": "up", "brier_score": 0.42,
                      "log_loss": 0.69, "calibration_bucket": "0.5-0.6",
                      "outcome_value": '{"hit": true}', "eval_method": "brier_multiclass",
                      "eval_score": 0.42}, settled_at)
    sql = captured[0]
    assert sql.startswith("ALTER TABLE c1_market.judgment_next_day_forecast UPDATE")
    assert "evaluated_at IS NULL" in sql  # 双闸：并发结算器后到者命中 0 行
    assert "judgment_id = 'J1'" in sql
    assert "mutations_sync" in sql  # 同步等待：回填假成功免疫
    for judgment_col in ("payload =", "confidence =", "module_id ="):
        assert judgment_col not in sql  # 判定列组永不被 UPDATE（铁律）
    assert "evaluated_at = '2026-09-16 08:00:00.000'" in sql

    js._backfill_unresolvable("c1_market.judgment_next_day_forecast", "J2", "target_gap_30d_no_kline",
                              settled_at)
    sql2 = captured[1]
    assert "eval_method = 'unresolvable'" in sql2 and "reason" in sql2
    assert "evaluated_at IS NULL" in sql2


def test_sql_literal_escapes() -> None:
    assert js._sql_literal("it's") == "'it\\'s'"
    assert js._sql_literal(True) == "1"
    assert js._sql_literal(0.25) == "0.25"
    with pytest.raises(ValueError):
        js._sql_literal({"dict": 1})


# ── settle_table 组合（通道注入）──


def test_settle_table_integration(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [
        _row("K1", {"p_up": 0.5, "p_flat": 0.3, "p_down": 0.2}, asof="2026-09-15 08:00:00.000"),
        _row("K2", "{broken", asof="2026-09-15 08:00:00.000"),
        _row("K3", {"p_up": 0.3, "p_flat": 0.3, "p_down": 0.4}, asof="2026-09-16 08:00:00.000"),
    ]
    monkeypatch.setattr(js, "_scan_unsettled", lambda t: rows)
    monkeypatch.setattr(js, "_load_kline_calendar", lambda s: dict(_CAL))
    backfills: list[str] = []
    monkeypatch.setattr(js, "_writer_execute", lambda sql: backfills.append(sql))
    report = js.settle_table("next_day_forecast", asof_day="2026-09-16")
    assert report.scanned == 3
    assert report.settled == 1  # K1
    assert report.unresolvable == 1  # K2 坏 payload
    assert report.not_matured == 1  # K3 T+1 未收盘（cal 最新=16，target 无）
    assert report.failed == 0
    assert len(backfills) == 2  # settled + unresolvable 各一条 mutation


def test_settle_table_backfill_error_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [_row("F1", {"p_up": 0.5, "p_flat": 0.3, "p_down": 0.2}, asof="2026-09-15 08:00:00.000")]
    monkeypatch.setattr(js, "_scan_unsettled", lambda t: rows)
    monkeypatch.setattr(js, "_load_kline_calendar", lambda s: dict(_CAL))

    def boom(sql: str) -> None:
        raise RuntimeError("channel dead")

    monkeypatch.setattr(js, "_writer_execute", boom)
    report = js.settle_table("next_day_forecast", asof_day="2026-09-16")
    assert report.failed == 1 and report.settled == 0  # 单行失败不中断，留待下轮


def test_settle_table_unknown_key() -> None:
    with pytest.raises(ValueError, match="table_key"):
        js.settle_table("nope")


# ── aggregate_report ──


def test_aggregate_report_sql_and_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def fake_reader(sql: str) -> list[tuple]:
        captured["sql"] = sql
        return [("MOD-A", "v1", 10, 8, 1, 0.21, 0.55, 0.75)]

    monkeypatch.setattr(js, "_reader_execute", fake_reader)
    out = js.aggregate_report("next_day_forecast", window_days=7, asof_day="2026-09-16",
                              synthetic=False)
    assert "AND synthetic = 0" in captured["sql"]
    assert "2026-09-10" in captured["sql"]  # 7 日窗口起点
    groups = out["next_day_forecast"]
    assert groups[0]["module_id"] == "MOD-A" and groups[0]["n_settled"] == 8
    assert groups[0]["hit_rate"] == pytest.approx(0.75)


def test_aggregate_report_all_tables_and_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(js, "_reader_execute", lambda sql: [])
    out = js.aggregate_report(asof_day="2026-09-16")
    assert set(out) == set(js._SETTLE_TABLES)
    with pytest.raises(ValueError):
        js.aggregate_report("bogus")


# ── 事件挂点（照抄 regime 先例）──


def test_hook_skips_non_wake_points(monkeypatch: pytest.MonkeyPatch) -> None:
    assert pe.maybe_settle_judgment_ledger(task_id="c4_batch_screen", success=True) == {
        "action": "skipped_wake_point"}
    assert pe.maybe_settle_judgment_ledger(task_id="daily_kline_x", success=False) == {
        "action": "skipped_wake_point"}


def test_hook_marker_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: True)
    assert pe.maybe_settle_judgment_ledger(task_id="daily_kline_x")["action"] == "already_settled"


def test_hook_success_brief(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: False)
    touched: list[str] = []
    monkeypatch.setattr(pe, "_touch_marker", lambda key: touched.append(key))
    from zephyr.plan_engine import judgment_settler as js_mod

    def fake_settle_all(*, asof_day: str | None = None, dry_run: bool = False):
        assert asof_day == "2026-09-15"
        return {"next_day_forecast": js.SettleReport("t", 3, 2, 1, 0, 0)}

    monkeypatch.setattr(js_mod, "settle_all", fake_settle_all)
    out = pe.maybe_settle_judgment_ledger(task_id="daily_kline_x")
    assert out["action"] == "settled" and "settled=2" in out["brief"]
    assert touched == ["judgment_ledger_settle:2026-09-15"]  # marker 先落（防重扫风暴裁定）


def test_hook_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-09-15")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: False)
    monkeypatch.setattr(pe, "_touch_marker", lambda key: None)
    from zephyr.plan_engine import judgment_settler as js_mod

    def boom(*, asof_day=None, dry_run=False):
        raise RuntimeError("CH down")

    monkeypatch.setattr(js_mod, "settle_all", boom)
    out = pe.maybe_settle_judgment_ledger(task_id="daily_kline_x")
    assert out["action"] == "error" and "RuntimeError" in str(out.get("error"))
