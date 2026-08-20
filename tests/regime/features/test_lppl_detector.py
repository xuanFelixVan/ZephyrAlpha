# [A_test] module_id: MOD-TEST-LPPL | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.8.1
# [MODULE] tests.regime.features.test_lppl_detector
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.lppl_detector; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_lppl_detector.py
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.8.1 LPPL 赶顶检测（T4）
# [ALGO_FLOW]
# 层: 输入
# - I1: close 价格序列（多窗口拟合：60/90/120 交易日）
# 层: 算法
# - A1: LPPL 线性化拟合（固定 tc/m/ω 网格，lstsq 解 A/B/C1/C2）
# - A2: 五维评分：m∈(0.1,0.9)+20 / ω∈(5,15)+20 / tc 中位≤20 日+25 /
#       有效窗口占比>50%+15 / tc 标准差<20 日+10
# 层: 输出
# - O1: LPPLResult（score 0-90 + 五组件 + valid_window_ratio）
"""test_lppl_detector.py — 10 号 §4.8.1 LPPL 赶顶检测（T4）独立函数单元测试。

覆盖：
  1. 合成 LPPL 泡沫（已知 m=0.5/ω=8/tc=N+10）→ 高分（≥60，T4 触发门槛 LPPL≥40）
  2. tc 远离（N+55）→ 临界时间维度不得分
  3. 随机游走（无泡沫结构）→ 低分（<40）
  4. 平盘序列 → 0（B<0 泡沫方向不满足，无有效窗口）
  5. 退化：序列过短 → degraded score=0；非正价格 → ValueError
  6. 结果结构：valid_window_ratio∈[0,1]，组件齐备

依据: 10_regime_detector_spec §4.8.1（Johansen & Sornette / 国金宏观 2026-06 实证）
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.lppl_detector import LPPLResult, lppl_blowoff_score


def _synthetic_lppl(n: int = 180, tc_ahead: float = 10.0,
                    m: float = 0.5, omega: float = 8.0) -> pd.Series:
    """按 LPPL 公式合成泡沫价格序列（已知参数）。"""
    t = np.arange(1, n + 1, dtype=float)
    tc = n + tc_ahead
    dt = tc - t
    a, b, c, phi = 9.0, -0.5, 0.04, 0.5
    ln_p = a + b * dt**m + c * dt**m * np.cos(omega * np.log(dt) - phi)
    return pd.Series(np.exp(ln_p))


class TestLPPLBubbleDetection:
    def test_synthetic_bubble_high_score(self):
        """合成 LPPL 泡沫（m=0.5/ω=8/tc=N+10）→ 高分（≥60，过 T4 LPPL≥40 门槛）。"""
        close = _synthetic_lppl()
        r = lppl_blowoff_score(close)
        assert r.score >= 60
        assert r.valid_window_ratio > 0.5

    def test_synthetic_bubble_recovers_params(self):
        """参数回收：m/ω 中位数落在真值网格附近，tc 中位 ≈ 10 交易日。"""
        close = _synthetic_lppl()
        r = lppl_blowoff_score(close)
        assert r.m_median == pytest.approx(0.5, abs=0.15)
        assert r.omega_median == pytest.approx(8.0, abs=1.5)
        assert r.tc_median_days == pytest.approx(10.0, abs=6.0)

    def test_tc_far_no_proximity_points(self):
        """tc=N+55（远离当前 ±20 日带）→ 临界时间维度（+25）不得分。"""
        close = _synthetic_lppl(tc_ahead=55.0)
        r = lppl_blowoff_score(close)
        assert r.tc_median_days is not None and r.tc_median_days > 20
        # 总分不含临界时间 25 分（满分变 65）
        assert r.score <= 65


class TestLPPLNoBubble:
    def test_random_walk_low_score(self):
        """随机游走（无超指数加速结构）→ 低分（<40，不过 T4 门槛）。"""
        rng = np.random.default_rng(42)
        rets = rng.normal(0.0005, 0.012, 180)
        close = pd.Series(3000.0 * np.exp(np.cumsum(rets)))
        r = lppl_blowoff_score(close)
        assert r.score < 40

    def test_flat_series_zero(self):
        """平盘序列：B<0（泡沫方向）不满足 → 无有效窗口 → 0。"""
        close = pd.Series(np.full(180, 100.0))
        r = lppl_blowoff_score(close)
        assert r.score == 0
        assert r.valid_window_ratio == 0.0


class TestLPPLEdgeCases:
    def test_short_series_degraded(self):
        """序列 < 最短窗口 → degraded，score=0，不抛错。"""
        close = pd.Series(np.linspace(100, 110, 30))
        r = lppl_blowoff_score(close)
        assert r.score == 0
        assert r.degraded is True

    def test_non_positive_price_raises(self):
        with pytest.raises(ValueError, match="正"):
            lppl_blowoff_score(pd.Series([100.0, 0.0, 101.0] * 40))

    def test_result_structure(self):
        close = _synthetic_lppl()
        r = lppl_blowoff_score(close)
        assert isinstance(r, LPPLResult)
        assert 0.0 <= r.valid_window_ratio <= 1.0
        assert r.windows_evaluated >= 1
