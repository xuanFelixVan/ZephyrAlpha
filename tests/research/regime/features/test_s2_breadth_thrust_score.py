# [A_test] module_id: MOD-TEST-S2-BREADTH-THRUST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4 P1-E9d
# [MODULE] tests.regime.features.test_s2_breadth_thrust_score
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.features.overlay_features; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/regime/features/test_s2_breadth_thrust_score.py
# [TTL] permanent
# [ARCH-REF] #P1-E9d #14_regime_s2_diagnosis §4.4
# [ALGO_FLOW]
# 层: 输入
# - I1: adv_issues/dec_issues（涨跌家数，399106 广度指数）+ ema_window=10
# 层: 算法
# - A1: breadth_ratio=adv/(adv+dec) → 10 日 EMA
# - A2: 分档映射（>0.55→30 / >0.615→60 / 10日内曾<0.40且当前>0.615 完整 thrust→80）
# 层: 输出
# - O1: pd.Series ∈ {0,30,60,100→80}（confirm 析取门槛 60）
"""test_s2_breadth_thrust_score.py — P1-E9d Zweig Breadth Thrust V 反转通路单元测试。

覆盖（14_regime_s2_diagnosis §4.4 + §4.5 step 1 stub 要求）：
  1. 完整 thrust：10 日窗口内 EMA 曾 <0.40（washout）且当前 >0.615 → 80
  2. V 反转场景：无深洗盘但广度急升（EMA>0.615）→ 60（confirm 析取可达）
  3. EMA>0.55 未达 thrust → 30；常态 → 0
  4. washout 落在窗口中段（非恰好 -10 日）也判完整 thrust（rolling.min 语义）
  5. 退化输入：adv+dec=0 / 全零序列 → 0

依据: 14_regime_s2_diagnosis v0.4.5 §4.4 / §4.5
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.regime.features.overlay_features import s2_breadth_thrust_score

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _adv_dec_from_ratio(ratios: list[float]) -> tuple[pd.Series, pd.Series]:
    """按目标上涨占比构造 adv/dec 家数（总量恒 5000）。"""
    r = pd.Series(ratios, dtype=float)
    return r * 5000.0, (1.0 - r) * 5000.0


# ---------------------------------------------------------------------------
# 1. 完整 thrust / 分档映射
# ---------------------------------------------------------------------------


class TestBreadthThrustMapping:
    def test_full_thrust_80(self):
        """washout（ratio 0.30×15 日）→ 急升（0.80×10 日）：EMA 从 <0.40 → >0.615 → 80。"""
        ratios = [0.30] * 15 + [0.80] * 10
        adv, dec = _adv_dec_from_ratio(ratios)
        out = s2_breadth_thrust_score(adv, dec)
        assert out.iloc[-1] == 80

    def test_v_reversal_no_washout_60(self):
        """V 反转无深洗盘：ratio 恒 0.70（EMA>0.615 但无 <0.40 起点）→ 60（达析取门槛）。"""
        adv, dec = _adv_dec_from_ratio([0.70] * 30)
        out = s2_breadth_thrust_score(adv, dec)
        assert out.iloc[-1] == 60

    def test_improving_breadth_30(self):
        """ratio 恒 0.58（EMA>0.55 未达 0.615）→ 30。"""
        adv, dec = _adv_dec_from_ratio([0.58] * 30)
        assert s2_breadth_thrust_score(adv, dec).iloc[-1] == 30

    def test_normal_market_zero(self):
        """ratio 恒 0.50（涨跌各半）→ 0。"""
        adv, dec = _adv_dec_from_ratio([0.50] * 30)
        assert s2_breadth_thrust_score(adv, dec).iloc[-1] == 0.0

    def test_washout_mid_window_counts(self):
        """washout 低点落在窗口中段（-5 日）而非恰好 -10 日 → 仍判完整 thrust（80）。

        v0.4.1 bug 修正实证：ema.shift(10) 只看恰好 -10 日会漏判此情形，
        rolling(10).min().shift(1) 取窗口内最低 EMA 匹配"10 日内曾 washout"语义。
        """
        # 前 20 日温和 0.55 → 5 日急杀 0.30（washout 在窗口中段）→ 8 日急升 0.85
        ratios = [0.55] * 20 + [0.30] * 5 + [0.85] * 8
        adv, dec = _adv_dec_from_ratio(ratios)
        out = s2_breadth_thrust_score(adv, dec)
        assert out.iloc[-1] == 80


# ---------------------------------------------------------------------------
# 2. 退化输入
# ---------------------------------------------------------------------------


class TestDegenerateInputs:
    def test_zero_issues_zero(self):
        """adv+dec=0（数据断更填 0）→ ratio≈0 → 0（不误触发）。"""
        adv = pd.Series(np.zeros(30))
        dec = pd.Series(np.zeros(30))
        assert (s2_breadth_thrust_score(adv, dec) == 0.0).all()

    def test_persistent_decline_zero(self):
        """持续普跌（ratio 0.30）→ EMA<0.40 → 0（washout 本身不给分，须反转确认）。"""
        adv, dec = _adv_dec_from_ratio([0.30] * 30)
        assert s2_breadth_thrust_score(adv, dec).iloc[-1] == 0.0

    def test_return_value_domain(self):
        """值域 ⊆ {0,30,60,80}。"""
        ratios = [0.30] * 15 + [0.80] * 15
        adv, dec = _adv_dec_from_ratio(ratios)
        out = s2_breadth_thrust_score(adv, dec)
        assert set(out.unique()).issubset({0.0, 30.0, 60.0, 80.0})
