# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/T0_MATERIAL_EXAM_CARD_draft.md | §4 成交模型 M0
# [MODULE] tests.backtest.test_t0_material_line
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest, pandas
# [CONSUMERS] t0_material_line 管线（L05-C02 材料线草案）同批测试
# [STARTUP] manual（pytest tests/backtest/test_t0_material_line.py）
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数面零 IO 零网络（禁触 CH 禁真全量跑，测试隔离=构造数据）；判据常数断言 import 复用 cost_trio_exam（31.2/30/30 禁本地重写）；闭卷硬拦行为必须红（越切点=SystemExit）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [TTL] task_bound
"""t0_material_line 管线单测——构造数据纯函数面：M0 触发/成交价/末日强平/除零挡/
重采样分桶/板别涨跌停门/闭卷硬拦/抽样确定性/FakeConn 端到端。禁真全量跑。"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from scripts.audit import cost_trio_exam as ct  # 判据唯一真源（import 复用断言用）
from scripts.backtest import t0_material_line as ml

# ---------- 构造数据 ----------


def make_day(prices: list[float], date: str = "2024-03-04") -> pd.DataFrame:
    n = len(prices)
    times = pd.date_range(f"{date} 09:30", periods=n, freq="min")
    return pd.DataFrame(
        {
            "trade_time": times,
            "open": prices,
            "high": prices,
            "low": prices,
            "close": prices,
            "volume": [1000.0] * n,
        }
    )


def make_dip_rally_day(date: str = "2024-03-04") -> pd.DataFrame:
    """240 根：开盘 10.00 平走→bar30 探 9.85→9.95 平台→bar100 冲 10.10→10.02 平台收尾。

    M0(100bp) 预期：买触发 bar30 成交 9.90（=min(open 9.92, 触发 9.90)）；
    卖触发 bar100 成交 10.05（=max(open 10.05, 触发 9.999)）；毛价差=10.05/9.90−1≈152bp。
    """
    df = make_day([10.0] * 240, date)
    df.loc[30, "open"], df.loc[30, "low"], df.loc[30, "close"] = 9.92, 9.85, 9.95
    df.loc[31:99, ["open", "high", "low", "close"]] = 9.95
    df.loc[100, "open"], df.loc[100, "high"], df.loc[100, "close"] = 10.05, 10.10, 10.02
    df.loc[101:, ["open", "high", "low", "close"]] = 10.02
    return df


# ---------- 板别涨跌停极限（V3 M-4 + 红蓝 #11） ----------


def test_board_limit_bp():
    assert ml.board_limit_bp("600519") == 1000.0  # 主板 ±10%
    assert ml.board_limit_bp("000001") == 1000.0
    assert ml.board_limit_bp("300750") == 2000.0  # 创业板 ±20%
    assert ml.board_limit_bp("301236") == 2000.0
    assert ml.board_limit_bp("688981") == 2000.0  # 科创板 ±20%
    assert ml.board_limit_bp("920002") == 3000.0  # 北交所 ±30%（红蓝 #11）
    assert ml.board_limit_bp("830799") == 3000.0
    assert ml.board_limit_bp("430047") == 3000.0


# ---------- 周期重采样（日内 bar 序数分桶，钟面无关） ----------


def test_resample_period_1_identity():
    day = make_dip_rally_day()
    out = ml.resample_period(day, 1)
    assert len(out) == 240
    assert out["open"].iloc[0] == 10.0


def test_resample_period_5_bucketing():
    day = make_dip_rally_day()
    out = ml.resample_period(day, 5)
    assert len(out) == 48  # 240/5
    b6 = out.iloc[6]  # 桶 6 = bar30..34：open=9.92（首根）、low=9.85（最小）、close=9.95（末根）
    assert b6["open"] == 9.92
    assert b6["low"] == 9.85
    assert b6["close"] == 9.95
    assert b6["trade_time"] == day["trade_time"].iloc[34]  # 桶时刻=桶内末根
    b0 = out.iloc[0]
    assert b0["high"] == 10.0 and b0["low"] == 10.0
    # 午休/缺 bar 免疫：序数分桶不依赖钟面（构造 37 根非整除同样不炸）
    odd = make_day([10.0] * 37)
    assert len(ml.resample_period(odd, 5)) == 8  # ceil(37/5)


def test_min_bars_table_consistency():
    assert set(ml.MIN_BARS_BY_PERIOD) == set(ml.ALLOWED_PERIODS)
    assert 120 not in ml.ALLOWED_PERIODS  # 120min 不做（Owner 明令）
    for p, mb in ml.MIN_BARS_BY_PERIOD.items():
        assert mb >= 0.8 * (240 / p)  # ≥83% 标准 session 桶数（1min 真实 240）


# ---------- M0 探针模型 ----------


def test_m0_pair_trigger_and_fill_prices():
    day = make_dip_rally_day()
    fills, reason = ml.run_model_m0(day, grid_bp=100.0, notional=100_000.0, min_bars=200)
    assert reason == "pair" and fills is not None
    assert fills["buy_ts"] == day["trade_time"].iloc[30]
    assert fills["buy_price"] == pytest.approx(9.90)  # min(bar.open 9.92, 触发 9.90)：挂单限价机制
    assert fills["sell_ts"] == day["trade_time"].iloc[100]
    assert fills["sell_price"] == pytest.approx(10.05)  # max(bar.open 10.05, 触发 9.999)
    assert fills["qty"] == 10_100  # floor(100000/9.9/100)*100 = floor(101.01)*100 = 10100
    gross = (fills["sell_price"] / fills["buy_price"] - 1) * 1e4
    assert gross == pytest.approx(151.52, abs=0.05)
    assert gross >= ct.EDGE_PRECONDITION_BP  # 前置命中


def test_m0_no_touch_day():
    day = make_day([10.0] * 240)  # 全天 ±0.1% 内，永不探 1% 档
    fills, reason = ml.run_model_m0(day, grid_bp=100.0, notional=100_000.0, min_bars=200)
    assert fills is None and reason == "no_touch"


def test_m0_force_close_eod():
    df = make_day([10.0] * 240)
    df.loc[30, "open"], df.loc[30, "low"] = 9.92, 9.85  # 探档买入
    df.loc[31:, ["open", "high", "low", "close"]] = 9.92  # 全天不回升 ⇒ 末根强平
    fills, reason = ml.run_model_m0(df, grid_bp=100.0, notional=100_000.0, min_bars=200)
    assert reason == "pair" and fills is not None
    assert fills["sell_ts"] == df["trade_time"].iloc[-1]  # 末根强平，同日两腿仍在
    assert fills["sell_price"] == pytest.approx(9.92)
    gross = (fills["sell_price"] / fills["buy_price"] - 1) * 1e4
    assert gross < ct.EDGE_PRECONDITION_BP  # 强平对=前置不命中（如实进语料，禁挑样）


def test_m0_guards_low_bars_and_zero_price():
    short = make_day([10.0] * 100)
    fills, reason = ml.run_model_m0(short, grid_bp=100.0, notional=1e5, min_bars=200)
    assert fills is None and reason == "low_bars"
    df = make_day([10.0] * 240)
    df.loc[100, "low"] = 0.0  # 零价 bar（t0_ceiling_verdict §4 实测存在的坏行）
    fills, reason = ml.run_model_m0(df, grid_bp=100.0, notional=1e5, min_bars=200)
    assert fills is None and reason == "zero_price"
    one = make_day([10.0])
    fills, reason = ml.run_model_m0(one, grid_bp=100.0, notional=1e5, min_bars=200)
    assert fills is None and reason == "one_bar"


# ---------- 配对真源 import 复用（禁重写） ----------


def test_fills_flow_through_frozen_build_pairs():
    day = make_dip_rally_day()
    fills, reason = ml.run_model_m0(day, 100.0, 100_000.0, 200)
    assert reason == "pair"
    ct_fills = ml.fills_to_cost_trio_format("600519", "2024-03-04", fills, run_id="t0mat-test")
    assert len(ct_fills) == 2
    assert ct_fills[0]["run_id"] == ct_fills[1]["run_id"] == "t0mat-test"  # M-2 同体 by construction
    assert ":" in str(ct_fills[0]["timestamp"])  # M-1 日内粒度
    pairs = ct.build_pairs(ct_fills)  # frozen 配对真源（同票同日既买又卖）
    assert len(pairs) == 1
    p = pairs[0]
    assert p["symbol"] == "600519" and p["trade_date"] == "2024-03-04"
    assert p["net_bp"] == pytest.approx(p["gross_bp"] - ct.RT_COST_BP)  # 31.2bp import 复用零改动


# ---------- 材料资格门（V3 M-4） ----------


def test_material_gate_m4_price_limit():
    pairs = [
        {"symbol": "600519", "gross_bp": 1100.0, "net_bp": 1068.8},  # 超主板 ±10% ⇒ 剔
        {"symbol": "300750", "gross_bp": 1500.0, "net_bp": 1468.8},  # 创业板限内 ⇒ 留
        {"symbol": "688981", "gross_bp": 2100.0, "net_bp": 2068.8},  # 超科创板 ±20% ⇒ 剔
    ]
    kept, audit = ml.apply_material_gates(pairs)
    assert len(kept) == 1 and kept[0]["symbol"] == "300750"
    assert audit["m4_rejected_price_limit"] == 2


# ---------- 闭卷硬拦与窗校验 ----------


def test_enforce_closed_book_hard_block():
    ml.enforce_closed_book("2021-09-01", "2025-09-09")  # 切点当日=合法（<= 切点）
    with pytest.raises(SystemExit, match="闭卷"):
        ml.enforce_closed_book("2021-09-01", "2025-09-10")
    with pytest.raises(SystemExit, match="法定起点"):
        ml.enforce_closed_book("2021-08-31", "2025-09-09")


# ---------- 确定性行距抽样 ----------


def test_deterministic_sample():
    universe = [f"{i:06d}" for i in range(1000)]
    s1 = ml.deterministic_sample(universe, 20)
    s2 = ml.deterministic_sample(universe, 20)
    assert s1 == s2  # 无随机种子=可复现
    assert len(s1) == 20 and len(set(s1)) == 20
    assert s1 == sorted(s1)
    assert ml.deterministic_sample(universe[:10], 20) == universe[:10]  # n≥len 全取


# ---------- 端到端（FakeConn 构造行，禁触真库） ----------


class _FakeConn:
    """execute() 直接返回构造行：1 只 × 1 日 × 240 根 dip-rail 日。"""

    def __init__(self, day: pd.DataFrame, symbol: str = "600519", trade_date: str = "2024-03-04"):
        d = dt.date.fromisoformat(trade_date)
        self.rows = [
            (symbol, d, t.to_pydatetime(), float(r.open), float(r.high), float(r.low), float(r.close), float(r.volume))
            for t, r in zip(day["trade_time"], day.itertuples(index=False), strict=True)
        ]
        self.queries: list[str] = []

    def execute(self, sql: str):
        self.queries.append(sql)
        return self.rows


def test_run_pipeline_end_to_end_fake_conn():
    conn = _FakeConn(make_dip_rally_day())
    frames, stats = ml.run_pipeline(
        conn,
        symbols=["600519"],
        start="2021-09-01",
        end="2025-09-09",
        periods=[1, 5],
        grid_bp=100.0,
        notional=100_000.0,
        run_id="t0mat-test",
    )
    # 判据来源=import 复用（禁本地常量顶替）
    cs = stats["criteria_source"]
    assert cs["rt_cost_bp"] == ct.RT_COST_BP == 31.2
    assert cs["pair_gate"] == ct.PAIR_GATE == 30
    assert cs["edge_precondition_bp"] == ct.EDGE_PRECONDITION_BP == 30.0
    assert stats["window"]["closed_book_ok"] is True
    assert stats["window"]["end"] <= ml.CLOSED_BOOK_CUTOFF
    # 两个周期同一构造日各出 1 对（dip 桶/冲高桶在 5min 分桶后仍在不同桶）
    for label in ("1min", "5min"):
        blk = stats["periods"][label]
        assert blk["n_symbol_days"] == 1
        assert blk["n_pairs"] == 1
        assert blk["reason_counts"].get("pair") == 1
        assert blk["edge_ge_30bp"] == 1
    df = frames["1min"]
    assert list(df["gross_bp"]) and float(df["gross_bp"].iloc[0]) >= 30.0
    assert "market_kline_1min" in conn.queries[0] or "kline_1min" in conn.queries[0]


def test_cli_period_validation_and_closed_book(tmp_path, monkeypatch):
    # --end 越切点：main 入口即拦（fail-closed），禁闭卷数据入研究
    monkeypatch.setattr("sys.argv", ["t0_material_line.py", "--sample", "2", "--end", "2025-09-10"])
    with pytest.raises(SystemExit, match="闭卷"):
        ml.main()
    monkeypatch.setattr("sys.argv", ["t0_material_line.py", "--sample", "2", "--period", "1,120"])
    with pytest.raises(SystemExit, match="周期"):
        ml.main()
    monkeypatch.setattr("sys.argv", ["t0_material_line.py"])
    with pytest.raises(SystemExit, match="股票池"):
        ml.main()
