# [BLUEPRINT] MOD-REGIME-011 | docs/03_modules/_domain_regime/volatility_regime_alerter/blueprint.md | §test
# [MODULE] tests.regime.test_volatility_regime_alerter
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.volatility_regime_alerter
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_volatility_regime_alerter.py
# [A_test] module_id: MOD-REGIME-011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-011 单元测试: 波动率体制转换与关键时点预警。

覆盖: GARCH(1,1) 日频波动预测（自研复用 MOD-RK-26，不引 arch 库）、
RV_5d/RV_20d 压缩标记、波动突变告警、overlay 维度契约（score∈[0,100]/flag∈{0,1}/
无信号=0）、样本不足与 GARCH 不收敛降级（不抛错）、配置 Fail-Closed。
"""

from __future__ import annotations

import sys

import numpy as np
import pytest

from zephyr.regime.volatility_regime_alerter import (
    VolatilityAlerterConfigError,
    VolatilityRegimeAlerter,
    VolAlerterConfig,
)


def _garch_like_returns(n: int = 120, seed: int = 7, spike_last: bool = False) -> np.ndarray:
    """合成波动聚集收益序列；spike_last=True 时尾 10 日波动骤升+末日极端冲击。"""
    rng = np.random.default_rng(seed)
    vol = np.full(n, 0.01)
    if spike_last:
        vol[-10:] = 0.08  # 末日段波动骤升
    r = rng.normal(0.0, vol)
    if spike_last:
        r[-1] = -0.30  # 末日极端负冲击（驱动 GARCH sigma_forecast 骤升）
    return r


class TestNoArchDependency:
    def test_arch_package_not_imported(self):
        """项目裁定：自研 GARCH（L-BFGS-B QMLE，fhs_engine 先例），禁止引 arch 库。"""
        assert "arch" not in sys.modules


class TestCompressionFlag:
    def test_rv_compression_detected(self):
        """近 5 日波动远低于 20 日基线 → 压缩标记=1。"""
        rng = np.random.default_rng(11)
        base = rng.normal(0.0, 0.03, 80)  # 前段高波
        calm = rng.normal(0.0, 0.003, 8)  # 近段骤降
        returns = np.concatenate([base, calm])
        sig = VolatilityRegimeAlerter().assess(returns)
        assert sig.rv_ratio < 0.8
        assert sig.overlay_dims()["vol_compression"] == 1

    def test_no_compression_when_uniform(self):
        returns = _garch_like_returns(120, seed=3)
        sig = VolatilityRegimeAlerter().assess(returns)
        assert sig.overlay_dims()["vol_compression"] == 0  # 无信号=0（不干预）


class TestVolShiftAlert:
    def test_shift_alert_on_vol_spike(self):
        """尾部波动骤升 → GARCH 预测 sigma_forecast 显著高于 RV_20d → 突变告警=1。"""
        returns = _garch_like_returns(150, seed=5, spike_last=True)
        sig = VolatilityRegimeAlerter().assess(returns)
        assert sig.garch_available
        assert sig.shift_ratio >= 1.5
        assert sig.overlay_dims()["vol_shift_alert"] == 1

    def test_overlay_dims_contract(self):
        returns = _garch_like_returns(150, seed=5, spike_last=True)
        dims = VolatilityRegimeAlerter().assess(returns).overlay_dims()
        assert set(dims) == {"vol_compression", "vol_shift_alert", "vol_forecast_score"}
        assert dims["vol_compression"] in (0, 1)
        assert dims["vol_shift_alert"] in (0, 1)
        assert 0.0 <= dims["vol_forecast_score"] <= 100.0


class TestDegradation:
    def test_short_history_degrades_not_raises(self):
        sig = VolatilityRegimeAlerter().assess(np.array([0.01, -0.02, 0.005]))
        assert sig.degraded
        assert all(v == 0 for v in sig.overlay_dims().values())  # 降级=全 0 不干预

    def test_nonfinite_filtered(self):
        returns = _garch_like_returns(80, seed=9)
        returns[::17] = np.nan  # 撒 NaN（占比 < 5% 上限）
        sig = VolatilityRegimeAlerter().assess(returns)
        assert not sig.degraded


class TestConfigGuard:
    def test_invalid_compression_threshold(self):
        with pytest.raises(VolatilityAlerterConfigError):
            VolAlerterConfig(compression_threshold=1.5)

    def test_invalid_shift_threshold(self):
        with pytest.raises(VolatilityAlerterConfigError):
            VolAlerterConfig(shift_threshold=0.5)

    def test_rv_windows_ordered(self):
        with pytest.raises(VolatilityAlerterConfigError):
            VolAlerterConfig(rv_short_window=20, rv_long_window=5)
