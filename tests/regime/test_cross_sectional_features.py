# [BLUEPRINT] MOD-REGIME-007 | 待统筹登记
# [MODULE] tests.regime.test_cross_sectional_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pytest; zephyr.regime.cross_sectional_features; zephyr.regime.regime_feature_builder
# [CONSUMERS] 无(测试模块)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全部合成面板确定性种子;PIT截断断言(T日特征不含T+1信息);开关关=输出逐字节回归
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] 自测
# [A_module] module_id=TST-REGIME-007 | layer=test | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-007 横截面结构特征单元测试（ALG-01）。

覆盖：
  - 4 特征已知答案合成截面（全同涨跌 → 离散度=0；半数强于 MA20 → 宽度=50%；
    全同收益 → 平均相关=1；独立收益 → 相关≈0；已知截面 std 精确值）；
  - 无前视偏差：T 截断面板特征 = 全面板前 T 日特征（shift 断言，多切点）；
  - NaN 纪律：截面 <30 只该日全 NaN；个股缺数据该日剔除不填补；
  - 抽样确定性：同一面板两次计算逐字节一致；
  - builder 开关：关 = 输出与现状逐字节一致；开 = 尾部追加 4 列，前 6 列值不变。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.cross_sectional_features import (
    CROSS_SECTIONAL_FEATURE_NAMES,
    CrossSectionalFeatureError,
    compute_cross_sectional_features,
)
from zephyr.regime.regime_feature_builder import (
    FEATURE_NAMES,
    RegimeFeatureBuilder,
    RegimeFeatureError,
)

# ---------------------------------------------------------------------------
# 面板构造工具
# ---------------------------------------------------------------------------


def _make_panel(
    close_map: dict[str, np.ndarray],
    dates: pd.DatetimeIndex,
    *,
    amount: float = 1e8,
) -> pd.DataFrame:
    """由 {symbol: close 数组} 构造长表面板（确定性）。"""
    rows = []
    for s, closes in close_map.items():
        assert len(closes) == len(dates)
        for d, c in zip(dates, closes, strict=True):
            rows.append((d, s, c, 1e6, amount))
    return pd.DataFrame(rows, columns=["trade_date", "symbol", "close", "volume", "amount"])


def _random_panel(n_days: int = 200, n_syms: int = 60, seed: int = 7) -> pd.DataFrame:
    """独立随机游走面板（确定性种子）。"""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-01-01", periods=n_days)
    close_map = {}
    for i in range(n_syms):
        close_map[f"S{i:03d}"] = 10.0 * np.exp(np.cumsum(rng.normal(0, 0.01, n_days)))
    # 流动性差异化（分层抽样用）：确定性递减成交额
    rows = []
    for i, (s, closes) in enumerate(close_map.items()):
        for d, c in zip(dates, closes, strict=True):
            rows.append((d, s, c, 1e6, 1e8 * (n_syms - i)))
    return pd.DataFrame(rows, columns=["trade_date", "symbol", "close", "volume", "amount"])


# ---------------------------------------------------------------------------
# 输出结构 / 列序 / 确定性
# ---------------------------------------------------------------------------


class TestOutputSchema:
    def test_column_order_pinned(self):
        out = compute_cross_sectional_features(_random_panel())
        assert list(out.columns) == CROSS_SECTIONAL_FEATURE_NAMES
        assert out.index.is_monotonic_increasing

    def test_deterministic_same_panel_same_output(self):
        panel = _random_panel()
        a = compute_cross_sectional_features(panel)
        b = compute_cross_sectional_features(panel)
        pd.testing.assert_frame_equal(a, b)

    def test_multiindex_panel_accepted(self):
        panel = _random_panel(n_days=80, n_syms=40).set_index(["trade_date", "symbol"])
        out = compute_cross_sectional_features(panel)
        assert list(out.columns) == CROSS_SECTIONAL_FEATURE_NAMES


# ---------------------------------------------------------------------------
# 已知答案合成截面
# ---------------------------------------------------------------------------


class TestKnownAnswers:
    def test_all_same_movement_dispersion_and_corr(self):
        """全部个股同涨跌 → 离散度=0、波动率离散=0、平均相关=1。"""
        n_days = 120
        dates = pd.bdate_range("2024-01-01", periods=n_days)
        rng = np.random.default_rng(11)
        rets = rng.normal(0.0005, 0.012, n_days)
        px = 10.0 * np.exp(np.cumsum(rets))
        panel = _make_panel({f"S{i:03d}": px for i in range(40)}, dates)

        out = compute_cross_sectional_features(panel)
        disp = out["cross_dispersion"].dropna()
        assert len(disp) > 0 and (disp.abs() < 1e-12).all()
        vd = out["vol_dispersion"].dropna()
        assert len(vd) > 0 and (vd.abs() < 1e-9).all()
        corr = out["avg_pairwise_corr"].dropna()
        assert len(corr) > 0 and np.allclose(corr, 1.0, atol=1e-8)

    def test_independent_returns_corr_near_zero(self):
        """独立随机收益 → 平均成对相关 ≈ 0。"""
        out = compute_cross_sectional_features(_random_panel(n_days=200, n_syms=60))
        corr = out["avg_pairwise_corr"].dropna()
        assert len(corr) > 0
        assert (corr.abs() < 0.2).all()

    def test_half_above_ma20_breadth_50(self):
        """半数收盘强于 MA20 → 动量宽度 = 50%。"""
        n_days = 21
        dates = pd.bdate_range("2024-01-01", periods=n_days)
        close_map = {}
        for i in range(30):
            px = np.full(n_days, 10.0)
            px[-1] = 11.0 if i < 15 else 9.0  # 15 只跳升(>MA20)，15 只跳水(<MA20)
            close_map[f"S{i:03d}"] = px
        out = compute_cross_sectional_features(_make_panel(close_map, dates))
        assert out["momentum_breadth"].iloc[-1] == pytest.approx(50.0)

    def test_std_method_known_value(self):
        """std 口径已知答案：截面收益 ±1%/±2% 对称 → 精确 std。"""
        n_days = 30
        dates = pd.bdate_range("2024-01-01", periods=n_days)
        # 前 29 日平坦，末日 4 组各 10 只收益 -2%/-1%/+1%/+2%
        close_map = {}
        for g, r in enumerate([-0.02, -0.01, 0.01, 0.02]):
            for k in range(10):
                px = np.full(n_days, 10.0)
                px[-1] = 10.0 * (1 + r)
                close_map[f"G{g}S{k:02d}"] = px
        out = compute_cross_sectional_features(
            _make_panel(close_map, dates),
            dispersion_method="std",
            dispersion_smooth_window=1,  # 关平滑，直接看末日截面 std
        )
        expected = np.std([-0.02] * 10 + [-0.01] * 10 + [0.01] * 10 + [0.02] * 10, ddof=1)
        assert out["cross_dispersion"].iloc[-1] == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# PIT：无前视偏差（截断断言）
# ---------------------------------------------------------------------------


class TestNoLookahead:
    @pytest.mark.parametrize("cut", [80, 120, 160])
    def test_truncated_panel_equals_full_prefix(self, cut: int):
        """T 截断面板的特征须与全面板前 T 日逐字节一致（T 日特征不含 T+1 信息）。"""
        panel = _random_panel(n_days=200, n_syms=60)
        dates = sorted(panel["trade_date"].unique())
        cut_date = dates[cut]
        full = compute_cross_sectional_features(panel)
        trunc = compute_cross_sectional_features(panel[panel["trade_date"] <= cut_date])
        prefix = full.loc[:cut_date]
        pd.testing.assert_frame_equal(prefix, trunc)


# ---------------------------------------------------------------------------
# NaN 纪律
# ---------------------------------------------------------------------------


class TestNaNDiscipline:
    def test_below_min_cs_names_all_nan(self):
        """截面 20 只（<30）→ 4 列全部 NaN。"""
        out = compute_cross_sectional_features(_random_panel(n_days=120, n_syms=20))
        assert out.isna().all().all()

    def test_missing_data_excluded_not_filled(self):
        """个股缺 1 日收盘 → 该日及次日收益剔除（不填补）→ 截面 29<30 该日 NaN。"""
        n_days = 100
        panel = _random_panel(n_days=n_days, n_syms=30)
        dates = sorted(panel["trade_date"].unique())
        gap_day = dates[60]
        victim = panel["symbol"].iloc[0]
        panel.loc[(panel["trade_date"] == gap_day) & (panel["symbol"] == victim), "close"] = np.nan

        out = compute_cross_sectional_features(panel, dispersion_method="std", dispersion_smooth_window=1)
        # 缺口日 + 次日（pct_change 需前收）截面只剩 29 只 → NaN；若被填补则为非 NaN
        assert pd.isna(out["cross_dispersion"].loc[gap_day])
        assert pd.isna(out["cross_dispersion"].loc[dates[61]])
        # 远离缺口的正常日为非 NaN
        assert pd.notna(out["cross_dispersion"].loc[dates[80]])


# ---------------------------------------------------------------------------
# 输入校验
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_empty_panel_raises(self):
        with pytest.raises(CrossSectionalFeatureError):
            compute_cross_sectional_features(pd.DataFrame())

    def test_missing_close_col_raises(self):
        bad = pd.DataFrame({"trade_date": ["2024-01-02"], "symbol": ["S1"]})
        with pytest.raises(CrossSectionalFeatureError):
            compute_cross_sectional_features(bad)

    def test_bad_method_raises(self):
        with pytest.raises(CrossSectionalFeatureError):
            compute_cross_sectional_features(_random_panel(n_days=40, n_syms=35), dispersion_method="mad")


# ---------------------------------------------------------------------------
# builder 开关：关 = 逐字节回归；开 = 尾部追加
# ---------------------------------------------------------------------------


def _make_index_kline(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """合成指数 K 线（000300/000905/399006/399106），MultiIndex(symbol, trade_date)。"""
    rng = np.random.default_rng(3)
    frames = []
    for s in ["000300", "000905", "399006", "399106"]:
        n = len(dates)
        close = 4000.0 * np.exp(np.cumsum(rng.normal(0, 0.008, n)))
        frames.append(
            pd.DataFrame(
                {
                    "symbol": s,
                    "trade_date": dates,
                    "open": close,
                    "high": close * 1.01,
                    "low": close * 0.99,
                    "close": close,
                    "volume": 1e9,
                    "advance_count": 900.0,
                    "decline_count": 700.0,
                }
            )
        )
    return pd.concat(frames).set_index(["symbol", "trade_date"]).sort_index()


def _make_builder(dates: pd.DatetimeIndex, **kwargs) -> RegimeFeatureBuilder:
    b = RegimeFeatureBuilder(
        backtest_start=str(dates[0].date()),
        backtest_end=str(dates[-1].date()),
        data_load_start=str(dates[0].date()),
        **kwargs,
    )
    index_df = _make_index_kline(dates)
    b.get_index_kline = lambda: index_df  # type: ignore[method-assign]  # 离线注入，免 CH
    return b


class TestBuilderSwitch:
    def test_switch_off_byte_identical(self):
        """开关关（默认）输出与未传新参的 builder 逐字节一致，列序 = FEATURE_NAMES。"""
        dates = pd.bdate_range("2024-01-01", periods=140)
        a = _make_builder(dates).build_features()
        b = _make_builder(dates, enable_cross_sectional=False).build_features()
        pd.testing.assert_frame_equal(a, b)
        assert list(a.columns) == FEATURE_NAMES

    def test_switch_on_appends_tail(self):
        """开关开：列序 = FEATURE_NAMES + 4 列（尾部），前 6 列值与开关关逐字节一致。"""
        dates = pd.bdate_range("2024-01-01", periods=140)
        panel = _random_panel(n_days=140, n_syms=40)
        panel["trade_date"] = pd.DatetimeIndex(panel["trade_date"]).map(
            lambda d: dates[min(np.searchsorted(dates, d), len(dates) - 1)]
        )  # 对齐到 builder 日期轴
        off = _make_builder(dates, enable_cross_sectional=False).build_features()
        on = _make_builder(dates, enable_cross_sectional=True, cross_sectional_panel=panel).build_features()
        assert list(on.columns) == FEATURE_NAMES + CROSS_SECTIONAL_FEATURE_NAMES
        pd.testing.assert_frame_equal(on[FEATURE_NAMES], off[FEATURE_NAMES])

    def test_active_feature_names(self):
        dates = pd.bdate_range("2024-01-01", periods=140)
        assert _make_builder(dates).active_feature_names() == FEATURE_NAMES
        assert _make_builder(dates, enable_cross_sectional=True).active_feature_names() == (
            FEATURE_NAMES + CROSS_SECTIONAL_FEATURE_NAMES
        )


# ---------------------------------------------------------------------------
# ALG2-2 复权腿：真源指向 + 失维绊线（红队车道 st-ff-rb-pit-20260918 攻面二）
#
# 现场实证（2026-09-18，本机 CH 只读）：c1_market.adj_factor 专表日行数 2026-07-03
# 前 ~7,470 → 07-06 起 2~60；服务端 join_use_nulls=0 且该列 Decimal(18,8) 非
# Nullable ⇒ LEFT JOIN 未命中填 0 而非 NULL ⇒ 旧 SQL 的 ifNull(...,nan) 永不触发，
# close_hfq 实为 0 价（面板 31.7% 的行），C1/C2/C3 全 NaN、C4 报 0.07%（真值 28%）。
# 下列三件断言各自锁死一处防线，任一处回退即红。
# ---------------------------------------------------------------------------


def _panel_with_hfq(days: int, per_day: int, hfq_ratio: float) -> pd.DataFrame:
    """构造 days×per_day 长表，close_hfq 按 hfq_ratio 比例给正价、其余填 0（塌缩复刻）。"""
    rng = np.random.default_rng(20260918)
    dates = pd.bdate_range("2026-08-03", periods=days)
    rows = []
    for d in dates:
        for i in range(per_day):
            price = float(rng.uniform(5, 50))
            hfq = price * 1.1 if rng.random() < hfq_ratio else 0.0
            rows.append((d, f"{i:06d}", price, 1e6, 1e8, hfq))
    return pd.DataFrame(rows, columns=["trade_date", "symbol", "close", "volume", "amount", "close_hfq"])


class TestStockPanelAdjustmentSource:
    def test_zero_fill_collapse_must_raise(self):
        """复权塌缩（0 价占绝大多数）必须硬失败，不得带 0 价出特征。"""
        dates = pd.bdate_range("2026-08-03", periods=30)
        b = _make_builder(dates, enable_cross_sectional=True)
        panel = _panel_with_hfq(days=30, per_day=20, hfq_ratio=0.005)
        with pytest.raises(RegimeFeatureError, match="复权覆盖率"):
            b._assert_hfq_coverage(panel)

    def test_healthy_coverage_passes_silently(self):
        """覆盖率达标（>50%）时绊线不动作。"""
        dates = pd.bdate_range("2026-08-03", periods=30)
        b = _make_builder(dates, enable_cross_sectional=True)
        panel = _panel_with_hfq(days=30, per_day=20, hfq_ratio=0.97)
        b._assert_hfq_coverage(panel)  # 不抛 = 通过

    def test_sql_points_at_hfq_truth_and_guards_zero(self):
        """面板 SQL 必须读后复权真值表，且把非正复权价显式置 NULL（不靠 ifNull 拦 0）。"""
        dates = pd.bdate_range("2026-08-03", periods=30)
        b = _make_builder(dates, enable_cross_sectional=True)
        captured: dict[str, str] = {}

        def _fake_query(sql: str, context: str) -> str:
            captured["sql"] = sql
            body = [
                f"2026-08-03\t000001\t10.0\t1000\t1e7\t11.0",
                "2026-08-03\t000002\t12.0\t1000\t1e7\t\\N",
            ]
            return "\n".join(body) + "\n"

        b._safe_query = _fake_query  # type: ignore[method-assign]  # 离线注入，免 CH
        df = b._load_stock_panel()
        sql = captured["sql"]
        assert "kline_daily_hfq" in sql, "复权源必须指向后复权真值表 kline_daily_hfq"
        assert "c1_market.adj_factor" not in sql and "market_adj_factor" not in sql, (
            "禁再读 adj_factor 专表当整窗乘子（日覆盖已塌缩到 2~60 行）"
        )
        assert "ifNull(a.adj_factor" not in sql, "ifNull 拦不住 join 未命中的 0 填充（join_use_nulls=0）"
        assert "> 0" in sql and "NULL" in sql, "非正复权价必须显式 NULL 化"
        assert float(df["close_hfq"].iloc[0]) == pytest.approx(11.0)
        assert pd.isna(df["close_hfq"].iloc[1]), "CH 侧 NULL 必须落成 NaN（被截面剔除而非当 0 用）"

    def test_loader_wires_the_tripwire(self):
        """绊线必须挂在 _load_stock_panel 上：面板全 0 复权价时加载即失败。"""
        dates = pd.bdate_range("2026-08-03", periods=30)
        b = _make_builder(dates, enable_cross_sectional=True)

        def _zero_tsv(sql: str, context: str) -> str:
            lines = [f"2026-08-0{i + 3}\t00000{j}\t10.0\t1000\t1e7\t0" for i in range(5) for j in range(4)]
            return "\n".join(lines) + "\n"

        b._safe_query = _zero_tsv  # type: ignore[method-assign]  # 离线注入，免 CH
        with pytest.raises(RegimeFeatureError, match="复权覆盖率"):
            b._load_stock_panel()


