# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""统计族技术指标测试（9 个指标/10 输出列，2026-09-14 统计族批新建；
2026-09-20 回归扩展批新增 LINEARREG_ANGLE/SLOPE/INTERCEPT/STDERR，
批2-C 清欠班新增 ZSCORE）。

测试内容：
- 9 个统计指标全部注册到 Registry（category=statistics）
- 每个指标 meta.output_columns == 期望列（catalog §2.6 契约）
- 数值正确性：CORREL 完全线性相关→±1；BETA x=y→1；LINEARREG/TSF 完美直线闭式对照；
  VAR 常数→0；ZSCORE 手工微样本+独立逐窗复算（批2-C 清欠班）
- 黄金样本（回归扩展批）：200 根种子几何随机游走 vs TA-Lib 全序列精确容差比对
  （LINEARREG_SLOPE/LINEARREG_INTERCEPT/LINEARREG_ANGLE）；STDERR 与逐窗
  numpy.polyfit 独立 OLS 残差标准误对照（talib 0.7.1 无 STDERR）
- 手工微样本：5 根已知收盘价手算 slope/intercept/angle/stderr 写死数值断言
- 边界：warmup NaN、空 DataFrame 短路、缺列抛 ValueError、kwargs 覆盖 period 列名后缀

口径对齐 TA-Lib Statistic Functions（CORREL/BETA/LINEARREG/TSF/VAR），VAR ddof=0。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.6
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.technical_indicators import statistics  # noqa: F401 — 注册副作用
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

talib = pytest.importorskip("talib")  # 仅测试参照，生产代码零 TA-Lib 依赖（本机 0.7.1 无 STDERR，见黄金样本类）

CORREL = TechnicalIndicatorRegistry.get("correl")
BETA = TechnicalIndicatorRegistry.get("beta")
LINEARREG = TechnicalIndicatorRegistry.get("linearreg")
ROLLVAR = TechnicalIndicatorRegistry.get("rollvar")
LINEARREG_ANGLE = TechnicalIndicatorRegistry.get("linearreg_angle")
SLOPE = TechnicalIndicatorRegistry.get("slope")
INTERCEPT = TechnicalIndicatorRegistry.get("intercept")
STDERR = TechnicalIndicatorRegistry.get("stderr")
ZSCORE = TechnicalIndicatorRegistry.get("zscore")

# 期望契约（catalog §2.6）：indicator_id → (name, output_columns)
EXPECTED = {
    "correl": ("滚动相关系数", ["correl_30"]),
    "beta": ("滚动beta系数", ["beta_30"]),
    "linearreg": ("线性回归线", ["linearreg_14", "tsf_14"]),
    "rollvar": ("滚动方差", ["var_20"]),
    "linearreg_angle": ("线性回归角度", ["linearreg_angle_14"]),
    "slope": ("线性回归斜率", ["slope_14"]),
    "intercept": ("线性回归截距", ["intercept_14"]),
    "stderr": ("回归标准误差", ["stderr_14"]),
    "zscore": ("滚动Z分数", ["zscore_20"]),
}


def _make_ohlcv(n: int = 50) -> pd.DataFrame:
    """生成带趋势的 OHLCV 测试数据（价格始终为正）。"""
    rng = np.random.default_rng(42)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + rng.uniform(0.1, 0.5, n)
    low = close - rng.uniform(0.1, 0.5, n)
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 1000.0})


def _df_from_close(close: np.ndarray) -> pd.DataFrame:
    """由 close 数组构造齐列 OHLCV DataFrame（黄金样本/微样本共用）。"""
    close = np.asarray(close, dtype=float)
    return pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1, "close": close, "volume": 1000.0})


# ===========================================================================
# 注册与元数据契约测试
# ===========================================================================


class TestStatisticsRegistered:
    def test_all_registered(self):
        metas = {m.indicator_id: m for m in TechnicalIndicatorRegistry.list_by_category("statistics")}
        for iid in EXPECTED:
            assert iid in metas, f"统计指标 '{iid}' 未注册"

    def test_count(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("statistics")) == len(EXPECTED) == 9  # noqa: PLR2004

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
        df = pd.DataFrame(
            {
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 1000.0,
            }
        )
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
        df = pd.DataFrame(
            {
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 1000.0,
            }
        )
        result = ROLLVAR().compute(df, period=2)
        assert result["var_2"].iloc[2] == pytest.approx(1.0)


# ===========================================================================
# 回归扩展批（2026-09-20）：黄金样本对照 + 手工微样本
# ===========================================================================


def _make_golden_close(n: int = 200) -> np.ndarray:
    """黄金对照样本：200 根种子合成几何随机游走收盘价（default_rng(7)）。"""
    rng = np.random.default_rng(7)
    return 100.0 * np.exp(0.02 * rng.standard_normal(n).cumsum())


class TestRegressionGoldenVsTalib:
    """黄金样本：200 根种子几何随机游走全序列精确容差对照（预热段两侧均 NaN）。

    本机 talib 0.7.1 无 SLOPE/INTERCEPT/STDERR 短名与 STDERR 函数（TA-Lib C 全集
    只有 LINEARREG_SLOPE/LINEARREG_INTERCEPT/LINEARREG_ANGLE），故前三列对照
    LINEARREG_* 同名函数；STDERR 黄金参照改为逐窗 numpy.polyfit 独立 OLS 残差
    标准误（与生产闭式解是完全独立的算法路径）。
    """

    n_rows, n = 200, 14

    @classmethod
    def setup_class(cls):
        cls.close = _make_golden_close(cls.n_rows)
        cls.df = _df_from_close(cls.close)

    def _checked_valid_mask(self, mine: pd.Series, ref: pd.Series) -> pd.Series:
        mask = pd.notna(mine) & pd.notna(ref)
        assert mask.sum() == self.n_rows - (self.n - 1)  # 预热段两侧一致为 NaN
        return mask

    def test_slope_matches_talib(self):
        mine = SLOPE().compute(self.df)["slope_14"]
        ref = pd.Series(talib.LINEARREG_SLOPE(self.close, timeperiod=self.n), index=self.df.index)
        mask = self._checked_valid_mask(mine, ref)
        assert np.allclose(mine[mask], ref[mask], rtol=1e-8, atol=1e-8)

    def test_intercept_matches_talib(self):
        mine = INTERCEPT().compute(self.df)["intercept_14"]
        ref = pd.Series(talib.LINEARREG_INTERCEPT(self.close, timeperiod=self.n), index=self.df.index)
        mask = self._checked_valid_mask(mine, ref)
        assert np.allclose(mine[mask], ref[mask], rtol=1e-8, atol=1e-8)

    def test_angle_matches_talib(self):
        mine = LINEARREG_ANGLE().compute(self.df)["linearreg_angle_14"]
        ref = pd.Series(talib.LINEARREG_ANGLE(self.close, timeperiod=self.n), index=self.df.index)
        mask = self._checked_valid_mask(mine, ref)
        assert np.allclose(mine[mask], ref[mask], rtol=1e-8, atol=1e-8)

    def test_stderr_matches_independent_ols(self):
        mine = STDERR().compute(self.df)["stderr_14"]
        x = np.arange(self.n, dtype=float)
        ref = np.full(self.n_rows, np.nan)
        for t in range(self.n - 1, self.n_rows):
            win = self.close[t - self.n + 1 : t + 1]
            b, a = np.polyfit(x, win, 1)  # 独立 OLS 路径，不复用生产闭式解
            resid = win - (a + b * x)
            ref[t] = np.sqrt((resid**2).sum() / (self.n - 2))
        ref = pd.Series(ref, index=self.df.index)
        mask = self._checked_valid_mask(mine, ref)
        assert np.allclose(mine[mask], ref[mask], rtol=1e-8, atol=1e-8)


class TestRegressionHandComputed:
    """手工微样本：close=[1,2,3,2,5]、x=0..4、period=5 的手算口径钉死（非纯对拍）。

    手算：Σx=10，Σx²=30，Σy=13，Σxy=34，Σy²=43，denom=5·30−10²=50
      b=(5·34−10·13)/50=0.8；a=(13−0.8·10)/5=1.0
      angle=degrees(atan(0.8))=38.6598082540901°
      SSR=Σy²−a·Σy−b·Σxy=43−13−27.2=2.8 → stderr=sqrt(2.8/3)=0.9660917830792954
    """

    @classmethod
    def _df(cls) -> pd.DataFrame:
        return _df_from_close(np.array([1.0, 2.0, 3.0, 2.0, 5.0]))

    def test_slope_hand_computed(self):
        result = SLOPE().compute(self._df(), period=5)
        assert result["slope_5"].iloc[:4].isna().all()  # 预热期仅末根有效
        assert result["slope_5"].iloc[4] == pytest.approx(0.8)

    def test_intercept_hand_computed(self):
        result = INTERCEPT().compute(self._df(), period=5)
        assert result["intercept_5"].iloc[4] == pytest.approx(1.0)

    def test_angle_hand_computed(self):
        result = LINEARREG_ANGLE().compute(self._df(), period=5)
        assert result["linearreg_angle_5"].iloc[4] == pytest.approx(38.6598082540901)

    def test_stderr_hand_computed(self):
        result = STDERR().compute(self._df(), period=5)
        assert result["stderr_5"].iloc[4] == pytest.approx(0.9660917830792954)


# ===========================================================================
# 边界与错误契约测试
# ===========================================================================


class TestStatisticsBoundaries:
    def test_empty_dataframe_short_circuit(self):
        for cls in (CORREL, BETA, LINEARREG, ROLLVAR, LINEARREG_ANGLE, SLOPE, INTERCEPT, STDERR, ZSCORE):
            result = cls().compute(pd.DataFrame(columns=["open", "high", "low", "close", "volume"]))
            assert result.empty

    def test_missing_column_raises(self):
        with pytest.raises(ValueError, match="缺少列"):
            CORREL().compute(pd.DataFrame({"close": [1.0] * 40}))

    def test_missing_close_raises_regression_family(self):
        for cls in (LINEARREG_ANGLE, SLOPE, INTERCEPT, STDERR, ZSCORE):
            with pytest.raises(ValueError, match="缺少列"):
                cls().compute(pd.DataFrame({"volume": [1.0] * 40}))

    def test_regression_warmup_nan(self):
        """前 13 根（index 0..12）预热 NaN，第 14 根（index 13）起全有效且 index 对齐。"""
        df = _make_ohlcv(30)
        for cls, col in (
            (LINEARREG_ANGLE, "linearreg_angle_14"),
            (SLOPE, "slope_14"),
            (INTERCEPT, "intercept_14"),
            (STDERR, "stderr_14"),
        ):
            result = cls().compute(df)
            assert result[col].iloc[:13].isna().all(), cls
            assert result[col].iloc[13:].notna().all(), cls
            assert (result.index == df.index).all()

    def test_period_kwarg_renames_column(self):
        """kwargs 覆盖 period=20 后列名带 period 后缀（与 linearreg_14 参数化语义一致）。"""
        df = _make_ohlcv(30)
        assert list(SLOPE().compute(df, period=20).columns) == ["slope_20"]
        assert list(INTERCEPT().compute(df, period=20).columns) == ["intercept_20"]
        assert list(LINEARREG_ANGLE().compute(df, period=20).columns) == ["linearreg_angle_20"]
        assert list(STDERR().compute(df, period=20).columns) == ["stderr_20"]
        slope20 = SLOPE().compute(df, period=20)["slope_20"]
        assert slope20.iloc[:19].isna().all()
        assert slope20.iloc[19:].notna().all()

    def test_regression_output_columns(self):
        result = SLOPE().compute(_make_ohlcv(30))
        assert list(result.columns) == ["slope_14"]

    def test_index_aligned(self):
        df = _make_ohlcv(40)
        result = ROLLVAR().compute(df)
        assert (result.index == df.index).all()


# ===========================================================================
# 批2-C 清欠班（2026-09-20）：ZSCORE 数值正确性
# ===========================================================================


class TestZscoreNumeric:
    """ZSCORE 滚动标准分——数值正确性 + 边界测试（ddof=0 与 BOLL 中轨 std 口径一致）。"""

    def test_zscore_hand_computed(self):
        """手工微样本：close=[1,2,6,3,7]、period=3 逐窗手算写死。

        win[0..2]=[1,2,6]: mean=3, var=14/3 → z=(6−3)/sqrt(14/3)=3/sqrt(14/3)
        win[1..3]=[2,6,3]: mean=11/3, var=26/9 → z=(3−11/3)/(sqrt(26)/3)=−2/sqrt(26)
        win[2..4]=[6,3,7]: mean=16/3, var=26/9 → z=(7−16/3)/(sqrt(26)/3)=5/sqrt(26)
        """
        df = _df_from_close(np.array([1.0, 2.0, 6.0, 3.0, 7.0]))
        result = ZSCORE().compute(df, period=3)
        assert result["zscore_3"].iloc[:2].isna().all()
        assert result["zscore_3"].iloc[2] == pytest.approx(3.0 / np.sqrt(14.0 / 3.0))
        assert result["zscore_3"].iloc[3] == pytest.approx(-2.0 / np.sqrt(26.0))
        assert result["zscore_3"].iloc[4] == pytest.approx(5.0 / np.sqrt(26.0))

    def test_zscore_independent_recompute(self):
        """独立逐窗循环复算对照（numpy 标量路径，非生产 rolling 向量化）。"""
        n_rows, n = 60, 20
        df = _make_ohlcv(n_rows)
        result = ZSCORE().compute(df)
        c = df["close"].to_numpy()
        expected = np.full(n_rows, np.nan)
        for t in range(n - 1, n_rows):
            win = c[t - n + 1 : t + 1]
            expected[t] = (win[-1] - win.mean()) / win.std()  # numpy std 默认 ddof=0
        np.testing.assert_allclose(result["zscore_20"].values, expected, rtol=1e-10, atol=1e-12)

    def test_zscore_warmup_nan_and_alignment(self):
        """默认 period=20：前 19 根预热 NaN，第 20 根起全有效，index 对齐。"""
        df = _make_ohlcv(30)
        result = ZSCORE().compute(df)
        assert result["zscore_20"].iloc[:19].isna().all()
        assert result["zscore_20"].iloc[19:].notna().all()
        assert (result.index == df.index).all()

    def test_zscore_period_kwarg_renames_column(self):
        """kwargs 覆盖 period=10 后列名 zscore_N（预热窗随之收缩）。"""
        df = _make_ohlcv(30)
        result = ZSCORE().compute(df, period=10)
        assert list(result.columns) == ["zscore_10"]
        assert result["zscore_10"].iloc[:9].isna().all()
        assert result["zscore_10"].iloc[9:].notna().all()
