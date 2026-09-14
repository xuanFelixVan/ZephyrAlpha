# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_candlestick_scanner.py
# [MODULE] tests.signal_ashare.test_candlestick_scanner
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.candlestick_scanner; zephyr.signal_ashare.strategy_signal.pattern_event_store
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 合成 OHLC 数据，禁触 CH/生产路径
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_candlestick_scanner.py
# [TTL] permanent
"""candlestick_scanner 单测（P2-a）——CDL 包装/A股 extras/行契约闭环。"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from zephyr.signal_ashare.strategy_signal.candlestick_scanner import (
    _cdl_functions,
    scan_candles,
)
from zephyr.signal_ashare.strategy_signal.pattern_event_store import build_event_rows


def _df(rows):
    return pd.DataFrame(
        rows, columns=["trade_date", "open", "high", "low", "close"]
    )


def _flat_rows(n=20, price=10.0):
    """n 根平静无事件小K线（不漂移：开10.00/收10.01/高10.02/低9.99）。"""
    rows = []
    for i in range(n):
        rows.append((date(2026, 1, 1) + pd.Timedelta(days=i), 10.00, 10.02, 9.99, 10.01))
    return rows


def test_cdl_functions_has_61():
    fns = _cdl_functions()
    assert len(fns) == 61
    assert "CDLHAMMER" in fns and "CDLENGULFING" in fns


def test_hammer_detected_bullish():
    # 先造 6 根下跌（TA-Lib CDLHAMMER 需要下跌趋势上下文），尾部锤子：长下影、小实体、微上影
    rows = []
    p = 10.40
    for i in range(14):
        o = p
        c = round(p - 0.05, 2)
        rows.append((date(2026, 1, 1) + pd.Timedelta(days=i), o, round(o + 0.03, 2), round(c - 0.03, 2), c))
        p = c
    rows.append((date(2026, 1, 21), 9.64, 9.66, 9.00, 9.65))  # 锤子（上影≤实体）
    events = scan_candles("600519", _df(rows))
    hits = [e for e in events if e["pattern_id"] == "CDLHAMMER"]
    assert hits, "CDLHAMMER 未检出"
    assert hits[-1]["direction"] == "向上"


def test_engulfing_detected():
    rows = _flat_rows(20, 10.0)
    # 阴线后超大阳线吞没
    rows[-1] = (date(2026, 1, 20), 10.02, 10.06, 9.98, 9.99)  # 阴
    rows.append((date(2026, 1, 21), 9.97, 10.30, 9.96, 10.28))  # 吞没阳
    events = scan_candles("600519", _df(rows))
    assert any(e["pattern_id"] == "CDLENGULFING" and e["direction"] == "向上" for e in events)


def test_limit_up_flat_ashare():
    rows = _flat_rows(20, 10.0)
    pc = rows[-1][4]
    lim = round(pc * 1.10, 2)
    rows.append((date(2026, 1, 21), lim, lim, lim, lim))  # 一字涨停
    events = scan_candles("600519", _df(rows))
    hits = [e for e in events if e["pattern_id"] == "X-一字涨停板"]
    assert hits and hits[-1]["direction"] == "向上"


def test_nr7_is_neutral():
    # 前 19 根振幅 0.05+，最后一根振幅 0.02 → NR7 命中且方向中性
    rows = _flat_rows(19, 10.0)
    rows.append((date(2026, 1, 20), 10.02, 10.06, 9.98, 10.03))
    rows.append((date(2026, 1, 21), 10.02, 10.04, 10.02, 10.03))
    events = scan_candles("600519", _df(rows))
    hits = [e for e in events if e["pattern_id"] == "X-窄幅整理日"]
    assert hits and hits[-1]["direction"] == "中性"


def test_key_reversal_bearish():
    rows = _flat_rows(20, 10.0)
    prev_c = rows[-1][4]
    rows.append((date(2026, 1, 21), 10.05, 10.40, 10.02, 9.90))  # 新高但收破前收
    events = scan_candles("600519", _df(rows))
    hits = [e for e in events if e["pattern_id"] == "X-关键反转日"]
    assert hits and hits[-1]["direction"] == "向下"
    _ = prev_c


def test_missing_column_raises():
    with pytest.raises(ValueError, match="缺少必需列"):
        scan_candles("600519", pd.DataFrame({"open": [1], "high": [1], "low": [1]}))


def test_rows_pass_store_closed_set():
    rows = _flat_rows(20, 10.0)
    rows.append((date(2026, 1, 21), 10.02, 10.05, 9.30, 10.03))
    events = scan_candles("600519", _df(rows))
    built = build_event_rows(events[:5], data_source="candle_scanner")
    assert len(built) == 5  # pattern_class=K线 在封闭集内，全部通过校验


def test_deterministic_same_input_same_events():
    rows = _flat_rows(20, 10.0)
    rows.append((date(2026, 1, 21), 10.02, 10.05, 9.30, 10.03))
    a = scan_candles("600519", _df(rows))
    b = scan_candles("600519", _df(rows))
    keys_a = {(e["pattern_id"], e["anchor_trade_date"], e["direction"]) for e in a}
    keys_b = {(e["pattern_id"], e["anchor_trade_date"], e["direction"]) for e in b}
    assert keys_a == keys_b


# ---------------------------------------------------------------------------
# 2026-09-15 件8：Bulkowski 小形态 6 条（PAT-CANDLE-078..083）合成向量单测
# ---------------------------------------------------------------------------

import numpy as np

from zephyr.signal_ashare.strategy_signal.candlestick_scanner import _EXTRA_RULES


def _run_rule(name, o, h, l, c):
    fn, _pid = _EXTRA_RULES[name]
    arr = [np.asarray(x, dtype=np.float64) for x in (o, h, l, c)]
    pc = np.concatenate(([np.nan], arr[3][:-1]))
    return fn(*arr, pc)


def test_inside_days_neutral():
    o = [10.0, 10.2]
    h = [11.0, 10.8]  # h < 前高
    l = [9.0, 9.5]  # l > 前低
    c = [10.5, 10.4]
    _bull, _bear, neutral = _run_rule("内包日", o, h, l, c)
    assert neutral[0].sum() == 1 and neutral[0][1]
    # 非内包：高低任一破前日即 False
    o2 = [10.0, 10.2, 10.2]
    h2 = [11.0, 10.8, 10.9]  # 破前高 → 非内包
    l2 = [9.0, 9.5, 9.6]
    c2 = [10.5, 10.4, 10.4]
    _b, _s, neutral2 = _run_rule("内包日", o2, h2, l2, c2)
    assert neutral2[0][2] is np.False_ or not neutral2[0][2]


def test_weekly_reversal_bullish_new_low_close_up():
    # 12 根缓跌 + 第 13 根创新低但收阳
    o = list(np.linspace(12, 9.0, 12)) + [8.0]
    c = list(np.linspace(11.9, 8.9, 12)) + [8.2]
    h = [x + 0.1 for x in o]
    l = [x - 0.1 for x in c]
    l[-1] = 7.5  # 创 12 窗新低
    c[-1] = 8.2
    o[-1] = 8.0
    h[-1] = 8.3
    bull, bear, _n = _run_rule("周线反转", o, h, l, c)
    assert bull[0][-1] and not bear[0][-1]


def test_open_close_reversal_bullish_pair():
    # 背景 3 根 + bar1 长阴（开近高收近低）+ bar2 长阳（开近低收近高、收破 bar1 收盘）
    o = [12.0, 11.8, 11.6, 10.9, 10.2]
    h = [12.1, 11.9, 11.7, 11.0, 11.2]
    l = [11.7, 11.5, 11.3, 10.0, 10.1]
    c = [11.8, 11.6, 11.4, 10.1, 11.1]
    bull, bear, _n = _run_rule("开收反转", o, h, l, c)
    assert bull[0][4] and not bear[0][4]


def test_hook_reversal_bearish():
    # 前日 H=11/C=10.5；当日跳空开 11.2（>前高）、收 10.4（<前收）→ HRD 向下
    o = [10.0, 10.6, 11.2]
    h = [10.5, 11.0, 11.3]
    l = [9.9, 10.4, 10.3]
    c = [10.2, 10.5, 10.4]
    bull, bear, _n = _run_rule("钩形反转", o, h, l, c)
    assert bear[0][2] and not bull[0][2]
    assert not bear[0][1]  # 首日无前日，不触发


def test_pivot_point_reversal_bullish():
    # 前日 H=11/L=9；当日 L=8.8（创新低）收 11.1（穿越前日高）→ PPRU 向上
    o = [10.0, 10.2, 9.0]
    h = [11.0, 10.8, 11.2]
    l = [9.0, 9.2, 8.8]
    c = [10.8, 10.5, 11.1]
    bull, bear, _n = _run_rule("枢轴点反转", o, h, l, c)
    assert bull[0][2] and not bear[0][2]


def test_shark32_trigger_breaks_setup_high():
    # 三连跌 + Setup bar（开收近低）+ 次日收盘破 Setup 高
    o = [11.0, 10.9, 10.7, 10.5, 10.30, 10.45]
    h = [11.1, 11.0, 10.8, 10.6, 10.60, 10.80]
    l = [10.9, 10.75, 10.55, 10.35, 10.30, 10.40]
    c = [10.95, 10.8, 10.6, 10.4, 10.35, 10.70]
    bull, bear, _n = _run_rule("鲨鱼32", o, h, l, c)
    assert bull[0][5], "触发 bar=收盘破 Setup 高"
    assert bear == ()  # 单向形态：无 bear 组


def test_new_rules_emit_via_scan_candles():
    # 端到端：内包日经 scan_candles 产出 X-内包日 事件（中性）
    rows = [
        (date(2026, 1, 5), 10.0, 11.0, 9.0, 10.5),
        (date(2026, 1, 6), 10.2, 10.8, 9.5, 10.4),
    ]
    events = scan_candles("600519", _df(rows))
    inside = [e for e in events if e["pattern_id"] == "X-内包日"]
    assert len(inside) == 1 and inside[0]["direction"] == "中性"
