# [BLUEPRINT] MOD-REGIME-006 | docs/03_modules/_domain_regime/regime_cycle_analyzer/blueprint.md | §8
# [TTL] permanent
# [MODULE] tests.regime.test_regime_cycle_analyzer
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pytest
# [CONSUMERS] MOD-REGIME-006(RegimeCycleAnalyzer 单测)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯合成数据零外部依赖（不连 ClickHouse）; 显著性用例以人造效应自证（非断言 A 股真实效应存在）
# [A_module] module_id=TST-REGIME-006 | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-REGIME-006 RegimeCycleAnalyzer 单元测试。

覆盖：月末/月初/节后日历标记、Welch 事件研究+Bonferroni、显著高低点识别、
周年日窗口、PIT 严格性、边界钉死（不显著→confidence=0/direction=neutral）、
确定性（同输入同输出）、数据不足异常（ZA-REGIME-0030）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.regime_cycle_analyzer import (
    ANNIVERSARY_TOLERANCE,
    MONTH_EDGE_K,
    N_HYPOTHESES,
    RegimeCycleAnalyzer,
    RegimeCycleError,
    anniversary_windows,
    confidence_from_p_adj,
    detect_swing_extremes,
    event_study,
    trading_day_features,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_ohlc(close: np.ndarray, start: str = "2020-01-01") -> pd.DataFrame:
    """合成 OHLC（business day 日历）。"""
    dates = pd.bdate_range(start=start, periods=len(close))
    return pd.DataFrame({"close": close}, index=dates)


@pytest.fixture
def planted_month_end_effect() -> pd.DataFrame:
    """人造月末效应：每月最后 2 个交易日收益 +0.8%，其余 N(0, 0.8%)。"""
    rng = np.random.default_rng(7)
    n = 3 * 252
    dates = pd.bdate_range(start="2020-01-01", periods=n)
    rets = rng.normal(0.0, 0.008, n)
    feats = trading_day_features(pd.DatetimeIndex(dates))
    rets[feats["is_month_end"].to_numpy()] += 0.008
    close = 10.0 * np.exp(np.cumsum(rets))
    return pd.DataFrame({"close": close}, index=dates)


@pytest.fixture
def pure_noise() -> pd.DataFrame:
    """纯随机游走（无任何效应）。"""
    rng = np.random.default_rng(11)
    rets = rng.normal(0.0, 0.008, 3 * 252)
    close = 10.0 * np.exp(np.cumsum(rets))
    return _make_ohlc(close)


# ---------------------------------------------------------------------------
# 日历结构标记
# ---------------------------------------------------------------------------


class TestTradingDayFeatures:
    def test_month_end_flags_last_k_days(self) -> None:
        dates = pd.bdate_range("2024-01-01", periods=60)
        feats = trading_day_features(pd.DatetimeIndex(dates))
        # 2024-01 最后交易日 01-31(周三)、前一交易日 01-30
        assert feats.loc[pd.Timestamp("2024-01-31"), "is_month_end"]
        assert feats.loc[pd.Timestamp("2024-01-30"), "is_month_end"]
        assert not feats.loc[pd.Timestamp("2024-01-29"), "is_month_end"]

    def test_month_start_flags_first_k_days(self) -> None:
        dates = pd.bdate_range("2024-03-01", periods=40)
        feats = trading_day_features(pd.DatetimeIndex(dates))
        assert feats.loc[pd.Timestamp("2024-03-01"), "is_month_start"]
        assert feats.loc[pd.Timestamp("2024-03-04"), "is_month_start"]
        assert not feats.loc[pd.Timestamp("2024-03-05"), "is_month_start"]

    def test_month_edge_counts(self) -> None:
        dates = pd.bdate_range("2020-01-01", periods=3 * 252)
        feats = trading_day_features(pd.DatetimeIndex(dates))
        n_months = len(pd.DatetimeIndex(dates).to_period("M").unique())
        assert feats["is_month_end"].sum() == n_months * MONTH_EDGE_K
        assert feats["is_month_start"].sum() == n_months * MONTH_EDGE_K

    def test_post_holiday_flag_after_long_gap(self) -> None:
        # 注入 9 自然日长假（模拟春节/国庆）
        dates = pd.DatetimeIndex(
            list(pd.bdate_range("2024-01-01", periods=30))
            + list(pd.bdate_range("2024-02-19", periods=30))
        )
        feats = trading_day_features(dates)
        gap_day = dates[30]
        assert (gap_day - dates[29]).days >= 5
        assert feats.loc[gap_day, "is_post_holiday"]
        # 普通周末间隔（3 天）不触发
        normal_days = feats.index[(feats["gap_days"] == 3)]
        assert not feats.loc[normal_days, "is_post_holiday"].any()

    def test_empty_calendar_raises(self) -> None:
        with pytest.raises(RegimeCycleError):
            trading_day_features(pd.DatetimeIndex([]))


# ---------------------------------------------------------------------------
# 事件研究 + Bonferroni
# ---------------------------------------------------------------------------


class TestEventStudy:
    def test_significant_effect_detected(self) -> None:
        rng = np.random.default_rng(3)
        metric = pd.Series(rng.normal(0.0, 0.01, 500))
        mask = pd.Series(False, index=metric.index)
        mask.iloc[::10] = True
        metric.loc[mask] += 0.02  # 人造 +2% 效应
        ev = event_study(metric, mask, n_hypotheses=N_HYPOTHESES)
        assert ev.significant
        assert ev.confidence == 1.0
        assert ev.p_adj <= 0.01

    def test_noise_not_significant(self) -> None:
        rng = np.random.default_rng(5)
        metric = pd.Series(rng.normal(0.0, 0.01, 500))
        mask = pd.Series(False, index=metric.index)
        mask.iloc[::10] = True
        ev = event_study(metric, mask, n_hypotheses=N_HYPOTHESES)
        assert not ev.significant
        assert ev.confidence == 0.0

    def test_bonferroni_correction(self) -> None:
        rng = np.random.default_rng(9)
        metric = pd.Series(rng.normal(0.0, 0.01, 500))
        mask = pd.Series(False, index=metric.index)
        mask.iloc[::7] = True
        ev = event_study(metric, mask, n_hypotheses=4)
        assert ev.p_adj == pytest.approx(min(1.0, ev.p_value * 4))

    def test_min_n_guard(self) -> None:
        metric = pd.Series(np.linspace(-0.01, 0.01, 100))
        mask = pd.Series(False, index=metric.index)
        mask.iloc[:5] = True  # 5 < MIN_EVENTS
        ev = event_study(metric, mask)
        assert not ev.significant
        assert ev.confidence == 0.0
        assert ev.n_events == 5

    def test_confidence_mapping(self) -> None:
        assert confidence_from_p_adj(0.005) == 1.0
        assert confidence_from_p_adj(0.03) == 0.6
        assert confidence_from_p_adj(0.08) == 0.3
        assert confidence_from_p_adj(0.5) == 0.0


# ---------------------------------------------------------------------------
# 显著高低点 + 周年日窗口
# ---------------------------------------------------------------------------


class TestAnniversary:
    def test_detect_swing_extremes_v_shape(self) -> None:
        # 人造 V 形：上涨 → 显著低点（跌幅 >20%）→ 反弹
        n = 120
        close = np.full(n, 100.0)
        close[:40] = np.linspace(100, 130, 40)   # 涨到 130
        close[40:70] = np.linspace(130, 95, 30)  # 跌到 95（振幅 >20%）
        close[70:] = np.linspace(95, 120, 50)    # 反弹
        df = detect_swing_extremes(_make_ohlc(close)["close"])
        kinds = set(df["kind"])
        assert "high" in kinds or "low" in kinds
        # 极值价格应接近 130 / 95
        prices = set(df["price"].round(0))
        assert 130.0 in prices or 95.0 in prices

    def test_flat_series_no_extremes(self) -> None:
        close = np.full(100, 10.0) + np.linspace(0, 0.5, 100)  # 微涨，无 20% 波段
        df = detect_swing_extremes(pd.Series(close, index=pd.bdate_range("2024-01-01", periods=100)))
        assert df.empty

    def test_unconfirmed_tail_extreme_rejected(self) -> None:
        # 末端 10 日急涨（右窗未满 → 未确认极值不采信）
        close = np.concatenate([np.full(90, 100.0), np.linspace(100, 140, 10)])
        df = detect_swing_extremes(_make_ohlc(close)["close"], lookback=20)
        # 末端高点右窗未满，不得收录
        assert df.empty or df["date"].max() < _make_ohlc(close).index[-1]

    def test_anniversary_windows_tolerance(self) -> None:
        extremes = pd.DataFrame(
            {"date": [pd.Timestamp("2023-03-15")], "kind": ["high"], "price": [130.0]}
        )
        wins = anniversary_windows(extremes, tolerance=ANNIVERSARY_TOLERANCE, max_years=2)
        first = wins.iloc[0]
        assert first["start"] == pd.Timestamp("2024-03-15") - pd.Timedelta(days=5)
        assert first["end"] == pd.Timestamp("2024-03-15") + pd.Timedelta(days=5)
        assert first["kind"] == "anniversary_high"
        assert set(wins["year_offset"]) == {1, 2}


# ---------------------------------------------------------------------------
# 编排器：显著性自证 / 边界钉死 / PIT / 确定性 / 异常
# ---------------------------------------------------------------------------


class TestAnalyzer:
    def test_planted_month_end_significant(self, planted_month_end_effect: pd.DataFrame) -> None:
        result = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of="2022-12-15")
        ev = result.evidence_table["month_end"]
        assert ev.significant
        assert ev.confidence > 0.0

    def test_noise_no_significant_windows(self, pure_noise: pd.DataFrame) -> None:
        result = RegimeCycleAnalyzer().analyze(pure_noise, as_of="2022-12-15")
        for ev in result.evidence_table.values():
            assert not ev.significant

    def test_boundary_nail_non_significant(self, pure_noise: pd.DataFrame) -> None:
        """边界钉死：统计不显著窗口 confidence=0.0 且 direction=neutral。"""
        result = RegimeCycleAnalyzer().analyze(pure_noise, as_of="2022-12-15")
        for window in (*result.active_windows, *result.upcoming_windows):
            assert window.confidence == 0.0
            assert window.direction == "neutral"
        assert result.is_advisory_only

    def test_active_window_on_month_end(self, planted_month_end_effect: pd.DataFrame) -> None:
        idx = planted_month_end_effect.index
        feats = trading_day_features(idx)
        me_days = idx[(feats["is_month_end"]) & (idx >= "2022-06-01") & (idx <= "2022-06-30")]
        assert len(me_days) > 0
        result = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of=me_days[0])
        active_kinds = {w.window_kind for w in result.active_windows}
        assert "month_end" in active_kinds
        me_window = next(w for w in result.active_windows if w.window_kind == "month_end")
        assert me_window.cycle_id == "CYC-STAT-013"

    def test_pit_no_future_leak(self, planted_month_end_effect: pd.DataFrame) -> None:
        """PIT 严格：as_of=t 的分析结果与"截断到 t 的历史"分析结果一致。"""
        as_of = "2021-06-15"
        full = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of=as_of)
        truncated = planted_month_end_effect[planted_month_end_effect.index <= as_of]
        part = RegimeCycleAnalyzer().analyze(truncated, as_of=as_of)
        assert full.evidence_table.keys() == part.evidence_table.keys()
        for key in full.evidence_table:
            f_ev = full.evidence_table[key]
            p_ev = part.evidence_table[key]
            assert f_ev.n_events == p_ev.n_events
            assert f_ev.p_adj == pytest.approx(p_ev.p_adj)

    def test_determinism(self, planted_month_end_effect: pd.DataFrame) -> None:
        r1 = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of="2022-12-15")
        r2 = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of="2022-12-15")
        assert r1.to_dict() == r2.to_dict()

    def test_to_dict_serializable(self, planted_month_end_effect: pd.DataFrame) -> None:
        result = RegimeCycleAnalyzer().analyze(planted_month_end_effect, as_of="2022-12-15")
        d = result.to_dict()
        assert d["as_of"] == "2022-12-15"
        assert set(d["evidence_table"]) == {"month_end", "month_start", "post_holiday", "anniversary"}
        assert d["is_advisory_only"]

    def test_insufficient_data_raises(self) -> None:
        short = _make_ohlc(np.linspace(10, 11, 30))
        with pytest.raises(RegimeCycleError, match="数据不足"):
            RegimeCycleAnalyzer().analyze(short, as_of="2020-03-01")

    def test_missing_close_raises(self) -> None:
        bad = pd.DataFrame({"open": [1.0] * 100}, index=pd.bdate_range("2024-01-01", periods=100))
        with pytest.raises(RegimeCycleError, match="close"):
            RegimeCycleAnalyzer().analyze(bad, as_of="2024-06-01")

    def test_date_column_input_accepted(self, planted_month_end_effect: pd.DataFrame) -> None:
        df = planted_month_end_effect.reset_index(names="date")
        result = RegimeCycleAnalyzer().analyze(df, as_of="2022-12-15")
        assert result.evidence_table["month_end"].significant
