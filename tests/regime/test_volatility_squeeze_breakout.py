# [BLUEPRINT] MOD-REGIME-013 | docs/03_modules/_domain_regime/volatility_squeeze_breakout/blueprint.md | §test
# [MODULE] tests.regime.test_volatility_squeeze_breakout
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.volatility_squeeze_breakout
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_volatility_squeeze_breakout.py
# [A_test] module_id: MOD-REGIME-013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-013 单元测试: 模块51 波动率压缩与突破模型。

覆盖: RV_5d/RV_20d<0.5 强压缩腿 + 布林带宽分位<10% 腿联合判定（单腿不联合）、
突破方向概率口径（价格位置/量能方向等权，非压缩期中性 0.5 不干预）、RV 扩张
+放量 3 日维持确认与方向、样本不足降级不抛错、配置非法 Fail-Closed、
overlay_dims 契约（score∈[0,100]/flag∈{0,1}/无信号=0）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.regime.volatility_squeeze_breakout import (
    SqueezeConfig,
    SqueezeConfigError,
    VolatilitySqueezeBreakout,
)


def _closes_from_returns(returns: list[float], start: float = 100.0) -> np.ndarray:
    closes = [start]
    for r in returns:
        closes.append(closes[-1] * (1.0 + r))
    return np.array(closes)


def _flat_returns(n: int, amp: float = 0.0005) -> list[float]:
    """低波横盘：交替微幅涨跌（RV 极小）。"""
    return [amp if i % 2 == 0 else -amp for i in range(n)]


class TestConfigFailClosed:
    def test_defaults_valid(self):
        SqueezeConfig()

    def test_rv_windows(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(rv_short_window=1)
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(rv_short_window=20, rv_long_window=20)

    def test_strong_threshold_range(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(strong_compression_threshold=1.0)
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(strong_compression_threshold=0.0)

    def test_percentile_range(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(bb_percentile_threshold=0.0)
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(bb_percentile_threshold=1.0)

    def test_sustain_days(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(sustain_days=0)

    def test_expansion_thresholds(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(confirm_rv_expansion=1.0)
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(confirm_volume_expansion=0.5)

    def test_min_history(self):
        with pytest.raises(SqueezeConfigError):
            SqueezeConfig(min_history=10)


class TestDegrade:
    def test_insufficient_history_degraded(self):
        model = VolatilitySqueezeBreakout()
        closes = _closes_from_returns(_flat_returns(30))
        sig = model.assess(closes, np.full(31, 1000.0))
        assert sig.degraded is True
        assert sig.squeeze_flag == 0
        assert sig.confirmed == 0
        assert sig.overlay_dims() == {
            "vol_squeeze": 0,
            "breakout_dir_score": 0.0,
            "breakout_confirmed": 0,
        }

    def test_length_mismatch_fail_closed(self):
        model = VolatilitySqueezeBreakout()
        closes = _closes_from_returns(_flat_returns(80))
        with pytest.raises(SqueezeConfigError):
            model.assess(closes, np.full(10, 1000.0))

    def test_non_finite_filtered_then_degrade(self):
        model = VolatilitySqueezeBreakout(SqueezeConfig(min_history=40))
        returns = _flat_returns(30) + [float("nan")] * 50
        closes = _closes_from_returns([r if np.isfinite(r) else 0.0 for r in returns])
        closes[31:] = np.nan  # 非有限收盘价
        sig = model.assess(closes, np.full(len(closes), 1000.0))
        assert sig.degraded is True


class TestSqueezeLegs:
    def _make_squeeze_data(self):
        """前段 102 日正常波动（建立带宽基线），尾段 18 日极平（RV 压缩+带宽极窄）。

        尾段须 <20 日：rv20 窗口内须仍含高波日，rv_ratio 才 <0.5（否则 rv20
        自身已走平，比值回 1）。
        """
        normal = [0.012 if i % 3 else -0.011 for i in range(102)]
        tail = _flat_returns(18, amp=0.0002)
        closes = _closes_from_returns(normal + tail)
        volumes = np.full(len(closes), 1000.0)
        return closes, volumes

    def test_strong_compression_detected(self):
        model = VolatilitySqueezeBreakout()
        closes, volumes = self._make_squeeze_data()
        sig = model.assess(closes, volumes)
        assert sig.degraded is False
        assert sig.rv_ratio < 0.5
        assert sig.strong_rv_leg == 1
        assert sig.bb_width_percentile < 0.10
        assert sig.bb_squeeze_leg == 1
        assert sig.squeeze_flag == 1

    def test_single_leg_not_joint(self):
        """RV 强压缩命中但带宽分位不低（高低波交替，带宽历史同水平）→ 不联合。"""
        model = VolatilitySqueezeBreakout()
        # 10 日高波 + 10 日低波交替 ×6（尾块为低波）：rv5 极小、rv20 混合仍高
        # → RV 腿命中；20 窗恒为 10高+10低 → 带宽全程同水平 → 分位=1.0 → BB 腿不命中
        block = [0.008 if i % 2 == 0 else -0.008 for i in range(10)] + _flat_returns(10, amp=0.0002)
        returns = block * 6
        closes = _closes_from_returns(returns)
        sig = model.assess(closes, np.full(len(closes), 1000.0))
        assert sig.strong_rv_leg == 1  # RV 腿命中
        assert sig.bb_squeeze_leg == 0  # 带宽历史同水平 → 分位不低
        assert sig.squeeze_flag == 0

    def test_no_squeeze_trending(self):
        model = VolatilitySqueezeBreakout()
        trending = [0.015] * 119  # 持续单边，RV 不小、带宽不窄
        closes = _closes_from_returns(trending)
        sig = model.assess(closes, np.full(len(closes), 1000.0))
        assert sig.squeeze_flag == 0
        assert sig.p_up == 0.5  # 非压缩期方向中性不干预
        assert sig.p_down == 0.5
        assert sig.overlay_dims()["breakout_dir_score"] == 0.0


class TestDirectionProbability:
    def test_up_bias_in_squeeze(self):
        model = VolatilitySqueezeBreakout()
        # 前段 102 日正常，尾段 18 日压缩但收于区间上沿且上涨日放量
        normal = [0.012 if i % 3 else -0.011 for i in range(102)]
        tail = [0.0004 if i % 2 == 0 else -0.0001 for i in range(18)]  # 偏多微涨
        closes = _closes_from_returns(normal + tail)
        volumes = np.array([1000.0] * len(closes))
        # 尾段上涨日放量、下跌日缩量
        for i in range(len(closes) - 18, len(closes)):
            volumes[i] = 1600.0 if closes[i] >= closes[i - 1] else 600.0
        sig = model.assess(closes, volumes)
        assert sig.squeeze_flag == 1
        assert sig.p_up > 0.5
        assert sig.p_down == pytest.approx(1.0 - sig.p_up)
        assert sig.overlay_dims()["vol_squeeze"] == 1
        assert sig.overlay_dims()["breakout_dir_score"] == pytest.approx(sig.p_up * 100.0)


class TestConfirmation:
    def _make_breakout_data(self, sustain: int = 3, direction: float = 1.0):
        """前段 116 日平静（低 RV 低量），尾部 sustain 日递增单边+3倍量。

        突破日收益递增（1%/2%/5% 取尾部 sustain 日）：等额连涨下 rv5/rv20
        结构性上限 ≈1.495（偏差均值效应），递增序列方使 RV 扩张比稳超 1.5。
        """
        calm = _flat_returns(116, amp=0.0005)
        burst_seq = [direction * 0.01, direction * 0.02, direction * 0.05]
        burst = burst_seq[-sustain:]
        closes = _closes_from_returns(calm + burst)
        volumes = np.array([1000.0] * (len(closes) - sustain) + [3000.0] * sustain)
        return closes, volumes

    def test_three_day_sustain_confirmed_up(self):
        model = VolatilitySqueezeBreakout()
        closes, volumes = self._make_breakout_data(sustain=3, direction=1.0)
        sig = model.assess(closes, volumes)
        assert sig.confirmed == 1
        assert sig.confirm_direction == "up"
        assert sig.sustain_hits >= 3
        assert sig.overlay_dims()["breakout_confirmed"] == 1

    def test_three_day_sustain_confirmed_down(self):
        model = VolatilitySqueezeBreakout()
        closes, volumes = self._make_breakout_data(sustain=3, direction=-1.0)
        sig = model.assess(closes, volumes)
        assert sig.confirmed == 1
        assert sig.confirm_direction == "down"

    def test_two_day_burst_not_confirmed(self):
        model = VolatilitySqueezeBreakout()
        closes, volumes = self._make_breakout_data(sustain=2, direction=1.0)
        sig = model.assess(closes, volumes)
        assert sig.confirmed == 0
        assert sig.confirm_direction is None

    def test_burst_without_volume_not_confirmed(self):
        model = VolatilitySqueezeBreakout()
        closes, volumes = self._make_breakout_data(sustain=3, direction=1.0)
        volumes[:] = 1000.0  # 无量突破
        sig = model.assess(closes, volumes)
        assert sig.confirmed == 0
