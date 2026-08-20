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
"""calculate_dsr / calculate_full_metrics 单元测试(52号 §7 新发现1 测试债清偿).

覆盖: 样本量<60 退化、DSR∈[0,1]、多重测试修正(n_trials 增大→DSR下降)、
非正态修正(偏度/峰度影响 adjusted_sharpe)、is_overfitting 阈值 0.5、
n_trials=1 无修正、calculate_full_metrics 合并字段。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.metrics import (
    DEFAULT_N_TRIALS,
    MIN_SAMPLES_FOR_SHARPE,
    calculate_dsr,
    calculate_full_metrics,
)


# ============== calculate_dsr ==============


class TestCalculateDSR:
    def test_insufficient_samples_degenerate(self):
        r = calculate_dsr(sharpe_ratio=2.0, n_trials=10, n_samples=59)
        assert r["dsr"] == 0.0
        assert r["is_overfitting"] is True
        assert r["expected_max_sharpe"] == 0.0

    def test_min_samples_boundary(self):
        # n_samples=60 恰好达标, 正常计算
        r = calculate_dsr(sharpe_ratio=1.0, n_trials=1, n_samples=MIN_SAMPLES_FOR_SHARPE)
        assert 0.0 <= r["dsr"] <= 1.0

    def test_dsr_in_unit_interval(self):
        r = calculate_dsr(sharpe_ratio=1.5, n_trials=10, n_samples=252)
        assert 0.0 <= r["dsr"] <= 1.0

    def test_strong_sharpe_few_trials_not_overfitting(self):
        r = calculate_dsr(sharpe_ratio=2.0, n_trials=1, n_samples=504)
        assert r["dsr"] > 0.5
        assert r["is_overfitting"] is False

    def test_more_trials_lower_dsr(self):
        # 多重测试偏差: 同样Sharpe, 试错越多DSR越低
        r_few = calculate_dsr(sharpe_ratio=0.5, n_trials=2, n_samples=252)
        r_many = calculate_dsr(sharpe_ratio=0.5, n_trials=500, n_samples=252)
        assert r_many["dsr"] < r_few["dsr"]
        assert r_many["expected_max_sharpe"] > r_few["expected_max_sharpe"]

    def test_weak_sharpe_many_trials_overfitting(self):
        # 极弱Sharpe(0.05)+大量试错(1000次) → E[max SR]虚高超过观测 → DSR<0.5
        r = calculate_dsr(sharpe_ratio=0.05, n_trials=1000, n_samples=252)
        assert r["dsr"] < 0.5
        assert r["is_overfitting"] is True

    def test_single_trial_no_bias_correction(self):
        r = calculate_dsr(sharpe_ratio=1.0, n_trials=1, n_samples=252)
        assert r["expected_max_sharpe"] == 0.0

    def test_skewness_affects_dsr_via_variance(self):
        """#14 裁定：公式统编到 MOD-SIM-024 论文口径，弃 Cornish-Fisher 预调整——
        adjusted_sharpe 键=原始 sr（向后兼容），skewness 经 V[SR] 方差项影响 dsr。

        注：取 sr=0.2/n=100 使 z≈1.7~2.0 落在 Φ 敏感区；sr=1.0/n=252 时 z≈9~13，
        float64 下 Φ 饱和为 1.0，无法观测方差项效应。"""
        r_sym = calculate_dsr(sharpe_ratio=0.2, n_trials=1, n_samples=100, skewness=0.0)
        r_neg = calculate_dsr(sharpe_ratio=0.2, n_trials=1, n_samples=100, skewness=-1.5)
        # 兼容键：adjusted_sharpe 现=原始 sr（不再预调整）
        assert r_neg["adjusted_sharpe"] == r_sym["adjusted_sharpe"] == 0.2
        # 负偏度增大 V[SR]=(1-skew·SR+...) → σ_sr 增大 → dsr 下降（论文口径）
        assert r_neg["dsr"] != r_sym["dsr"]
        assert r_neg["dsr"] < r_sym["dsr"]

    def test_kurtosis_affects_dsr_via_variance(self):
        """#14 裁定：kurtosis 经 V[SR] 方差项影响 dsr（(kurt-1)/4·SR² 项），不再经 adjusted_sharpe。
        参数同取 Φ 敏感区（z≈1.9），避免高 z 值下 CDF 饱和。"""
        r_normal = calculate_dsr(sharpe_ratio=0.2, n_trials=1, n_samples=100, kurtosis=3.0)
        r_fat = calculate_dsr(sharpe_ratio=0.2, n_trials=1, n_samples=100, kurtosis=15.0)
        assert r_fat["adjusted_sharpe"] == r_normal["adjusted_sharpe"] == 0.2
        # 肥尾增大 V[SR] → σ_sr 增大 → dsr 下降
        assert r_fat["dsr"] != r_normal["dsr"]
        assert r_fat["dsr"] < r_normal["dsr"]

    def test_result_keys(self):
        r = calculate_dsr(sharpe_ratio=1.0, n_trials=10, n_samples=252)
        assert set(r) == {"dsr", "adjusted_sharpe", "expected_max_sharpe", "is_overfitting"}

    def test_default_n_trials(self):
        assert DEFAULT_N_TRIALS == 10


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

    def test_dsr_consistent_with_standalone(self):
        nav = self._nav()
        full = calculate_full_metrics(nav, trades_count=50, n_trials=10)
        rets = nav.pct_change().dropna()
        standalone = calculate_dsr(
            sharpe_ratio=full["sharpe_ratio"],
            n_trials=10,
            n_samples=len(rets),
            skewness=float(rets.skew()),
            kurtosis=float(rets.kurtosis()) + 3.0,
        )
        assert full["dsr"] == pytest.approx(standalone["dsr"])

    def test_short_series_degenerate_dsr(self):
        nav = pd.Series(
            1_000_000 * np.cumprod(1 + np.full(30, 0.001)),
            index=pd.date_range("2024-01-01", periods=30, freq="B"),
        )
        r = calculate_full_metrics(nav, trades_count=5)
        # 样本<60 → dsr=0, is_overfitting=True
        assert r["dsr"] == 0.0
        assert r["is_overfitting"] is True
