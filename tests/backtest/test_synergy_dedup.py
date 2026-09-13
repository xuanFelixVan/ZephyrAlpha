# [BLUEPRINT] MOD-BT-087 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_synergy_dedup
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.pf_alloc.core.synergy_dedup
# [CONSUMERS] synergy_dedup 质量守卫
# [STARTUP] manual
# [INVARIANTS] 纯合成数据；簇首=最高 Sharpe；去重后簇数 ≤ 原策略数
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-087 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""synergy_dedup 质量守卫——相关性聚类去重测试。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.pf_alloc.core.synergy_dedup import synergy_dedup


def _make_returns(n_days: int = 200, n_strats: int = 4, seed: int = 11):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    rets = {}
    for i in range(n_strats):
        rets[f"strat_{i}"] = pd.Series(rng.normal(0.001, 0.01, n_days), index=dates)
    return rets


class TestSynergyDedup:
    def test_two_identical_merge(self):
        base = pd.Series(np.random.default_rng(1).normal(0.001, 0.01, 200),
                         index=pd.bdate_range("2020-01-01", periods=200))
        rets = {"orig": base, "copy": base + np.random.default_rng(2).normal(0, 0.0001, 200)}
        sharpe = {"orig": 1.0, "copy": 0.9}
        clusters = synergy_dedup(rets, sharpe, corr_threshold=0.90)
        assert len(clusters) == 1
        assert clusters[0]["head"] == "orig"
        assert "copy" in clusters[0]["members"]

    def test_independent_stay_separate(self):
        rng = np.random.default_rng(3)
        d = pd.bdate_range("2020-01-01", periods=200)
        rets = {
            "indep_a": pd.Series(rng.normal(0.001, 0.01, 200), index=d),
            "indep_b": pd.Series(rng.normal(0.001, 0.01, 200), index=d),
        }
        sharpe = {"indep_a": 0.5, "indep_b": 0.6}
        clusters = synergy_dedup(rets, sharpe, corr_threshold=0.70)
        assert len(clusters) == 2  # 独立策略不合并

    def test_single_strategy_single_cluster(self):
        rets = {"only": pd.Series(np.random.default_rng(5).normal(0, 0.01, 100),
                                   index=pd.bdate_range("2020-01-01", periods=100))}
        sharpe = {"only": 0.5}
        clusters = synergy_dedup(rets, sharpe)
        assert len(clusters) == 1 and clusters[0]["members"] == ["only"]

    def test_head_is_highest_sharpe(self):
        rng = np.random.default_rng(6)
        d = pd.bdate_range("2020-01-01", periods=200)
        base = pd.Series(rng.normal(0.001, 0.01, 200), index=d)
        noisy = base + rng.normal(0, 0.001, 200)  # 高相关但略有差异
        rets = {"strong": base * 1.0, "weak": noisy * 0.5}
        sharpe = {"strong": 1.5, "weak": 0.3}
        clusters = synergy_dedup(rets, sharpe, corr_threshold=0.90)
        assert len(clusters) == 1
        assert clusters[0]["head"] == "strong"
