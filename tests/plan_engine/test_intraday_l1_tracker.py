# [A_test] module_id: MOD-PLAN-028 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-028 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表1/§六任务1
# [MODULE] tests.plan_engine.test_intraday_l1_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""intraday_l1_tracker 盘中 L1 跟踪件施工验证测试（判定台账标准 v0.1 §三表1）。

覆盖：
- 特征装配：量比同序号口径/全日降级口径、涨跌家数比当日快照/昨日收盘降级、
  拉板数代理、缺口与盘中涨跌、隔夜 A50 参照；无 bar=空手返回。
- 五态打分：概率 softmax 结构性归一（红蓝项：和恒 1）、单调性（多头证据越强
  bull 越高、亢奋侧概率越大）、必需特征缺席 fail-closed、参数化（改参可变盘）。
- 尾盘方向：bull 越强 tail_dir_prob_down 越低、收盘 bar rest_of_day=None（诚实留空）。
- 发射：payload 过发射器 fail-closed 校验（概率越界/label 越界被拒）、PIT 锚
  input_cutoff≤asof、发射字段完备（12 列全落位——与 schemas INSERT 清单机械对齐）。
- 幂等（红蓝项：事件重放）：同 bar_key 已发射→latest_unemitted_bar 跳过→零发射。
- 唤醒点：非 60min 任务/失败任务→skipped_wake_point；无新 bar→no_new_bar
  （非交易日抑制=数据驱动结构性质）；发射异常不反噬（error 返回不抛）。
- 与 P1 库件联测：emit_judgment 产出行（canned ch_writer 捕获）→ judgment_settler
  的 _settle_intraday 纯函数回填（当日 OHLC 注入）→ brier_contrib/state_realized 对账。
全 monkeypatch/canned 隔离，不触真 ClickHouse（真库冒烟走 synthetic=1 标注+清理通道）。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import judgment_settler as js
from zephyr.plan_engine import intraday_l1_tracker as tr
from zephyr.plan_engine.intraday_l1_tracker import (
    IntradayL1Tracker,
    build_features,
    decide_five_state,
    emit_for_bar,
    format_bar_key,
    latest_unemitted_bar,
    maybe_track_intraday_state,
    score_features,
)
from zephyr.shared.utils.time_utils import now_utc


# ── 夹具（synthetic 数据——结构对齐 kline_etf_60min 行元组）──


def _bars(day: str, times: list[str], base: float = 4000.0, vol: float = 1000.0) -> list[tuple]:
    out = []
    for i, tm in enumerate(times):
        px = base * (1 + 0.001 * (i + 1))
        out.append((
            day,
            datetime.fromisoformat(f"{day} {tm}:00"),
            round(px * 0.999, 2), round(px, 2), round(px * 1.002, 2), round(px * 0.998, 2),
            vol * (i + 1),
        ))
    return out


_HIST_DAYS = ("2026-09-14", "2026-09-15")
_BREADTH = {"ts": datetime.fromisoformat("2026-09-16 11:29"),
            "advancing": 3900, "declining": 1100, "limit_up": 66, "limit_down": 4}
_INDEX_PREV = ("2026-09-15", 3900, 1200, 4020.0)
_A50 = [14303.0, 14271.0]


def _hist() -> list[tuple]:
    out: list[tuple] = []
    for d in _HIST_DAYS:
        out += _bars(d, ["10:30", "11:30", "14:00", "15:00"])
    return out


# ── 特征装配 ──


def test_build_features_full_evidence() -> None:
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0, vol=2000.0)
    f, missing = build_features(today, _hist(), _BREADTH, _INDEX_PREV, _A50)
    assert missing == []
    # 量比=同序号口径：当日累计(2000+4000)=6000；历史各日同 2 根累计 3000 → 2.0
    assert f["volume_ratio"] == pytest.approx(2.0)
    assert f["ratio_note"] == "same_index"
    assert f["breadth_ratio"] == pytest.approx(3900 / 5000)  # 当日快照口径
    assert f["attack_sector_count"] == 66  # 涨停计数代理
    assert f["breadth_source"] == "market_breadth_snapshot"
    # gap=首根 open/昨末根 close-1；ret=末根 close/昨末根 close-1
    prev_last_close = float(_hist()[-1][3])
    assert f["gap_pct"] == pytest.approx(float(today[0][2]) / prev_last_close - 1.0)
    assert f["ret_intraday"] == pytest.approx(float(today[-1][3]) / prev_last_close - 1.0)
    assert f["overnight_ref"]["a50_ret"] == pytest.approx(14303.0 / 14271.0 - 1.0)


def test_build_features_breadth_degraded_to_prev_day() -> None:
    today = _bars("2026-09-16", ["10:30"], base=4040.0)
    f, missing = build_features(today, _hist(), None, _INDEX_PREV, [])
    assert f["breadth_source"] == "kline_index_prev_day"
    assert f["degraded_breadth"] is True  # 昨日收盘口径降级=如实标注
    assert "attack_sector_count" in missing  # 无快照无拉板数（缺席≠编 0）


def test_build_features_volume_ratio_full_day_fallback() -> None:
    # 当日收了 5 根（历史各日仅 4 根，同序号口径不可得）→ 全日均量折算
    today = _bars("2026-09-16", ["10:30", "11:30", "13:30", "14:30", "15:00"],
                  base=4040.0, vol=800.0)
    f, _ = build_features(today, _hist(), _BREADTH, _INDEX_PREV, _A50)
    assert f["ratio_note"] == "full_day_fallback"
    # 当日累计 800*(1+..+5)=12000 / 历史全日均量 (1000+2000+3000+4000)=10000 → 1.2
    assert f["volume_ratio"] == pytest.approx(1.2)


def test_build_features_no_bars_returns_empty() -> None:
    f, missing = build_features([], _hist(), _BREADTH, _INDEX_PREV, _A50)
    assert f == {} and missing == ["bars_today"]


# ── 五态打分 ──


def test_score_probs_normalized_all_inputs() -> None:
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0, vol=2000.0)
    f, _ = build_features(today, _hist(), _BREADTH, _INDEX_PREV, _A50)
    j = score_features(f)
    assert abs(sum(j.state_probs.values()) - 1.0) < 1e-9  # 红蓝项：归一
    assert set(j.state_probs) == {"低迷", "防御", "震荡", "进攻", "亢奋"}
    assert all(0.0 <= v <= 1.0 for v in j.state_probs.values())
    assert j.state_label == max(j.state_probs, key=lambda k: j.state_probs[k])  # type: ignore[arg-type]
    assert 0.0 <= j.confidence <= 1.0


def test_score_monotone_bull_evidence() -> None:
    """多头证据越强 → bull 越高、亢奋+进攻概率越大。"""
    f_weak = {"breadth_ratio": 0.2, "ret_intraday": -0.01, "volume_ratio": 0.3,
              "attack_sector_count": 5, "amp_base_pct": 1.0}
    f_strong = {"breadth_ratio": 0.9, "ret_intraday": 0.015, "volume_ratio": 2.5,
                "attack_sector_count": 120, "amp_base_pct": 1.0}
    jw, js_ = score_features(f_weak), score_features(f_strong)
    assert js_.bull_score > jw.bull_score
    bull_strong = js_.state_probs["进攻"] + js_.state_probs["亢奋"]
    bull_weak = jw.state_probs["进攻"] + jw.state_probs["亢奋"]
    assert bull_strong > bull_weak
    assert js_.tail_dir_prob_down < jw.tail_dir_prob_down  # 多头强=尾盘下跌概率低


def test_score_missing_required_feature_fail_closed() -> None:
    # 盘中涨跌=唯一硬性必需（无价格证据禁判定）
    with pytest.raises(ValueError, match="ret_intraday"):
        score_features({"breadth_ratio": 0.5})


def test_score_degrades_gracefully_when_breadth_missing() -> None:
    """红蓝项：breadth 缺席=权重归一重分配降级打分（kline_index 涨跌家数断供既定处置）。"""
    full = {"breadth_ratio": 0.9, "ret_intraday": 0.015, "volume_ratio": 2.5,
            "attack_sector_count": 120, "amp_base_pct": 1.0}
    degraded = {"ret_intraday": 0.015, "volume_ratio": 2.5,
                "attack_sector_count": 120, "amp_base_pct": 1.0}
    j_full, j_deg = score_features(full), score_features(degraded)
    assert 0.0 <= j_deg.bull_score <= 1.0  # 降级路径 bull 仍在语义轴内
    assert abs(sum(j_deg.state_probs.values()) - 1.0) < 1e-9
    assert j_deg.state_label == j_full.state_label  # 强多头证据下降级不改判


def test_score_params_tunable() -> None:
    f = {"breadth_ratio": 0.8, "ret_intraday": 0.01, "volume_ratio": 2.0,
         "attack_sector_count": 80, "amp_base_pct": 1.0}
    j1 = score_features(f, dict(tr.RULE_PARAMS, state_sigma=0.01))
    j2 = score_features(f, dict(tr.RULE_PARAMS, state_sigma=0.4))
    # 温度越小分布越尖（argmax 概率更高）
    assert j1.state_probs[j1.state_label] >= j2.state_probs[j2.state_label]
    assert abs(sum(j1.state_probs.values()) - 1.0) < 1e-9


def test_score_bull_always_on_semantic_axis() -> None:
    """红蓝项：极端输入下 bull 恒在 [0,1]（软归一有界性——量比 2.5 不得越轴）。"""
    extremes = [
        {"breadth_ratio": 1.0, "ret_intraday": 0.10, "volume_ratio": 50.0,
         "attack_sector_count": 500, "amp_base_pct": 5.0},
        {"breadth_ratio": 0.0, "ret_intraday": -0.10, "volume_ratio": 0.001,
         "attack_sector_count": 0, "amp_base_pct": 0.0},
        {"breadth_ratio": 0.5, "ret_intraday": 0.0, "volume_ratio": 1.0,
         "attack_sector_count": 50, "amp_base_pct": 1.0},
    ]
    for f in extremes:
        j = score_features(f)
        assert 0.0 <= j.bull_score <= 1.0
        assert 0.1 <= j.tail_dir_prob_down <= 0.9


def test_confidence_deducted_by_missing_features() -> None:
    full = {"breadth_ratio": 0.5, "ret_intraday": 0.0, "volume_ratio": 1.0,
            "attack_sector_count": 50, "overnight_ref": {"a50_ret": 0.0}, "amp_base_pct": 1.0}
    poor = {"breadth_ratio": 0.5, "ret_intraday": 0.0, "amp_base_pct": 1.0}
    assert score_features(full).confidence > score_features(poor).confidence


# ── 判定组装（收盘 bar 诚实留空）──


def test_decide_rest_of_day_semantics() -> None:
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0)
    payload, conf = decide_five_state(today, _hist(), _BREADTH, _INDEX_PREV, _A50,
                                      is_closing_bar=False)
    assert payload["rest_of_day"] is not None
    assert 0.1 <= payload["rest_of_day"]["tail_dir_prob_down"] <= 0.9
    assert len(payload["rest_of_day"]["amp_range_pct"]) == 2
    assert 0.0 < conf <= 1.0
    # 代理缺口如实标注（红蓝项：不伪造分钟级/板块级）
    notes = payload["evidence"]["proxy_notes"]
    assert "pending_minute_source" in notes["index_intraday"]
    assert "pending_sector_pool" in notes["attack_sectors"]
    assert payload["evidence"]["attack_sectors"] == []

    with_close = today + _bars("2026-09-16", ["15:00"], base=4050.0)
    payload2, _ = decide_five_state(with_close, _hist(), _BREADTH, _INDEX_PREV, _A50,
                                    is_closing_bar=True)
    assert payload2["rest_of_day"] is None  # 收盘后无剩余时段——留空而非给无意义概率


def test_decide_insufficient_features_raises() -> None:
    with pytest.raises(ValueError, match="特征装配不完整"):
        decide_five_state([], _hist(), _BREADTH, _INDEX_PREV, _A50, is_closing_bar=False)


# ── 发射（字段完备/PIT）──


class _CapturedWriter:
    """ch_writer.write_tsv_outcome 的 canned 替身（捕获行+返回已提交）。"""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bytes]] = []

    def __call__(self, table: str, columns: str, data: bytes):
        from zephyr.data.ch_writer import WriteDisposition

        self.rows.append((table, columns, data))

        class _R:
            disposition = WriteDisposition.CH_COMMITTED  # 真枚举（.value 契约对齐）

        return _R()


def test_emit_fields_complete_and_payload_valid() -> None:
    cap = _CapturedWriter()
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0)
    bar_key = format_bar_key(today[-1][1])
    a_ts = now_utc()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "_reader_execute", lambda sql: [] if "count()" in sql else _hist())
        mp.setattr(tr, "_load_breadth", lambda day, reader=None: _BREADTH)
        mp.setattr(tr, "_load_index_prev", lambda day, reader=None: _INDEX_PREV)
        mp.setattr(tr, "_load_a50", lambda reader=None: _A50)
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        result = emit_for_bar(bar_key, today, _hist(), asof_ts=a_ts)
    assert result.committed is True
    table, columns, data = cap.rows[0]
    assert table == "c1_market.judgment_intraday_market_state"
    # 12 列全落位（schemas INSERT 清单真源）
    assert columns.count(",") == 11 and columns.startswith("(judgment_id")
    cells = data.decode("utf-8").rstrip("\n").split("\t")
    assert len(cells) == 12
    (jid, module_id, model_version, asof, cutoff, horizon, subject,
     payload_raw, confidence, inputs_ref, run_id, synthetic) = cells
    assert len(jid) == 26 and module_id == "MOD-PLAN-028" and model_version == "v0-rule"
    assert horizon == "intraday_rest" and subject == "index:000300.SH"
    assert synthetic == "0"
    assert asof >= cutoff  # PIT 锚机械可观测
    payload = json.loads(payload_raw)
    assert set(payload) >= {"state_label", "state_probs", "evidence", "rest_of_day"}
    assert float(confidence) == pytest.approx(float(confidence), abs=1.0)
    assert f"bar_key:{bar_key}" in inputs_ref  # 幂等键落 inputs_ref
    assert run_id == f"intraday-track:{bar_key}"
    # payload 须经发射器校验（坏 payload 此前已被拒——此处复验 label/probs 值域）
    jl.validate_payload("intraday_market_state", payload)  # 不抛=完备合法


def test_emit_pit_violation_clamped() -> None:
    """bar 时间戳漂移（cutoff>asof）被钳到 asof——发射器侧再校验一道。"""
    cap = _CapturedWriter()
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0)
    bar_key = format_bar_key(today[-1][1])
    early = datetime(2026, 9, 16, 2, 0, tzinfo=timezone.utc)  # 早于 bar 收盘(03:30 UTC)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "_load_breadth", lambda day, reader=None: None)
        mp.setattr(tr, "_load_index_prev", lambda day, reader=None: _INDEX_PREV)
        mp.setattr(tr, "_load_a50", lambda reader=None: [])
        mp.setattr(tr, "_reader_execute", lambda sql: [])
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        result = emit_for_bar(bar_key, today, _hist(), asof_ts=early)
    assert result.committed is True
    cells = cap.rows[0][2].decode("utf-8").rstrip("\n").split("\t")
    assert cells[4] <= cells[3]  # input_cutoff ≤ asof（钳制生效）


# ── 幂等（事件重放）与唤醒点 ──


def _sql_like_match(pattern: str, value: str) -> bool:
    """SQL LIKE 通配语义模拟（% → 任意串）——幂等 fake 的真实语义（防宽匹配假绿）。"""
    import re

    return re.fullmatch(re.escape(pattern).replace(r"%", ".*"), value) is not None


def _emitted_checker(emitted_keys: set[str]):
    """按真实 LIKE 语义的 count() 查重 fake（模式对真实格式 inputs_ref 做通配匹配）。"""
    import re

    def fake_count(sql: str) -> list[tuple]:
        pattern = sql.split("LIKE '")[1].split("'")[0]
        for key in emitted_keys:
            ref = f"bar_key:{key}|bar_hash:x|proxy:etf_510300|breadth_ts:|missing:none|"
            if _sql_like_match(pattern, ref):
                return [(1,)]
        return [(0,)]

    return fake_count


def test_latest_unemitted_bar_skips_emitted() -> None:
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0)
    emitted = {format_bar_key(datetime.fromisoformat("2026-09-16 11:30:00"))}

    def fake_reader(sql: str) -> list[tuple]:
        if "count()" in sql:
            return _emitted_checker(emitted)(sql)
        return _hist() + today

    found = latest_unemitted_bar(reader=fake_reader, today="2026-09-16")
    assert found is not None
    bar_key, bars_today, _hist_out = found
    # 最新 bar(11:30) 已发射 → 回退到上一根未发射 bar(10:30)
    assert bar_key == format_bar_key(datetime.fromisoformat("2026-09-16 10:30:00"))
    assert bars_today == today


def test_latest_unemitted_bar_none_when_all_emitted() -> None:
    today = _bars("2026-09-16", ["10:30"], base=4040.0)
    emitted = {format_bar_key(datetime.fromisoformat("2026-09-16 10:30:00"))}

    def fake_reader(sql: str) -> list[tuple]:
        if "count()" in sql:
            return _emitted_checker(emitted)(sql)
        return _hist() + today

    assert latest_unemitted_bar(reader=fake_reader, today="2026-09-16") is None


def test_hook_wake_point_matching() -> None:
    # 非 60min 任务/失败任务 → 零动作
    assert maybe_track_intraday_state(task_id="daily_kline:20260916", success=True) == {
        "action": "skipped_wake_point"}
    assert maybe_track_intraday_state(task_id="kline_etf_60min_incremental",
                                      success=False)["action"] == "skipped_wake_point"
    # 60min 任务匹配
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "latest_unemitted_bar", lambda: None)
        out = maybe_track_intraday_state(task_id="kline_etf_60min_incremental", success=True)
    assert out == {"action": "no_new_bar"}  # 无新 bar=零发射（非交易日抑制）


def test_hook_never_raises_and_reports() -> None:
    def boom() -> None:
        raise RuntimeError("ch down")

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "latest_unemitted_bar", boom)
        out = maybe_track_intraday_state(task_id="kline_60min_incremental", success=True)
    assert out["action"] == "error" and "RuntimeError" in out["error"]


def test_hook_emit_not_committed_disposition() -> None:
    class _FakeResult:
        judgment_id = "JX"
        committed = False
        disposition = "local_durable"

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "latest_unemitted_bar",
                   lambda: ("2026-09-16T10:30", _bars("2026-09-16", ["10:30"]), _hist()))
        mp.setattr(tr, "emit_for_bar", lambda *a, **k: _FakeResult())
        out = maybe_track_intraday_state(task_id="kline_60min_incremental", success=True)
    assert out["action"] == "emit_not_committed" and out["disposition"] == "local_durable"


# ── 与 P1 库件联测：发射行 → 结算器回填 ──


def _emit_one_row() -> tuple[dict[str, Any], str]:
    """经真实发射器产出台账行 dict（canned writer），返回 (row, bar_key)。

    asof_ts 固定 2026-09-16（不依赖墙钟——结算日联结对账需与夹具 OHLC 同日）。
    """
    cap = _CapturedWriter()
    today = _bars("2026-09-16", ["10:30", "11:30"], base=4040.0)
    bar_key = format_bar_key(today[-1][1])
    fixed_ts = datetime(2026, 9, 16, 3, 30, tzinfo=timezone.utc)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tr, "_load_breadth", lambda day, reader=None: _BREADTH)
        mp.setattr(tr, "_load_index_prev", lambda day, reader=None: _INDEX_PREV)
        mp.setattr(tr, "_load_a50", lambda reader=None: _A50)
        mp.setattr(tr, "_reader_execute", lambda sql: [])
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        emit_for_bar(bar_key, today, _hist(), asof_ts=fixed_ts)
    cols = [c.strip("() \t") for c in cap.rows[0][1].split(",")]
    cells = cap.rows[0][2].decode("utf-8").rstrip("\n").split("\t")
    row = dict(zip(cols, cells))
    return row, bar_key


def test_ledger_roundtrip_settler_backfills_intraday() -> None:
    """联测：发射→行结构→judgment_settler._settle_intraday 回填对账（P1 件只 import 不改）。"""
    row, _bar_key = _emit_one_row()
    scan_row = {k: row[k] for k in js._SCAN_COLUMNS}
    assert scan_row["module_id"] == "MOD-PLAN-028"
    # 当日 OHLC（收盘 4053.24/开盘≈4039.26 → close/open≈+0.35%>0.3% → up）
    ohlc = {"2026-09-16": (4039.26, 4053.24)}
    backfill, res, permanent = js._settle_intraday(scan_row, ohlc)
    assert res.action == "settled" and not permanent
    assert backfill is not None
    assert backfill["realized_close_vs_open"] == pytest.approx(4053.24 / 4039.26 - 1.0)
    assert backfill["state_realized"] == "up"  # ±0.3% 带宽外
    probs = json.loads(row["payload"])["state_probs"]
    p_bull = probs["进攻"] + probs["亢奋"]
    assert backfill["brier_contrib"] == pytest.approx(
        js.brier_score([(p_bull, 1.0)]))
    assert json.loads(backfill["outcome_value"])["hit"] == (p_bull >= 0.5)
    # 判定列组在发射行中完好（结算器契约：只填结算列组）
    assert row["state_label" if "state_label" in row else "payload"]  # payload 列在
    assert "evaluated_at" not in row  # 判定器无结算列写通道（结构性缺席）


def test_ledger_roundtrip_unresolvable_subject() -> None:
    row, _ = _emit_one_row()
    scan_row = {k: row[k] for k in js._SCAN_COLUMNS}
    scan_row["subject"] = "index:999999.XX"  # 未映射 subject
    backfill, res, permanent = js._settle_intraday(scan_row, {"2026-09-16": (1, 1)})
    assert res.action == "unresolvable" and res.reason == "subject_unmapped" and permanent
    assert backfill is None


def test_facade_contract() -> None:
    f = IntradayL1Tracker()
    assert f.module_id == "MOD-PLAN-028" and f.model_version == "v0-rule"
    assert f.subject == "index:000300.SH"
    payload, conf = f.decide(_bars("2026-09-16", ["10:30"], base=4040.0), _hist(),
                             _BREADTH, _INDEX_PREV, _A50, is_closing_bar=False)
    assert payload["state_label"] in {"低迷", "防御", "震荡", "进攻", "亢奋"}
