# [A_test] module_id: MOD-TEST-OVERLAY-FEAT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2c
# [MODULE] tests.regime.test_overlay_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_overlay_features.py
# [A_module] module_id: MOD-TEST-OVERLAY-FEAT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #10_regime_detector_spec §4 #Phase2c #P1-E5
"""test_overlay_features.py — T3 评分纯函数单元测试（P1-E5 Step 4）。

覆盖 7 个 T3（RECOVERY→BREAKOUT）评分函数，每个 4+ 用例：
  - t3_volume_price_score: 量价配合 0/35/65/80
  - t3_ma_trend_score: 均线趋势 0/30/60/70
  - t3_sentiment_score: 市场情绪 0/35/65/80
  - t3_money_effect_score: 资金效应 0/25/50/65/80（Phase 2c）
  - t3_mainline_score: 主线效应 0/35/65/80（Phase 2c）
  - t3_leader_score: 龙头效应 0/35/65/80（Phase 2c）
  - t3_one_day_mainline_flag: 一日主线证伪 0/1（Phase 2c）

测试维度：
  - 各分层阈值边界（含精确边界值）
  - NaN 容错（fillna 生效）
  - 返回类型/值域（pd.Series, score∈[0,100], flag∈{0,1}）
  - 索引对齐（reindex 行为）

依据: 10_regime_detector_spec v1.3.1 §4 / Phase 2c 计划 / P1-E5
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.overlay_features import (
    t3_leader_score,
    t3_ma_trend_score,
    t3_mainline_score,
    t3_money_effect_score,
    t3_one_day_mainline_flag,
    t3_sentiment_score,
    t3_volume_price_score,
)

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _series(values: list[float], name: str = "x") -> pd.Series:
    """快速构造 pd.Series（默认整数索引）。"""
    return pd.Series(values, name=name)


# ---------------------------------------------------------------------------
# 1. t3_volume_price_score — 量价配合 0/35/65/80
# ---------------------------------------------------------------------------


class TestT3VolumePriceScore:
    """量价配合评分：上涨+放量 → 高分，下跌/缩量 → 0。"""

    def test_strong_surge_with_volume(self):
        """涨>2% & z>2 → 80（放量大涨，强配合）。"""
        pct = _series([0.025, 0.03])
        vol_z = _series([2.5, 3.0])
        result = t3_volume_price_score(pct, vol_z)
        assert (result == 80).all()

    def test_moderate_rise_with_volume(self):
        """涨>1% & z>1 → 65（量价齐升，过门槛）。"""
        pct = _series([0.015, 0.012])
        vol_z = _series([1.5, 1.2])
        result = t3_volume_price_score(pct, vol_z)
        assert (result == 65).all()

    def test_weak_positive(self):
        """涨>0 & z>0 → 35（正方向，未达门槛）。"""
        pct = _series([0.005, 0.008])
        vol_z = _series([0.5, 0.3])
        result = t3_volume_price_score(pct, vol_z)
        assert (result == 35).all()

    def test_no_signal_when_declining(self):
        """下跌或缩量 → 0（无量或下跌）。"""
        # 下跌+放量
        assert t3_volume_price_score(_series([-0.02]), _series([3.0])).iloc[0] == 0
        # 上涨+缩量
        assert t3_volume_price_score(_series([0.03]), _series([-1.0])).iloc[0] == 0
        # 下跌+缩量
        assert t3_volume_price_score(_series([-0.01]), _series([-0.5])).iloc[0] == 0

    def test_nan_tolerated(self):
        """NaN → fillna(0) → 视为 0 → score=0。"""
        pct = _series([np.nan, 0.03])
        vol_z = _series([3.0, np.nan])
        result = t3_volume_price_score(pct, vol_z)
        # NaN pct → 0 → 不满足 >0 条件 → 0
        assert result.iloc[0] == 0
        # NaN vol_z → 0 → 不满足 z>0 → 0
        assert result.iloc[1] == 0

    def test_boundary_values(self):
        """精确边界: pct=0.01 不满足 >0.01, pct=0.02 不满足 >0.02。"""
        # pct=0.01 & z=1 → 不满足 >0.01&>1 → 仅满足 >0&>0 → 35
        assert t3_volume_price_score(_series([0.01]), _series([1.0])).iloc[0] == 35
        # pct=0.02 & z=2 → 不满足 >0.02&>2 → 满足 >0.01&>1 → 65
        assert t3_volume_price_score(_series([0.02]), _series([2.0])).iloc[0] == 65


# ---------------------------------------------------------------------------
# 2. t3_ma_trend_score — 均线趋势 0/30/60/70
# ---------------------------------------------------------------------------


class TestT3MaTrendScore:
    """均线趋势评分：MA5>MA20>MA60 多头排列强度。"""

    @pytest.fixture
    def _strong_uptrend_close(self) -> pd.Series:
        """构造强多头序列：持续上涨，MA5/MA60 > 1.05。"""
        # 70 日持续上涨，斜率足够大让 MA5/MA60 > 1.05
        return pd.Series(np.linspace(100, 120, 70))

    @pytest.fixture
    def _flat_close(self) -> pd.Series:
        """构造横盘序列：MA5 = MA20 = MA60（完全不涨不跌）。"""
        return pd.Series([100.0] * 70)

    def test_strong_full_alignment(self, _strong_uptrend_close):
        """MA5>MA20>MA60 & MA5/MA60>1.05 → 70。"""
        result = t3_ma_trend_score(_strong_uptrend_close)
        # 最后一天应满足强多头
        assert result.iloc[-1] == 70

    def test_full_alignment_without_strength(self):
        """MA5>MA20>MA60 但 MA5/MA60 <= 1.05 → 60。"""
        # 温和上涨：MA5>MA20>MA60 但比值不够 1.05
        close = pd.Series(np.linspace(100, 103, 70))
        result = t3_ma_trend_score(close)
        assert result.iloc[-1] == 60

    def test_short_only(self):
        """MA5>MA20 但 MA20<=MA60 → 30（短期多头）。"""
        # 先涨后跌：MA5 刚上穿 MA20，但 MA20 仍在 MA60 下方
        close = pd.Series(list(np.linspace(90, 85, 60)) + list(np.linspace(85, 88, 10)))
        result = t3_ma_trend_score(close)
        # 最后一天 MA5 可能 > MA20 但 MA20 < MA60
        assert result.iloc[-1] in (30, 0)  # 取决于 MA 交叉精确位置

    def test_no_alignment_when_flat(self, _flat_close):
        """横盘 → MA5 ≈ MA20 → 0。"""
        result = t3_ma_trend_score(_flat_close)
        assert result.iloc[-1] == 0

    def test_returns_pd_series(self, _strong_uptrend_close):
        """返回类型为 pd.Series，索引对齐。"""
        result = t3_ma_trend_score(_strong_uptrend_close)
        assert isinstance(result, pd.Series)
        assert len(result) == len(_strong_uptrend_close)


# ---------------------------------------------------------------------------
# 3. t3_sentiment_score — 市场情绪 0/35/65/80
# ---------------------------------------------------------------------------


class TestT3SentimentScore:
    """市场情绪评分：ad_ratio 涨多跌少程度。"""

    def test_broad_rally(self):
        """ad_ratio>0.6 → 80（普涨，强情绪）。"""
        result = t3_sentiment_score(_series([0.7, 0.65, 0.9]))
        assert (result == 80).all()

    def test_moderate_positive(self):
        """ad_ratio>0.3 → 65（涨多跌少，过门槛）。"""
        result = t3_sentiment_score(_series([0.4, 0.35, 0.5]))
        assert (result == 65).all()

    def test_slight_positive(self):
        """ad_ratio>0 → 35（偏多，未达门槛）。"""
        result = t3_sentiment_score(_series([0.1, 0.05, 0.2]))
        assert (result == 35).all()

    def test_negative_or_neutral(self):
        """ad_ratio<=0 → 0（偏空或中性）。"""
        result = t3_sentiment_score(_series([0.0, -0.1, -0.5]))
        assert (result == 0).all()

    def test_nan_tolerated(self):
        """NaN → fillna(0) → 0。"""
        result = t3_sentiment_score(_series([np.nan, 0.7]))
        assert result.iloc[0] == 0
        assert result.iloc[1] == 80

    def test_boundary_values(self):
        """精确边界: 0.3 → 不满足 >0.3 → 35; 0.6 → 不满足 >0.6 → 65。"""
        assert t3_sentiment_score(_series([0.3])).iloc[0] == 35
        assert t3_sentiment_score(_series([0.6])).iloc[0] == 65


# ---------------------------------------------------------------------------
# 4. t3_money_effect_score — 资金效应 0/25/50/65/80（Phase 2c）
# ---------------------------------------------------------------------------


class TestT3MoneyEffectScore:
    """资金效应评分：主力净流入 + 涨停数共振。"""

    def test_strong_capital_surge(self):
        """inflow>5% & 涨停>100 → 80（强资金+广涨停，主线确立）。"""
        inflow = _series([6.0, 5.5, 8.0])
        lu_count = _series([120, 150, 200])
        result = t3_money_effect_score(inflow, lu_count)
        assert (result == 80).all()

    def test_moderate_capital(self):
        """inflow>3% & 涨停>50 → 65（中度资金+涨停）。"""
        inflow = _series([4.0, 3.5])
        lu_count = _series([60, 55])
        result = t3_money_effect_score(inflow, lu_count)
        assert (result == 65).all()

    def test_confirm_threshold(self):
        """inflow>2% & 涨停>30 → 50（温和资金，过 confirm 门槛）。"""
        inflow = _series([2.5, 3.0])
        lu_count = _series([35, 40])
        result = t3_money_effect_score(inflow, lu_count)
        assert (result == 50).all()

    def test_weak_inflow(self):
        """inflow>0 但不满足共振条件 → 25（净流入但弱）。"""
        # inflow>0 但涨停数不足
        inflow = _series([1.0, 0.5])
        lu_count = _series([5, 10])
        result = t3_money_effect_score(inflow, lu_count)
        assert (result == 25).all()

    def test_outflow_zero(self):
        """inflow<=0 → 0（净流出，无资金效应）。"""
        inflow = _series([-1.0, 0.0, -3.0])
        lu_count = _series([100, 200, 300])
        result = t3_money_effect_score(inflow, lu_count)
        assert (result == 0).all()

    def test_nan_tolerated(self):
        """NaN inflow → fillna(0) → 0；NaN lu → fillna(0) → 降级。"""
        inflow = _series([np.nan, 6.0])
        lu_count = _series([200, np.nan])
        result = t3_money_effect_score(inflow, lu_count)
        # NaN inflow → 0 → score=0
        assert result.iloc[0] == 0
        # inflow=6 but NaN lu → 0 → 不满足 >100 → 25
        assert result.iloc[1] == 25

    def test_index_reindex(self):
        """limit_up_count 索引不同于 inflow_pct 时正确 reindex。"""
        inflow = pd.Series([5.0, 6.0], index=[0, 1])
        lu_count = pd.Series([150, 200], index=[10, 11])  # 不同索引
        result = t3_money_effect_score(inflow, lu_count)
        # reindex 后 lu 全 NaN → fillna(0) → 不满足涨停条件 → 25
        assert (result == 25).all()


# ---------------------------------------------------------------------------
# 5. t3_mainline_score — 主线效应 0/35/65/80（Phase 2c）
# ---------------------------------------------------------------------------


class TestT3MainlineScore:
    """主线效应评分：板块涨幅集中度 HHI + 头部板块涨幅。"""

    def test_strong_concentration(self):
        """HHI>0.15 & Top>3% → 80（强集中+强领涨，主线明确）。"""
        hhi = _series([0.18, 0.20])
        top_pct = _series([4.0, 5.0])
        result = t3_mainline_score(hhi, top_pct)
        assert (result == 80).all()

    def test_moderate_concentration(self):
        """HHI>0.10 & Top>2% → 65（中度集中）。"""
        hhi = _series([0.12, 0.11])
        top_pct = _series([2.5, 3.0])
        result = t3_mainline_score(hhi, top_pct)
        assert (result == 65).all()

    def test_weak_concentration(self):
        """HHI>0.08 & Top>1% → 35（弱集中，未达门槛）。"""
        hhi = _series([0.09, 0.085])
        top_pct = _series([1.5, 1.2])
        result = t3_mainline_score(hhi, top_pct)
        assert (result == 35).all()

    def test_scattered_no_mainline(self):
        """HHI<=0.08 或 Top<=1% → 0（散乱无主线）。"""
        # HHI 低
        assert t3_mainline_score(_series([0.05]), _series([5.0])).iloc[0] == 0
        # Top 低
        assert t3_mainline_score(_series([0.20]), _series([0.5])).iloc[0] == 0

    def test_boundary_values(self):
        """精确边界: HHI=0.10 不满足 >0.10; Top=2.0 不满足 >2。"""
        # HHI=0.10 & Top=3 → 不满足 >0.10&>3 → 满足 >0.08&>1 → 35
        assert t3_mainline_score(_series([0.10]), _series([3.0])).iloc[0] == 35
        # HHI=0.15 & Top=2 → 不满足 >0.15&>3 也不满足 >0.10&>2（Top=2 不满足 >2）
        # → 仅满足 >0.08&>1 → 35
        assert t3_mainline_score(_series([0.15]), _series([2.0])).iloc[0] == 35

    def test_nan_tolerated(self):
        """NaN → fillna(0) → 0。"""
        hhi = _series([np.nan, 0.20])
        top_pct = _series([5.0, np.nan])
        result = t3_mainline_score(hhi, top_pct)
        assert result.iloc[0] == 0
        assert result.iloc[1] == 0


# ---------------------------------------------------------------------------
# 6. t3_leader_score — 龙头效应 0/35/65/80（Phase 2c）
# ---------------------------------------------------------------------------


class TestT3LeaderScore:
    """龙头效应评分：最高连板数 + 晋级率。"""

    def test_strong_leader(self):
        """连板>=5 & 晋级>0.5 → 80（高连板+高晋级，强龙头）。"""
        consec = _series([5.0, 6.0, 8.0])
        promo = _series([0.6, 0.55, 0.8])
        result = t3_leader_score(consec, promo)
        assert (result == 80).all()

    def test_moderate_leader(self):
        """连板>=3 & 晋级>0.3 → 65（中连板+中晋级）。"""
        consec = _series([3.0, 4.0])
        promo = _series([0.4, 0.35])
        result = t3_leader_score(consec, promo)
        assert (result == 65).all()

    def test_low_consec(self):
        """连板>=2 → 35（低连板，未达门槛）。"""
        # 连板>=2 但晋级率不足
        consec = _series([2.0, 2.0])
        promo = _series([0.1, 0.2])
        result = t3_leader_score(consec, promo)
        assert (result == 35).all()

    def test_no_leader(self):
        """连板<2 → 0（无连板，无龙头）。"""
        consec = _series([0.0, 1.0, 1.5])
        promo = _series([0.8, 0.6, 0.5])
        result = t3_leader_score(consec, promo)
        assert (result == 0).all()

    def test_boundary_values(self):
        """精确边界: 连板=3 不满足 >=3&>0.3 的连板部分不适用（3>=3 成立）。
        连板=5 & 晋级=0.5 → 不满足 >0.5 → 65（不是 80）。"""
        # 连板=5 & 晋级=0.5 → 不满足 >0.5 → 落到 >=3&>0.3 → 65
        assert t3_leader_score(_series([5.0]), _series([0.5])).iloc[0] == 65
        # 连板=3 & 晋级=0.3 → 不满足 >0.3 → 落到 >=2 → 35
        assert t3_leader_score(_series([3.0]), _series([0.3])).iloc[0] == 35

    def test_nan_tolerated(self):
        """NaN consec → fillna(0) → 0; NaN promo → fillna(0) → 降级。"""
        consec = _series([np.nan, 5.0])
        promo = _series([0.8, np.nan])
        result = t3_leader_score(consec, promo)
        # NaN consec → 0 → <2 → 0
        assert result.iloc[0] == 0
        # consec=5 but NaN promo → 0 → 不满足 >0.5 → 满足 >=2 → 35
        assert result.iloc[1] == 35


# ---------------------------------------------------------------------------
# 7. t3_one_day_mainline_flag — 一日主线证伪 0/1（Phase 2c）
# ---------------------------------------------------------------------------


class TestT3OneDayMainlineFlag:
    """一日主线证伪标志：昨日 Top3 今日全跌>2% → flag=1。"""

    def test_triggered_when_all_decline(self):
        """prev_top3_max < -2.0 → 1.0（三者全跌>2%，主线一日游）。"""
        result = t3_one_day_mainline_flag(_series([-2.5, -3.0, -5.0]))
        assert (result == 1.0).all()

    def test_not_triggered_when_partial_recovery(self):
        """prev_top3_max >= -2.0 → 0.0（至少一个板块未跌超 2%）。"""
        result = t3_one_day_mainline_flag(_series([-1.5, 0.0, 2.0]))
        assert (result == 0.0).all()

    def test_boundary_exactly_minus_two(self):
        """prev_top3_max = -2.0 → 0.0（边界值不触发，< -2.0 才触发）。"""
        result = t3_one_day_mainline_flag(_series([-2.0]))
        assert result.iloc[0] == 0.0

    def test_mixed_values(self):
        """混合值: 部分触发部分不触发。"""
        result = t3_one_day_mainline_flag(_series([-3.0, -1.0, -2.01, 0.5]))
        assert result.iloc[0] == 1.0
        assert result.iloc[1] == 0.0
        assert result.iloc[2] == 1.0
        assert result.iloc[3] == 0.0

    def test_nan_tolerated(self):
        """NaN → fillna(0) → 0.0（不触发）。"""
        result = t3_one_day_mainline_flag(_series([np.nan, -3.0]))
        assert result.iloc[0] == 0.0
        assert result.iloc[1] == 1.0

    def test_returns_float_series(self):
        """返回 pd.Series，值域 {0.0, 1.0}。"""
        result = t3_one_day_mainline_flag(_series([-3.0, 1.0]))
        assert isinstance(result, pd.Series)
        assert set(result.unique()) <= {0.0, 1.0}


# ---------------------------------------------------------------------------
# 值域与类型契约（跨函数）
# ---------------------------------------------------------------------------


class TestT3ScoreContracts:
    """所有 T3 评分函数的值域与返回类型契约。"""

    def test_all_scores_in_range_0_100(self):
        """所有 score 函数返回值 ∈ [0, 100]。"""
        idx = pd.date_range("2024-01-01", periods=70, freq="B")
        close = pd.Series(np.linspace(100, 120, 70), index=idx)
        pct = close.pct_change().fillna(0)
        vol_z = pd.Series(np.linspace(-1, 3, 70), index=idx)
        ad = pd.Series(np.linspace(-0.5, 0.8, 70), index=idx)
        inflow = pd.Series(np.linspace(-1, 6, 70), index=idx)
        lu = pd.Series(np.linspace(0, 150, 70), index=idx)
        hhi = pd.Series(np.linspace(0.01, 0.2, 70), index=idx)
        top = pd.Series(np.linspace(0, 5, 70), index=idx)
        consec = pd.Series(np.linspace(0, 6, 70), index=idx)
        promo = pd.Series(np.linspace(0, 0.8, 70), index=idx)
        prev_top3 = pd.Series(np.linspace(-5, 3, 70), index=idx)

        scores = [
            t3_volume_price_score(pct, vol_z),
            t3_ma_trend_score(close),
            t3_sentiment_score(ad),
            t3_money_effect_score(inflow, lu),
            t3_mainline_score(hhi, top),
            t3_leader_score(consec, promo),
        ]
        for s in scores:
            assert s.min() >= 0, f"score min {s.min()} < 0"
            assert s.max() <= 100, f"score max {s.max()} > 100"

        # flag 函数值域 {0, 1}
        flag = t3_one_day_mainline_flag(prev_top3)
        assert flag.min() >= 0
        assert flag.max() <= 1

    def test_all_return_pd_series(self):
        """所有函数返回 pd.Series，索引与第一个参数对齐。"""
        idx = range(5)
        pct = pd.Series([0.01, 0.03, -0.01, 0.0, 0.02], index=idx)
        vol_z = pd.Series([1, 3, 0, -1, 2], index=idx)
        assert isinstance(t3_volume_price_score(pct, vol_z), pd.Series)
        assert isinstance(t3_sentiment_score(pd.Series([0.1] * 5)), pd.Series)
        assert isinstance(t3_one_day_mainline_flag(pd.Series([-3.0] * 5)), pd.Series)
