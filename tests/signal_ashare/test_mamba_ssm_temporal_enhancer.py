# [BLUEPRINT] MOD-SIG-051 | docs/03_modules/MOD-SIG-051/
# [MODULE] tests.signal_ashare.test_mamba_ssm_temporal_enhancer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/signal_ashare/test_mamba_ssm_temporal_enhancer.py -q
# [TTL] permanent

"""Mamba-SSM 时序增强器骨架（MOD-SIG-051）单元测试——接口契约/输入校验/未训练 fail-closed。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.mamba_ssm_temporal_enhancer import (
    MambaSsmTemporalEnhancer,
)


class TestFailClosed:
    def test_enhance_before_fit_raises(self):
        e = MambaSsmTemporalEnhancer()
        with pytest.raises(ValueError, match="未训练"):
            e.enhance(np.ones((5, 3)))

    def test_fit_rejects_bad_input(self):
        e = MambaSsmTemporalEnhancer()
        with pytest.raises(ValueError):
            e.fit(np.array([]))
        with pytest.raises(ValueError):
            e.fit(np.array([[1.0, np.nan]]))


class TestEnhance:
    def test_output_shape_preserved(self):
        e = MambaSsmTemporalEnhancer(smoothing=0.5)
        x = np.arange(30, dtype=float).reshape(10, 3)
        e.fit(x)
        out = e.enhance(x)
        assert out.shape == x.shape
        assert np.all(np.isfinite(out))

    def test_zero_std_column_safe(self):
        e = MambaSsmTemporalEnhancer()
        x = np.column_stack([np.ones(10), np.arange(10, dtype=float)])
        e.fit(x)
        out = e.enhance(x)
        assert np.all(np.isfinite(out))

    def test_enhance_dim_mismatch_rejected(self):
        e = MambaSsmTemporalEnhancer()
        e.fit(np.ones((10, 3)))
        with pytest.raises(ValueError):
            e.enhance(np.ones((10, 4)))

    def test_smoothing_bounds_validated(self):
        with pytest.raises(ValueError):
            MambaSsmTemporalEnhancer(smoothing=0.0)
        with pytest.raises(ValueError):
            MambaSsmTemporalEnhancer(smoothing=1.5)
