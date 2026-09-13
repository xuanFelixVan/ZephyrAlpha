# [BLUEPRINT] MOD-PA-027 | docs/03_modules/_domain_portfolio_alloc/risk_budget_allocator/blueprint.md
# [MODULE] tests.pf_alloc.test_risk_budget_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.pf_alloc.core.risk_budget_allocator
# [CONSUMERS] risk_budget_allocator 质量守卫
# [STARTUP] manual
# [INVARIANTS] 纯合成数据；权重和=1.0
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-PA-027 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""risk_budget_allocator 质量守卫——三种分配模式+边界测试。"""

from __future__ import annotations

import pytest

from zephyr.pf_alloc.core.risk_budget_allocator import (
    predicted_cvar,
    predicted_var,
    risk_budget_allocate,
)


class TestRiskBudgetAllocate:
    def test_inverse_var_weights_sum_to_one(self):
        var = {"A": 0.01, "B": 0.04, "C": 0.02}
        w = risk_budget_allocate(var, mode="inverse_var")
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert all(0 <= v for v in w.values())

    def test_low_risk_gets_more_weight(self):
        var = {"A": 0.01, "B": 0.04}
        w = risk_budget_allocate(var, mode="inverse_var")
        assert w["A"] > w["B"]

    def test_risk_parity_mode(self):
        var = {"A": 0.01, "B": 0.02, "C": 0.03}
        w = risk_budget_allocate(var, mode="risk_parity")
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert all(v > 0 for v in w.values())

    def test_sharpe_weight_requires_er(self):
        with pytest.raises(ValueError):
            risk_budget_allocate({"A": 0.01}, mode="sharpe_weight")

    def test_sharpe_weight_with_er(self):
        var = {"A": 0.01, "B": 0.02}
        er = {"A": 0.10, "B": 0.05}
        w = risk_budget_allocate(var, mode="sharpe_weight", er_estimates=er)
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert w["A"] > 0

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            risk_budget_allocate({}, mode="inverse_var")

    def test_invalid_mode_rejected(self):
        with pytest.raises(ValueError):
            risk_budget_allocate({"A": 0.01}, mode="unknown_mode")


class TestPredictedVar:
    def test_basic_var(self):
        import numpy as np
        import pandas as pd
        rng = np.random.default_rng(42)
        rets = pd.Series(rng.normal(0, 0.01, 200), index=pd.bdate_range("2020-01-01", periods=200))
        var = predicted_var(rets, confidence=0.05, window=60)
        assert len(var.dropna()) > 100
        assert (var.dropna() < 0).all()  # VaR 应为负（损失）

    def test_var_none_for_short_series(self):
        import numpy as np
        import pandas as pd
        rets = pd.Series([0.01, -0.005, 0.003], index=pd.bdate_range("2020-01-01", periods=3))
        var = predicted_var(rets, confidence=0.05, window=60)
        assert var.isna().all()
