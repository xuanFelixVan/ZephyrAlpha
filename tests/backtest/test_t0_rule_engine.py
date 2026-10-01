# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/（4 卡）
# [MODULE] tests.backtest.test_t0_rule_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest, pandas
# [CONSUMERS] t0_rule_engine（L05-C03）同批测试
# [STARTUP] manual（pytest tests/backtest/test_t0_rule_engine.py）
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数面零 IO 零网络（禁触 CH 禁真全量跑；卡读取仅断言预注册完整性）；R01 与 t0_material_line.run_model_m0 同参逐位一致必须绿；判据常数 import 断言禁本地重写；闭卷硬拦行为必须红
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [TTL] task_bound
"""t0_rule_engine 单测——构造数据纯函数面：R01 与 M0 同参一致/R02 波动带/R03 运行 VWAP/
R04 ORB/批次确定性/前置日上下文/规则卡预注册完整性。禁真全量跑。"""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.backtest import t0_material_line as ml
from scripts.backtest import t0_rule_engine as eng
from scripts.backtest.t0_state_match_matrix import sha256_file  # 共享哈希工具（复用断言）

CARDS_DIR = eng.DEFAULT_CARDS_DIR


# ---------- 构造数据 ----------


def make_day_frame(prices: list[list[float]], date: str = "2024-03-04", symbol: str = "000001") -> pd.DataFrame:
    """prices=每根 bar 的 (open, high, low, close)。"""
    n = len(prices)
    rows = [
        {
            "symbol": symbol,
            "trade_date": date,
            "trade_time": i,
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": 1000.0,
        }
        for i, (o, h, l, c) in enumerate(prices)
    ]
    return pd.DataFrame(rows)


def dip_rally_bars() -> list[list[float]]:
    """bar30 探 9.85（触发 100bp 买）→ bar100 冲 10.10（触发卖）。"""
    bars = [[10.0] * 4 for _ in range(240)]
    bars[30] = [9.92, 9.95, 9.85, 9.95]
    for i in range(31, 100):
        bars[i] = [9.95, 9.95, 9.95, 9.95]
    bars[100] = [10.05, 10.10, 10.05, 10.02]
    for i in range(101, 240):
        bars[i] = [10.02, 10.02, 10.02, 10.02]
    return bars


# ---------- R01 == M0 同参一致（卡委托零重实现的承重断言） ----------


def test_r01_delegates_to_m0_bitwise():
    day = make_day_frame(dip_rally_bars())
    card = {"params": {"grid_bp": 100.0}, "run_id_prefix": "t0rule-r01-t-p"}
    bars = ml.resample_period(day, 1)
    fills_engine, reason_e = eng.evaluate_day(day, bars, 1, "r01", card, {})
    assert reason_e == "pair"
    fills_m0, reason_m0 = ml.run_model_m0(bars, 100.0, ml.DEFAULT_NOTIONAL, ml.MIN_BARS_BY_PERIOD[1])
    assert reason_m0 == "pair"
    assert fills_engine is not None and fills_m0 is not None
    # cost_trio 格式两腿 vs M0 原始 fills：价格/时刻/数量逐位一致
    buy_leg = fills_engine[0]
    sell_leg = fills_engine[1]
    assert float(buy_leg["price"]) == fills_m0["buy_price"]
    assert float(sell_leg["price"]) == fills_m0["sell_price"]
    assert int(buy_leg["quantity"]) == fills_m0["qty"] == int(sell_leg["quantity"])
    assert str(buy_leg["timestamp"]) == str(fills_m0["buy_ts"])
    assert str(sell_leg["timestamp"]) == str(fills_m0["sell_ts"])


# ---------- R02 波动率自适应带 ----------

R02_CARD = {"params": {"band_k": 1.0, "band_floor_bp": 50.0, "band_cap_bp": 300.0}}


def test_r02_band_from_prev_day_tr_and_symmetry():
    day = make_day_frame(dip_rally_bars())
    bars = ml.resample_period(day, 1)
    prev_tr_bp = 120.0  # 落在 [50,300] 内 ⇒ band=120bp
    fills, reason = eng.run_rule_r02(bars, prev_tr_bp, R02_CARD)
    assert reason == "pair"
    base = 10.0
    buy_level = base * (1 - 120.0 / 1e4)
    assert fills["buy_price"] == pytest.approx(min(9.92, buy_level))
    sell_level = fills["buy_price"] * (1 + 120.0 / 1e4)
    assert fills["sell_price"] == pytest.approx(max(10.05, sell_level))


def test_r02_floor_cap_and_no_prev_day():
    day = make_day_frame(dip_rally_bars())
    bars = ml.resample_period(day, 1)
    # floor：prev_tr=1bp ⇒ band=50bp ⇒ 买档 10×0.995=9.95；bar30 low 9.85 触发，fill=min(9.92,9.95)=9.92
    fills_floor, reason_floor = eng.run_rule_r02(bars, 1.0, R02_CARD)
    assert reason_floor == "pair" and fills_floor["buy_price"] == pytest.approx(9.92)
    # cap：prev_tr=10000bp ⇒ band=300bp ⇒ 买档 7.0，不触
    fills_cap, reason_cap = eng.run_rule_r02(bars, 10000.0, R02_CARD)
    assert reason_cap == "no_touch" and fills_cap is None
    # 首日无前置日
    fills_none, reason_none = eng.run_rule_r02(bars, None, R02_CARD)
    assert reason_none == "no_prev_day" and fills_none is None


def test_r02_prev_ctx_sequence_across_days():
    day = make_day_frame(dip_rally_bars())
    bars = ml.resample_period(day, 1)
    prev_ctx: dict = {}
    eng.update_prev_ctx(bars, prev_ctx)
    tr = prev_ctx["tr_bp"]
    assert tr == pytest.approx((10.10 - 9.85) / 10.02 * 1e4)
    # tr=249.5bp ⇒ band=249.5 ⇒ 买档 9.7505：原日 low 9.85 不触（band 值确实流入了触发）
    fills, reason = eng.run_rule_r02(bars, tr, dict(R02_CARD))
    assert reason == "no_touch"
    # 更深回撤日（bar30 low 9.70）在 band=249.5 下触发 ⇒ 前置日上下文语义完整
    deep = dip_rally_bars()
    deep[30][2] = 9.70
    fills2, reason2 = eng.run_rule_r02(ml.resample_period(make_day_frame(deep), 1), tr, dict(R02_CARD))
    assert reason2 == "pair" and fills2["buy_price"] == pytest.approx(9.70 * 0 + min(9.92, 10.0 * (1 - tr / 1e4)))


# ---------- R03 VWAP 带反转 ----------

R03_CARD = {"params": {"vwap_band_bp": 50.0}}


def test_r03_running_vwap_trigger():
    # 3 根 bar：vwap1=10.00；bar2 触发买（low≤vwap×0.995）；bar3 触发卖
    bars_df = make_day_frame([[10.0, 10.0, 10.0, 10.0], [9.9, 9.95, 9.9, 9.92], [9.96, 10.0, 9.95, 10.0]])
    bars = ml.resample_period(bars_df, 1)
    fills, reason = eng.run_rule_r03(bars, R03_CARD)
    assert reason == "pair"
    vwap1 = 10.0
    trig1 = vwap1 * 0.995
    assert fills["buy_price"] == pytest.approx(min(9.9, trig1))
    sell_level = fills["buy_price"] * 1.005
    assert fills["sell_price"] == pytest.approx(max(9.96, sell_level))


def test_r03_no_touch_reason():
    bars_df = make_day_frame([[10.0] * 4 for _ in range(240)])
    fills, reason = eng.run_rule_r03(ml.resample_period(bars_df, 1), R03_CARD)
    assert reason == "no_touch" and fills is None


# ---------- R04 ORB ----------


def _r04_card(k: int) -> dict:
    return {"params": {"or_bars_by_period": {k: k}, "target_bp": 100.0}}


def test_r04_or_window_stop_entry():
    bars = [[10.0, 10.02, 9.98, 10.0], [10.0, 10.01, 9.99, 10.0]]  # OR 高=10.02
    bars.append([10.03, 10.04, 10.02, 10.03])  # bar2 突破 ⇒ stop 进入 fill=max(10.03,10.02)=10.03
    bars.append([10.05, 10.06, 10.04, 10.05])  # 触发 100bp 目标？10.03×1.01=10.1303>10.06 ⇒ 未触
    bars.append([10.30, 10.35, 10.29, 10.31])  # 触发
    df = make_day_frame(bars)
    fills, reason = eng.run_rule_r04(ml.resample_period(df, 1), _r04_card(2), 2)
    assert reason == "pair"
    assert fills["buy_price"] == pytest.approx(10.03)
    assert fills["sell_price"] == pytest.approx(max(10.30, 10.03 * 1.01))


def test_r04_no_breakout_and_no_or():
    # OR 高=10.01，窗口后各 bar high 9.99 严格低于 OR 高 ⇒ no_breakout（卡面 >=or_high 触发，等高即成交）
    bars = [[10.0, 10.02, 9.98, 10.0], [10.0, 10.01, 9.99, 10.0]]
    bars += [[9.99, 9.995, 9.98, 9.99]] * 4
    fills, reason = eng.run_rule_r04(ml.resample_period(make_day_frame(bars), 1), _r04_card(2), 2)
    assert reason == "no_breakout" and fills is None
    short = make_day_frame([[10.0, 10.01, 9.99, 10.0]] * 2)
    fills2, reason2 = eng.run_rule_r04(ml.resample_period(short, 1), _r04_card(2), 2)
    assert reason2 == "no_or" and fills2 is None


# ---------- 批次与预注册完整性 ----------


def test_plan_batches_deterministic():
    syms = [str(i).zfill(6) for i in range(0, 137)]
    b1 = eng.plan_batches(syms, 50)
    b2 = eng.plan_batches(list(reversed(syms)), 50)  # 禁随机：输入同集合输出同分批
    assert [sorted(x) for x in b1] == [sorted(x) for x in b2]
    assert sum(len(b) for b in b1) == 137 and len(b1) == 3


def test_rule_cards_prereg_integrity():
    """预注册完整性：4 卡在位、rule_id 一致、哈希可计算、R01 与材料线同参。"""
    for rid in ("r01", "r02", "r03", "r04"):
        card = eng.load_rule_card(CARDS_DIR, rid)
        assert card["rule_id"] == rid and len(card["_sha256"]) == 64
    r01 = eng.load_rule_card(CARDS_DIR, "r01")
    assert float(r01["params"]["grid_bp"]) == 100.0
    assert r01["execution"]["window"]["end"] == ml.CLOSED_BOOK_CUTOFF
    assert sha256_file(CARDS_DIR / "r01_fixed_grid_day_t.yaml") == r01["_sha256"]


def test_load_rule_card_missing_aborts(tmp_path):
    with pytest.raises(SystemExit):
        eng.load_rule_card(tmp_path, "r99")


def test_closed_book_inherited_from_material_line():
    with pytest.raises(SystemExit):
        ml.enforce_closed_book("2021-09-01", "2025-09-10")
