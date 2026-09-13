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
