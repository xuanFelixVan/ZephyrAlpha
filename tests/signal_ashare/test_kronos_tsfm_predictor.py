# [BLUEPRINT] MOD-SIG-050 | docs/03_modules/MOD-SIG-050/
# [MODULE] tests.signal_ashare.test_kronos_tsfm_predictor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/signal_ashare/test_kronos_tsfm_predictor.py -q
# [TTL] permanent

"""Kronos TSFM 时序预测骨架（MOD-SIG-050）单元测试——接口契约/输入校验/未训练 fail-closed。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.kronos_tsfm_predictor import (
    KronosTsfmPredictor,
    TsfmConfig,
    TsfmPrediction,
)


class TestConfig:
    def test_default_config(self):
        cfg = TsfmConfig()
        assert cfg.horizon == 1
        assert cfg.max_lookback > 0

    def test_invalid_horizon_rejected(self):
        with pytest.raises(ValueError):
            TsfmConfig(horizon=0)
        with pytest.raises(ValueError):
            TsfmConfig(max_lookback=0)


class TestFailClosed:
    def test_predict_before_fit_raises(self):
        p = KronosTsfmPredictor()
        with pytest.raises(ValueError, match="未训练"):
            p.predict(np.array([1.0, 2.0, 3.0]))

    def test_load_checkpoint_missing_file_raises(self, tmp_path):
        p = KronosTsfmPredictor()
        with pytest.raises(ValueError):
            p.load_checkpoint(tmp_path / "nope.bin")

    def test_load_checkpoint_marks_ready(self, tmp_path):
        ckpt = tmp_path / "ckpt.bin"
        ckpt.write_bytes(b"placeholder")
        p = KronosTsfmPredictor()
        p.load_checkpoint(ckpt)
        assert p.is_ready is True


class TestInputValidation:
    def _fitted(self) -> KronosTsfmPredictor:
        p = KronosTsfmPredictor()
        p.fit_baseline(np.arange(20, dtype=float))
        return p

    def test_empty_series_rejected(self):
        with pytest.raises(ValueError):
            self._fitted().predict(np.array([]))

    def test_non_finite_series_rejected(self):
        with pytest.raises(ValueError):
            self._fitted().predict(np.array([1.0, np.nan, 3.0]))

    def test_lookback_truncated_to_config(self):
        p = KronosTsfmPredictor(TsfmConfig(horizon=2, max_lookback=5))
        p.fit_baseline(np.arange(100, dtype=float))
        pred = p.predict(np.arange(100, dtype=float))
        assert isinstance(pred, TsfmPrediction)
        assert len(pred.values) == 2


class TestBaselinePrediction:
    def test_baseline_prediction_shape_and_flag(self):
        p = KronosTsfmPredictor(TsfmConfig(horizon=3))
        p.fit_baseline(np.array([10.0, 11.0, 12.0]))
        pred = p.predict(np.array([10.0, 11.0, 12.0]))
        assert pred.values.shape == (3,)
        assert pred.is_baseline is True
        assert np.all(np.isfinite(pred.values))

    def test_fit_baseline_rejects_short_series(self):
        p = KronosTsfmPredictor()
        with pytest.raises(ValueError):
            p.fit_baseline(np.array([1.0]))
