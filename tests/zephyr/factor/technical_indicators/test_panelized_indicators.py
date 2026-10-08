"""panelized_indicators 单元测试（st-mx07-L5 转正；纯合成数据，零 CH 依赖）。

对拍口径与 parity_check 一致：数值 |Δ|≤1e-9；NaN/None 模式全等。
生产参照实现（rolling.apply 逐窗回调）在此内联合成数据重写，验证向量化等价性。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import panelized_indicators as pi


@pytest.fixture()
def ohlcv() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    n = 260
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + np.abs(rng.normal(0, 0.5, n))
    low = close - np.abs(rng.normal(0, 0.5, n))
    open_ = np.concatenate([[close[0]], close[:-1]])
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)


# --- L2 window-vec 基元 vs 生产参照（rolling.apply 逐窗回调） -----------------


def test_wma_vec_equals_prod_reference(ohlcv):
    close = ohlcv["close"]
    n = 10
    ref = close.rolling(n).apply(lambda w: np.dot(w, np.arange(1, n + 1)) / np.arange(1, n + 1).sum(), raw=True)
    got = pi._wma_vec(close, n)
    np.testing.assert_allclose(got.to_numpy(), ref.to_numpy(), atol=1e-9, equal_nan=True)


def test_wma_vec_nan_window_propagates():
    s = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0])
    got = pi._wma_vec(s, 3)
    assert np.isnan(got.iloc[2]) and np.isnan(got.iloc[3])  # 含 NaN 窗不产出（min_periods 门）
    assert not np.isnan(got.iloc[-1])


def test_linreg_endpoint_vec_equals_closed_form(ohlcv):
    s = ohlcv["close"]
    length = 20
    ref = s.rolling(length).apply(
        lambda w: np.polyfit(np.arange(length), w, 1)[0] * (length - 1) + np.polyfit(np.arange(length), w, 1)[1],
        raw=True,
    )
    got = pi._linreg_endpoint_vec(s, length)
    np.testing.assert_allclose(got.to_numpy(), ref.to_numpy(), atol=1e-7, equal_nan=True)


def test_argpos_vec_first_extreme_and_nan_gate():
    s = pd.Series([3.0, 1.0, 1.0, 2.0, np.nan, 5.0, 1.0, 0.0, 2.0])
    got_max = pi._argpos_vec(s, 4, "max")
    # 窗 [1,1,2,NaN]（iloc[4]）/ [2,NaN,5,1]（iloc[6]）含 NaN → NaN（min_periods 门对齐）
    assert np.isnan(got_max.iloc[4]) and np.isnan(got_max.iloc[6])
    # 窗 [3,1,1,2]（iloc[3]）argmax=0；窗 [5,1,0,2]（iloc[8]）极值在窗首 argmax=0
    assert got_max.iloc[3] == 0.0
    assert got_max.iloc[8] == 0.0


def test_pctrank_vec_matches_reference(ohlcv):
    ret = ohlcv["close"].pct_change()
    n = 100
    ref = ret.rolling(n).apply(lambda w: (w[:-1] < w[-1]).sum() / (n - 1) * 100, raw=True)
    got = pi._pctrank_vec(ret, n)
    np.testing.assert_allclose(got.to_numpy(), ref.to_numpy(), atol=1e-9, equal_nan=True)


def test_swma_vec_matches_reference():
    s = pd.Series(np.arange(12, dtype=float))
    ref = s.rolling(4).apply(lambda w: np.dot(w, np.array([1.0, 2.0, 2.0, 1.0]) / 6.0), raw=True)
    got = pi._swma_vec(s)
    np.testing.assert_allclose(got.to_numpy(), ref.to_numpy(), atol=1e-12, equal_nan=True)


# --- L2 等价重实现指标（公式照抄生产的向量化段） -----------------------------


def test_cci_vec_shape_and_values(ohlcv):
    out = pi._cci_vec(ohlcv)
    assert list(out.columns) == ["cci_14"]
    assert len(out) == len(ohlcv)
    assert out["cci_14"].iloc[:13].isna().all()
    assert out["cci_14"].iloc[13:].notna().all()


def test_aroon_vec_range(ohlcv):
    out = pi._aroon_vec(ohlcv)
    assert list(out.columns) == ["aroon_up", "aroon_down"]
    body = out.iloc[14:]
    assert ((body >= 0) & (body <= 100)).all().all()


def test_rvgi_vec_columns(ohlcv):
    out = pi._rvgi_vec(ohlcv)
    assert list(out.columns) == ["rvgi_10", "rvgi_sig"]


# --- L3 materialize vs 生产 _build_row 逐格参照 ------------------------------


def _build_row_reference(bar_ts, symbol, period, row_data, columns):
    """生产 _build_row 的同逻辑参照（复制语义，不 import provider）。"""
    bar_dt = pd.Timestamp(bar_ts).to_pydatetime()
    row = []
    for col in columns:
        if col == "trade_date":
            row.append(bar_dt.date())
        elif col == "trade_time":
            row.append(bar_dt)
        elif col == "symbol":
            row.append(symbol)
        elif col == "period":
            row.append(period)
        elif col == "data_source":
            row.append("internal")
        else:
            val = row_data.get(col) if hasattr(row_data, "get") else None
            row.append(val if not (isinstance(val, float) and not np.isfinite(val)) else None)
    return tuple(row)


def test_materialize_rows_vectorized_equals_build_row(ohlcv):
    n = len(ohlcv)
    rng = np.random.default_rng(11)
    merged = pd.DataFrame(
        {
            "ma_5": ohlcv["close"].rolling(5).mean(),
            "w_3": ohlcv["close"].rolling(3).apply(np.dot, raw=True, args=(np.ones(3),)),
            "with_inf": np.where(rng.random(n) < 0.1, np.inf, ohlcv["close"]),
        },
        index=ohlcv.index,
    )
    columns = ["trade_date", "trade_time", "symbol", "period", "data_source", "ma_5", "w_3", "with_inf", "missing_col"]
    rows_ref = [_build_row_reference(ts, "000001", "daily", row, columns) for ts, row in merged.iterrows()]
    rows_vec = pi.materialize_rows_vectorized(merged, "000001", "daily", columns)
    assert len(rows_ref) == len(rows_vec) == n
    for t in range(n):
        for j, col in enumerate(columns):
            a, b = rows_ref[t][j], rows_vec[t][j]
            a_none = a is None or (isinstance(a, float) and not np.isfinite(a))
            b_none = b is None or (isinstance(b, float) and not np.isfinite(b))
            if a_none or b_none:
                assert a_none and b_none, f"row={t} col={col}: None 模式不一致 {a!r} vs {b!r}"
            elif isinstance(a, (int, float, np.floating)) and isinstance(b, (int, float, np.floating)):
                assert abs(float(a) - float(b)) <= 1e-9, f"row={t} col={col}: {a!r} vs {b!r}"
            else:
                assert a == b, f"row={t} col={col}: {a!r} vs {b!r}"


def test_materialize_empty_merged():
    assert pi.materialize_rows_vectorized(pd.DataFrame(), "000001", "daily", ["trade_date"]) == []


def test_patched_helpers_restore():
    """补丁必须还原（不污染生产模块态）。"""
    from zephyr.factor.technical_indicators import trend

    before = (trend._wma, trend._linreg_endpoint)
    with pi._PatchedHelpers():
        assert trend._wma is pi._wma_vec
        assert trend._linreg_endpoint is pi._linreg_endpoint_vec
    assert (trend._wma, trend._linreg_endpoint) == before
