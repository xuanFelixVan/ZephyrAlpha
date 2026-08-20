# [A_test] module_id: MOD-TEST-S2-FUND | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4
# [MODULE] tests.regime.features.test_s2_fund_score
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_fund_score.py
# [TTL] permanent
# [ARCH-REF] #14_regime_s2_diagnosis §4.0 fund 警告/§6 开放问题 10（跨 P1-E4）
# [ALGO_FLOW]
# 层: 输入
# - I1: volume（旧 MVP 路径唯一输入）
# - I2: margin_balance（融资余额日频，注入式可选）+ xl_order_inflow（超大单净流入，注入式可选）
# 层: 算法
# - A1: 旧 MVP 路径（两新源均 None）：近 window 均量/前 window 均量比值分档 0/25/50/70（不变）
# - A2: 升级路径（任一新源注入）：融资余额变化分位 + 超大单净流入分位 + 成交量分位
#       按权重 0.4/0.35/0.25 加权（缺源按可用源归一化），composite 分档 0/25/50/70
# 层: 输出
# - O1: pd.Series 0-100（全 NaN 预热期 → 0，无信号不干预）
"""test_s2_fund_score.py — S2 fund 维度升级（融资余额+超大单加权）单元测试。

覆盖（14_regime_s2_diagnosis §4.0 fund 警告 + §6 开放问题 10，跨 P1-E4）：
  1. 旧 MVP 路径锁定（仅 volume）：均量比 >1.5→70 / >1.2→50 / >1.0→25 / else→0
  2. 升级路径：三源共振高分位 → ≥50（过 confirm 门槛）；三源低迷 → 0
  3. 单源注入降权归一化（仅融资余额 / 仅超大单）
  4. 预热期全 NaN → 0（无信号）；成交量代理偏弱场景（量升但融资余额不升）打分受限

依据: 14_regime_s2_diagnosis v0.5.2 §4.0/§6-10
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.overlay_features import s2_fund_score


def _flat_then_ratio(ratio: float, window: int = 20) -> pd.Series:
    """构造 volume：前 window 日均 1000、后 window 日均 1000×ratio（两段等长，
    末日 recent_avg/prev_avg 恰为两段均值之比——对齐 legacy 路径口径）。"""
    pre = np.full(window, 1000.0)
    post = np.full(window, 1000.0 * ratio)
    return pd.Series(np.concatenate([pre, post]))


# ---------------------------------------------------------------------------
# 1. 旧 MVP 路径（两新源均 None）——行为锁定，向后兼容
# ---------------------------------------------------------------------------


class TestFundLegacyPath:
    def test_ratio_above_1p5_gives_70(self):
        s = s2_fund_score(_flat_then_ratio(1.6))
        assert s.iloc[-1] == 70

    def test_ratio_above_1p2_gives_50(self):
        s = s2_fund_score(_flat_then_ratio(1.3))
        assert s.iloc[-1] == 50

    def test_ratio_above_1p0_gives_25(self):
        s = s2_fund_score(_flat_then_ratio(1.05))
        assert s.iloc[-1] == 25

    def test_shrinking_volume_gives_0(self):
        s = s2_fund_score(_flat_then_ratio(0.8))
        assert s.iloc[-1] == 0


# ---------------------------------------------------------------------------
# 2. 升级路径（融资余额 + 超大单注入）
# ---------------------------------------------------------------------------


def _late_shift_series(
    n: int = 300,
    base: float = 1000.0,
    shift_per_bar: float = 5.0,
    shift_bars: int = 40,
    seed: int = 7,
) -> pd.Series:
    """构造"末段骤变"序列：前 n-shift_bars 日 base+小噪声，末 shift_bars 日按
    shift_per_bar 线性漂移——使 diff/rolling-sum 的滚动分位在末日非退化
    （线性趋势序列 diff 恒定→分位≈0.5 退化，无法区分强弱场景）。"""
    rng = np.random.default_rng(seed)
    quiet = base + rng.normal(0, base * 0.005, n - shift_bars)
    start = quiet[-1]
    # 加速漂移（增量线性放大），使末日 diff/rolling-sum 为窗口内唯一极值
    # （匀速漂移下 diff 平台期并列最大，rank(pct) 取平均秩≈0.96 而非 1.0）
    steps = np.linspace(shift_per_bar, shift_per_bar * 2.5, shift_bars)
    surge = start + np.cumsum(steps)
    return pd.Series(np.concatenate([quiet, surge]), dtype=float)


class TestFundUpgradedPath:
    def test_three_sources_resonance_high_score(self):
        """三源共振（融资余额攀升 + 超大单净流入放大 + 量能跃升）→ ≥50（过 confirm 门槛）。"""
        volume = _late_shift_series(300, 1000.0, 50.0, seed=1)
        margin = _late_shift_series(300, 1.2e11, 5e9, seed=2)   # 融资余额末段攀升
        xl = _late_shift_series(300, 1e8, 5e7, seed=3)          # 超大单净流入末段放大
        s = s2_fund_score(volume, margin_balance=margin, xl_order_inflow=xl)
        assert s.iloc[-1] >= 50

    def test_all_sources_weak_gives_low(self):
        """三源低迷（融资余额末段新低 + 超大单流出 + 缩量）→ 0。"""
        volume = _late_shift_series(300, 1000.0, -50.0, seed=1)
        margin = _late_shift_series(300, 1.2e11, -5e9, seed=2)  # 末段骤降（出清中）
        xl = _late_shift_series(300, 1e8, -5e7, seed=3)
        s = s2_fund_score(volume, margin_balance=margin, xl_order_inflow=xl)
        assert s.iloc[-1] == 0

    def test_volume_only_proxy_capped(self):
        """成交量代理偏弱（memo 核心批评）：量升但融资余额/超大单不升 → 加权分远低于纯量路径。"""
        volume = _late_shift_series(300, 1000.0, 50.0, seed=1)   # 量能末段跃升
        margin = _late_shift_series(300, 1.2e11, -5e9, seed=2)   # 融资余额末段骤降（散户接盘式上涨）
        xl = _late_shift_series(300, 1e8, -5e7, seed=3)          # 超大单末段流出
        s_upgraded = s2_fund_score(volume, margin_balance=margin, xl_order_inflow=xl)
        s_legacy = s2_fund_score(volume)
        # 升级路径识别"散户接盘"（两资金源低迷拖累加权分），评分显著低于纯量路径
        assert s_upgraded.iloc[-1] < s_legacy.iloc[-1]

    def test_margin_only_injection_renormalized(self):
        """仅注入融资余额：权重按可用源归一化（margin 0.4 + volume 0.25 → 0.615/0.385）。"""
        volume = _late_shift_series(300, 1000.0, -50.0, seed=1)  # 缩量（分位低）
        margin = _late_shift_series(300, 1.2e11, 5e9, seed=2)    # 融资余额末段攀升（分位高）
        s = s2_fund_score(volume, margin_balance=margin)
        # composite ≈ 0.615×1.0 + 0.385×~0 ≈ 0.615 → 落 >0.60 档 = 50
        assert s.iloc[-1] == 50

    def test_xl_only_injection_renormalized(self):
        """仅注入超大单：权重 xl 0.35 + volume 0.25 → 0.583/0.417。"""
        volume = _late_shift_series(300, 1000.0, -50.0, seed=1)
        xl = _late_shift_series(300, 1e8, 5e7, seed=3)
        s = s2_fund_score(volume, xl_order_inflow=xl)
        # composite ≈ 0.583×1.0 + 0.417×~0 ≈ 0.583 → 落 >0.40 档 = 25
        assert s.iloc[-1] == 25

    def test_warmup_all_nan_gives_zero(self):
        """预热期（数据 < pct_window min_periods）全 NaN → 0（无信号不干预）。"""
        volume = _late_shift_series(30, 1000.0, 50.0, shift_bars=10, seed=1)
        margin = _late_shift_series(30, 1.2e11, 5e9, shift_bars=10, seed=2)
        s = s2_fund_score(volume, margin_balance=margin)
        assert (s == 0).all()

    def test_partial_nan_margin_tolerated(self):
        """融资余额中段 NaN（数据源缺口）：按可用源归一化不抛错。"""
        volume = _late_shift_series(300, 1000.0, 50.0, seed=1)
        margin = _late_shift_series(300, 1.2e11, 5e9, seed=2)
        margin.iloc[100:120] = np.nan
        s = s2_fund_score(volume, margin_balance=margin)
        assert not s.isna().any()
        assert s.iloc[-1] >= 50
