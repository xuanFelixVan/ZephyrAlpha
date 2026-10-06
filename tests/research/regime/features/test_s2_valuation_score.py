# [A_test] module_id: MOD-TEST-S2-VALUATION | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 P1-E9b
# [MODULE] tests.regime.features.test_s2_valuation_score
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_valuation_score.py
# [TTL] permanent
# [ARCH-REF] #P1-E9b #14_regime_s2_diagnosis §4.2
# [ALGO_FLOW]
# 层: 输入
# - I1: 路B close（价格回撤代理）/ 路A cape_percentile + 可选 pb/破净/ERP/巴菲特
# 层: 算法
# - A1: 路B pos=close/rolling_max(250,min_periods=20) 分档 0/40/60/80（阈值右移校准）
# - A2: 路A CAPE 分位主映射（<10%→80/<25%→60/<40%→40）+ PB/破净+10 + ERP 双确认
#       （≤10 封顶）+ 巴菲特<70%+5，总分封顶 100
# 层: 输出
# - O1: pd.Series 0-100（CAPE 分位缺失 fillna(1.0)→0，危机期 PE 失真不回填）
"""test_s2_valuation_score.py — P1-E9b valuation 路B校准 + 路A基本面单元测试。

覆盖（14_regime_s2_diagnosis §4.2 + §4.5 step 1 stub 要求）：
  1. 路 B 阈值：pos<0.70→40 / <0.60→60 / <0.50→80（原 <0.50 才 40 过严已校准）
  2. 路 A CAPE 分位映射：<0.10→80 / <0.25→60 / <0.40→40 / else→0
  3. 危机期 PE 失真不回填：CAPE 低分位（低估）评分不受 PE_TTM 影响（无 pe 参数）
  4. 叠加加分：PB<10%→+10 / 破净率>10%→+10（互斥分支）/ ERP 分位>95%→+5 /
     ERP 绝对值>5%→+5、>6%→10（封顶 10）/ 巴菲特<70%→+5 / 总分封顶 100
  5. NaN 容错（CAPE fillna(1.0)→0）

依据: 14_regime_s2_diagnosis v0.4.5 §4.2 / §4.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.overlay_features import (
    s2_valuation_score,
    s2_valuation_score_fundamental,
)

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _close_with_pos(pos: float, n: int = 300) -> pd.Series:
    """构造 close：前 n-1 日恒 3000（rolling_max=3000），末日 = 3000×pos。"""
    arr = np.full(n, 3000.0)
    arr[-1] = 3000.0 * pos
    return pd.Series(arr)


# ---------------------------------------------------------------------------
# 1. 路 B：价格回撤代理（阈值校准版）
# ---------------------------------------------------------------------------


class TestValuationRouteB:
    def test_pos_above_070_zero(self):
        """pos=0.90（2020/2024 型非腰斩复苏）→ 0（路 B 救不了，须路 A）。"""
        assert s2_valuation_score(_close_with_pos(0.90)).iloc[-1] == 0.0

    def test_pos_below_070_gives_40(self):
        """pos<0.70（距高点 -30%）→ 40（过 confirm 门槛，新校准档）。"""
        assert s2_valuation_score(_close_with_pos(0.65)).iloc[-1] == 40

    def test_pos_below_060_gives_60(self):
        assert s2_valuation_score(_close_with_pos(0.55)).iloc[-1] == 60

    def test_pos_below_050_gives_80(self):
        """pos<0.50（腰斩级，2015 型）→ 80。"""
        assert s2_valuation_score(_close_with_pos(0.45)).iloc[-1] == 80

    def test_boundary_exact_070_not_triggered(self):
        """pos 恰=0.70 不触发（严格 <）。"""
        assert s2_valuation_score(_close_with_pos(0.70)).iloc[-1] == 0.0

    def test_warmup_min_periods(self):
        """min_periods=20：短序列（<250 日）不误零（P0 治标保留）。"""
        close = pd.Series(np.full(30, 3000.0))
        close.iloc[-1] = 1500.0  # pos=0.50 边界外 → 60 档? 0.50 不<0.50 → 60? 0.5<0.6 ✓
        assert s2_valuation_score(close).iloc[-1] == 60


# ---------------------------------------------------------------------------
# 2. 路 A：CAPE 分位主映射
# ---------------------------------------------------------------------------


class TestValuationRouteAMapping:
    def test_cape_extreme_undervaluation_80(self):
        """CAPE 分位 <10%（极度低估）→ 80。"""
        cp = pd.Series([0.05, 0.09])
        assert (s2_valuation_score_fundamental(cp) == 80).all()

    def test_cape_undervaluation_60(self):
        """CAPE 分位 <25% → 60。"""
        assert s2_valuation_score_fundamental(pd.Series([0.20])).iloc[0] == 60

    def test_cape_low_40(self):
        """CAPE 分位 <40% → 40（刚达 confirm 门槛）。"""
        assert s2_valuation_score_fundamental(pd.Series([0.35])).iloc[0] == 40

    def test_cape_high_zero(self):
        """CAPE 分位 ≥40% → 0。"""
        assert s2_valuation_score_fundamental(pd.Series([0.60])).iloc[0] == 0.0

    def test_cape_nan_zero(self):
        """CAPE NaN → fillna(1.0) → 0（数据缺失不误判低估）。"""
        assert s2_valuation_score_fundamental(pd.Series([np.nan])).iloc[0] == 0.0


# ---------------------------------------------------------------------------
# 3. 路 A：叠加加分
# ---------------------------------------------------------------------------


class TestValuationRouteABonus:
    def test_pb_bonus(self):
        """CAPE<10%（80）+ PB 分位<10% → +10 → 90。"""
        out = s2_valuation_score_fundamental(pd.Series([0.05]), pb_percentile=pd.Series([0.08]))
        assert out.iloc[0] == 90

    def test_broken_net_bonus_elif_branch(self):
        """pb_percentile 缺省时走 broken_net_ratio：破净率>10% → +10。"""
        out = s2_valuation_score_fundamental(pd.Series([0.05]), broken_net_ratio=pd.Series([0.15]))
        assert out.iloc[0] == 90

    def test_pb_takes_precedence_over_broken_net(self):
        """pb_percentile 优先（elif）：PB 不达标时即使破净率达标也不加（走 PB 分支）。"""
        out = s2_valuation_score_fundamental(
            pd.Series([0.05]),
            pb_percentile=pd.Series([0.50]),
            broken_net_ratio=pd.Series([0.15]),
        )
        assert out.iloc[0] == 80

    def test_erp_percentile_bonus(self):
        """ERP 分位 >95% → +5。"""
        out = s2_valuation_score_fundamental(pd.Series([0.05]), erp_percentile=pd.Series([0.97]))
        assert out.iloc[0] == 85

    def test_erp_absolute_bonus_5pct(self):
        """ERP 绝对值 >5%（历史大底）→ +5。"""
        out = s2_valuation_score_fundamental(pd.Series([0.05]), erp_absolute=pd.Series([0.055]))
        assert out.iloc[0] == 85

    def test_erp_absolute_bear_end_full_10(self):
        """ERP 绝对值 >6%（熊末）→ ERP 项直接满额 10（分位+绝对值不重复超 10）。"""
        out = s2_valuation_score_fundamental(
            pd.Series([0.05]),
            erp_percentile=pd.Series([0.97]),
            erp_absolute=pd.Series([0.07]),
        )
        assert out.iloc[0] == 90  # 80 + 10（ERP 封顶）

    def test_buffett_bonus(self):
        """巴菲特指标 <70%（A 股本土化深度低估）→ +5。"""
        out = s2_valuation_score_fundamental(pd.Series([0.05]), buffett_ratio=pd.Series([0.65]))
        assert out.iloc[0] == 85

    def test_total_clip_100(self):
        """全加分叠加 → 封顶 100（80+10+10+5=105 → 100）。"""
        out = s2_valuation_score_fundamental(
            pd.Series([0.05]),
            pb_percentile=pd.Series([0.05]),
            erp_percentile=pd.Series([0.97]),
            erp_absolute=pd.Series([0.07]),
            buffett_ratio=pd.Series([0.60]),
        )
        assert out.iloc[0] == 100

    def test_no_optional_inputs_pure_cape(self):
        """仅 CAPE（其余 None）→ 纯 CAPE 分（降级运行不抛错）。"""
        out = s2_valuation_score_fundamental(pd.Series([0.20, 0.50]))
        assert out.tolist() == [60, 0.0]

    def test_crisis_pe_distortion_not_used(self):
        """危机期 PE_TTM 失真不进入评分（函数无 PE 参数，CAPE 低分位照常给分）。"""
        # 构造"盈利崩塌期"：CAPE 分位 5%（5 年平滑后仍低估）→ 80，不受瞬时 PE 影响
        out = s2_valuation_score_fundamental(pd.Series([0.05]))
        assert out.iloc[0] == 80
