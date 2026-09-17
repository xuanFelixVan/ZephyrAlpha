# [A_test] module_id: MOD-PLAN-032 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-032 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] tests.plan_engine.test_close_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""close_verifier 收盘验证器施工验证测试（判定台账标准 v0.1 §三表3 下半）。

覆盖：
- actual 归类规则边界：hits 非空=最早 trigger_ts；hits 空+日线 EOD 兜底命中
  （eod_daily_proxy 模式）；全不中=no_scenario 哨兵（红蓝：无场景日如实记账）；
  EOD 特征缺席=不可兜底。
- plan_quality_score 口径：prior 似然取值对账；actual 不在分支集（含哨兵）=0.0；
  越界 clamp。
- EOD 定格全链：计划装载→bars 重放→EOD 行追加（10 列/actual/score/verified_by 对账）；
  幂等（EOD 行已存在→already_verified 零写入，红蓝：事件重放）；无计划=no_plan；
  60min bars 缺席→日线兜底模式标注；T+1 日线缺席→data_insufficient 不写行
  （P1 宽限期惯例：结算器 unresolvable 链兜底，红蓝）。
- 唤醒点：非 daily 任务/失败任务→skipped_wake_point；异常→error 不反噬。
- 与 P1 发射器-结算器**全链联测**：canned CH 发射预案行（真 emit_judgment 12 列）→
  收盘验证 EOD 行（真 write_verification）→ 行内容回灌 judgment_settler._settle_
  daily_plan → scenario_brier/actual_scenario_id/hit 对账（发射-验证-结算三段闭环）。
全 monkeypatch/canned 隔离，不触真 ClickHouse（真库冒烟走 synthetic=1 标注+清理通道）。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import close_verifier as cv
from zephyr.plan_engine import daily_plan as dp
from zephyr.plan_engine import scenario_classifier as scmod
from zephyr.plan_engine.close_verifier import (
    classify_actual,
    maybe_verify_plan_close,
    prev_business_day,
    quality_score_of,
    verify_for_session,
)
from zephyr.plan_engine.daily_plan import NO_SCENARIO, build_v0_scenarios


# ── 夹具 ─--

def _bar(day: str, hhmm: str, o: float, c: float, vol: float) -> tuple:
    return (day, datetime.fromisoformat(f"{day}T{hhmm}:00+08:00"), o, c, max(o, c) * 1.001,
            min(o, c) * 0.999, vol)


def _hist_bars(days: int = 25, base: float = 4000.0) -> list[tuple]:
    from datetime import date, timedelta

    rows: list[tuple] = []
    d0 = date(2026, 8, 1)
    for i in range(days):
        d = (d0 + timedelta(days=i)).isoformat()
        for hhmm in ("10:30", "11:30", "14:00", "15:00"):
            rows.append(_bar(d, hhmm, base, base, 1.0e8))
    return rows


def _kline_rows() -> list[tuple]:
    """指数日线（末两日构造：G=2026-08-28 平开收平；D=2026-08-31 低开未收复→S2）。"""
    rows: list[tuple] = []
    px = 4000.0
    for i in range(40):
        rows.append((f"2026-07-{i + 1:02d}" if i < 20 else f"2026-08-{i - 19:02d}",
                     px, px * 1.002, px * 0.998, px, 1.0e8))
    rows.append(("2026-08-28", 4000.0, 4008.0, 3992.0, 4000.0, 1.0e8))  # G 日：平开平收
    rows.append(("2026-08-31", 3980.0, 3985.0, 3950.0, 3960.0, 0.6e8))  # D 日：低开 -0.5% 未收复
    return rows


SCENARIOS = build_v0_scenarios()


def _canned(monkeypatch, *, plan_rows, kline_rows, bars, ver_store, write_capture,
            prev_day="2026-08-28"):
    def _rd(sql: str) -> list[tuple]:
        if "judgment_daily_plan" in sql:
            return plan_rows
        if "max(trade_date)" in sql:
            return [(prev_day,)]
        if "kline_etf_60min" in sql:
            return bars
        if "kline_index" in sql:
            return kline_rows
        if "judgment_plan_verification" in sql and "count()" in sql:
            eod = [v for v in ver_store if "close_verifier" in v[2]]
            return [(len(eod),)]
        if "judgment_plan_verification" in sql:
            return [ver_store[-1]] if ver_store else []
        return []

    monkeypatch.setattr(cv, "_reader_execute", _rd)

    def _fake_write(table, columns, tsv_bytes, *a, **k):
        fields = tsv_bytes.decode("utf-8").strip().split("\t")
        ver_store.append((fields[2], fields[3], fields[8], fields[7]))
        write_capture.append((table, columns, fields))
        from zephyr.data.ch_writer import WriteDisposition, WriteOutcome

        return WriteOutcome(WriteDisposition.CH_COMMITTED, "canned")

    import zephyr.data.ch_writer as cw

    monkeypatch.setattr(cw, "write_tsv_outcome", _fake_write)


# ── actual 归类规则边界 ─--


def test_classify_actual_earliest_hit_wins() -> None:
    hits = [
        {"scenario_id": "S3_oscillation", "trigger_ts": "2026-08-31 10:30:00.000", "trigger_price": 1.0},
        {"scenario_id": "S1_attack", "trigger_ts": "2026-08-31 11:30:00.000", "trigger_price": 1.0},
    ]
    actual, mode = classify_actual(SCENARIOS, hits, {"open_gap_pct": 0.0})
    assert actual == "S3_oscillation" and mode == "intraday_hits"


def test_classify_actual_eod_fallback_red_blue() -> None:
    """红蓝：盘中分钟源缺席 → 日线 EOD 特征兜底归类（模式如实标注）。"""
    eod = {"open_gap_pct": -0.5, "amount_ratio": 0.9, "ret_intraday_pct": -1.0}
    actual, mode = classify_actual(SCENARIOS, [], eod)
    assert actual == "S2_defense" and mode == "eod_daily_proxy"


def test_classify_actual_no_scenario_day_red_blue() -> None:
    """红蓝：全场景不触发=无场景日 → no_scenario 哨兵如实记账（禁硬凑归属）。"""
    eod = {"open_gap_pct": 0.5, "amount_ratio": 0.7, "ret_intraday_pct": 0.0}  # 高开缩量
    actual, mode = classify_actual(SCENARIOS, [], eod)
    assert actual == NO_SCENARIO and mode == "no_scenario"


def test_classify_actual_no_eod_features() -> None:
    actual, mode = classify_actual(SCENARIOS, [], None)
    assert actual == NO_SCENARIO and mode == "no_scenario"


# ── plan_quality_score 口径 ─--


def test_quality_score_prior_likelihood() -> None:
    scs = [
        {"scenario_id": "S1_attack", "path_prior": 0.5},
        {"scenario_id": "S2_defense", "path_prior": 0.3},
        {"scenario_id": "S3_oscillation", "path_prior": 0.2},
    ]
    assert quality_score_of(scs, "S2_defense") == pytest.approx(0.3)
    assert quality_score_of(scs, "S1_attack") == pytest.approx(0.5)  # argmax 命中=最高 prior
    assert quality_score_of(scs, NO_SCENARIO) == 0.0  # 哨兵不在分支集=0（不编造中性分）
    assert quality_score_of(scs, "unknown") == 0.0
    assert quality_score_of([{"scenario_id": "S1", "path_prior": 9.9}], "S1") == 1.0  # clamp


# ── 业务日 ─--


def test_prev_business_day(monkeypatch) -> None:
    monkeypatch.setattr(cv, "_reader_execute", lambda sql: [("2026-08-28",)])
    assert prev_business_day("2026-08-31") == "2026-08-28"
    monkeypatch.setattr(cv, "_reader_execute", lambda sql: [(None,)])
    assert prev_business_day("2026-08-31") is None


# ── EOD 定格全链 ─--


def _plan_rows(g_day: str, jid: str = "JID-PLAN-9") -> list[tuple]:
    payload = json.dumps({"scenarios": SCENARIOS}, ensure_ascii=False)
    return [(jid, payload, f"{g_day} 07:05:00.000", f"plan_date:{g_day}|inputs_hash:x|")]


def test_verify_full_chain_bars_replay(monkeypatch) -> None:
    """bars 在场：S2 首根触发（低开未收复）→ actual=S2，score=prior(S2)。"""
    writes: list[tuple] = []
    ver_store: list[tuple] = []
    hist = _hist_bars()
    today = [_bar("2026-08-31", "10:30", 3980.0, 3970.0, 1.0e8),
             _bar("2026-08-31", "11:30", 3970.0, 3965.0, 1.0e8)]
    _canned(monkeypatch, plan_rows=_plan_rows("2026-08-28"), kline_rows=_kline_rows(),
            bars=hist + today, ver_store=ver_store, write_capture=writes)
    out = verify_for_session("2026-08-31")
    assert out["action"] == "verified"
    assert out["actual_scenario_id"] == "S2_defense"
    assert out["mode"] == "intraday_hits"
    fields = writes[0][2]
    assert len(fields) == 10
    assert fields[3] == "S2_defense"
    assert fields[4] == "0"  # plan_followed v0 预留（编排器执行链未接电）
    hits = json.loads(fields[2])
    assert hits[0]["scenario_id"] == "S2_defense"
    assert hits[0]["trigger_ts"] == "2026-08-31 10:30:00.000"
    # verified_by 模式标注
    assert fields[8].startswith("close_verifier:v0:bars_replay")


def test_verify_idempotent_eod_row(monkeypatch) -> None:
    """红蓝：EOD 定格行已存在 → already_verified 零写入（重复唤醒零副作用）。"""
    writes: list[tuple] = []
    ver_store: list[tuple] = [("[]", "S2_defense", "close_verifier:v0:bars_replay",
                               "2026-08-31 08:05:00.000")]
    hist = _hist_bars()
    today = [_bar("2026-08-31", "10:30", 3980.0, 3970.0, 1.0e8)]
    _canned(monkeypatch, plan_rows=_plan_rows("2026-08-28"), kline_rows=_kline_rows(),
            bars=hist + today, ver_store=ver_store, write_capture=writes)
    out = verify_for_session("2026-08-31")
    assert out["action"] == "already_verified"
    assert writes == []


def test_verify_no_60min_bars_eod_proxy(monkeypatch) -> None:
    """60min 缺席 → 日线 EOD 兜底模式（verified_by 标注；hits=空数组如实）。"""
    writes: list[tuple] = []
    _canned(monkeypatch, plan_rows=_plan_rows("2026-08-28"), kline_rows=_kline_rows(),
            bars=[], ver_store=[], write_capture=writes)
    out = verify_for_session("2026-08-31")
    assert out["action"] == "verified"
    assert out["mode"] == "eod_daily_proxy"
    assert out["actual_scenario_id"] == "S2_defense"
    fields = writes[0][2]
    assert json.loads(fields[2]) == []  # 盘中 hits 空（无分钟源，不伪造盘中触发）
    assert ":eod_daily_proxy" in fields[8]


def test_verify_no_plan(monkeypatch) -> None:
    _canned(monkeypatch, plan_rows=[], kline_rows=_kline_rows(), bars=[], ver_store=[],
            write_capture=[])
    assert verify_for_session("2026-08-31")["action"] == "no_plan"


def test_verify_missing_daily_fail_closed_red_blue(monkeypatch) -> None:
    """红蓝：T+1 日线缺席 → data_insufficient 不写行（P1 宽限链兜底 unresolvable）。"""
    rows = [r for r in _kline_rows() if str(r[0]) < "2026-08-31"]
    _canned(monkeypatch, plan_rows=_plan_rows("2026-08-28"), kline_rows=rows, bars=[],
            ver_store=[], write_capture=[])
    with pytest.raises(ValueError, match="不在库"):
        verify_for_session("2026-08-31")


def test_hook_wake_filter_and_grace(monkeypatch) -> None:
    assert maybe_verify_plan_close(task_id="kline_60min")["action"] == "skipped_wake_point"
    assert maybe_verify_plan_close(task_id="daily_kline", success=False)["action"] == "skipped_wake_point"


def test_hook_error_swallowed(monkeypatch) -> None:
    def _boom(*a, **k):
        raise RuntimeError("ch down")

    monkeypatch.setattr(cv, "_reader_execute", _boom)
    out = maybe_verify_plan_close(task_id="daily_kline_incremental")
    assert out["action"] in ("error", "data_insufficient")


# ── 与 P1 发射-结算全链联测（synthetic 标注语义，canned 隔离）──--


def test_e2e_emit_verify_settle_joint(monkeypatch) -> None:
    """发射（真 emit_judgment）→ 收盘验证（真 write_verification）→ 结算
    （真 _settle_daily_plan）三段闭环：brier/actual/hit 全对账。"""
    from zephyr.plan_engine import judgment_settler as js

    cap_rows: list[list[str]] = []

    def _fake_write(table, columns, tsv_bytes, *a, **k):
        from zephyr.data.ch_writer import WriteDisposition, WriteOutcome

        for line in tsv_bytes.decode("utf-8").strip().split("\n"):
            cap_rows.append(line.split("\t"))
        return WriteOutcome(WriteDisposition.CH_COMMITTED, "canned")

    import zephyr.data.ch_writer as cw

    monkeypatch.setattr(cw, "write_tsv_outcome", _fake_write)
    # ① 发射预案（G 日收盘，真 emit_judgment 12 列契约）
    rows = _kline_rows()

    def _rd1(sql: str) -> list[tuple]:
        if "kline_index" in sql:
            return rows
        if "count()" in sql:
            return [(0,)]
        return []

    g_day = "2026-08-28"
    res = dp.emit_for_trade_date(g_day, reader=_rd1,
                                 asof_ts=datetime(2026, 8, 28, 7, 5, tzinfo=timezone.utc))
    assert res.committed
    plan_fields = cap_rows[0]
    assert len(plan_fields) == 12
    plan_payload = json.loads(plan_fields[7])
    judgment_id = plan_fields[0]
    priors = {s["scenario_id"]: s["path_prior"] for s in plan_payload["scenarios"]}
    # ② 收盘验证（D 日，60min 缺席=日线 EOD 兜底模式）
    def _rd2(sql: str) -> list[tuple]:
        if "judgment_daily_plan" in sql:
            return [(judgment_id, plan_fields[7], "2026-08-28 07:05:00.000", plan_fields[10])]
        if "max(trade_date)" in sql:
            return [("2026-08-28",)]
        if "kline_index" in sql:
            return rows
        if "judgment_plan_verification" in sql and "count()" in sql:
            return [(0,)]
        return []

    monkeypatch.setattr(cv, "_reader_execute", _rd2)
    out = verify_for_session("2026-08-31")
    assert out["action"] == "verified"
    assert out["actual_scenario_id"] == "S2_defense"
    ver_fields = cap_rows[1]
    assert len(ver_fields) == 10  # 真验证行 10 列契约
    # ③ 结算（真 settler 纯函数联结 EOD 行）
    ver = {
        "actual_scenario_id": ver_fields[3],
        "plan_followed": int(ver_fields[4]),
        "scenario_hits": ver_fields[2],
    }
    row = {"judgment_id": judgment_id, "module_id": plan_fields[1],
           "model_version": plan_fields[2], "asof_ts": "2026-08-28 07:05:00.000",
           "subject": plan_fields[6], "payload": plan_fields[7],
           "confidence": float(plan_fields[8])}
    bf, settle_res, _perm = js._settle_daily_plan(row, {judgment_id: ver}, "2026-08-31")
    assert settle_res.action == "settled"
    assert bf["actual_scenario_id"] == "S2_defense"
    # brier 手算：one-hot(S2)，prior 三元（发射行实际值）
    p = [priors["S1_attack"], priors["S2_defense"], priors["S3_oscillation"]]
    expect = (p[0] - 0.0) ** 2 + (p[1] - 1.0) ** 2 + (p[2] - 0.0) ** 2
    assert bf["scenario_brier"] == pytest.approx(expect)
    assert json.loads(bf["outcome_value"])["n_hits"] == 0  # eod 代理路径 hits 空
    assert json.loads(bf["outcome_value"])["plan_followed"] is False
