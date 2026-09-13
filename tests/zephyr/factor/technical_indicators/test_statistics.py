# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""统计族技术指标测试（5 个，2026-09-14 统计族批新建）。

测试内容：
- 5 个统计指标全部注册到 Registry（category=statistics）
- 每个指标 meta.output_columns == 期望列（catalog §2.6 契约）
- 数值正确性：CORREL 完全线性相关→±1；BETA x=y→1；LINEARREG/TSF 完美直线闭式对照；
  VAR 常数→0
- 边界：warmup NaN、空 DataFrame 短路、缺列抛 ValueError

口径对齐 TA-Lib Statistic Functions（CORREL/BETA/LINEARREG/TSF/VAR），VAR ddof=0。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.6
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import statistics  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

CORREL = TechnicalIndicatorRegistry.get("correl")
BETA = TechnicalIndicatorRegistry.get("beta")
LINEARREG = TechnicalIndicatorRegistry.get("linearreg")
ROLLVAR = TechnicalIndicatorRegistry.get("rollvar")

# 期望契约（catalog §2.6）：indicator_id → (name, output_columns)
EXPECTED = {
    "correl": ("滚动相关系数", ["correl_30"]),
    "beta": ("滚动beta系数", ["beta_30"]),
    "linearreg": ("线性回归线", ["linearreg_14", "tsf_14"]),
    "rollvar": ("滚动方差", ["var_20"]),
}


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正）。"""
    rng = np.random.default_rng(42)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + rng.uniform(0.1, 0.5, n)
    low = close - rng.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


# ===========================================================================
# 注册与元数据契约测试
# ===========================================================================


class TestStatisticsRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("statistics")}
        for iid in EXPECTED:
            assert iid in metas, f"统计指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("statistics")) == len(EXPECTED) == 4  # noqa: PLR2004

    def test_category(self):
        for m in TechnicalIndicatorRegistry.list_by_category("statistics"):
            assert m.category == "statistics"

    def test_meta_contract(self):
        for iid, (name, cols) in EXPECTED.items():
            meta = TechnicalIndicatorRegistry.get(iid).meta
            assert meta.name == name
            assert meta.output_columns == cols


# ===========================================================================
# 数值正确性测试
# ===========================================================================


class TestCorrelNumeric:
    def test_perfect_positive_correlation(self):
        df = _make_ohlcv(50)
        df["volume"] = 2.0 * df["close"]  # 完全线性相关 → r=1
        result = CORREL().compute(df)
        np.testing.assert_allclose(result["correl_30"].dropna(), 1.0, atol=1e-10)

    def test_perfect_negative_correlation(self):
        df = _make_ohlcv(50)
        df["volume"] = 2000.0 - df["close"]
        result = CORREL().compute(df)
        np.testing.assert_allclose(result["correl_30"].dropna(), -1.0, atol=1e-10)

    def test_warmup_nan(self):
        df = _make_ohlcv(50)
        df["volume"] = 2.0 * df["close"]  # 恒定 volume 零方差会产 inf，须用变 Volume 测预热
        result = CORREL().compute(df)
        assert result["correl_30"].iloc[:29].isna().all()
        assert result["correl_30"].iloc[29:].notna().all()


class TestBetaNumeric:
    def test_identical_series_beta_one(self):
        df = _make_ohlcv(50)
        df["volume"] = df["close"]  # x=y → beta=Cov/Var=1
        result = BETA().compute(df)
        np.testing.assert_allclose(result["beta_30"].dropna(), 1.0, atol=1e-10)

    def test_beta_times_variance_equals_covariance(self):
        df = _make_ohlcv(50)
        n = 30
        cov = df["close"].rolling(n).cov(df["volume"])
        var = df["volume"].rolling(n).var()
        beta = BETA().compute(df)["beta_30"]
        np.testing.assert_allclose(beta.dropna(), (cov / var).dropna(), rtol=1e-10)


class TestLinearRegNumeric:
    def test_perfect_line_fitted_value(self):
        """y=2+3x 完美直线：LINEARREG=当前值，TSF=当前值+3。"""
        n_rows, n = 30, 14
        close = 2 + 3 * np.arange(n_rows, dtype=float)
        df = pd.DataFrame({
            "open": close, "high": close, "low": close,
            "close": close, "volume": 1000.0,
        })
        result = LINEARREG().compute(df)
        valid = result["linearreg_14"].dropna()
        np.testing.assert_allclose(valid, close[13:], atol=1e-8)
        tsf = result["tsf_14"].dropna()
        np.testing.assert_allclose(tsf, close[13:] + 3.0, atol=1e-8)
        assert len(valid) == n_rows - 13

    def test_output_columns(self):
        result = LINEARREG().compute(_make_ohlcv(30))
        assert list(result.columns) == ["linearreg_14", "tsf_14"]

    def test_warmup_nan(self):
        result = LINEARREG().compute(_make_ohlcv(30))
        assert result["linearreg_14"].iloc[:13].isna().all()


class TestRollVarNumeric:
    def test_constant_zero_variance(self):
        df = _make_ohlcv(30)
        df["close"] = 100.0
        result = ROLLVAR().compute(df)
        assert (result["var_20"].dropna() == 0.0).all()

    def test_known_two_point_case(self):
        # 窗口 [1, 3]：mean=2，总体方差=((1-2)²+(3-2)²)/2=1
        close = pd.Series([5.0, 1.0, 3.0])
        df = pd.DataFrame({
            "open": close, "high": close, "low": close,
            "close": close, "volume": 1000.0,
        })
        result = ROLLVAR().compute(df, period=2)
        assert result["var_2"].iloc[2] == pytest.approx(1.0)


# ===========================================================================
# 边界与错误契约测试
# ===========================================================================


class TestStatisticsBoundaries:
    def test_empty_dataframe_short_circuit(self):
        for cls in (CORREL, BETA, LINEARREG, ROLLVAR):
            result = cls().compute(pd.DataFrame(columns=["open", "high", "low", "close", "volume"]))
            assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CORREL().compute(pd.DataFrame({"close": [1.0] * 40}))

    def test_index_aligned(self):
        df = _make_ohlcv(40)
        result = ROLLVAR().compute(df)
        assert (result.index == df.index).all()
