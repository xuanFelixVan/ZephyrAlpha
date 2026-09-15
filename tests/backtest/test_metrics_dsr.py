# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_metrics_dsr
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_metrics_dsr.py
# [TTL] task_bound
"""calculate_full_metrics DSR 合并字段单元测试（A4 退役 metrics.calculate_dsr 后重写）.

口径（2026-09-15 A4 裁定）：DSR 数学全量委托官方件 MOD-SIM-024
DeflatedSharpeCalculator（日频收益序列直入，量纲自洽）——原 calculate_dsr
坏路径（年化 Sharpe 配日频样本数，σ_SR 系统性偏小、DSR 偏向 1）已删除。

覆盖: 样本量<60 退化（dsr=0/is_overfitting=True）、DSR∈[0,1]、
多重测试修正（n_trials 增大→DSR 下降）、is_overfitting 阈值 0.5、
与官方件直算逐位一致、合并字段完整性。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.metrics import (
    DEFAULT_N_TRIALS,
    calculate_full_metrics,
)
from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_OVERFITTING_FLOOR,
    DSR_SIGNIFICANCE_THRESHOLD,
    DSRConfig,
    DeflatedSharpeCalculator,
)


# ============== calculate_full_metrics ==============


class TestCalculateFullMetrics:
    def _nav(self, n: int = 300, daily_ret: float = 0.001) -> pd.Series:
        rng = np.random.default_rng(11)
        rets = daily_ret + rng.normal(0.0, 0.005, n - 1)
        nav = 1_000_000 * np.cumprod(1 + np.concatenate([[0.0], rets]))
        idx = pd.date_range("2023-01-02", periods=n, freq="B")
        return pd.Series(nav, index=idx)

    def test_merged_fields(self):
        r = calculate_full_metrics(self._nav(), trades_count=50, n_trials=10)
        for key in (
            "total_return",
            "annual_return",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "win_rate",
            "trades_count",
            "dsr",
            "adjusted_sharpe",
            "expected_max_sharpe",
            "is_overfitting",
        ):
            assert key in r

    def test_dsr_matches_official_calculator(self):
        """DSR 与官方件 MOD-SIM-024 直算逐位一致（A4 委托契约）。"""
        nav = self._nav()
        full = calculate_full_metrics(nav, trades_count=50, n_trials=10)
        rets = [float(r) for r in nav.pct_change().dropna()]
        official = DeflatedSharpeCalculator(
            DSRConfig(periods_per_year=252)
        ).calculate(rets, num_trials=10, risk_free_rate=0.025 / 252)
        assert full["dsr"] == pytest.approx(official.dsr)

    def test_dsr_bounded_and_not_biased_to_one(self):
        """DSR∈[0,1]；坏路径已退役——正常波动序列不得系统性输出 DSR≈1。"""
        r = calculate_full_metrics(self._nav(), trades_count=50, n_trials=10)
        assert 0.0 <= r["dsr"] <= 1.0
        # 有噪声的日频序列，无噪声自由午餐：DSR 不得恒为 1（坏路径病症）
        assert r["dsr"] < 1.0

    def test_more_trials_lower_dsr(self):
        # 多重测试偏差: 同样收益序列, 试错越多DSR越低
        r_few = calculate_full_metrics(self._nav(), trades_count=50, n_trials=2)
        r_many = calculate_full_metrics(self._nav(), trades_count=50, n_trials=500)
        assert r_many["dsr"] <= r_few["dsr"]
        assert r_many["expected_max_sharpe"] >= r_few["expected_max_sharpe"]

    def test_is_overfitting_floor_semantics(self):
        """is_overfitting = dsr < 0.5（运气中值否决线；放行线 0.95 归 is_significant）。"""
        r = calculate_full_metrics(self._nav(), trades_count=50, n_trials=10)
        assert r["is_overfitting"] == bool(r["dsr"] < DSR_OVERFITTING_FLOOR)

    def test_short_series_degenerate_dsr(self):
        nav = pd.Series(
            1_000_000 * np.cumprod(1 + np.full(30, 0.001)),
            index=pd.date_range("2024-01-01", periods=30, freq="B"),
        )
        r = calculate_full_metrics(nav, trades_count=5)
        # 样本<60 → dsr=0, is_overfitting=True（官方件<3抛错前先行拦截）
        assert r["dsr"] == 0.0
        assert r["is_overfitting"] is True
        assert r["adjusted_sharpe"] == r["sharpe_ratio"]

    def test_adjusted_sharpe_is_annualized_sharpe(self):
        nav = self._nav()
        r = calculate_full_metrics(nav, trades_count=50, n_trials=10)
        assert r["adjusted_sharpe"] == r["sharpe_ratio"]


def test_default_n_trials():
    assert DEFAULT_N_TRIALS == 10
    # 阈值常量 SSOT 引用（A5 三线统一锚点）
    assert DSR_SIGNIFICANCE_THRESHOLD == 0.95
    assert DSR_OVERFITTING_FLOOR == 0.5
