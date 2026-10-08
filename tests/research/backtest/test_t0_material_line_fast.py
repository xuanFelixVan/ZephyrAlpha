# [MODULE] tests.research.backtest.test_t0_material_line_fast
# [DOMAIN] D_BACKTEST
# [TTL] task_bound
"""t0_material_line_fast 单测（构造数据纯函数面，禁真库/禁写 data/，输出走 tmp_path）。

对拍口径：fast 核 vs legacy run_model_m0/resample_period 逐位相等（float 输入契约下
== 全等，非容差）。覆盖：M0 触发/成交价/末日强平/除零挡/one_bar/low_bars/no_touch/
重采样分桶/reason 优先级/numba 与 numpy 兜底同读数/规范化语义缝/确定性。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _p in (
    str(_REPO_ROOT / "scripts"),
    str(_REPO_ROOT / "scripts" / "backtest"),
    str(_REPO_ROOT / "scripts" / "audit"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import t0_material_line as t0m  # noqa: E402
import t0_material_line_fast as fast  # noqa: E402

GRID_BP = 100.0
NOTIONAL = 100_000.0
MIN_BARS = t0m.MIN_BARS_BY_PERIOD[1]


def _day_df(lows, highs, opens, closes, base_time="2025-08-07 09:30:00", volumes=None):
    n = len(lows)
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame(
        {
            "trade_time": [f"{base_time[:10]} {9 + i // 60:02d}:{i % 60:02d}:00" for i in range(n)],
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
    )


def _legacy_loop(bars: pd.DataFrame, periods, grid_bp, notional, run_id):
    """与 parity harness 同构的 legacy 循环（构造数据基准）。"""
    grouped = bars.groupby(["symbol", "trade_date"], sort=True)
    fills_by: dict[str, list[dict]] = {}
    reasons_by: dict[str, dict[str, int]] = {}
    for period in periods:
        fills_all: list[dict] = []
        reason_counts: dict[str, int] = {}
        for (symbol, trade_date), day_bars in grouped:
            day_bars = day_bars.sort_values("trade_time")
            fills, reason = t0m.build_corpus_for_symbol_day(
                str(symbol), str(trade_date), day_bars, period, grid_bp, notional, run_id
            )
            fills_all.extend(fills)
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        fills_by[f"{period}min"] = fills_all
        reasons_by[f"{period}min"] = reason_counts
    return fills_by, reasons_by


def _corpus(periods=(1, 5)):
    return {"periods": list(periods), "grid_bp": GRID_BP, "notional": NOTIONAL, "run_id": "test-fast"}


def _assert_bitwise_equal(bars: pd.DataFrame, periods) -> None:
    cfg = _corpus(periods)
    lf, lr = _legacy_loop(bars, cfg["periods"], cfg["grid_bp"], cfg["notional"], cfg["run_id"])
    ff, fr, n_days, _eng = fast.build_corpus_fast(
        bars, cfg["periods"], cfg["grid_bp"], cfg["notional"], cfg["run_id"], t0m.MIN_BARS_BY_PERIOD
    )
    n_expected = bars.groupby(["symbol", "trade_date"], sort=True).ngroups
    assert n_days == n_expected
    for label in (f"{p}min" for p in cfg["periods"]):
        assert lr[label] == fr[label], f"{label} reason_counts: {lr[label]} != {fr[label]}"
        assert lf[label] == ff[label], f"{label} fills 逐位不等"


def _synthetic_bars(n_days: int = 12, seed: int = 7, day_bars: int = 24) -> pd.DataFrame:
    """构造多 symbol-day 语料：价格走势混合触档/不触档/末日强平/低 bar 数等形态。"""
    rng = np.random.default_rng(seed)
    rows = []
    for d in range(n_days):
        symbol = "600000" if d % 2 == 0 else "300577"
        date = f"2025-08-{1 + d:02d}"
        base = 20.0 + 0.3 * d
        for i in range(day_bars if d % 11 != 0 else 3):  # d%11==0 → 低 bar 数日（low_bars）
            drift = rng.normal(0, 0.05)
            o = round(base + drift, 2)
            c = round(o + rng.normal(0, 0.08), 2)
            h = round(max(o, c) + abs(rng.normal(0, 0.06)), 2)
            low = round(min(o, c) - abs(rng.normal(0, 0.15)), 2)
            if low <= 0:
                low = 0.01
            rows.append((symbol, date, f"{date} {9 + i // 60:02d}:{i % 60:02d}:00", o, h, low, c, 1000.0 + i))
    return pd.DataFrame(rows, columns=["symbol", "trade_date", "trade_time", "open", "high", "low", "close", "volume"])


class TestBitwiseParity:
    def test_synthetic_corpus_bitwise_all_periods(self):
        bars = _synthetic_bars()
        _assert_bitwise_equal(bars, [1, 5, 15, 30, 60])

    def test_forced_close_day_bitwise(self):
        # 买后永不触卖 → 末日强平（legacy=fast 同读数）
        bars = _synthetic_bars(n_days=1, day_bars=240)
        _assert_bitwise_equal(bars, [1])

    def test_zero_price_guard(self):
        bars = _synthetic_bars(n_days=3)
        bad = bars.index[bars["low"] <= 0]
        assert bad.empty
        zero_day = bars["trade_date"] == bars["trade_date"].iloc[0]
        bars.loc[zero_day, "low"] = 0.0  # 注入零价日（除零契约）
        _assert_bitwise_equal(bars, [1])


class TestReasonPrecedence:
    @staticmethod
    def _single_day(lows, highs, opens, closes) -> pd.DataFrame:
        df = _day_df(lows, highs, opens, closes)
        df.insert(0, "trade_date", "2025-08-07")
        df.insert(0, "symbol", "600000")
        return df

    def test_one_bar_day(self):
        bars = self._single_day([20.0], [20.2], [20.1], [20.05])
        _f, fr, _n, _e = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        assert fr["1min"] == {"one_bar": 1}

    def test_low_bars_day(self):
        n = 10  # <200 → low_bars
        bars = self._single_day([20.0] * n, [20.2] * n, [20.1] * n, [20.05] * n)
        _f, fr, _n, _e = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        assert fr["1min"] == {"low_bars": 1}

    def test_no_touch_day(self):
        n = 240  # 整日 low 抬在 base 之上 → no_touch
        bars = self._single_day([21.5] * n, [22.0] * n, [21.0] * n, [21.6] * n)
        _f, fr, _n, _e = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        assert fr["1min"] == {"no_touch": 1}


class TestResampleArrays:
    def test_bucket_ohlc_semantics(self):
        bars = _synthetic_bars(n_days=1, day_bars=10)
        _s, _d, day_start, day_len = fast.segment_days(bars)
        r = fast.resample_arrays(bars, day_start, day_len, 5)
        legacy = t0m.resample_period(bars, 5)
        assert np.array_equal(r["r_open"], legacy["open"].to_numpy(dtype=float))
        assert np.array_equal(r["r_high"], legacy["high"].to_numpy(dtype=float))
        assert np.array_equal(r["r_low"], legacy["low"].to_numpy(dtype=float))
        assert np.array_equal(r["r_close"], legacy["close"].to_numpy(dtype=float))
        assert list(r["r_time"]) == list(legacy["trade_time"].to_numpy())

    def test_period_identity(self):
        bars = _synthetic_bars(n_days=2, day_bars=6)
        _s, _d, day_start, day_len = fast.segment_days(bars)
        r = fast.resample_arrays(bars, day_start, day_len, 1)
        assert np.array_equal(r["r_open"], bars["open"].to_numpy(dtype=float))
        assert np.array_equal(r["res_day_start"], day_start)

    def test_invalid_period(self):
        bars = _synthetic_bars(n_days=1, day_bars=4)
        _s, _d, day_start, day_len = fast.segment_days(bars)
        with pytest.raises(ValueError, match="period"):
            fast.resample_arrays(bars, day_start, day_len, 0)


class TestKernelBackends:
    def test_numba_and_numpy_same_reads(self):
        bars = _synthetic_bars(n_days=10, day_bars=40)
        _s, _d, day_start, day_len = fast.segment_days(bars)
        arrs = fast.resample_arrays(bars, day_start, day_len, 5)
        args = (
            arrs["r_open"],
            arrs["r_high"],
            arrs["r_low"],
            arrs["r_close"],
            arrs["res_day_start"],
            arrs["res_day_len"],
            GRID_BP,
            MIN_BARS,
        )
        r_numba, bi_n, bf_n, si_n, sf_n, k1 = fast.m0_scan(*args)
        assert k1 == "numba_prange"
        r_numpy, bi_x, bf_x, si_x, sf_x = fast._m0_scan_numpy(*args)
        assert np.array_equal(r_numba, r_numpy)
        assert np.array_equal(bi_n, bi_x)
        assert np.array_equal(bf_n, bf_x)
        assert np.array_equal(si_n, si_x)
        assert np.array_equal(sf_n, sf_x)

    def test_determinism_repeat_runs(self):
        bars = _synthetic_bars(n_days=8, day_bars=30)
        a = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        b = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        assert a[0] == b[0] and a[1] == b[1]


class TestNormalizeSeam:
    def test_decimal_input_matches_float_input(self):
        # 语义缝：Decimal 输入经规范化后与 float 输入逐位同读数
        from decimal import Decimal

        bars = _synthetic_bars(n_days=2, day_bars=20)
        dec = bars.copy()
        for c in ("open", "high", "low", "close"):
            dec[c] = dec[c].map(Decimal)
        norm = fast.normalize_prices_float64(dec)
        assert str(norm["low"].dtype) == "float64"
        a = fast.build_corpus_fast(norm, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        b = fast.build_corpus_fast(bars, [1], GRID_BP, NOTIONAL, "t", t0m.MIN_BARS_BY_PERIOD)
        assert a[0] == b[0] and a[1] == b[1]

    def test_float_passthrough_no_copy_semantics(self):
        bars = _synthetic_bars(n_days=1, day_bars=6)
        out = fast.normalize_prices_float64(bars)
        assert out["low"].tolist() == bars["low"].tolist()
