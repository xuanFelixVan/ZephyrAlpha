# [BLUEPRINT] MOD-PA-021 | docs/03_modules/_domain_portfolio_alloc/forward_stop_loss/blueprint.md
# [MODULE] tests.pf_alloc.test_forward_stop_loss
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.pf_alloc.core.forward_stop_loss
# [CONSUMERS] forward_stop_loss 质量守卫
# [STARTUP] manual
# [INVARIANTS] 纯合成数据；边界与逻辑断言
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-PA-021 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""forward_stop_loss 质量守卫——概率止损信号+复合评分测试。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.pf_alloc.core.forward_stop_loss import (
    composite_stop_score,
    forward_stop_signal,
)


class TestForwardStopSignal:
    def test_basic_output(self):
        rng = np.random.default_rng(42)
        rets = pd.Series(rng.normal(0, 0.01, 100), index=pd.bdate_range("2020-01-01", periods=100))
        result = forward_stop_signal(rets, window=20, decline_threshold=0.65)
        assert "neg_prob" in result.columns
        assert "stop_review" in result.columns
        assert len(result) == 100

    def test_persistent_decline_triggers(self):
        dates = pd.bdate_range("2020-01-01", periods=40)
        rets = pd.Series([-0.01] * 40, index=dates)  # 持续下跌
        result = forward_stop_signal(rets, window=10, decline_threshold=0.65)
        assert result["stop_review"].iloc[-1]

    def test_persistent_rally_no_trigger(self):
        dates = pd.bdate_range("2020-01-01", periods=40)
        rets = pd.Series([0.01] * 40, index=dates)  # 持续上涨
        result = forward_stop_signal(rets, window=10, decline_threshold=0.65)
        assert not result["stop_review"].any()

    def test_invalid_threshold_rejected(self):
        rets = pd.Series([0.01] * 20)
        with pytest.raises(ValueError):
            forward_stop_signal(rets, decline_threshold=0.3)

    def test_invalid_window_rejected(self):
        with pytest.raises(ValueError):
            forward_stop_signal(pd.Series([0.01] * 10), window=3, min_observations=5)


class TestCompositeStopScore:
    def _make_quantile_pred(self, n: int = 50, offset: float = 0.0):
        dates = pd.bdate_range("2022-01-03", periods=n)
        rng = np.random.default_rng(7)
        q50 = pd.Series(rng.normal(offset, 0.01, n), index=dates)
        q05 = q50 - 0.02
        q95 = q50 + 0.02
        return pd.DataFrame({"q05": q05, "q50": q50, "q95": q95}, index=dates)

    def test_negative_median_triggers(self):
        pred = self._make_quantile_pred(50, offset=-0.03)
        realized = pd.Series(0, index=pred.index)
        result = composite_stop_score(pred, realized)
        assert result["stop_review"].sum() > 0

    def test_positive_median_no_trigger(self):
        pred = self._make_quantile_pred(50, offset=0.01)
        realized = pd.Series(0, index=pred.index)
        result = composite_stop_score(pred, realized)
        assert result["stop_review"].sum() < 25
