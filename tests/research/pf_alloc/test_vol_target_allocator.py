# [BLUEPRINT] MOD-BT-083 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.pf_alloc.test_vol_target_allocator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; src.zephyr.pf_alloc.core.vol_target_allocator
# [CONSUMERS] vol_target_allocator 质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [INVARIANTS] 纯合成数据；边界与守恒断言
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-083 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""vol_target_allocator 单元测试（纯合成数据，无 IO）。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.zephyr.pf_alloc.core.vol_target_allocator import (
    kelly_full_weight,
    latest_weight,
    vol_target_weight,
)


def _returns(n: int = 300, mean: float = 0.0, vol: float = 0.01, seed: int = 11) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.Series(rng.normal(mean, vol, n), index=idx)


class TestVolTargetWeight:
    def test_output_bounds_and_length(self):
        k = vol_target_weight(_returns(), max_weight=1.0, min_weight=0.0)
        assert len(k) == 300
        assert (k >= 0.0).all() and (k <= 1.0).all()

    def test_warmup_is_min_weight(self):
        k = vol_target_weight(_returns(100), window=20)
        assert (k.iloc[:19] == 0.0).all()

    def test_high_vol_lowers_weight(self):
        calm = vol_target_weight(_returns(200, vol=0.005))
        wild = vol_target_weight(_returns(200, vol=0.04))
        assert calm.iloc[-1] >= wild.iloc[-1]

    def test_high_vol_regime_drops_weight(self):
        r = _returns(300, vol=0.005)
        r.iloc[200:] = r.iloc[200:] * 8  # 后段波动放大
        k = vol_target_weight(r)
        assert k.iloc[-1] < k.iloc[150]

    def test_zero_vol_gets_min_weight(self):
        flat = pd.Series(0.001, index=pd.bdate_range("2020-01-01", periods=100))
        k = vol_target_weight(flat)
        assert (k == 0.0).all()

    def test_deterministic(self):
        r = _returns(150)
        k1 = vol_target_weight(r)
        k2 = vol_target_weight(r.copy())
        assert k1.equals(k2)

    def test_latest_weight_returns_float(self):
        v = latest_weight(_returns(100))
        assert isinstance(v, float)
        assert 0.0 <= v <= 1.0

    def test_invalid_params_rejected(self):
        r = _returns(50)
        with pytest.raises(ValueError):
            vol_target_weight(r, window=1)
        with pytest.raises(ValueError):
            vol_target_weight(r, target_vol=0.0)
        with pytest.raises(ValueError):
            vol_target_weight(r, max_weight=0.2, min_weight=0.5)


class TestKellyFull:
    def test_positive_er_positive_sigma(self):
        k = kelly_full_weight(expected_return=0.01, sigma=0.20, max_weight=5.0, kelly_fraction=1.0)
        assert k == pytest.approx(0.01 / 0.04, abs=0.01)

    def test_negative_er_clamps_to_min(self):
        k = kelly_full_weight(expected_return=-0.10, sigma=0.20, kelly_fraction=1.0)
        assert k == 0.0

    def test_half_kelly_fraction(self):
        k_full = kelly_full_weight(expected_return=0.01, sigma=0.20, max_weight=5.0, kelly_fraction=1.0)
        k_half = kelly_full_weight(expected_return=0.01, sigma=0.20, max_weight=5.0, kelly_fraction=0.5)
        assert k_half == pytest.approx(k_full / 2, abs=0.01)

    def test_zero_sigma_returns_min(self):
        assert kelly_full_weight(expected_return=0.10, sigma=0.0) == 0.0

    def test_clamp_to_max(self):
        k = kelly_full_weight(expected_return=10.0, sigma=0.01, kelly_fraction=1.0)
        assert k <= 1.0
