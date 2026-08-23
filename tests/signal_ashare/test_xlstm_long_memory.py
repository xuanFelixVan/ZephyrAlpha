# [BLUEPRINT] MOD-SIG-053 | docs/03_modules/MOD-SIG-053/
# [MODULE] tests.signal_ashare.test_xlstm_long_memory
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/signal_ashare/test_xlstm_long_memory.py -q
# [TTL] permanent

"""xLSTM 长记忆骨架（MOD-SIG-053）单元测试——接口契约/输入校验/未训练 fail-closed。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.xlstm_long_memory import XLstmLongMemory


class TestFailClosed:
    def test_predict_before_fit_raises(self):
        m = XLstmLongMemory()
        with pytest.raises(ValueError, match="未训练"):
            m.predict(np.arange(10.0), horizon=2)

    def test_fit_rejects_short_or_dirty_series(self):
        m = XLstmLongMemory()
        with pytest.raises(ValueError):
            m.fit_baseline(np.array([1.0]))
        with pytest.raises(ValueError):
            m.fit_baseline(np.array([1.0, np.nan, 3.0]))


class TestBaseline:
    def test_predict_shape_and_finiteness(self):
        m = XLstmLongMemory(decay=0.9)
        m.fit_baseline(np.arange(50, dtype=float))
        pred = m.predict(np.arange(50, dtype=float), horizon=4)
        assert pred.shape == (4,)
        assert np.all(np.isfinite(pred))

    def test_horizon_validated(self):
        m = XLstmLongMemory()
        m.fit_baseline(np.arange(10, dtype=float))
        with pytest.raises(ValueError):
            m.predict(np.arange(10.0), horizon=0)

    def test_decay_bounds_validated(self):
        with pytest.raises(ValueError):
            XLstmLongMemory(decay=0.0)
        with pytest.raises(ValueError):
            XLstmLongMemory(decay=1.5)

    def test_memory_state_summary(self):
        m = XLstmLongMemory()
        m.fit_baseline(np.arange(20, dtype=float))
        summary = m.memory_summary()
        assert summary["fitted"] is True
        assert summary["decay"] > 0
