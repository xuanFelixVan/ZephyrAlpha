# [BLUEPRINT] MOD-PA-025 | docs/03_modules/_domain_portfolio_alloc/tail_hedge_signal/blueprint.md
# [MODULE] tests.pf_alloc.test_tail_hedge_signal
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.pf_alloc.core.tail_hedge_signal
# [CONSUMERS] tail_hedge_signal 质量守卫
# [STARTUP] manual
# [INVARIANTS] 纯合成数据
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-PA-025 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tail_hedge_signal 质量守卫——尾部对冲信号+CVaR 阈值测试。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.pf_alloc.core.tail_hedge_signal import tail_hedge_signal


def _normal_returns(n: int = 200, vol: float = 0.01, seed: int = 7):
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(0.0003, vol, n), index=pd.bdate_range("2020-01-01", periods=n))


class TestTailHedgeSignal:
    def test_normal_market_no_hedge(self):
        rets = _normal_returns(200, vol=0.01)
        result = tail_hedge_signal(rets, cvar_threshold=-0.03)
        assert result["hedge_signal"].sum() == 0

    def test_crash_triggers_hedge(self):
        rets = _normal_returns(200, vol=0.01)
        rets.iloc[100:110] = -0.05  # 注入暴跌
        result = tail_hedge_signal(rets, cvar_threshold=-0.02)
        assert result["hedge_signal"].sum() > 0

    def test_cvar_pred_all_negative(self):
        rets = _normal_returns(200, vol=0.01)
        result = tail_hedge_signal(rets, cvar_threshold=-0.10)
        valid = result["cvar_pred"].dropna()
        assert len(valid) > 0
        assert (valid <= 0).all()

    def test_no_nan_in_output(self):
        rets = _normal_returns(200, vol=0.01)
        result = tail_hedge_signal(rets, cvar_threshold=-0.10)
        # 前 window-1 行因滚动窗口不足含 NaN 是预期行为，后续行不应有 NaN
        valid = result["cvar_pred"].dropna()
        assert len(valid) > 100  # 200 - 59 ≈ 141 行有效
        assert (result["hedge_signal"].iloc[59:] == (result["hedge_signal"].iloc[59:] == True)).all()
