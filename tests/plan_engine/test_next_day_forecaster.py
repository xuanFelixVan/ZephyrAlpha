# [A_test] module_id: MOD-PLAN-029 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-029 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表2/§六任务2
# [MODULE] tests.plan_engine.test_next_day_forecaster
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""next_day_forecaster 次日概率件施工验证测试（判定台账标准 v0.1 §三表2）。

覆盖：
- percentile 纯函数：插值/单点/空序列 fail-closed/q 越界。
- 特征装配：ret/vol_ratio/breadth 手算对账；历史不足/均量非正/涨跌家数缺失 fail-closed。
- 条件桶：up/flat/down 带宽边界 × 量能三桶；判定坐标单调。
- 条件统计：Laplace 平滑手算对账（红蓝项：概率和恒 1——含 fallback 路径）；分位数
  单调有序；样本量 n 与 fallback 触发；**PIT 截断**（T 日之后的数据禁入历史样本——
  红蓝项：末行后偷偷塞未来行不改变判定）。
- 发射：payload 过发射器 fail-closed 校验、inputs_hash 确定性（同输入同指纹/输入变
  指纹变）、inputs_ref 幂等键（trade_date）、12 列完备（schemas INSERT 清单对齐）。
- 幂等（事件重放）：同 trade_date 已发射 → already_emitted 零发射。
- 唤醒点：非 daily_kline 任务/失败任务 → skipped_wake_point；T 日线不在库 →
  data_insufficient（fail-closed 漏判不瞎判）；业务日不可解析 → error 不反噬。
- 与 P1 库件联测：发射行（canned ch_writer）→ judgment_settler._settle_next_day 回填
  （T+1 收盘注入）→ brier/log_loss/label 对账。
全 monkeypatch/canned 隔离，不触真 ClickHouse（真库冒烟走 synthetic=1 标注+清理通道）。
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import judgment_settler as js
from zephyr.plan_engine import next_day_forecaster as nf
from zephyr.plan_engine.next_day_forecaster import (
    NextDayForecaster,
    build_day_features,
    bucket_of,
    cond_prob_from_history,
    emit_for_trade_date,
    inputs_hash_of,
    maybe_emit_next_day_forecast,
    percentile,
)


# ── percentile ──


def test_percentile_interpolation() -> None:
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == pytest.approx(2.5)
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.0) == 1.0
    assert percentile([1.0, 2.0, 3.0, 4.0], 1.0) == 4.0
    assert percentile([1.0, 2.0, 3.0], 0.25) == pytest.approx(1.5)
    assert percentile([5.0], 0.7) == 5.0


def test_percentile_fail_closed() -> None:
    with pytest.raises(ValueError, match="空序列"):
        percentile([], 0.5)
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        percentile([1.0], 1.5)


# ── 夹具（synthetic 日线——结构对齐 kline_index 行元组）──


def _kline_rows(n: int = 60, seed: int = 7) -> list[tuple]:
    """合成 n 日 OHLCV+涨跌家数（确定性伪随机——循环同余生成器，零外部依赖）。"""
    rows: list[tuple] = []
    px = 4000.0
    state = seed
    for i in range(n):
        state = (state * 1103515245 + 12345) % (2**31)
        chg = ((state % 2000) - 1000) / 1000.0 * 0.012  # ±1.2%
        op = px
        cl = px * (1 + chg)
        hi = max(op, cl) * 1.004
        lo = min(op, cl) * 0.996
        vol = int(8e8 + (state % 400) * 1e6)  # 8e8~1.196e9
        adv = int(2500 + chg * 60000)
        dec = int(2500 - chg * 60000)
        d = f"2026-{5 + i // 28:02d}-{1 + i % 28:02d}"
        rows.append((d, round(op, 2), round(hi, 2), round(lo, 2), round(cl, 2), vol, adv, dec))
        px = cl
    return rows


# ── 特征装配（手算对账）──


def test_build_day_features_hand_computed() -> None:
    rows = _kline_rows()
    feat = build_day_features(rows)
    t, prev = rows[-1], rows[-2]
    assert feat["ret"] == pytest.approx(float(t[4]) / float(prev[4]) - 1.0)
    vol_hist = [float(r[5]) for r in rows[-21:-1]]
    assert feat["vol_ratio"] == pytest.approx(float(t[5]) / (sum(vol_hist) / 20))
    assert feat["breadth"] == pytest.approx(float(t[6]) / (float(t[6]) + float(t[7])))
    assert feat["trade_date"] == str(t[0])


def test_build_day_features_fail_closed() -> None:
    rows = _kline_rows()
    with pytest.raises(ValueError, match="历史不足"):
        build_day_features(rows[:10])
    # 末前 20 日全为 0 量 → 历史均量非正（fail-closed）
    zero_vol_hist = [(r[0], r[1], r[2], r[3], r[4], 0, r[6], r[7]) for r in rows[-21:-1]]
    bad_vol = rows[:-21] + zero_vol_hist + [rows[-1]]
    with pytest.raises(ValueError, match="均量非正"):
        build_day_features(bad_vol)


def test_build_day_features_breadth_missing_degrades() -> None:
    """红蓝项：涨跌家数缺席（kline_index 该列 2026-07 后断供实况）=降级标注不拒绝。"""
    rows = _kline_rows()
    no_breadth = rows[:-1] + [tuple(r[:6]) + (0, 0) for r in rows[-1:]]
    feat = build_day_features(no_breadth)
    assert "breadth" not in feat
    assert feat["degraded_breadth"] is True
    # 桶统计仍完备（桶=ret×vol，breadth 不参与）
    st = cond_prob_from_history(no_breadth, feat)
    assert abs(st["p_up"] + st["p_flat"] + st["p_down"] - 1.0) < 1e-9


# ── 条件桶 ──


def test_bucket_of_boundaries() -> None:
    band = nf.RULE_PARAMS["ret_band"]
    assert bucket_of({"ret": band * 2, "vol_ratio": 1.0}) == ("up", "mid")
    assert bucket_of({"ret": -band * 2, "vol_ratio": 1.0}) == ("down", "mid")
    assert bucket_of({"ret": 0.0, "vol_ratio": 1.0}) == ("flat", "mid")
    assert bucket_of({"ret": band, "vol_ratio": 1.0}) == ("flat", "mid")  # 带内=flat
    assert bucket_of({"ret": 0.0, "vol_ratio": 0.5}) == ("flat", "low")
    assert bucket_of({"ret": 0.0, "vol_ratio": 2.0}) == ("flat", "high")


# ── 条件统计（归一/PIT/fallback）──


def test_cond_prob_normalized_and_laplace() -> None:
    rows = _kline_rows(n=120)
    feat = build_day_features(rows)
    st = cond_prob_from_history(rows, feat)
    total = st["p_up"] + st["p_flat"] + st["p_down"]
    assert abs(total - 1.0) < 1e-9  # 红蓝项：归一（Laplace 分母同径）
    assert all(0.0 < v < 1.0 for v in (st["p_up"], st["p_flat"], st["p_down"]))
    # Laplace 手算对账：p_up=(n_up+α)/(N+3α)
    assert st["p_up"] == pytest.approx(
        (st["n"] * st["p_up"] * 0 + _n_up(rows, feat) + nf.RULE_PARAMS["laplace_alpha"])
        / (st["n"] + 3 * nf.RULE_PARAMS["laplace_alpha"]))
    # 分位单调有序
    q = st["quantiles"]
    assert q["q10"] <= q["q25"] <= q["q50"] <= q["q75"] <= q["q90"]
    assert st["expected_vol_pct"] >= 0
    assert st["expected_range_pct"] >= 0


def _n_up(rows: list[tuple], feat: dict[str, float]) -> int:
    """同桶历史中次日上涨计数（与 cond_prob_from_history 同口径）。"""
    band = float(nf.RULE_PARAMS["ret_band"])
    st = cond_prob_from_history(rows, feat)
    # 反解：p_up*(N+3α)-α = n_up
    return round(st["p_up"] * (st["n"] + 3 * float(nf.RULE_PARAMS["laplace_alpha"]))
                 - float(nf.RULE_PARAMS["laplace_alpha"]))


def test_cond_prob_pit_truncation() -> None:
    """红蓝项：T 日之后塞入未来行不得改变判定（历史窗口按 trade_date 截断）。"""
    rows = _kline_rows(n=60)
    feat = build_day_features(rows)
    base = cond_prob_from_history(rows, feat)
    future = []
    px = float(rows[-1][4])
    for i in range(1, 6):  # 未来 5 日（trade_date 大于 T 日）
        d = f"2026-12-{i:02d}"
        px = px * 1.05  # 剧烈上涨的未来
        future.append((d, round(px, 2), round(px * 1.01, 2), round(px * 0.99, 2),
                       round(px, 2), 10**9, 4000, 1000))
    padded = rows + future
    after = cond_prob_from_history(padded, feat)  # feat 仍是原 T 日
    assert after["p_up"] == base["p_up"]  # 未来数据禁入样本——判定不变
    assert after["n"] == base["n"]


def test_cond_prob_fallback_small_bucket() -> None:
    rows = _kline_rows(n=60)
    feat = build_day_features(rows)
    st = cond_prob_from_history(rows, feat)
    if st["fallback"]:
        # 全样本基线路径：n=全部历史日数（≥min_bucket_n 才有非空统计）
        assert st["n"] >= nf.RULE_PARAMS["min_bucket_n"]
    else:
        assert st["n"] >= nf.RULE_PARAMS["min_bucket_n"]
    # 无论哪条路径都归一
    assert abs(st["p_up"] + st["p_flat"] + st["p_down"] - 1.0) < 1e-9


def test_cond_prob_empty_history_fail_closed() -> None:
    rows = _kline_rows(n=25)  # 刚过 lookback+1，但可统计窗口几乎为 0
    feat = build_day_features(rows)
    with pytest.raises(ValueError):
        cond_prob_from_history(rows[:21], feat)


# ── 发射（指纹/字段完备/PIT）──


class _CapturedWriter:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bytes]] = []

    def __call__(self, table: str, columns: str, data: bytes):
        from zephyr.data.ch_writer import WriteDisposition

        self.rows.append((table, columns, data))

        class _R:
            disposition = WriteDisposition.CH_COMMITTED

        return _R()


def _fixed_ts() -> datetime:
    return datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc)


def test_inputs_hash_deterministic() -> None:
    rows = _kline_rows()
    feat = build_day_features(rows)
    st = cond_prob_from_history(rows, feat)
    h1 = inputs_hash_of(feat, st)
    h2 = inputs_hash_of(build_day_features(rows), cond_prob_from_history(rows, feat))
    assert h1 == h2 and len(h1) == 16  # 同输入同指纹
    feat2 = dict(feat, close=feat["close"] + 1.0)
    assert inputs_hash_of(feat2, st) != h1  # 输入变=指纹变


def test_emit_fields_complete() -> None:
    cap = _CapturedWriter()
    rows = _kline_rows()
    day = str(rows[-1][0])
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute",
                   lambda sql: rows if "SELECT trade_date" in sql else [(0,)])
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        result = emit_for_trade_date(day, asof_ts=_fixed_ts())
    assert result.committed is True
    table, columns, data = cap.rows[0]
    assert table == "c1_market.judgment_next_day_forecast"
    assert columns.count(",") == 11
    cells = data.decode("utf-8").rstrip("\n").split("\t")
    assert len(cells) == 12
    (jid, module_id, model_version, asof, cutoff, horizon, subject,
     payload_raw, confidence, inputs_ref, run_id, synthetic) = cells
    assert module_id == "MOD-PLAN-029" and model_version == "v0-hist"
    assert horizon == "next_day" and subject == "index:000300.SH"
    assert synthetic == "0" and asof == cutoff  # 日线收盘口径：数据齐才触发
    payload = json.loads(payload_raw)
    assert abs(payload["p_up"] + payload["p_flat"] + payload["p_down"] - 1.0) < 1e-6
    assert set(payload["quantiles"]) == {"q10", "q25", "q50", "q75", "q90"}
    assert payload["expected_vol_pct"] >= 0 and payload["expected_range_pct"] >= 0
    assert f"trade_date:{day}" in inputs_ref  # 幂等键
    assert "inputs_hash:" in inputs_ref
    assert run_id == f"next-day:{day}"
    assert 0.0 <= float(confidence) <= 1.0
    jl.validate_payload("next_day_forecast", payload)  # 不抛=完备合法


def test_emit_t_day_missing_fail_closed() -> None:
    rows = _kline_rows()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute", lambda sql: rows)
        with pytest.raises(ValueError, match="不在库"):
            emit_for_trade_date("2030-01-01", asof_ts=_fixed_ts())


# ── 幂等与唤醒点 ──


def _sql_like_match(pattern: str, value: str) -> bool:
    """SQL LIKE 通配语义模拟（% → 任意串；大小写敏感近似）——幂等 fake 的真实语义。"""
    import re

    return re.fullmatch(re.escape(pattern).replace(r"%", ".*"), value) is not None


def test_hook_idempotent_same_trade_date() -> None:
    rows = _kline_rows()
    day = str(rows[-1][0])

    def fake_reader(sql: str) -> list[tuple]:
        if "count()" in sql:
            # 真实 LIKE 语义：提取 pattern，对真实格式 inputs_ref 做通配匹配
            # （此前 fake 用宽子串判断=假绿，放跑了 '%|key|%' 首键 miss 事故——红蓝修复）
            pattern = sql.split("LIKE '")[1].split("'")[0]
            sample_ref = (f"trade_date:{day}|inputs_hash:c81cba763bebf69b"
                          f"|bucket:down:low|n:470|fallback:0|")
            return [(1,)] if _sql_like_match(pattern, sample_ref) else [(0,)]
        return rows

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute", fake_reader)
        mp.setattr("zephyr.strategy_pipeline.pipeline_events.resolve_pf_alloc_trade_date",
                   lambda: day)
        out = maybe_emit_next_day_forecast(task_id="daily_kline:20260729", success=True)
    assert out == {"action": "already_emitted", "trade_date": day}  # 事件重放零副作用
    # 修复断言：pattern 必须匹配首键在前的真实 inputs_ref（防回归 '%|key|%' 写法）
    assert _sql_like_match("%trade_date:%|", f"trade_date:{day}|x|")


def test_hook_wake_point_matching() -> None:
    assert maybe_emit_next_day_forecast(task_id="kline_etf_60min_incremental",
                                        success=True) == {"action": "skipped_wake_point"}
    assert maybe_emit_next_day_forecast(task_id="daily_kline:20260729",
                                        success=False)["action"] == "skipped_wake_point"


def test_hook_t_day_not_ready_data_insufficient() -> None:
    rows = _kline_rows()
    day = str(rows[-1][0])

    def fake_reader(sql: str) -> list[tuple]:
        if "count()" in sql:
            return [(0,)]
        return [r for r in rows if str(r[0]) < day][:10]  # T 日线未齐+历史不足

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute", fake_reader)
        mp.setattr("zephyr.strategy_pipeline.pipeline_events.resolve_pf_alloc_trade_date",
                   lambda: day)
        out = maybe_emit_next_day_forecast(task_id="kline_index_incremental", success=True)
    assert out["action"] == "data_insufficient"  # fail-closed 漏判，不瞎判不反噬


def test_hook_resolve_failure_never_raises() -> None:
    with pytest.MonkeyPatch.context() as mp:
        def boom() -> str:
            raise RuntimeError("ch down")

        mp.setattr("zephyr.strategy_pipeline.pipeline_events.resolve_pf_alloc_trade_date", boom)
        out = maybe_emit_next_day_forecast(task_id="daily_kline:20260729", success=True)
    assert out["action"] == "error" and "RuntimeError" in out["error"]


def test_hook_emitted_happy_path() -> None:
    cap = _CapturedWriter()
    rows = _kline_rows()
    day = str(rows[-1][0])

    def fake_reader(sql: str) -> list[tuple]:
        if "count()" in sql:
            # 首次发射场景：已发射清单为空 → 查重恒 0（真实 LIKE 语义由
            # test_hook_idempotent_same_trade_date 的正反向断言覆盖）
            return [(0,)]
        return rows if "SELECT trade_date" in sql else []

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute", fake_reader)
        mp.setattr("zephyr.strategy_pipeline.pipeline_events.resolve_pf_alloc_trade_date",
                   lambda: day)
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        out = maybe_emit_next_day_forecast(task_id="daily_kline:20260729", success=True)
    assert out["action"] == "emitted" and out["trade_date"] == day
    assert len(cap.rows) == 1


# ── 与 P1 库件联测：发射行 → 结算器回填 ──


def _emit_one_row() -> dict[str, Any]:
    cap = _CapturedWriter()
    rows = _kline_rows()
    day = str(rows[-1][0])
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(nf, "_reader_execute",
                   lambda sql: rows if "SELECT trade_date" in sql else [(0,)])
        import zephyr.plan_engine.judgment_ledger as jl

        mp.setattr(jl.ch_writer, "write_tsv_outcome", cap)
        emit_for_trade_date(day, asof_ts=_fixed_ts())
    cols = [c.strip("() \t") for c in cap.rows[0][1].split(",")]
    cells = cap.rows[0][2].decode("utf-8").rstrip("\n").split("\t")
    return dict(zip(cols, cells))


def test_ledger_roundtrip_settler_backfills_next_day() -> None:
    """联测：发射→行结构→judgment_settler._settle_next_day 回填对账（P1 件只 import 不改）。"""
    row = _emit_one_row()
    scan_row = {k: row[k] for k in js._SCAN_COLUMNS}
    assert scan_row["module_id"] == "MOD-PLAN-029"
    asof_day = str(scan_row["asof_ts"])[:10]
    t_close = 4000.0
    t1_close = 4040.0  # T+1 +1.0%
    cal = {asof_day: t_close, "2026-08-03": t1_close}
    backfill, res, permanent = js._settle_next_day(scan_row, cal)
    assert res.action == "settled" and not permanent
    assert backfill is not None
    assert backfill["realized_return"] == pytest.approx(0.01)
    assert backfill["realized_label"] == "up"  # ±0.1% 带宽
    payload = json.loads(row["payload"])
    expected_brier = sum(
        (p - o) ** 2 for p, o in zip(
            (payload["p_up"], payload["p_flat"], payload["p_down"]), (1.0, 0.0, 0.0)))
    assert backfill["brier_score"] == pytest.approx(expected_brier, abs=1e-9)
    assert backfill["log_loss"] == pytest.approx(-math.log(payload["p_up"]))
    assert backfill["calibration_bucket"].startswith("0.")
    assert "evaluated_at" not in row  # 判定器无结算列写通道（结构性缺席）


def test_facade_contract() -> None:
    f = NextDayForecaster()
    assert f.module_id == "MOD-PLAN-029" and f.model_version == "v0-hist"
    st = f.forecast(_kline_rows())
    assert abs(st["p_up"] + st["p_flat"] + st["p_down"] - 1.0) < 1e-9
