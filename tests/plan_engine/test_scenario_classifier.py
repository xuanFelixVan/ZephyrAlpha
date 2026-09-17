# [A_test] module_id: MOD-PLAN-031 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-031 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] tests.plan_engine.test_scenario_classifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""scenario_classifier 盘中场景归类器施工验证测试（判定台账标准 v0.1 §三表3 中段）。

覆盖：
- 计划装载：payload 结构 fail-closed（坏 JSON/缺 scenarios/坏触发式/重复 id）。
- 盘中特征：同序号量比手算对账；full_day_fallback 降级；历史缺席 fail-closed。
- 重放归类：条件首穿记 hit（trigger_ts/trigger_price 对账）；**闭锁语义**（同场景
  至多一 hit——后续穿越不追加，红蓝）；**触发边界**（等值不触发严格大于——gap_band
  边界归类唯一，红蓝）；同刻多场景命中按清单序（红蓝：多场景同触发优先序确定性）。
- 归类规则边界：earliest_actual 最早 ts 优先/同刻清单序/空=no_scenario 哨兵。
- 写行契约：10 列 INSERT（schemas 真源对齐）；plan_quality_score=NULL 写 TSV 转义字面量；
  verified_by=scenario_engine:intraday:<bar_key>。
- 幂等：确定性重放对账——同 bar 集重放 no_change 零写入（红蓝：事件重放/调度器
  重复唤醒零副作用）；新 bar 到达→追加快照行；**EOD 定格行冻结**（晚到 bar 不覆盖
  定格行——最新行覆盖语义自保闸，红蓝）。
- 唤醒点：非 60min 任务/失败任务 → skipped_wake_point；无计划/无 bars → 零写入；
  坏计划 payload → skipped_invalid_plan；异常 → error 不反噬。
- 与 P1 链联测：盘中行(actual='') + EOD 行(actual=定格) 共存时结算器读**最新行**
  （_settle_daily_plan 联结语义——T3 收口后结算才成立）。
全 monkeypatch/canned 隔离，不触真 ClickHouse。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import scenario_classifier as scmod
from zephyr.plan_engine.daily_plan import NO_SCENARIO, build_v0_scenarios
from zephyr.plan_engine.scenario_classifier import (
    earliest_actual,
    latest_verification,
    maybe_classify_intraday_scenario,
    prev_session_close,
    replay_hits,
    scenarios_from_payload,
    session_feature_at,
    write_verification,
)


# ── 夹具（synthetic 60min bars——结构对齐 kline_etf_60min 行元组）──

def _bar(day: str, hhmm: str, o: float, c: float, vol: float) -> tuple:
    return (day, datetime.fromisoformat(f"{day}T{hhmm}:00+08:00"), o, c, max(o, c) * 1.001,
            min(o, c) * 0.999, vol)


def _hist_bars(days: int = 30, base: float = 4000.0, day_vols: float = 4.0e8) -> list[tuple]:
    """合成 N 日 4 根 60min bars（每日恒定价格/量——量比可手算）。"""
    from datetime import date, timedelta

    rows: list[tuple] = []
    d0 = date(2026, 8, 1)
    for i in range(days):
        d = (d0 + timedelta(days=i)).isoformat()
        per = day_vols / 4.0
        for hhmm, k in (("10:30", 0), ("11:30", 1), ("14:00", 2), ("15:00", 3)):
            rows.append(_bar(d, hhmm, base, base, per))
    return rows


def _today_bars(day: str, opens: float, closes: list[float], vols: list[float]) -> list[tuple]:
    hhmm = ("10:30", "11:30", "14:00", "15:00")
    prev_close = None
    rows = []
    for i, (hm, c) in enumerate(zip(hhmm, closes)):
        o = opens if i == 0 else rows[-1][3]
        rows.append(_bar(day, hm, o, c, vols[i]))
        prev_close = c
    return rows


SCENARIOS = build_v0_scenarios()


# ── 计划装载 fail-closed ─--


def test_scenarios_from_payload_structures() -> None:
    assert len(scenarios_from_payload({"scenarios": SCENARIOS})) == 3
    with pytest.raises(ValueError):
        scenarios_from_payload("not a dict")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        scenarios_from_payload({})
    with pytest.raises(ValueError):
        scenarios_from_payload({"scenarios": [{"scenario_id": "S1"}]})  # 缺 trigger
    with pytest.raises(ValueError):
        scenarios_from_payload({"scenarios": [
            {"scenario_id": "S1", "trigger": "open_gap_pct > 0.3 AND 拉板 > 1"}]})  # 词表外
    with pytest.raises(ValueError):
        scenarios_from_payload({"scenarios": [
            {"scenario_id": "S1", "trigger": "open_gap_pct > 0.3"},
            {"scenario_id": "S1", "trigger": "open_gap_pct < -0.3"}]})  # 重复 id


# ── 盘中特征 ─--


def test_prev_session_close() -> None:
    hist = _hist_bars(3)
    assert prev_session_close(hist) == pytest.approx(4000.0)
    assert prev_session_close([]) is None


def test_session_feature_same_index_handcheck() -> None:
    hist = _hist_bars(25, day_vols=4.0e8)  # 每根 bar 1e8
    today = _today_bars("2026-08-31", opens=4020.0, closes=[4030.0, 4025.0, 4010.0, 4005.0],
                        vols=[1.2e8, 0.8e8, 1.0e8, 1.0e8])
    # bar 0 收盘时：累计量 1.2e8 / 同序号基 1e8 = 1.2；缺口 = 4020/4000-1 = +0.5%
    f, note = session_feature_at(today, hist, 0)
    assert note == "same_index"
    assert f["open_gap_pct"] == pytest.approx(0.5)
    assert f["amount_ratio"] == pytest.approx(1.2)
    assert f["ret_intraday_pct"] == pytest.approx((4030.0 / 4000.0 - 1) * 100)
    # bar 3 收盘时：累计 4.0e8 / 同序号基（25 日均 4.0e8）= 1.0
    f3, _ = session_feature_at(today, hist, 3)
    assert f3["amount_ratio"] == pytest.approx(1.0)


def test_session_feature_full_day_fallback() -> None:
    """全部历史日仅 3 根 bars（无 15:00 收盘根）→ 同序号基不可得 → 全日均量降级。"""
    hist = [r for r in _hist_bars(25) if r[1].hour != 15]
    today = _today_bars("2026-08-31", 4000.0, [4010.0, 4005.0, 4008.0, 4006.0],
                        [1e8, 1e8, 1e8, 1e8])
    f, note = session_feature_at(today, hist, 3)
    assert note == "full_day_fallback"
    assert f["amount_ratio"] > 0


def test_session_feature_missing_history_fail_closed() -> None:
    today = _today_bars("2026-08-31", 4000.0, [4010.0], [1e8])
    with pytest.raises(ValueError):
        session_feature_at(today, [], 0)


# ── 重放归类（首穿/闭锁/边界/优先序）──--


def test_replay_first_cross_records_hit() -> None:
    hist = _hist_bars(25)
    # 高开 +0.5%（S1 缺口轴 ✓）但首根量比 1.0（amount_ratio>1.2 未满足）→ bar1 放量后 S1 触发
    # （bar1 累计 2.5e8 / 同序号基 2.0e8 = 1.25 > 1.2）
    today = _today_bars("2026-08-31", opens=4020.0, closes=[4025.0, 4030.0, 4020.0, 4015.0],
                        vols=[1.0e8, 1.5e8, 1.0e8, 1.0e8])
    hits, note = replay_hits(today, hist, SCENARIOS)
    assert note is None
    s1 = [h for h in hits if h["scenario_id"] == "S1_attack"]
    assert len(s1) == 1  # 闭锁：后续 bar 不重复记
    assert s1[0]["trigger_ts"] == "2026-08-31 11:30:00.000"  # bar1 收盘时刻（首穿）
    assert s1[0]["trigger_price"] == pytest.approx(4030.0)


def test_replay_boundary_equality_goes_to_s3() -> None:
    """红蓝：触发边界——gap=+0.3 等值不满足 S1（严格>），唯一归属 S3（≤0.3）。"""
    hist = _hist_bars(25)
    today = _today_bars("2026-08-31", opens=4012.0, closes=[4012.0, 4012.0, 4012.0, 4012.0],
                        vols=[1e8, 1e8, 1e8, 1e8])  # gap=+0.3%
    hits, _ = replay_hits(today, hist, SCENARIOS)
    assert [h["scenario_id"] for h in hits] == ["S3_oscillation"]


def test_replay_multi_match_same_bar_priority_order() -> None:
    """红蓝：同刻多场景命中 → 清单序确定性（构造低开未收复日：S2 首根即触发；
    S3 需 |gap|≤0.3 与 S2 的 gap<-0.3 轴互斥——此处验证 S2 唯一）。"""
    hist = _hist_bars(25)
    today = _today_bars("2026-08-31", opens=3980.0, closes=[3970.0, 3965.0, 3960.0, 3955.0],
                        vols=[1e8, 1e8, 1e8, 1e8])  # 低开 -0.5% 且 ret<0 → S2
    hits, _ = replay_hits(today, hist, SCENARIOS)
    assert [h["scenario_id"] for h in hits] == ["S2_defense"]
    assert hits[0]["trigger_ts"].endswith("10:30:00.000")


def test_replay_no_scenario_day() -> None:
    """高开缩量=覆盖缺口（无场景日）——hits 空，如实。"""
    hist = _hist_bars(25)
    today = _today_bars("2026-08-31", opens=4020.0, closes=[4010.0, 4008.0, 4006.0, 4005.0],
                        vols=[0.5e8, 0.5e8, 0.5e8, 0.5e8])  # 高开 +0.5% 但缩量 → S1 不触发
    hits, note = replay_hits(today, hist, SCENARIOS)
    assert hits == []
    assert earliest_actual(hits, SCENARIOS) == NO_SCENARIO


def test_earliest_actual_tie_break_by_list_order() -> None:
    hits = [
        {"scenario_id": "S2_defense", "trigger_ts": "2026-08-31 11:30:00.000", "trigger_price": 1.0},
        {"scenario_id": "S1_attack", "trigger_ts": "2026-08-31 11:30:00.000", "trigger_price": 1.0},
    ]
    assert earliest_actual(hits, SCENARIOS) == "S1_attack"  # 同刻按清单序（S1 在前）
    hits2 = [
        {"scenario_id": "S1_attack", "trigger_ts": "2026-08-31 14:00:00.000", "trigger_price": 1.0},
        {"scenario_id": "S2_defense", "trigger_ts": "2026-08-31 10:30:00.000", "trigger_price": 1.0},
    ]
    assert earliest_actual(hits2, SCENARIOS) == "S2_defense"  # 最早 trigger_ts 优先


# ── 写行契约 ─--


def test_write_verification_columns_and_null(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def _fake_write(table, columns, tsv_bytes, *a, **k):
        captured["table"] = table
        captured["columns"] = columns
        captured["row"] = tsv_bytes.decode("utf-8").strip()
        from zephyr.data.ch_writer import WriteDisposition, WriteOutcome

        return WriteOutcome(WriteDisposition.CH_COMMITTED, "canned")

    import zephyr.data.ch_writer as cw

    monkeypatch.setattr(cw, "write_tsv_outcome", _fake_write)
    ok, disp = write_verification(
        plan_judgment_id="JID1", scenario_hits="[]",
        verified_by="scenario_engine:intraday:2026-08-31T10:30",
        verified_at=datetime(2026, 8, 31, 3, 0, tzinfo=timezone.utc))
    assert ok is True and disp == "ch_committed"
    from schemas.categories.judgment.judgment_plan_verification import INSERT_COLUMNS

    assert captured["columns"] == INSERT_COLUMNS
    fields = captured["row"].split("\t")
    assert len(fields) == 10
    assert fields[1] == "JID1" and fields[2] == "[]" and fields[3] == ""
    assert fields[4] == "0" and fields[5] == "[]"
    assert fields[6] == "\\N"  # plan_quality_score NULL（盘中行不越权打分）
    assert fields[8] == "scenario_engine:intraday:2026-08-31T10:30"
    assert fields[9] == "0"  # synthetic


def test_write_verification_requires_join_key() -> None:
    with pytest.raises(ValueError):
        write_verification(plan_judgment_id="", scenario_hits="[]", verified_by="x",
                           verified_at=datetime(2026, 8, 31, tzinfo=timezone.utc))


# ── 钩子（幂等/唤醒点/冻结）──--


def _plan_row(day: str, jid: str = "JID-PLAN-1") -> list[tuple]:
    payload = json.dumps({"scenarios": SCENARIOS}, ensure_ascii=False)
    return [(jid, payload, f"{day} 07:05:00.000", f"plan_date:{day}|inputs_hash:x|")]


def _canned(monkeypatch, *, plan_rows, kline_max, bars, last_ver=None, write_capture=None):
    """有状态 canned：write_verification 的行回灌 ver_store（模拟 CH 累积——重放对账可测）。"""
    ver_store: list[tuple] = list(last_ver or [])

    def _rd(sql: str) -> list[tuple]:
        if "judgment_daily_plan" in sql:
            return plan_rows
        if "max(trade_date)" in sql:
            return [(kline_max,)] if kline_max else [(None,)]
        if "kline_etf_60min" in sql:
            return bars
        if "judgment_plan_verification" in sql and "count()" not in sql:
            return [ver_store[-1]] if ver_store else []
        return []

    monkeypatch.setattr(scmod, "_reader_execute", _rd)
    if write_capture is not None:
        def _fake_write(table, columns, tsv_bytes, *a, **k):
            fields = tsv_bytes.decode("utf-8").strip().split("\t")
            # (scenario_hits, actual, verified_by, verified_at)——回灌累积状态
            ver_store.append((fields[2], fields[3], fields[8], fields[7]))
            write_capture.append((table, tsv_bytes.decode("utf-8").strip()))
            from zephyr.data.ch_writer import WriteDisposition, WriteOutcome

            return WriteOutcome(WriteDisposition.CH_COMMITTED, "canned")

        import zephyr.data.ch_writer as cw

        monkeypatch.setattr(cw, "write_tsv_outcome", _fake_write)


def _freeze_now(monkeypatch, day: str) -> None:
    monkeypatch.setattr(scmod, "now_utc",
                        lambda: datetime.fromisoformat(f"{day}T02:00:00+00:00"))


def test_hook_wake_filter_and_no_plan(monkeypatch) -> None:
    assert maybe_classify_intraday_scenario(task_id="daily_kline")["action"] == "skipped_wake_point"
    assert maybe_classify_intraday_scenario(task_id="kline_60min", success=False)["action"] == "skipped_wake_point"
    _freeze_now(monkeypatch, "2026-08-31")
    _canned(monkeypatch, plan_rows=[], kline_max="2026-08-28", bars=[])
    assert maybe_classify_intraday_scenario(task_id="kline_60min")["action"] == "no_plan"


def test_hook_no_bars_zero_write(monkeypatch) -> None:
    _freeze_now(monkeypatch, "2026-08-31")
    _canned(monkeypatch, plan_rows=_plan_row("2026-08-28"), kline_max="2026-08-28", bars=[])
    assert maybe_classify_intraday_scenario(task_id="kline_etf_60min")["action"] == "no_bars"


def test_hook_appends_and_dedups_replay(monkeypatch) -> None:
    """红蓝：确定性重放对账——首次追加；同 bar 集重放 no_change（事件重放零副作用）。"""
    writes: list[tuple] = []
    hist = _hist_bars(25)
    # bar1 收盘时：累计 2.5e8 / 同序号基 2.0e8 = 1.25 > 1.2 → S1 首穿于 11:30 bar
    today = _today_bars("2026-08-31", opens=4020.0, closes=[4025.0, 4030.0, 4020.0, 4015.0],
                        vols=[1.0e8, 1.5e8, 1.0e8, 1.0e8])
    _freeze_now(monkeypatch, "2026-08-31")
    _canned(monkeypatch, plan_rows=_plan_row("2026-08-28"), kline_max="2026-08-28",
            bars=hist + today, write_capture=writes)
    out = maybe_classify_intraday_scenario(task_id="kline_etf_60min_incremental")
    assert out["action"] == "appended" and out["n_hits"] == 1
    assert len(writes) == 1
    # 同 bar 集重放（调度器 5 分钟重复唤醒）：hit 集一致 → no_change 零写入
    out2 = maybe_classify_intraday_scenario(task_id="kline_etf_60min_incremental")
    assert out2["action"] == "no_change"
    assert len(writes) == 1


def test_hook_new_bar_appends_snapshot(monkeypatch) -> None:
    """新 bar 到达且 hit 集变化 → 追加快照行（累积 hit 集）。"""
    writes: list[tuple] = []
    hist = _hist_bars(25)
    today = _today_bars("2026-08-31", opens=3980.0, closes=[3970.0], vols=[1e8])  # 首根即 S2
    _freeze_now(monkeypatch, "2026-08-31")
    _canned(monkeypatch, plan_rows=_plan_row("2026-08-28"), kline_max="2026-08-28",
            bars=hist + today, write_capture=writes)
    out = maybe_classify_intraday_scenario(task_id="kline_etf_60min")
    assert out["action"] == "appended"
    row = json.loads(writes[0][1].split("\t")[2])
    assert row[0]["scenario_id"] == "S2_defense"


def test_hook_frozen_by_eod_red_blue(monkeypatch) -> None:
    """红蓝：EOD 定格行已存在 → 盘中冻结（晚到 bar 不得以 actual='' 覆盖定格行）。"""
    writes: list[tuple] = []
    hist = _hist_bars(25)
    today = _today_bars("2026-08-31", opens=3980.0, closes=[3970.0], vols=[1e8])
    _freeze_now(monkeypatch, "2026-08-31")
    _canned(monkeypatch, plan_rows=_plan_row("2026-08-28"), kline_max="2026-08-28",
            bars=hist + today, last_ver=[("[]", "S2_defense", "close_verifier:v0:bars_replay",
                                          "2026-08-31 08:00:00.000")],
            write_capture=writes)
    out = maybe_classify_intraday_scenario(task_id="kline_etf_60min")
    assert out["action"] == "frozen_by_eod"
    assert writes == []


def test_hook_bad_plan_payload_fail_closed(monkeypatch) -> None:
    _freeze_now(monkeypatch, "2026-08-31")
    bad = [( "JID-BAD", json.dumps({"scenarios": [{"scenario_id": "S1"}]}),
             "2026-08-28 07:05:00.000", "plan_date:2026-08-28|x|")]
    _canned(monkeypatch, plan_rows=bad, kline_max="2026-08-28", bars=[])
    out = maybe_classify_intraday_scenario(task_id="kline_etf_60min")
    assert out["action"] == "skipped_invalid_plan"


def test_hook_error_swallowed(monkeypatch) -> None:
    def _boom(*a, **k):
        raise RuntimeError("ch down")

    monkeypatch.setattr(scmod, "_reader_execute", _boom)
    out = maybe_classify_intraday_scenario(task_id="kline_etf_60min")
    assert out["action"] == "error"


def test_latest_verification_latest_row_wins(monkeypatch) -> None:
    """与 P1 结算器联结语义联测：盘中行(actual='') + EOD 行 → 最新行=EOD（actual 定格）。"""
    rows = [
        ("[]", "", "scenario_engine:intraday:2026-08-31T10:30", "2026-08-31 03:00:00.000"),
        (json.dumps([{"scenario_id": "S2_defense", "trigger_ts": "2026-08-31 10:30:00.000",
                      "trigger_price": 3970.0}]), "S2_defense",
         "close_verifier:v0:bars_replay", "2026-08-31 08:05:00.000"),
    ]
    _canned(monkeypatch, plan_rows=[], kline_max="", bars=[], last_ver=rows)
    last = latest_verification("JID1")
    assert last["actual_scenario_id"] == "S2_defense"
    # 结算器同取法（ORDER BY verified_at DESC）：联结最新行 → settled 而非 unresolvable
    from zephyr.plan_engine import judgment_settler as js
    from zephyr.plan_engine.daily_plan import build_v0_scenarios as _bv

    scs = _bv()
    for i, s in enumerate(scs):
        s["path_prior"] = [0.2, 0.5, 0.3][i]
    payload = {"scenarios": scs}
    ver = {"actual_scenario_id": last["actual_scenario_id"], "plan_followed": 0,
           "scenario_hits": last["scenario_hits"]}
    row = {"judgment_id": "JID1", "module_id": "m", "model_version": "v",
           "asof_ts": "2026-08-28 07:05:00.000", "subject": "index:000300.SH",
           "payload": json.dumps(payload), "confidence": 0.5}
    bf, res, _perm = js._settle_daily_plan(row, {"JID1": ver}, "2026-08-31")
    assert res.action == "settled" and bf["actual_scenario_id"] == "S2_defense"
    assert bf["scenario_brier"] == pytest.approx((0.2 - 0) ** 2 + (0.5 - 1) ** 2 + 0.3 ** 2)
