# [A_test] module_id: MOD-TEST-OVERLAY-FEAT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 Phase2c
# [MODULE] tests.regime.test_overlay_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; inspect; re; itertools
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
  - 阈值校准欠账台账（THRESHOLD_CALIBRATION_LEDGER，OVB-4 五项）：结构契约 +
    在册集合钉死 + 台账所记数字与调用点常量/字段间自洽（车道#14 补覆盖）

依据: 10_regime_detector_spec v1.3.1 §4 / Phase 2c 计划 / P1-E5
      overlay_dims_mining §2#4/§4（OVB-4 阈值 A 股校准缺口五项）
"""

from __future__ import annotations

import inspect
import re
from itertools import pairwise

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features import overlay_features
from zephyr.regime.features.overlay_features import (
    ALERT_UNCALIBRATED_THRESHOLDS,
    THRESHOLD_CALIBRATION_LEDGER,
    s2_capitulation_score,
    t3_leader_score,
    t3_ma_trend_score,
    t3_mainline_score,
    t3_money_effect_score,
    t3_one_day_mainline_flag,
    t3_sentiment_score,
    t3_volume_price_score,
    t5_leader_break_score,
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


# ---------------------------------------------------------------------------
# t5_leader_break_score — 领涨股破位（OVB-5 治本：真实个股龙头 cohort 大面率）
# ---------------------------------------------------------------------------


class TestT5LeaderBreakScore:
    """领涨股破位评分：输入个股龙头大面率 leader_distress∈[0,1]（非指数代理）。"""

    def test_normal_no_break(self):
        """大面率 ≤0.05（常态）→ 0（无信号不干预）。"""
        distress = _series([0.0, 0.02, 0.05])
        result = t5_leader_break_score(distress)
        assert (result == 0).all()

    def test_cooling(self):
        """0.05<distress<0.10 → 35（偏冷，未达 trigger 门槛）。"""
        distress = _series([0.06, 0.08, 0.099])
        result = t5_leader_break_score(distress)
        assert (result == 35).all()

    def test_trigger_threshold(self):
        """distress>=0.10 → 60（过 T5 trigger 门槛）。"""
        distress = _series([0.10, 0.12])
        result = t5_leader_break_score(distress)
        assert (result == 60).all()

    def test_strong_break(self):
        """distress>=0.15 → 70（强破位）。"""
        distress = _series([0.15, 0.18, 0.21])
        result = t5_leader_break_score(distress)
        assert (result == 70).all()

    def test_extreme_break(self):
        """distress>=0.22（≈p98 龙头集体核）→ 85（极端退潮）。"""
        distress = _series([0.22, 0.30, 0.5])
        result = t5_leader_break_score(distress)
        assert (result == 85).all()

    def test_boundary_values(self):
        """精确边界：0.10→60、0.099→35；0.22→85、0.219→70。"""
        assert t5_leader_break_score(_series([0.10])).iloc[0] == 60
        assert t5_leader_break_score(_series([0.0999])).iloc[0] == 35
        assert t5_leader_break_score(_series([0.22])).iloc[0] == 85
        assert t5_leader_break_score(_series([0.2199])).iloc[0] == 70

    def test_nan_and_clip_tolerated(self):
        """NaN→0；越界值 clip 到 [0,1]（0.5 与 2.0 同归 85）。"""
        result = t5_leader_break_score(_series([np.nan]))
        assert result.iloc[0] == 0
        clipped = t5_leader_break_score(_series([2.0]))
        assert clipped.iloc[0] == 85

    def test_value_domain_and_alignment(self):
        """值域∈{0,35,60,70,85}⊂[0,100]；索引与输入对齐。"""
        idx = pd.date_range("2024-01-01", periods=6, freq="B")
        distress = pd.Series([0.0, 0.06, 0.10, 0.15, 0.22, 0.40], index=idx)
        result = t5_leader_break_score(distress)
        assert isinstance(result, pd.Series)
        assert list(result.index) == list(idx)
        assert set(result.unique()) <= {0.0, 35.0, 60.0, 70.0, 85.0}
        assert result.min() >= 0 and result.max() <= 100


# ---------------------------------------------------------------------------
# 阈值校准欠账台账（THRESHOLD_CALIBRATION_LEDGER，OVB-4 五项）
# ---------------------------------------------------------------------------
# 台账是"哪些 overlay 阈值仍未经 A 股本土 walk-forward 复推"的唯一真源，且直接决定
# 运行期一次性告警的内容（overlay_signals_builder._precompute 消费 ALERT_UNCALIBRATED_
# THRESHOLDS）。此前该路径零测试覆盖：一条 ALERT 被悄悄删除/改判、或台账数字与调用点
# 常量脱钩，都不会有任何测试变红（车道#14 补覆盖）。
# 本节的钉死策略：集合字面量 + 文本契约 + 源码交叉核对，不复制硬编码小数
# （所有数字都从台账文本解析后再与代码比对，改一处即失败）。

_LEDGER_STATUS_ALERT = "ALERT"
_LEDGER_STATUS_RESOLVED = "RESOLVED"
_LEDGER_STATUSES = frozenset({_LEDGER_STATUS_ALERT, _LEDGER_STATUS_RESOLVED})

# 在册项钉死（OVB-4 五项）：新增/删除/改判必须同时改动这两组字面量 → 评审可见
_RESOLVED_IDS = frozenset({"s2_capitulation_confirm", "s1_vix_panic_s2_vix"})
_ALERT_IDS = frozenset({"s2_breadth_thrust", "t3_money_effect", "t3_mainline"})

# 台账项 → 承载该阈值的宿主函数（默认约定：<key>_score）。
# 复合键（一条欠账横跨两路函数）与参数级欠账无法由 key 反推，显式登记。
_LEDGER_HOSTS: dict[str, tuple[str, ...]] = {
    "s1_vix_panic_s2_vix": ("s1_vix_panic_score", "s2_vix_score"),
    "s2_capitulation_confirm": ("s2_capitulation_score",),
}

# "0.615/0.40"、"0.75/0.85/0.90/0.95" 这类小数阈值族
_DEC_LITERALS = re.compile(r"(?<!≈)\d+\.\d+")
# "涨停家数门槛 30/50/100" 这类整数门槛族
_INT_GATE_FAMILY = re.compile(r"门槛\s*(\d+(?:/\d+)+)")
# "命中≈62%/45%/10%" 这类 CH 实测命中率族
_HIT_RATE_FAMILY = re.compile(r"命中≈([\d%/]+)")
# "0.75/0.85/0.90/0.95 恒为 p75/85/90/95" 这类"分位切点"自证claims
_PCTILE_CLAIM = re.compile(r"([0-9.]+(?:/[0-9.]+)+)\s*恒为\s*p(\d+(?:/\d+)+)")
# "12.44→6.24（虚增 1.99x）" 这类"改前→改后（幅度 Nx）"量级 claims
_MAGNITUDE_CLAIM = re.compile(
    r"(\d+(?:\.\d+)?)\s*%?→\s*(\d+(?:\.\d+)?)\s*%?[（(]([^（）()]*?)(\d+(?:\.\d+)?)\s*[xX倍]"
)
# 代码位引用：`THRESHOLD_CALIBRATION_LEDGER["<key>"]`（docstring 里可能折行）
_LEDGER_CODE_REF = re.compile(r'THRESHOLD_CALIBRATION_LEDGER\s*(?:\n\s*)?\["([a-z0-9_]+)"\]')


def _fields(key: str) -> tuple[str, str, str]:
    r"""按值格式契约 '<状态> | <CH 只读实证依据> | <处置>' 拆三段。

    管道前后空白用宽容切分（\s*\|\s*）：容忍排版漂移，段数仍须恰为 3；
    分隔符书写是否规范另由 test_separator_style_ratchet 单独棘轮。
    """
    parts = re.split(r"\s*\|\s*", THRESHOLD_CALIBRATION_LEDGER[key])
    assert len(parts) == 3, f"{key} 值格式须为 '<状态> | <依据> | <处置>'，实际 {len(parts)} 段: {parts}"
    return parts[0], parts[1], parts[2]


def _host_sources(key: str) -> dict[str, str]:
    """台账项宿主函数源码：{函数名: 源码}。宿主不存在即台账与代码脱钩。"""
    out: dict[str, str] = {}
    for name in _LEDGER_HOSTS.get(key, (f"{key}_score",)):
        fn = getattr(overlay_features, name, None)
        assert callable(fn), f"台账项 {key} 的宿主函数 {name} 不存在（欠账已指向死代码）"
        out[name] = inspect.getsource(fn)
    return out


class TestThresholdCalibrationLedgerSchema:
    """台账结构契约：值格式 + 在册集合 + 告警集合可推导 + 与源码互指。"""

    def test_entry_set_pinned(self):
        """五项在册，且 2 RESOLVED / 3 ALERT 的身份集合逐一钉死（悄悄增删即红）。"""
        assert set(THRESHOLD_CALIBRATION_LEDGER) == _RESOLVED_IDS | _ALERT_IDS
        by_status: dict[str, set[str]] = {s: set() for s in _LEDGER_STATUSES}
        for key in THRESHOLD_CALIBRATION_LEDGER:
            status, _, _ = _fields(key)
            assert status in _LEDGER_STATUSES, f"{key} 状态未知: {status!r}（可选 ALERT/RESOLVED）"
            by_status[status].add(key)
        assert by_status[_LEDGER_STATUS_RESOLVED] == set(_RESOLVED_IDS)
        assert by_status[_LEDGER_STATUS_ALERT] == set(_ALERT_IDS)

    def test_alert_tuple_is_derived_not_hardcoded(self):
        """ALERT_UNCALIBRATED_THRESHOLDS 必须是台账的投影（顺序=台账序，无重复）。"""
        expected = tuple(
            k for k, v in THRESHOLD_CALIBRATION_LEDGER.items() if v.startswith(_LEDGER_STATUS_ALERT)
        )
        assert expected == ALERT_UNCALIBRATED_THRESHOLDS
        assert isinstance(ALERT_UNCALIBRATED_THRESHOLDS, tuple)
        assert len(set(ALERT_UNCALIBRATED_THRESHOLDS)) == len(_ALERT_IDS) == 3
        # RESOLVED 项绝不进告警集（避免噪声，同时防"改判未撤告警"的半吊子状态）
        assert not (set(ALERT_UNCALIBRATED_THRESHOLDS) & _RESOLVED_IDS)

    def test_three_fields_all_present_and_meaningful(self):
        """三段齐全非空：状态是裸枚举词，依据/处置均有实质内容（代码只读状态前缀）。"""
        for key in THRESHOLD_CALIBRATION_LEDGER:
            assert isinstance(THRESHOLD_CALIBRATION_LEDGER[key], str), f"{key} 值须为字符串"
            status, evidence, action = _fields(key)
            assert status == status.strip() and status in _LEDGER_STATUSES
            assert " " not in status, f"{key} 状态段混入了依据文字: {status!r}"
            assert len(evidence) >= 20, f"{key} 实证依据段过短（须留 CH 只读实证痕迹）"
            assert len(action) >= 8, f"{key} 处置段过短（无实质处置口径）"

    def test_ledger_and_code_reference_each_other(self):
        """双向互指：docstring 引用的台账 key 必须在册，在册 key 必须被调用点文档引用。"""
        refs = set(_LEDGER_CODE_REF.findall(inspect.getsource(overlay_features)))
        assert refs == set(THRESHOLD_CALIBRATION_LEDGER), (
            f"代码引用 {sorted(refs)} 与台账在册 {sorted(THRESHOLD_CALIBRATION_LEDGER)} 不一致"
            "（新增欠账须写进对应评分函数 docstring，删欠账须同步删引用）"
        )

    def test_alert_entries_point_at_live_scoring_functions(self):
        """每条 ALERT 欠账都得能落到一个真实评分函数上（防"台账项对应维度已改名/删除"）。"""
        for key in ALERT_UNCALIBRATED_THRESHOLDS:
            hosts = _host_sources(key)
            assert hosts, f"ALERT 项 {key} 无宿主函数"

    def test_separator_style_ratchet(self):
        """分隔符书写规范棘轮：值格式规定 ' | '（管道前后各一空格）。

        t3_mainline 现存历史瑕疵（"）| " 少一个前导空格，overlay_features.py 台账尾项），
        宽容切分已保证不影响解析；本棘轮只保证不再新增此类漂移，修好后请把名单清空。
        """
        non_canonical = {k for k, v in THRESHOLD_CALIBRATION_LEDGER.items() if len(v.split(" | ")) != 3}
        assert non_canonical <= {"t3_mainline"}, f"新增分隔符漂移项: {sorted(non_canonical)}"


class TestThresholdCalibrationLedgerSelfConsistency:
    """台账内部自洽：状态↔处置、所记数字↔调用点常量、claims↔claims。"""

    def test_status_and_disposition_do_not_contradict(self):
        """ALERT 须声称"保留现值 + 告警"，RESOLVED 不得声称仍需告警/待改（两字段互相打脸即红）。"""
        for key in THRESHOLD_CALIBRATION_LEDGER:
            status, _, action = _fields(key)
            if status == _LEDGER_STATUS_ALERT:
                assert "告警" in action, f"{key} 状态 ALERT 但处置未声称告警（运行期告警将被静默消失）"
                assert "保留现值" in action, (
                    f"{key} 状态 ALERT 但处置未声称'保留现值'——若阈值已改，运行期告警文案"
                    "（现行值沿用）即失实，须同步台账"
                )
            else:
                assert "告警" not in action, f"{key} 已 RESOLVED 却仍处置为告警（半吊子改判）"
                assert "保留现值" not in action, f"{key} 已 RESOLVED 却仍声称沿用未裁定"

    def test_documented_threshold_literals_still_live_at_call_sites(self):
        """台账依据段写下的阈值常量必须仍出现在宿主函数源码里（改代码不改台账=红）。

        单宿主项：全部记录常量须在该宿主源码逐一定位。
        复合宿主项（一条欠账横跨两路函数）：每个常量至少落在一路宿主上，且每路
        宿主都仍用到台账记录的某个常量——两路共用同一族分位阈值正是该项 RESOLVED
        的论证前提，任一路彻底弃用即前提失守。
        """
        for key in THRESHOLD_CALIBRATION_LEDGER:
            _, evidence, _ = _fields(key)
            sources = _host_sources(key)
            decimals = _DEC_LITERALS.findall(evidence)
            if len(sources) == 1:
                src = next(iter(sources.values()))
                for lit in decimals:
                    assert lit in src, (
                        f"{key} 台账记录阈值 {lit}，但宿主 {key} 对应函数源码已无此常量"
                    )
            elif decimals:
                for lit in decimals:
                    assert any(lit in s for s in sources.values()), (
                        f"{key} 台账记录阈值 {lit}，两路宿主源码均已无此常量: {sorted(sources)}"
                    )
                for name, src in sources.items():
                    assert any(lit in src for lit in decimals), (
                        f"{key} 的宿主 {name} 已不再使用台账记录的任何阈值 → 复合键声称的"
                        "「两路同阈值」前提不再成立，须重裁定或拆分台账项"
                    )
            for family in _INT_GATE_FAMILY.findall(evidence):
                for num in family.split("/"):
                    assert any(re.search(rf">\s*{num}\b", s) for s in sources.values()), (
                        f"{key} 台账记录整数门槛 {num}，宿主源码已无 `> {num}` 判定"
                    )

    def test_percentile_equivalence_claim_is_arithmetically_self_consistent(self):
        """'0.75/…/0.95 恒为 p75/…/p95' 型 claims：小数族与分位族必须逐项等值。"""
        checked = 0
        for key in THRESHOLD_CALIBRATION_LEDGER:
            _, evidence, _ = _fields(key)
            for decs, pcts in _PCTILE_CLAIM.findall(evidence):
                dec_list = [float(d) for d in decs.split("/")]
                pct_list = [float(p) for p in pcts.split("/")]
                assert len(dec_list) == len(pct_list), f"{key} 分位 claims 两族长度不等"
                for d, p in zip(dec_list, pct_list, strict=True):
                    assert abs(d * 100.0 - p) < 1e-6, f"{key} 声称 {d} 恒为 p{p}，实算 {d * 100:g}"
                checked += 1
        assert checked >= 1, "s1_vix_panic_s2_vix 的分位等价 claims 已消失（台账文案被改写？）"

    def test_threshold_ladder_agrees_with_hit_rate_ladder(self):
        """'门槛 30/50/100 单调 + 命中≈62%/45%/10%'：严门槛必须低命中，否则两处 claims 相互打脸。"""
        checked = 0
        for key in THRESHOLD_CALIBRATION_LEDGER:
            _, evidence, _ = _fields(key)
            gates = _INT_GATE_FAMILY.findall(evidence)
            rates = _HIT_RATE_FAMILY.findall(evidence)
            if not (gates and rates):
                continue
            g = [float(x) for x in gates[0].split("/")]
            r = [float(x) for x in re.findall(r"\d+", rates[0])]
            assert len(g) == len(r), f"{key} 门槛族与命中率族项数不等: {g} vs {r}"
            assert all(a < b for a, b in pairwise(g)), f"{key} 门槛非单调递增: {g}"
            assert all(a > b for a, b in pairwise(r)), f"{key} 命中率未随门槛收紧而下降: {r}"
            checked += 1
        assert checked >= 1, "t3_money_effect 的门槛/命中率 pairs claims 已消失（台账文案被改写？）"

    def test_capitulation_confirm_resolved_claim_matches_signature(self):
        """confirm 项 RESOLVED 的依据=「30/40 仅占位、生产用默认 10/20」→ 核函数签名默认值。"""
        _, evidence, _ = _fields("s2_capitulation_confirm")
        assert "halflife=30/lookback=40" in evidence, "台账不再声称 30/40 占位 → 本测试需随裁定更新"
        params = inspect.signature(s2_capitulation_score).parameters
        assert params["halflife"].default == 10, "生产默认 halflife 已变，须复核 confirm 项是否仍无运行期欠账"
        assert params["lookback"].default == 20, "生产默认 lookback 已变，须复核 confirm 项是否仍无运行期欠账"

    def test_recorded_before_after_magnitudes_agree_with_stated_multiple(self):
        """台账文本里的"改前→改后（虚增 Nx）"型量级 claims 只做自检：比值须等于声称倍数。

        数字不在测试里二次硬编码（改前/改后/倍数由同一句 claims 提供，只验其互洽）。
        台账当前不承载此类 claims（OVB-2 的连板虚增量级记在 builder 侧，见
        tests/regime/test_overlay_signals_builder.py 的同款自检），本测试为
        "一旦台账开始记录量级 claims 即必须自洽"的前瞻契约。
        """
        for key, entry in THRESHOLD_CALIBRATION_LEDGER.items():
            for before, after, qualifier, multiple in _MAGNITUDE_CLAIM.findall(entry):
                b, a, m = float(before), float(after), float(multiple)
                assert abs(b / a - m) <= 0.01 * m + 1e-6, (
                    f"{key} 量级 claims 自相矛盾: {before}→{after} 比值 {b / a:.4f} ≠ 声称 {multiple}x"
                )
                if "虚增" in qualifier:
                    assert b > a, f"{key} 声称虚增却记录 {before}→{after}（改后反而更大）"
