"""kline_sector_intraday_from_constituents 纯函数核测（聚合数学/桶 OHLC/停牌填充/边界跳过）。"""

import sys
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, r"D:/ZephyrAlpha/scripts/data")

from kline_sector_intraday_from_constituents import (  # noqa: E402
    MIN_MEMBERS,
    bucket_ohlc,
    build_board_rows,
    compute_board_1m,
)

T0 = datetime(2026, 9, 29, 9, 30, 0)


def _grid(n):
    return [T0 + pd.Timedelta(minutes=i) for i in range(n)]


def test_chain_two_members():
    idx = _grid(4)
    # 成员A: 100→110→99→99；成员B: 200→200→220→220；成员C 平盘做权重锚
    sub = pd.DataFrame(
        {"A": [100.0, 110.0, 99.0, 99.0], "B": [200.0, 200.0, 220.0, 220.0], "C": [50.0, 50.0, 50.0, 50.0]}, index=idx
    )
    path = compute_board_1m(sub)
    assert path is not None
    # 基点=首分钟等权均价=(100+200+50)/3≈116.667
    assert np.isclose(path.iloc[0], 350.0 / 3.0)
    # 第2分钟: A +10%、B/C 0% → 均值 +10/3 % → 基点×(1+1/30)
    assert np.isclose(path.iloc[1], (350.0 / 3.0) * (1 + 1 / 30.0))
    # 第3分钟: A -10%、B +10%、C 0% → 0% → 路径不变
    assert np.isclose(path.iloc[2], path.iloc[1])


def test_suspension_ffill_zero_return():
    idx = _grid(4)
    # 成员A第3分钟缺格（停牌）→ 前向填充收益0；C 平盘锚
    sub = pd.DataFrame(
        {"A": [100.0, 110.0, np.nan, 120.0], "B": [100.0, 100.0, 100.0, 100.0], "C": [100.0, 100.0, 100.0, 100.0]},
        index=idx,
    )
    path = compute_board_1m(sub)
    # 第3分钟: A ffill=110 → 0%，B/C 0% → 路径不变
    assert np.isclose(path.iloc[2], path.iloc[1])
    # 第4分钟: A 110→120 = +9.09%，B/C 0% → 均值 +9.09%/3
    assert np.isclose(path.iloc[3], path.iloc[1] * (1 + (120.0 / 110.0 - 1) / 3), rtol=1e-3)


def test_too_few_members_skipped():
    idx = _grid(4)
    sub = pd.DataFrame({"A": [1.0, 2.0, 3.0, 4.0]}, index=idx)
    assert compute_board_1m(sub) is None


def test_bucket_ohlc_five_minutes():
    idx = _grid(6)
    path = pd.Series([100.0, 102.0, 101.0, 105.0, 103.0, 104.0], index=idx)
    vol = pd.Series([10, 20, 30, 40, 50, 60], index=idx)
    df = bucket_ohlc(path, 5, vol_1m=vol)
    assert len(df) == 2
    first, second = df.iloc[0], df.iloc[1]
    assert np.isclose(first["open"], 100.0) and np.isclose(first["close"], 103.0)
    assert np.isclose(first["high"], 105.0) and np.isclose(first["low"], 100.0)
    assert first["volume"] == 10 + 20 + 30 + 40 + 50
    assert np.isclose(second["open"], 104.0) and np.isclose(second["close"], 104.0)


def test_build_board_rows_all_periods():
    idx = _grid(12)
    rng = np.random.default_rng(7)
    sub = pd.DataFrame(rng.uniform(9.0, 11.0, size=(12, 5)), index=idx, columns=list("ABCDE"))
    vol = pd.DataFrame(np.ones((12, 5), dtype="int64"), index=idx, columns=list("ABCDE"))
    amt = pd.DataFrame(np.full((12, 5), 100.0), index=idx, columns=list("ABCDE"))
    rows = build_board_rows("880301.SH", sub, vol, amt)
    periods = {r[2] for r in rows}
    assert periods == {"1m", "5m", "15m", "30m", "60m"}
    # 每行 data_source=internal_eqw；code 后缀码
    assert all(r[9] == "internal_eqw" and r[1] == "880301.SH" for r in rows)
    # 5m 桶数 = ceil(12/5) = 3
    assert sum(1 for r in rows if r[2] == "5m") == 3


def test_min_members_constant():
    assert MIN_MEMBERS == 3
